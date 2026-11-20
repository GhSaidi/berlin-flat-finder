-- M1: listings table with an embedding column for semantic search.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS listings (
    id          SERIAL PRIMARY KEY,
    title       TEXT    NOT NULL,
    district    TEXT    NOT NULL,
    price_eur   INTEGER NOT NULL,   -- monthly warm rent
    rooms       INTEGER NOT NULL,
    size_m2     INTEGER NOT NULL,
    description TEXT    NOT NULL,
    embedding   vector(1536)        -- text-embedding-3-small
);

CREATE INDEX IF NOT EXISTS listings_embedding_hnsw
    ON listings USING hnsw (embedding vector_cosine_ops);
