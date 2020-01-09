import pandas as pd


class BalanceTools:
    @staticmethod
    def get_balance(exges_list, data_frame):
        columns = ["exercice", "siret", "organisme", "type budget", "nomenclature", "compte", "BEDEB", "BECRED", "OBDEB", "OBCRED", "OBODEB", "OBOCRED", "ONBDEB", "ONBCRED", "ADEB", "ACRED", "OADEB", "OACRED", "BSDEB", "BSCRED", "SDEB", "SCRED"]
        data_frames = pd.DataFrame(columns=columns)

        for ex in exges_list:
            data_frame_ex = data_frame[data_frame['exercice'] == ex]
            sirets_list = data_frame_ex['siret']
            sirets_list = sirets_list.unique()
            for siret in sirets_list:
                data_frame_siret = data_frame_ex[data_frame_ex['siret'] == siret]
                comptes_list = data_frame_siret['comptes']
                comptes_list = comptes_list.unique()
                for compte in comptes_list:
                    data_frame_compte = data_frame_siret[data_frame_siret['comptes'] == compte]
                    #data_frame_compte_bak = data_frame_compte[data_frame_compte['comptes'] == compte]
                    #del data_frame_compte['comptes']
                    #data_frame_compte = data_frame_compte.groupby(['exercice', 'cptop'])[["cptcre", "cptdeb"]].sum().reset_index()
                    c = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0}
                    d = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0}
                    for index, row in data_frame_compte.iterrows():
                        c[int(row['cptop'])] = float(row['cptcre'])
                        d[int(row['cptop'])] = float(row['cptdeb'])

                    serie = {}
                    serie['exercice'] = ex
                    serie['siret'] = data_frame_compte.iloc[0]['siret']
                    serie['organisme'] = data_frame_compte.iloc[0]['lbudg']
                    serie['type budget'] = data_frame_compte.iloc[0]['libelle_budget']
                    serie['nomenclature'] = data_frame_compte.iloc[0]['nomen']
                    serie['compte'] = compte
                    serie['BEDEB'] = d[1]
                    serie['BECRED'] = c[1]
                    serie['OBDEB'] = d[2]
                    serie['OBCRED'] = c[2]
                    serie['OBODEB'] = d[6]
                    serie['OBOCRED'] = c[6]
                    serie['ONBDEB'] = d[3] + d[4]
                    serie['ONBCRED'] = c[3] + c[4]
                    serie['ADEB'] = d[7]
                    serie['ACRED'] = c[7]
                    serie['OADEB'] = d[2] + d[3] + d[4] + d[7]
                    serie['OACRED'] = c[2] + c[3] + c[4] + c[7]
                    serie['BSDEB'] = d[1] + d[2] + d[3] + d[4] + d[7]
                    serie['BSCRED'] = c[1] + c[2] + c[3] + c[4] + c[7]
                    if serie['BSDEB'] > serie['BSCRED']:
                        serie['SDEB'] = serie['BSDEB'] - serie['BSCRED']
                        serie['SCRED'] = 0
                    else:
                        serie['SDEB'] = 0
                        serie['SCRED'] = serie['BSCRED'] - serie['BSDEB']
                    serie = pd.DataFrame(serie, columns=columns, index=[0])
                    data_frames = data_frames.append(serie)

        return data_frames
