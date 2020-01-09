from django.db import connections
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from open_anafi.lib import DatabaseTools
from open_anafi.models import Department, InstitutionType, IdentifierType
from open_anafi.serializers import DepartmentSerializer, InstitutionTypeSerializer, IdentifierTypeSerializer


class IdentifierViews(APIView):
  permission_classes = (IsAuthenticated,)
  """
    retrieve Identifier in function of the types: SIRET, SIRENT and FINESS
  """
  def get(self, requests):
    #@TODO: Refactor function, dirty code
    # SIRET => ident
    # SIREN => nine first SIRET's charaters
    # FINESS => finess
    global department_query, department_query
    params = requests.query_params
    sql_query = ""
    if 'type' in params:
      if params['type'] == 'SIRET':
        sql_query += '''
						SELECT DISTINCT C.ident, C.ctype, C.lbudg
						FROM collectivite AS C, 
							(SELECT DISTINCT ident AS ident, MAX(exer) AS max_exer, ctype, cnome 
							FROM collectivite  
							WHERE ident IS NOT NULL GROUP BY ident, ctype, cnome) AS MC 
						WHERE C.ident = MC.ident AND C.exer = MC.max_exer AND C.ctype = MC.ctype
						'''
      elif params['type'] == 'SIREN':
        sql_query +=    """
                                SELECT DISTINCT  substring(c.ident FROM 1 FOR 9) AS ident, c.lbudg, c.ctype , c.cbudg
                                FROM collectivite as C RIGHT JOIN
                                    (
                                        SELECT DISTINCT substring(ident FROM 1 FOR 9) AS idente, MIN(cbudg ) as cbudge
                                        FROM collectivite
                                        GROUP BY idente
                                        HAVING  CAST( MIN(cbudg ) AS SMALLINT )<=2
                                    ) ft ON substring(c.ident FROM 1 FOR 9) = ft.idente AND c.cbudg = ft.cbudge  WHERE c.ident IS NOT NULL
                                """


        #"SELECT DISTINCT substring(ident FROM 1 FOR 9) AS ident, MIN(ctype) as ctype, MIN(lbudg) as lbudg  FROM collectivite AS C WHERE ident IS NOT NULL "



        # """
        #                 select  c.ident, c.lbudg, c.ctype , c.cbudg, c.cnome
        #                 from (select ROW_NUMBER() over(partition by substring(t2.ident FROM 1 FOR 9) order by cbudg )as rownum,substring(t2.ident FROM 1 FOR 9) AS ident, lbudg, ctype , cbudg, cnome, ndept from collectivite as t2) c
        #                 where c.rownum=1
        #
        #
        #                 """





      elif params['type'] == 'FINESS':
        sql_query += "SELECT DISTINCT finess AS ident, lbudg, ctype FROM collectivite WHERE ident IS NOT NULL "
      else:
        return Response(status = 400)
    else:
      return Response(status = 400)
    if 'department' in params:
      department_query = "AND C.ndept = '{}'".format(params['department'])

    institution_query = ""
    if 'institutions' in params:
      first = True
      institutions = params['institutions'].split(',')
      for institution in institutions:
        if first:
          institution_query = "C.ctype = '{}'".format(institution)
          first = False
        else:
          institution_query += "OR C.ctype = '{}'".format(institution)
      sql_query = "{} {} AND ({});".format(sql_query, department_query, institution_query)
    else:
      sql_query = "{} {};".format(sql_query, department_query)

    #if params['type'] == 'SIREN':
    # continue
    with connections['cci'].cursor() as cursor:
      cursor.execute(sql_query)
      columns = [col[0] for col in cursor.description]
      answers = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return Response(answers, status = 200)



class DepartmentViews(viewsets.ModelViewSet):
  queryset = Department.objects.all()
  serializer_class = DepartmentSerializer
  permission_classes = (IsAuthenticated,)

class InstitutionTypeViews(viewsets.ModelViewSet):
  queryset = InstitutionType.objects.all()
  serializer_class = InstitutionTypeSerializer
  permission_classes = (IsAuthenticated,)


class IdentifierTypeViews(viewsets.ModelViewSet):
  queryset = IdentifierType.objects.all()
  serializer_class = IdentifierTypeSerializer
  permission_classes = (IsAuthenticated,)

class DataBaseInfoList(APIView):
  permission_classes = (IsAuthenticated,)

  def post(self, request):
    table = request.data['column'].split('.')[0]
    column = request.data['column'].split('.')[1]
    limit = request.data['limit']

    sql_query = f'''
			SELECT DISTINCT {column} FROM {table} LIMIT {limit}
		'''

    with connections['cci'].cursor() as cursor:
      cursor.execute(sql_query)
      data = cursor.fetchall()

    answer = [element[0] for element in data]

    return Response(answer, status = 200)

class DataBaseInfoViews(APIView):
  permission_classes = (IsAuthenticated,)

  def get(self):

    sql_query = '''
		WITH l as (
			select oid::regclass::text table_name
			from pg_class 
			except
			select distinct inhrelid::regclass::text
			from pg_inherits)
			SELECT t.table_name, column_name, data_type
			FROM information_schema.columns AS t
			INNER JOIN l ON l.table_name = t.table_name
			WHERE t.table_schema = 'public'
			ORDER BY t.table_name;
		'''
    with connections['cci'].cursor() as cursor:
      cursor.execute(sql_query)
      # columns = [col[0] for col in cursor.description]
      # answers = [dict(zip(columns, row)) for row in cursor.fetchall()]
      data = cursor.fetchall()

    answers = {}
    for i in data:
      data_dict = {}
      data_dict['selected'] = False
      data_dict['option'] = ""
      data_dict['logicalOperator'] = ""
      data_dict['condition'] = ""
      data_dict['name'] = i[1]
      data_dict['type'] = i[2]
      if i[0] not in answers:
        answers[i[0]] = {'name': i[0], 'columns': [data_dict]}
      else:
        answers[i[0]]['columns'].append(data_dict)

    return_values = []
    for key, value in answers.items():
      return_values.append(value)

    return Response(return_values, status = 200)


class DataBaseSimpleInfoViews(APIView):
  permission_classes = (IsAuthenticated,)

  def get(self):
    data = [
      {
        "name": "comptes.comptes",
        "alias": "Nom de comptes",
        "type": "character varying",
        "selected": False,
        "operator": {"name": "", "data": ""},
        "option": "",
        "condition": ""
      },
      {
        "name": "collectivite.ident",
        "alias": "Identifiant",
        "type": "character varying",
        "selected": False,
        "operator": {"name": "", "data": ""},
        "option": "",
        "condition": ""
      },
      {
        "name": "collectivite.exer",
        "alias": "Exercice de gestion",
        "type": "Integer",
        "selected": False,
        "operator": {"name": "", "data": ""},
        "option": "",
        "condition": ""
      },
      {
        "name": "departement.dp_code",
        "alias": "Code département",
        "type": "character varying",
        "selected": False,
        "operator": {"name": "", "data": ""},
        "option": "",
        "condition": ""
      },
      {
        "name": "type_etablissements.libelle_ets",
        "alias": "Libelle établissement",
        "type": "character varying",
        "selected": False,
        "operator": {"name": "", "data": ""},
        "option": "",
        "condition": ""
      },
    ]

    return Response(data = data, status = 200)

class DataBaseCustomQueryViews(APIView):
  permission_classes = (IsAuthenticated,)

  def get(self):
    data = {
      "columns": [
        {
          "name": "departement.dp_code",
          "alias": "Code département",
          "type": "character varying",
          "selected": True,
          "operator": {"name": "", "data": ""},
          "option": "",
          "condition": ""
        }
      ],
      "joinsTable": [
        {
          "column1": "collectivite.ident",
          "column2": "execution_2010.ident"
        }, {
          "column1": "collectivite.ndept",
          "column2": "departement.dp_code"
        }, {
          "column1": "nomenclature.nomen",
          "column2": "collectivite.nomen"
        }, {
          "column1": "type_budget.code_budget",
          "column2": "collectivite.cbudg"
        }, {
          "column1": "type_etablissements.code_type_ets",
          "column2": "collectivite.ctype"
        }, {
          "column1": "execution_2010.cptop",
          "column2": "operations.code_operation"
        }, {
          "column1": "collectivite.exer",
          "column2": "execution_2010.exercice"
        }, {
          "column1": "execution_2010.comptes",
          "column2": "comptes.comptes"
        }
      ]
    }

    return Response(data = data, status = 200)

class DataBaseQueryViews(APIView):
  permission_classes = (IsAuthenticated,)

  def post(self, request):

    global final_query
    if request.query_params.get('type') == 'advanced':
      tables = request.data['tables']
      joins_conditions = request.data['joinsTable']
      where_conditions = request.data['conditions']

      final_query = DatabaseTools.get_final_query(tables, joins_conditions, where_conditions)
    elif request.query_params.get('type') == 'simple':
      columns = request.data['columns']
      joins_conditions = request.data['joinsTable']
      where_conditions = request.data['conditions']

      final_query = DatabaseTools.get_final_query_simple(columns, joins_conditions, where_conditions)
    with connections['cci'].cursor() as cursor:
      cursor.execute(final_query)
      columns = [col[0] for col in cursor.description]
      answers = [dict(zip(columns, row)) for row in cursor.fetchall()]

    final_answer = {}
    final_answer['query'] = final_query
    final_answer['answers'] = answers

    return Response(final_answer, status = 200)

class DataBaseQueryViewViews(APIView):
  permission_classes = (IsAuthenticated,)

  def post(self, request):
    global final_query
    if request.query_params.get('type') == 'advanced':
      tables = request.data['tables']
      joins_conditions = request.data['joinsTable']
      where_conditions = request.data['conditions']

      final_query = DatabaseTools.get_final_query(tables, joins_conditions, where_conditions)
    elif request.get('type') == 'simple':
      columns = request.data['columns']
      joins_conditions = request.data['joinsTable']
      where_conditions = request.data['conditions']

      final_query = DatabaseTools.get_final_query_simple(columns, joins_conditions, where_conditions)

    final_answer = {}
    final_answer['query'] = final_query

    return Response(final_answer, status = 200)

