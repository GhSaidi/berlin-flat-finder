"""OpenAI embeddings for listing documents and search queries."""

import os
from functools import cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


@cache
def _client() -> OpenAI:
    """Create the OpenAI client once, on first use (reads OPENAI_API_KEY)."""
    return OpenAI()


def embed(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector per input text, in the same order."""
    response = _client().embeddings.create(
        model=os.environ["OPENAI_EMBEDDING_MODEL"],
        input=texts,
    )
    return [item.embedding for item in response.data]
