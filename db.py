"""Database connection and search queries."""

import os
from typing import Any, TypedDict, cast

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg.rows import DictRow, dict_row

load_dotenv()

SEARCH_SQL = """
    SELECT id, title, district, price_eur, rooms, size_m2, description,
           1 - (embedding <=> %(qvec)s) AS similarity
    FROM listings
    WHERE price_eur <= %(max_price)s
      AND rooms >= %(min_rooms)s
      AND (%(district)s::text IS NULL OR district = %(district)s)
    ORDER BY embedding <=> %(qvec)s
    LIMIT 10;
"""

DISTRICTS_SQL = "SELECT DISTINCT district FROM listings ORDER BY district;"


class SearchResult(TypedDict):
    id: int
    title: str
    district: str
    price_eur: int
    rooms: int
    size_m2: int
    description: str
    similarity: float


Connection = psycopg.Connection[DictRow]


def connect() -> Connection:
    """Open a connection using DATABASE_URL (local Docker or a hosted Postgres)."""
    conn = Connection.connect(os.environ["DATABASE_URL"], autocommit=True, row_factory=dict_row)
    register_vector(conn)
    return conn


def search(
    conn: Connection,
    query_vec: list[float],
    max_price: int,
    min_rooms: int,
    district: str | None,
) -> list[SearchResult]:
    """Return the 10 listings closest in meaning to query_vec that pass the filters."""
    params: dict[str, Any] = {
        "qvec": np.array(query_vec),
        "max_price": max_price,
        "min_rooms": min_rooms,
        "district": district,
    }
    rows = conn.execute(SEARCH_SQL, params).fetchall()
    return cast(list[SearchResult], rows)


def districts(conn: Connection) -> list[str]:
    """Return the districts that have at least one listing, sorted by name."""
    rows = conn.execute(DISTRICTS_SQL).fetchall()
    return [row["district"] for row in rows]
