from langchain_community.document_loaders import WebBaseLoader
import json
import os

# 1. Inizializziamo il loader
url = "https://www.asianapoli.it/dove-lo-butto/antenna/"
loader = WebBaseLoader(web_paths=(url,))
soup = loader.scrape()

# 2. Estrazione dati (come prima)
dati_rifiuto = {
    "rifiuto": soup.find('h1').text.strip() if soup.find('h1') else "Titolo non trovato",
    "url_fonte": url, # AGGIUNTO: Utilissimo come metadato per citare le fonti nel RAG!
    "luoghi_conferimento": []
}

classe_padre = "elementor-element-4041ea3" 
classe_contenuto = "jet-listing-dynamic-field__content"
contenitori = soup.find_all(class_=classe_padre)

for contenitore in contenitori:
    campi_testo = contenitore.find_all(class_=classe_contenuto)
    if len(campi_testo) > 0:
        nome_luogo = campi_testo[0].text.strip()
        descrizione_luogo = "Nessuna istruzione aggiuntiva."
        if len(campi_testo) > 1:
            testo_desc = campi_testo[1].text.strip()
            if testo_desc and "eventuale messaggio" not in testo_desc:
                descrizione_luogo = testo_desc
        
        dati_rifiuto["luoghi_conferimento"].append({
            "nome": nome_luogo,
            "istruzioni": descrizione_luogo
        })

# --- SALVATAGGIO IN JSON ---
nome_file_json = "dati_rifiuti.json"

# Controlla se il file esiste già per aggiungere i nuovi dati a quelli vecchi, 
# invece di sovrascriverli (utile se farai un ciclo su tanti URL)
if os.path.exists(nome_file_json):
    with open(nome_file_json, 'r', encoding='utf-8') as file:
        try:
            database_esistente = json.load(file)
        except json.JSONDecodeError:
            database_esistente = []
else:
    database_esistente = []

# Aggiunge il nuovo rifiuto alla lista
database_esistente.append(dati_rifiuto)

# Salva il file
with open(nome_file_json, 'w', encoding='utf-8') as file:
    # indent=4 rende il file leggibile per gli umani
    # ensure_ascii=False permette di salvare correttamente lettere accentate (come la 'è')
    json.dump(database_esistente, file, indent=4, ensure_ascii=False)

print(f"✅ Dati salvati con successo in {nome_file_json}")