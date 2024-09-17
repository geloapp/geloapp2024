import pandas as pd

def nettoyer_colonne(valeur):
    """
    Nettoie une valeur en remplaçant les virgules par des points
    et en supprimant le signe euro et les espaces.
    
    :param valeur: Valeur à nettoyer (supposée être une chaîne de caractères).
    :return: Valeur nettoyée.
    """
    if pd.notnull(valeur):  # Vérifie que la valeur n'est pas nulle
        valeur = str(valeur)  # Convertit la valeur en chaîne de caractères
        valeur = valeur.replace(',', '.')  # Remplace la virgule par un point
        valeur = valeur.replace('€', '').strip()  # Supprime le signe euro et les espaces autour
        valeur = valeur.replace('EUR', '').strip()  # Supprime le signe euro et les espaces autour
    return valeur
