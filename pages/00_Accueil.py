# 00_Accueil.py - Page d'accueil du chat

import streamlit as st
from rag_pipeline import MedicalRAGAssistant
import os
from datetime import datetime
import sys
import base64
from fpdf import FPDF

# Ajouter le répertoire parent au path pour importer utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import get_user_profile, update_user_history, export_to_pdf, show_user_sidebar

# Configuration de page
st.set_page_config(
    page_title="Chat - Assistant Santé IA",
    page_icon="🩺",
    layout="wide"
)

# Vérifier la connexion
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Veuillez vous connecter sur la page principale pour accéder au chat.")
    # Ajouter un bouton pour faciliter la navigation vers la page de connexion
    if st.button("🔐 Aller à la page de connexion"):
        # Navigation vers la page principale
        st.switch_page("app.py") 
    st.stop()

# Charger l'assistant
@st.cache_resource
def load_assistant():
    return MedicalRAGAssistant()
assistant = load_assistant()

# Récupérer profil utilisateur
user = st.session_state.current_user
profile = get_user_profile(user)

# Afficher la barre latérale utilisateur
show_user_sidebar(user)

# Interface chat
now = datetime.now().strftime('%d/%m/%Y %H:%M')
st.markdown(f"### 👤 Bienvenue, **{user}** | Connecté le {now}")
st.title("🤖 Posez votre question médicale")
question = st.text_input("Votre question :", key="chat_input")

# Initialisation des variables de session pour stocker les résultats
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None
    st.session_state.last_sources = None
    st.session_state.last_question = None

if st.button("Envoyer", key="send_chat"):
    if question.strip():
        with st.spinner("Recherche... 🧠"):
            context, metadata = assistant.retrieve_context(question)
        with st.spinner("Génération de la réponse... ✨"):
            answer = assistant.generate_answer_with_gemini(question, context)
        
        sources = [m.get('source','inconnue') for m in metadata]
        
        # Stocker dans la session state
        st.session_state.last_answer = answer
        st.session_state.last_sources = sources
        st.session_state.last_question = question
        
        # Mise à jour de l'historique utilisateur
        update_user_history(user, question, answer, sources)
        
        # Actualiser le profil pour l'affichage à jour
        profile = get_user_profile(user)
        
        # Affichage
        st.markdown("#### 🧠 Réponse Médicale")
        st.markdown(f"<div class='response-box'>{answer}</div>", unsafe_allow_html=True)
        
        st.markdown("#### 📄 Sources consultées")
        for i, source in enumerate(sources):
            st.markdown(f"{i+1}. {source}")
          # Export PDF
        if st.button("📥 Télécharger en PDF"):
            href = export_to_pdf(question, answer, sources)
            st.markdown(href, unsafe_allow_html=True)
            
# Boutons de navigation vers les autres pages
st.markdown("---")
st.subheader("📍 Navigation")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🕰️ Historique", use_container_width=True):
        st.switch_page("pages/01_Historique.py")
with col2:
    if st.button("👤 Profil", use_container_width=True):
        st.switch_page("pages/02_Profil.py")
with col3:
    if st.button("🩺 Maladies Potentielles", use_container_width=True):
        st.switch_page("pages/03_Maladies_Potentielles.py")
