"""
FastAPI backend for the user registration app.

Rules:
 - A submission succeeds only if:
     1. The username does NOT already exist in the database, AND
     2. The age is strictly greater than 18.
 - On success, the user (username + age) is saved to the SQLite database.
 - On failure, nothing is saved; the API explains why it failed.
"""

import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

# The DB file lives in a mounted volume (see docker-compose.yml) so data
# persists across container restarts.
DB_PATH = os.environ.get("DB_PATH", "/data/app.db")


def init_db() -> None:
    """Create the users table if it doesn't already exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                age INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class UserSubmission(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=150)


class UserResponse(BaseModel):
    success: bool
    message: str


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="User Registration API")

# Allow the frontend (served from a different container/origin) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for a real deployment, restrict this to the frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/register", response_model=UserResponse)
def register_user(submission: UserSubmission) -> UserResponse:
    username = submission.username.strip()
    age = submission.age

    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty.")

    with get_db() as conn:
        existing = conn.execute(
            "SELECT 1 FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing is not None:
            return UserResponse(
                success=False,
                message=f"Username '{username}' is already taken.",
            )

        if age <= 18:
            return UserResponse(
                success=False,
                message="Age must be greater than 18.",
            )

        conn.execute(
            "INSERT INTO users (username, age) VALUES (?, ?)",
            (username, age),
        )
        conn.commit()

    return UserResponse(
        success=True,
        message=f"Welcome, {username}! Registration successful.",
    )


@app.get("/api/users")
def list_users() -> list[dict]:
    """Helper endpoint to inspect stored users (useful for debugging/demo)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT username, age, created_at FROM users ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]
