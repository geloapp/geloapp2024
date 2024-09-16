import sys
import os

# Ajoutez le répertoire 'package' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'package')))

import subprocess

import pandas as pd
from package.import_excel_data import import_excel
from package.mean_calcul import somme_revenus_par_groupes

def process_charges(file_paths):
    charges_data = import_excel(file_paths, dataset_folder='dataset')

    # Conversion des formats de date
    charges_data['mois_annee'] = charges_data['mois_annee'].dt.strftime('%m/%Y')

    # Calcul des charges par mois et par annonce
    charges_data_rev = somme_revenus_par_groupes(
        dataframe=charges_data,
        colonne_titre_annonce="Titre_annonce",
        colonne_mois_annee="mois_annee",
        colonne_revenus="Charges"
    )

    return charges_data_rev
