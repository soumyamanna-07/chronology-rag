import json
import os
import ladybug as lb

DB_PATH = "Data/chronology.lbdb"
EVENTS_PATH = "Output/events.json"

print("Loading events...")

with open(EVENTS_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

print("Events loaded:", len(events))

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
print("Creating LadybugDB database...")

db = lb.Database(DB_PATH)
conn = lb.Connection(db)

conn.execute("""
CREATE NODE TABLE Event(
    event_id INT64 PRIMARY KEY,
    month STRING,
    date STRING,
    text STRING
)
""")

print("Event table created.")

query = """
CREATE (e:Event {
    event_id: $event_id,
    month: $month,
    date: $date,
    text: $text
})
"""

prepared_stmt = conn.prepare(query)

for i, event in enumerate(events):
    params = {
        "event_id": i,
        "month": str(event.get("month", "")),
        "date": str(event.get("date", "")),
        "text": str(event.get("text", ""))
    }

    conn.execute(prepared_stmt, params)

    if (i + 1) % 1000 == 0:
        print("Inserted:", i + 1)

print("\nLadybugDB database created successfully!")

result = conn.execute("MATCH (e:Event) RETURN count(e)")

for row in result:
    print("Events in database:", row)