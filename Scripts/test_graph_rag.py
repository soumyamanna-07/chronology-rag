import ladybug as lb

DB_PATH = "Data/chronology.lbdb"

print("Opening LadybugDB...")

# Open database
db = lb.Database(DB_PATH)

# Correct way to create connection
conn = lb.Connection(db)

print("LadybugDB connected successfully!")
print()

# --------------------------------------------------
# 1. Check Entity table
# --------------------------------------------------

print("1. Checking Entity table...")

result = conn.execute("""
MATCH (e:Entity)
RETURN e.id, e.type
LIMIT 10
""")

for row in result.get_all():
    print(row)

print()

# --------------------------------------------------
# 2. Find Swami Vivekananda
# --------------------------------------------------

print("2. Finding Swami Vivekananda...")

result = conn.execute("""
MATCH (e:Entity)
WHERE e.id = 'Swami Vivekananda'
RETURN e.id, e.type
""")

rows = result.get_all()

if rows:
    for row in rows:
        print("Found:", row)
else:
    print("Swami Vivekananda not found.")

print()

# --------------------------------------------------
# 3. Find America
# --------------------------------------------------

print("3. Finding America...")

result = conn.execute("""
MATCH (e:Entity)
WHERE e.id = 'America'
RETURN e.id, e.type
""")

rows = result.get_all()

if rows:
    for row in rows:
        print("Found:", row)
else:
    print("America not found.")

print()

# --------------------------------------------------
# 4. Find relationships from Swami Vivekananda
# --------------------------------------------------

print("4. Relationships from Swami Vivekananda...")

result = conn.execute("""
MATCH (a:Entity)-[r:RELATED]->(b:Entity)
WHERE a.id = 'Swami Vivekananda'
RETURN a.id, r.relation, b.id
LIMIT 30
""")

rows = result.get_all()

if rows:
    for row in rows:
        print(row)
else:
    print("No relationships found.")

print()

# --------------------------------------------------
# 5. Find EVENT nodes involving Swami Vivekananda
# --------------------------------------------------

print("5. Events involving Swami Vivekananda...")

result = conn.execute("""
MATCH (event:Entity)-[r:RELATED]->(person:Entity)
WHERE person.id = 'Swami Vivekananda'
AND r.relation = 'INVOLVES'
RETURN event.id, r.relation, person.id
LIMIT 20
""")

rows = result.get_all()

if rows:
    for row in rows:
        print(row)
else:
    print("No event relationships found.")

print()

# --------------------------------------------------
# 6. Find events involving America
# --------------------------------------------------

print("6. Events involving America...")

result = conn.execute("""
MATCH (event:Entity)-[r:RELATED]->(place:Entity)
WHERE place.id = 'America'
AND r.relation = 'INVOLVES'
RETURN event.id, r.relation, place.id
LIMIT 20
""")

rows = result.get_all()

if rows:
    for row in rows:
        print(row)
else:
    print("No America event relationships found.")

print()

print("=" * 60)
print("GRAPH TEST COMPLETED")
print("=" * 60)