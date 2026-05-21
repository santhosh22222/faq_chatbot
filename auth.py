"""
auth.py — Registration, login, and password-hashing helpers using bcrypt.
"""

import re
import bcrypt
import streamlit as st

from database import (
    create_user,
    get_user_by_username,
    get_user_by_email,
)


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

def register_user(full_name: str, username: str, email: str, password: str, confirm: str) -> tuple[bool, str]:
    """
    Validate and create a new user.
    Returns (success, message).
    """
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

    # Check duplicates
    if get_user_by_username(username):
        return False, f"Username '{username}' is already taken."
    if get_user_by_email(email):
        return False, f"An account with '{email}' already exists."

    uid = create_user(username, email, hash_password(password), full_name)
    if uid is None:
        return False, "Registration failed — please try again."
    return True, "Account created successfully! Please log in."


def login_user(username_or_email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Authenticate by username OR email.
    Returns (success, message, user_dict_or_None).
    """
    identifier = username_or_email.strip().lower()
    user = get_user_by_username(identifier) or get_user_by_email(identifier)

    if not user:
        return False, "Account not found. Check your username / e-mail.", None
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password.", None

    user_dict = dict(user)
    return True, f"Welcome back, {user['full_name'] or user['username']}!", user_dict


# ─────────────────────────────────────────────
# Session-state helpers
# ─────────────────────────────────────────────

def set_session(user: dict) -> None:
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.theme = user.get("theme", "dark")


def logout() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)
