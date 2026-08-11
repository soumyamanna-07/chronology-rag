import csv
import os
import ladybug as lb

DB_PATH = "Data/chronology.lbdb"
NODES_PATH = "Output/clean_graph_nodes.csv"
EDGES_PATH = "Output/clean_graph_edges.csv"
RELATIONSHIP_PATH = "Output/ladybug_relationships.csv"

print("Opening LadybugDB...")

db = lb.Database(DB_PATH)
conn = lb.Connection(db)

print("LadybugDB connected successfully!")

# ============================================================
# CLEAN OLD TABLES
# ============================================================

print("\nCleaning previous graph tables...")

try:
    conn.execute("DROP TABLE RELATED")
    print("Old RELATED table removed.")
except Exception:
    print("No old RELATED table found.")

try:
    conn.execute("DROP TABLE Entity")
    print("Old Entity table removed.")
except Exception:
    print("No old Entity table found.")

# ============================================================
# CREATE NODE TABLE
# ============================================================

print("\nCreating Entity table...")

conn.execute("""
CREATE NODE TABLE Entity(
    id STRING PRIMARY KEY,
    type STRING
)
""")

print("Entity table created.")

# ============================================================
# CREATE RELATIONSHIP TABLE
# ============================================================

print("\nCreating RELATED relationship table...")

conn.execute("""
CREATE REL TABLE RELATED(
    FROM Entity TO Entity,
    relation STRING
)
""")

print("RELATED relationship table created.")

# ============================================================
# LOAD NODES
# ============================================================

print("\nLoading clean graph nodes...")

with open(NODES_PATH, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)

    header = next(reader)

    nodes = list(reader)

print("Nodes loaded:", len(nodes))

# ============================================================
# CREATE TEMPORARY NODE CSV WITHOUT HEADER
# ============================================================

print("\nPreparing node data...")

node_csv_path = "Output/ladybug_nodes.csv"

with open(node_csv_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)

    for row in nodes:
        writer.writerow(row)

# ============================================================
# BULK IMPORT NODES
# ============================================================

print("\nImporting nodes into LadybugDB...")

conn.execute(
    f"COPY Entity FROM '{node_csv_path}'"
)

print("Nodes imported successfully!")

# ============================================================
# LOAD EDGES
# ============================================================

print("\nLoading clean graph edges...")

with open(EDGES_PATH, "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)

    header = next(reader)

    edges = list(reader)

print("Edges loaded:", len(edges))

# ============================================================
# CREATE LADYBUG RELATIONSHIP CSV
#
# Ladybug expects:
#
# FROM
# TO
# relationship properties...
#
# ============================================================

print("\nPreparing relationship data...")

with open(
    RELATIONSHIP_PATH,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.writer(f)

    for row in edges:

        source = row[0]
        relation = row[1]
        target = row[2]

        writer.writerow([
            source,
            target,
            relation
        ])

print("Relationship CSV created.")

# ============================================================
# BULK IMPORT RELATIONSHIPS
# ============================================================

print("\nImporting relationships into LadybugDB...")

result = conn.execute(
    f"COPY RELATED FROM '{RELATIONSHIP_PATH}'"
)

print("Relationships imported successfully!")

# ============================================================
# VERIFY NODE COUNT
# ============================================================

print("\n" + "=" * 60)
print("GRAPH IMPORT VERIFICATION")
print("=" * 60)

print("\nChecking Entity count...")

result = conn.execute("""
MATCH (e:Entity)
RETURN count(e)
""")

for row in result:
    print("Entities in database:", row)

# ============================================================
# VERIFY RELATIONSHIP COUNT
# ============================================================

print("\nChecking relationship count...")

result = conn.execute("""
MATCH ()-[r:RELATED]->()
RETURN count(r)
""")

for row in result:
    print("Relationships in database:", row)

# ============================================================
# TEST SWAMI VIVEKANANDA -> AMERICA
# ============================================================

print("\nTesting Swami Vivekananda -> America relationship...")

result = conn.execute("""
MATCH (a:Entity)-[r:RELATED]->(b:Entity)
WHERE a.id = 'Swami Vivekananda'
AND b.id = 'America'
RETURN a.id, r.relation, b.id
""")

found = False

for row in result:
    print("FOUND:", row)
    found = True

if not found:
    print("Direct Swami Vivekananda -> America relationship not found.")

# ============================================================
# SHOW SAMPLE RELATIONSHIPS
# ============================================================

print("\nShowing sample relationships of Swami Vivekananda...")

result = conn.execute("""
MATCH (a:Entity)-[r:RELATED]->(b:Entity)
WHERE a.id = 'Swami Vivekananda'
RETURN a.id, r.relation, b.id
LIMIT 20
""")

sample_found = False

for row in result:
    print(row)
    sample_found = True

if not sample_found:
    print("No relationships found.")

# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 60)
print("GRAPH IMPORT COMPLETED")
print("=" * 60)

print("All graph data has been imported using LadybugDB COPY.")

print("\nNext step:")
print("Build the Graph RAG search.")