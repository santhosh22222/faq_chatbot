"""
auth.py — Registration, login, password helpers, and Google OAuth.
"""

import os
import re
import urllib.parse

import bcrypt
import requests as http_requests
import streamlit as st

from database import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    find_or_create_google_user,
)

# ─────────────────────────────────────────────
# Google OAuth config  (set in .env)
# ─────────────────────────────────────────────

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID",     "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI",  "http://localhost:8501")

_GOOGLE_AUTH_ENDPOINT  = "https://accounts.google.com/o/oauth2/auth"
_GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL   = "https://www.googleapis.com/oauth2/v3/userinfo"


def google_is_configured() -> bool:
    """True when both GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set."""
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def get_google_auth_url() -> str:
    """Return the Google OAuth 2.0 authorisation URL."""
    params = {
        "client_id":     GOOGLE_CLIENT_ID,
        "redirect_uri":  GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return _GOOGLE_AUTH_ENDPOINT + "?" + urllib.parse.urlencode(params)


def exchange_code_for_user(code: str) -> tuple[bool, str, dict | None]:
    """
    Exchange the Google authorisation *code* for tokens, fetch the user's
    profile, then find-or-create the local account.

    Returns (success, message, user_dict_or_None).
    """
    try:
        # Step 1 — exchange code for access token
        token_resp = http_requests.post(
            _GOOGLE_TOKEN_ENDPOINT,
            data={
                "code":          code,
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri":  GOOGLE_REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
            timeout=10,
        )
        token_data = token_resp.json()

        if "access_token" not in token_data:
            err = token_data.get("error_description") or token_data.get("error", "unknown")
            return False, f"Google sign-in failed: {err}", None

        # Step 2 — fetch profile
        userinfo_resp = http_requests.get(
            _GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
            timeout=10,
        )
        info = userinfo_resp.json()

        google_id = info.get("sub", "")
        email     = info.get("email", "")
        full_name = info.get("name", "")

        if not google_id:
            return False, "Could not retrieve your Google account info.", None

        # Step 3 — find or create local user
        user_row = find_or_create_google_user(google_id, email, full_name)
        if user_row is None:
            return False, "Failed to create account — please try again.", None

        return True, f"Welcome, {full_name or email}!", dict(user_row)

    except Exception as exc:
        return False, f"Google sign-in error: {exc}", None


# ─────────────────────────────────────────────
# Password utilities
# ─────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ─────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────

def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))


def _valid_username(username: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_]{3,20}$", username))


def _strong_password(pw: str) -> tuple[bool, str]:
    if len(pw) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", pw):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"\d", pw):
        return False, "Password must contain at least one digit."
    return True, ""


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def register_user(
    full_name: str, username: str, email: str, password: str, confirm: str
) -> tuple[bool, str]:
    """Validate and create a new user. Returns (success, message)."""
    if not full_name.strip():
        return False, "Full name is required."
    if not _valid_username(username):
        return False, "Username must be 3–20 characters (letters, digits, underscores)."
    if not _valid_email(email):
        return False, "Please enter a valid e-mail address."
    ok, msg = _strong_password(password)
    if not ok:
        return False, msg
    if password != confirm:
        return False, "Passwords do not match."

    if get_user_by_username(username):
        return False, f"Username '{username}' is already taken."
    if get_user_by_email(email):
        return False, f"An account with '{email}' already exists."

    uid = create_user(username, email, hash_password(password), full_name)
    if uid is None:
        return False, "Registration failed — please try again."
    return True, "Account created successfully! Please log in."


def login_user(
    username_or_email: str, password: str
) -> tuple[bool, str, dict | None]:
    """
    Authenticate by username OR email.
    Returns (success, message, user_dict_or_None).
    """
    identifier = username_or_email.strip().lower()
    user = get_user_by_username(identifier) or get_user_by_email(identifier)

    if not user:
        return False, "Account not found. Check your username / e-mail.", None

    # Google-only account — no local password set
    if user["password_hash"] == "GOOGLE_OAUTH":
        return (
            False,
            "This account uses Google Sign-In. Please click 'Sign in with Google'.",
            None,
        )

    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password.", None

    return True, f"Welcome back, {user['full_name'] or user['username']}!", dict(user)


# ─────────────────────────────────────────────
# Session-state helpers
# ─────────────────────────────────────────────

def set_session(user: dict) -> None:
    st.session_state.authenticated = True
    st.session_state.user = user


def logout() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)
