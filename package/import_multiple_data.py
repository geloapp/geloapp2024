import pandas as pd
import os

def import_csv(file_name, dataset_folder='datasets', sep=',', encoding='utf-8'):
    """
    Importer un fichier CSV depuis le dossier de datasets.

    :param file_name: Nom du fichier CSV
    :param dataset_folder: Dossier contenant les fichiers CSV
    :param sep: Séparateur des colonnes dans le fichier CSV
    :param encoding: Encodage du fichier CSV
    :return: DataFrame contenant les données
    """
    file_path = os.path.join(dataset_folder, file_name)
    print(f"Tentative de lecture du fichier : {file_path}")  # Affiche le chemin du fichier pour vérification

    try:
        data = pd.read_csv(file_path, sep=sep, encoding=encoding)
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

def import_multiple_csv(file_names, dataset_folder='datasets', sep=',', encoding='utf-8'):
    """
    Importer plusieurs fichiers CSV depuis le dossier de datasets.

    :param file_names: Liste des noms de fichiers CSV
    :param dataset_folder: Dossier contenant les fichiers CSV
    :param sep: Séparateur des colonnes dans les fichiers CSV
    :param encoding: Encodage des fichiers CSV
    :return: Liste de DataFrames contenant les données
    """
    data_frames = []
    for file_name in file_names:
        data = import_csv(file_name, dataset_folder, sep, encoding)
        if data is not None:
            data_frames.append(data)
    return data_frames
