"""Streamlit UI: describe a flat in plain words, filter with SQL, rank by meaning."""

import logging
from collections.abc import Callable

import openai
import psycopg
import streamlit as st

import db
from embeddings import embed

EXAMPLE_SIMPLE = "quiet flat near a park with a balcony"
EXAMPLE_DETAILED = "2-room flat in Pankow with a balcony near a park"
PLACEHOLDER = f"Try “{EXAMPLE_SIMPLE}” or “{EXAMPLE_DETAILED}”"
MIN_SIMILARITY = 0.30  # measured: unrelated queries score 15-22 %, real descriptions 50 %+
ERROR_MESSAGE = "Search is unavailable right now, please try again."
EXPECTED_ERRORS = (openai.OpenAIError, psycopg.Error, KeyError)

logger = logging.getLogger(__name__)


@st.cache_resource
def get_conn() -> db.Connection:
    """One database connection, shared across reruns and visitors."""
    return db.connect()


def with_retry[T](query: Callable[[db.Connection], T]) -> T:
    """Run a query; if the connection was dropped (e.g. idle timeout), reconnect once."""
    conn = get_conn()
    if conn.closed:
        get_conn.clear()
        conn = get_conn()
    try:
        return query(conn)
    except psycopg.OperationalError:
        get_conn.clear()
        return query(get_conn())


@st.cache_data(show_spinner=False)
def embed_query(text: str) -> list[float]:
    """Embed the search text; the same text never calls the API twice."""
    return embed([text])[0]


def log_failure(exc: Exception) -> None:
    """Log only the error type, never messages that could contain secrets."""
    logger.error("Request failed: %s", type(exc).__name__)


st.set_page_config(page_title="Berlin Flat Finder", page_icon="🏠")
st.title("🏠 Berlin Flat Finder")
st.caption("Describe your ideal flat in plain words. Filters run in SQL, ranking by meaning.")

try:
    district_names = with_retry(db.districts)
except EXPECTED_ERRORS as exc:
    log_failure(exc)
    st.error(ERROR_MESSAGE)
    st.stop()

with st.sidebar:
    st.header("Filters")
    max_price = st.slider("Max warm rent (€)", 300, 3300, 1500, step=50)
    min_rooms = st.slider("Min rooms", 1, 4, 1)
    district_choice = st.selectbox("District", ["Any", *district_names])
    district = None if district_choice == "Any" else district_choice

query = st.text_input("Describe your ideal flat", placeholder=PLACEHOLDER).strip()

if query:
    try:
        with st.spinner("Searching..."):
            query_vec = embed_query(query)
            results = with_retry(
                lambda conn: db.search(conn, query_vec, max_price, min_rooms, district)
            )
    except EXPECTED_ERRORS as exc:
        log_failure(exc)
        st.error(ERROR_MESSAGE)
        st.stop()

    if not results:
        st.info("No flats match these filters. Try a higher price or fewer rooms.")
        st.stop()

    if results[0]["similarity"] < MIN_SIMILARITY:
        st.warning(
            "No flats match this description. Describe the flat itself, for example "
            "the number of rooms, the district or features like a balcony or a park nearby."
        )
        st.caption("Or copy one of these examples:")
        st.code(EXAMPLE_SIMPLE, language=None)
        st.code(EXAMPLE_DETAILED, language=None)
        st.stop()

    for flat in results:
        rooms = f"{flat['rooms']} room" + ("s" if flat["rooms"] > 1 else "")
        with st.container(border=True):
            st.subheader(flat["title"])
            st.markdown(
                f"**{flat['district']}** · €{flat['price_eur']:,} · {rooms} · "
                f"{flat['size_m2']} m² · **{flat['similarity'] * 100:.0f}% match**"
            )
            st.write(flat["description"])
