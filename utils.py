# utils.py - Fonctions utilitaires partagées pour l'application 

import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
import base64

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

# Charger ou créer un profil utilisateur
def get_user_profile(username):
    users = load_users()
    if username in users:
        return users[username]
    else:
        users[username] = {
            "password": "",
            "created_at": str(datetime.now()),
            "history": [],
            "potential_diseases": [],
            "language": "fr"
        }
        save_users(users)
        return users[username]

# Mettre à jour l'historique utilisateur
def update_user_history(username, question, answer, sources):
    users = load_users()
    user = users.get(username, {"history": [], "potential_diseases": []})

    user["history"].append({
        "question": question,
        "answer": answer,
        "sources": sources,
        "timestamp": str(datetime.now())
    })

    keywords = ["maladie", "symptôme", "tête", "ventre", "diabète", "hypertension", "fièvre", "douleur"]
    
    if any(k in question.lower() for k in keywords):
        if "potential_diseases" not in user:
            user["potential_diseases"] = []

        user["potential_diseases"].append({
            "symptom_question": question,
            "suggested_answer": answer,
            "date": str(datetime.now())
        })
    
    users[username] = user
    save_users(users)

# Créer un PDF de la réponse médicale
def create_medical_pdf(question, answer, sources):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Filtrage/remplacement latin-1
    safe_question = question.encode("latin-1", "replace").decode("latin-1")
    safe_answer = answer.encode("latin-1", "replace").decode("latin-1")
    safe_sources = [s.encode("latin-1", "replace").decode("latin-1") for s in sources]

    pdf.cell(200, 10, txt="Reponse Medicale", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt=f"Question : {safe_question}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Réponse : {safe_answer}")
    pdf.ln(5)

    pdf.set_font("Arial", 'I', size=10)
    pdf.cell(200, 10, txt="Sources consultees :", ln=True)
    for safe_source in safe_sources:
        pdf.cell(200, 10, txt=f"- {safe_source}", ln=True)

    filename = f"rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# Fonction d'export en PDF
def export_to_pdf(question, answer, sources):
    filename = create_medical_pdf(question, answer, sources)
    with open(filename, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Télécharger le PDF</a>'
    return href

def create_full_history_pdf(history, username):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', size=16)
    # Filtrer le nom d'utilisateur pour le PDF
    safe_username = username.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 10, txt=f"Historique des questions - {safe_username}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for idx, item in enumerate(history):
        pdf.set_font("Arial", 'B', size=12)
        # Nettoyage/remplacement des caractères non-latin1 pour question/réponse/sources
        safe_question = item['question'].encode("latin-1", "replace").decode("latin-1")
        safe_answer = item['answer'].encode("latin-1", "replace").decode("latin-1")
        safe_sources = [s.encode("latin-1", "replace").decode("latin-1") for s in item['sources']]
        pdf.cell(0, 10, txt=f"Question {idx+1} : {safe_question}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=f"Réponse : {safe_answer}")
        pdf.set_font("Arial", 'I', size=10)
        pdf.cell(0, 10, txt=f"Date : {item['timestamp']}", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, txt=f"Sources : {', '.join(safe_sources)}", ln=True)
        pdf.ln(5)
    filename = f"historique_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def export_full_history_pdf(history, username):
    filename = create_full_history_pdf(history, username)
    with open(filename, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Télécharger tout l\'historique en PDF</a>'
    return href

# Fonction pour exporter le PDF d'une maladie potentielle
def export_potential_disease_pdf(question, answer):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    # Filtrage/remplacement latin-1
    safe_question = question.encode("latin-1", "replace").decode("latin-1")
    safe_answer = answer.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(200, 10, txt="Rapport Maladie Potentielle", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt=f"Question : {safe_question}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Réponse : {safe_answer}")
    filename = f"maladie_potentielle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def export_disease_pdf(question, answer):
    filename = export_potential_disease_pdf(question, answer)
    with open(filename, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📥 Télécharger le rapport en PDF</a>'
    return href

# Export all diseases to PDF
def create_all_diseases_pdf(diseases):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", 'B', size=16)
    
    pdf.cell(200, 10, txt="Rapport Complet de Symptômes et Maladies Potentielles", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(200, 10, txt="Avertissement Médical", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, "Ce document ne constitue pas un diagnostic médical. Les informations présentées sont générées par un système d'intelligence artificielle et doivent être validées par un professionnel de santé.")
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Symptômes et Conditions Potentielles ({len(diseases)} entrées)", ln=True)
    pdf.ln(5)
    
    for i, disease in enumerate(diseases):
        # Date
        pdf.set_font("Arial", 'I', size=10)
        date = disease.get("date", "Date inconnue")
        date_safe = date.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(200, 7, txt=f"Date: {date_safe}", ln=True)
        
        # Question/symptôme
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"Symptôme rapporté:", ln=True)
        pdf.set_font("Arial", size=11)
        question_safe = disease.get("symptom_question", "").encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, question_safe)
        pdf.ln(5)
        
        # Réponse/analyse
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt=f"Analyse:", ln=True)
        pdf.set_font("Arial", size=11)
        answer_safe = disease.get("suggested_answer", "").encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, answer_safe)
        pdf.ln(10)
    
    filename = f"rapport_maladies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def export_all_diseases_pdf(diseases):
    filename = create_all_diseases_pdf(diseases)
    with open(filename, "rb") as f:
        pdf_data = f.read()
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-button">📥 Télécharger le rapport complet en PDF</a>'
    return href

# Fonctions de l'interface utilisateur
def show_user_sidebar(username):
    """Affiche la barre latérale avec les informations utilisateur"""
    profile = get_user_profile(username)
    
    st.sidebar.header("📊 À propos du Modèle")
    # Statistiques sur les données médicales
    try:
        # Nombre de maladies (fichiers dans nhs_condition_details)
        nb_maladies = len(os.listdir("data/raw/nhs_condition_details"))
    except Exception:
        nb_maladies = "?"
    try:
        # Nombre de documents médicaux
        nb_docs = sum(1 for _ in open("data/raw/medical_data.jsonl", encoding="utf-8"))
    except Exception:
        nb_docs = "?"
    try:
        # Nombre d'utilisateurs
        users = load_users()
        nb_users = len(users)
    except Exception:
        nb_users = "?"
        
    st.sidebar.markdown(f"""
    <div style='background:#e9f7fe;padding:12px 18px;border-radius:10px;margin-bottom:10px;'>
    <b>📚 Maladies référencées :</b> {nb_maladies}<br>
    <b>📄 Documents médicaux :</b> {nb_docs}<br>
    <b>👥 Utilisateurs :</b> {nb_users}<br>
    <b>🧠 Modèle d'embedding :</b> all-MiniLM-L6-v2<br>
    <b>🤖 LLM utilisé :</b> Google Gemini Flash<br>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗂️ Données utilisateur")
    st.sidebar.write(f"👤 Connecté en tant que : **{username}**")
    st.sidebar.write(f"📅 Créé le : {profile['created_at']}")
    st.sidebar.write(f"🌐 Langue : {'Français' if profile.get('language', 'fr') == 'fr' else 'Anglais'}")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Vos Statistiques")
    with st.sidebar.container():
        st.markdown("<div class='stats-box'>", unsafe_allow_html=True)
        total_questions = len(profile["history"])
        potential_diseases = len(profile.get("potential_diseases", []))
        st.metric("Questions posées", total_questions)
        st.metric("Symptômes analysés", potential_diseases)
        if total_questions > 0:
            last_consultation = profile["history"][-1]["timestamp"]
            st.markdown(f"Dernière consultation: {last_consultation}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🔓 Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.success("👋 Vous avez été déconnecté.")
        st.switch_page("app.py")
