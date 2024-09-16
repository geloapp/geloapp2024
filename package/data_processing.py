import pandas as pd

def supprimer_colonnes_except_colonne(dataframe, colonne_conserve, nombre_colonnes_a_supprimer):
    """
    Supprime un certain nombre de colonnes d'un DataFrame tout en conservant une colonne spécifiée.

    :param dataframe: Le DataFrame original.
    :param colonne_conserve: Le nom de la colonne à conserver.
    :param nombre_colonnes_a_supprimer: Le nombre de colonnes à supprimer depuis le début du DataFrame.
    :return: Un nouveau DataFrame avec les colonnes spécifiées supprimées, sauf celle à conserver.
    """
    # Vérifier si la colonne à conserver est dans le DataFrame
    if colonne_conserve not in dataframe.columns:
        raise ValueError(f"La colonne '{colonne_conserve}' n'existe pas dans le DataFrame.")

    # Sélectionner la colonne à conserver
    colonne_conserve_data = dataframe[colonne_conserve]
    
    # Supprimer les premières colonnes spécifiées
    dataframe_reduit = dataframe.iloc[:, nombre_colonnes_a_supprimer:]
    
    # Ajouter la colonne à conserver au DataFrame réduit
    dataframe_reduit.insert(0, colonne_conserve, colonne_conserve_data)
    
    return dataframe_reduit
