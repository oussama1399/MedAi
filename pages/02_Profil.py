# 02_Profil.py - Page de profil utilisateur

import streamlit as st
import json
import os
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Titre et style de l'application
st.set_page_config(
    page_title="👤 Profil - Assistant Santé IA",
    page_icon="🩺",
    layout="wide"
)

# Chemin de stockage local
USER_DATA_DIR = "user_data"
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")

# CSS personnalisé pour un design fluide et pro
st.markdown("""
<style>
    .profile-container {
        background: white;
        padding: 32px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.10);
        margin-bottom: 24px;
    }
    .stat-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #0dcaf0;
        margin-bottom: 15px;
        font-size: 1.1em;
    }
    .warning-box {
        background: #fff3cd;
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 20px 0;
        font-size: 1em;
    }
</style>
""", unsafe_allow_html=True)

# Fonctions pour gérer les utilisateurs
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Vérification de la session
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vous devez être connecté pour accéder à cette page.")
    st.info("👉 Retournez à la page principale pour vous connecter.")
    st.stop()

# Obtenir les données utilisateur
username = st.session_state.current_user
users = load_users()
user_data = users.get(username, {})

# Interface principale
st.title(f"👤 Profil de {username}")

# Informations utilisateur
with st.container():
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)
    
    # Informations de base
    st.subheader("📋 Informations personnelles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Nom d'utilisateur :** {username}<br>
        **Créé le :** {user_data.get('created_at', 'Date inconnue')}<br>
        **Langue préférée :** {"🇫🇷 Français" if user_data.get('language', 'fr') == 'fr' else "🇬🇧 Anglais"}<br>
        """, unsafe_allow_html=True)
    
    with col2:
        # Statistiques utilisateur
        total_questions = len(user_data.get("history", []))
        potential_diseases = len(user_data.get("potential_diseases", []))
        
        st.metric("Questions posées", total_questions)
        st.metric("Symptômes analysés", potential_diseases)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Modification du profil
with st.container():
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)
    st.subheader("✏️ Modifier votre profil")
    
    # Changement de mot de passe
    with st.expander("🔐 Changer de mot de passe"):
        current_password = st.text_input("Mot de passe actuel", type="password")
        new_password = st.text_input("Nouveau mot de passe", type="password")
        confirm_password = st.text_input("Confirmer nouveau mot de passe", type="password")
        
        if st.button("Mettre à jour le mot de passe", use_container_width=True):
            if user_data.get("password") != current_password:
                st.error("❌ Mot de passe actuel incorrect.")
            elif len(new_password) < 6:
                st.warning("⚠️ Mot de passe trop court (minimum 6 caractères).")
            elif new_password != confirm_password:
                st.error("❌ Les nouveaux mots de passe ne correspondent pas.")
            else:
                user_data["password"] = new_password
                users[username] = user_data
                save_users(users)
                st.success("✅ Mot de passe mis à jour avec succès!")
    
    # Changement de langue préférée
    with st.expander("🌐 Changer de langue préférée"):
        current_language = user_data.get('language', 'fr')
        new_language = st.selectbox(
            "Langue préférée", 
            options=["fr", "en"],
            format_func=lambda x: "Français" if x == "fr" else "English",
            index=0 if current_language == "fr" else 1
        )
        
        if st.button("Mettre à jour la langue", use_container_width=True):
            user_data["language"] = new_language
            users[username] = user_data
            save_users(users)
            st.success("✅ Préférence de langue mise à jour avec succès!")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Option de suppression de compte
with st.container():
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)
    st.subheader("❌ Suppression du compte")
    
    st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
    st.warning("⚠️ Attention ! La suppression de votre compte est définitive et entraînera la perte de toutes vos données, y compris l'historique de vos questions et analyses médicales.")
    st.markdown("</div>", unsafe_allow_html=True)
    
    delete_confirm = st.text_input("Pour confirmer, tapez votre nom d'utilisateur:")
    password_confirm = st.text_input("Et votre mot de passe:", type="password")
    
    if st.button("💣 Supprimer définitivement mon compte", use_container_width=True):
        if delete_confirm != username:
            st.error("❌ Nom d'utilisateur incorrect.")
        elif password_confirm != user_data.get("password"):
            st.error("❌ Mot de passe incorrect.")
        else:
            # Supprimer l'utilisateur
            del users[username]
            save_users(users)
            # Réinitialiser la session
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.success("✅ Compte supprimé avec succès.")
            st.info("👋 Vous avez été déconnecté.")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Section À propos en bas de page
st.markdown("---")
st.markdown("""
<div style='font-size:0.95em;color:#888;text-align:center;margin-top:30px;'>
    <b>À propos :</b> Assistant IA médical développé pour l'aide à l'information santé, ne remplace pas un avis médical professionnel.<br>
    Données issues de NHS, PubMed, OMS.| Développé par Ahmed QAIS et Oussama KADDOURI
</div>
""", unsafe_allow_html=True)
