import os
import json
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

def main():
    # Carica le variabili d'ambiente dal file .env
    load_dotenv()
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Errore: GOOGLE_API_KEY non trovata. Controlla il tuo file .env")
        return

    try:
        with open('dati_rifiuti.json', 'r', encoding='utf-8') as f:
            database_json = json.load(f)
    except FileNotFoundError:
        print("Errore: Esegui prima 2_scraper.py")
        return

    documenti_per_vettoriale = []
    
    for item in database_json:
        contenuto_ricerca = f"Categoria rifiuto: {item['rifiuto_esatto']}."
        metadati = {
            "rifiuto_esatto": item["rifiuto_esatto"],
            "url_fonte": item["url_fonte"],
            "info_conferimento_json": json.dumps(item["luoghi"], ensure_ascii=False)
        }
        
        doc = Document(page_content=contenuto_ricerca, metadata=metadati)
        documenti_per_vettoriale.append(doc)

    print("🧠 Generazione embedding e salvataggio su Qdrant in corso...")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    qdrant_db = QdrantVectorStore.from_documents(
        documents=documenti_per_vettoriale,
        embedding=embeddings,
        path="./qdrant_db_rifiuti", 
        collection_name="rifiuti_asia_napoli"
    )
    
    print(f"✅ Database Qdrant pronto! Inseriti {len(documenti_per_vettoriale)} documenti.\n")
    
    # Test di Ricerca
    query_di_ricerca = "Ho una maglietta strappata"
    print(f"TEST RICERCA: '{query_di_ricerca}'")
    
    risultati = qdrant_db.similarity_search(query_di_ricerca, k=1)
    
    if risultati:
        doc_trovato = risultati[0]
        nome = doc_trovato.metadata["rifiuto_esatto"]
        luoghi = json.loads(doc_trovato.metadata["info_conferimento_json"])
        
        print(f"🎯 Trovato: {nome}")
        for luogo in luoghi:
            print(f"  - {luogo['nome']}: {luogo['istruzioni']}")
    else:
        print("Nessuna corrispondenza trovata.")

if __name__ == "__main__":
    main()