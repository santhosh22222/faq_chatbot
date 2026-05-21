"""
database.py — SQLite layer for users, chat sessions, and messages.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")


# ─────────────────────────────────────────────
# Initialise
# ─────────────────────────────────────────────

def init_db() -> None:
    """Create tables if they don't already exist."""
    conn = _connect()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            full_name     TEXT    DEFAULT '',
            theme         TEXT    DEFAULT 'dark',
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS chat_sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL DEFAULT 'New Chat',
            domain     TEXT    NOT NULL DEFAULT 'general',
            created_at TEXT    DEFAULT (datetime('now')),
            updated_at TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role       TEXT    NOT NULL,   -- 'user' | 'assistant' | 'system'
            content    TEXT    NOT NULL,
            timestamp  TEXT    DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ─────────────────────────────────────────────
# User operations
# ─────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str, full_name: str = "") -> int | None:
    """Insert a new user. Returns the new user id, or None on conflict."""
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?,?,?,?)",
            (username.strip().lower(), email.strip().lower(), password_hash, full_name.strip()),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM users WHERE username = ?", (username.strip().lower(),)
    ).fetchone()
    conn.close()
    return row


def get_user_by_email(email: str) -> sqlite3.Row | None:
    conn = _connect()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
    ).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    conn = _connect()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def update_user_theme(user_id: int, theme: str) -> None:
    conn = _connect()
    conn.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user_id))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Chat session operations
# ─────────────────────────────────────────────

def create_session(user_id: int, domain: str, title: str = "New Chat") -> int:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_sessions (user_id, domain, title) VALUES (?,?,?)",
        (user_id, domain, title),
    )
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return session_id


def get_sessions(user_id: int) -> list[sqlite3.Row]:
    """Return all sessions for a user, newest first."""
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY updated_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def update_session_title(session_id: int, title: str) -> None:
    conn = _connect()
    conn.execute(
        "UPDATE chat_sessions SET title = ?, updated_at = datetime('now') WHERE id = ?",
        (title[:80], session_id),
    )
    conn.commit()
    conn.close()


def touch_session(session_id: int) -> None:
    conn = _connect()
    conn.execute(
        "UPDATE chat_sessions SET updated_at = datetime('now') WHERE id = ?",
        (session_id,),
    )
    conn.commit()
    conn.close()


def delete_session(session_id: int) -> None:
    conn = _connect()
    conn.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# Message operations
# ─────────────────────────────────────────────

def add_message(session_id: int, role: str, content: str) -> int:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?,?,?)",
        (session_id, role, content),
    )
    conn.commit()
    msg_id = cur.lastrowid
    conn.close()
    touch_session(session_id)
    return msg_id


def get_messages(session_id: int) -> list[sqlite3.Row]:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,),
    ).fetchall()
    conn.close()
    return rows


def count_user_messages(user_id: int) -> int:
    conn = _connect()
    count = conn.execute(
        """SELECT COUNT(*) FROM messages m
           JOIN chat_sessions s ON m.session_id = s.id
           WHERE s.user_id = ?""",
        (user_id,),
    ).fetchone()[0]
    conn.close()
    return count
