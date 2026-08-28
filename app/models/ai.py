from typing import Optional

from pydantic import BaseModel


class AccessClassificationRequest(BaseModel):
    facility_name: str = ""
    description: str = ""
    access_tag: Optional[str] = None
    operator: Optional[str] = None
    website_text: Optional[str] = None


class AccessClassificationResult(BaseModel):
    classification: str
    confidence: float
    evidence: str
    source: str
    model: Optional[str] = None
    ai_error: Optional[str] = None
