from typing import Optional

from pydantic import BaseModel


class ReportRequest(BaseModel):
    report_type: str
    description: str
    condition: Optional[str] = None


class Report(BaseModel):
    id: str
    facility_id: str
    report_type: str
    description: str
    condition: Optional[str] = None
    status: str = "received"
    created_at: str
