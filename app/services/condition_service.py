"""Condition scoring from user reports, weighting newer reports more heavily."""

from datetime import datetime, timezone
from typing import Any, Optional

STATUS_SCORES = {"excellent": 100, "good": 80, "fair": 50, "poor": 20}
HALF_LIFE_DAYS = 60.0


def _report_weight(created_at: str) -> float:
    try:
        reported = datetime.fromisoformat(created_at)
        if reported.tzinfo is None:
            reported = reported.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return 0.1

    age_days = max(0.0, (datetime.now(timezone.utc) - reported).total_seconds() / 86400)
    return 0.5 ** (age_days / HALF_LIFE_DAYS)


def condition_from_reports(reports: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """Blend condition-type reports into a status/score, weighted by recency."""
    condition_reports = [
        r for r in reports if r.get("report_type") == "condition" and r.get("condition")
    ]
    if not condition_reports:
        return None

    total_weight = 0.0
    weighted_score = 0.0
    latest = None

    for report in condition_reports:
        status = str(report.get("condition", "")).lower()
        score = STATUS_SCORES.get(status)
        if score is None:
            continue
        weight = _report_weight(report.get("created_at", ""))
        weighted_score += score * weight
        total_weight += weight
        if latest is None or report.get("created_at", "") > latest:
            latest = report.get("created_at")

    if total_weight == 0:
        return None

    final_score = weighted_score / total_weight
    status = min(STATUS_SCORES.items(), key=lambda kv: abs(kv[1] - final_score))[0]

    return {
        "status": status,
        "score": round(final_score, 1),
        "last_reported": latest,
    }
