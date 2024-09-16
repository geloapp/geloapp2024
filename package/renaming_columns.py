def renommer_colonnes(dataframe, nouveaux_noms):
    """
    Renomme les colonnes d'un DataFrame avec les nouveaux noms spécifiés.

    :param dataframe: Le DataFrame original.
    :param nouveaux_noms: Liste des nouveaux noms de colonnes.
    :return: Un nouveau DataFrame avec les colonnes renommées.
    """
    dataframe.columns = nouveaux_noms
    return dataframe
