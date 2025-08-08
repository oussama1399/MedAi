# 03_Maladies_Potentielles.py - Page des maladies potentielles

import streamlit as st
import json
import os
from datetime import datetime
import logging
from fpdf import FPDF
import base64

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Titre et style de l'application
st.set_page_config(
    page_title="🩺 Maladies Potentielles - Assistant Santé IA",
    page_icon="🩺",
    layout="wide"
)

# Chemin de stockage local
USER_DATA_DIR = "user_data"
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")

# CSS personnalisé
st.markdown("""
<style>
    .disease-item {
        background-color: #fff3cd;
        padding: 20px;
        border-left: 5px solid #ffc107;
        margin-bottom: 14px;
        border-radius: 10px;
        font-size: 1.08em;
        min-width: 260px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }
    .disease-date {
        font-size: 0.95em;
        color: #6c757d;
        margin-bottom: 5px;
    }
    .warning-box {
        background-color: #f8d7da;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin-bottom: 20px;
        font-size: 1em;
    }
    .download-button {
        background-color: #198754 !important;
        color: white !important;
        padding: 0.7rem 1.2rem;
        border-radius: 7px;
        font-size: 1.1em;
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

# Créer un PDF des maladies potentielles
def create_diseases_pdf(diseases):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', size=16)
    
    pdf.cell(200, 10, txt="Rapport de Maladies Potentielles", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Avertissement Médical", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, "Ce document ne constitue pas un diagnostic médical. Les informations présentées sont générées par un système d'intelligence artificielle et doivent être validées par un professionnel de santé.")
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Symptômes et Conditions Potentielles", ln=True)
    pdf.ln(5)
    
    for i, disease in enumerate(diseases):
        # Date
        pdf.set_font("Arial", 'I', size=10)
        date = disease.get("date", "Date inconnue")
        pdf.cell(200, 7, txt=f"Date: {date}", ln=True)
        
        # Question/symptôme
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"Symptôme rapporté:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, disease.get("symptom_question", ""))
        pdf.ln(5)
        
        # Réponse/analyse
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"Analyse:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 7, disease.get("suggested_answer", ""))
        pdf.ln(10)
    
    filename = f"maladie_potentielle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# Fonction d'export en PDF
def export_to_pdf(diseases):
    filename = create_diseases_pdf(diseases)
    with open(filename, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button">📥 Télécharger le rapport PDF</a>'
    return href

# Vérification de la session
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vous devez être connecté pour accéder à cette page.")
    st.info("👉 Retournez à la page principale pour vous connecter.")
    st.stop()

# Obtenir les données utilisateur
username = st.session_state.current_user
users = load_users()
user_data = users.get(username, {})
diseases = user_data.get("potential_diseases", [])

# Interface principale
st.title("🩺 Maladies Potentielles")

# Avertissement médical
st.markdown("""
<div class='warning-box'>
⚠️ <strong>Avertissement Médical Important:</strong><br>
Cette section présente des analyses automatisées basées sur vos questions et symptômes rapportés. 
Ces informations ne constituent en aucun cas un diagnostic médical et ne remplacent pas une 
consultation avec un professionnel de santé qualifié. Veuillez consulter un médecin pour toute 
préoccupation de santé.
</div>
""", unsafe_allow_html=True)

# Affichage des statistiques
total_diseases = len(diseases)
st.subheader(f"📊 {total_diseases} symptôme{'s' if total_diseases > 1 else ''} analysé{'s' if total_diseases > 1 else ''}")

# Tri des maladies
sort_options = ["Plus récentes d'abord", "Plus anciennes d'abord"]
sort_choice = st.radio("Tri des symptômes:", sort_options, horizontal=True)

# Trier les maladies
if sort_choice == "Plus anciennes d'abord":
    diseases = sorted(diseases, key=lambda x: x.get("date", ""))
else:
    diseases = sorted(diseases, key=lambda x: x.get("date", ""), reverse=True)

# Affichage des maladies potentielles
if not diseases:
    st.info("👍 Aucun symptôme ou maladie potentielle n'a été détecté dans vos questions.")
else:
    # Bouton pour exporter toutes les maladies en PDF
    st.markdown(export_to_pdf(diseases), unsafe_allow_html=True)
    
    # Affichage de chaque maladie
    for i, disease in enumerate(diseases):
        with st.container():
            # Formatage des dates
            try:
                date = datetime.fromisoformat(disease.get("date", "")).strftime("%d/%m/%Y à %H:%M")
            except:
                date = disease.get("date", "Date inconnue")
            
            st.markdown(f"<div class='disease-date'>📅 {date}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='disease-item'>
                <strong>❓ Symptôme rapporté:</strong> {disease['symptom_question']}<br><br>
                <strong>🔬 Analyse:</strong> {disease['suggested_answer']}
            </div>
            """, unsafe_allow_html=True)
            
            # Option pour supprimer une entrée individuelle
            if st.button(f"🗑️ Supprimer cette entrée", key=f"delete_{i}"):
                diseases.pop(i)
                user_data["potential_diseases"] = diseases
                users[username] = user_data
                save_users(users)
                st.success("✅ Entrée supprimée avec succès!")
                st.rerun()
    
    # Option pour effacer toutes les maladies
    if st.button("🗑️ Effacer toutes les maladies potentielles", type="primary", use_container_width=True):
        user_data["potential_diseases"] = []
        users[username] = user_data
        save_users(users)
        st.success("✅ Liste des maladies potentielles effacée avec succès!")
        st.rerun()

# Section À propos en bas de page
st.markdown("---")
st.markdown("""
<div style='font-size:0.95em;color:#888;text-align:center;margin-top:30px;'>
    <b>À propos :</b> Assistant IA médical développé pour l'aide à l'information santé, ne remplace pas un avis médical professionnel.<br>
    Données issues de NHS, PubMed, OMS.| Développé par Ahmed QAIS et Oussama KADDOURI
</div>
""", unsafe_allow_html=True)
