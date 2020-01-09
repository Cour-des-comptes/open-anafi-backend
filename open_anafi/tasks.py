from __future__ import absolute_import, unicode_literals

import time

import django.db as db
import numpy as np
import pandas as pd
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import connections

from open_anafi.lib import AggregationRequestMaker
from open_anafi.lib import ExcelWriterTools, BalanceTools, ReportTools, SQL_REQUEST_COLLECTIVITE_PER_YEAR
from open_anafi.lib import SQL_REQUEST_COLLECTIVITE, SQL_REQUEST_POPULATION, SQL_REQUEST_FINESS
from open_anafi.lib import SQL_REQUEST_SIRET, SQL_REQUEST_SIRET_BALANCE, SQL_REQUEST_SIREN_BALANCE
from open_anafi.lib.sql_requests import SQL_REQUEST_SIRET_SAFE
from open_anafi.models import Frame, Report, IndicatorParameter, Variable, Nomenclature

logger = get_task_logger(__name__)

MULTI_NOMENCLATURE_DICT = {'M4*': ['M41','M42','M43'] }

@shared_task
def compute_frame(frame_id, exmin, exmax, ident, type_ident, nomenclature_id, institutions, report_id, aggregate=False):
    """
    Computes an open_anafi frame

    :param nomenclature_id:
    :param aggregate:
    :param frame_id: The id of the frame to use as a model
    :type frame_id: int

    :param exmin: The lower bound of the range to calculate the report on
    :type exmin: int

    :param exmax: The upper bound of the range to calculate the report on
    :type exmax: int

    :param ident: The identifier(s) to calculate the report on (a concatenation in case of an aggregation)
    :type ident: str

    :param type_ident: The type of the identifier(s) (SIRET, SIREN, FINESS)
    :type type_ident: str

    :param nomenclature_id: The selected nomenclature id
    :type nomenclature_id: str

    :param institutions: List of institution types
    :type institutions: list

    :param report_id: The id of the report object to update
    :type report_id: int
    """
    global p_df, population_query, collectivite_query, final_query
    try:
        start = time.time()
        logger.debug("Start !")
        exges_list = list(range(exmin, exmax + 1))
        exercices_clause = ""

        for i in range(len(exges_list)):
            exercices_clause += " e.exercice = '{}' ".format(exges_list[i])
            if i != len(exges_list) - 1:
                exercices_clause += "OR"

        if type_ident == "SIREN":
            request_string = """
                                    SELECT e.ident AS sirets
                                    FROM execution_2010 AS e 
                                    WHERE substring(e.ident from 1 for 9) IN {sirens};
                                """
            sirens_string = f"{ident}".replace('[', '(').replace(']', ')')
            first_query = request_string.format(sirens=sirens_string)
            with db.connections['cci'].cursor() as cursor:
                cursor.execute(first_query)
                columns = [col[0] for col in cursor.description]
                answers = [dict(zip(columns, row)) for row in cursor.fetchall()]
            ident = [ answers[i]['sirets'] for i in range(len(answers)) ]
            if len(ident)<1 : raise ValueError("Le/Les SIREN choisis ne correspondent à aucun SIRET ")
            type_ident="SIRET"
            logger.debug("SIRETs correspondant au(x) SIREN trouvés ")


        perimeter_query = SQL_REQUEST_COLLECTIVITE_PER_YEAR.format(
            sirets=f"{ident}".replace('[', '(').replace(']', ')'),
            exercice=f"{list(exges_list)}".replace('[', '(').replace(']', ')'))
        logger.debug(perimeter_query)
        with db.connections['cci'].cursor() as cursor:

            cursor.execute(perimeter_query)
            columns = [col[0] for col in cursor.description]
            perimeter = [dict(zip(columns, row)) for row in cursor.fetchall()]

        perimeter_df = pd.DataFrame(perimeter)
        if len(perimeter_df) < 1:
            logger.debug('Empty data frame')
            report = Report.objects.get(id=report_id)
            report.state = "EMPTY"
            report.save()
            return

        else :
            nomenclature = Nomenclature.objects.filter(id=nomenclature_id)[0].name

            filt1 = (perimeter_df.cnome == nomenclature)
            filt2 =  (pd.to_numeric(perimeter_df.ctype).isin( institutions))
            filt = (filt1 & filt2)

            time.sleep(5)

            p_df = perimeter_df[filt]
            siret_safe, exer_safe = list(p_df.ident), list(p_df.exer)
            if len(p_df) > 0:
                safe_query = "WHERE"

                for siret, exer in zip(siret_safe, exer_safe):
                    safe_query+= " (e.ident = '{siret}' AND e.exercice = {exercice}) OR".format(siret= siret, exercice = exer)
                safe_query= safe_query[:-2]
                exges_list = exer_safe
                final_query = SQL_REQUEST_SIRET_SAFE.format(whereclause = safe_query)
                safe_query_status = True
            else:
                logger.debug('Empty data frame')
                report = Report.objects.get(id=report_id)
                report.state = "EMPTY"
                report.save()
                return

        if type_ident == "SIRET":
            if aggregate:
                ident_frame = pd.DataFrame(ident)
                final_query = AggregationRequestMaker.get_data_frame_request(ident_frame, exges_list)
                collectivite_query = AggregationRequestMaker.get_siret_request(ident_frame, exges_list)
                population_query = AggregationRequestMaker.get_population_request(ident_frame, exges_list)
            else:
                sirets_string = f"{ident}".replace('[', '(').replace(']', ')')
                sirets_sql = f"{sirets_string}"
                if not safe_query_status :
                    final_query = SQL_REQUEST_SIRET.format(sirets=sirets_sql, exercices=exercices_clause)
                collectivite_query = SQL_REQUEST_COLLECTIVITE.format(sirets=sirets_sql)
                population_query = SQL_REQUEST_POPULATION.format(sirets = sirets_sql,
                                                                    exercices = tuple(exges_list) if len(exges_list) > 1 else f"({exges_list[0]})")
        elif type_ident == "FINESS":
            final_query =  SQL_REQUEST_FINESS.format(finess = ident, exercices = exercices_clause)

        with db.connections['cci'].cursor() as cursor:
            cursor.execute(final_query)
            columns = [col[0] for col in cursor.description]
            answers = [dict(zip(columns, row)) for row in cursor.fetchall()]

        with db.connections['cci'].cursor() as cursor:
            cursor.execute(collectivite_query)
            columns = [col[0] for col in cursor.description]
            collectivites = [dict(zip(columns, row)) for row in cursor.fetchall()]

        with db.connections['cci'].cursor() as cursor:
            cursor.execute(population_query)
            population = np.array([row[0] for row in cursor.fetchall()], dtype=float)

        logger.debug(f'population {population}')
        data_frame = pd.DataFrame(answers)
        exges_list = list(np.sort(np.unique(data_frame['exercice'])))
        # We check the state of the account for each year, in order to know if it's "Definite" or "Provisoire" (D or P)
        dps_lookup_table = {
            'D': 'Definitif',
            'P': 'Provisoire'
        }
        dps = []
        for ex in exges_list:
            data_frame_ex = data_frame[data_frame['exercice'] == ex]
            current_dp = data_frame_ex['dp'].unique()
            if len(current_dp) > 1:
                dps.append('Mixte')
            else:
                dps.append(dps_lookup_table[current_dp[0]])

        logger.debug("starting calculation...")

        frame = Frame.objects.get(id = frame_id)
        logger.debug("lbl1")
        indicators_dic = {}
        variables_dic = {}
        max_depth = frame.max_depth
        logger.debug(max_depth)
        result = {}
        logger.debug("lbl2")
        indicators_to_be_computed = frame.indicators.all()
        equations = IndicatorParameter.objects.filter(indicator__in = indicators_to_be_computed)
        variables = Variable.objects.filter(indicator_parameter__in = equations)
        logger.debug('computing indic dict')
        for indic in indicators_to_be_computed:
            indicators_dic[indic.name] = (indic, equations.filter(indicator = indic))
            result[indic.name] = None
        for eq in equations:
            subset = variables.filter(indicator_parameter = eq)
            for var in subset:
                variables_dic[(eq, var.name)] = var

        logger.debug('computing indicators')


        for depth in range(1, max_depth + 1):
            matching_indicators = indicators_to_be_computed.filter(max_depth = depth)
            for indic in matching_indicators:
                logger.debug(indic.name)
                ReportTools.compute_indicator(indic.name,
                                                indicators_dic,
                                                variables_dic,
                                                exges_list,
                                                data_frame,
                                                collectivites,
                                                population,
                                              result)
                logger.debug('Done')

        collectivites_dataframe = pd.DataFrame(collectivites)
        report_name = ExcelWriterTools.write_report(result,
                                                    collectivites_dataframe,
                                                    type_ident,
                                                    exges_list,
                                                    collectivites_dataframe['lbudg'].tolist(),
                                                    frame.model_name,
                                                    dps=dps,
                                                    aggregate=aggregate,
                                                    perimeter=p_df)

        report = Report.objects.get(id = report_id)
        report.name = report_name
        report.state = "DONE"
        report.save()

        end = time.time()

        logger.debug(end - start)
    except Exception as e:
        logger.debug(e)

        report = Report.objects.get(id = report_id)

        report.state = "FAILED"

        report.save()

@shared_task
def compute_balance(exmin, exmax, ident, type_ident, report_id):
    """

    :param exmin:
    :param exmax:
    :param ident:
    :param type_ident:
    :param report_id:
    :return:
    """
    global final_query
    try:
        start = time.time()
        exges_list = list(range(exmin, exmax + 1))
        exercices_clause = ""
        exercices_collectivite = ""
        for i in range(len(exges_list)):
            exercices_clause += " e.exercice = '{}' ".format(exges_list[i])
            exercices_collectivite += " c.exer = '{}' ".format(exges_list[i])
            if i != len(exges_list) - 1:
                exercices_clause += "OR"
                exercices_collectivite += "OR"
        if type_ident == "SIRET":
            sirets_string = f"{ident}".replace('[', '(').replace(']', ')')
            sirets_sql = f"{sirets_string}"
            final_query = SQL_REQUEST_SIRET_BALANCE.format(sirets=sirets_sql, exercices=exercices_clause,
                                                           exercices_collectivite=exercices_collectivite)
        elif type_ident == "SIREN":
            final_query = SQL_REQUEST_SIREN_BALANCE.format(siren=ident[0], exercices=exercices_clause,
                                                           exercices_collectivite=exercices_collectivite)
        elif type_ident == "FINESS":
            final_query = SQL_REQUEST_FINESS.format(finess=ident, exercices=exercices_clause)

        with connections['cci'].cursor() as cursor:
            cursor.execute(final_query)
            columns = [col[0] for col in cursor.description]
            answers = [dict(zip(columns, row)) for row in cursor.fetchall()]

        data_frame = pd.DataFrame(answers)

        balances = BalanceTools.get_balance(exges_list, data_frame)
        balances = balances.sort_values(by=['exercice', 'compte'])
        balance_name = ExcelWriterTools.write_balance(ident, type_ident, exmin, exmax, data_frame['lbudg'].unique(),
                                                      balances)

        report = Report.objects.get(id=report_id)

        report.name = balance_name

        report.state = "DONE"

        report.save()

        end = time.time()

        logger.debug('Execution Time {}'.format(end - start))
    except Exception as e:
        logger.debug(e)
        report = Report.objects.get(id=report_id)

        report.state = "FAILED"

        report.save()

    return
