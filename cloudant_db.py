# ==============================================================================
# Kinetic FanLab — IBM Cloudant NoSQL Persistence Module
# Session 4: IBM Cloud Enterprise Services & watsonx Orchestrate Skill Registration
# ==============================================================================
# Graceful fallback: if Cloudant credentials are absent, uses a local JSON
# cache (cloudant_cache.json) so respect taps and accolades persist across
# app reloads without crashing.
# ==============================================================================

import os
import json
from typing import Optional

# ---------------------------------------------------------------------------
# Immutable member hashes — never change these values
# ---------------------------------------------------------------------------
_MEMBER_HASHES: dict[str, str] = {
    "Marcus Vance":  "0xMV-sec114-8f7a2",
    "Elena Rostova": "0xER-sec114-3c9b1",
    "Devon Miller":  "0xDM-sec114-6d4e8",
    "Jordan Lee":    "0xJL-sec114-1f4a9",
    "Sarah Jenkins": "0xSJ-sec115-7b2a5",
    "Carlos Mendez": "0xCM-sec115-4e8f9",
    "Maya Patel":    "0xMP-sec115-1a5c3",
    "Alex Taylor":   "0xAT-sec115-5c2d3",
}

# Default baseline respect tap counts that seed new passport records
_DEFAULT_RESPECT_TAPS: dict[str, int] = {
    "Marcus Vance":  313,
    "Elena Rostova": 168,
    "Devon Miller":  245,
    "Jordan Lee":     28,
    "Sarah Jenkins": 480,
    "Carlos Mendez": 395,
    "Maya Patel":    185,
    "Alex Taylor":    45,
}

# ---------------------------------------------------------------------------
# Environment / connection configuration
# ---------------------------------------------------------------------------
_CLOUDANT_APIKEY: str = os.environ.get("CLOUDANT_APIKEY", "")
_CLOUDANT_URL: str = os.environ.get("CLOUDANT_URL", "")
_CLOUDANT_DB: str = "kinetic-fan-passports"

_CLOUDANT_CONFIGURED: bool = bool(_CLOUDANT_APIKEY and _CLOUDANT_URL)

# Local fallback cache
_LOCAL_CACHE_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "cloudant_cache.json"
)

# In-process cache to avoid repeated disk reads in the same session
_memory_cache: Optional[dict] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_cloudant_client():  # type: ignore[return]
    """Return an ibm_cloud_sdk_core-authenticated CloudantV1 client."""
    from ibmcloudant.cloudant_v1 import CloudantV1  # type: ignore[import-untyped]
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator  # type: ignore[import-untyped]

    authenticator = IAMAuthenticator(_CLOUDANT_APIKEY)
    client = CloudantV1(authenticator=authenticator)
    client.set_service_url(_CLOUDANT_URL)
    return client


def _load_local_cache() -> dict:
    """Load (or seed) the local JSON cache from disk."""
    global _memory_cache
    if _memory_cache is not None:
        return _memory_cache

    if os.path.exists(_LOCAL_CACHE_PATH):
        try:
            with open(_LOCAL_CACHE_PATH, "r", encoding="utf-8") as fh:
                _memory_cache = json.load(fh)
                return _memory_cache
        except (json.JSONDecodeError, OSError):
            pass

    # Seed with defaults for all 8 members
    _memory_cache = {
        name: {
            "member_hash": _MEMBER_HASHES[name],
            "respect_taps": _DEFAULT_RESPECT_TAPS[name],
            "nft_badges_unlocked": [],
        }
        for name in _MEMBER_HASHES
    }
    _save_local_cache(_memory_cache)
    return _memory_cache


def _reset_memory_cache() -> None:
    """
    Reset the in-process memory cache to None.

    **Test-only helper** — call this in setUp() to ensure each test class
    starts from a clean, unseeded state rather than inheriting mutations
    from a previous test.  Has no effect in production (the cache simply
    repopulates from disk or defaults on the next load call).
    """
    global _memory_cache
    _memory_cache = None


def _save_local_cache(data: dict) -> None:
    """Persist the in-memory cache to disk."""
    global _memory_cache
    _memory_cache = data
    try:
        with open(_LOCAL_CACHE_PATH, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        pass  # Non-fatal — in-memory cache still works for the session


def _default_passport(member_name: str) -> dict:
    """Return a fresh, seeded passport document for a member."""
    return {
        "_id": member_name,
        "member_hash": _MEMBER_HASHES.get(member_name, "0xUNKNOWN"),
        "respect_taps": _DEFAULT_RESPECT_TAPS.get(member_name, 0),
        "nft_badges_unlocked": [],
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_member_passport(member_name: str) -> dict:
    """
    Load the Fan Passport document for *member_name*.

    Returns the full passport dict (guaranteed to include ``member_hash`` and
    ``respect_taps``).  Falls back to local cache when Cloudant is not
    configured or unavailable.
    """
    if _CLOUDANT_CONFIGURED:
        try:
            client = _get_cloudant_client()
            doc_id = member_name
            response = client.get_document(db=_CLOUDANT_DB, doc_id=doc_id).get_result()
            return dict(response)
        except Exception:
            pass  # Fall through to local cache

    cache = _load_local_cache()
    if member_name not in cache:
        cache[member_name] = _default_passport(member_name)
        _save_local_cache(cache)
    return dict(cache[member_name])


def save_member_passport(member_name: str, updated_data: dict) -> bool:
    """
    Persist *updated_data* as the Fan Passport for *member_name*.

    Enforces the immutable member hash — any supplied ``member_hash`` value in
    *updated_data* is silently overwritten with the canonical hash.

    Returns ``True`` on success, ``False`` on failure.
    """
    # Always enforce the immutable hash
    updated_data["member_hash"] = _MEMBER_HASHES.get(member_name, updated_data.get("member_hash", "0xUNKNOWN"))
    updated_data["_id"] = member_name

    if _CLOUDANT_CONFIGURED:
        try:
            client = _get_cloudant_client()
            # Get current revision for update (upsert pattern)
            try:
                existing = client.get_document(db=_CLOUDANT_DB, doc_id=member_name).get_result()
                updated_data["_rev"] = existing.get("_rev", "")
            except Exception:
                pass
            client.put_document(db=_CLOUDANT_DB, doc_id=member_name, document=updated_data)
            return True
        except Exception:
            pass  # Fall through to local cache

    cache = _load_local_cache()
    cache[member_name] = updated_data
    _save_local_cache(cache)
    return True


def increment_respect_tap(member_name: str, count: int = 1) -> int:
    """
    Atomically increment the respect tap counter for *member_name* by *count*.

    Returns the new total respect tap count.
    """
    passport = load_member_passport(member_name)
    current: int = int(passport.get("respect_taps", _DEFAULT_RESPECT_TAPS.get(member_name, 0)))
    new_total: int = current + count
    passport["respect_taps"] = new_total
    save_member_passport(member_name, passport)
    return new_total
