from collections import Iterable
import logging

logger = logging.getLogger(__name__)

import numpy as np

from open_anafi.lib import VariableTools


def keepinf(t):
    """ Accepts iterable of numerical inputs or numerical inputs
        Returns 1 for non infinite values, and np.inf for infinite values"""
    lambd = lambda x: np.inf if np.isinf(x) else 1
    if isinstance(t, Iterable):
        return np.array(list(map(lambd, t)))
    else:
        return lambd(t)


class ReportTools:



    @staticmethod
    def evaluate_tree(parameter, tree, data_frame, result, variables_dic, population, exges_list, exges_effective):
        """A recursive function that evaluates an equation. Usually a python tuple. But it will be called 
           with strings and integers when reaching the bottom of the tree.
           All the calculations are made using numpy arrays. We calculate the results on every year at once.

        :param parameter: The indicator parameter we are currently calculating
        :type parameter: open_anafi.models.IndicatorParameter

        :param tree: The current node that is being evaluated
        :type tree: tuple, str, int

        :param data_frame: The data frame that will be used to extract the datas to evaluate variables
        :type data_frame: class:`pandas.DataFrame`

        :param result: The dictionary that will store the output of the evaluation. It will also be used if an indicator is used in the calculation of another one of higher depth. The result dictionary will be searched for the value to pick.
        :type result: dict

        :param variables_dic: A dictionary that will contain all the `open_anafi.models.Variable` objects who can be used during the report calculation.
                              The key is a tuple of the form (`open_anafi.models.IndicatorParameter`, variable_name)
        :type variables_dic: dict

        :param population: The population for all the evaluated years
        :type population: optional, list of int

        :param exges_list: A list of all the years to evaluate in the report
        :type exges_list: list of int

        :param exges_effective: A list of all the years the current parameter can be evaluated on (Some may have no formulas for certain years)
        :type exges_effective: list of int
        """
        uminus = False

        if type(tree) is tuple:
            #Si c'est un tuple
            left_child = ReportTools.evaluate_tree(parameter, 
                                                   tree[1],
                                                   data_frame,
                                                   result,
                                                   variables_dic, 
                                                   population, 
                                                   exges_list, 
                                                   exges_effective)

            right_child = ReportTools.evaluate_tree(parameter, 
                                                   tree[2],
                                                   data_frame,
                                                   result,
                                                   variables_dic, 
                                                   population, 
                                                   exges_list, 
                                                   exges_effective)
                                    
            if tree[0] == '+':
                return np.add(np.nan_to_num(left_child), np.nan_to_num(right_child))
            elif tree[0] == '-':
                return np.subtract(np.nan_to_num(left_child), np.nan_to_num(right_child))
            elif tree[0] == '*':
                return np.multiply(np.nan_to_num(left_child), np.nan_to_num(right_child))
            elif tree[0] == '/':
                return np.divide(np.nan_to_num(left_child), np.nan_to_num(right_child), out=np.full_like(left_child, None), where=right_child != 0)
            elif tree[0] == '^':
                return np.power(np.nan_to_num(left_child), np.nan_to_num(right_child))
        elif type(tree) is not str:
            return float(tree)
        else:
            #Sinon, il s'agit d'une variable ou d'un indicateur

            #Uminus check
            if tree.startswith('-'):
                uminus = True
                var_or_indicator_name = tree[1:]
            else:
                var_or_indicator_name = tree

            if (parameter, var_or_indicator_name) in variables_dic:
                variable = variables_dic[(parameter, var_or_indicator_name)]
                var_data_frame = data_frame[data_frame['comptes'].str.startswith(variable.numero_compte, na=False)]
                if uminus:
                    return np.multiply(-1, VariableTools.feed_variable(variable, exges_list, exges_effective, var_data_frame))
                else:
                    return VariableTools.feed_variable(variable, exges_list, exges_effective, var_data_frame)

            elif var_or_indicator_name in result or var_or_indicator_name[3:] in result:
                #Gestion de l'offset
                if var_or_indicator_name.startswith('@'):
                    
                    var_or_indicator_name = var_or_indicator_name[1:] #On retire l'@
                    offset_value = int(var_or_indicator_name[1])

                    corresponding_indicator = result[var_or_indicator_name[2:]]

                    if var_or_indicator_name.startswith('M'):
                        corresponding_indicator = np.pad(corresponding_indicator, (offset_value, 0), mode='constant', constant_values=(np.nan,))[:-offset_value]
                    elif var_or_indicator_name.startswith('P'):
                        corresponding_indicator = np.pad(corresponding_indicator, (0, offset_value), mode='constant', constant_values=(np.nan,))[offset_value:]
                    logger.debug(corresponding_indicator)
                else:
                    corresponding_indicator = result[var_or_indicator_name]

                if uminus:
                    return np.multiply(-1, corresponding_indicator)
                else:
                    return corresponding_indicator
            elif var_or_indicator_name == "$POP":
                return population

    @staticmethod
    def compute_indicator(indicator, indicator_dic, variables_dic, exges_list, data_frame, collectivites, population,
                          result_dic):
        """The medthod that evaluates an indicator. It will iterate through all the parameters and calculate every parameter who matches the requested report. For example, if an indicator has 2 parameters : One going from 2009 to 2014, and the other from 2015 to 2018, the resulting  will be two numpy arrays of the form [value, value, value, value, value, value, 0, 0, 0, 0] and [0, 0, 0, 0, 0, 0, value, value, value, value]. Adding them together will then give the evaluation of the desired indicator.

        :param indicator: The name of the indicator to evaluate (We can use the name has it is unique)
        :type indicator: str

        :param indicator_dic: A  dictionnary that contains the indicator objects as well as all the parameters linked to that indicator. The key is the name of the indicator.
        :type indicator_dic: dict

        :param variables_dic: A dictionary that will contain all the `open_anafi.models.Variable` objects who can be used during the report calculation.
                              The key is a tuple of the form (`open_anafi.models.IndicatorParameter`, variable_name)
        :type variables_dic: dict

        :param exges_list: A list of all the years to evaluate in the report
        :type exges_list: list of int

        :param data_frame: The data frame that will be used to extract the datas to evaluate variables
        :type data_frame: class:`pandas.DataFrame`

        :param collectivites: The result of the collectivites sql request. A list of dictionnaries containing all the informations on the collectivites currently evaluate. The data will be used to determine the TB and TE parameters (Type budget and Type Etablissement). This will let us know if a parameter can be selected or not.
        :type collectivites: list of dict


        :param population: The population for all the evaluated years
        :type population: optional, list of int

        :param result_dic: The dictionary that will store the output of the evaluation.
        :type result_dic: dict
        """
        exges_size = len(exges_list)
        exmax = exges_list[exges_size - 1]
        exmin = exges_list[0]
        result = np.zeros(exges_size)

        #Parcourt des paramètres et calculs de ces derniers en fonction des années/TB/TE
        for parameter in indicator_dic[indicator][1]:
            param_year_min = int(parameter.year_min) if parameter.year_min is not None else None
            param_year_max = int(parameter.year_max) if parameter.year_max is not None else None

            if param_year_min is not None and param_year_min > exmax:
                continue

            if param_year_max is not None and param_year_max < exmin:
                continue

             #TODO - Gestion du TE

            #Gestion du code budget
            # On considère que toutes les collectivités ont le même code du budget dans le cas de l'aggregation.
            if parameter.type_budget is not None:
                cbudg = collectivites[0]['cbudg']
                if cbudg == '1' or cbudg == '2':
                    type_budget = 'BP'
                elif cbudg == '3' or cbudg == '4':
                    type_budget = 'BA'
                else:
                    raise ValueError

                #Après avoir évalué le type_budget, on compare avec le paramètre courant.
                if type_budget != parameter.type_budget:
                    continue

            if param_year_min is not None and param_year_min > exges_list[0]:
                year_min = param_year_min
            else:
                year_min = exges_list[0]

            if param_year_max is not None and param_year_max < exmax:
                year_max = param_year_max
            else:
                year_max = exmax

            try:
                eq = eval(parameter.readable_equation)
            except NameError:
                eq = parameter.readable_equation
            exges_effective = [x for x in list(range(year_min, year_max + 1)) if x in exges_list]

            population = population[exges_effective[0]%exmin:exges_effective[-1]%exmin+1]

            if parameter.displaying is not None:

                result = np.add(result, np.absolute(np.nan_to_num(ReportTools.evaluate_tree(parameter, eq, data_frame, result_dic, variables_dic, population, exges_list, exges_effective))))

            else:
                result = np.add(result, np.nan_to_num(ReportTools.evaluate_tree(parameter, eq, data_frame, result_dic, variables_dic, population, exges_list, exges_effective)))

        result_dic[indicator] = np.nan_to_num(result)