# pubmed_collector.py

from Bio import Entrez
import json
import time
import os
import xml.etree.ElementTree as ET

# Configuration obligatoire
Entrez.email = "ahmedqais@gmail.com"  # Remplace par ton email valide
MAX_RESULTS_PER_QUERY = 10  # Réduit pour tester rapidement
RETRY_LIMIT = 3
DELAY_BETWEEN_REQUESTS = 2  # secondes
OUTPUT_FILE = "data/raw/medical_data_for_rag.jsonl"

def fetch_pubmed(query: str, max_results: int = MAX_RESULTS_PER_QUERY):
    """Récupère des articles PubMed selon une requête"""
    print(f"\n🔍 Recherche PubMed pour : '{query}'")

    try:
        # Recherche principale
        handle_search = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        record = Entrez.read(handle_search)

        id_list = record.get("IdList", [])
        if not id_list:
            print(f"⚠️ Aucun article trouvé pour '{query}'")
            return []

        print(f"📄 {len(id_list)} articles trouvés. Récupération des détails...")

        # Récupération détaillée
        handle_fetch = Entrez.efetch(db="pubmed", id=",".join(id_list), rettype="abstract", retmode="xml")
        data = handle_fetch.read()
        
        # Vérifier si c'est du XML ou une chaîne inattendue
        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            print("💥 Erreur : La réponse n'est pas du XML valide.")
            return []

        papers = root.findall(".//PubmedArticle")

        articles = []
        for i, paper in enumerate(papers):
            try:
                pmid_elem = paper.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else "inconnu"

                title_elem = paper.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else ""

                abstract_elem = paper.find(".//AbstractText")
                abstract = abstract_elem.text if abstract_elem is not None else ""

                if title or abstract:
                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "source": "PubMed",
                        "domain": query
                    })

                print(f"[{i+1}/{len(papers)}] {title[:60]}...")
                time.sleep(DELAY_BETWEEN_REQUESTS)

            except Exception as e:
                print(f"❌ Erreur lors du traitement de l'article {i+1}: {str(e)}")
                continue

        return articles

    except Exception as e:
        print(f"💥 Erreur critique lors de la recherche PubMed : {str(e)}")
        return []

def save_to_jsonl(data, file_path):
    """Sauvegarde les données au format JSONL"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"\n✅ {len(data)} articles sauvegardés dans {file_path}")

def main():
    domains = [
        "diabetes treatment",
        "hypertension management",
        "mental health therapy",
        "cardiovascular diseases",
        "infectious diseases"
    ]

    all_articles = []

    for domain in domains:
        retries = 0
        success = False
        while retries < RETRY_LIMIT and not success:
            results = fetch_pubmed(domain, MAX_RESULTS_PER_QUERY)
            if results:
                all_articles.extend(results)
                success = True
                print(f"✅ Succès pour '{domain}'")
            else:
                retries += 1
                print(f"🔄 Nouvelle tentative pour '{domain}' (tentative {retries + 1}/{RETRY_LIMIT})")
                time.sleep(5)

    if all_articles:
        save_to_jsonl(all_articles, OUTPUT_FILE)
    else:
        print("🚫 Aucun article récupéré.")

if __name__ == "__main__":
    main()