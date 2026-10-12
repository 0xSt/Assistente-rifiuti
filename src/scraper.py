import json
import time
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader

def estrai_dati(url_rifiuto):
    loader = WebBaseLoader(web_paths=(url_rifiuto,))
    soup = loader.scrape()
    
    titolo_elemento = soup.find('h1')
    if not titolo_elemento:
        return None
        
    nome_rifiuto = titolo_elemento.text.strip().replace("Dove buttare ", "").replace("?", "").strip()
    
    dati = {
        "rifiuto_esatto": nome_rifiuto,
        "url_fonte": url_rifiuto,
        "luoghi": []
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
            
            dati["luoghi"].append({"nome": nome_luogo, "istruzioni": descrizione_luogo})
            
    return dati

def main():
    try:
        with open('urls_da_scansionare.json', 'r', encoding='utf-8') as f:
            lista_urls = json.load(f)
    except FileNotFoundError:
        print("Errore: Esegui prima 1_crawler.py")
        return
        
    dati_estratti = []
    print(f"⏳ Inizio lo scraping di {len(lista_urls)} pagine...")
    
    for idx, url in enumerate(lista_urls):
        print(f"[{idx+1}/{len(lista_urls)}] Estrazione da: {url}")
        dati = estrai_dati(url)
        
        if dati and len(dati["luoghi"]) > 0:
            dati_estratti.append(dati)
            
        time.sleep(1.5) # Pausa obbligatoria anti-ban
        
    with open('dati_rifiuti.json', 'w', encoding='utf-8') as f:
        json.dump(dati_estratti, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Scraping completato. Salvati {len(dati_estratti)} rifiuti in 'dati_rifiuti.json'.")

if __name__ == "__main__":
    main()