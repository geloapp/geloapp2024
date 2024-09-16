import pandas as pd


def merge_airbnb_booking_charges(airbnb_data, booking_data, charges_data):
    # Concaténer les données Airbnb et Booking
    combined_data = pd.concat([airbnb_data, booking_data], ignore_index=True)

    # Merge avec les données des charges
    all_data = pd.merge(combined_data, charges_data, on=['Titre_annonce', 'mois_annee'], how='inner')

    # Calcul du solde mensuel
    all_data['Solde_mensuel'] = all_data['Revenus'] - all_data['Charges']

    return all_data
