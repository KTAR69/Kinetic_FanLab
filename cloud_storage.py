# ==============================================================================
# Kinetic FanLab — IBM Cloud Object Storage (COS) Module
# Session 4: IBM Cloud Enterprise Services & watsonx Orchestrate Skill Registration
# ==============================================================================
# Graceful fallback: if COS credentials are absent, archives locally to
# cloud_storage_archive/ and returns status: "ARCHIVED_LOCALLY (Simulated IBM COS)"
# ==============================================================================

import os
import json
import hashlib
import datetime

# Local archive directory used when COS credentials are not configured
_LOCAL_ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloud_storage_archive")

# Detect whether real COS credentials are present
_COS_APIKEY: str = os.environ.get("COS_APIKEY", "")
_COS_RESOURCE_CRN: str = os.environ.get("COS_RESOURCE_CRN", "")
_COS_ENDPOINT: str = os.environ.get("COS_ENDPOINT", "")
_COS_BUCKET: str = os.environ.get("COS_BUCKET", "kinetic-fanlab-archive")

_COS_CONFIGURED: bool = bool(_COS_APIKEY and _COS_RESOURCE_CRN and _COS_ENDPOINT)


def _cos_client():  # type: ignore[return]
    """Return an ibm_boto3 COS resource; only called when credentials are present."""
    import ibm_boto3  # type: ignore[import-untyped]
    from ibm_botocore.client import Config  # type: ignore[import-untyped]

    return ibm_boto3.resource(
        "s3",
        ibm_api_key_id=_COS_APIKEY,
        ibm_service_instance_id=_COS_RESOURCE_CRN,
        config=Config(signature_version="oauth"),
        endpoint_url=_COS_ENDPOINT,
    )


def _crypto_timestamp() -> str:
    """Return a deterministic, sortable ISO-8601 timestamp with a short SHA-256 suffix."""
    now = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
    digest = hashlib.sha256(now.encode()).hexdigest()[:8]
    return f"{now}#{digest}"


def _write_local(object_key: str, payload: dict) -> str:
    """Persist *payload* to the local archive folder and return the file path."""
    os.makedirs(_LOCAL_ARCHIVE_DIR, exist_ok=True)
    safe_key = object_key.replace("/", "_").replace(":", "-")
    file_path = os.path.join(_LOCAL_ARCHIVE_DIR, f"{safe_key}.json")
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return file_path


def archive_crowd_box_score(
    fixture_id: str,
    sport: str,
    cmi: float,
    surge: float,
    winning_section: str,
    fan_contribution: dict,
) -> dict:
    """
    Archive a verified post-game Crowd Box Score record.

    Returns a transaction receipt dict with keys:
      status, bucket, object_key, crypto_timestamp, [local_path]
    """
    crypto_ts = _crypto_timestamp()
    object_key = f"crowd_box_scores/{sport.lower()}/{fixture_id}_{crypto_ts[:19].replace(':', '-')}.json"

    record: dict = {
        "schema_version": "1.0",
        "record_type": "crowd_box_score",
        "fixture_id": fixture_id,
        "sport": sport,
        "calculated_momentum_index": cmi,
        "momentum_surge_pts": surge,
        "winning_section": winning_section,
        "fan_contribution": fan_contribution,
        "crypto_timestamp": crypto_ts,
        "powered_by": "IBM watsonx & Granite Foundation Models",
    }

    if _COS_CONFIGURED:
        try:
            cos = _cos_client()
            cos.Object(_COS_BUCKET, object_key).put(Body=json.dumps(record, indent=2))  # type: ignore[union-attr]
            return {
                "status": "ARCHIVED (IBM Cloud Object Storage)",
                "bucket": _COS_BUCKET,
                "object_key": object_key,
                "crypto_timestamp": crypto_ts,
            }
        except Exception as exc:
            # Fall through to local on runtime error
            local_path = _write_local(object_key, record)
            return {
                "status": f"ARCHIVED_LOCALLY (COS Error: {exc})",
                "bucket": _COS_BUCKET,
                "object_key": object_key,
                "crypto_timestamp": crypto_ts,
                "local_path": local_path,
            }
    else:
        local_path = _write_local(object_key, record)
        return {
            "status": "ARCHIVED_LOCALLY (Simulated IBM COS)",
            "bucket": _COS_BUCKET,
            "object_key": object_key,
            "crypto_timestamp": crypto_ts,
            "local_path": local_path,
        }


def archive_proof_of_momentum_card(
    fixture_id: str,
    sport: str,
    points: str,
    outcome: str,
    narrative: str,
) -> dict:
    """
    Archive a Proof-of-Momentum Story Card for permanent record.

    Returns a transaction receipt dict with keys:
      status, bucket, object_key, crypto_timestamp, [local_path]
    """
    crypto_ts = _crypto_timestamp()
    object_key = f"proof_of_momentum/{sport.lower()}/{fixture_id}_{crypto_ts[:19].replace(':', '-')}.json"

    record: dict = {
        "schema_version": "1.0",
        "record_type": "proof_of_momentum_card",
        "fixture_id": fixture_id,
        "sport": sport,
        "points_display": points,
        "outcome": outcome,
        "granite_narrative": narrative,
        "crypto_timestamp": crypto_ts,
        "powered_by": "IBM watsonx & Granite Foundation Models",
    }

    if _COS_CONFIGURED:
        try:
            cos = _cos_client()
            cos.Object(_COS_BUCKET, object_key).put(Body=json.dumps(record, indent=2))  # type: ignore[union-attr]
            return {
                "status": "ARCHIVED (IBM Cloud Object Storage)",
                "bucket": _COS_BUCKET,
                "object_key": object_key,
                "crypto_timestamp": crypto_ts,
            }
        except Exception as exc:
            local_path = _write_local(object_key, record)
            return {
                "status": f"ARCHIVED_LOCALLY (COS Error: {exc})",
                "bucket": _COS_BUCKET,
                "object_key": object_key,
                "crypto_timestamp": crypto_ts,
                "local_path": local_path,
            }
    else:
        local_path = _write_local(object_key, record)
        return {
            "status": "ARCHIVED_LOCALLY (Simulated IBM COS)",
            "bucket": _COS_BUCKET,
            "object_key": object_key,
            "crypto_timestamp": crypto_ts,
            "local_path": local_path,
        }
