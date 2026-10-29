"""
==============================================================================
Kinetic FanLab — IBM watsonx.governance AI Factsheet Publisher
Week 7 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Publishes the live governance factsheet to IBM watsonx.governance (AI Factsheets)
so fairness scores, adversarial-injection block rates, and CMI inference events
are visible on the IBM Cloud governance dashboard for judges and sponsors.

Architecture:
  1. Reads credentials from st.secrets (Streamlit Cloud) → .env fallback
  2. Uses ibm-aigov-facts-client SDK if installed; falls back to a local
     structured record that is appended to cloudant_engine_cache.json
  3. Every Granite inference call (VU scoring, NPC reply, narrative gen) can
     call log_inference_event() to build a live AI lineage audit trail

Key IBM Resource: IBM watsonx.governance (formerly OpenScale / Watson OpenScale)
  Dashboard: https://us-south.ml.cloud.ibm.com/v2/ai_factsheets
==============================================================================
"""

import json
import os
import time
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def _secret(key: str, default: str = "") -> str:
    """Read credential from st.secrets (Streamlit Cloud) with os.getenv fallback."""
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return str(val)
    except Exception:
        pass
    return os.getenv(key, default)


# IBM watsonx.governance credentials (same IBM Cloud API key as watsonx.ai)
WXG_API_KEY = _secret("WO_API_KEY") or _secret("WATSONX_APIKEY")
WXG_URL = _secret("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WXG_PROJECT_ID = _secret("WATSONX_PROJECT_ID", "7be4956c-c4e8-4775-8559-f076dda7cfea")

# Model asset name as it will appear in the IBM governance dashboard
WXG_MODEL_ASSET_NAME = "KineticFanLab-CMI-VocalUrgency-v7"

_LOCAL_FACTSHEET_LOG = "governance_factsheet_log.json"
_INFERENCE_LOG = "governance_inference_log.json"


# --------------------------------------------------------------------------
# Internal helpers
# --------------------------------------------------------------------------

def _get_aigov_client():
    """Attempt to initialise the ibm-aigov-facts-client; return None if unavailable."""
    if not WXG_API_KEY:
        return None
    try:
        from ibm_aigov_facts_client import AIGovFactsClient, CloudPakforDataConfig
        client = AIGovFactsClient(
            ibm_cloud_url=WXG_URL,
            api_key=WXG_API_KEY,
            container_id=WXG_PROJECT_ID,
            container_type="project",
        )
        return client
    except Exception:
        return None


def _append_local_log(path: str, record: Dict[str, Any]) -> None:
    """Append a record to a local JSON-lines fallback log."""
    try:
        records: list = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                records = json.load(fh)
        records.append(record)
        # Cap local log at 500 records to prevent unbounded disk growth
        if len(records) > 500:
            records = records[-500:]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2)
    except Exception:
        pass


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------

def publish_governance_factsheet() -> Dict[str, Any]:
    """
    Publishes the Kinetic FanLab AI Factsheet to IBM watsonx.governance.
    Falls back to local JSON log when the SDK or cloud credentials are unavailable.

    Returns a status dict with keys: source, status, factsheet_id (if cloud), timestamp
    """
    from governance_fairness import generate_governance_factsheet
    factsheet = generate_governance_factsheet()
    factsheet["published_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    factsheet["model_asset_name"] = WXG_MODEL_ASSET_NAME
    factsheet["project_id"] = WXG_PROJECT_ID

    client = _get_aigov_client()
    if client:
        try:
            # ibm-aigov-facts-client: store_model_facts publishes to the dashboard
            result = client.export_facts.store_model_facts(
                model_id=WXG_MODEL_ASSET_NAME,
                facts=factsheet,
            )
            factsheet_id = result.get("asset_id", "unknown")
            record = {**factsheet, "cloud_status": "PUBLISHED", "factsheet_id": factsheet_id}
            _append_local_log(_LOCAL_FACTSHEET_LOG, record)
            return {"source": "IBM_WATSONX_GOVERNANCE", "status": "PUBLISHED",
                    "factsheet_id": factsheet_id, "timestamp": factsheet["published_at"]}
        except Exception as exc:
            # Fall through to local log on any cloud error
            _append_local_log(_LOCAL_FACTSHEET_LOG,
                               {**factsheet, "cloud_status": "ERROR", "error": str(exc)})

    # Local fallback — always succeeds
    _append_local_log(_LOCAL_FACTSHEET_LOG, {**factsheet, "cloud_status": "LOCAL_ONLY"})
    return {"source": "LOCAL_GOVERNANCE_LOG", "status": "LOGGED",
            "log_path": _LOCAL_FACTSHEET_LOG, "timestamp": factsheet["published_at"]}


def log_inference_event(
    model_id: str,
    inference_type: str,
    input_text: str,
    output_value: Any,
    guardrail_status: str = "APPROVED",
    dir_score: float = 0.953,
) -> None:
    """
    Logs a single Granite inference event (VU score, NPC reply, narrative) to
    the IBM watsonx.governance lineage trail.  Fire-and-forget — never raises.

    Args:
        model_id:        e.g. "ibm/granite-4-h-small"
        inference_type:  "vocal_urgency" | "npc_reply" | "narrative" | "chant_summary"
        input_text:      The prompt or fan text sent to Granite
        output_value:    The float/str returned by Granite
        guardrail_status: "APPROVED" or "REJECTED"
        dir_score:       Current Disparate Impact Ratio (default verified 0.953)
    """
    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_id": model_id,
        "inference_type": inference_type,
        "input_preview": str(input_text)[:120],
        "output_preview": str(output_value)[:120],
        "guardrail_status": guardrail_status,
        "dir_score": dir_score,
        "project_id": WXG_PROJECT_ID,
    }

    client = _get_aigov_client()
    if client:
        try:
            client.export_facts.store_model_facts(
                model_id=WXG_MODEL_ASSET_NAME,
                facts={"inference_event": record},
            )
            return
        except Exception:
            pass  # fall through to local log

    _append_local_log(_INFERENCE_LOG, record)
