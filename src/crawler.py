import json
import time
from bs4 import BeautifulSoup
from langchain_community.document_loaders import WebBaseLoader

def main():
    url_base = "https://www.asianapoli.it/dove-lo-butto/"
    links_totali = set()
    pagina = 1
    
    print(f"🔍 Inizio la scansione partendo da: {url_base}")
    
    while True:
        # Generiamo l'URL esatto che hai scoperto ispezionando il codice!
        url_corrente = f"{url_base}?jsf=jet-engine:lista-rifiuti&pagenum={pagina}"
        print(f"\nScansiono la pagina {pagina}: {url_corrente}")
        
        try:
            loader = WebBaseLoader(web_paths=(url_corrente,))
            soup = loader.scrape()
            
            links_nella_pagina = set()
            
            # Cerca tutti i tag <a>
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Vogliamo solo i link che puntano ai singoli rifiuti.
                # Devono contenere "/dove-lo-butto/", ma non essere l'URL base 
                # e NON devono contenere i parametri di JetEngine.
                if "/dove-lo-butto/" in href and href != url_base and "?jsf=" not in href and "pagenum=" not in href:
                    links_nella_pagina.add(href)
            
            # Se la pagina è vuota di link utili, ci fermiamo
            if not links_nella_pagina:
                print("Nessun link utile trovato in questa pagina. Paginazione terminata.")
                break
                
            # JetEngine a volte ricomincia dalla pagina 1 se chiedi una pagina che non esiste.
            # Se tutti i link trovati erano già nel nostro set totale, significa che stiamo girando in tondo.
            if links_nella_pagina.issubset(links_totali):
                print("Il sito sta ripetendo i risultati. Paginazione terminata.")
                break
                
            # Aggiungiamo i nuovi link
            links_totali.update(links_nella_pagina)
            print(f"✅ Trovati {len(links_nella_pagina)} link in questa pagina. Totale accumulato: {len(links_totali)}")
            
            pagina += 1
            time.sleep(1.5) # Pausa di cortesia
            
        except Exception as e:
            print(f"Errore durante la scansione della pagina {pagina}: {e}")
            break

    lista_urls = list(links_totali)
    
    print("=" * 50)
    print(f"🎉 RICERCA COMPLETATA! Trovati in totale {len(lista_urls)} url unici di rifiuti.")
    print("=" * 50)
    
    with open('urls_da_scansionare.json', 'w', encoding='utf-8') as f:
        json.dump(lista_urls, f, indent=4)
        
    print("Il file 'urls_da_scansionare.json' è pronto per lo Script 2.")

if __name__ == "__main__":
    main()