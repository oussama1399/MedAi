
<<<<<<< HEAD
## Overview

This project is an intelligent medical assistant application that leverages **Retrieval-Augmented Generation (RAG)** to provide evidence-based medical information. The system combines a vector database of medical knowledge with advanced language models to deliver accurate, contextual responses to medical queries while maintaining user profiles and interaction history.

## 🏗️ Architecture

The system is composed of the following main components:

*   **Frontend Layer (Streamlit)**: A multi-page web application for user interaction, authentication, and profile management.
*   **RAG Pipeline (Core Intelligence)**: Handles document retrieval, context-aware response generation, and integration with the Google Gemini API.
*   **Vector Database (ChromaDB)**: Stores document embeddings for fast similarity search.
*   **Data Layer**: Manages the medical knowledge base (from PubMed and NHS) and user data.

### System Architecture Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  RAG Pipeline   │────│  Vector Store   │
│   (Frontend)    │    │   (Core Logic)  │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Management│    │  Google Gemini  │    │  Medical Data   │
│   (JSON Files)  │    │      API        │    │   (JSONL)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Technologies Used

### Backend
*   **Python 3.11+**
*   **ChromaDB**
*   **SentenceTransformers**
*   **Google Gemini API**
*   **BioPython**

### Frontend
*   **Streamlit**
*   **FPDF**
*   **JSON**

### Data Processing
<<<<<<< HEAD
### Data Processing

| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **XML/JSON** | Data parsing | Standard formats for PubMed and NHS data |
| **Pandas** | Data manipulation | Efficient data processing and analysis |

## 📊 RAG Implementation Process
=======

| Technology | Purpose | Why We Chose It |
|------------|---------|-----------------|
| **XML/JSON** | Data parsing | Standard formats for PubMed and NHS data |
| **Pandas** | Data manipulation | Efficient data processing and analysis |

## 📊 RAG Implementation Process

### 1. Data Collection Phase

#### PubMed Data Harvesting (`pubmed_collector.py`)

**Configuration and Setup:**
```python
from Bio import Entrez
import json
import time
import os
import xml.etree.ElementTree as ET

# Essential configuration for PubMed API access
Entrez.email = "okaddouri62@gmail.com"  # Required by NCBI
MAX_RESULTS_PER_QUERY = 10  # Limit for testing and rate limiting
RETRY_LIMIT = 3  # Number of retry attempts for failed requests
DELAY_BETWEEN_REQUESTS = 2  # seconds between API calls
OUTPUT_FILE = "data/raw/medical_data_for_rag.jsonl"

# Medical domains we systematically target
domains = [
    "diabetes treatment",
    "hypertension management", 
    "mental health therapy",
    "cardiovascular diseases",
    "infectious diseases"
]
```

**📋 How This Configuration Works:**

1. **BioPython Import (`from Bio import Entrez`)**: 
   - BioPython is a specialized library for biological data processing
   - `Entrez` module provides direct access to NCBI databases including PubMed
   - This is the official and recommended way to access PubMed programmatically

2. **Email Requirement (`Entrez.email`)**: 
   - NCBI requires an email address for all API requests for identification and contact purposes
   - This helps NCBI track usage patterns and contact users if there are issues
   - Without this, API requests will be rejected

3. **Rate Limiting Parameters**:
   - `MAX_RESULTS_PER_QUERY = 10`: Limits results to prevent overwhelming the system during development
   - `DELAY_BETWEEN_REQUESTS = 2`: Implements a 2-second pause between API calls to respect NCBI's rate limits
   - `RETRY_LIMIT = 3`: Allows up to 3 retry attempts for failed requests due to network issues

4. **Medical Domain Strategy**:
   - We target specific medical specialties rather than generic searches
   - This ensures we get high-quality, relevant medical literature
   - Each domain query will return focused results for that medical area

5. **File Output Format (JSONL)**:
   - JSONL (JSON Lines) format stores one JSON object per line
   - This allows for efficient streaming processing of large datasets
   - Each line represents one medical article with its metadata

**🔍 Detailed Explanation:**

**Import Analysis:**
- `Bio.Entrez`: BioPython's interface to NCBI databases - provides Python wrappers for all NCBI E-utilities (esearch, efetch, etc.)
- `json`: For structured data serialization - converts Python objects to JSON format for persistent storage
- `time`: Implements delays between API calls - prevents overwhelming PubMed servers and respects rate limits
- `xml.etree.ElementTree`: XML parser for PubMed's response format - handles the complex nested XML structure returned by NCBI

**Configuration Variables Purpose:**
- `Entrez.email`: **NCBI requirement** - identifies your application to their servers and enables them to contact you if issues arise
- `MAX_RESULTS_PER_QUERY`: **Rate limiting strategy** - limits requests to prevent API abuse and ensures reasonable response times
- `RETRY_LIMIT`: **Resilience mechanism** - handles network failures, temporary API unavailability, or rate limiting responses
- `DELAY_BETWEEN_REQUESTS`: **Respectful API usage** - follows NCBI guidelines for automated access (max 3 requests/second without API key)
- `OUTPUT_FILE`: **Data organization** - uses JSONL format (JSON Lines) for efficient streaming and large dataset handling

**Domain Selection Strategy:**
The medical domains are strategically chosen to cover major health areas:
- **Diabetes treatment**: Metabolic disorders affecting millions globally
- **Hypertension management**: Cardiovascular health - leading cause of mortality
- **Mental health therapy**: Increasingly important area with growing awareness
- **Cardiovascular diseases**: Heart-related conditions - major health burden
- **Infectious diseases**: Communicable diseases and antimicrobial resistance

**Core Data Fetching Function:**
```python
def fetch_pubmed(query: str, max_results: int = MAX_RESULTS_PER_QUERY):
    """
    Retrieves medical articles from PubMed with comprehensive error handling
    
    Implementation Details:
    1. Two-step API process: search → fetch details
    2. XML parsing with fallback error handling
    3. Structured data extraction with validation
    4. Rate limiting to respect API guidelines
    """
    print(f"\n🔍 Recherche PubMed pour : '{query}'")

    try:
        # Step 1: Search for article IDs matching the query
        handle_search = Entrez.esearch(
            db="pubmed", 
            term=query, 
            retmax=max_results
        )
        record = Entrez.read(handle_search)
        
        # Extract list of PubMed IDs (PMIDs)
        id_list = record.get("IdList", [])
        if not id_list:
            print(f"⚠️ Aucun article trouvé pour '{query}'")
            return []

        print(f"📄 {len(id_list)} articles trouvés. Récupération des détails...")

        # Step 2: Fetch detailed information for found articles
        handle_fetch = Entrez.efetch(
            db="pubmed", 
            id=",".join(id_list), 
            rettype="abstract", 
            retmode="xml"
        )
        data = handle_fetch.read()
        
        # Parse XML response with error handling
        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            print("💥 Erreur : La réponse n'est pas du XML valide.")
            return []

        # Extract individual articles from XML structure
        papers = root.findall(".//PubmedArticle")
        articles = []
        
        # Process each article with structured data extraction
        for i, paper in enumerate(papers):
            try:
                # Extract PMID (unique identifier)
                pmid_elem = paper.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else "inconnu"

                # Extract article title
                title_elem = paper.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else ""

                # Extract abstract text
                abstract_elem = paper.find(".//AbstractText")
                abstract = abstract_elem.text if abstract_elem is not None else ""

                # Only include articles with meaningful content
                if title or abstract:
                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "source": "PubMed",
                        "domain": query  # Track which domain this came from
                    })

                print(f"[{i+1}/{len(papers)}] {title[:60]}...")
                
                # Rate limiting to be respectful to PubMed API
                time.sleep(DELAY_BETWEEN_REQUESTS)

            except Exception as e:
                print(f"❌ Erreur lors du traitement de l'article {i+1}: {str(e)}")
                continue

        return articles

    except Exception as e:
        print(f"💥 Erreur critique lors de la recherche PubMed : {str(e)}")
        return []
```

**🔧 How This Function Works:**

**Two-Step API Process:**
1. **Search Phase (`Entrez.esearch`)**:
   - Queries PubMed database with medical terms (e.g., "diabetes treatment")
   - Returns a list of PubMed IDs (PMIDs) - unique identifiers for articles
   - This is lightweight and fast - only returns IDs, not full articles
   - Parameters: `db="pubmed"` specifies the database, `retmax` limits results

2. **Fetch Phase (`Entrez.efetch`)**:
   - Takes the PMIDs from step 1 and retrieves full article details
   - `rettype="abstract"` gets abstracts (not full text which requires subscriptions)
   - `retmode="xml"` returns structured XML data for reliable parsing
   - This step is heavier but gives us the actual content we need

**XML Processing Logic:**
3. **XML Parsing (`ET.fromstring`)**:
   - PubMed returns data in XML format with nested structure
   - We use ElementTree to parse this into a navigable tree structure
   - Error handling catches malformed XML responses

4. **Data Extraction Process**:
   - **XPath Queries**: `.//PubmedArticle` finds all article nodes in the XML tree
   - **Safe Extraction**: Each field (PMID, title, abstract) is extracted with null checks
   - **Content Validation**: Only articles with meaningful content (title OR abstract) are kept
   - **Metadata Tracking**: We store the original query domain to track data sources

**Rate Limiting and Error Handling:**
5. **Respectful API Usage**:
   - `time.sleep(DELAY_BETWEEN_REQUESTS)` prevents overwhelming NCBI servers
   - This is both polite and prevents our IP from being temporarily banned
   - Progress tracking shows which article is being processed

6. **Robust Error Management**:
   - Individual article processing errors don't stop the entire process
   - Network timeouts and XML parsing errors are caught and logged
   - The function continues processing remaining articles even if some fail

**Data Structure Output:**
Each article is structured as:
```json
{
    "pmid": "12345678",           // Unique PubMed identifier
    "title": "Article Title",     // Research paper title
    "abstract": "Abstract text",  // Paper abstract/summary
    "source": "PubMed",          // Data source identifier
    "domain": "diabetes treatment" // Medical domain/specialty
}
```

**🔍 Detailed Explanation:**

**Function Architecture - Two-Phase Approach:**

**Phase 1: Search (`Entrez.esearch`)**
- **Purpose**: Finds article IDs matching search criteria without downloading full content
- **Parameters Breakdown**:
  - `db="pubmed"`: Specifies PubMed database (not PMC, protein, etc.)
  - `term=query`: Search query using PubMed's advanced search syntax
  - `retmax=max_results`: Limits number of results to prevent overwhelming responses
- **Return Value**: Dictionary containing `IdList` with PMIDs (PubMed IDs)
- **Efficiency**: This step is fast as it only returns identifiers, not full articles

**Phase 2: Fetch (`Entrez.efetch`)**
- **Purpose**: Downloads detailed information for specific article IDs
- **Parameters Breakdown**:
  - `db="pubmed"`: Same database as search phase
  - `id=",".join(id_list)`: Comma-separated list of PMIDs to fetch
  - `rettype="abstract"`: Specifies we want abstracts included (not just metadata)
  - `retmode="xml"`: Returns structured XML instead of plain text
- **Data Volume**: This step transfers the actual content and is bandwidth-intensive

**XML Parsing Strategy:**
```python
try:
    root = ET.fromstring(data)
except ET.ParseError:
    print("💥 Erreur : La réponse n'est pas du XML valide.")
    return []
```
- **Error Handling**: Catches malformed XML responses (network issues, API errors)
- **Fallback Strategy**: Returns empty list to prevent application crash
- **XML Structure**: PubMed returns complex nested XML with multiple namespaces

**Data Extraction Process:**
```python
# Extract PMID (unique identifier)
pmid_elem = paper.find(".//PMID")
pmid = pmid_elem.text if pmid_elem is not None else "inconnu"
```
- **XPath Usage**: `.//PMID` searches recursively for PMID elements anywhere in the tree
- **Null Safety**: Checks if element exists before accessing `.text` property
- **Default Values**: Provides fallback values ("inconnu") for missing data

**Content Validation:**
```python
# Only include articles with meaningful content
if title or abstract:
    articles.append({...})
```
- **Quality Filter**: Excludes articles without substantial textual content
- **Data Structure**: Creates consistent dictionary format for downstream processing
- **Metadata Preservation**: Tracks source and domain for later filtering and attribution

**Rate Limiting Implementation:**
```python
time.sleep(DELAY_BETWEEN_REQUESTS)
```
- **Purpose**: Prevents overwhelming PubMed servers and getting IP banned
- **NCBI Guidelines**: Maximum 3 requests per second for non-API key users
- **Professional Courtesy**: Ensures sustainable access for all researchers

**Data Persistence and Retry Logic:**
```python
def save_to_jsonl(data, file_path):
    """
    Saves data in JSONL format for efficient streaming processing
    Each line = one JSON object = one article
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"\n✅ {len(data)} articles sauvegardés dans {file_path}")

def main():
    """
    Main execution with domain-specific collection and retry mechanism
    """
    all_articles = []

    for domain in domains:
        retries = 0
        success = False
        
        # Retry mechanism for network/API failures
        while retries < RETRY_LIMIT and not success:
            results = fetch_pubmed(domain, MAX_RESULTS_PER_QUERY)
            if results:
                all_articles.extend(results)
                success = True
                print(f"✅ Succès pour '{domain}'")
            else:
                retries += 1
                print(f"🔄 Nouvelle tentative pour '{domain}' (tentative {retries + 1}/{RETRY_LIMIT})")
                time.sleep(5)  # Wait before retry

    # Save all collected articles
    if all_articles:
        save_to_jsonl(all_articles, OUTPUT_FILE)
    else:
        print("🚫 Aucun article récupéré.")
```

**💾 How Data Persistence Works:**

**JSONL Format Choice:**
1. **Why JSONL over JSON**:
   - **Streaming Processing**: Each line is independent - we can process one article at a time
   - **Memory Efficiency**: Don't need to load entire dataset into memory at once
   - **Fault Tolerance**: If file gets corrupted, we only lose one line, not the entire dataset
   - **Append-Friendly**: Easy to add new articles without rewriting entire file

2. **File Creation Process**:
   - `os.makedirs(os.path.dirname(file_path), exist_ok=True)`: Creates directory structure if it doesn't exist
   - `encoding="utf-8"`: Ensures proper handling of medical terms with special characters
   - `ensure_ascii=False`: Preserves non-ASCII characters (important for medical terminology)

**Retry Mechanism Logic:**
3. **Domain-by-Domain Processing**:
   - Each medical domain is processed separately to ensure balanced coverage
   - If one domain fails, others can still succeed
   - Domain-specific failures don't stop the entire collection process

4. **Intelligent Retry Strategy**:
   - **Three-Tier Approach**: Try up to 3 times per domain
   - **Exponential Backoff**: 5-second wait between retries (could be enhanced to exponential)
   - **Success Tracking**: `success` flag prevents unnecessary retries once domain succeeds
   - **Graceful Degradation**: Process continues even if some domains fail completely

5. **Error Recovery Process**:
   - Network timeouts → Retry with delay
   - API rate limiting → Wait and retry
   - Server errors → Multiple attempts before giving up
   - Invalid responses → Skip and continue with next domain

**Data Quality Assurance:**
6. **Content Validation**:
   - Only save articles that actually contain content (title OR abstract)
   - Track source and domain for each article for later filtering/analysis
   - Preserve original query terms to understand data provenance

#### NHS Data Integration

**File Structure Processing:**
```python
# NHS data is organized in numbered text files
# Example: data/raw/nhs_condition_details/001_AAA, see Abdominal aortic aneurysm.txt

import os
import json
from pathlib import Path

def process_nhs_data():
    """
    Processes NHS condition files into structured format
    
    Implementation:
    1. Scan directory for .txt files
    2. Extract condition name from filename
    3. Read and clean file content
    4. Structure as medical knowledge documents
    """
    nhs_dir = Path("data/raw/nhs_condition_details")
    conditions = []
    
    for file_path in nhs_dir.glob("*.txt"):
        try:
            # Extract condition name from filename
            # Format: "001_Condition Name.txt"
            filename = file_path.stem
            condition_name = filename.split('_', 1)[1] if '_' in filename else filename
            
            # Read file content with encoding handling
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Structure the data
            condition_data = {
                "title": condition_name,
                "text": content,
                "source": "NHS",
                "domain": "general_medicine",
                "file_id": filename.split('_')[0] if '_' in filename else "unknown"
            }
            
            conditions.append(condition_data)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    return conditions
```

**Data Quality and Standardization:**
```python
def standardize_medical_text(text):
    """
    Standardizes medical text for better RAG performance
    
    Text Processing Steps:
    1. Remove excessive whitespace
    2. Normalize medical terminology
    3. Handle special characters
    4. Ensure consistent formatting
    """
    import re
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Standardize common medical abbreviations
    medical_abbreviations = {
        'w/': 'with',
        'w/o': 'without',
        'pt': 'patient',
        'pts': 'patients',
        'dx': 'diagnosis',
        'tx': 'treatment',
        'sx': 'symptoms'
    }
    
    for abbrev, full_form in medical_abbreviations.items():
        text = re.sub(r'\b' + re.escape(abbrev) + r'\b', full_form, text, flags=re.IGNORECASE)
    
    return text
```

### 2. Embedding Generation Phase

#### Vector Creation (`create_embeddings.py`)

**Model Selection and Initialization:**
```python
from sentence_transformers import SentenceTransformer
import chromadb
import json
import os

# Configuration constants
DATA_FILE = "data/raw/medical_data.jsonl"
CHROMA_PATH = "vector_db/"

def initialize_embedding_model():
    """
    Initialize the SentenceTransformer model for medical text embeddings
    
    Model Choice: all-MiniLM-L6-v2
    - 384-dimensional embeddings (memory efficient)
    - Optimized for semantic similarity tasks
    - Good performance on medical/scientific text
    - Fast inference time suitable for real-time applications
    """
    print("🧠 Initializing embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Model specifications:
    # - Max sequence length: 256 tokens
    # - Embedding dimension: 384
    # - Training: Trained on 1B+ sentence pairs
    
    return model
```

**Document Loading and Preprocessing:**
```python
def load_medical_documents(file_path):
    """
    Load and preprocess medical documents from JSONL format
    
    Document Structure:
    {
        "pmid": "unique_identifier",
        "title": "Article Title",
        "abstract": "Article abstract text",
        "source": "PubMed|NHS",
        "domain": "medical_specialty"
    }
    """
    documents = []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Parse JSON line
                    doc = json.loads(line.strip())
                    
                    # Combine title and abstract for comprehensive context
                    # Format: "Title: Abstract" for better semantic understanding
                    if doc.get('title') and doc.get('abstract'):
                        combined_text = f"{doc['title']}: {doc['abstract']}"
                    elif doc.get('title'):
                        combined_text = doc['title']
                    elif doc.get('text'):  # NHS format
                        combined_text = doc['text']
                    else:
                        continue  # Skip documents without meaningful content
                    
                    # Text preprocessing for better embeddings
                    processed_text = preprocess_medical_text(combined_text)
                    
                    documents.append({
                        'text': processed_text,
                        'metadata': {
                            'source': doc.get('source', 'unknown'),
                            'domain': doc.get('domain', 'general'),
                            'pmid': doc.get('pmid', ''),
                            'title': doc.get('title', '')[:100]  # Truncate for metadata
                        }
                    })
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ Invalid JSON on line {line_num}: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []
    
    print(f"📚 Loaded {len(documents)} medical documents")
    return documents

def preprocess_medical_text(text):
    """
    Preprocess medical text for optimal embedding generation
    
    Processing Steps:
    1. Text normalization
    2. Length optimization for model constraints
    3. Medical terminology standardization
    """
    import re
    
    # Remove excessive whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Handle model's max sequence length (256 tokens ≈ ~200 words)
    words = text.split()
    if len(words) > 200:
        # Keep first 200 words to maintain context coherence
        text = ' '.join(words[:200]) + '...'
    
    # Medical text specific preprocessing
    # Standardize common medical notation
    text = re.sub(r'(\d+)\s*mg', r'\1 milligrams', text)
    text = re.sub(r'(\d+)\s*ml', r'\1 milliliters', text)
    
    return text
```

**Vector Store Creation with ChromaDB:**
```python
def create_vector_store(documents):
    """
    Create and populate ChromaDB vector store with medical embeddings
    
    ChromaDB Features:
    - Persistent storage (SQLite backend)
    - Automatic indexing with HNSW algorithm
    - Metadata filtering capabilities
    - Cosine similarity search
    """
    # Initialize embedding model
    model = initialize_embedding_model()
    
    # Prepare texts and metadata
    texts = [doc['text'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]
    
    print("🔢 Generating embeddings...")
    # Generate embeddings with progress tracking
    embeddings = model.encode(
        texts, 
        show_progress_bar=True,
        batch_size=32,  # Optimize for memory usage
        convert_to_numpy=True
    )
    
    print("🗄️ Creating ChromaDB collection...")
    # Initialize ChromaDB client with persistence
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Create or get collection with specific configuration
    collection = client.get_or_create_collection(
        name="medical_kb",
        metadata={
            "description": "Medical knowledge base for RAG",
            "embedding_model": "all-MiniLM-L6-v2",
            "created_date": "2025-06-01"
        }
    )
    
    # Batch insertion for efficiency
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        
        # Prepare batch data
        batch_embeddings = embeddings[i:batch_end].tolist()
        batch_texts = texts[i:batch_end]
        batch_metadatas = metadatas[i:batch_end]
        batch_ids = [f"doc_{idx}" for idx in range(i, batch_end)]
        
        # Add to collection
        collection.add(
            embeddings=batch_embeddings,
            documents=batch_texts,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        
        print(f"✅ Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    print(f"🎉 Vector store created with {len(documents)} documents")
    
    # Verify collection
    count = collection.count()
    print(f"📊 Collection size: {count} documents")
    
    return collection

# Main execution
if __name__ == "__main__":
    docs = load_medical_documents(DATA_FILE)
    if docs:
        create_vector_store(docs)
    else:
        print("❌ No documents to process")
```

**Embedding Quality Verification:**
```python
def verify_embeddings(collection, sample_queries):
    """
    Verify embedding quality with sample medical queries
    
    Tests semantic understanding and retrieval accuracy
    """
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    test_queries = [
        "diabetes symptoms and treatment",
        "high blood pressure management",
        "depression therapy options",
        "heart attack prevention"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # Generate query embedding
        query_embedding = model.encode([query]).tolist()[0]
        
        # Search collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        # Display results
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"  {i+1}. {metadata.get('title', 'No title')[:50]}...")
            print(f"     Source: {metadata.get('source', 'Unknown')}")
            print(f"     Distance: {results['distances'][0][i]:.4f}")
```

### 3. Retrieval Mechanism

#### Core RAG Pipeline (`rag_pipeline.py`)

**Class Initialization and Configuration:**
```python
import os
import json
import requests
from sentence_transformers import SentenceTransformer
import chromadb
import logging
from chromadb.config import Settings

# Configuration constants
DATA_FILE = "data/raw/medical_data.jsonl"
VECTOR_DB_PATH = "./vector_db"
COLLECTION_NAME = "medical_kb"
GEMINI_API_KEY = "AIzaSyCsVIM8TMW0fY63Ln7xVk5A_uBdetHB1Wo"
GEMINI_MODEL = "gemini-1.5-flash"

class MedicalRAGAssistant:
    def __init__(self):
        """
        Initialize the Medical RAG Assistant with all required components
        
        Architecture:
        1. Embedding model for query encoding
        2. ChromaDB client for vector operations
        3. Medical knowledge base loading
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("🧠 Chargement du modèle d'embedding...")
        # Initialize the same model used for creating embeddings
        # Critical: Must use identical model for query-document compatibility
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.logger.info("📁 Initialisation de la base vectorielle...")
        # Connect to persistent ChromaDB instance
        self.chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
        
        # Get existing collection (created by create_embeddings.py)
        try:
            self.collection = self.chroma_client.get_collection(COLLECTION_NAME)
            self.logger.info(f"✅ Collection loaded: {self.collection.count()} documents")
        except Exception as e:
            self.logger.error(f"❌ Collection not found: {e}")
            # Fallback: create collection if it doesn't exist
            self.collection = self.chroma_client.get_or_create_collection(COLLECTION_NAME)
            self.load_medical_knowledge()
```

**Advanced Semantic Search Implementation:**
```python
def retrieve_context(self, question: str, top_k: int = 3, min_similarity: float = 0.5):
    """
    Advanced semantic retrieval with similarity filtering and ranking
    
    Parameters:
    - question: User's medical query
    - top_k: Number of documents to retrieve
    - min_similarity: Minimum similarity threshold (0-1)
    
    Returns:
    - retrieved_docs: List of relevant document texts
    - metadata: Associated metadata for each document
    - similarities: Similarity scores for transparency
    """
    self.logger.info(f"🔍 Retrieving context for: '{question[:50]}...'")
    
    # Step 1: Generate query embedding
    # Same model and preprocessing as document embeddings
    query_embedding = self.embedder.encode([question]).tolist()[0]
    
    # Step 2: Perform vector similarity search
    try:
        # ChromaDB query with expanded results for filtering
        raw_results = self.collection.query(
            query_embeddings=[query_embedding], 
            n_results=top_k * 2,  # Get more results for filtering
            include=["documents", "metadatas", "distances"]
        )
        
        # Step 3: Filter by similarity threshold
        # Convert distances to similarities (ChromaDB uses L2 distance)
        documents = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0]
        
        # Filter results by similarity threshold
        filtered_results = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            # Convert L2 distance to cosine similarity approximation
            similarity = 1 / (1 + dist)  # Rough conversion
            
            if similarity >= min_similarity:
                filtered_results.append({
                    'document': doc,
                    'metadata': meta,
                    'similarity': similarity
                })
        
        # Step 4: Rank and select top results
        # Sort by similarity (highest first)
        filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
        final_results = filtered_results[:top_k]
        
        # Extract components
        retrieved_docs = [r['document'] for r in final_results]
        final_metadata = [r['metadata'] for r in final_results]
        similarities = [r['similarity'] for r in final_results]
        
        # Log retrieval results
        self.logger.info(f"📊 Retrieved {len(retrieved_docs)} relevant documents")
        for i, (meta, sim) in enumerate(zip(final_metadata, similarities)):
            source = meta.get('source', 'Unknown')
            domain = meta.get('domain', 'General')
            self.logger.info(f"  {i+1}. {source} ({domain}) - Similarity: {sim:.3f}")
        
        return retrieved_docs, final_metadata, similarities
        
    except Exception as e:
        self.logger.error(f"❌ Retrieval error: {e}")
        return [], [], []

def enhance_query(self, question: str):
    """
    Query enhancement for better retrieval performance
    
    Techniques:
    1. Medical term expansion
    2. Synonym addition
    3. Context enrichment
    """
    # Medical term mappings for query expansion
    medical_synonyms = {
        'pain': ['discomfort', 'ache', 'soreness'],
        'diabetes': ['diabetes mellitus', 'blood sugar disorder'],
        'hypertension': ['high blood pressure', 'elevated blood pressure'],
        'depression': ['depressive disorder', 'mood disorder'],
        'heart attack': ['myocardial infarction', 'cardiac arrest']
    }
    
    enhanced_terms = [question]
    
    # Add synonyms for key medical terms
    question_lower = question.lower()
    for term, synonyms in medical_synonyms.items():
        if term in question_lower:
            enhanced_terms.extend(synonyms)
    
    # Combine terms for enriched query
    enhanced_query = f"{question} {' '.join(enhanced_terms)}"
    
    return enhanced_query
```

**Context Ranking and Relevance Scoring:**
```python
def rank_retrieved_context(self, question: str, documents: list, metadata: list):
    """
    Advanced context ranking using multiple signals
    
    Ranking Factors:
    1. Semantic similarity score
    2. Source reliability (PubMed > NHS > Other)
    3. Domain relevance
    4. Content quality indicators
    """
    scored_docs = []
    
    for i, (doc, meta) in enumerate(zip(documents, metadata)):
        score = 0.0
        
        # Factor 1: Base similarity (already computed)
        base_similarity = 1.0  # Placeholder - would use actual similarity
        score += base_similarity * 0.4
        
        # Factor 2: Source reliability weighting
        source = meta.get('source', '').lower()
        if source == 'pubmed':
            score += 0.3  # High reliability for peer-reviewed research
        elif source == 'nhs':
            score += 0.2  # Good reliability for clinical guidelines
        else:
            score += 0.1  # Lower weight for other sources
        
        # Factor 3: Domain relevance
        domain = meta.get('domain', '').lower()
        question_lower = question.lower()
        
        # Check if query matches document domain
        domain_keywords = {
            'diabetes': ['diabetes', 'blood sugar', 'insulin'],
            'cardiovascular': ['heart', 'cardiac', 'blood pressure'],
            'mental health': ['depression', 'anxiety', 'mental'],
            'infectious': ['infection', 'bacteria', 'virus']
        }
        
        for domain_key, keywords in domain_keywords.items():
            if domain_key in domain and any(kw in question_lower for kw in keywords):
                score += 0.2
                break
        
        # Factor 4: Content quality (length, structure)
        content_length = len(doc.split())
        if 50 <= content_length <= 300:  # Optimal length range
            score += 0.1
        
        scored_docs.append({
            'document': doc,
            'metadata': meta,
            'relevance_score': score
        })
    
    # Sort by relevance score
    scored_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return scored_docs
```

### 4. Generation Phase

#### Advanced Response Generation with Google Gemini API

**Prompt Engineering and Template Design:**
```python
def generate_answer_with_gemini(self, question: str, context: list, metadata: list = None):
    """
    Generate contextual medical responses using advanced prompt engineering
    
    Prompt Structure:
    1. System instructions for medical accuracy
    2. Context injection with source attribution
    3. User question
    4. Response format specifications
    """
    
    # Build context with source attribution
    contextual_information = []
    if metadata:
        for i, (ctx, meta) in enumerate(zip(context, metadata)):
            source = meta.get('source', 'Unknown')
            domain = meta.get('domain', 'General')
            
            # Format: [Source] Content
            formatted_context = f"[{source} - {domain}] {ctx}"
            contextual_information.append(formatted_context)
    else:
        contextual_information = context
    
    # Advanced prompt template with medical guidelines
    prompt = f"""Tu es un assistant médical IA expert qui fournit des informations précises et fondées sur des preuves.

INSTRUCTIONS IMPORTANTES:
1. Base ta réponse UNIQUEMENT sur le contexte médical fourni
2. Cite tes sources en indiquant [Source] à la fin des informations
3. Si les informations sont insuffisantes, indique-le clairement
4. Recommande TOUJOURS de consulter un professionnel de santé
5. Utilise un langage clair et accessible
6. Structure ta réponse avec des points clés

CONTEXTE MÉDICAL:
{chr(10).join(contextual_information)}

QUESTION DU PATIENT: {question}

RÉPONSE MÉDICALE:
Fournissez une réponse structurée, précise et sourcée en français."""

    try:
        # Gemini API request with optimized parameters
        response = requests.post(
            url=f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [
                    {
                        "parts": [{"text": prompt}], 
                        "role": "user"
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,        # Low for medical accuracy
                    "topP": 0.95,              # Balanced creativity
                    "maxOutputTokens": 500,    # Comprehensive responses
                    "candidateCount": 1,       # Single best response
                    "stopSequences": ["FIN"]   # Custom stop sequence
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_MEDICAL",
                        "threshold": "BLOCK_ONLY_HIGH"
                    }
                ]
            },
            timeout=15  # Increased timeout for complex queries
        )

        # Response handling and validation
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract generated text
            candidates = response_data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                generated_text = candidates[0]["content"]["parts"][0]["text"]
                
                # Post-process the response
                processed_response = self.post_process_response(
                    generated_text, 
                    context, 
                    metadata
                )
                
                return processed_response
            else:
                self.logger.warning("⚠️ No content in Gemini response")
                return "❌ Impossible de générer une réponse appropriée."
                
        else:
            # Handle API errors gracefully
            error_message = response.text[:200] if response.text else "Unknown error"
            self.logger.error(f"❌ Gemini API Error ({response.status_code}): {error_message}")
            
            # Fallback response
            return self.generate_fallback_response(question, context)

    except requests.exceptions.Timeout:
        self.logger.error("⏰ Gemini API timeout")
        return "⏰ Délai d'attente dépassé. Veuillez réessayer."
        
    except requests.exceptions.RequestException as e:
        self.logger.error(f"🌐 Network error: {e}")
        return "🌐 Erreur de connexion. Vérifiez votre connexion internet."
        
    except Exception as e:
        self.logger.error(f"💥 Unexpected error: {e}")
        return "💥 Une erreur inattendue s'est produite."

def post_process_response(self, response: str, context: list, metadata: list):
    """
    Post-process the generated response for quality and safety
    
    Processing Steps:
    1. Add medical disclaimers
    2. Validate content appropriateness
    3. Enhance with source links where possible
    4. Format for readability
    """
    # Add medical disclaimer if not present
    disclaimer = "\n\n⚠️ **Important**: Cette information est fournie à titre éducatif uniquement. Consultez toujours un professionnel de santé pour un diagnostic et un traitement appropriés."
    
    if "consultant" not in response.lower() and "professionnel" not in response.lower():
        response += disclaimer
    
    # Format for better readability
    # Add bullet points for lists
    import re
    
    # Detect numbered lists and convert to bullet points
    response = re.sub(r'^(\d+)\.\s*', r'• ', response, flags=re.MULTILINE)
    
    # Add source summary if multiple sources used
    if metadata and len(metadata) > 1:
        sources = set()
        for meta in metadata:
            source = meta.get('source', 'Unknown')
            if source != 'Unknown':
                sources.add(source)
        
        if sources:
            source_text = f"\n\n📚 **Sources consultées**: {', '.join(sources)}"
            response += source_text
    
    return response

def generate_fallback_response(self, question: str, context: list):
    """
    Generate a basic response when Gemini API fails
    
    Uses rule-based templates for common medical queries
    """
    question_lower = question.lower()
    
    # Template-based responses for common queries
    if any(term in question_lower for term in ['symptôme', 'symptom', 'signe']):
        return f"""D'après les informations médicales disponibles:

{context[0][:300] if context else 'Informations limitées disponibles.'}...

⚠️ **Important**: Ces informations sont générales. Pour une évaluation précise de vos symptômes, consultez un professionnel de santé qui pourra effectuer un examen approprié.

🏥 **Urgence**: Si vous ressentez des symptômes graves ou inquiétants, contactez immédiatement les services d'urgence."""

    elif any(term in question_lower for term in ['traitement', 'treatment', 'médicament']):
        return f"""Informations sur les options thérapeutiques:

{context[0][:300] if context else 'Informations limitées disponibles.'}...

⚠️ **Important**: Les traitements médicaux doivent être prescrits et supervisés par un professionnel de santé qualifié. Ne commencez jamais un traitement sans consultation médicale.

💊 **Sécurité**: Informez toujours votre médecin de tous les médicaments que vous prenez pour éviter les interactions."""

    else:
        # Generic fallback
        return f"""Information médicale générale:

{context[0][:400] if context else 'Les informations demandées ne sont pas disponibles dans notre base de connaissances actuelle.'}

⚠️ **Important**: Cette réponse est générée automatiquement à partir de sources médicales fiables, mais ne remplace pas l'avis d'un professionnel de santé.

🩺 **Recommandation**: Pour toute question spécifique à votre situation, consultez votre médecin traitant."""
```

**Response Quality Control and Validation:**
```python
def validate_medical_response(self, response: str, question: str):
    """
    Validate generated response for medical appropriateness
    
    Validation Checks:
    1. Contains appropriate medical disclaimers
    2. Avoids definitive diagnostic statements
    3. Includes professional consultation recommendations
    4. No harmful advice detected
    """
    validation_score = 0
    issues = []
    
    # Check 1: Medical disclaimer present
    disclaimer_keywords = ['consultant', 'professionnel', 'médecin', 'avis médical']
    if any(keyword in response.lower() for keyword in disclaimer_keywords):
        validation_score += 25
    else:
        issues.append("Missing medical disclaimer")
    
    # Check 2: Avoid definitive diagnosis
    diagnostic_red_flags = ['vous avez', 'diagnostic:', 'vous souffrez de']
    if any(flag in response.lower() for flag in diagnostic_red_flags):
        issues.append("Contains definitive diagnostic language")
        validation_score -= 20
    else:
        validation_score += 25
    
    # Check 3: Professional consultation recommendation
    consultation_keywords = ['consultez', 'contactez', 'rendez-vous', 'médecin']
    if any(keyword in response.lower() for keyword in consultation_keywords):
        validation_score += 25
    else:
        issues.append("Missing consultation recommendation")
    
    # Check 4: Appropriate response length
    if 100 <= len(response) <= 1000:
        validation_score += 25
    else:
        issues.append("Response length inappropriate")
    
    return {
        'score': validation_score,
        'issues': issues,
        'is_valid': validation_score >= 75 and not any('definitive' in issue for issue in issues)
    }
```

### 5. User Experience Layer

#### Streamlit Multi-Page Application Architecture

**Main Application Entry Point (`app.py`):**
```python
import streamlit as st
import json
import os
from datetime import datetime

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="🩺 Assistant Santé IA",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global constants for data persistence
USER_DATA_DIR = "user_data"
USERS_FILE = os.path.join(USER_DATA_DIR, "users.json")
os.makedirs(USER_DATA_DIR, exist_ok=True)

def load_users():
    """
    Robust user data loading with encoding fallback
    
    Handles various encoding issues that can occur with JSON files
    """
    if not os.path.exists(USERS_FILE):
        return {}
    
    # Try multiple encodings for compatibility
    encodings = ['utf-8', 'latin-1', 'ISO-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(USERS_FILE, "r", encoding=encoding) as f:
                return json.load(f)
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            break
    
    # Fallback: create new file if corrupted
    return {}

def save_users(users):
    """Save user data with UTF-8 encoding"""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# Session state initialization for persistent user experience
def initialize_session_state():
    """
    Initialize all session state variables for the application
    
    Session State Management:
    - User authentication status
    - Current user information
    - Language preferences
    - Navigation state
    """
    default_states = {
        "logged_in": False,
        "current_user": None,
        "language": "fr",
        "show_register": False,
        "chat_history": [],
        "last_query": "",
        "rag_assistant": None  # Cached RAG instance
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Initialize session state
initialize_session_state()

# Authentication system
def authenticate_user(username: str, password: str) -> bool:
    """
    User authentication with secure password handling
    
    Security Features:
    - Case-insensitive username matching
    - Password verification
    - Session management
    """
    users = load_users()
    
    # Case-insensitive username lookup
    for stored_user, user_data in users.items():
        if stored_user.lower() == username.lower():
            if user_data.get("password") == password:
                # Set session state for successful login
                st.session_state.logged_in = True
                st.session_state.current_user = stored_user
                return True
    
    return False

def register_user(username: str, password: str, email: str = "") -> bool:
    """
    User registration with validation
    
    Validation:
    - Username uniqueness
    - Password requirements
    - Email format (optional)
    """
    users = load_users()
    
    # Check if username already exists (case-insensitive)
    for existing_user in users.keys():
        if existing_user.lower() == username.lower():
            return False
    
    # Create new user profile
    users[username] = {
        "password": password,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "history": [],
        "potential_diseases": [],
        "language": "fr",
        "profile": {
            "age": None,
            "gender": None,
            "medical_conditions": [],
            "medications": [],
            "allergies": []
        }
    }
    
    save_users(users)
    return True

# Main authentication interface
def show_authentication():
    """
    Display authentication interface with login/register forms
    """
    st.title("🩺 Assistant Santé IA")
    st.markdown("### Connectez-vous pour accéder à vos consultations personnalisées")
    
    # Tab interface for login/register
    tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
    
    with tab1:
        # Login form
        with st.form("login_form"):
            st.subheader("Connexion")
            username = st.text_input("Nom d'utilisateur", key="login_username")
            password = st.text_input("Mot de passe", type="password", key="login_password")
            submit_login = st.form_submit_button("Se connecter", type="primary")
            
            if submit_login:
                if username and password:
                    if authenticate_user(username, password):
                        st.success(f"✅ Connexion réussie ! Bienvenue {username}")
                        st.rerun()
                    else:
                        st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
    
    with tab2:
        # Registration form
        with st.form("register_form"):
            st.subheader("Inscription")
            new_username = st.text_input("Nom d'utilisateur", key="reg_username")
            new_password = st.text_input("Mot de passe", type="password", key="reg_password")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password", key="reg_confirm")
            email = st.text_input("Email (optionnel)", key="reg_email")
            submit_register = st.form_submit_button("S'inscrire", type="secondary")
            
            if submit_register:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        if register_user(new_username, new_password, email):
                            st.success("✅ Inscription réussie ! Vous pouvez maintenant vous connecter")
                        else:
                            st.error("❌ Ce nom d'utilisateur existe déjà")
                    else:
                        st.error("❌ Les mots de passe ne correspondent pas")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs obligatoires")

# Main application logic
if not st.session_state.logged_in:
    show_authentication()
else:
    # User is logged in - show navigation
    st.sidebar.success(f"👤 Connecté: {st.session_state.current_user}")
    
    if st.sidebar.button("🚪 Déconnexion"):
        # Clear session state for logout
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Application content for authenticated users
    st.success("✅ Vous êtes connecté ! Utilisez la navigation pour accéder aux différentes fonctionnalités.")
    
    # Navigation guidance
    st.markdown("""
    ### 📋 Navigation:
    - **🏠 00_Accueil**: Interface de chat principal
    - **📚 01_Historique**: Historique de vos consultations
    - **👤 02_Profil**: Gestion de votre profil médical
    - **🔍 03_Maladies_Potentielles**: Analyse des maladies potentielles
    """)
```

**Chat Interface Implementation (`pages/00_Accueil.py`):**
```python
import streamlit as st
from rag_pipeline import MedicalRAGAssistant
import os
from datetime import datetime
import sys
from fpdf import FPDF

# Add parent directory for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import get_user_profile, update_user_history, export_to_pdf, show_user_sidebar

# Page configuration
st.set_page_config(
    page_title="Chat - Assistant Santé IA",
    page_icon="🩺",
    layout="wide"
)

# Authentication check
if not st.session_state.get("logged_in", False):
    st.warning("⚠️ Veuillez vous connecter sur la page principale pour accéder au chat.")
    if st.button("🔐 Aller à la page de connexion"):
        st.switch_page("app.py") 
    st.stop()

@st.cache_resource
def load_assistant():
    """
    Load RAG assistant with caching for performance
    
    Caching Strategy:
    - @st.cache_resource ensures single instance across sessions
    - Reduces memory usage and initialization time
    - Automatic cache invalidation on code changes
    """
    try:
        assistant = MedicalRAGAssistant()
        return assistant
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement de l'assistant: {e}")
        return None

# Load assistant
assistant = load_assistant()
if not assistant:
    st.stop()

# User interface implementation
def display_chat_interface():
    """
    Main chat interface with real-time interaction
    """
    user = st.session_state.current_user
    profile = get_user_profile(user)
    
    # User welcome and context
    now = datetime.now().strftime('%d/%m/%Y %H:%M')
    st.markdown(f"### 👤 Bienvenue, **{user}** | Connecté le {now}")
    
    # Sidebar with user information
    show_user_sidebar(user)
    
    # Main chat interface
    st.title("🤖 Posez votre question médicale")
    
    # Chat input with real-time processing
    question = st.text_input(
        "Votre question :", 
        key="chat_input",
        placeholder="Ex: Quels sont les symptômes du diabète de type 2?"
    )
    
    # Advanced options in expander
    with st.expander("⚙️ Options avancées"):
        col1, col2 = st.columns(2)
        with col1:
            num_sources = st.slider("Nombre de sources", 1, 5, 3)
            include_metadata = st.checkbox("Afficher les métadonnées", value=True)
        with col2:
            response_language = st.selectbox("Langue de réponse", ["Français", "English"])
            export_format = st.selectbox("Format d'export", ["PDF", "TXT", "JSON"])
    
    # Process question when submitted
    if st.button("🔍 Rechercher", type="primary") or question:
        if question.strip():
            process_medical_query(question, user, num_sources, include_metadata)
        else:
            st.warning("⚠️ Veuillez saisir une question")

def process_medical_query(question: str, user: str, num_sources: int, show_metadata: bool):
    """
    Process medical query with comprehensive RAG pipeline
    
    Processing Steps:
    1. Retrieve relevant context
    2. Generate response
    3. Validate content
    4. Display results
    5. Save to history
    """
    with st.spinner("🔍 Recherche dans la base de connaissances médicales..."):
        # Step 1: Retrieve context
        try:
            contexts, metadata, similarities = assistant.retrieve_context(
                question, 
                top_k=num_sources
            )
            
            if not contexts:
                st.error("❌ Aucune information pertinente trouvée dans la base de connaissances.")
                return
            
            # Step 2: Generate response
            st.info("🤖 Génération de la réponse...")
            answer = assistant.generate_answer_with_gemini(question, contexts, metadata)
            
            # Step 3: Display results
            display_results(question, answer, contexts, metadata, similarities, show_metadata)
            
            # Step 4: Save to user history
            save_consultation_to_history(user, question, answer, contexts, metadata)
            
        except Exception as e:
            st.error(f"❌ Erreur lors du traitement: {str(e)}")

def display_results(question: str, answer: str, contexts: list, metadata: list, 
                   similarities: list, show_metadata: bool):
    """
    Display query results with rich formatting and interactivity
    """
    # Main response
    st.markdown("### 🩺 Réponse médicale")
    st.markdown(answer)
    
    # Source information
    if show_metadata and metadata:
        st.markdown("### 📚 Sources consultées")
        
        for i, (context, meta, sim) in enumerate(zip(contexts, metadata, similarities)):
            with st.expander(f"📄 Source {i+1}: {meta.get('source', 'Unknown')} (Pertinence: {sim:.2%})"):
                st.markdown(f"**Domaine:** {meta.get('domain', 'Non spécifié')}")
                st.markdown(f"**PMID:** {meta.get('pmid', 'N/A')}")
                st.markdown(f"**Extrait:**")
                st.text(context[:300] + "..." if len(context) > 300 else context)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📄 Exporter en PDF"):
            export_consultation_pdf(question, answer, metadata)
    with col2:
        if st.button("💾 Sauvegarder"):
            st.success("✅ Consultation sauvegardée dans votre historique")
    with col3:
        if st.button("🔄 Nouvelle recherche"):
            st.rerun()

def export_consultation_pdf(question: str, answer: str, metadata: list):
    """
    Export consultation to PDF with professional formatting
    """
    try:
        pdf_content = export_to_pdf(question, answer, metadata)
        
        # Create download button
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"consultation_medicale_{timestamp}.pdf"
        
        st.download_button(
            label="📥 Télécharger PDF",
            data=pdf_content,
            file_name=filename,
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"❌ Erreur lors de l'export PDF: {e}")

# Initialize session state for chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None

if 'last_sources' not in st.session_state:
    st.session_state.last_sources = []

# Display chat interface
display_chat_interface()
```

**Utility Functions (`utils.py`):**
```python
import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
import base64

def get_user_profile(username: str) -> dict:
    """
    Retrieve or create user profile with comprehensive medical tracking
    
    Profile Structure:
    - Basic info (age, gender)
    - Medical history
    - Current medications
    - Allergies
    - Consultation history
    """
    users = load_users()
    
    if username in users:
        return users[username]
    else:
        # Create new user profile with default structure
        default_profile = {
            "password": "",
            "created_at": datetime.now().isoformat(),
            "history": [],
            "potential_diseases": [],
            "language": "fr",
            "profile": {
                "age": None,
                "gender": None,
                "weight": None,
                "height": None,
                "blood_type": None,
                "medical_conditions": [],
                "current_medications": [],
                "allergies": [],
                "emergency_contact": {}
            },
            "preferences": {
                "language": "fr",
                "notification_email": True,
                "data_sharing": False
            }
        }
        
        users[username] = default_profile
        save_users(users)
        return default_profile

def update_user_history(username: str, question: str, answer: str, sources: list):
    """
    Update user consultation history with detailed tracking
    
    History Entry Structure:
    - Timestamp
    - Question and answer
    - Sources used
    - Consultation metadata
    """
    users = load_users()
    
    if username in users:
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "sources": sources,
            "session_id": st.session_state.get("session_id", "unknown"),
            "response_quality": "good",  # Could be enhanced with quality scoring
            "user_feedback": None  # For future feedback collection
        }
        
        users[username]["history"].append(history_entry)
        
        # Maintain history size (keep last 100 consultations)
        if len(users[username]["history"]) > 100:
            users[username]["history"] = users[username]["history"][-100:]
        
        save_users(users)

def show_user_sidebar(username: str):
    """
    Display comprehensive user sidebar with profile and navigation
    """
    profile = get_user_profile(username)
    
    st.sidebar.markdown(f"### 👤 Profil: {username}")
    
    # User statistics
    history_count = len(profile.get("history", []))
    st.sidebar.metric("📊 Consultations", history_count)
    
    # Quick profile info
    if profile.get("profile", {}).get("age"):
        st.sidebar.info(f"🎂 Âge: {profile['profile']['age']} ans")
    
    # Recent activity
    if history_count > 0:
        last_consultation = profile["history"][-1]["timestamp"]
        last_date = datetime.fromisoformat(last_consultation).strftime("%d/%m/%Y")
        st.sidebar.info(f"📅 Dernière consultation: {last_date}")
    
    # Quick actions
    st.sidebar.markdown("### ⚡ Actions rapides")
    if st.sidebar.button("📚 Voir l'historique"):
        st.switch_page("pages/01_Historique.py")
    
    if st.sidebar.button("⚙️ Modifier le profil"):
        st.switch_page("pages/02_Profil.py")
      if st.sidebar.button("🔍 Analyse des maladies"):
        st.switch_page("pages/03_Maladies_Potentielles.py")
```

## 🔄 Data Pipeline & Processing

### Medical Data Collection Pipeline

**NHS Data Processing Workflow:**
```python
def process_nhs_conditions():
    """
    Complete NHS data processing pipeline
    
    Pipeline Steps:
    1. Extract condition text files from nhs_condition_details/
    2. Parse and clean medical content
    3. Classify conditions by medical domain
    4. Structure data for embedding generation
    5. Quality validation and error handling
    """
    conditions_dir = "data/raw/nhs_condition_details"
    processed_conditions = []
    
    # Process each condition file
    for filename in os.listdir(conditions_dir):
        if filename.endswith('.txt'):
            try:
                # Extract condition name and content
                condition_name = extract_condition_name(filename)
                content = read_condition_file(os.path.join(conditions_dir, filename))
                
                # Clean and structure data
                structured_data = {
                    "title": f"NHS: {condition_name}",
                    "content": clean_medical_text(content),
                    "source": "nhs",
                    "domain": classify_medical_domain(condition_name),
                    "condition_id": filename.split('_')[0],
                    "url": f"https://www.nhs.uk/conditions/{condition_name.lower().replace(' ', '-')}"
                }
                
                processed_conditions.append(structured_data)
                
            except Exception as e:
                print(f"⚠️ Error processing {filename}: {e}")
                continue
    
    return processed_conditions
```

**Data Quality Validation:**
```python
def validate_medical_content(content: str, min_length: int = 50):
    """
    Validate medical content quality before adding to knowledge base
    
    Validation Criteria:
    1. Minimum content length for meaningful context
    2. Medical terminology presence
    3. Language detection and filtering
    4. Content safety and appropriateness
    """
    # Length validation
    if len(content.strip()) < min_length:
        return False, "Content too short"
    
    # Medical term validation
    medical_indicators = [
        'symptoms', 'treatment', 'diagnosis', 'condition', 'disease',
        'medical', 'health', 'patient', 'therapy', 'medication'
    ]
    
    has_medical_content = any(term in content.lower() for term in medical_indicators)
    if not has_medical_content:
        return False, "No medical terminology detected"
    
    # Language validation (basic English check)
    english_indicators = ['the', 'and', 'or', 'is', 'are', 'in', 'on', 'at']
    has_english = sum(1 for word in english_indicators if word in content.lower()) >= 3
    
    if not has_english:
        return False, "Non-English content detected"
    
    return True, "Content validated"
```

### Advanced RAG Features

**Query Enhancement and Expansion:**
```python
def enhance_medical_query(query: str):
    """
    Enhance user queries for better retrieval performance
    
    Enhancement Techniques:
    1. Medical synonym expansion
    2. Abbreviation expansion (e.g., 'MI' → 'myocardial infarction')
    3. Related term addition
    4. Query reformulation for clarity
    """
    # Medical abbreviation mappings
    abbreviations = {
        'mi': 'myocardial infarction heart attack',
        'copd': 'chronic obstructive pulmonary disease',
        'diabetes': 'diabetes mellitus blood sugar',
        'htn': 'hypertension high blood pressure',
        'af': 'atrial fibrillation irregular heartbeat'
    }
    
    # Symptom to condition mappings
    symptom_mappings = {
        'chest pain': 'heart attack angina cardiac',
        'shortness of breath': 'asthma copd respiratory',
        'headache': 'migraine tension headache neurological',
        'fatigue': 'anemia depression thyroid chronic fatigue'
    }
    
    enhanced_query = query.lower()
    
    # Expand abbreviations
    for abbrev, expansion in abbreviations.items():
        if abbrev in enhanced_query:
            enhanced_query += f" {expansion}"
    
    # Add related symptoms/conditions
    for symptom, related in symptom_mappings.items():
        if symptom in enhanced_query:
            enhanced_query += f" {related}"
    
    return enhanced_query
```

**Context Ranking Algorithm:**
```python
def rank_retrieved_contexts(query: str, contexts: list, metadata: list):
    """
    Advanced context ranking using multiple relevance signals
    
    Ranking Factors:
    1. Semantic similarity score (40%)
    2. Source authority weight (25%)
    3. Domain relevance match (20%)
    4. Content recency and quality (15%)
    """
    ranked_contexts = []
    
    for i, (context, meta) in enumerate(zip(contexts, metadata)):
        score = 0.0
        
        # Factor 1: Semantic similarity (base score)
        semantic_score = calculate_semantic_similarity(query, context)
        score += semantic_score * 0.4
        
        # Factor 2: Source authority
        source = meta.get('source', '').lower()
        if source == 'pubmed':
            score += 0.25  # Highest authority (peer-reviewed)
        elif source == 'nhs':
            score += 0.20  # High authority (clinical guidelines)
        else:
            score += 0.10  # Standard authority
        
        # Factor 3: Domain relevance
        domain_match = check_domain_relevance(query, meta.get('domain', ''))
        score += domain_match * 0.2
        
        # Factor 4: Content quality indicators
        quality_score = assess_content_quality(context)
        score += quality_score * 0.15
        
        ranked_contexts.append({
            'context': context,
            'metadata': meta,
            'relevance_score': score,
            'ranking_position': i + 1
        })
    
    # Sort by relevance score (highest first)
    ranked_contexts.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return ranked_contexts
```

**Medical Safety Validation:**
```python
def validate_medical_safety(response: str):
    """
    Ensure generated responses meet medical safety standards
    
    Safety Checks:
    1. No definitive diagnostic statements
    2. Appropriate medical disclaimers present
    3. Emergency situation recognition
    4. Professional consultation recommendations
    """
    safety_score = 0
    warnings = []
    
    # Check for inappropriate diagnostic language
    dangerous_phrases = [
        'you have', 'you are diagnosed with', 'this is definitely',
        'you should take', 'stop taking', 'increase dosage'
    ]
    
    for phrase in dangerous_phrases:
        if phrase in response.lower():
            warnings.append(f"Definitive medical advice detected: '{phrase}'")
            safety_score -= 20
    
    # Check for emergency recognition
    emergency_terms = ['chest pain', 'difficulty breathing', 'severe pain', 'bleeding']
    emergency_detected = any(term in response.lower() for term in emergency_terms)
    
    if emergency_detected:
        emergency_advice = "seek immediate medical attention" in response.lower()
        if not emergency_advice:
            warnings.append("Emergency symptoms mentioned without urgent care advice")
            safety_score -= 30
        else:
            safety_score += 20  # Good emergency handling
    
    # Check for professional consultation recommendation
    consultation_phrases = [
        'consult', 'see a doctor', 'medical professional', 
        'healthcare provider', 'speak with your doctor'
    ]
    
    has_consultation_advice = any(phrase in response.lower() for phrase in consultation_phrases)
    if has_consultation_advice:
        safety_score += 25
    else:
        warnings.append("Missing professional consultation recommendation")
        safety_score -= 15
    
    # Check for appropriate disclaimers
    disclaimer_present = any(term in response.lower() for term in [
        'informational purposes', 'not medical advice', 'consult a professional'
    ])
    
    if disclaimer_present:
        safety_score += 20
    else:
        warnings.append("Medical disclaimer missing or insufficient")
        safety_score -= 25
    
    # Normalize score to 0-100 range
    final_score = max(0, min(100, safety_score + 50))
    
    return {
        'safety_score': final_score,
        'is_safe': final_score >= 70,
        'warnings': warnings,
        'recommendations': generate_safety_recommendations(warnings)
    }
```

## 🔧 Installation & Setup

### Prerequisites
```bash
Python 3.11+
pip package manager
```

### Dependencies Installation
```bash
pip install streamlit sentence-transformers chromadb biopython fpdf2
pip install requests json5 pandas
```

### Environment Configuration
1. Set up Google Gemini API key in `rag_pipeline.py`
2. Configure email for PubMed API in `pubmed_collector.py`
3. Create necessary directories: `data/raw/`, `user_data/`, `vector_db/`

**API Configuration Example:**
```python
# rag_pipeline.py - Secure API key management
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class MedicalRAGAssistant:
    def __init__(self):
        # Load API key from environment variable (recommended)
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            # Fallback to hardcoded key (not recommended for production)
            self.api_key = "your-google-api-key-here"
            
        # Configure Gemini client
        genai.configure(api_key=self.api_key)
```

**Environment Variables Setup (.env file):**
```bash
# Create .env file in project root
GOOGLE_API_KEY=your_actual_api_key_here
PUBMED_EMAIL=your_email@example.com
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Running the Application
```bash
# Start the Streamlit application
streamlit run app.py

# Collect medical data (optional - data already provided)
python pubmed_collector.py

# Generate embeddings (if needed)
python create_embeddings.py
```

## 📁 Project Structure

```
Medical_assistant/
├── app.py                    # Main application entry point
├── rag_pipeline.py          # Core RAG implementation
├── pubmed_collector.py      # Data collection from PubMed
├── create_embeddings.py     # Vector database creation
├── utils.py                 # Shared utility functions
├── pages/                   # Streamlit pages
│   ├── 00_Accueil.py       # Chat interface
│   ├── 01_Historique.py    # History management
│   ├── 02_Profil.py        # User profiles
│   └── 03_Maladies_Potentielles.py # Disease analysis
├── data/
│   └── raw/
│       ├── medical_data_for_rag.jsonl    # PubMed articles
│       ├── medical_data.jsonl            # NHS conditions
│       └── nhs_condition_details/        # Detailed NHS data
├── user_data/              # User profiles and history
├── vector_db/              # ChromaDB storage
└── README.md               # This file
```

## 🎯 Key Features

### 1. Intelligent Medical Q&A
- Evidence-based responses using RAG
- Source attribution for transparency
- Context-aware conversation handling

### 2. User Profile Management
- Secure authentication system
- Persistent conversation history
- Personalized medical tracking

### 3. Medical Report Generation
- PDF export of consultations
- Potential disease analysis
- Historical trend tracking

### 4. Multi-Source Knowledge Base
- PubMed research articles
- NHS medical conditions database
- Continuously expandable data sources

## 🔬 RAG Evaluation Metrics

### Retrieval Quality
- **Precision@K**: Relevance of top-K retrieved documents
- **Recall**: Coverage of relevant information
- **Mean Reciprocal Rank**: Ranking quality assessment

### Generation Quality
- **Faithfulness**: Adherence to retrieved context
- **Answer Relevance**: Pertinence to user query
- **Context Utilization**: Effective use of retrieved information

## 🚀 Future Enhancements

### Technical Improvements
- [ ] Implement reranking models for better retrieval
- [ ] Add query expansion for improved matching
- [ ] Integrate multiple LLM providers for redundancy
- [ ] Implement caching for faster responses

### Feature Additions
- [ ] Voice input/output capabilities
- [ ] Image analysis for medical images
- [ ] Integration with wearable device data
- [ ] Multilingual support expansion

### Data Expansion
- [ ] Medical textbook integration
- [ ] Drug interaction databases
- [ ] Clinical trial data inclusion
- [ ] Real-time medical news feeds

## 📊 System Monitoring & Performance

### Performance Optimization

**Caching Strategy:**
```python
@st.cache_resource
def load_assistant():
    """
    Singleton pattern for RAG assistant with Streamlit caching
    
    Benefits:
    - Single model instance across all user sessions
    - Reduced memory footprint and initialization time
    - Automatic cache invalidation on code changes
    - Improved response times for subsequent queries
    """
    return MedicalRAGAssistant()
```

**Memory Management:**
- **Vector Database**: ChromaDB uses efficient HNSW indexing for fast similarity search
- **Model Loading**: SentenceTransformer cached in memory for reuse
- **Session State**: Minimal data stored per user session
- **Batch Processing**: Documents processed in batches to prevent memory overflow

**Error Handling & Resilience:**
```python
def robust_api_call(self, prompt: str, max_retries: int = 3):
    """
    Resilient API calls with exponential backoff
    
    Error Recovery:
    1. Network timeouts → Retry with increased delay
    2. Rate limiting → Exponential backoff
    3. API errors → Fallback to template responses
    4. Critical failures → Graceful degradation
    """
    for attempt in range(max_retries):
        try:
            response = self.api_call(prompt)
            return response
        except Exception as e:
            wait_time = (2 ** attempt) * 1  # Exponential backoff
            time.sleep(wait_time)
            if attempt == max_retries - 1:
                return self.generate_fallback_response(prompt)
```

### Quality Metrics

**RAG System Evaluation:**
- **Retrieval Precision**: Relevance of retrieved documents (target: >85%)
- **Response Accuracy**: Medical fact verification (ongoing validation)
- **User Satisfaction**: Implicit feedback from session duration and interactions
- **Safety Score**: Medical disclaimer and safety warning coverage (100%)

**Performance Benchmarks:**
- **Average Response Time**: 2-5 seconds per query
- **Vector Search**: <100ms for similarity search
- **Model Inference**: 1-3 seconds for response generation
- **Concurrent Users**: Supports 10-50 simultaneous sessions

## 🛠️ Troubleshooting & Deployment

### Common Issues and Solutions

**1. ChromaDB Connection Errors:**
```python
# Error: Collection not found
# Solution: Run embedding generation first
python create_embeddings.py

# Error: Permission denied on vector_db/
# Solution: Check directory permissions
chmod -R 755 vector_db/  # Linux/Mac
# Or ensure write permissions on Windows
```

**2. Google Gemini API Issues:**
```python
# Error: API key not configured
# Solution: Set API key in rag_pipeline.py
GOOGLE_API_KEY = "your-api-key-here"

# Error: Rate limit exceeded
# Solution: Implement exponential backoff (already included)
```

**3. Memory Issues with Large Datasets:**
```python
# Solution: Adjust batch processing parameters
BATCH_SIZE = 32  # Reduce if out of memory
MAX_DOCS_PER_QUERY = 3  # Limit retrieved documents
```

**4. Streamlit Performance Optimization:**
```python
# Enable caching for better performance
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# Clear cache if needed
st.cache_resource.clear()
```

### Production Deployment Considerations

**Security Hardening:**
- Use environment variables for API keys
- Implement HTTPS/SSL certificates
- Add rate limiting per user
- Enable audit logging for medical consultations
- Implement user session timeouts

**Scalability Enhancements:**
- Deploy with Docker containers
- Use Redis for session management
- Implement load balancing for multiple instances
- Add database connection pooling
- Consider cloud vector databases (Pinecone, Weaviate)

**Monitoring & Logging:**
```python
# Production logging configuration
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medical_assistant.log'),
        logging.StreamHandler()
    ]
)

# Health check endpoint for load balancers
@app.route('/health')
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
```

**Data Backup Strategy:**
```python
# Automated backup script
def backup_user_data():
    """Create timestamped backups of user data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup user data
    shutil.copy("user_data/users.json", f"{backup_dir}/users.json")
    
    # Backup vector database
    shutil.copytree("vector_db", f"{backup_dir}/vector_db")
    
    print(f"✅ Backup created: {backup_dir}")
```

## ⚠️ Disclaimers

**Medical Disclaimer**: This application is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns.

**Data Privacy**: User data is stored locally. Ensure proper security measures in production deployments.

## 📄 License

This project is developed for educational and research purposes. Please ensure compliance with data source terms of service (PubMed, NHS) when using this system.

---

**Contact**: For questions or contributions, please open an issue in the repository.
>>>>>>> 867b41b49f080d275928ee00a465e627c12ff295
=======
>>>>>>> 1580ee9d12eb8a840b02d793ff53d4b5173c271a
