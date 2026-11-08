import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://streamxhd.sbs/"
OUTPUT_FILE = "disney_events.json"

def scrape_disney_events():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/159.0.0.0 Safari/537.36",
        "Referer": "https://streamxhd.sbs/"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        events = []

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'disney' in href.lower() or 'stream=disney' in href.lower():
                text = a_tag.get_text(strip=True)

                if href.startswith('/'):
                    stream_url = "https://streamxhd.sbs" + href
                elif not href.startswith('http'):
                    stream_url = "https://streamxhd.sbs/" + href
                else:
                    stream_url = href

                event_item = {
                    "name": text if text else "Evento Disney",
                    "info": "En Vivo",
                    "CH-events": "no",
                    "NSFW": "NO",
                    "status": "true",
                    "url": stream_url,
                    "type": "CLEARKEY",
                    "icono": "https://raw.githubusercontent.com/NovaplayGO/novaimg/main/icons/564.webp",
                    "evento": "yes"
                }

                if event_item not in events:
                    events.append(event_item)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

        print(f"[EXITO] Se encontraron {len(events)} eventos de Disney guardados en {OUTPUT_FILE}")

    except Exception as e:
        print(f"[ERROR] Fallo al raspar streamxhd.sbs: {e}")

if __name__ == "__main__":
    scrape_disney_events()
