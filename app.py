# app.py - Point d'entrée principal pour l'application d'assistant médical

import streamlit as st
import json
import os
from datetime import datetime

# Titre et style de l'application - DOIT ÊTRE la première commande Streamlit
st.set_page_config(
    page_title="🩺 Assistant Santé IA",
    page_icon="🩺",
    layout="wide"
)

# Chemins de stockage local
USER_DATA_DIR = "user_data"
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Charger les utilisateurs
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    
    # Essayer différents encodages
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(USERS_FILE, "r", encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            break
    
    # Si rien ne fonctionne, créer un nouveau fichier vide
    return {}

# Sauvegarder les utilisateurs
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# Initialisation session state pour l'authentification
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "language" not in st.session_state:
    st.session_state.language = "fr"

# Page login
def login_page():
    st.title("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Se connecter", use_container_width=True):
            users = load_users()
            if username in users and users[username].get("password") == password:
                st.session_state.logged_in = True
                st.session_state.current_user = username
                st.session_state.language = users[username].get("language", "fr")
                st.success(f"👋 Bienvenue {username} ! Redirection vers l'accueil...")
                # Redirection automatique vers la page d'accueil
                st.switch_page("pages/00_Accueil.py")
            else:
                st.error("❌ Nom d'utilisateur ou mot de passe incorrect.")

    with col2:
        if st.button("S'enregistrer", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

# Page inscription
def register_page():
    st.title("📝 Inscription")
    new_username = st.text_input("Nouveau nom d'utilisateur")
    new_password = st.text_input("Nouveau mot de passe", type="password")

    language = st.selectbox("Langue préférée", ["fr", "en"])

    if st.button("Créer compte", use_container_width=True):
        users = load_users()
        if new_username in users:
            st.warning("⚠️ Ce nom d'utilisateur existe déjà.")
        elif len(new_password) < 6:
            st.warning("⚠️ Mot de passe trop court (minimum 6 caractères).")
        else:
            users[new_username] = {
                "password": new_password,
                "created_at": str(datetime.now()),
                "history": [],
                "potential_diseases": [],
                "language": language
            }
            save_users(users)
            st.success("✅ Compte créé ! Redirection vers l'accueil...")
            st.session_state.logged_in = True
            st.session_state.current_user = new_username
            st.session_state.language = language
            # Redirection automatique vers la page d'accueil
            st.switch_page("pages/00_Accueil.py")

# Interface principale
def main():
    # Masquer le menu de navigation si l'utilisateur n'est pas connecté
    if not st.session_state.logged_in:
        # Cacher la sidebar avec CSS
        st.markdown("""
        <style>
        .css-1d391kg {display: none}
        .css-1rs6os {display: none}
        .css-17eq0hr {display: none}
        section[data-testid="stSidebar"] {display: none;}
        .css-164nlkn {display: none;}        </style>
        """, unsafe_allow_html=True)
    
    if st.session_state.logged_in:
        # Si déjà connecté, rediriger automatiquement vers la page d'accueil
        st.success("✅ Vous êtes connecté! Redirection vers la page d'accueil...")
        st.button("🏠 Aller à la page d'accueil", on_click=lambda: st.switch_page("pages/00_Accueil.py"))
    else:
        st.title("🩺 Assistant Santé IA - Connectez-vous pour commencer")

        menu = ["Connexion", "Inscription"]
        choice = st.selectbox("Menu", menu)

        if choice == "Inscription":
            register_page()
        else:
            login_page()
    
    # Section d'informations déplacée en bas
    st.markdown("---")
    with st.expander("ℹ️ À propos de cette application", expanded=False):
        st.markdown("""
        ### 🏥 Assistant Santé IA
        
        Cette application utilise l'intelligence artificielle pour fournir des informations médicales fiables.
        
        #### Pages disponibles après connexion:
        - **Accueil**: Posez vos questions médicales à l'assistant IA
        - **Historique**: Consultez vos questions et réponses précédentes 
        - **Profil**: Gérez vos informations personnelles
        - **Maladies Potentielles**: Suivez les symptômes et maladies potentielles détectées
        
        *L'application utilise des sources médicales fiables (NHS, PubMed) pour générer ses réponses.*
        """)

# Section à propos en bas de page
st.markdown("---")
st.markdown("""
<div style='font-size:0.95em;color:#888;text-align:center;margin-top:30px;'>
    <b>À propos :</b> Assistant IA médical développé pour l'aide à l'information santé, ne remplace pas un avis médical professionnel.<br>
    Données issues de NHS, PubMed, OMS.| Développé par Ahmed QAIS et Oussama KADDOURI
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
