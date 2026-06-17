# User Registration App

A small full-stack demo with two separate, containerized applications plus a database:

- **Frontend**: plain HTML/CSS/JS, served by nginx. A simple form asking for a username and age.
- **Backend**: FastAPI service that validates submissions and stores them.
- **Database**: SQLite file, persisted via a Docker volume.

## Validation rule

A submission is accepted **only if**:
1. The username does **not already exist** in the database, **and**
2. The age is **strictly greater than 18**.

If accepted, the username and age are saved to the database. Otherwise, nothing is saved and the user sees why it failed (username taken, or age too low).

## Project structure

```
user-registration-app/
├── backend/
│   ├── main.py            # FastAPI app + SQLite logic
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── app.js
│   ├── config.js          # placeholder, overwritten at container start
│   ├── entrypoint.sh       # injects backend URL into config.js
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Running it

From the project root:

```bash
docker compose up --build
```

Then open:
- Frontend: http://localhost:8080
- Backend API docs (Swagger UI): http://localhost:8000/docs
- List stored users (debug helper): http://localhost:8000/api/users

To stop:

```bash
docker compose down
```

The SQLite database is stored in a named Docker volume (`backend-data`), so data persists across `docker compose down` / `up` cycles. To wipe all data:

```bash
docker compose down -v
```

## How the pieces talk to each other

- The **frontend container** serves static files via nginx on port 80 (mapped to host port 8080).
- The **backend container** runs FastAPI via uvicorn on port 8000 (mapped to host port 8000).
- The browser calls the backend directly at `http://localhost:8000`, configured via the `API_BASE_URL` environment variable in `docker-compose.yml`. This is injected into the frontend container at startup (see `frontend/entrypoint.sh`), so you can point the same built frontend image at a different backend URL (e.g. in a real deployment) without rebuilding it.
- CORS is enabled on the backend so the browser (running on a different origin/port) is allowed to call it.

## Running without Docker (optional, for local development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
DB_PATH=./app.db uvicorn main:app --reload --port 8000
```

**Frontend:**
Just open `frontend/index.html` directly in a browser, or serve it with any static file server. It will default to calling `http://localhost:8000`.

## API reference

### `POST /api/register`
Request body:
```json
{ "username": "jane_doe", "age": 25 }
```
Response:
```json
{ "success": true, "message": "Welcome, jane_doe! Registration successful." }
```

### `GET /api/users`
Returns the list of all stored users (for debugging/demo purposes).

### `GET /health`
Basic health check.
