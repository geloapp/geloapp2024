import pandas as pd
import os

def import_excel(file_names, dataset_folder='dataset'):
    """
    Importer un ou plusieurs fichiers Excel depuis le dossier de datasets.
    
    :param file_names: Liste des noms des fichiers Excel à importer (ou un seul fichier en tant que chaîne)
    :param dataset_folder: Dossier contenant les fichiers Excel
    :return: DataFrame concaténé contenant les données de tous les fichiers Excel
    """
    if isinstance(file_names, str):
        # Si un seul fichier est passé, on le transforme en liste
        file_names = [file_names]
    
    # Liste pour stocker les DataFrames importés
    dataframes = []

    for file_name in file_names:
        # Chemin complet du fichier Excel
        file_path = os.path.join(dataset_folder, file_name)
        
        # Lire le fichier Excel
        try:
            data = pd.read_excel(file_path)
            dataframes.append(data)
        except FileNotFoundError:
            print(f"Le fichier {file_name} n'a pas été trouvé dans le dossier {dataset_folder}.")
        except pd.errors.EmptyDataError:
            print(f"Le fichier {file_name} est vide.")
        except ValueError as ve:
            print(f"Erreur lors de l'importation du fichier {file_name} : {ve}")
        except Exception as e:
            print(f"Une erreur inattendue s'est produite lors de l'importation du fichier {file_name} : {e}")

    if dataframes:
        # Concaténer les DataFrames s'il y en a plusieurs
        return pd.concat(dataframes, ignore_index=True)
    else:
        print("Aucun fichier valide n'a été importé.")
        return None
