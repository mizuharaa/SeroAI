"""
Simple SQLite-backed user store for local + Google-authenticated users.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, Optional, TypedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "users.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class UserPublic(TypedDict):
    id: int
    email: str
    name: str
    picture: Optional[str]
    provider: str


_INIT_LOCK = threading.Lock()
_INITIALIZED = False


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _initialize():
    global _INITIALIZED  # pylint: disable=global-statement
    if _INITIALIZED:
        return
    with _INIT_LOCK:
        if _INITIALIZED:
            return
        with _get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    google_sub TEXT UNIQUE,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    picture TEXT,
                    password_hash TEXT,
                    auth_provider TEXT DEFAULT 'local',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        _INITIALIZED = True


def _row_to_user(row: sqlite3.Row) -> UserPublic:
    return {
        "id": int(row["id"]),
        "email": row["email"],
        "name": row["name"] or row["email"],
        "picture": row["picture"],
        "provider": row["auth_provider"] or ("google" if row["google_sub"] else "local"),
    }


def upsert_google_user(sub: str, email: str, name: str, picture: Optional[str]) -> UserPublic:
    _initialize()
    with _get_conn() as conn:
        existing = conn.execute("SELECT id, google_sub FROM users WHERE email = ?", (email,)).fetchone()
        if existing and not existing["google_sub"]:
            conn.execute(
                """
                UPDATE users
                SET google_sub = ?, name = ?, picture = ?, auth_provider = 'google', last_login = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (sub, name, picture, existing["id"]),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (existing["id"],)).fetchone()
            return _row_to_user(row)
        conn.execute(
            """
            INSERT INTO users (google_sub, email, name, picture, auth_provider)
            VALUES (?, ?, ?, ?, 'google')
            ON CONFLICT(google_sub) DO UPDATE SET
                email=excluded.email,
                name=excluded.name,
                picture=excluded.picture,
                auth_provider='google',
                last_login=CURRENT_TIMESTAMP
            """,
            (sub, email, name, picture),
        )
        row = conn.execute("SELECT * FROM users WHERE google_sub = ?", (sub,)).fetchone()
    if row is None:
        raise RuntimeError("Failed to upsert google user")
    return _row_to_user(row)


def create_local_user(email: str, password_hash: str, name: Optional[str]) -> UserPublic:
    _initialize()
    with _get_conn() as conn:
        try:
            conn.execute(
                """
                INSERT INTO users (email, name, password_hash, auth_provider)
                VALUES (?, ?, ?, 'local')
                """,
                (email, name or email, password_hash),
            )
        except sqlite3.IntegrityError as exc:  # type: ignore[attr-defined]
            raise ValueError("Email already registered") from exc
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        raise RuntimeError("Failed to create user")
    return _row_to_user(row)


def get_user_by_email(email: str) -> Optional[UserPublic]:
    _initialize()
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return _row_to_user(row) if row else None


def get_user_credentials(email: str) -> Optional[sqlite3.Row]:
    _initialize()
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return row


def get_user_by_id(user_id: int) -> Optional[UserPublic]:
    _initialize()
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return _row_to_user(row) if row else None


def mark_login(user_id: int) -> None:
    _initialize()
    with _get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
        )


def email_exists(email: str) -> bool:
    _initialize()
    with _get_conn() as conn:
        row = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
    return row is not None

