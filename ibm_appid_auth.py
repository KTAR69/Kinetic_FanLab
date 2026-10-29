"""
==============================================================================
Kinetic FanLab — IBM App ID Authentication Stub
Week 7 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Provides OAuth2 / IBMid single sign-on for the Streamlit Cloud tester URL,
replacing custom password management in registered_fans.json with a governed
IBM Cloud identity layer.

Architecture:
  1. Redirects unauthenticated users to the IBM App ID authorization endpoint
  2. Exchanges the authorization code for tokens at the IBM App ID token endpoint
  3. Maps the IBMid subject claim to a Kinetic FanLab fan handle/hash
  4. Falls back silently (returns None) when App ID credentials are not configured,
     preserving the existing registered_fans.json login path for local dev

IBM Resource: IBM App ID
  Console:  https://cloud.ibm.com/catalog/services/app-id
  Docs:     https://cloud.ibm.com/docs/appid

Setup (Streamlit Cloud secrets.toml):
  APPID_TENANT_ID    = "your-app-id-tenant-id"
  APPID_CLIENT_ID    = "your-app-id-client-id"
  APPID_CLIENT_SECRET = "your-app-id-client-secret"
  APPID_REGION       = "us-south"   # or eu-de, etc.
  APPID_REDIRECT_URI = "https://your-streamlit-app.streamlit.app/oauth/callback"
==============================================================================
"""

import os
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def _secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.getenv(key, default)


# IBM App ID credentials (all optional — module degrades gracefully when absent)
APPID_TENANT_ID = _secret("APPID_TENANT_ID")
APPID_CLIENT_ID = _secret("APPID_CLIENT_ID")
APPID_CLIENT_SECRET = _secret("APPID_CLIENT_SECRET")
APPID_REGION = _secret("APPID_REGION", "us-south")
APPID_REDIRECT_URI = _secret("APPID_REDIRECT_URI", "")

_APPID_BASE = f"https://{APPID_REGION}.appid.cloud.ibm.com/oauth/v4/{APPID_TENANT_ID}"

APPID_CONFIGURED = bool(APPID_TENANT_ID and APPID_CLIENT_ID and APPID_CLIENT_SECRET)


def is_appid_enabled() -> bool:
    """Returns True when all required IBM App ID credentials are present."""
    return APPID_CONFIGURED


def get_authorization_url(state: str = "") -> Optional[str]:
    """
    Builds the IBM App ID OAuth2 authorization URL to redirect the user to.
    Returns None when App ID is not configured.
    """
    if not APPID_CONFIGURED:
        return None
    import urllib.parse
    params = {
        "response_type": "code",
        "client_id": APPID_CLIENT_ID,
        "redirect_uri": APPID_REDIRECT_URI,
        "scope": "openid profile email",
        "state": state or str(int(time.time())),
    }
    return f"{_APPID_BASE}/authorization?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """
    Exchanges an OAuth2 authorization code for an IBM App ID access + ID token.
    Returns the token response dict, or None on failure.
    """
    if not APPID_CONFIGURED:
        return None
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        resp = requests.post(
            f"{_APPID_BASE}/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": APPID_REDIRECT_URI,
            },
            auth=HTTPBasicAuth(APPID_CLIENT_ID, APPID_CLIENT_SECRET),
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def decode_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes the IBM App ID ID token (JWT) without signature verification.
    For production, verify with the App ID JWKS endpoint.
    Returns the claims dict, or None on failure.
    """
    try:
        import base64, json as _json
        parts = id_token.split(".")
        if len(parts) < 2:
            return None
        padding = "=" * (4 - len(parts[1]) % 4)
        payload = base64.urlsafe_b64decode(parts[1] + padding)
        return _json.loads(payload)
    except Exception:
        return None


def map_appid_claims_to_fan_identity(claims: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps IBM App ID / IBMid JWT claims to a Kinetic FanLab fan identity dict
    compatible with the session state keys set by the existing login flow.

    Returns a partial fan-identity dict; caller merges into session state.
    """
    import hashlib
    email = claims.get("email", claims.get("sub", "unknown@ibm.com"))
    name = claims.get("name", claims.get("given_name", "IBMid Fan"))
    handle = "@" + email.split("@")[0].lower().replace(".", "_")[:20]
    # Deterministic passport hash from IBMid subject claim (stable across sessions)
    sub = claims.get("sub", email)
    passport_hash = "0xIBM-" + hashlib.sha256(sub.encode()).hexdigest()[:10]
    return {
        "member_name": name,
        "member_handle": handle,
        "member_email": email,
        "member_hash": passport_hash,
        "auth_provider": "IBM_APP_ID",
    }


def render_appid_login_button() -> None:
    """
    Renders an IBM App ID SSO login button in the Streamlit UI.
    Only renders when App ID is configured; no-ops silently otherwise.
    """
    if not APPID_CONFIGURED:
        return
    try:
        import streamlit as st
        auth_url = get_authorization_url()
        if auth_url:
            st.markdown(
                f"""<a href="{auth_url}" target="_self"
                    style="display:inline-block;padding:8px 18px;background:#0f62fe;
                           color:#fff;border-radius:4px;text-decoration:none;
                           font-weight:600;font-size:13px;">
                    🔐 Sign in with IBMid (App ID)
                </a>""",
                unsafe_allow_html=True,
            )
    except Exception:
        pass


def handle_oauth_callback() -> Optional[Dict[str, Any]]:
    """
    Checks st.query_params for an OAuth2 callback code and exchanges it.
    Returns fan-identity dict if successful, None otherwise.
    Call this once at the top of app.py (before any screen renders).
    """
    if not APPID_CONFIGURED:
        return None
    try:
        import streamlit as st
        params = st.query_params
        code = params.get("code")
        if not code:
            return None
        token_resp = exchange_code_for_token(code)
        if not token_resp:
            return None
        id_token = token_resp.get("id_token")
        if not id_token:
            return None
        claims = decode_id_token(id_token)
        if not claims:
            return None
        # Clear the OAuth code from the URL to prevent re-processing on rerun
        st.query_params.clear()
        return map_appid_claims_to_fan_identity(claims)
    except Exception:
        return None
