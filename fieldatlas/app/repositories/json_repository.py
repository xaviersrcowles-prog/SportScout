"""JSON-file backed storage for facilities and reports.

Isolated behind this repository so the frontend/service contract can move
to a real database later without touching callers.
"""

import json
from pathlib import Path
from typing import Any


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    temporary_path.replace(path)


class JsonRepository:
    def __init__(self, facilities_file: Path, reports_file: Path):
        self.facilities_file = facilities_file
        self.reports_file = reports_file
        self._facilities: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {}
        self.reload()

    def ensure_files(self) -> None:
        self.facilities_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.facilities_file.exists():
            save_json_file(
                self.facilities_file,
                {
                    "metadata": {
                        "source": "OpenStreetMap",
                        "region": "Massachusetts, USA",
                        "schema_version": "1.0",
                    },
                    "facilities": [],
                },
            )
        if not self.reports_file.exists():
            save_json_file(self.reports_file, [])

    def reload(self) -> None:
        self.ensure_files()
        data = load_json_file(self.facilities_file, {"metadata": {}, "facilities": []})
        if isinstance(data, dict):
            self.metadata = data.get("metadata", {})
            facilities = data.get("facilities", [])
            self._facilities = facilities if isinstance(facilities, list) else []
        elif isinstance(data, list):
            self.metadata = {}
            self._facilities = data
        else:
            self.metadata = {}
            self._facilities = []

    def all_facilities(self) -> list[dict[str, Any]]:
        return self._facilities

    def find(self, facility_id: str) -> dict[str, Any] | None:
        for facility in self._facilities:
            if str(facility.get("id")) == str(facility_id):
                return facility
        return None

    def load_reports(self) -> list[dict[str, Any]]:
        data = load_json_file(self.reports_file, [])
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            reports = data.get("reports", [])
            return reports if isinstance(reports, list) else []
        return []

    def save_report(self, report: dict[str, Any]) -> None:
        reports = self.load_reports()
        reports.append(report)
        save_json_file(self.reports_file, reports)

    def reports_for_facility(self, facility_id: str) -> list[dict[str, Any]]:
        return [
            r for r in self.load_reports() if str(r.get("facility_id")) == str(facility_id)
        ]
