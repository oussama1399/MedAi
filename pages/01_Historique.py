# 01_Historique.py - Page d'historique des chats

import streamlit as st
from rag_pipeline import MedicalRAGAssistant
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
    page_title="🕰️ Historique - Assistant Santé IA",
    page_icon="🩺",
    layout="wide"
)

# Chemin de stockage local
USER_DATA_DIR = "user_data"
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")

# Charger les utilisateurs
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Vérification de la session
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vous devez être connecté pour accéder à cette page.")
    st.info("👉 Retournez à la page principale pour vous connecter.")
    st.stop()

# Obtenir les données utilisateur
username = st.session_state.current_user
users = load_users()
user_data = users.get(username, {"history": []})
history = user_data.get("history", [])

# CSS personnalisé
st.markdown("""
<style>
    .history-item {
        background: #f8f9fa;
        padding: 20px 28px;
        margin-bottom: 18px;
        border-radius: 12px;
        border-left: 6px solid #0d6efd;
        font-size: 1.08em;
        min-height: 80px;
        max-width: 100%;
        word-break: break-word;
    }
    .history-date {
        font-size: 0.95em;
        color: #6c757d;
        margin-bottom: 5px;
    }
    .action-btn {
        background-color: #0d6efd !important;
        color: white !important;
        border-radius: 7px;
        margin-right: 8px;
        font-size: 1.05em;
        padding: 0.4em 1.1em;
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

# Fonction pour créer un PDF
def create_medical_pdf(question, answer, sources):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Réponse Médicale - Assistant Santé IA", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=12)
    pdf.multi_cell(0, 10, f"Question : {question}")
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Réponse : {answer}")
    pdf.ln(5)

    pdf.set_font("Arial", 'I', size=10)
    pdf.cell(200, 10, txt="Sources consultées :", ln=True)
    pdf.ln(5)
    for source in sources:
        pdf.multi_cell(0, 10, f"- {source}")

    filename = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# Fonction d'export en PDF
def export_to_pdf(question, answer, sources):
    filename = create_medical_pdf(question, answer, sources)
    with open(filename, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button">📥 Télécharger le PDF</a>'
    return href

# Interface principale
st.title("🕰️ Historique de vos Consultations")

# Affichage des statistiques
total_questions = len(history)
st.subheader(f"📊 Vous avez posé {total_questions} question{'s' if total_questions > 1 else ''}")

# Filtrage par mot-clé
keyword = st.text_input("🔍 Rechercher dans vos questions", "")

# Tri des questions
sort_options = ["Plus récentes d'abord", "Plus anciennes d'abord"]
sort_choice = st.radio("Tri des questions:", sort_options, horizontal=True)

# Filtrer et trier l'historique
filtered_history = history
if keyword:
    filtered_history = [h for h in history if keyword.lower() in h["question"].lower() or keyword.lower() in h["answer"].lower()]

# Tri selon l'option sélectionnée
if sort_choice == "Plus anciennes d'abord":
    filtered_history = sorted(filtered_history, key=lambda x: x.get("timestamp", ""))
else:
    filtered_history = sorted(filtered_history, key=lambda x: x.get("timestamp", ""), reverse=True)

# Affichage des résultats de recherche
if keyword and filtered_history:
    st.success(f"✅ {len(filtered_history)} résultat(s) trouvé(s) pour '{keyword}'")
elif keyword:
    st.warning(f"⚠️ Aucun résultat trouvé pour '{keyword}'")

# Affichage de l'historique
if not filtered_history:
    st.info("👉 Aucune question posée encore. Retournez à l'accueil pour commencer.")
else:
    for i, item in enumerate(filtered_history):
        with st.container():
            # Formatage des dates
            try:
                timestamp = datetime.fromisoformat(item.get("timestamp", "")).strftime("%d/%m/%Y à %H:%M")
            except:
                timestamp = item.get("timestamp", "Date inconnue")
            
            # Affichage de la question et réponse
            st.markdown(f"<div class='history-date'>📅 {timestamp}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='history-item'>
                <strong>❓ Question:</strong> {item['question']}<br><br>
                <strong>🧠 Réponse:</strong> {item['answer']}
            </div>
            """, unsafe_allow_html=True)
            
            # Sources
            with st.expander("📚 Sources consultées"):
                for i, source in enumerate(item.get("sources", [])):
                    st.markdown(f"{i+1}. {source}")
            
            # Bouton d'export PDF
            st.markdown(export_to_pdf(item['question'], item['answer'], item.get("sources", [])),
                      unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

# Option pour effacer l'historique
if total_questions > 0:
    if st.button("🗑️ Effacer tout l'historique", type="primary", use_container_width=True):
        user_data["history"] = []
        users[username] = user_data
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=2)
        st.success("✅ Historique effacé avec succès!")
        st.rerun()
