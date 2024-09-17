import streamlit as st
import pandas as pd
import os
import plotly.express as px

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
    file1_name = 'reservations.csv'
    airbnb_data = import_csv(file1_name)

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

def process_booking_data():
    file_names = [
        "Arrivée du 2024-07-01 au 2024-07-31_cosya.csv",
        "Arrivée du 2024-08-01 au 2024-08-31_cosya.csv",
        "Arrivée du 2024-07-01 au 2024-07-31_mad.csv",
        "Arrivée du 2024-08-01 au 2024-08-31_mad.csv"
    ]

    dataset_folder = os.path.join(os.path.abspath('.'), 'dataset')
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

def process_charges_data():
    multiple_charge = import_excel(['charge_salaire_cosyappart.xlsx', 'charge_salaire_madoumier.xlsx'], dataset_folder='dataset')

    if multiple_charge is not None:
        multiple_charge['mois_annee'] = multiple_charge['mois_annee'].dt.strftime('%m/%Y')
        charges_data_rev = somme_revenus_par_groupes(multiple_charge, 'Titre_annonce', 'mois_annee', 'Charges')
        return charges_data_rev
    else:
        st.error("Erreur lors de l'import des données de charges.")
        return None

def concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev):
    config1 = 'annonce.csv'
    annonce_data = import_csv(config1)

    if annonce_data is not None:
        correspondance_noms = dict(zip(annonce_data['Nom_original'], annonce_data['Nom_uniformise']))
        booking_data_rev['Titre_annonce'] = booking_data_rev['Titre_annonce'].replace(correspondance_noms)

        try:
            airbnb_booking_data = pd.concat([airbnb_data_rev, booking_data_rev], ignore_index=True)
        except Exception as e:
            st.error(f"Erreur lors de la concaténation : {e}")
            return None

        st.write("Colonnes Airbnb :", airbnb_data_rev.columns)
        st.write("Colonnes Booking :", booking_data_rev.columns)
        st.write("Colonnes après concaténation :", airbnb_booking_data.columns)

        airbnb_booking_data_rev = somme_revenus_par_groupes(
            dataframe=airbnb_booking_data,
            colonne_titre_annonce="Titre_annonce",
            colonne_mois_annee="mois_annee",
            colonne_revenus="Revenus"
        )
        return airbnb_booking_data_rev
    else:
        st.error("Erreur lors de l'import des données d'annonces.")
        return None

def main():
    st.markdown("<h1 style='font-size:24px;'>Analyse des Revenus, Charges et Soldes Mensuels</h1>", unsafe_allow_html=True)

    airbnb_data_rev = process_airbnb_data()
    booking_data_rev = process_booking_data()
    charges_data_rev = process_charges_data()

    if airbnb_data_rev is not None and booking_data_rev is not None:
        airbnb_booking_data_rev = concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev)

        if airbnb_booking_data_rev is not None and charges_data_rev is not None:
            final_data = pd.merge(airbnb_booking_data_rev, charges_data_rev, on=['Titre_annonce', 'mois_annee'], how='inner')
            final_data['Solde_mensuel'] = final_data['Revenus'] - final_data['Charges']

            final_data['Revenus'] = pd.to_numeric(final_data['Revenus'], errors='coerce')
            final_data['Charges'] = pd.to_numeric(final_data['Charges'], errors='coerce')
            final_data['Solde_mensuel'] = pd.to_numeric(final_data['Solde_mensuel'], errors='coerce')

            final_data = final_data.fillna(0)

            fig_revenus = px.bar(
                final_data, 
                x='mois_annee', 
                y='Revenus', 
                color='Titre_annonce', 
                labels={'mois_annee': 'Date', 'Revenus': 'Revenus (€)'}, 
                title='Mes revenus mensuels',
                barmode='group',
                text='Revenus',
                color_discrete_sequence=['#FF8C00', '#FFD700']
            )
            fig_revenus.update_traces(texttemplate='%{text:.2s}', textposition='outside')

            fig_charges = px.bar(
                final_data, 
                x='mois_annee', 
                y='Charges', 
                color='Titre_annonce', 
                labels={'mois_annee': 'Date', 'Charges': 'Charges (€)'}, 
                title='Mes charges mensuelles',
                barmode='group',
                text='Charges',
                color_discrete_sequence=['#FF0000', '#FFA07A']
            )
            fig_charges.update_traces(texttemplate='%{text:.2s}', textposition='outside')

            fig_soldes = px.bar(
                final_data, 
                x='mois_annee', 
                y='Solde_mensuel', 
                color='Titre_annonce', 
                labels={'mois_annee': 'Date', 'Solde_mensuel': 'Solde Mensuel (€)'}, 
                title='Mes soldes mensuels',
                barmode='group',
                text='Solde_mensuel',
                color_discrete_sequence=['#32CD32', '#7CFC00']
            )
            fig_soldes.update_traces(texttemplate='%{text:.2s}', textposition='outside')

            st.plotly_chart(fig_revenus)
            st.plotly_chart(fig_charges)
            st.plotly_chart(fig_soldes)

if __name__ == "__main__":
    main()
