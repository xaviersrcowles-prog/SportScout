"""Allowlist of OSM tags that identify sport/recreation facilities."""

SPORT_TAG_ALLOWLIST = {
    "soccer",
    "tennis",
    "basketball",
    "baseball",
    "softball",
    "running",
    "athletics",
    "equestrian",
    "swimming",
    "volleyball",
    "skateboard",
    "multi",
}

LEISURE_ALLOWLIST = {
    "pitch",
    "sports_centre",
    "stadium",
    "track",
    "swimming_pool",
    "golf_course",
    "ice_rink",
    "fitness_centre",
    "playground",
}

FACILITY_TYPE_BY_LEISURE = {
    "pitch": "field",
    "sports_centre": "sports_centre",
    "stadium": "stadium",
    "track": "track",
    "swimming_pool": "pool",
    "golf_course": "golf_course",
    "ice_rink": "rink",
    "fitness_centre": "gym",
    "playground": "playground",
}


def is_sport_feature(tags: dict) -> bool:
    if tags.get("leisure") in LEISURE_ALLOWLIST:
        return True
    if "sport" in tags:
        return True
    return False


def facility_type_for(tags: dict) -> str:
    leisure = tags.get("leisure")
    return FACILITY_TYPE_BY_LEISURE.get(leisure, leisure or "facility")
