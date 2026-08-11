import json
import spacy

nlp = spacy.load("en_core_web_sm")

# -------- Custom Dictionaries --------

KNOWN_PEOPLE = [
    "Swami Vivekananda",
    "Swamiji",
    "Swami Abhedananda",
    "Swami Saradananda",
    "Swami Akhandananda",
    "Pavhari Baba",
    "Pramadadas Mitra",
    "Baburam",
    "Balaram Bose",
    "Sri Ramakrishna",
    "Holy Mother",
    "Raghunath Rao"
]

KNOWN_PLACES = [
    "Calcutta",
    "Kolkata",
    "Ghazipur",
    "Benares",
    "Varanasi",
    "Madras",
    "Chennai",
    "Almora",
    "Allahabad",
    "Khetri",
    "Jaipur",
    "Bombay",
    "Mumbai",
    "America",
    "Chicago",
    "New York",
    "London"
]

# -------------------------------------

with open("../Output/events.json", "r", encoding="utf-8") as f:
    events = json.load(f)

output = []

for event in events:

    text = event["text"]

    doc = nlp(text)

    people = set()
    places = set()
    organizations = set()
    dates = set()

    # spaCy entities
    for ent in doc.ents:

        if ent.label_ == "PERSON":
            people.add(ent.text)

        elif ent.label_ in ["GPE", "LOC"]:
            places.add(ent.text)

        elif ent.label_ == "ORG":
            organizations.add(ent.text)

        elif ent.label_ == "DATE":
            dates.add(ent.text)

    # Dictionary matching
    lower = text.lower()

    for person in KNOWN_PEOPLE:
        if person.lower() in lower:
            people.add(person)

    for place in KNOWN_PLACES:
        if place.lower() in lower:
            places.add(place)

    event["people"] = sorted(list(people))
    event["places"] = sorted(list(places))
    event["organizations"] = sorted(list(organizations))
    event["dates_found"] = sorted(list(dates))

    output.append(event)

with open("../Output/events_with_entities.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=4, ensure_ascii=False)

print("Finished!")
print("Processed", len(output), "events")