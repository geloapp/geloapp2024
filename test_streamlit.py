import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import plotly.express as px  # Ajout de plotly pour le graphique

def process_airbnb_data():
    # Importer les données Airbnb
    file1_name = 'reservations.csv'
    airbnb_data = import_csv(file1_name)

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
    config1 = 'annonce.csv'
    annonce_data = import_csv(config1)

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

# Ajoutez le répertoire 'package' au chemin de recherche des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'package')))

# Import des fonctions spécifiques depuis vos modules
from package.import_csv_data import import_csv
from package.data_processing import supprimer_colonnes_except_colonne
from package.renaming_columns import renommer_colonnes
from package.clean_columns import nettoyer_colonne
from package.filter_data import filtrer_dataframe
from package.convert_data import convertir_colonne
from package.mean_calcul import somme_revenus_par_groupes
from package.import_multiple_data import import_multiple_csv
from package.import_excel_data import import_excel


# --- FONCTIONS --- #
# Vous pouvez garder ici toutes vos fonctions comme `process_airbnb_data()`, `process_booking_data()`, etc.
# (les fonctions restent inchangées par rapport à votre code original)


# --- PAGE 1 : ANALYSE DES REVENUS, CHARGES ET SOLDES --- #
def page1():
    st.markdown("<h1 style='font-size:24px;'>Analyse des Revenus, Charges et Soldes Mensuels</h1>", unsafe_allow_html=True)
    st.markdown(
        "Découvrez une vue d'ensemble détaillée de vos revenus, charges, et soldes mensuels. "
        "Cette analyse vous aide à mieux comprendre les fluctuations financières et à optimiser la gestion de vos annonces pour un rendement maximal.",
        unsafe_allow_html=True
    )

    airbnb_data_rev = process_airbnb_data()
    booking_data_rev = process_booking_data()
    charges_data_rev = process_charges_data()

    if airbnb_data_rev is not None and booking_data_rev is not None:
        airbnb_booking_data_rev = concatenate_airbnb_booking_data(airbnb_data_rev, booking_data_rev)

        if airbnb_booking_data_rev is not None and charges_data_rev is not None:
            # Fusionner les données Airbnb, Booking et charges
            final_data = pd.merge(airbnb_booking_data_rev, charges_data_rev, on=['Titre_annonce', 'mois_annee'], how='inner')
            final_data['Solde_mensuel'] = final_data['Revenus'] - final_data['Charges']

            # Convertir les colonnes au bon format et remplacer les valeurs NaN par 0
            final_data['Revenus'] = pd.to_numeric(final_data['Revenus'], errors='coerce')
            final_data['Charges'] = pd.to_numeric(final_data['Charges'], errors='coerce')
            final_data['Solde_mensuel'] = pd.to_numeric(final_data['Solde_mensuel'], errors='coerce')
            final_data = final_data.fillna(0)

            # Créer les graphiques avec Plotly
            fig_revenus = px.bar(
                final_data, 
                x='mois_annee', 
                y='Revenus', 
                color='Titre_annonce', 
                title='Mes revenus mensuels',
                barmode='group',
                text='Revenus',
                color_discrete_sequence=['#FF8C00', '#FFD700']
            )
            fig_charges = px.bar(
                final_data, 
                x='mois_annee', 
                y='Charges', 
                color='Titre_annonce', 
                title='Mes charges mensuelles',
                barmode='group',
                text='Charges',
                color_discrete_sequence=['#FF0000', '#FFA07A']
            )
            fig_soldes = px.bar(
                final_data, 
                x='mois_annee', 
                y='Solde_mensuel', 
                color='Titre_annonce', 
                title='Mon solde mensuel',
                barmode='group',
                text='Solde_mensuel',
                color_discrete_sequence=['#006400', '#90EE90']
            )

            # Afficher les graphiques et les données
            col1, col2, col3 = st.columns(3)
            col1.plotly_chart(fig_revenus, use_container_width=True)
            col2.plotly_chart(fig_charges, use_container_width=True)
            col3.plotly_chart(fig_soldes, use_container_width=True)
            st.dataframe(final_data)

        else:
            st.error("Erreur lors de la concaténation des données Airbnb et Booking.")
    else:
        st.error("Erreur lors du traitement des données.")


# --- PAGE 2 : FORMULAIRES DE CALCUL DU REVENU IMPOSABLE --- #
import streamlit as st
import pandas as pd

def page2():
    # Titre de la page
    st.markdown("<h1 style='font-size:24px;'>Revenus imposables (micro-bic ou réel)</h1>", unsafe_allow_html=True)
    
    # Description de la page
    st.markdown(
        """<p>
        Découvrez facilement quel régime fiscal vous convient le mieux et estimez votre revenu imposable pour vos locations saisonnières. Que vous optiez pour le régime <strong>Micro-BIC</strong> ou le <strong>Régime Réel</strong>, notre outil calcule automatiquement votre revenu imposable en tenant compte des spécificités de chaque régime.
        </p>
        <p><strong>Régime Micro-BIC :</strong></p>
        <p>Le régime Micro-BIC est un régime simplifié qui vous permet de bénéficier d’un abattement forfaitaire de 50% sur vos revenus locatifs bruts. Vous n’avez pas besoin de justifier vos dépenses, ce qui simplifie vos démarches. C'est idéal si vos charges réelles sont inférieures à cet abattement.</p>
        <p><strong>Formule de calcul :</strong></p>
        <p>Revenu imposable = Revenus locatifs bruts × (1 - 50%)</p>
        <p><strong>Régime Réel :</strong></p>
        <p>Le régime Réel permet de déduire l’ensemble de vos charges et frais liés à l’activité locative (charges d’entretien, frais de gestion, impôts locaux, etc.). Ce régime est plus avantageux si vos charges réelles dépassent 50% de vos revenus.</p>
        <p><strong>Formule de calcul :</strong></p>
        <p>Revenu imposable = Revenus locatifs bruts - Total des charges</p>""", 
        unsafe_allow_html=True
    )

    # Chargement des données CSV
    df = pd.read_csv('revenus_charges_final.csv')

    if df.empty:
        st.error("Le fichier CSV est vide ou introuvable.")
    else:
        total_revenus = df['Revenus'].sum()
        total_charges = df['Charges'].sum()

        # Sélection du régime fiscal
        regime_fiscal = st.selectbox('Sélectionnez le régime fiscal', ['Micro-BIC', 'Régime Réel'])

        if regime_fiscal == 'Micro-BIC':
            abattement = 0.50
            revenu_imposable = total_revenus * (1 - abattement)
            st.markdown(f"<p style='color: navy;'>Total des revenus locatifs : {total_revenus:.2f} €</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: lightcoral;'>Revenu imposable après abattement de 50% : {revenu_imposable:.2f} €</p>", unsafe_allow_html=True)
        else:
            revenu_imposable = total_revenus - total_charges
            st.markdown(f"<p style='color: navy;'>Total des revenus locatifs : {total_revenus:.2f} €</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: navy;'>Total des charges : {total_charges:.2f} €</p>", unsafe_allow_html=True)
            st.markdown(f"<p>Revenu imposable (après déduction des charges) : {revenu_imposable:.2f} €</p>", unsafe_allow_html=True)

        # Section du formulaire fiscal 2042 avec réduction de la taille de la police
        st.markdown("<h3 style='font-size:20px;'>Formulaire 2042</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: darkorange;'>Case 4BE (Micro-BIC) ou 4BB (Régime réel) : {revenu_imposable:.2f} €</p>", unsafe_allow_html=True)

        # Calcul de réduction d'impôt et affichage du revenu final
        reduction_impot = 300
        revenu_imposable_final = revenu_imposable - reduction_impot
        st.markdown(f"<p style='color: lightcoral;'>Revenu imposable après réductions d'impôt : {revenu_imposable_final:.2f} €</p>", unsafe_allow_html=True)

        # Générer le fichier CSV pour le téléchargement
        df_result = pd.DataFrame({
            'Formulaire': ['2042', '2042C', '2042 RICI'],
            'Case': ['4BE / 4BB', '2DC', 'Réductions d\'impôt'],
            'Montant': [revenu_imposable, 0, reduction_impot]
        })
        
        # Convertir le DataFrame en fichier CSV pour le téléchargement
       


# --- NAVIGATION --- #
def main():
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Sélectionnez une page", ["Analyse des Revenus", "Formulaires Fiscaux"])

    if page == "Analyse des Revenus":
        page1()
    elif page == "Formulaires Fiscaux":
        page2()


if __name__ == "__main__":
    main()
