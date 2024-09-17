import streamlit as st

# Titre de l'application
st.title("Bienvenue sur mon application Streamlit")

# Création d'un formulaire simple
name = st.text_input("Entrez votre nom :")

# Bouton pour soumettre
if st.button("Soumettre"):
    st.write(f"Bonjour, {name} ! Bienvenue sur l'application.")
