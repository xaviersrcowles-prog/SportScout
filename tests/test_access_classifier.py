from app.models.ai import AccessClassificationRequest
from app.services.access_classifier import deterministic_access_classification


def classify(access_tag):
    request = AccessClassificationRequest(access_tag=access_tag)
    return deterministic_access_classification(request)


def test_public_tag():
    result = classify("yes")
    assert result["classification"] == "public"
    assert result["confidence"] > 0


def test_private_tag():
    result = classify("no")
    assert result["classification"] == "private"


def test_restricted_tag():
    result = classify("permit")
    assert result["classification"] == "restricted"


def test_unknown_when_no_tag():
    result = classify(None)
    assert result["classification"] == "unknown"
    assert result["confidence"] == 0.0
