"""
Utility: Hashing and security functions.
"""

import hashlib
import hmac
import secrets


import os

def sha256_hash(text: str) -> str:
    """SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    """
    Generate a secure random API key.
    Format: fw_live_<32 random hex chars>
    """
    return f"fw_live_{secrets.token_hex(32)}"


def hash_api_key(key: str) -> str:
    """Hash an API key for storage using HMAC-SHA256 (never store raw keys)."""
    pepper = os.getenv("API_KEY_PEPPER", "default_insecure_pepper")
    return hmac.new(
        pepper.encode("utf-8"),
        key.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def hash_prompt(prompt: str) -> str:
    """
    Hash a prompt for logging. NEVER store raw prompts.
    Uses SHA-256 for deterministic, irreversible hashing.
    """
    return sha256_hash(prompt)
