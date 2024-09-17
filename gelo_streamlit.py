import inspect
from typing import Callable, TypeVar

from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import plotly.express as px  # Ajout de plotly pour le graphique


import streamlit as st
import pandas as pd
import sys
import os


# Ajoutez le répertoire 'package' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'package')))

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
    # Importer les données Airbnb
    #file1_name = 'reservations.csv'
    file1_name = 'https://raw.githubusercontent.com/geloapp/geloapp2024/main/dataset/reservations.csv'
    airbnb_data = pd.read_csv(file1_name)
    #airbnb_data = import_csv(file1_name)

    if airbnb_data is not None:
        # Traiter les données Airbnb
        airbnb_data_reduit = supprimer_colonnes_except_colonne(airbnb_data, 'Statut', 7)
        nouveaux_noms = ["Statut_reservation", "Date_debut", "Date_fin", "Nombre_nuits", "Date_reservation",
                         "Titre_annonce", "Revenus"]
        airbnb_data_renomme = renommer_colonnes(airbnb_data_reduit, nouveaux_noms)
        airbnb_data_renomme['Revenus'] = airbnb_data_renomme['Revenus'].apply(nettoyer_colonne)
        airbnb_data_renomme['Date_debut'] = pd.to_datetime(airbnb_data_renomme['Date_debut'], format='%d/%m/%Y', errors='coerce')
        airbnb_data_renomme['mois_annee'] = airbnb_data_renomme['Date_debut'].dt.strftime('%m/%Y')

        # Filtrer les données
        conditions = {"Statut_reservation": ["Annulée par le voyageur"], "Titre_annonce": ["Chambre Deluxe"]}
        airbnb_data_filtre = filtrer_dataframe(airbnb_data_renomme, conditions)

        # Convertir les colonnes en format numérique
        airbnb_data_convert = convertir_colonne(airbnb_data_filtre, 'Revenus')

        # Calculer la somme des revenus par mois et par annonce
        airbnb_data_rev = somme_revenus_par_groupes(airbnb_data_convert, 'Titre_annonce', 'mois_annee', 'Revenus')
        return airbnb_data_rev
    else:
        st.error("Erreur lors de l'import des données Airbnb.")
        return None

def process_booking_data():
    # Liste des fichiers CSV Booking
    file_names = [
        "Arrivée du 2024-07-01 au 2024-07-31_cosya.csv",
        "Arrivée du 2024-08-01 au 2024-08-31_cosya.csv",
        "Arrivée du 2024-07-01 au 2024-07-31_mad.csv",
        "Arrivée du 2024-08-01 au 2024-08-31_mad.csv"
    ]

    # Import des données Booking
    dataset_folder = os.path.join(os.path.abspath('.'), 'dataset')
    booking_dataframes = import_multiple_csv(file_names, dataset_folder, sep=';', encoding='latin1')

    if booking_dataframes:
        # Concaténer les DataFrames
        booking_data = pd.concat(booking_dataframes, ignore_index=True)

        # Traiter les données Booking
        nouveaux_noms = ["Numero_de_reservation", "Rerserve_par", "Nom_du_client", "Arrivee", "Depart", "Reserve_le",
                         "Statut", "Hebergement", "Personnes", "Adultes", "Enfants", "Ages_des_enfants", "Tarif",
                         "Pourcentage_com", "Montant_com", "Statut_du_paiement", "Moyen_de_paiement", "Remarques",
                         "Groupe", "Booker_country", "Motif_du_voyage", "Appareil", "Titre_annonce", "Duree_nuits",
                         "Data_annulation", "Adresse", "Contact_clients"]
        booking_data_renomme = renommer_colonnes(booking_data, nouveaux_noms)

        # Nettoyage des colonnes
        booking_data_renomme['Tarif'] = booking_data_renomme['Tarif'].apply(nettoyer_colonne)
        booking_data_renomme['Montant_com'] = booking_data_renomme['Montant_com'].apply(nettoyer_colonne)

        # Conversion des colonnes en format numérique
        booking_data_renomme = convertir_colonne(booking_data_renomme, 'Tarif')
        booking_data_renomme = convertir_colonne(booking_data_renomme, 'Montant_com')

        # Calcul des revenus
        booking_data_renomme['Revenus'] = booking_data_renomme['Tarif'] - booking_data_renomme['Montant_com']
        booking_data_renomme['mois_annee'] = pd.to_datetime(booking_data_renomme['Arrivee'], errors='coerce').dt.strftime('%m/%Y')

        # Filtrer les données
        conditions = {"Statut": ["cancelled_by_guest"]}
        booking_data_filtre = filtrer_dataframe(booking_data_renomme, conditions)

        # Calculer la somme des revenus
        booking_data_rev = somme_revenus_par_groupes(booking_data_filtre, 'Titre_annonce', 'mois_annee', 'Revenus')
        return booking_data_rev
    else:
        st.error("Erreur lors de l'import des données Booking.")
        return None

def process_charges_data():
    # Importer les fichiers de charges Excel
    multiple_charge = import_excel(['charge_salaire_cosyappart.xlsx', 'charge_salaire_madoumier.xlsx'], dataset_folder='dataset')

    if multiple_charge is not None:
        # Conversion du format de la colonne mois/année
        multiple_charge['mois_annee'] = multiple_charge['mois_annee'].dt.strftime('%m/%Y')

        # Calcul des charges par mois et par annonce
        charges_data_rev = somme_revenus_par_groupes(multiple_charge, 'Titre_annonce', 'mois_annee', 'Charges')
        return charges_data_rev
    else:
        st.error("Erreur lors de l'import des données de charges.")
        return None

def concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev):
    # Importer le fichier de configuration des annonces
    config1 = 'https://raw.githubusercontent.com/geloapp/geloapp2024/main/dataset/annonce.csv'
    annonce_data = pd.read_csv(config1)
    #config1 = 'annonce.csv'
    #annonce_data = import_csv(config1)

    if annonce_data is not None:
        # Créer un dictionnaire de correspondance à partir du fichier CSV
        correspondance_noms = dict(zip(annonce_data['Nom_original'], annonce_data['Nom_uniformise']))

        # Uniformiser les noms dans df_airbnb en utilisant la correspondance
        booking_data_rev['Titre_annonce'] = booking_data_rev['Titre_annonce'].replace(correspondance_noms)

        # Concaténer les deux DataFrames
        airbnb_booking_data = pd.concat([airbnb_data_rev, booking_data_rev], ignore_index=True)

        # Utiliser la fonction pour faire la somme des revenus
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


# ... (tes autres importations et fonctions)

#def main():
    #st.title("Analyse des Revenus, Charges et Soldes Mensuels")
def main():
    # Utilisation de Markdown pour personnaliser la taille du titre
    st.markdown("<h1 style='font-size:24px;'>Analyse des Revenus, Charges et Soldes Mensuels</h1>", unsafe_allow_html=True)
    
    # Phrase d'accroche
    st.markdown(
        "Découvrez une vue d'ensemble détaillée de vos revenus, charges, et soldes mensuels. "
        "Cette analyse vous aide à mieux comprendre les fluctuations financières et à optimiser la gestion de vos annonces pour un rendement maximal.",
        unsafe_allow_html=True
    )

    airbnb_data_rev = process_airbnb_data()
    booking_data_rev = process_booking_data()
    charges_data_rev = process_charges_data()

    if airbnb_data_rev is not None and booking_data_rev is not None:
        # Concaténer les données Airbnb et Booking
        airbnb_booking_data_rev = concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev)

        if airbnb_booking_data_rev is not None and charges_data_rev is not None:
            # Fusionner avec les données de charges
            final_data = pd.merge(airbnb_booking_data_rev, charges_data_rev, on=['Titre_annonce', 'mois_annee'], how='inner')
            final_data['Solde_mensuel'] = final_data['Revenus'] - final_data['Charges']

            # **Convertir les colonnes au bon type**
            final_data['Revenus'] = pd.to_numeric(final_data['Revenus'], errors='coerce')
            final_data['Charges'] = pd.to_numeric(final_data['Charges'], errors='coerce')
            final_data['Solde_mensuel'] = pd.to_numeric(final_data['Solde_mensuel'], errors='coerce')

            # Remplacer les valeurs NaN (s'il y en a) par 0
            final_data = final_data.fillna(0)

            # **Créer un histogramme des revenus par mois et par annonce**
            fig_revenus = px.bar(
                final_data, 
                x='mois_annee', 
                y='Revenus', 
                color='Titre_annonce', 
                labels={'mois_annee': 'Date', 'Revenus': 'Revenus (€)'}, 
                title='Mes revenus mensuels',
                barmode='group',
                text='Revenus',  # Ajoute les étiquettes de données
                color_discrete_sequence=['#FF8C00', '#FFD700']  # Orange foncé et orange clair
                #color_discrete_sequence=px.colors.qualitative.Pastel  # Choix des couleurs pastel
            )
            fig_revenus.update_traces(texttemplate='%{text:.2s}', textposition='outside')

            # Réduire la taille des labels des axes et des titres
            fig_revenus.update_layout(
                xaxis_title_font=dict(size=10),
                yaxis_title_font=dict(size=10),
                title_font=dict(size=14),
                legend_font=dict(size=10)
            )

            # **Créer un histogramme des charges par mois et par annonce**
            fig_charges = px.bar(
                final_data, 
                x='mois_annee', 
                y='Charges', 
                color='Titre_annonce', 
                labels={'mois_annee': 'Date', 'Charges': 'Charges (€)'}, 
                title='Mes charges mensuelles',
                barmode='group',
                text='Charges',  # Ajoute les étiquettes de données
                color_discrete_sequence=['#FF0000', '#FFA07A']  # Rouge vif et rouge clair
                #color_discrete_sequence=px.colors.qualitative.Bold  # Choix des couleurs plus intenses
            )
            fig_charges.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            # Réduire la taille des labels des axes et des titres
            fig_charges.update_layout(
                xaxis_title_font=dict(size=10),
                yaxis_title_font=dict(size=10),
                title_font=dict(size=14),
                legend_font=dict(size=10)
            )
            # **Créer un histogramme des soldes mensuels par mois et par annonce**
            fig_soldes = px.bar(
                final_data, 
                x='mois_annee', 
                y='Solde_mensuel', 
                color='Titre_annonce', 
                labels={'mois_annee': 'Date', 'Solde_mensuel': 'Solde Mensuel (€)'}, 
                title='Mon solde mensuel',
                barmode='group',
                text='Solde_mensuel',  # Ajoute les étiquettes de données
                color_discrete_sequence=['#006400', '#90EE90']  # Vert foncé et vert clair
                #color_discrete_sequence=['#FF8C00', '#FFD700']  # Orange foncé et orange clair
                #color_discrete_sequence=px.colors.qualitative.Prism  # Autre palette de couleurs
            )
            fig_soldes.update_traces(texttemplate='%{text:.2s}', textposition='outside')

            # Réduire la taille des labels des axes et des titres
            fig_soldes.update_layout(
                xaxis_title_font=dict(size=10),
                yaxis_title_font=dict(size=10),
                title_font=dict(size=14),
                legend_font=dict(size=10)
            )

            # Afficher les graphiques sur la même ligne avec Streamlit columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.plotly_chart(fig_revenus, use_container_width=True)

            with col2:
                st.plotly_chart(fig_charges, use_container_width=True)

            with col3:
                st.plotly_chart(fig_soldes, use_container_width=True)

            # Afficher le tableau en bas de page
            st.write("Données :")
            st.dataframe(final_data)
            
        else:
            st.error("Erreur lors de la concaténation des données Airbnb et Booking.")
    else:
        st.error("Erreur lors du traitement des données.")

if __name__ == "__main__":
    main()



