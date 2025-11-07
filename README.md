# NAYA – Modern Travel Journal

NAYA is a social travel journal that mixes a secure Flask API with a polished static web client. Travellers can record places, rate experiences, publish stories, upload galleries, like & comment on reviews, and showcase public profiles.

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Requirements](#requirements)
6. [Installation Options](#installation-options)
7. [Configuration](#configuration)
8. [Important Folders](#important-folders)
9. [Running the Apps](#running-the-apps)
10. [Core API](#core-api)
11. [Testing](#testing)
12. [Contribution Guidelines](#contribution-guidelines)

## Overview

NAYA ships with:
- a REST API under `/api/v1` built with Flask, SQLAlchemy, JWT, and service/repository layers for clean business logic;
- a responsive HTML/CSS/JS front-end that consumes the API, offers a feed, a map view, profile management, and a theme switcher;
- a SQLite database for development (drop-in PostgreSQL support for production) plus Pytest coverage for major scenarios.

## Key Features

**Traveller Experience**
- Sign up/login, profile editing, avatars, stats, and public profile sharing.
- Places and detailed reviews (rating, visit date, descriptions) with optional photo galleries.
- Real-time-like feed, search, map discovery, likes, comments, and the ability to view other explorers.

**API & Services**
- JWT access + refresh tokens with automatic refresh logic in the front-end.
- Dedicated services (auth, places, reviews, photos) backed by repositories to isolate persistence.
- File uploads with extension whitelisting and storage in `Backend/uploads`.

**Dev & Ops**
- Configurable environments (`config.py`) and automatic admin provisioning when default admin credentials are present.
- CORS enabled by default, structured logging, and schema checks that keep SQLite aligned with model requirements.
- Ready-to-run Pytest suite and simple static hosting for the front-end.

## Architecture

```
Naya/
├── Backend/
│   ├── app/
│   │   ├── api/v1/            # Flask blueprints (auth, places, reviews, photos)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # Data access layer
│   │   └── services/          # Business logic
│   ├── instance/              # SQLite dev database (naya_dev.db)
│   ├── uploads/               # Local file storage (created on demand)
│   ├── config.py
│   └── run.py
├── Frontend/
│   ├── index.html             # Static SPA shell
│   ├── css/
│   └── js/
└── README.md
```

The front-end stores the API base URL in `localStorage` (button in the UI) and talks to the Flask API through `fetch`. Uploaded files are served from the backend via configured routes.

## Tech Stack
- **Backend:** Python 3.11+, Flask 2.3, SQLAlchemy 2.x, Flask-JWT-Extended, Flask-CORS.
- **Database:** SQLite (dev) with optional PostgreSQL in production.
- **Frontend:** HTML5, modern CSS, vanilla JS modules.
- **Testing:** Pytest + pytest-cov for auth, reviews, places, and photos.

## Requirements
- Python ≥ 3.11
- Pip (or Pipenv/Poetry if preferred)
- SQLite already bundled with Python
- Optional: PostgreSQL server, Docker, or a reverse proxy for production deployments

## Installation Options

Pick the workflow that fits your tooling:

1. **Virtualenv (classic)**
   ```bash
   git clone <repo-url> naya && cd naya
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r Backend/requirements.txt
   ```

2. **Pipenv/Poetry**
   ```bash
   pip install pipenv          # or: pipx install pipenv
   pipenv install -r Backend/requirements.txt
   pipenv shell
   ```
   With Poetry, create a `pyproject.toml` and run `poetry add $(cat Backend/requirements.txt)`.

3. **System Python / --user install**
   ```bash
   pip install --user -r Backend/requirements.txt
   export PATH="$HOME/.local/bin:$PATH"
   ```

4. **Containerized**
   - Build a simple Docker image from `Backend/run.py` (copy app, install requirements, expose `5000`).
   - Serve the `Frontend/` folder with NGINX or any static file server.

## Configuration

1. Copy `Backend/.env.example` to `Backend/.env` (create the example file if it does not exist yet).
2. Update the most important variables:

| Variable | Description | Dev default |
| --- | --- | --- |
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_APP` | Entry point | `run.py` |
| `FLASK_DEBUG` | Enable debug | `True` |
| `FLASK_HOST` / `FLASK_PORT` | Bind address | `127.0.0.1` / `5000` |
| `DEV_DATABASE_URL` | Dev DB | `sqlite:///instance/naya_dev.db` |
| `DATABASE_URL` | Prod DB | `postgresql://user:pass@host/db` |
| `SECRET_KEY` / `JWT_SECRET_KEY` | Secrets | set strong values |
| `UPLOAD_FOLDER` | Local storage | `uploads` |
| `ADMIN_EMAILS` | Approved admins | `admin@naya.app` |
| `ADMIN_DEFAULT_EMAIL` | Auto-provisioned admin | `admin@naya.app` |
| `ADMIN_DEFAULT_PASSWORD` | Password for the admin | `ChangeMe123!` |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:4173` |
| `GOOGLE_MAPS_API_KEY` | Optional maps key | blank |

Example `.env`:
```
FLASK_ENV=development
FLASK_APP=run.py
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
DEV_DATABASE_URL=sqlite:///instance/naya_dev.db
SECRET_KEY=replace-me
JWT_SECRET_KEY=replace-me
UPLOAD_FOLDER=uploads
ADMIN_DEFAULT_EMAIL=admin@naya.app
ADMIN_DEFAULT_PASSWORD=ChangeMe123!
```

Ensure `Backend/uploads` (and subfolders like `avatars`) exist or let the service create them on demand.

## Important Folders
- `Backend/app/models/` – user/place/review/photo models and mixins.
- `Backend/app/services/` – AuthService, ReviewService, PlaceService, PhotoService, etc.
- `Backend/app/api/v1/` – REST blueprints, error handling, JWT guards.
- `Backend/tests/` – Pytest suites (`test_auth.py`, `test_reviews.py`, etc.).
- `Frontend/js/*.js` – modules such as `api.js`, `core.js`, `reviews.js`.

## Running the Apps

### Backend API
```bash
cd Backend
export $(grep -v '^#' .env | xargs)    # Windows PowerShell: Get-Content .env | foreach { if ($_ -and $_ -notmatch '^#') { $name,$value = $_ -split '=',2; set-item -path env:$name -value $value } }
python run.py
```
The API listens on `http://127.0.0.1:5000` and exposes `/api/v1/*`.

### Frontend
Open `Frontend/index.html` directly or serve the directory:
```bash
cd Frontend
python -m http.server 4173
```
Use the “API” indicator button in the UI to verify the base URL (defaults to `http://127.0.0.1:5000/api/v1`).

### Default Admin
If both `ADMIN_DEFAULT_EMAIL` and `ADMIN_DEFAULT_PASSWORD` are set, the backend will provision (or update) the admin on startup. Check the server logs to confirm creation.

## Core API

| Resource | Endpoints |
| --- | --- |
| **Auth** | `POST /auth/register`, `POST /auth/login`, `GET/PUT /auth/profile`, `PUT /auth/change-password`, `PUT /auth/avatar`, `PUT /auth/deactivate`, `GET /auth/stats`, `GET /auth/users/<id>`, `POST /auth/refresh` |
| **Places** | `GET /places?search=&country=&city=`, `POST /places`, `GET/PUT/DELETE /places/<id>`, `GET /places/<id>/reviews`, `GET /places/search`, `GET /places/nearby` |
| **Reviews** | `GET /reviews` (filters `user_id`, `place_id`, `search`), `POST /reviews`, `GET/PUT/DELETE /reviews/<id>`, `GET/POST/DELETE /reviews/<id>/likes`, `GET/POST/DELETE /reviews/<id>/comments`, `GET /reviews/statistics/<place_id>` |
| **Photos** | `POST /photos` (multipart), `GET /photos/<id>`, `PUT /photos/<id>`, `DELETE /photos/<id>`, `GET /photos/user/<user_id>` |

All responses follow the `{success: bool, data|error}` convention and protected routes rely on `@jwt_required`.

## Testing

```bash
cd Backend
pytest
pytest -q tests/test_reviews.py
pytest --cov=app --cov-report=term-missing
```

Tests run against the in-memory SQLite DB provided by `TestingConfig`, so they are safe for local data. Extend `Backend/tests/` with new cases and fixtures when adding features.

## Contribution Guidelines
- Activate a virtual environment, Pipenv shell, Poetry shell, or rely on system installs—choose what best suits your workflow, but keep dependencies isolated when possible.
- Keep business logic inside services/repositories and avoid bloating blueprints.
- Add tests for every noteworthy bug fix or feature.
- Before pushing: run `pytest`, check formatting (add Ruff/Flake8 if you need linting), and spot-check the front-end.
- For production, prefer PostgreSQL, store uploads on S3/GCS (or similar), place the API behind NGINX/Traefik with HTTPS, and keep secrets in your orchestration layer.

---

AUTHOR: Nawfel & Yassine
