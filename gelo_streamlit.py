import inspect
from typing import Callable, TypeVar
from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import plotly.express as px
import streamlit as st
import pandas as pd
import sys
import os

# Ajouter le répertoire 'package' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'package')))

from package.import_csv_data import import_csv
from package.data_processing import supprimer_colonnes_except_colonne
from package.renaming_columns import renommer_colonnes
from package.clean_columns import nettoyer_colonne
from package.filter_data import filtrer_dataframe
from package.convert_data import convertir_colonne
from package.mean_calcul import somme_revenus_par_groupes
from package.import_multiple_data import import_multiple_csv
from package.import_excel_data import import_excel


def process_airbnb_data():
    try:
        file1_name = os.path.join('dataset', 'reservations.csv')
        airbnb_data = pd.read_csv(file1_name, encoding='utf-8')

        if airbnb_data is not None:
            airbnb_data_reduit = supprimer_colonnes_except_colonne(airbnb_data, 'Statut', 7)
            nouveaux_noms = ["Statut_reservation", "Date_debut", "Date_fin", "Nombre_nuits", "Date_reservation", "Titre_annonce", "Revenus"]
            airbnb_data_renomme = renommer_colonnes(airbnb_data_reduit, nouveaux_noms)

            airbnb_data_renomme['Revenus'] = airbnb_data_renomme['Revenus'].apply(nettoyer_colonne)
            airbnb_data_renomme['Date_debut'] = pd.to_datetime(airbnb_data_renomme['Date_debut'], format='%d/%m/%Y', errors='coerce')
            airbnb_data_renomme['mois_annee'] = airbnb_data_renomme['Date_debut'].dt.strftime('%m/%Y')

            conditions = {"Statut_reservation": ["Annulée par le voyageur"], "Titre_annonce": ["Chambre Deluxe"]}
            airbnb_data_filtre = filtrer_dataframe(airbnb_data_renomme, conditions)

            airbnb_data_convert = convertir_colonne(airbnb_data_filtre, 'Revenus')
            airbnb_data_rev = somme_revenus_par_groupes(airbnb_data_convert, 'Titre_annonce', 'mois_annee', 'Revenus')
            return airbnb_data_rev
        else:
            st.error("Erreur lors de l'import des données Airbnb.")
            return None
    except Exception as e:
        st.error(f"Erreur lors de l'import des données Airbnb : {e}")
        return None


def process_booking_data():
    try:
        file_names = [
            "Arrivée du 2024-07-01 au 2024-07-31_cosya.csv",
            "Arrivée du 2024-08-01 au 2024-08-31_cosya.csv",
            "Arrivée du 2024-07-01 au 2024-07-31_mad.csv",
            "Arrivée du 2024-08-01 au 2024-08-31_mad.csv"
        ]
        dataset_folder = 'dataset'
        booking_dataframes = import_multiple_csv(file_names, dataset_folder, sep=';', encoding='latin1')

        if booking_dataframes:
            booking_data = pd.concat(booking_dataframes, ignore_index=True)
            nouveaux_noms = ["Numero_de_reservation", "Rerserve_par", "Nom_du_client", "Arrivee", "Depart", "Reserve_le", "Statut",
                             "Hebergement", "Personnes", "Adultes", "Enfants", "Ages_des_enfants", "Tarif", "Pourcentage_com",
                             "Montant_com", "Statut_du_paiement", "Moyen_de_paiement", "Remarques", "Groupe", "Booker_country",
                             "Motif_du_voyage", "Appareil", "Titre_annonce", "Duree_nuits", "Data_annulation", "Adresse", "Contact_clients"]

            booking_data_renomme = renommer_colonnes(booking_data, nouveaux_noms)
            booking_data_renomme['Tarif'] = booking_data_renomme['Tarif'].apply(nettoyer_colonne)
            booking_data_renomme['Montant_com'] = booking_data_renomme['Montant_com'].apply(nettoyer_colonne)

            booking_data_renomme = convertir_colonne(booking_data_renomme, 'Tarif')
            booking_data_renomme = convertir_colonne(booking_data_renomme, 'Montant_com')

            booking_data_renomme['Revenus'] = booking_data_renomme['Tarif'] - booking_data_renomme['Montant_com']
            booking_data_renomme['mois_annee'] = pd.to_datetime(booking_data_renomme['Arrivee'], errors='coerce').dt.strftime('%m/%Y')

            conditions = {"Statut": ["cancelled_by_guest"]}
            booking_data_filtre = filtrer_dataframe(booking_data_renomme, conditions)
            booking_data_rev = somme_revenus_par_groupes(booking_data_filtre, 'Titre_annonce', 'mois_annee', 'Revenus')
            return booking_data_rev
        else:
            st.error("Erreur lors de l'import des données Booking.")
            return None
    except Exception as e:
        st.error(f"Erreur lors de l'import des données Booking : {e}")
        return None


def process_charges_data():
    try:
        dataset_folder = 'dataset'
        file1 = os.path.join(dataset_folder, 'charge_salaire_cosyappart.xlsx')
        file2 = os.path.join(dataset_folder, 'charge_salaire_madoumier.xlsx')

        charge_cosy = pd.read_excel(file1)
        charge_madoumier = pd.read_excel(file2)

        multiple_charge = pd.concat([charge_cosy, charge_madoumier], ignore_index=True)

        if multiple_charge is not None:
            multiple_charge['mois_annee'] = pd.to_datetime(multiple_charge['mois_annee'], errors='coerce').dt.strftime('%m/%Y')
            charges_data_rev = somme_revenus_par_groupes(multiple_charge, 'Titre_annonce', 'mois_annee', 'Charges')
            return charges_data_rev
        else:
            st.error("Erreur lors de l'import des données de charges.")
            return None
    except Exception as e:
        st.error(f"Erreur lors de l'import des données de charges : {e}")
        return None


def concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev):
    try:
        config1 = os.path.join('dataset', 'annonce.csv')
        annonce_data = pd.read_csv(config1, encoding='utf-8')

        if annonce_data is not None:
            if 'Nom_original' in annonce_data.columns and 'Nom_uniformise' in annonce_data.columns:
                correspondance_noms = dict(zip(annonce_data['Nom_original'], annonce_data['Nom_uniformise']))
                booking_data_rev['Titre_annonce'] = booking_data_rev['Titre_annonce'].replace(correspondance_noms)

                airbnb_booking_data = pd.concat([airbnb_data_rev, booking_data_rev], ignore_index=True)
                airbnb_booking_data_rev = somme_revenus_par_groupes(
                    dataframe=airbnb_booking_data,
                    colonne_titre_annonce="Titre_annonce",
                    colonne_mois_annee="mois_annee",
                    colonne_revenus="Revenus"
                )
                return airbnb_booking_data_rev
            else:
                st.error("Colonnes 'Nom_original' ou 'Nom_uniformise' manquantes dans annonce.csv.")
                return None
        else:
            st.error("Erreur lors de l'import des données d'annonces.")
            return None
    except Exception as e:
        st.error(f"Erreur lors de l'import des données d'annonces : {e}")
        return None


def main():
    airbnb_data_rev = process_airbnb_data()
    booking_data_rev = process_booking_data()
    charges_data_rev = process_charges_data()

    if airbnb_data_rev is not None and booking_data_rev is not None:
        airbnb_booking_data_rev = concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev)
        
        if airbnb_booking_data_rev is not None and charges_data_rev is not None:
            final_data = pd.merge(airbnb_booking_data_rev, charges_data_rev, how='left', on=['Titre_annonce', 'mois_annee'])
            final_data['Profit'] = final_data['Revenus'] - final_data['Charges']

            st.write("Voici le tableau récapitulatif des revenus, charges et profits par annonce et mois:")
            st.write(final_data)

            fig = px.bar(
                final_data, x="mois_annee", y="Profit", color="Titre_annonce",
                labels={"mois_annee": "Mois/Année", "Profit": "Profits"}
            )
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
