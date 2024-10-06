import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

from streamlit.delta_generator import DeltaGenerator
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import plotly.express as px  # Ajout de plotly pour le graphique

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


# --- FONCTIONS --- #
# Vous pouvez garder ici toutes vos fonctions comme `process_airbnb_data()`, `process_booking_data()`, etc.
# (les fonctions restent inchangées par rapport à votre code original)


# --- PAGE 1 : ANALYSE DES REVENUS, CHARGES ET SOLDES --- #
def page1():
    # Ajouter le logo de Fifiloc
    # Importer les données Airbnb
    logo1 = 'final_logo_fifiloc_#1.png'

    st.image(logo1, width=100)  # Ajustez le chemin et la taille selon vos besoins

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
def page2():
    # Ajouter le logo de Fifiloc
    # Importer les données Airbnb
    logo1 = 'final_logo_fifiloc_#1.png'

    st.image(logo1, width=100)  # Ajustez le chemin et la taille selon vos besoins
    st.markdown("<h1 style='font-size:24px;'>Revenus imposables (micro-bic ou réel)</h1>", unsafe_allow_html=True)
    
    # Description de la page
    st.markdown(
        """<p>
        Découvrez facilement quel régime fiscal vous convient le mieux et estimez votre revenu imposable pour vos locations saisonnières. 
        Que vous optiez pour le régime <strong>Micro-BIC</strong> ou le <strong>Régime Réel</strong>, notre outil calcule automatiquement votre revenu imposable en tenant compte des spécificités de chaque régime.
        </p>""", 
        unsafe_allow_html=True
    )

    # Chargement des données CSV
    df = pd.read_csv('revenus_charges_final.csv')

    if df.empty:
        st.error("Le fichier CSV est vide ou introuvable.")
        return

    total_revenus = df['Revenus'].sum()
    total_charges = df['Charges'].sum()

    # Sélection du régime fiscal
    regime_fiscal = st.selectbox('Sélectionnez le régime fiscal', ['Micro-BIC', 'Régime Réel'])

    if regime_fiscal == 'Micro-BIC':
        abattement = 0.50
        revenu_imposable = total_revenus * (1 - abattement)
    else:
        revenu_imposable = total_revenus - total_charges

    # Affichage des résultats sous forme de KPI
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("<h3 style='font-size:18px;'>Total des Revenus</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: navy;'>{total_revenus:.2f} €</h2>", unsafe_allow_html=True)

    with col2:
        st.markdown("<h3 style='font-size:18px;'>Total des Charges</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: red;'>{total_charges:.2f} €</h2>", unsafe_allow_html=True)

    with col3:
        st.markdown("<h3 style='font-size:18px;'>Revenu Imposable</h3>", unsafe_allow_html=True)
        if revenu_imposable < 0:
            st.markdown(f"<h2 style='color: orange;'>Négatif : {revenu_imposable:.2f} €</h2>", unsafe_allow_html=True)
            st.warning("Votre revenu imposable est négatif. Vous n'aurez pas d'impôt à payer.")
        else:
            st.markdown(f"<h2 style='color: green;'>{revenu_imposable:.2f} €</h2>", unsafe_allow_html=True)
            st.success("Votre revenu imposable est positif. Vous aurez des impôts à payer.")

    # Section du formulaire fiscal 2042
    st.markdown("<h3 style='font-size:18px;'>Formulaire 2042</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: darkorange;'>Case 4BE (Micro-BIC) ou 4BB (Régime réel) : {revenu_imposable:.2f} €</p>", unsafe_allow_html=True)

    # Calcul de réduction d'impôt et affichage du revenu final
    reduction_impot = 300
    revenu_imposable_final = revenu_imposable - reduction_impot
    st.markdown(f"<p style='color: lightcoral;'>Revenu imposable après réductions d'impôt : {revenu_imposable_final:.2f} €</p>", unsafe_allow_html=True)

    
# --- PAGE 3 : FORMULAIRE FISCAL PAR TYPE D'ANNONCE --- #
def page3():
    # Ajouter le logo de Fifiloc
    # Importer les données Airbnb
    logo1 = 'final_logo_fifiloc_#1.png'

    st.image(logo1, width=100)  # Ajustez le chemin et la taille selon vos besoins
    st.markdown("<h1 style='font-size:24px;'>Revenus imposables par location</h1>", unsafe_allow_html=True)

    st.markdown(
        "Cette page vous permet d'estimer votre revenu imposable en fonction du type d'annonce que vous gérez. Chaque bien locatif peut être soumis à un régime fiscal différent, ce qui influence le calcul de votre revenu imposable. Que vous louiez un appartement, une maison ou une chambre, vous pouvez sélectionner le type d'annonce correspondant pour obtenir des résultats précis et adaptés à votre situation.<br><br>"
        "En choisissant le type d'annonce, vous pourrez visualiser vos revenus et charges spécifiques, ainsi que le régime fiscal applicable, que ce soit le régime Micro-BIC ou le régime Réel. Cette fonctionnalité vous aide à mieux comprendre les implications fiscales de chaque bien et à optimiser votre gestion locative pour maximiser vos bénéfices.",
        unsafe_allow_html=True
    )

    # Chargement des données CSV
    df = pd.read_csv('revenus_charges_final.csv')

    if df.empty:
        st.error("Le fichier CSV est vide ou introuvable.")
    else:
        # Sélection du type d'annonce
        types_annonce = df['Titre_annonce'].unique()
        type_annonce_selectionne = st.selectbox('Sélectionnez le type d\'annonce', types_annonce)

        # Filtrage des données pour l'annonce sélectionnée
        df_annonce = df[df['Titre_annonce'] == type_annonce_selectionne]

        total_revenus = df_annonce['Revenus'].sum()
        total_charges = df_annonce['Charges'].sum()

        # Sélection du régime fiscal
        regime_fiscal = st.selectbox('Sélectionnez le régime fiscal', ['Micro-BIC', 'Régime Réel'])

        if regime_fiscal == 'Micro-BIC':
            abattement = 0.50
            revenu_imposable = total_revenus * (1 - abattement)
        else:
            revenu_imposable = total_revenus - total_charges

        # Affichage des KPI
        st.markdown("<h3 style='font-size:22px;'>Résultats Financiers</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        kpi_style = "<h3 style='font-size:18px;'>Total des Revenus</h3>"
        kpi_value_style_revenus = f"<h2 style='color: navy;'>{total_revenus:.2f} €</h2>"
        kpi_value_style_charges = f"<h2 style='color: red;'>{total_charges:.2f} €</h2>"
        kpi_value_style_revenu_imposable = f"<h2 style='color: green;'>{revenu_imposable:.2f} €</h2>"

        with col1:
            st.markdown(kpi_style, unsafe_allow_html=True)
            st.markdown(kpi_value_style_revenus, unsafe_allow_html=True)

        with col2:
            st.markdown("<h3 style='font-size:18px;'>Total des Charges</h3>", unsafe_allow_html=True)
            st.markdown(kpi_value_style_charges, unsafe_allow_html=True)

        with col3:
            st.markdown("<h3 style='font-size:18px;'>Revenu Imposable</h3>", unsafe_allow_html=True)
            st.markdown(kpi_value_style_revenu_imposable, unsafe_allow_html=True)

        # Afficher le revenu final après réduction d'impôt
        st.markdown("<h3 style='font-size:22px;'>Revenu Imposable Final</h3>", unsafe_allow_html=True)
        reduction_impot = 300
        revenu_imposable_final = revenu_imposable - reduction_impot
        st.markdown(f"<p style='color: lightcoral;'>Revenu imposable après réductions d'impôt : <strong>{revenu_imposable_final:.2f} €</strong></p>", unsafe_allow_html=True)

        # Section du formulaire fiscal 2042
        st.markdown("<h3 style='font-size:18px;'>Formulaire 2042</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: darkorange;'>Case 4BE (Micro-BIC) ou 4BB (Régime réel) : {revenu_imposable:.2f} €</p>", unsafe_allow_html=True)

        # Résumé des implications fiscales
        st.markdown("<h3 style='font-size:16px;'>Résumé des Implications Fiscales</h3>", unsafe_allow_html=True)
        if regime_fiscal == 'Micro-BIC':
            st.markdown("Avec le régime **Micro-BIC**, vous bénéficiez d'un abattement de 50% sur vos revenus, ce qui simplifie vos démarches fiscales.")
        else:
            st.markdown("Avec le régime **Régime Réel**, vous devez prendre en compte vos charges réelles, ce qui peut entraîner une fiscalité plus favorable selon vos dépenses.")

        # Générer le fichier CSV pour le téléchargement
        df_result = pd.DataFrame({
            'Formulaire': ['2042', '2042C', '2042 RICI'],
            'Case': ['4BE / 4BB', '2DC', 'Réductions d\'impôt'],
            'Montant': [revenu_imposable, 0, reduction_impot]
        })

        # Convertir le DataFrame en fichier CSV pour le téléchargement
        csv = df_result.to_csv(index=False).encode('utf-8')

        # Ajout du bouton de téléchargement
        st.download_button(
            label="Télécharger le rapport",
            data=csv,
            file_name='resultats_fiscaux.csv',
            mime='text/csv',
        )

# --- PAGE 4 : NICE TO KNOW --- #
def page4():
    # Ajouter le logo de Fifiloc
    # Importer les données Airbnb
    logo1 = 'final_logo_fifiloc_#1.png'

    st.image(logo1, width=100)  # Ajustez le chemin et la taille selon vos besoins
    st.markdown("<h1 style='font-size:24px;'>Petit moment de lecture</h1>", unsafe_allow_html=True)
    
    st.markdown(
        """<p>
        Cette page fournit des informations sur les régimes fiscaux français applicables aux locations saisonnières et non saisonnières, ainsi que les étapes à suivre pour la déclaration d'impôts.
        </p>""",
        unsafe_allow_html=True
    )
    
    st.markdown("<h2 style='font-size:20px;'>1. Régimes Fiscaux</h2>", unsafe_allow_html=True)
    st.markdown(
        """<p>
        En France, les revenus générés par la location de biens immobiliers sont généralement soumis à l'impôt sur le revenu. Il existe plusieurs régimes fiscaux qui peuvent s'appliquer selon la nature et le montant des revenus :
        </p>
        <ul>
            <li><strong>Régime Micro-BIC :</strong> Applicable pour les revenus locatifs annuels inférieurs à 72 600 €. Un abattement de 50% est appliqué automatiquement.</li>
            <li><strong>Régime Réel :</strong> Permet de déduire les charges réelles (travaux, frais d'agence, intérêts d'emprunt, etc.) du revenu locatif. Il est recommandé pour ceux qui ont des dépenses élevées.</li>
        </ul>""",
        unsafe_allow_html=True
    )
    
    st.markdown("<h2 style='font-size:20px;'>2. Déclaration d'Impôts</h2>", unsafe_allow_html=True)
    st.markdown(
        """<p>
        Pour déclarer vos revenus locatifs, voici les étapes à suivre :
        </p>
        <ol>
            <li>Rassemblez toutes les informations concernant vos revenus et charges liés à la location.</li>
            <li>Choisissez le régime fiscal adapté à votre situation.</li>
            <li>Remplissez le formulaire 2042 pour déclarer vos revenus locatifs. Selon le régime choisi, vous devrez peut-être remplir également le formulaire 2042-C.</li>
            <li>Soumettez votre déclaration en ligne ou par courrier avant la date limite de dépôt.</li>
        </ol>""",
        unsafe_allow_html=True
    )
    
    st.markdown("<h2 style='font-size:20px;'>3. Formulaires Utiles</h2>", unsafe_allow_html=True)
    st.markdown(
        """<p>Voici les principaux formulaires que vous pourriez avoir besoin de remplir :</p>
        <ul>
            <li><strong>Formulaire 2042 :</strong> Déclaration des revenus. Utilisé pour déclarer vos revenus globaux.</li>
            <li><strong>Formulaire 2042-C :</strong> Annexes au formulaire 2042. À remplir si vous avez des revenus de location (Micro-BIC ou réel).</li>
            <li><strong>Formulaire 2044 :</strong> Déclaration des revenus fonciers. Utilisé pour le régime réel, où vous détaillez vos charges.</li>
            <li><strong>Formulaire 2042-RICI :</strong> Réduction d’impôt pour les investissements locatifs. À utiliser si vous bénéficiez de réductions fiscales.</li>
        </ul>""",
        unsafe_allow_html=True
    )
    
    st.markdown("<h2 style='font-size:20px;'>4. Ressources Utiles</h2>", unsafe_allow_html=True)
    st.markdown(
        """<p>
        Pour plus d'informations, vous pouvez consulter :
        </p>
        <ul>
            <li><a href='https://www.impots.gouv.fr/' target='_blank'>Site officiel des impôts en France</a></li>
            <li><a href='https://www.service-public.fr/' target='_blank'>Service Public - Informations fiscales</a></li>
            <li><a href='https://www.economie.gouv.fr/' target='_blank'>Ministère de l'Économie - Informations sur la fiscalité</a></li>
        </ul>""",
        unsafe_allow_html=True
    )


# --- NAVIGATION --- #
def main():
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Sélectionnez une page", ["Analyse des Revenus", "Formulaires Fiscaux", "Formulaire Fiscal par Location", "Bon à savoir"])

    if page == "Analyse des Revenus":
        page1()
    elif page == "Formulaires Fiscaux":
        page2()
    elif page == "Formulaire Fiscal par Location":
        page3()
    elif page == "Bon à savoir":
        page4()
if __name__ == "__main__":
    main()
