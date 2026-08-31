"""Builds data/facilities.json from the Overpass API instead of a local PBF.

Overpass gives us live access to the full OpenStreetMap dataset for a
region without downloading/processing a multi-hundred-MB .osm.pbf file.
Good for getting broad coverage quickly; ingestion/build_dataset.py (PBF
based) remains the offline, repeatable, PRD-specified path for production
regeneration.

Usage:
    python -m ingestion.overpass_ingest
    python -m ingestion.overpass_ingest --area "Massachusetts" --output data/facilities.json
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

from ingestion.normalizer import normalize_element
from ingestion.osm_filters import LEISURE_ALLOWLIST, SPORT_TAG_ALLOWLIST

# Facility types kept even without a name — real, shared community pitches
# and courts are frequently unnamed on OSM (e.g. "the tennis court in
# Danehy Park"). Types NOT in this set (pool, playground, gym, generic
# "facility", picnic_table, ...) are dominated by unnamed private/backyard
# nodes on OSM, so those are only kept when they carry a real name.
KEEP_UNNAMED_TYPES = {
    "field",
    "track",
    "stadium",
    "sports_centre",
    "golf_course",
    "rink",
    "disc_golf_course",
    "sports_hall",
}


def is_worth_keeping(facility: dict) -> bool:
    has_name = bool(facility.get("name")) and facility["name"] != "Unnamed facility"
    return has_name or facility.get("facility_type") in KEEP_UNNAMED_TYPES

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = BASE_DIR / "data" / "facilities.json"


def build_query(area_name: str) -> str:
    leisure_regex = "|".join(sorted(LEISURE_ALLOWLIST))
    return f"""
[out:json][timeout:180];
area["name"="{area_name}"]["admin_level"="4"]->.searchArea;
(
  node["leisure"~"^({leisure_regex})$"](area.searchArea);
  way["leisure"~"^({leisure_regex})$"](area.searchArea);
  relation["leisure"~"^({leisure_regex})$"](area.searchArea);
  node["sport"](area.searchArea);
  way["sport"](area.searchArea);
  relation["sport"](area.searchArea);
);
out center tags;
""".strip()


def fetch_elements(area_name: str) -> list[dict]:
    query = build_query(area_name)
    last_error = None

    headers = {"User-Agent": "SportScoutIngest/1.0 (contact: instructor.bettermindlabs@gmail.com)"}

    for endpoint in OVERPASS_ENDPOINTS:
        try:
            with httpx.Client(timeout=200.0) as client:
                response = client.post(endpoint, data={"data": query}, headers=headers)
                response.raise_for_status()
                return response.json().get("elements", [])
        except Exception as exc:  # noqa: BLE001 - fall through to next mirror
            last_error = exc
            time.sleep(2)

    raise RuntimeError(f"All Overpass endpoints failed: {last_error}")


def element_coordinates(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    center = element.get("center")
    if center:
        return center["lat"], center["lon"]
    return None


def build(area_name: str, output_path: Path) -> dict:
    from datetime import datetime, timezone

    raw_elements = fetch_elements(area_name)
    facilities = []
    seen_ids = set()

    for element in raw_elements:
        tags = element.get("tags", {})
        coordinates = element_coordinates(element)
        if coordinates is None:
            continue

        facility = normalize_element(element["type"], element["id"], tags, coordinates[0], coordinates[1])

        if facility["id"] in seen_ids:
            continue
        if not is_worth_keeping(facility):
            continue
        seen_ids.add(facility["id"])
        facilities.append(facility)

    dataset = {
        "metadata": {
            "source": "OpenStreetMap (Overpass API)",
            "region": f"{area_name}, USA",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "facility_count": len(facilities),
        },
        "facilities": facilities,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2, ensure_ascii=False)

    return dataset["metadata"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build facilities.json via the Overpass API.")
    parser.add_argument("--area", default="Massachusetts")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    metadata = build(args.area, Path(args.output))
    print(f"Wrote {metadata['facility_count']} facilities to {args.output}")


if __name__ == "__main__":
    main()
