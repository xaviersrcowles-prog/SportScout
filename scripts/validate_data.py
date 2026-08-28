"""Validates data/facilities.json against the expected schema shape.

Run: python scripts/validate_data.py
Exits non-zero (and prints each problem) if validation fails, so it can be
used as a CI/pre-deploy gate.
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FACILITIES_FILE = BASE_DIR / "data" / "facilities.json"

REQUIRED_FIELDS = ["id", "name", "latitude", "longitude", "access", "condition"]
VALID_ACCESS = {"public", "restricted", "members_only", "private", "unknown"}
VALID_CONDITION = {"excellent", "good", "fair", "poor", "unknown"}


def validate() -> list[str]:
    problems = []

    if not FACILITIES_FILE.exists():
        return [f"{FACILITIES_FILE} does not exist."]

    with FACILITIES_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if "metadata" not in data or "facilities" not in data:
        problems.append("Top-level object must have 'metadata' and 'facilities' keys.")
        return problems

    seen_ids = set()

    for index, facility in enumerate(data["facilities"]):
        label = f"facilities[{index}]"

        for field in REQUIRED_FIELDS:
            if field not in facility:
                problems.append(f"{label} missing required field '{field}'.")

        facility_id = facility.get("id")
        if facility_id in seen_ids:
            problems.append(f"{label} has duplicate id '{facility_id}'.")
        seen_ids.add(facility_id)

        lat, lon = facility.get("latitude"), facility.get("longitude")
        if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
            problems.append(f"{label} has invalid latitude '{lat}'.")
        if not isinstance(lon, (int, float)) or not (-180 <= lon <= 180):
            problems.append(f"{label} has invalid longitude '{lon}'.")

        access = facility.get("access", {})
        classification = access.get("classification") if isinstance(access, dict) else None
        if classification not in VALID_ACCESS:
            problems.append(f"{label} has invalid access classification '{classification}'.")

        condition = facility.get("condition", {})
        status = condition.get("status") if isinstance(condition, dict) else None
        if status not in VALID_CONDITION:
            problems.append(f"{label} has invalid condition status '{status}'.")

    return problems


if __name__ == "__main__":
    issues = validate()
    if issues:
        print(f"facilities.json failed validation with {len(issues)} problem(s):")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)

    print("facilities.json is valid.")
