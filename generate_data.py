"""Generate synthetic Berlin flat listings (no API calls, reproducible)."""

import json
import random
from pathlib import Path
from typing import TypedDict

DATA_DIR = Path(__file__).parent / "data"
NUM_LISTINGS = 200

FEATURES = [
    "balcony",
    "elevator",
    "quiet courtyard",
    "near a park",
    "5 min to U-Bahn",
    "renovated kitchen",
    "wooden floors",
    "room for a home office",
    "pet-friendly",
    "furnished",
    "bathtub",
    "rooftop terrace",
    "bright south-facing",
    "close to cafés and bars",
    "high ceilings",
    "new windows with good sound insulation",
    "bike storage in the basement",
    "fast fibre internet",
    "dishwasher included",
    "view over the rooftops",
]

ADJECTIVES = ["Bright", "Cosy", "Spacious", "Charming", "Modern", "Quiet", "Sunny", "Stylish"]


class District(TypedDict):
    name: str
    rate: float
    description: str


class Listing(TypedDict):
    title: str
    district: str
    price_eur: int
    rooms: int
    size_m2: int
    description: str


def make_listing(district: District) -> Listing:
    rooms = random.randint(1, 4)
    size_m2 = round(rooms * random.uniform(25, 35) + random.uniform(-5, 5))
    price_eur = round(size_m2 * district["rate"] * random.uniform(0.85, 1.2), -1)
    features = random.sample(FEATURES, k=random.randint(3, 4))
    description = (
        f"{rooms}-room flat, {size_m2} m². Features: {', '.join(features)}. "
        f"{district['description']}"
    )
    return {
        "title": f"{random.choice(ADJECTIVES)} {rooms}-room flat in {district['name']}",
        "district": district["name"],
        "price_eur": int(price_eur),
        "rooms": rooms,
        "size_m2": size_m2,
        "description": description,
    }


def main() -> None:
    random.seed(42)
    districts: list[District] = json.loads(
        (DATA_DIR / "districts.json").read_text(encoding="utf-8")
    )
    listings: list[Listing] = [make_listing(random.choice(districts)) for _ in range(NUM_LISTINGS)]
    out = DATA_DIR / "listings.json"
    out.write_text(json.dumps(listings, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(listings)} listings to {out}")


if __name__ == "__main__":
    main()
