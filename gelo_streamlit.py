import os
import streamlit as st
import pandas as pd
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

# Fonction pour lister les fichiers disponibles dans le répertoire courant
def list_files_in_directory():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    st.write(f"Répertoire actuel : {current_dir}")
    st.write(os.listdir(current_dir))

# Fonction pour charger un fichier via file_uploader ou à partir du dossier local
def upload_or_load_file(file_name, dataset_folder='dataset', file_uploader=False):
    if file_uploader:
        uploaded_file = st.file_uploader(f"Charger le fichier : {file_name}", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            if uploaded_file.name.endswith('.csv'):
                return pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                return pd.read_excel(uploaded_file)
        else:
            st.error(f"{file_name} non chargé via file_uploader.")
            return None
    else:
        # Si le fichier est dans le dépôt, le charger directement
        file_path = os.path.join(dataset_folder, file_name)
        if os.path.exists(file_path):
            return import_csv(file_path)
        else:
            st.error(f"Le fichier {file_name} n'existe pas dans le dossier {dataset_folder}.")
            return None

# Processus pour les données Airbnb
def process_airbnb_data():
    try:
        file1_name = 'reservations.csv'
        airbnb_data = upload_or_load_file(file1_name, file_uploader=False)  # Passez à True si vous voulez utiliser file_uploader

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
        st.error(f"Erreur lors du traitement des données Airbnb : {e}")
        return None

# Processus pour les données Booking
def process_booking_data():
    try:
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
            nouveaux_noms = ["Numero_de_reservation", "Reserve_par", "Nom_du_client", "Arrivee", "Depart", "Reserve_le", 
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
    except Exception as e:
        st.error(f"Erreur lors du traitement des données Booking : {e}")
        return None

# Processus pour les données de charges
def process_charges_data():
    try:
        multiple_charge = upload_or_load_file('charge_salaire_cosyappart.xlsx', file_uploader=False)  # Passez à True si vous voulez utiliser file_uploader
        if multiple_charge is not None:
            multiple_charge['mois_annee'] = multiple_charge['mois_annee'].dt.strftime('%m/%Y')
            charges_data_rev = somme_revenus_par_groupes(multiple_charge, 'Titre_annonce', 'mois_annee', 'Charges')
            return charges_data_rev
        else:
            st.error("Erreur lors de l'import des données de charges.")
            return None
    except Exception as e:
        st.error(f"Erreur lors du traitement des données de charges : {e}")
        return None

# Fonction pour concaténer les données Airbnb et Booking
def concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev):
    try:
        config1 = 'annonce.csv'
        annonce_data = upload_or_load_file(config1, file_uploader=False)  # Passez à True si vous voulez utiliser file_uploader

        if annonce_data is not None:
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
            st.error("Erreur lors de l'import des données d'annonces.")
            return None
    except Exception as e:
        st.error(f"Erreur lors de la concaténation des données Airbnb et Booking : {e}")
        return None

# Fonction principale
def main():
    st.title("Analyse des Revenus, Charges et Soldes Mensuels")
    st.write("Liste des fichiers dans le répertoire :")
    list_files_in_directory()  # Affiche les fichiers disponibles pour faciliter le débogage

    airbnb_data_rev = process_airbnb_data()
    booking_data_rev = process_booking_data()
    charges_data_rev = process_charges_data()

    if airbnb_data_rev is not None and booking_data_rev is not None:
        airbnb_booking_data_rev = concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev)

        if airbnb_booking_data_rev is not None and charges_data_rev is not None:
            solde_data = airbnb_booking_data_rev.copy()
            solde_data['Charges'] = charges_data_rev['Charges']
            solde_data['Solde'] = solde_data['Revenus'] - solde_data['Charges']
            
            st.write("Données finales avec solde calculé :")
            st.dataframe(solde_data)

            fig = px.line(solde_data, x='mois_annee', y='Solde', color='Titre_annonce', title="Solde par mois et annonce")
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
