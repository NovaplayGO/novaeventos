import urllib.request
import re

URL = "https://streamxhd.sbs/"

def inspect_links():
    req = urllib.request.Request(URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/159.0.0.0 Safari/537.36",
        "Referer": "https://streamxhd.sbs/"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
            links = re.findall(r'href=["\']([^"\']+)["\']', html)
            print("Total enlaces encontrados:", len(links))
            for l in links[:50]:
                if 'live' in l or 'stream' in l or '.php' in l:
                    print("Enlace relevante:", l)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    inspect_links()
