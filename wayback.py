import requests
import sys

domain = sys.argv[1]
print(f"[*] Menarik URL untuk: {domain}")

url = f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=txt&fl=original&collapse=urlkey"

try:
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        urls = set(response.text.splitlines())
        with open("urls.txt", "w") as f:
            for u in urls:
                if u:
                    f.write(u + "\n")
        print(f"[+] Berjaya! {len(urls)} URL disimpan dalam urls.txt")
    else:
        print(f"[!] Error HTTP: {response.status_code}")
except Exception as e:
    print(f"[!] Error: {e}")
