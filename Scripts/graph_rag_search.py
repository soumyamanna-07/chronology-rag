import os
import json
import re
import ladybug
from sentence_transformers import SentenceTransformer
import numpy as np

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

EVENTS_PATH = os.path.join(
    PROJECT_ROOT,
    "Output",
    "events_with_entities.json"
)

DB_PATH = os.path.join(
    PROJECT_ROOT,
    "Data",
    "chronology.lbdb"
)

# ============================================================
# CHECK FILES
# ============================================================

print("Checking project files...")

print("Events file:")
print(EVENTS_PATH)

print("Database:")
print(DB_PATH)

if not os.path.exists(EVENTS_PATH):
    print("ERROR: events_with_entities.json not found.")
    raise SystemExit

if not os.path.exists(DB_PATH):
    print("ERROR: chronology.lbdb not found.")
    raise SystemExit

print("Project files found!")

# ============================================================
# LOAD EVENTS
# ============================================================

print("\nLoading events...")

with open(EVENTS_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

print("Events loaded:", len(events))

event_lookup = {}

for i, event in enumerate(events):

    event_id = event.get(
        "event_id",
        f"EVENT_{i}"
    )

    event_lookup[str(event_id)] = event

print(
    "Event lookup created:",
    len(event_lookup)
)

# ============================================================
# LOAD SEMANTIC MODEL
# ============================================================

print("\nLoading semantic model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Semantic model loaded!")

# ============================================================
# CREATE EVENT TEXTS
# ============================================================

event_texts = []

for event in events:

    month = event.get("month", "")
    date = event.get("date", "")
    text = event.get("text", "")

    combined = f"{month} {date} {text}"

    event_texts.append(combined)

# ============================================================
# CREATE EMBEDDINGS
# ============================================================

print("\nCreating event embeddings...")
print("This may take a few minutes...")

embeddings = model.encode(
    event_texts,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True
)

embeddings = np.array(embeddings)

print(
    "Event embeddings created:",
    len(embeddings)
)

# ============================================================
# OPEN LADYBUGDB
# ============================================================

print("\nOpening LadybugDB...")

db = ladybug.Database(DB_PATH)
conn = ladybug.Connection(db)

print("LadybugDB connected successfully!")

# ============================================================
# ENTITY DETECTION
# ============================================================

def detect_entities(question):

    question_lower = question.lower()

    known_entities = [
        "Swami Vivekananda",
        "Swamiji",
        "Narendranath",
        "America",
        "India",
        "Chicago",
        "Bombay",
        "Madras",
        "Calcutta",
        "Kolkata",
        "London",
        "New York",
        "Khetri",
        "Almora",
        "Benares",
        "Varanasi",
        "Sri Ramakrishna",
        "Swami Abhedananda",
        "Swami Saradananda",
        "Swami Akhandananda"
    ]

    detected = []

    for entity in known_entities:

        if entity.lower() in question_lower:
            detected.append(entity)

    return detected


# ============================================================
# GRAPH SEARCH
# ============================================================

def graph_search(entities):

    event_ids = set()

    for entity in entities:

        query = """
        MATCH (e:Entity)-[r:RELATED]-(x:Entity)
        WHERE x.id = $entity
        RETURN e.id, r.relation, x.id
        LIMIT 5000
        """

        try:

            result = conn.execute(
                query,
                {"entity": entity}
            )

            rows = result.get_all()

            for row in rows:

                event_id = str(row[0])

                if event_id.startswith("EVENT_"):
                    event_ids.add(event_id)

        except Exception as e:

            print(
                "Graph query warning:",
                e
            )

    return list(event_ids)


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def question_keywords(question):

    words = re.findall(
        r"[a-zA-Z]+",
        question.lower()
    )

    stop_words = {
        "when",
        "did",
        "was",
        "were",
        "is",
        "the",
        "a",
        "an",
        "for",
        "to",
        "of",
        "in",
        "on",
        "from",
        "what",
        "where",
        "who",
        "how",
        "and",
        "or"
    }

    return [
        word
        for word in words
        if word not in stop_words
    ]


# ============================================================
# GRAPH RESULT RANKING
# ============================================================

def rank_graph_results(
    question,
    entities,
    graph_event_ids
):

    question_lower = question.lower()

    keywords = question_keywords(question)

    question_embedding = model.encode(
        [question],
        normalize_embeddings=True
    )[0]

    results = []

    for event_id in graph_event_ids:

        event = event_lookup.get(event_id)

        if not event:
            continue

        month = str(
            event.get("month", "")
        )

        date = str(
            event.get("date", "")
        )

        text = str(
            event.get("text", "")
        )

        full_text = (
            month + " " +
            date + " " +
            text
        )

        full_lower = full_text.lower()

        # ----------------------------------------------------
        # Semantic score
        # ----------------------------------------------------

        try:

            event_index = events.index(event)

            semantic_score = float(
                np.dot(
                    embeddings[event_index],
                    question_embedding
                )
            )

        except Exception:

            semantic_score = 0.0

        score = semantic_score * 10

        # ----------------------------------------------------
        # Entity score
        # ----------------------------------------------------

        for entity in entities:

            if entity.lower() in full_lower:
                score += 8

        # ----------------------------------------------------
        # Keyword score
        # ----------------------------------------------------

        for keyword in keywords:

            if keyword in full_lower:
                score += 5

        # ----------------------------------------------------
        # VERY IMPORTANT ACTION WORDS
        # ----------------------------------------------------

        action_words = [
            "sail",
            "sailed",
            "sailing",
            "depart",
            "departed",
            "departure",
            "left",
            "journey",
            "travel",
            "voyage"
        ]

        for word in action_words:

            if word in question_lower:

                if word in full_lower:
                    score += 15

                # Also handle related forms
                if word in ["sail", "sailed", "sailing"]:

                    if "sail" in full_lower:
                        score += 20

        # ----------------------------------------------------
        # AMERICA SCORE
        # ----------------------------------------------------

        if "america" in question_lower:

            if "america" in full_lower:
                score += 15

        # ----------------------------------------------------
        # BOMBAY SCORE
        # ----------------------------------------------------

        if (
            "sail" in question_lower
            or "sailed" in question_lower
        ):

            if "bombay" in full_lower:
                score += 10

        # ----------------------------------------------------
        # DATE SCORE
        # ----------------------------------------------------

        if date.strip():

            score += 2

        # ----------------------------------------------------
        # SPECIAL HIGH-CONFIDENCE PATTERN
        # ----------------------------------------------------

        sailing_patterns = [
            "sailed for america",
            "sail for america",
            "sailed to america",
            "sail to america",
            "sailed from bombay",
            "sailed for the west",
            "set sail for america"
        ]

        for pattern in sailing_patterns:

            if pattern in full_lower:
                score += 50

        results.append(
            {
                "event_id": event_id,
                "score": score,
                "semantic_score": semantic_score,
                "event": event
            }
        )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


# ============================================================
# GRAPH RAG
# ============================================================

def graph_rag_search(question):

    print("\n" + "=" * 70)

    print(
        "Question:",
        question
    )

    # --------------------------------------------------------
    # ENTITY DETECTION
    # --------------------------------------------------------

    entities = detect_entities(question)

    print(
        "Entities detected:",
        entities
    )

    # --------------------------------------------------------
    # GRAPH TRAVERSAL
    # --------------------------------------------------------

    graph_event_ids = graph_search(
        entities
    )

    print(
        "Graph-connected events:",
        len(graph_event_ids)
    )

    # --------------------------------------------------------
    # RANK GRAPH EVENTS
    # --------------------------------------------------------

    if graph_event_ids:

        results = rank_graph_results(
            question,
            entities,
            graph_event_ids
        )

        print(
            "\nGraph RAG Results:"
        )

        for rank, result in enumerate(
            results[:10],
            start=1
        ):

            event = result["event"]

            print(
                "\nResult #",
                rank,
                sep=""
            )

            print(
                "Event:",
                result["event_id"]
            )

            print(
                "Final Score:",
                round(
                    result["score"],
                    3
                )
            )

            print(
                "Semantic Score:",
                round(
                    result["semantic_score"],
                    3
                )
            )

            print(
                "Month:",
                event.get(
                    "month",
                    ""
                )
            )

            print(
                "Date:",
                event.get(
                    "date",
                    ""
                )
            )

            print(
                "Text:",
                event.get(
                    "text",
                    ""
                )
            )

        return

    # --------------------------------------------------------
    # SEMANTIC FALLBACK
    # --------------------------------------------------------

    print(
        "\nNo graph events found."
    )

    print(
        "Using semantic search..."
    )

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True
    )[0]

    scores = np.dot(
        embeddings,
        query_embedding
    )

    top_indices = np.argsort(
        scores
    )[::-1][:10]

    print(
        "\nTop semantic results:"
    )

    for rank, index in enumerate(
        top_indices,
        start=1
    ):

        event = events[index]

        print(
            "\nResult #",
            rank,
            sep=""
        )

        print(
            "Score:",
            round(
                float(scores[index]),
                3
            )
        )

        print(
            "Month:",
            event.get(
                "month",
                ""
            )
        )

        print(
            "Date:",
            event.get(
                "date",
                ""
            )
        )

        print(
            "Text:",
            event.get(
                "text",
                ""
            )
        )


# ============================================================
# MAIN PROGRAM
# ============================================================

print("\n")
print("#" * 70)
print("GRAPH RAG SEARCH")
print("#" * 70)

while True:

    question = input(
        "\nAsk a question (type 'exit' to quit):\n\n> "
    ).strip()

    if question.lower() == "exit":

        print(
            "\nExiting Graph RAG..."
        )

        break

    if not question:
        continue

    try:

        graph_rag_search(
            question
        )

    except Exception as e:

        print(
            "\nERROR:",
            type(e).__name__
        )

        print(
            str(e)
        )