"""
groq_client.py — Thin wrapper around the Groq SDK.

Supports:
  • Streaming chat completions (used in the chat interface)
  • Non-streaming completions (used for FAQ generation & title inference)

Models last verified working — May 2026.
Mixtral 8x7B was decommissioned by Groq; removed here.
"""

import os
from typing import Generator

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Model options ─────────────────────────────────────────────────────────────
AVAILABLE_MODELS: dict[str, str] = {
    "Llama 3.3 70B  ✦ Best quality":   "llama-3.3-70b-versatile",
    "Llama 3.1 70B  ✦ Balanced":       "llama-3.1-70b-versatile",
    "Llama 3.1 8B   ✦ Fastest":        "llama-3.1-8b-instant",
    "Gemma 2 9B     ✦ Compact":        "gemma2-9b-it",
}
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# ── Singleton client ──────────────────────────────────────────────────────────
_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add it to your .env file or set it as an environment variable."
            )
        _client = Groq(api_key=api_key)
    return _client


# ── Streaming chat ────────────────────────────────────────────────────────────

def stream_chat(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> Generator[str, None, None]:
    """
    Yields text chunks from a streaming Groq completion.
    Usage with Streamlit:
        response = st.write_stream(stream_chat(messages))
    """
    client = get_client()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ── Non-streaming (blocking) chat ─────────────────────────────────────────────

def chat(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Return the full assistant reply as a single string."""
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )
    return response.choices[0].message.content or ""


# ── Auto-title inference ──────────────────────────────────────────────────────

def infer_title(first_user_message: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Generate a short (≤6 words) chat title from the first user message.
    Falls back to a truncated version of the message if the call fails.
    """
    try:
        result = chat(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You create very short, descriptive chat titles (max 6 words). "
                        "Respond with ONLY the title — no quotes, no punctuation at the end."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Create a title for this chat: {first_user_message[:300]}",
                },
            ],
            model=model,
            temperature=0.3,
            max_tokens=20,
        )
        return result.strip().strip('"').strip("'")[:80]
    except Exception:
        return first_user_message[:60] + ("…" if len(first_user_message) > 60 else "")


# ── Health check ──────────────────────────────────────────────────────────────

def is_api_key_valid() -> bool:
    """Quick check that the API key works (uses the cheapest/fastest model)."""
    try:
        chat(
            messages=[{"role": "user", "content": "ping"}],
            model="llama-3.1-8b-instant",
            max_tokens=5,
        )
        return True
    except Exception:
        return False
