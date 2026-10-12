import json
import os
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
load_dotenv()

# 1. IMPOSTA LA TUA API KEY DI GOOGLE
# Puoi ottenere la chiave da: https://aistudio.google.com/
#os.environ["GOOGLE_API_KEY"] = "INSERISCI_QUI_LA_TUA_API_KEY_GEMINI"

# 2. CARICA I DATI DAL JSON
nome_file = "dati_rifiuti.json"
try:
    with open(nome_file, 'r', encoding='utf-8') as f:
        database_json = json.load(f)
except FileNotFoundError:
    print(f"Errore: Il file {nome_file} non esiste. Esegui prima lo script di scraping.")
    exit()

# 3. PREPARA I DOCUMENTI (Testo + Metadati)
documenti_per_vettoriale = []

for item in database_json:
    # Ripuliamo il nome del rifiuto
    nome_rifiuto = item['rifiuto'].replace("Dove buttare ", "").replace("?", "").strip()
    
    # page_content: Il testo che verrà vettorializzato da Gemini
    contenuto_ricerca = f"Categoria rifiuto: {nome_rifiuto}. Sinonimi: vestiti, indumenti, magliette, pantaloni, scarpe, abbigliamento."
    
    # metadata: I dati strutturati (che non vengono vettorializzati ma restituiti dal DB)
    metadati = {
        "rifiuto_esatto": nome_rifiuto,
        "url_fonte": item.get('url_fonte', ''),
        "info_conferimento_json": json.dumps(item['luoghi_conferimento'], ensure_ascii=False)
    }
    
    doc = Document(page_content=contenuto_ricerca, metadata=metadati)
    documenti_per_vettoriale.append(doc)

# 4. INIZIALIZZA GLI EMBEDDING DI GEMINI
# Usiamo il modello text-embedding-004, che è l'attuale standard di Google per la ricerca semantica
embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

# 5. CREA E SALVA IL DATABASE QDRANT
print("Generazione degli embedding e salvataggio su Qdrant in corso...")

qdrant_db = QdrantVectorStore.from_documents(
    documents=documenti_per_vettoriale,
    embedding=embeddings,
    path="./qdrant_db_rifiuti",  # Qdrant salverà i dati in questa cartella locale
    collection_name="rifiuti_asia_napoli"
)

print(f"✅ Database vettoriale salvato con successo! ({len(documenti_per_vettoriale)} documenti inseriti)\n")
print("-" * 50)

# ==========================================
# 6. TEST: VERIFICHIAMO SE FUNZIONA LA RICERCA
# ==========================================
print("TEST DI RICERCA SEMANTICA:")

# Simuliamo l'output di un modello Vision dopo che l'utente ha caricato una foto
query_di_ricerca = "Ho una vecchia maglietta bucata"
print(f"Query in ingresso: '{query_di_ricerca}'\n")

# Chiediamo a Qdrant di trovare il documento più simile (k=1)
risultati = qdrant_db.similarity_search(query_di_ricerca, k=1)

if risultati:
    documento_trovato = risultati[0]
    
    # Estraiamo i metadati
    nome_rifiuto = documento_trovato.metadata["rifiuto_esatto"]
    luoghi_json = json.loads(documento_trovato.metadata["info_conferimento_json"])
    
    print(f"🎯 Corrispondenza trovata: {nome_rifiuto}")
    print("📍 Istruzioni recuperate:")
    
    for luogo in luoghi_json:
        print(f"  - {luogo['nome']}: {luogo['istruzioni']}")
else:
    print("Nessuna corrispondenza trovata.")