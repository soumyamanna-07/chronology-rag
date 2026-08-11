import ladybug as lb

DB_PATH = "Data/chronology.lbdb"

print("Opening LadybugDB...")

db = lb.Database(DB_PATH)
conn = lb.Connection(db)

print("LadybugDB connected successfully!")

print("\nChecking database tables...\n")

queries = [
    "CALL show_tables() RETURN *",
    "MATCH (e:Event) RETURN e.event_id, e.month, e.date LIMIT 5"
]

for query in queries:
    print("\nQuery:")
    print(query)
    print("-" * 60)

    try:
        result = conn.execute(query)

        for row in result:
            print(row)

    except Exception as e:
        print("Query failed:")
        print(e)