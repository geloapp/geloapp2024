# package/import_csv.py

import pandas as pd
import os

def import_csv(file_name, dataset_folder='dataset'):
    """
    Importer un fichier CSV depuis le dossier de datasets.
    
    :param file_name: Nom du fichier CSV
    :param dataset_folder: Dossier contenant les fichiers CSV
    :return: DataFrame contenant les données
    """
    # Chemin complet du fichier CSV
    file_path = os.path.join(dataset_folder, file_name)
    
    # Lire le fichier CSV
    try:
        data = pd.read_csv(file_path, sep=',')
        return data
    except FileNotFoundError:
        print(f"Le fichier {file_name} n'a pas été trouvé dans le dossier {dataset_folder}.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Le fichier {file_name} est vide.")
        return None
    except pd.errors.ParserError:
        print(f"Erreur de parsing pour le fichier {file_name}.")
        return None
