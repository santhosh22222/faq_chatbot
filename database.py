"""
database.py — MongoDB layer for FAQBot users, chat sessions, and messages.

Connection is configured via two environment variables:
  MONGODB_URI  — e.g. mongodb://localhost:27017  or a MongoDB Atlas SRV URI
  MONGODB_DB   — database name (default: faqbot)
"""

import os
import re
from datetime import datetime, timezone

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

load_dotenv()

_MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
_MONGODB_DB  = os.getenv("MONGODB_DB",  "faqbot")

# Module-level singleton client (thread-safe in pymongo)
_client: MongoClient | None = None


def _db():
    global _client
    if _client is None:
        _client = MongoClient(_MONGODB_URI)
    return _client[_MONGODB_DB]


def _doc(raw) -> dict | None:
    """Convert a MongoDB document to a plain dict with 'id' as a string."""
    if raw is None:
        return None
    d = dict(raw)
    d["id"] = str(d.pop("_id"))
    return d


# ─────────────────────────────────────────────
# Initialise  (create indexes)
# ─────────────────────────────────────────────

def init_db() -> None:
    """Ensure indexes exist.  Safe to call on every startup."""
    db = _db()

    # Users — unique on username and email; sparse on google_id
    db.users.create_index("username", unique=True)
    db.users.create_index("email",    unique=True)
    db.users.create_index("google_id", sparse=True)

    # Sessions — filter by user_id, sort by updated_at
    db.chat_sessions.create_index(
        [("user_id", ASCENDING), ("updated_at", DESCENDING)]
    )

    # Messages — filter by session_id, sort by timestamp
    db.messages.create_index(
        [("session_id", ASCENDING), ("timestamp", ASCENDING)]
    )


# ─────────────────────────────────────────────
# User operations
# ─────────────────────────────────────────────

def create_user(
    username: str,
    email: str,
    password_hash: str,
    full_name: str = "",
) -> str | None:
    """Insert a new user. Returns the new user id (str) or None on conflict."""
    try:
        result = _db().users.insert_one({
            "username":      username.strip().lower(),
            "email":         email.strip().lower(),
            "password_hash": password_hash,
            "full_name":     full_name.strip(),
            "theme":         "dark",
            "google_id":     None,
            "created_at":    datetime.now(timezone.utc),
        })
        return str(result.inserted_id)
    except DuplicateKeyError:
        return None


def get_user_by_username(username: str) -> dict | None:
    return _doc(_db().users.find_one({"username": username.strip().lower()}))


def get_user_by_email(email: str) -> dict | None:
    return _doc(_db().users.find_one({"email": email.strip().lower()}))


def get_user_by_id(user_id: str) -> dict | None:
    try:
        return _doc(_db().users.find_one({"_id": ObjectId(user_id)}))
    except Exception:
        return None


def update_user_theme(user_id: str, theme: str) -> None:
    _db().users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"theme": theme}},
    )


# ─────────────────────────────────────────────
# Google OAuth helpers
# ─────────────────────────────────────────────

def _unique_username(base: str) -> str:
    """Return a username derived from *base* that doesn't already exist."""
    slug = re.sub(r"[^\w]", "", base)[:15] or "user"
    candidate = slug
    n = 1
    while _db().users.find_one({"username": candidate}):
        candidate = f"{slug}{n}"
        n += 1
    return candidate


def find_or_create_google_user(
    google_id: str,
    email: str,
    full_name: str,
) -> dict | None:
    """
    Look up a user by google_id, fall back to email match (linking the account),
    or create a brand-new document.  Returns the user dict or None on failure.
    """
    db = _db()
    email = email.strip().lower()

    # 1. Exact google_id hit
    doc = db.users.find_one({"google_id": google_id})
    if doc:
        return _doc(doc)

    # 2. Existing account with same email → link google_id
    doc = db.users.find_one({"email": email})
    if doc:
        db.users.update_one(
            {"_id": doc["_id"]},
            {"$set": {"google_id": google_id}},
        )
        return _doc(db.users.find_one({"_id": doc["_id"]}))

    # 3. Create new user (sentinel marks Google-only accounts)
    try:
        result = db.users.insert_one({
            "username":      _unique_username(email.split("@")[0]),
            "email":         email,
            "password_hash": "GOOGLE_OAUTH",
            "full_name":     full_name.strip(),
            "theme":         "dark",
            "google_id":     google_id,
            "created_at":    datetime.now(timezone.utc),
        })
        return _doc(db.users.find_one({"_id": result.inserted_id}))
    except DuplicateKeyError:
        return None


# ─────────────────────────────────────────────
# Chat session operations
# ─────────────────────────────────────────────

def create_session(user_id: str, domain: str, title: str = "New Chat") -> str:
    now = datetime.now(timezone.utc)
    result = _db().chat_sessions.insert_one({
        "user_id":    user_id,
        "title":      title,
        "domain":     domain,
        "created_at": now,
        "updated_at": now,
    })
    return str(result.inserted_id)


def get_sessions(user_id: str) -> list[dict]:
    """Return all sessions for a user, newest first."""
    cursor = _db().chat_sessions.find(
        {"user_id": user_id}
    ).sort("updated_at", DESCENDING)
    return [_doc(d) for d in cursor]


def update_session_title(session_id: str, title: str) -> None:
    _db().chat_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {
            "title":      title[:80],
            "updated_at": datetime.now(timezone.utc),
        }},
    )


def touch_session(session_id: str) -> None:
    _db().chat_sessions.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"updated_at": datetime.now(timezone.utc)}},
    )


def delete_session(session_id: str) -> None:
    db = _db()
    db.messages.delete_many({"session_id": session_id})          # cascade
    db.chat_sessions.delete_one({"_id": ObjectId(session_id)})


# ─────────────────────────────────────────────
# Message operations
# ─────────────────────────────────────────────

def add_message(session_id: str, role: str, content: str) -> str:
    result = _db().messages.insert_one({
        "session_id": session_id,
        "role":       role,
        "content":    content,
        "timestamp":  datetime.now(timezone.utc),
    })
    touch_session(session_id)
    return str(result.inserted_id)


def get_messages(session_id: str) -> list[dict]:
    cursor = _db().messages.find(
        {"session_id": session_id}
    ).sort("timestamp", ASCENDING)
    return [_doc(d) for d in cursor]


def count_user_messages(user_id: str) -> int:
    session_ids = [
        str(s["_id"])
        for s in _db().chat_sessions.find({"user_id": user_id}, {"_id": 1})
    ]
    if not session_ids:
        return 0
    return _db().messages.count_documents({"session_id": {"$in": session_ids}})
