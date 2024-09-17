import plotly.express as px
import streamlit as st
import pandas as pd
import os

from package.data_processing import supprimer_colonnes_except_colonne
from package.renaming_columns import renommer_colonnes
from package.clean_columns import nettoyer_colonne
from package.filter_data import filtrer_dataframe
from package.convert_data import convertir_colonne
from package.mean_calcul import somme_revenus_par_groupes

def import_csv_via_streamlit(file_name):
    uploaded_file = st.file_uploader(f"Téléchargez le fichier {file_name}", type="csv")
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    else:
        return None

def import_excel_via_streamlit(file_names):
    uploaded_files = st.file_uploader("Téléchargez les fichiers Excel", type="xlsx", accept_multiple_files=True)
    if uploaded_files:
        dfs = []
        for uploaded_file in uploaded_files:
            dfs.append(pd.read_excel(uploaded_file))
        return pd.concat(dfs, ignore_index=True)
    else:
        return None

def process_airbnb_data():
    airbnb_data = import_csv_via_streamlit('reservations.csv')

    if airbnb_data is not None:
        airbnb_data_reduit = supprimer_colonnes_except_colonne(airbnb_data, 'Statut', 7)
        nouveaux_noms = ["Statut_reservation", "Date_debut", "Date_fin", "Nombre_nuits", "Date_reservation",
                         "Titre_annonce", "Revenus"]
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
    booking_dataframes = []
    for i in range(4):  # Pour 4 fichiers Booking
        booking_data = import_csv_via_streamlit(f"Arrivée Booking (fichier {i+1})")
        if booking_data is not None:
            booking_dataframes.append(booking_data)

    if booking_dataframes:
        booking_data = pd.concat(booking_dataframes, ignore_index=True)

        nouveaux_noms = ["Numero_de_reservation", "Rerserve_par", "Nom_du_client", "Arrivee", "Depart", "Reserve_le",
                         "Statut", "Hebergement", "Personnes", "Adultes", "Enfants", "Ages_des_enfants", "Tarif",
                         "Pourcentage_com", "Montant_com", "Statut_du_paiement", "Moyen_de_paiement", "Remarques",
                         "Groupe", "Booker_country", "Motif_du_voyage", "Appareil", "Titre_annonce", "Duree_nuits",
                         "Data_annulation", "Adresse", "Contact_clients"]
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
    charges_data = import_excel_via_streamlit(['charge_salaire_cosyappart.xlsx', 'charge_salaire_madoumier.xlsx'])

    if charges_data is not None:
        charges_data['mois_annee'] = pd.to_datetime(charges_data['mois_annee'], errors='coerce').dt.strftime('%m/%Y')
        charges_data_rev = somme_revenus_par_groupes(charges_data, 'Titre_annonce', 'mois_annee', 'Charges')
        return charges_data_rev
    else:
        st.error("Erreur lors de l'import des données de charges.")
        return None

def concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev):
    annonce_data = import_csv_via_streamlit('annonce.csv')

    if annonce_data is not None:
        correspondance_noms = dict(zip(annonce_data['Nom_original'], annonce_data['Nom_uniformise']))
        booking_data_rev['Titre_annonce'] = booking_data_rev['Titre_annonce'].replace(correspondance_noms)

        airbnb_booking_data = pd.concat([airbnb_data_rev, booking_data_rev], ignore_index=True)
        airbnb_booking_data_rev = somme_revenus_par_groupes(airbnb_booking_data, 'Titre_annonce', 'mois_annee', 'Revenus')
        return airbnb_booking_data_rev
    else:
        st.error("Erreur lors de l'import des données d'annonces.")
        return None

def main():
    st.markdown("<h1 style='font-size:24px;'>Analyse des Revenus, Charges et Soldes Mensuels</h1>", unsafe_allow_html=True)
    st.markdown(
        "Découvrez une vue d'ensemble détaillée de vos revenus, charges, et soldes mensuels.",
        unsafe_allow_html=True
    )

    airbnb_data_rev = process_airbnb_data()
    booking_data_rev = process_booking_data()
    charges_data_rev = process_charges_data()

    if airbnb_data_rev is not None and booking_data_rev is not None:
        airbnb_booking_data_rev = concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev)

        if airbnb_booking_data_rev is not None and charges_data_rev is not None:
            final_data = pd.merge(airbnb_booking_data_rev, charges_data_rev, on=['Titre_annonce', 'mois_annee'], how='inner')
            final_data['Solde_mensuel'] = final_data['Revenus'] - final_data['Charges']
            final_data = final_data.fillna(0)

            fig_revenus = px.bar(final_data, x='mois_annee', y='Revenus', color='Titre_annonce', title='Mes revenus mensuels')
            fig_charges = px.bar(final_data, x='mois_annee', y='Charges', color='Titre_annonce', title='Mes charges mensuelles')
            fig_soldes = px.bar(final_data, x='mois_annee', y='Solde_mensuel', color='Titre_annonce', title='Mon solde mensuel')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.plotly_chart(fig_revenus, use_container_width=True)
            with col2:
                st.plotly_chart(fig_charges, use_container_width=True)
            with col3:
                st.plotly_chart(fig_soldes, use_container_width=True)

            st.write("Données :")
            st.dataframe(final_data)

if __name__ == "__main__":
    main
