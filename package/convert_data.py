# data_processing.py

import pandas as pd

def convertir_colonne(dataframe, nom_colonne):
    """
    Convertit une colonne spécifique d'un DataFrame en type numérique.

    :param dataframe: Le DataFrame contenant la colonne à convertir.
    :param nom_colonne: Nom de la colonne à convertir.
    :return: Le DataFrame avec la colonne spécifiée convertie en type numérique.
    """
    if nom_colonne in dataframe.columns:
        dataframe[nom_colonne] = pd.to_numeric(dataframe[nom_colonne], errors='coerce')
    else:
        print(f"La colonne '{nom_colonne}' n'existe pas dans le DataFrame.")
    return dataframe
