from pathlib import Path
from bs4 import BeautifulSoup
import json

root = Path("../Data/html")

records = []

# Read only chronology pages inside templates
html_files = list(root.rglob("templates/**/*.html"))

print(f"Found {len(html_files)} chronology pages")

for file in html_files:

    try:

        with open(file, encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")

        title = ""

        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

        headings = [
            h.get_text(" ", strip=True)
            for h in soup.find_all("h3")
        ]

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in soup.find_all("p")
        ]

        records.append({
            "source": str(file),
            "title": title,
            "headings": headings,
            "paragraphs": paragraphs
        })

    except Exception as e:
        print(file)
        print(e)

with open("../Output/chronology.json","w",encoding="utf8") as f:
    json.dump(records,f,indent=4,ensure_ascii=False)

print("Done")
print("Records:",len(records))