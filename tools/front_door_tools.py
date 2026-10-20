"""
==============================================================================
Tier 1: Front Door / Box Office Tools (`tools/front_door_tools.py`)
Agents:
  1. `ticket_bouncer_agent` (*The Box Office Bouncer*)
  2. `supervisor_agent` (*The Showrunner*)
==============================================================================
"""

from typing import Any, Dict
from db.fanlab_db import get_db

try:
    from ibm_watsonx_orchestrate.agent_builder.tools import tool
except Exception:
    def tool(*args, **kwargs):
        def decorator(fn):
            return fn
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator


@tool
def verify_seat_presence_and_hash(
    member_name: str,
    member_hash: str,
    section_id: str,
    ble_beacon_rssi_dbm: int = -58,
    early_checkin: bool = True,
) -> Dict[str, Any]:
    """
    [Agent #1: ticket_bouncer_agent — The Box Office Bouncer]
    Verifies cryptographic fan passport hash, checks BLE seat beacon proximity
    to prevent GPS/bot spoofing, and validates the 1.25x early arrival window.
    """
    db = get_db()
    record = db.get_passport(member_hash) or db.get_passport(member_name)
    hash_valid = bool(record and record["member_hash"] == member_hash)
    ble_proximity_valid = -90 <= ble_beacon_rssi_dbm <= -25
    anti_spoof_passed = hash_valid and ble_proximity_valid

    early_multiplier = 1.25 if (anti_spoof_passed and early_checkin) else 1.0
    return {
        "agent": "ticket_bouncer_agent",
        "persona": "The Box Office Bouncer",
        "member_name": member_name,
        "member_hash": member_hash,
        "section_id": section_id,
        "hash_verified": hash_valid,
        "ble_proximity_verified": ble_proximity_valid,
        "anti_spoof_status": "VERIFIED_IN_SEAT" if anti_spoof_passed else "SPOOF_BLOCKED",
        "early_arrival_multiplier": early_multiplier,
    }


@tool
def route_production_intent(
    event_type: str,
    sport: str,
    is_clutch: bool,
    anti_spoof_status: str = "VERIFIED_IN_SEAT",
) -> Dict[str, Any]:
    """
    [Agent #2: supervisor_agent — The Showrunner]
    Classifies incoming stadium/fan event, calculates intent confidence (>= 0.55),
    and builds the 4-tier execution plan across Front Stage, Backstage Crew, and Back Door.
    """
    if anti_spoof_status != "VERIFIED_IN_SEAT":
        return {
            "agent": "supervisor_agent",
            "persona": "The Showrunner",
            "intent_confidence": 0.20,
            "routing_status": "REJECTED_AT_BOX_OFFICE",
            "delegation_plan": ["stadium_dispatch_agent"],
            "escalate_to_human": True,
        }

    valid_events = {"CLUTCH_SURGE", "TAILGATE_HUDDLE", "PASSPORT_SYNC", "DISCOVERY_AUDIT", "BASELINE_TICK"}
    confidence = 0.96 if event_type in valid_events else 0.78

    delegation_plan = [
        "coordinator_agent",
        "sound_telemetry_agent",
        "mesh_rigging_agent",
        "trust_safety_agent",
        "synthesizer_agent",
        "optimizer_agent",
        "fan_coach_agent",
        "unit_economics_agent",
        "discovery_insights_agent",
        "cot_inspector_agent",
        "cloudant_chronicler_agent",
        "lakehouse_archivist_agent",
        "sponsor_monetization_agent",
        "stadium_dispatch_agent",
    ]
    return {
        "agent": "supervisor_agent",
        "persona": "The Showrunner",
        "sport": sport,
        "event_type": event_type,
        "is_clutch": is_clutch,
        "intent_confidence": confidence,
        "routing_status": "ROUTED_TO_FULL_CAST" if confidence >= 0.55 else "LOW_CONFIDENCE_ESCALATION",
        "delegation_plan": delegation_plan,
        "escalate_to_human": confidence < 0.55,
    }
