"""SportsFinder API entry point.

Business logic lives in app/routes, app/services and app/repositories;
this file only wires the FastAPI app together and serves the built
React frontend from the same Render web service.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, FACILITIES_FILE, FRONTEND_DIST, REPORTS_FILE
from app.repositories.json_repository import JsonRepository
from app.routes import ai, facilities, health, reports, search
from app.services.facility_service import FacilityService
from app.services.search_service import SearchService


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository = JsonRepository(FACILITIES_FILE, REPORTS_FILE)
    app.state.repository = repository
    app.state.facility_service = FacilityService(repository)
    app.state.search_service = SearchService(app.state.facility_service)
    yield


app = FastAPI(
    title="SportsFinder API",
    version="1.0.0",
    description="Find nearby sporting facilities and understand their access and condition.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
def api_root():
    return {"name": "SportsFinder API", "status": "ok"}


app.include_router(health.router)
app.include_router(facilities.router)
app.include_router(search.router)
app.include_router(reports.router)
app.include_router(ai.router)

# Serve the production React application from the same Render web service.
if FRONTEND_DIST.exists():
    assets_directory = FRONTEND_DIST / "assets"

    if assets_directory.exists():
        app.mount("/assets", StaticFiles(directory=assets_directory), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        requested_file = FRONTEND_DIST / full_path

        if full_path and requested_file.is_file():
            return FileResponse(requested_file)

        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)

        raise HTTPException(status_code=404, detail="Frontend build not found. Run npm run build.")
