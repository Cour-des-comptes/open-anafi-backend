import numpy as np
from open_anafi.lib import SoldeFactory


class VariableTools:
    @staticmethod
    def feed_variable(variable, exges_list, exges_effective, data_frame_comptes):
        """
    Evaluates a variable with the given data.

    :param variable: The variable object
    :type variable: class:`open_anafi.models.Variable`

    :param exges_list: The range of exercices given by the user
    :type exges_list: dict

    :param exges_effective: The effective range of exercices (without the empty ones)
    :type exges_effective: dict

    :param data_frame_comptes: The account data
    :type data_frame_comptes: class:`pandas.DataFrame`

    :return: A numpy array with the variable evaluation for each year (zero for empty exercices)
    :rtype: class:`numpy.Array`
    """
        to_return = np.zeros(len(exges_list))
        if not data_frame_comptes.empty:
            del data_frame_comptes['comptes']
            data_frame_comptes = data_frame_comptes.groupby(['exercice', 'cptop'])[
                ["cptcre", "cptdeb"]].sum().reset_index()
            solde_function = SoldeFactory.factory(variable.type_solde, variable.solde)
            exges_size = len(exges_list)
            mnt = np.zeros(exges_size)
            for idx, exercice in enumerate(exges_list):
                if exercice in exges_effective:
                    # We take into account the type of solde
                    data_frame_exges = data_frame_comptes[data_frame_comptes['exercice'] == exercice]
                    c = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0}
                    d = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0}
                    for index, row in data_frame_exges.iterrows():
                        c[int(row['cptop'])] = float(row['cptcre'])
                        d[int(row['cptop'])] = float(row['cptdeb'])

                    mnt[idx] = solde_function(c, d)
            to_return = mnt
        return to_return
