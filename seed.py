"""Load data/listings.json, embed every listing and insert it into Postgres."""

import json
import os
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector

from embeddings import embed
from generate_data import Listing

LISTINGS_FILE = Path(__file__).parent / "data" / "listings.json"

INSERT_SQL = """
    INSERT INTO listings (title, district, price_eur, rooms, size_m2, description, embedding)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""


def main() -> None:
    load_dotenv()
    listings: list[Listing] = json.loads(LISTINGS_FILE.read_text(encoding="utf-8"))

    texts = [f"{item['title']}. {item['description']}" for item in listings]
    vectors = embed(texts)
    print(f"Embedded {len(vectors)} listings")

    rows = [
        (
            item["title"],
            item["district"],
            item["price_eur"],
            item["rooms"],
            item["size_m2"],
            item["description"],
            np.array(vector),
        )
        for item, vector in zip(listings, vectors, strict=True)
    ]

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute("TRUNCATE listings RESTART IDENTITY;")
            cur.executemany(INSERT_SQL, rows)
    print(f"Inserted {len(rows)} listings")


if __name__ == "__main__":
    main()
