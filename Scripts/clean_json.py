import json
import re

# Load previous JSON
with open("../Output/chronology.json", "r", encoding="utf-8") as f:
    data = json.load(f)

events = []

# Matches: April 1, Tuesday / April 3-4, Thursday-Friday
date_pattern = re.compile(
    r'^(January|February|March|April|May|June|July|August|September|October|November|December).*',
    re.IGNORECASE
)

for month_record in data:

    title = month_record.get("title", "")
    source = month_record.get("source", "")
    paragraphs = month_record.get("paragraphs", [])

    current_date = ""

    for p in paragraphs:

        p = p.strip()

        if not p:
            continue

        if date_pattern.match(p):
            current_date = p
            continue

        events.append({
            "month": title,
            "date": current_date,
            "text": p,
            "source": source
        })

# Save cleaned events
with open("../Output/events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, indent=4, ensure_ascii=False)

print("Events created:", len(events))