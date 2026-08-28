"""All external AI provider calls are isolated in this module.

The API key never leaves the backend; the frontend only ever talks to
FastAPI, which talks to the provider from here.
"""

import json
from typing import Any

import httpx

from app.config import AI_API_KEY, AI_MODEL, AI_PROVIDER
from app.models.ai import AccessClassificationRequest
from app.utils.normalization import normalize_text

ALLOWED_CLASSIFICATIONS = {"public", "restricted", "members_only", "private", "unknown"}


def build_access_prompt(request: AccessClassificationRequest) -> str:
    return f"""
Classify the access status of this sporting facility.

Allowed classifications:
- public
- restricted
- members_only
- private
- unknown

Do not assume ownership means public access.
Return ONLY valid JSON with this exact structure:
{{
  "classification": "public|restricted|members_only|private|unknown",
  "confidence": 0.0,
  "evidence": "short evidence summary"
}}

Facility name: {request.facility_name}
Description: {request.description}
OSM access tag: {request.access_tag}
Operator: {request.operator}
Website/source text: {request.website_text}
""".strip()


def is_configured() -> bool:
    return bool(AI_API_KEY and AI_MODEL and AI_PROVIDER in {"openai", "openai-compatible"})


async def classify_with_ai(request: AccessClassificationRequest) -> dict[str, Any]:
    """Call the configured OpenAI-compatible chat API.

    Raises if the provider is not configured or the call fails; callers must
    catch and fall back to deterministic_access_classification.
    """
    if not is_configured():
        raise RuntimeError("AI API is not configured.")

    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You classify sporting facility access. "
                    "Follow the requested JSON structure exactly."
                ),
            },
            {"role": "user", "content": build_access_prompt(request)},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"]
    result = json.loads(content)

    classification = normalize_text(result.get("classification"))
    if classification not in ALLOWED_CLASSIFICATIONS:
        classification = "unknown"

    try:
        confidence = float(result.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = max(0.0, min(1.0, confidence))

    return {
        "classification": classification,
        "confidence": confidence,
        "evidence": str(result.get("evidence", ""))[:1000],
        "source": "ai",
        "model": AI_MODEL,
    }
