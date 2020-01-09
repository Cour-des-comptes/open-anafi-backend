# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 12:25:59 2018
Updated on Tuesday May 21 2019

@author: sclair
@author: avalingot
"""


import easygui
import requests
import json
import os
import pandas as pd
import datetime
import time
from pandas import ExcelWriter


def select_api():
    # fonction qui permet de sélectionner l'API sur laquelle vont être exécutées les analyses
    ApiEndpoint = ''
    env = easygui.choicebox(msg="Sélectionner l'environnement d'exécution des analyses", title='Et hop on clique :-)', choices=('Production','Recette','DEV'))
    if env == 'DEV':
        ApiEndpoint = 'http://openanafi-dev.ccomptes.re7'
    if env == 'Recette':
        ApiEndpoint = 'http://api-openanafi-rec.ccomptes.re7'
    if env == 'Production':
        ApiEndpoint = 'https://api-openanafi.ccomptes.fr'
    print('Environnement : ' + env)
    return(ApiEndpoint,env)
    
    
def get_token(ApiEndpoint):
    # fonction qui permet de récupérer le token nécessaire pour la génération des reports
        # Boite de dialogue pour récupérer login et mot de passe
    msg = "Saisie du login et du mot de passe"
    title = "Connexion à l'API : " + env
    fieldNames = ['Username', 'Password']
    fieldValues = []  # valeurs vides par défaut
    (user,pwd) = easygui.multenterbox(msg, title, fieldNames)
        # récupération du token auprès de l'API
    url_token = ApiEndpoint + '/users/authenticate/'
    auth =  {
            "username": user,
            "password": pwd
            }
    r = requests.post(url_token, json = auth, verify = False )
    token = 'Bearer ' + r.json()['token']
    head = {'Authorization': token}
    return(head)

def get_frame(ApiEndpoint):
    # fonction qui permet d'afficher les ID des trames exécutables sur un environnement donné
    texte = ''
    r = requests.get(url = ApiEndpoint  + '/frames/',  headers = token, verify = False)
    t = str(r.json())
    i = t.find("id\'")
    while i >= 0 :
        t = t[i:]
        j = t.find(',')
        id_i = t[:j].replace("id\': ","")
        k = t.find('name')
        t = t[k:]
        l = t.find("\',")
        name_i = t[:l].replace("name\': \'","")
        texte = texte + str('ID n° ' + id_i + ' - Etat : ' + name_i + '\n')
        i = t.find("id\'")
    title = "Saisie de l'ID du type d'état à générer"
    msg = "\nListe des états de l'API : " + env + ' :\n\n' +  texte 
    fieldNames = ['N°id : ']
    frame = int(easygui.multenterbox(msg, title, fieldNames)[0])
    d = texte.find('ID n° ' + str(frame)) + 6
    etat = texte[d:]
    f = etat.find('\n')
    trame = etat[:f]
    print ('Etat sélectionné : ' + trame)
    return(frame,trame)
    

# On définit l'environnement vers lequel va pointer le script
(ApiEndpoint,env) = select_api()


# on récupère le tocken
token = get_token(ApiEndpoint)

# on fait sélectionner l'id de l'état à produire
(frame,trame) = get_frame(ApiEndpoint)

# Boite de dialogue pour choisir le fichier dans lequel figurent les informations pour lancement des analyses M22
file_list = easygui.fileopenbox(msg= "Fichier Excel contenant les informations d'exécution", title='Choisir un fichier', default=r'C:\Users\smarcheix\Documents\2019\API Open Anafi\Source\*.xlsx', filetypes=None, multiple=False)
print('Fichier input : ' + file_list)

# on définit le path où seront déposés les fichiers produits
path = easygui.diropenbox(msg='Sélectionner un dossier cible pour les analyses', default='C:\\Users\\smarcheix\\Documents\\2019\\API Open Anafi\\Export')
print('Répertoire de sortie : ' + path)

# on créé un dataframe avec les informations des états à produire
df_liste = pd.read_excel(file_list, converters={'IDENTIFIANT':str,'CODE_DEPARTEMENT':str})
df_liste['id'] = 0
df_liste['status'] = 'None'
df_liste['file'] = 'None'

# Boucle de génération de la demande d'analyse M22
i=-1
for index, row in df_liste.iterrows():
    i=i+1
    siret = [row['IDENTIFIANT']]
    ex_min = row['EXERCICE_MIN']
    ex_max = row['EXERCICE_MAX']
    datas = {
        "frame": frame,
        "financial_year_min": ex_min,
        "financial_year_max": ex_max,
        "identifiers": siret,
        "identifiers_type": "SIRET"
    }    
    r = requests.post(url = ApiEndpoint  + '/reports/' , json = datas, headers = token, verify = False)
    rid = r.json()['report_id']
    df_liste.at[i, 'id'] = rid
    df_liste.at[i, 'status'] = 'PENDING'

# Boucle de constatation du statut et éventuel téléchargement
nb_ini = 0
finish = 'not'
while finish == 'not':
    i=-1
    for index, row in df_liste.iterrows():
        i=i+1
        # On ne gère que les enregistrements pour lesquels le dernier état est pending
        if row['status'] == 'PENDING':
            # On récupère l'état actuel 
            rid = row['id']
            url_stat = ApiEndpoint + '/reports/' + str(rid) + '/' 
            s = requests.get(url = url_stat, headers = token, verify = False) 
            data = s.json()
            etat = data['state']
            # On met à jour l'état
            df_liste.at[i, 'status'] = etat
            # Si c'est done on lance le téléchargement
            if etat == 'DONE':
                url_down = ApiEndpoint + '/reports/' + str(rid) + '/download'
                file_export = '\\' + env +'_Etat_' + str(frame) + '_' + row['IDENTIFIANT'] + '_' + str(row['EXERCICE_MIN']) + '_' + str(row['EXERCICE_MAX']) + '_' + row['LIBELLE_DE_BUDGET'] + ' ' + (str(datetime.datetime.now()).replace('.',':').replace(':',''))[:13]+'h'+(str(datetime.datetime.now()).replace('.',':').replace(':',''))[13:15] + '.xlsx'
                file_export = file_export.replace(' ','_')
                file_export = path + file_export
                s = requests.get(url = url_down, headers = token,verify = False )
                open(file_export, 'wb').write(s.content)
                df_liste.at[i, 'status'] = etat
                file = data['name']
                df_liste.at[i, 'file'] = file_export
            if etat == 'FAILED':
                df_liste.at[i, 'status'] = etat
    # On vérifie s'il reste des records au statut pending            
    df_check = df_liste[df_liste['status'] == 'PENDING']
    if df_check.empty:
        finish = 'yes'
        print('Traitement terminé :-) ')
    else:
        nb = len(df_check.index)
        if nb != nb_ini:
            nb_ini = nb
            print ('Il reste ' + str(nb) + ' état(s) au statut pending')
        time.sleep(30)
                
# Export du fichier log résultat
file_exp = path + '\\Log_Résultat_' + (str(datetime.datetime.now()).replace('.',':').replace(':',''))[:13]+'h'+(str(datetime.datetime.now()).replace('.',':').replace(':',''))[13:15] + '.xlsx'
writer = ExcelWriter(file_exp)
df_liste.to_excel(writer, 'retour')
writer.save()


