import pandas as pd

def filtrer_dataframe(dataframe, conditions):
    """
    Filtre les lignes d'un DataFrame en fonction des conditions spécifiées.

    :param dataframe: Le DataFrame à filtrer.
    :param conditions: Dictionnaire où les clés sont les noms de colonnes et les valeurs sont des listes de valeurs à exclure.
    :return: Un DataFrame filtré.
    """
    # Créer un masque initial avec toutes les valeurs True
    masque = pd.Series([True] * len(dataframe))

    # Appliquer les conditions
    for colonne, valeurs_a_exclure in conditions.items():
        masque = masque & ~dataframe[colonne].isin(valeurs_a_exclure)

    # Retourner le DataFrame filtré
    return dataframe[masque]
