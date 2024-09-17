import sys
import os

# Ajoutez le répertoire 'package' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'package')))

import subprocess

import pandas as pd
from package.import_csv_data import import_csv
from package.data_processing import supprimer_colonnes_except_colonne
from package.renaming_columns import renommer_colonnes
from package.clean_columns import nettoyer_colonne
from package.filter_data import filtrer_dataframe
from package.convert_data import convertir_colonne
from package.mean_calcul import somme_revenus_par_groupes


def process_airbnb_data(file_path):
    airbnb_data = import_csv(file_path)

    # Nettoyage des colonnes
    airbnb_data = supprimer_colonnes_except_colonne(airbnb_data, 'Statut', 7)
    airbnb_data = renommer_colonnes(airbnb_data, ["Statut_reservation", "Date_debut", "Date_fin", "Revenus", ...])

    # Autres transformations
    airbnb_data['Revenus'] = airbnb_data['Revenus'].apply(nettoyer_colonne)
    airbnb_data['Date_debut'] = pd.to_datetime(airbnb_data['Date_debut'], format='%d/%m/%Y', errors='coerce')
    airbnb_data['mois_annee'] = airbnb_data['Date_debut'].dt.strftime('%m/%Y')

    # Filtrage
    conditions = {"Statut_reservation": ["Annulée par le voyageur"]}
    airbnb_data = filtrer_dataframe(airbnb_data, conditions)

    # Conversion des données
    airbnb_data = convertir_colonne(airbnb_data, 'Revenus')

    # Calcul des revenus mensuels
    airbnb_data_rev = somme_revenus_par_groupes(
        dataframe=airbnb_data,
        colonne_titre_annonce="Titre_annonce",
        colonne_mois_annee="mois_annee",
        colonne_revenus="Revenus"
    )

    return airbnb_data_rev
