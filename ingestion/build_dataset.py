"""Command-line entry point: regenerate data/facilities.json from an OSM PBF.

Usage:
    python -m ingestion.build_dataset --pbf path/to/massachusetts.osm.pbf

Requires `pip install -r requirements-ingestion.txt` (osmium is a heavy,
optional dependency not needed to just run the web service).
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.normalizer import normalize_element
from ingestion.osm_parser import iter_sport_elements

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = BASE_DIR / "data" / "facilities.json"


def build(pbf_path: str, output_path: Path, region: str) -> dict:
    facilities = []
    seen_ids = set()

    for element in iter_sport_elements(pbf_path):
        if "wkb_point" in element:
            from shapely import wkb

            point = wkb.loads(element["wkb_point"], hex=True)
            lat, lon = point.y, point.x
        else:
            lat, lon = element["lat"], element["lon"]

        facility = normalize_element(element["type"], element["id"], element["tags"], lat, lon)

        if facility["id"] in seen_ids:
            continue
        seen_ids.add(facility["id"])
        facilities.append(facility)

    dataset = {
        "metadata": {
            "source": "OpenStreetMap",
            "region": region,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "source_file": Path(pbf_path).name,
            "facility_count": len(facilities),
        },
        "facilities": facilities,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2, ensure_ascii=False)

    return dataset["metadata"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build facilities.json from an OSM PBF extract.")
    parser.add_argument("--pbf", required=True, help="Path to the .osm.pbf file")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output JSON path")
    parser.add_argument("--region", default="Massachusetts, USA")
    args = parser.parse_args()

    metadata = build(args.pbf, Path(args.output), args.region)
    print(f"Wrote {metadata['facility_count']} facilities to {args.output}")


if __name__ == "__main__":
    main()
