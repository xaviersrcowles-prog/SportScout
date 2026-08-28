import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIST = BASE_DIR / "dist"

FACILITIES_FILE = Path(os.getenv("DATA_FILE", str(DATA_DIR / "facilities.json")))
REPORTS_FILE = Path(os.getenv("REPORTS_FILE", str(DATA_DIR / "reports.json")))

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "").lower()
AI_MODEL = os.getenv("AI_MODEL", "")

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "*")
CORS_ORIGINS = [o.strip() for o in FRONTEND_ORIGIN.split(",") if o.strip()] or ["*"]

DEFAULT_RADIUS_MILES = 5.0
RECOMMENDATION_WEIGHTS = {
    "distance": 0.35,
    "access": 0.25,
    "condition": 0.20,
    "hours": 0.10,
    "confidence": 0.10,
}
