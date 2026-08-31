"""Seeds data/facilities.json with a small curated set of real Massachusetts
sporting facilities, so the app is usable before the OSM PBF is ingested.

Run: python scripts/seed_data.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT = BASE_DIR / "data" / "facilities.json"

RAW = [
    # name, sport_types, facility_type, lat, lon, city, access, hours, operator, surface
    ("Boston Common Frog Pond & Fields", ["multi"], "field", 42.3554, -71.0656, "Boston", "public", "06:00-22:00", "City of Boston", "grass"),
    ("Charles River Esplanade Courts", ["tennis", "basketball"], "court", 42.3560, -71.0784, "Boston", "public", "06:00-23:00", "DCR", "hard"),
    ("Ronan Park", ["soccer", "baseball"], "field", 42.2989, -71.0650, "Dorchester", "public", "06:00-21:00", "City of Boston", "grass"),
    ("Franklin Park Golf Course", ["golf"], "golf_course", 42.3020, -71.0925, "Boston", "public", "06:00-19:00", "City of Boston", None),
    ("Cambridge Common Tennis Courts", ["tennis"], "court", 42.3773, -71.1218, "Cambridge", "public", "07:00-21:00", "City of Cambridge", "hard"),
    ("Danehy Park Sports Complex", ["soccer", "baseball", "running"], "field", 42.3927, -71.1370, "Cambridge", "public", "06:00-22:00", "City of Cambridge", "turf"),
    ("Somerville Dilboy Stadium", ["multi", "running"], "stadium", 42.3931, -71.1120, "Somerville", "public", "07:00-20:00", "City of Somerville", "turf"),
    ("Medford High School Athletic Complex", ["baseball", "soccer"], "field", 42.4251, -71.1120, "Medford", "restricted", None, "Medford Public Schools", "grass"),
    ("Malden YMCA Pool", ["swimming"], "pool", 42.4251, -71.0662, "Malden", "members_only", "05:30-21:00", "YMCA", None),
    ("Quincy Adams Field", ["soccer", "baseball"], "field", 42.2529, -71.0023, "Quincy", "public", "06:00-21:00", "City of Quincy", "grass"),
    ("Wollaston Beach Volleyball Courts", ["volleyball"], "court", 42.2649, -70.9954, "Quincy", "public", "sunrise-sunset", "City of Quincy", "sand"),
    ("Newton Crystal Lake Fields", ["soccer", "softball"], "field", 42.3232, -71.2019, "Newton", "public", "06:00-21:00", "City of Newton", "grass"),
    ("Newton South Skate Park", ["skateboard"], "skate_park", 42.3054, -71.2277, "Newton", "public", "08:00-20:00", "City of Newton", "concrete"),
    ("Brookline Soule Recreation Center", ["basketball", "tennis"], "sports_centre", 42.3467, -71.1354, "Brookline", "public", "06:00-22:00", "Town of Brookline", "hard"),
    ("Waltham Storer Field", ["baseball"], "field", 42.3765, -71.2356, "Waltham", "public", "06:00-21:00", "City of Waltham", "grass"),
    ("Lexington Center Recreation Complex", ["tennis", "basketball", "running"], "sports_centre", 42.4479, -71.2261, "Lexington", "public", "06:00-21:00", "Town of Lexington", "hard"),
    ("Concord Emerson Playground Fields", ["soccer"], "field", 42.4604, -71.3489, "Concord", "public", "06:00-20:00", "Town of Concord", "grass"),
    ("Worcester Green Hill Park Track", ["running", "athletics"], "track", 42.2887, -71.7756, "Worcester", "public", "06:00-21:00", "City of Worcester", "track"),
    ("Worcester Institute Park Tennis", ["tennis"], "court", 42.2681, -71.7900, "Worcester", "public", "07:00-20:00", "City of Worcester", "hard"),
    ("Springfield Forest Park Fields", ["soccer", "baseball"], "field", 42.0987, -72.5645, "Springfield", "public", "06:00-21:00", "City of Springfield", "grass"),
    ("Springfield YMCA Fitness Center", ["multi"], "gym", 42.1015, -72.5898, "Springfield", "members_only", "05:00-22:00", "YMCA", None),
    ("Lowell VFW Highlands Fields", ["soccer", "baseball"], "field", 42.6382, -71.3399, "Lowell", "public", "06:00-21:00", "City of Lowell", "grass"),
    ("Salem Willows Basketball Courts", ["basketball"], "court", 42.5311, -70.8639, "Salem", "public", "07:00-21:00", "City of Salem", "hard"),
    ("Salem State Equestrian Center", ["equestrian"], "equestrian", 42.5195, -70.9070, "Salem", "private", None, "Private Owner", None),
    ("New Bedford Buttonwood Park Fields", ["soccer", "baseball", "running"], "field", 41.6474, -70.9502, "New Bedford", "public", "06:00-21:00", "City of New Bedford", "grass"),
    ("Fall River South Park Courts", ["tennis", "basketball"], "court", 41.6957, -71.1548, "Fall River", "public", "07:00-20:00", "City of Fall River", "hard"),
    ("Barnstable Hyannis Youth Fields", ["soccer", "baseball"], "field", 41.6521, -70.2911, "Barnstable", "public", "06:00-20:00", "Town of Barnstable", "grass"),
    ("Northampton Look Park Fields", ["soccer", "softball"], "field", 42.3320, -72.6704, "Northampton", "public", "07:00-19:00", "Look Park Trustees", "grass"),
    ("Amherst College Athletic Fields", ["soccer", "baseball", "running"], "field", 42.3709, -72.5170, "Amherst", "restricted", None, "Amherst College", "turf"),
    ("Pittsfield Wahconah Park", ["baseball"], "stadium", 42.4636, -73.2540, "Pittsfield", "public", None, "City of Pittsfield", "grass"),
]


def build_facility(row: tuple, index: int) -> dict:
    (
        name,
        sports,
        facility_type,
        lat,
        lon,
        city,
        access,
        hours,
        operator,
        surface,
    ) = row

    confidence = {
        "public": 0.9,
        "restricted": 0.7,
        "members_only": 0.8,
        "private": 0.85,
    }.get(access, 0.5)

    return {
        "id": f"seed_{index + 1:03d}",
        "name": name,
        "sport_types": sports,
        "facility_type": facility_type,
        "latitude": lat,
        "longitude": lon,
        "address": {"city": city, "state": "MA"},
        "access": {
            "classification": access,
            "confidence": confidence,
            "evidence": f"Known {access.replace('_', ' ')} facility operated by {operator}.",
            "source": "curated",
        },
        "hours": {
            "raw": hours,
            "display": hours,
            "source": "curated" if hours else None,
        },
        "condition": {"status": "unknown", "score": None, "last_reported": None},
        "surface": surface,
        "amenities": [],
        "operator": operator,
        "website": None,
        "osm": {},
        "sources": ["curated"],
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    facilities = [build_facility(row, i) for i, row in enumerate(RAW)]

    dataset = {
        "metadata": {
            "source": "curated-seed",
            "region": "Massachusetts, USA",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "facility_count": len(facilities),
            "note": (
                "Seed data for local development and initial deployment. "
                "Run ingestion/build_dataset.py against the Massachusetts OSM "
                "PBF to replace this with the full normalized dataset."
            ),
        },
        "facilities": facilities,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=2, ensure_ascii=False)

    print(f"Wrote {len(facilities)} seed facilities to {OUTPUT}")


if __name__ == "__main__":
    main()
