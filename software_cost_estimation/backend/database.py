"""
Database module – SQLite setup for users and estimation history.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")


def get_connection():
    """Return a new SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            email       TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estimations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            method      TEXT    NOT NULL,
            inputs      TEXT    NOT NULL,
            effort      REAL    NOT NULL,
            time        REAL    NOT NULL,
            cost        REAL    NOT NULL,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ── User helpers ────────────────────────────────────────────────

def create_user(username: str, email: str, hashed_password: str):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password),
        )
        conn.commit()
    finally:
        conn.close()


def get_user_by_email(email: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Estimation history helpers ──────────────────────────────────

def save_estimation(user_id: int, method: str, inputs: dict,
                    effort: float, time_val: float, cost: float):
    conn = get_connection()
    conn.execute(
        """INSERT INTO estimations
           (user_id, method, inputs, effort, time, cost)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, method, json.dumps(inputs), effort, time_val, cost),
    )
    conn.commit()
    conn.close()


def get_estimations(user_id: int, limit: int = 50):
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM estimations
           WHERE user_id = ?
           ORDER BY created_at DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
