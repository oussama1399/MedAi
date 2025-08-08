# rag_pipeline.py

import os
import json
import requests
from sentence_transformers import SentenceTransformer
import chromadb
import logging
from chromadb.config import Settings

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chemins
DATA_FILE = "data/raw/medical_data.jsonl"
VECTOR_DB_PATH = "./vector_db"
COLLECTION_NAME = "medical_kb"

from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Clé Google Gemini (chargée depuis .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-1.5-flash"  # Modèle valide pour l'API Google

if not GEMINI_API_KEY:
    raise ValueError("Clé API Gemini non trouvée. Veuillez la définir dans le fichier .env")

class MedicalRAGAssistant:
    def __init__(self):
        logger.info("🧠 Chargement du modèle d'embedding...")
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        logger.info("📁 Initialisation de la base vectorielle...")
        self.chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        self.collection = self.chroma_client.get_or_create_collection(COLLECTION_NAME)

        logger.info("📄 Chargement des connaissances médicales...")
        self.load_medical_knowledge()

    def load_medical_knowledge(self, file_path=DATA_FILE):
        """Charge les documents médicaux et les indexe dans ChromaDB"""
        if self.collection.count() > 0:
            logger.info("🧠 Base vectorielle déjà chargée.")
            return

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier {file_path} introuvable.")

        with open(file_path, "r", encoding="utf-8") as f:
            docs = [json.loads(line) for line in f]

        logger.info(f"✅ {len(docs)} documents médicaux chargés.")

        logger.info("🧠 Génération des embeddings et indexation...")

        for i, doc in enumerate(docs):
            text = f"{doc.get('title', '')}: {doc.get('text', '')}"
            embedding = self.embedder.encode(text).tolist()
            
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[{
                    "source": doc.get("source", "inconnue"),
                    "domain": doc.get("domain", "général")
                }],
                ids=[f"id_{i}"]
            )
            logger.info(f"[{i+1}/{len(docs)}] '{doc['title'][:40]}...'")

        logger.info("✅ Indexation terminée.")

    def retrieve_context(self, question: str, top_k: int = 3):
        """Recherche les documents pertinents dans ChromaDB"""
        query_embedding = self.embedder.encode([question]).tolist()[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results["documents"][0], results["metadatas"][0]

    def generate_answer_with_gemini(self, question: str, context: list):
        """Génère une réponse médicale via Gemini API"""
        prompt = f"""Contexte médical :
{chr(10).join(context)}

Question : {question}

Réponse (précise, sourcée, en français) :"""

        try:
            response = requests.post(
                url=f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}], "role": "user"}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "topP": 0.95,
                        "maxOutputTokens": 300
                    }
                },
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"❌ Erreur API ({response.status_code}) : {response.text[:200]}...")
                return "⚠️ Échec de la génération de réponse."

            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            logger.error(f"💥 Erreur lors de l'appel à Gemini : {str(e)}")
            return "⚠️ Une erreur est survenue pendant la réponse."

def main():
    assistant = MedicalRAGAssistant()
    
    print("🏥 Assistant Santé IA – Tapez 'exit' pour quitter.")
    
    while True:
        question = input("\n❓ Posez votre question médicale : ")
        if question.lower() in ["exit", "quitter", "quit"]:
            break

        context, metadata = assistant.retrieve_context(question)
        answer = assistant.generate_answer_with_gemini(question, context)

        print("\n🧠 Réponse :")
        print(answer)


if __name__ == "__main__":
    main()