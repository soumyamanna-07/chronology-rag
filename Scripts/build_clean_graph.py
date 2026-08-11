import json
import csv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EVENTS_PATH = os.path.join(BASE_DIR, "Output", "events_with_entities.json")
NODES_PATH = os.path.join(BASE_DIR, "Output", "clean_graph_nodes.csv")
EDGES_PATH = os.path.join(BASE_DIR, "Output", "clean_graph_edges.csv")

print("Loading entity-enriched events...")

with open(EVENTS_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

print("Events loaded:", len(events))

nodes = {}
edges = []

# ============================================================
# CREATE EVENT NODES
# ============================================================

for i, event in enumerate(events):

    event_id = f"EVENT_{i}"

    nodes[event_id] = "Event"

    # -------------------------
    # Date
    # -------------------------

    date_value = event.get("date", "").strip()

    if date_value:
        nodes[date_value] = "Date"

        edges.append([
            event_id,
            "HAS_DATE",
            date_value
        ])

    # -------------------------
    # Month
    # -------------------------

    month_value = event.get("month", "").strip()

    if month_value:
        nodes[month_value] = "Month"

        edges.append([
            event_id,
            "HAS_MONTH",
            month_value
        ])

    # ========================================================
    # PEOPLE
    # ========================================================

    for person in event.get("people", []):

        person = str(person).strip()

        if not person:
            continue

        nodes[person] = "Person"

        edges.append([
            event_id,
            "INVOLVES",
            person
        ])

    # ========================================================
    # PLACES
    # ========================================================

    for place in event.get("places", []):

        place = str(place).strip()

        if not place:
            continue

        nodes[place] = "Place"

        edges.append([
            event_id,
            "INVOLVES",
            place
        ])

    # ========================================================
    # ORGANIZATIONS
    # ========================================================

    for org in event.get("organizations", []):

        org = str(org).strip()

        if not org:
            continue

        nodes[org] = "Organization"

        edges.append([
            event_id,
            "INVOLVES",
            org
        ])

    # ========================================================
    # DATES FOUND
    # ========================================================

    for found_date in event.get("dates_found", []):

        found_date = str(found_date).strip()

        if not found_date:
            continue

        nodes[found_date] = "Date"

        edges.append([
            event_id,
            "MENTIONS_DATE",
            found_date
        ])


# ============================================================
# REMOVE DUPLICATE EDGES
# ============================================================

unique_edges = []
seen_edges = set()

for edge in edges:

    key = tuple(edge)

    if key not in seen_edges:

        seen_edges.add(key)
        unique_edges.append(edge)

edges = unique_edges


# ============================================================
# SAVE NODES
# ============================================================

print("Saving clean graph nodes...")

with open(NODES_PATH, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(["id", "type"])

    for node_id, node_type in sorted(nodes.items()):

        writer.writerow([
            node_id,
            node_type
        ])


# ============================================================
# SAVE EDGES
# ============================================================

print("Saving clean graph edges...")

with open(EDGES_PATH, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "source",
        "relation",
        "target"
    ])

    for source, relation, target in edges:

        writer.writerow([
            source,
            relation,
            target
        ])


# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 60)
print("CLEAN KNOWLEDGE GRAPH CREATED")
print("=" * 60)

print("Events :", len(events))
print("Nodes  :", len(nodes))
print("Edges  :", len(edges))

event_nodes = [
    node for node, node_type in nodes.items()
    if node_type == "Event"
]

print("Event nodes :", len(event_nodes))

print()
print("Checking EVENT_10228...")

if "EVENT_10228" in nodes:
    print("SUCCESS: EVENT_10228 exists.")
else:
    print("ERROR: EVENT_10228 is missing.")

print()
print("Node file:")
print(NODES_PATH)

print()
print("Edge file:")
print(EDGES_PATH)

print()
print("Done!")