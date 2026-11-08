import urllib.request
import json
from datetime import datetime, timezone, timedelta

URL = "https://streamxhd.sbs/eventos.json"
OUTPUT_FILE = "events.json"

def get_paraguay_today():
    # Paraguay time: UTC-3
    py_tz = timezone(timedelta(hours=-3))
    return datetime.now(py_tz).date()

def parse_event_date_and_time(time_str):
    try:
        if "T" in time_str:
            dt = datetime.fromisoformat(time_str)
            py_tz = timezone(timedelta(hours=-3))
            dt_py = dt.astimezone(py_tz)
            return dt_py.date(), dt_py.strftime("%H:%M")
        elif " " in time_str:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            return dt.date(), dt.strftime("%H:%M")
    except Exception:
        pass
    return None, "En Vivo"

def extract_events():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/159.0.0.0 Safari/537.36",
        "Referer": "https://streamxhd.sbs/"
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sports = data.get("sports", [])
            events_list = []

            today_py = get_paraguay_today()
            print(f"Filtrando eventos para hoy en Paraguay (UTC-3): {today_py}")

            for sport in sports:
                for league in sport.get("leagues", []):
                    for ev in league.get("events", []):
                        title = ev.get("title", "Evento Deportivo")
                        time_raw = ev.get("time", "")

                        ev_date, info_time = parse_event_date_and_time(time_raw)

                        # Filtrar solo eventos del día actual en Paraguay
                        if ev_date and ev_date != today_py:
                            continue

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

            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(events_list, f, indent=2, ensure_ascii=False)

            print(f"[EXITO] Se procesaron y guardaron {len(events_list)} eventos de hoy en {OUTPUT_FILE}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    extract_events()
