import csv
import ladybug as lb

DB_PATH = "Data/chronology.lbdb"
NODES_PATH = "Output/graph_nodes.csv"
EDGES_PATH = "Output/graph_edges.csv"

print("Opening LadybugDB...")

db = lb.Database(DB_PATH)
conn = lb.Connection(db)

print("LadybugDB connected successfully!")

# --------------------------------------------------
# Remove previous partial graph import
# --------------------------------------------------

print("\nCleaning previous graph import...")

try:
    conn.execute("DROP TABLE RELATED")
    print("Old RELATED table removed.")
except Exception:
    pass

try:
    conn.execute("DROP TABLE Entity")
    print("Old Entity table removed.")
except Exception:
    pass

# --------------------------------------------------
# Create Entity table
# --------------------------------------------------

print("\nCreating Entity table...")

conn.execute("""
CREATE NODE TABLE Entity(
    id STRING PRIMARY KEY,
    type STRING
)
""")

print("Entity table created.")

# --------------------------------------------------
# Create relationship table
# --------------------------------------------------

print("\nCreating graph relationship table...")

conn.execute("""
CREATE REL TABLE RELATED(
    FROM Entity TO Entity,
    relation STRING
)
""")

print("RELATED relationship table created.")

# --------------------------------------------------
# Load nodes
# --------------------------------------------------

print("\nLoading graph nodes...")

nodes = []

with open(NODES_PATH, "r", encoding="utf-8", newline="") as f:

    reader = csv.DictReader(f)

    for row in reader:
        nodes.append(row)

print("Nodes loaded:", len(nodes))

# --------------------------------------------------
# Insert nodes using parameters
# --------------------------------------------------

print("\nInserting graph nodes...")

node_query = """
CREATE (:Entity {
    id: $id,
    type: $type
})
"""

inserted_nodes = 0

for node in nodes:

    parameters = {
        "id": node["id"],
        "type": node["type"]
    }

    try:

        conn.execute(node_query, parameters)

        inserted_nodes += 1

    except Exception as e:

        print("\nNode insertion error:")
        print(e)
        print("Node:", node["id"])
        break

    if inserted_nodes % 5000 == 0:
        print("Inserted nodes:", inserted_nodes)

print("Total nodes inserted:", inserted_nodes)

# --------------------------------------------------
# Load edges
# --------------------------------------------------

print("\nLoading graph edges...")

edges = []

with open(EDGES_PATH, "r", encoding="utf-8", newline="") as f:

    reader = csv.DictReader(f)

    for row in reader:
        edges.append(row)

print("Edges loaded:", len(edges))

# --------------------------------------------------
# Insert edges using parameters
# --------------------------------------------------

print("\nInserting graph edges...")

edge_query = """
MATCH (a:Entity {id: $source})
MATCH (b:Entity {id: $target})
CREATE (a)-[:RELATED {relation: $relation}]->(b)
"""

inserted_edges = 0

for edge in edges:

    parameters = {
        "source": edge["source"],
        "target": edge["target"],
        "relation": edge["relation"]
    }

    try:

        conn.execute(edge_query, parameters)

        inserted_edges += 1

    except Exception as e:

        print("\nEdge insertion error:")
        print(e)

        print("Source:", edge["source"])
        print("Target:", edge["target"])
        print("Relation:", edge["relation"])

        break

    if inserted_edges % 5000 == 0:
        print("Inserted edges:", inserted_edges)

print("Total edges inserted:", inserted_edges)

# --------------------------------------------------
# Verification
# --------------------------------------------------

print("\n" + "=" * 60)
print("GRAPH IMPORT FINISHED")
print("=" * 60)

print("\nChecking Entity count...")

result = conn.execute("""
MATCH (e:Entity)
RETURN count(e)
""")

for row in result:
    print("Entities in database:", row)

print("\nChecking relationship count...")

result = conn.execute("""
MATCH ()-[r:RELATED]->()
RETURN count(r)
""")

for row in result:
    print("Relationships in database:", row)

# --------------------------------------------------
# Test Swami Vivekananda -> America
# --------------------------------------------------

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

print("\nGraph import test completed!")