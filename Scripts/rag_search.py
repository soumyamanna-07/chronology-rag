import json
import re
from pathlib import Path

from sentence_transformers import SentenceTransformer, util


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
EVENTS_PATH = BASE_DIR / "Output" / "events.json"


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = SentenceTransformer("all-MiniLM-L6-v2")


# ============================================================
# LOAD EVENTS
# ============================================================

print("Loading events...")

if not EVENTS_PATH.exists():
    print("ERROR: events.json not found:")
    print(EVENTS_PATH)
    raise SystemExit(1)

with open(EVENTS_PATH, "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"Loaded {len(events)} events.")


# ============================================================
# PREPARE TEXT
# ============================================================

texts = []

for event in events:

    month = str(event.get("month", ""))
    date = str(event.get("date", ""))
    text = str(event.get("text", ""))

    combined = f"{month} {date} {text}"

    texts.append(combined)


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

print("Creating embeddings...")

embeddings = model.encode(
    texts,
    convert_to_tensor=True,
    show_progress_bar=True
)

print("\nRAG Search Ready!")


# ============================================================
# EXTRACT YEAR
# ============================================================

def extract_year(query):

    match = re.search(r"\b(18|19|20)\d{2}\b", query)

    if match:
        return match.group(0)

    return None


# ============================================================
# NORMALIZE WORDS
# ============================================================

def get_words(text):

    text = text.lower()

    words = re.findall(r"[a-z0-9]+", text)

    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "was",
        "were",
        "did",
        "do",
        "does",
        "when",
        "what",
        "where",
        "who",
        "how",
        "why",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "and",
        "or",
        "from",
        "with",
        "about",
        "his",
        "her",
        "their",
        "he",
        "she",
        "it",
    }

    return set(
        word
        for word in words
        if word not in stop_words and len(word) > 2
    )


# ============================================================
# KEYWORD SCORE
# ============================================================

def keyword_score(query, text):

    query_words = get_words(query)
    text_words = get_words(text)

    if not query_words:
        return 0.0

    matched_words = query_words.intersection(text_words)

    return len(matched_words) / len(query_words)


# ============================================================
# SEARCH
# ============================================================

def search(query, top_k=5):

    query = query.strip()

    if not query:
        return


    # --------------------------------------------------------
    # YEAR DETECTION
    # --------------------------------------------------------

    year = extract_year(query)

    candidate_indices = []


    if year:

        print(
            f"\nSearching specifically for events from {year}..."
        )

        for i, event in enumerate(events):

            month = str(event.get("month", ""))
            date = str(event.get("date", ""))
            text = str(event.get("text", ""))

            combined = f"{month} {date} {text}"

            if year in combined:
                candidate_indices.append(i)

        print(
            f"Found {len(candidate_indices)} events for {year}."
        )

    else:

        candidate_indices = list(range(len(events)))


    # --------------------------------------------------------
    # CHECK RESULTS
    # --------------------------------------------------------

    if not candidate_indices:

        print("\nNo matching events found.")

        return


    # --------------------------------------------------------
    # QUERY EMBEDDING
    # --------------------------------------------------------

    query_embedding = model.encode(
        query,
        convert_to_tensor=True
    )


    # --------------------------------------------------------
    # SEMANTIC SIMILARITY
    # --------------------------------------------------------

    candidate_embeddings = embeddings[candidate_indices]

    semantic_scores = util.cos_sim(
        query_embedding,
        candidate_embeddings
    )[0]


    # --------------------------------------------------------
    # HYBRID SCORING
    # --------------------------------------------------------

    final_results = []


    for position, semantic_score in enumerate(
        semantic_scores
    ):

        original_index = candidate_indices[position]

        event = events[original_index]

        month = str(event.get("month", ""))

        date = str(event.get("date", ""))

        text = str(event.get("text", ""))

        combined_text = f"{month} {date} {text}"


        # Semantic similarity
        semantic = float(semantic_score)


        # Keyword similarity
        keyword = keyword_score(
            query,
            combined_text
        )


        # ----------------------------------------------------
        # PHRASE BOOSTS
        # ----------------------------------------------------

        query_lower = query.lower()

        text_lower = combined_text.lower()

        phrase_bonus = 0.0


        # Sailing to America
        if (
            "sail" in query_lower
            and "america" in query_lower
            and "sail" in text_lower
            and "america" in text_lower
        ):

            phrase_bonus += 0.20


        # Chicago / Parliament of Religions
        if (
            "chicago" in query_lower
            and "chicago" in text_lower
        ):

            phrase_bonus += 0.15


        if (
            "parliament" in query_lower
            and "parliament" in text_lower
        ):

            phrase_bonus += 0.15


        # Birth
        if (
            "born" in query_lower
            and (
                "born" in text_lower
                or "birth" in text_lower
            )
        ):

            phrase_bonus += 0.15


        # Death
        if (
            "died" in query_lower
            and (
                "died" in text_lower
                or "death" in text_lower
            )
        ):

            phrase_bonus += 0.15


        # Final hybrid score
        final_score = (
            semantic * 0.70
            + keyword * 0.20
            + phrase_bonus
        )


        final_results.append(
            (
                final_score,
                semantic,
                keyword,
                original_index
            )
        )


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    final_results.sort(
        key=lambda x: x[0],
        reverse=True
    )


    # --------------------------------------------------------
    # TOP RESULTS
    # --------------------------------------------------------

    final_results = final_results[:top_k]


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    print("\nTop Results:\n")


    for rank, (
        final_score,
        semantic,
        keyword,
        original_index
    ) in enumerate(final_results, start=1):


        event = events[original_index]


        month = str(
            event.get("month", "N/A")
        )

        date = str(
            event.get("date", "N/A")
        )

        text = str(
            event.get("text", "N/A")
        )


        print("=" * 80)

        print(
            f"Result #{rank}"
        )

        print(
            f"Final Score   : {final_score:.3f}"
        )

        print(
            f"Semantic Score: {semantic:.3f}"
        )

        print(
            f"Keyword Score : {keyword:.3f}"
        )

        print(
            f"Month : {month}"
        )

        print(
            f"Date  : {date}"
        )

        print(
            f"Text  : {text}"
        )

        print("=" * 80)


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    try:

        query = input(
            "\nAsk a question (type 'exit' to quit): "
        )

    except KeyboardInterrupt:

        print("\nExiting RAG Search...")

        break


    if query.lower().strip() == "exit":

        print("Exiting RAG Search...")

        break


    search(query)