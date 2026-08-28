#!/usr/bin/env bash
# Regenerate data/facilities.json from a Massachusetts OSM PBF extract.
#
# Usage: scripts/build_data.sh path/to/massachusetts.osm.pbf
set -euo pipefail

PBF_PATH="${1:?Usage: scripts/build_data.sh path/to/file.osm.pbf}"

pip install -r requirements-ingestion.txt
python -m ingestion.build_dataset --pbf "$PBF_PATH"
python scripts/validate_data.py
