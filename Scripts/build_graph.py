import json
import csv

EVENTS_PATH = "Output/events_with_entities.json"
NODES_PATH = "Output/graph_nodes.csv"
EDGES_PATH = "Output/graph_edges.csv"

MAIN_PERSON = "Swami Vivekananda"

print("Loading entity-enriched events...")

with open(EVENTS_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

nodes = {}
edges = []

# Add main person
nodes[MAIN_PERSON] = "Person"

# --------------------------------------------------
# Build event + entity graph
# --------------------------------------------------

for event_id, event in enumerate(events):

    event_node = f"EVENT_{event_id}"

    # Event node
    nodes[event_node] = "Event"

    # ---------------- People ----------------

    for person in event.get("people", []):

        nodes[person] = "Person"

        edges.append([
            event_node,
            "INVOLVES",
            person
        ])

    # ---------------- Places ----------------

    for place in event.get("places", []):

        nodes[place] = "Place"

        edges.append([
            event_node,
            "INVOLVES",
            place
        ])

    # ---------------- Organizations ----------------

    for org in event.get("organizations", []):

        nodes[org] = "Organization"

        edges.append([
            event_node,
            "INVOLVES",
            org
        ])

    # ---------------- Dates ----------------

    for date in event.get("dates_found", []):

        nodes[date] = "Date"

        edges.append([
            event_node,
            "HAS_DATE",
            date
        ])

# --------------------------------------------------
# Add higher-level relationships
# --------------------------------------------------

for event in events:

    people = event.get("people", [])
    places = event.get("places", [])
    organizations = event.get("organizations", [])

    # Person → Place
    for person in people:

        for place in places:

            nodes[person] = "Person"
            nodes[place] = "Place"

            edges.append([
                person,
                "VISITED",
                place
            ])

    # Person → Organization
    for person in people:

        for org in organizations:

            nodes[person] = "Person"
            nodes[org] = "Organization"

            edges.append([
                person,
                "ASSOCIATED_WITH",
                org
            ])

# --------------------------------------------------
# Remove duplicate edges
# --------------------------------------------------

unique_edges = []

seen = set()

for edge in edges:

    key = tuple(edge)

    if key not in seen:

        seen.add(key)
        unique_edges.append(edge)

edges = unique_edges

# --------------------------------------------------
# Save Nodes
# --------------------------------------------------

print("Saving graph nodes...")

with open(
    NODES_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "id",
        "type"
    ])

    for node, node_type in sorted(nodes.items()):

        writer.writerow([
            node,
            node_type
        ])

# --------------------------------------------------
# Save Edges
# --------------------------------------------------

print("Saving graph edges...")

with open(
    EDGES_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "source",
        "relation",
        "target"
    ])

    for edge in edges:

        writer.writerow(edge)

print()
print("Knowledge Graph Created!")
print()
print("Events :", len(events))
print("Nodes  :", len(nodes))
print("Edges  :", len(edges))