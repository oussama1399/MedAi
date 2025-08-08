# create_embeddings.py

from sentence_transformers import SentenceTransformer
import chromadb
import json
import os

DATA_FILE = "data/raw/medical_data.jsonl"
CHROMA_PATH = "vector_db/"

def load_medical_documents(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line)["text"] for line in f]

def create_vector_store(documents):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(documents, show_progress_bar=True)
    
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection("medical_kb")
    
    collection.add(
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=[{"source": "NHS"} for _ in documents],
        ids=[f"id_{i}" for i in range(len(documents))]
    )
    print(f"✅ {len(documents)} documents ajoutés à la base vectorielle.")

if __name__ == "__main__":
    docs = load_medical_documents(DATA_FILE)
    create_vector_store(docs)