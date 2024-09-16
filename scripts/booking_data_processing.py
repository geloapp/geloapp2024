import sys
import os

# Ajoutez le répertoire 'package' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'package')))

import subprocess

import pandas as pd
from package.import_multiple_data import import_multiple_csv
from package.renaming_columns import renommer_colonnes
from package.clean_columns import nettoyer_colonne
from package.convert_data import convertir_colonne
from package.filter_data import filtrer_dataframe
from package.mean_calcul import somme_revenus_par_groupes


def process_booking_data(file_paths):
    booking_data = import_multiple_csv(file_paths, sep=';', encoding='latin1')

    # Concaténation
    booking_data = pd.concat(booking_data, ignore_index=True)

    # Renommage des colonnes
    booking_data = renommer_colonnes(booking_data, ["Numero_de_reservation", "Arrivee", "Revenus", ...])

    # Nettoyage des données
    booking_data['Tarif'] = booking_data['Tarif'].apply(nettoyer_colonne)
    booking_data['Montant_com'] = booking_data['Montant_com'].apply(nettoyer_colonne)

    # Calcul des revenus nets
    booking_data['Revenus'] = booking_data['Tarif'] - booking_data['Montant_com']
    booking_data['mois_annee'] = booking_data['Arrivee'].dt.strftime('%m/%Y')

    # Filtrage et agrégation
    conditions = {"Statut": ["cancelled_by_guest"]}
    booking_data = filtrer_dataframe(booking_data, conditions)

    booking_data_rev = somme_revenus_par_groupes(
        dataframe=booking_data,
        colonne_titre_annonce="Titre_annonce",
        colonne_mois_annee="mois_annee",
        colonne_revenus="Revenus"
    )

    return booking_data_rev
