import urllib.request
import json
from datetime import datetime

URL = "https://streamxhd.sbs/eventos.json"
OUTPUT_FILE = "disney_events.json"

def parse_time(time_str):
    try:
        if "T" in time_str:
            dt = datetime.fromisoformat(time_str)
            return dt.strftime("%H:%M")
        elif " " in time_str:
            parts = time_str.split(" ")
            if len(parts) > 1:
                return parts[1][:5]
    except Exception:
        pass
    return "En Vivo"

def scrape_disney_events():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/159.0.0.0 Safari/537.36",
        "Referer": "https://streamxhd.sbs/"
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sports = data.get("sports", [])
            events_list = []

            for sport in sports:
                for league in sport.get("leagues", []):
                    for ev in league.get("events", []):
                        title = ev.get("title", "Evento Deportivo")
                        time_raw = ev.get("time", "")
                        info_time = parse_time(time_raw)

                        servers = ev.get("servers", [])
                        for srv in servers:
                            srv_name = srv.get("name", "")
                            srv_url = srv.get("url", "")

                            if "disney" in srv_name.lower() or "disney" in srv_url.lower():
                                event_item = {
                                    "name": title,
                                    "info": info_time,
                                    "CH-events": "no",
                                    "NSFW": "NO",
                                    "status": "true",
                                    "url": srv_url,
                                    "type": "CLEARKEY",
                                    "icono": "https://raw.githubusercontent.com/NovaplayGO/novaimg/main/icons/564.webp",
                                    "evento": "yes"
                                }

                                if event_item not in events_list:
                                    events_list.append(event_item)

            with open(OUTPUT_FILE, 'w', encoding='utf-8' ) as f:
                json.dump(events_list, f, indent=2, ensure_ascii=False)

            print(f"[EXITO] Se procesaron y guardaron {len(events_list)} eventos de Disney en {OUTPUT_FILE}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    scrape_disney_events()
