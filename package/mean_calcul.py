import pandas as pd

def somme_revenus_par_groupes(dataframe, colonne_titre_annonce, colonne_mois_annee, colonne_revenus):
    """
    Calcule la somme des revenus groupés par les colonnes spécifiées.
    
    :param dataframe: Le DataFrame contenant les données.
    :param colonne_titre_annonce: Nom de la colonne contenant les titres des annonces.
    :param colonne_mois_annee: Nom de la colonne contenant les mois/années.
    :param colonne_revenus: Nom de la colonne contenant les revenus.
    :return: Un DataFrame avec la somme des revenus groupés.
    """
    # Groupement par titre d'annonce et mois/année
    result = dataframe.groupby([colonne_titre_annonce, colonne_mois_annee])[colonne_revenus].sum().reset_index()
    return result
