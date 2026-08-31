# SportScout

Find nearby sporting fields, courts, tracks and recreation facilities — with
access classification (public/restricted/members-only/private/unknown),
hours, condition, and an interactive OpenStreetMap-based map. Built for the
Massachusetts pilot region defined in [`docs/PRD.md`](docs/PRD.md).

React + Vite frontend, FastAPI backend, JSON-file storage, deployed as a
single Render web service.

## Project layout

```
main.py              FastAPI entry point (thin — wires routers together)
app/
  config.py           Environment configuration
  models/              Pydantic request/response models
  routes/               facilities, search, reports, ai, health
  services/             facility_service, search_service, access_classifier, ai_service, condition_service
  repositories/          json_repository.py — isolates JSON file access
  utils/                 geo.py, normalization.py
data/                 facilities.json, reports.json (runtime data)
ingestion/            OSM PBF -> facilities.json pipeline
src/                  React frontend
public/map-frame/     The embedded map iframe document (Leaflet + OSM tiles)
scripts/              build_data.sh, validate_data.py, seed_data.py
tests/                pytest suite
```

## Local development

Backend:

```bash
pip install -r requirements-dev.txt
uvicorn main:app --reload
```

Frontend (separate terminal):

```bash
npm install
npm run dev
```

The Vite dev server proxies nothing by default — set `VITE_API_BASE_URL` in
a `.env` file (copy `.env.example`) to point at `http://localhost:8000` if
you run the backend on a different port during development.

## Data

`data/facilities.json` ships pre-built with the full Massachusetts dataset
(~18,000 facilities: fields, courts, gyms, pools, rinks, etc.) pulled live
from OpenStreetMap via the Overpass API — no PBF download required. Unnamed
generic nodes (mostly private backyard pools/playgrounds) are filtered out;
unnamed pitches/courts/tracks/stadiums are kept, since those are real shared
facilities that just aren't individually named on OSM.

To refresh it (e.g. after OSM data changes):

```bash
python -m ingestion.overpass_ingest
python scripts/validate_data.py
```

Alternatively, if you have the Massachusetts `.osm.pbf` extract (e.g. from
Geofabrik) and prefer the fully offline/repeatable PRD-specified pipeline:

```bash
scripts/build_data.sh path/to/massachusetts.osm.pbf
```

This requires the optional ingestion dependencies (`pip install -r
requirements-ingestion.txt`, includes `osmium`) — not needed to just run the
web service. `scripts/validate_data.py` checks the resulting file against
the expected schema. `scripts/seed_data.py` regenerates the original ~30-row
curated fallback if you ever want a lightweight dataset instead.

Search results are capped at 500 (nearest first) and the map clusters
markers, since a large radius in a dense area can otherwise return/render
thousands of points.

## Map

The map surface is an iframe (`public/map-frame/index.html`) that embeds
Leaflet with OpenStreetMap tiles — no API key required. `src/components/MapFrame.jsx`
owns the iframe and exchanges `SET_RESULTS` / `MARKER_SELECTED` postMessage
events with it, per the contract in the PRD (section 16).

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Deployment (Render)

This repo includes a `render.yaml` for one Render web service that builds
the frontend and serves it from the same FastAPI process:

- Build: `npm install && npm run build && pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/health`

Steps:

1. Push this repo to GitHub.
2. In Render, "New +" → "Blueprint", point it at the repo — it will read
   `render.yaml` automatically. Or create a Web Service manually with the
   build/start commands above.
3. Set the `AI_API_KEY` environment variable in the Render dashboard (kept
   out of `render.yaml` since it's a secret). `AI_PROVIDER`/`AI_MODEL`
   default to `openai` / `gpt-4o-mini` — change if you use a different
   OpenAI-compatible provider.
4. Deploy. Render free-tier services spin down after inactivity, so the
   first request after idle time may be slow (cold start).

Without an `AI_API_KEY` configured, access classification still works via
the deterministic rule-based fallback (`app/services/access_classifier.py`)
— the app never breaks for lack of an AI key, it just loses AI-derived
evidence text.

## Environment variables

See `.env.example`. Backend variables are read via `python-dotenv`;
frontend variables must be prefixed `VITE_` to be exposed to the browser
(the AI key is never one of them — it only ever lives in the backend).
