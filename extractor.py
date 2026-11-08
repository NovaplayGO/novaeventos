import urllib.request
import json
from datetime import datetime, timezone, timedelta

URL = "https://streamxhd.sbs/eventos.json"
OUTPUT_FILE = "events.json"

def get_paraguay_today():
    py_tz = timezone(timedelta(hours=-3))
    return datetime.now(py_tz).date()

def parse_event_datetime(time_str):
    try:
        if "T" in time_str:
            dt = datetime.fromisoformat(time_str)
            py_tz = timezone(timedelta(hours=-3))
            dt_py = dt.astimezone(py_tz)
            return dt_py.replace(tzinfo=None), dt_py.strftime("%H:%M")
        elif " " in time_str:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            return dt, dt.strftime("%H:%M")
    except Exception:
        pass
    return datetime.max, "En Vivo"

def abbreviate_name(name, max_len=22):
    if not name or len(name) <= max_len:
        return name
    # Abreviaciones comunes para acortar nombres largos sin superar 22 caracteres
    shortened = (name
        .replace(" Fútbol Club", "")
        .replace(" Club de Fútbol", "")
        .replace(" de", "")
        .replace(" FC", "")
        .replace(" CF", "")
        .replace(" United", " Utd")
        .replace(" Athletic", " Ath")
        .replace(" Wandrerers", " Wand")
        .strip())

    if len(shortened) <= max_len:
        return shortened
    return shortened[:max_len].strip()

def extract_events():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/159.0.0.0 Safari/537.36",
        "Referer": "https://streamxhd.sbs/"
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sports = data.get("sports", [])
            raw_events = []

            today_py = get_paraguay_today()
            print(f"Filtrando eventos de fútbol de hoy (UTC-3): {today_py}")

            for sport in sports:
                sport_id = sport.get("id", "").lower()
                sport_name = sport.get("name", "").lower()

                if sport_id != "football" and "football" not in sport_name:
                    continue

                for league in sport.get("leagues", []):
                    league_name = league.get("name", "").strip()
                    for ev in league.get("events", []):
                        raw_title = ev.get("title", "Evento Deportivo")
                        title = abbreviate_name(raw_title, 22)

                        time_raw = ev.get("time", "")

                        dt_obj, info_time = parse_event_datetime(time_raw)

                        if dt_obj != datetime.max and dt_obj.date() != today_py:
                            continue

                        if league_name:
                            info_combined = f"{league_name} - {info_time}"
                        else:
                            info_combined = info_time

                        servers = ev.get("servers", [])
                        for srv in servers:
                            srv_name = srv.get("name", "")
                            srv_url = srv.get("url", "")

                            match_keyword = (
                                "disney" in srv_name.lower() or "disney" in srv_url.lower() or
                                "appletv" in srv_name.lower() or "appletv" in srv_url.lower() or
                                "apple" in srv_name.lower()
                            )

                            if match_keyword:
                                event_item = {
                                    "name": title,
                                    "info": info_combined,
                                    "CH-events": "no",
                                    "NSFW": "NO",
                                    "status": "true",
                                    "url": srv_url,
                                    "type": "CLEARKEY",
                                    "icono": "https://raw.githubusercontent.com/NovaplayGO/novaimg/main/icons/564.webp",
                                    "evento": "yes",
                                    "_dt": dt_obj
                                }

                                if event_item not in raw_events:
                                    raw_events.append(event_item)

            raw_events.sort(key=lambda x: x["_dt"])

            events_list = []
            for item in raw_events:
                clean_item = {k: v for k, v in item.items() if k != "_dt"}
                if clean_item not in events_list:
                    events_list.append(clean_item)

            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(events_list, f, indent=2, ensure_ascii=False)

            print(f"[EXITO] Se procesaron, abreviaron a máx 22 chars y guardaron {len(events_list)} eventos en {OUTPUT_FILE}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    extract_events()
