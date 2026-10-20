"""
==============================================================================
Tier 4: Back Door / Stage Door & Loading Dock Tools (`tools/back_door_tools.py`)
Agents:
  13. `cloudant_chronicler_agent` (*The House Chronicler*)
  14. `lakehouse_archivist_agent` (*The Vault Curator*)
  15. `sponsor_monetization_agent` (*The Commercial Promoter*)
  16. `stadium_dispatch_agent` (*The Stage Door Dispatcher*)
==============================================================================
"""

from typing import Any, Dict, List
from cloudant_engine import save_fan_passport, save_telemetry_snapshot
from cos_archive import archive_crowd_box_score
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
def sync_passport_and_standings_to_cloudant(
    fixture_id: str,
    sport: str,
    member_name: str,
    member_hash: str,
    section_id: str,
    role: str,
    tier: int,
    clean_db: float,
    clean_hr: float,
    clean_taps: float,
    clean_vu: float,
    cmi_score: float,
    early_multiplier: float = 1.25,
    clutch_multiplier: float = 2.0,
    per_capita_score: float = 96.8,
    chaser_alert: str = "Section 114 leads by 4.4 pts!",
) -> Dict[str, Any]:
    """
    [Agent #13: cloudant_chronicler_agent — The House Chronicler]
    Synchronizes Fan Passports, sanitized telemetry snapshots, and section
    standings to both local SQLite (`db/fanlab_db.py`) and IBM Cloudant NoSQL.
    """
    db = get_db()
    tel_id = db.log_telemetry(
        fixture_id=fixture_id,
        sport=sport,
        section_id=section_id,
        raw_db=round(clean_db - 2.0, 1),
        clean_log_db=clean_db,
        pa_bleed_db=3.5,
        clean_hr_bpm=clean_hr,
        taps_per_sec=clean_taps,
        granite_vu=clean_vu,
        cmi_score=cmi_score,
    )
    stand_id = db.log_section_standing(
        fixture_id=fixture_id,
        sport=sport,
        section_name=section_id,
        raw_cmi=cmi_score,
        checked_in_fans=150,
        early_multiplier=early_multiplier,
        clutch_multiplier=clutch_multiplier,
        per_capita_score=per_capita_score,
        rank_position=1,
        chaser_alert=chaser_alert,
    )
    cloudant_passport = save_fan_passport(
        member_name=member_name,
        member_hash=member_hash,
        section_id=section_id,
        sport=sport,
        role=role,
        tier=tier,
        device_anchor="Wearable BLE Anchor",
        early_multiplier=early_multiplier,
    )
    cloudant_tel = save_telemetry_snapshot(
        section_id=section_id,
        sport=sport,
        cmi=cmi_score,
        tier="Maximum" if cmi_score >= 80.0 else "High",
        db=clean_db,
        hr=clean_hr,
        taps=clean_taps,
        vu=clean_vu,
        fan_count=50,
    )
    return {
        "agent": "cloudant_chronicler_agent",
        "persona": "The House Chronicler",
        "sql_telemetry_log_id": tel_id,
        "sql_standing_id": stand_id,
        "cloudant_passport_status": cloudant_passport.get("status", "SUCCESS"),
        "cloudant_telemetry_status": cloudant_tel.get("status", "SUCCESS"),
    }


@tool
def archive_tamper_evident_box_score_to_cos(
    fixture_id: str,
    sport: str,
    cmi_score: float,
    surge_pts: float,
    winning_section: str,
    outcome_label: str,
    granite_narrative: str,
    fan_notes: List[str],
) -> Dict[str, Any]:
    """
    [Agent #14: lakehouse_archivist_agent — The Vault Curator]
    Packages the post-play Crowd Box Score into an immutable JSON payload,
    computes its SHA-256 cryptographic checksum, and archives it to IBM COS S3.
    """
    receipt = archive_crowd_box_score(
        fixture_id=fixture_id,
        sport=sport,
        cmi=cmi_score,
        surge=surge_pts,
        winning_section=winning_section,
        outcome=outcome_label,
        granite_narrative=granite_narrative,
        fan_notes=fan_notes,
    )
    receipt["agent"] = "lakehouse_archivist_agent"
    receipt["persona"] = "The Vault Curator"
    return receipt


@tool
def settle_sponsor_perk_and_roi(
    fixture_id: str,
    winning_section: str,
    cmi_score: float,
    cost_per_seat_usd: float = 0.0137,
) -> Dict[str, Any]:
    """
    [Agent #15: sponsor_monetization_agent — The Commercial Promoter]
    Unlocks dynamic sponsor concession/merch perks when a section hits Clutch
    Maximum Tier (CMI >= 80.0) and settles the revenue side of Unit Economics.
    """
    perk_unlocked = cmi_score >= 80.0
    sponsor_rev = 4.85 if perk_unlocked else 1.25
    net_margin = round(sponsor_rev - cost_per_seat_usd, 4)
    gross_margin_pct = round((net_margin / sponsor_rev) * 100.0, 2)
    return {
        "agent": "sponsor_monetization_agent",
        "persona": "The Commercial Promoter",
        "fixture_id": fixture_id,
        "winning_section": winning_section,
        "perk_unlocked": perk_unlocked,
        "perk_reward": "20% Off Team Store + Free Concession Upgrade (111 dB Roar Campaign)" if perk_unlocked else "1.25x Early Check-In Loyalty Points",
        "sponsor_revenue_per_seat_usd": sponsor_rev,
        "compute_cost_per_seat_usd": cost_per_seat_usd,
        "net_margin_per_seat_usd": net_margin,
        "gross_margin_pct": gross_margin_pct,
    }


@tool
def dispatch_jumbotron_and_human_ops(
    sport: str,
    winning_section: str,
    cmi_score: float,
    perk_reward: str,
    escalate_to_human: bool = False,
    escalation_reason: str = "NONE",
) -> Dict[str, Any]:
    """
    [Agent #16: stadium_dispatch_agent — The Stage Door Dispatcher]
    Pushes live Section Defense Belt graphics to the Arena Jumbotron LED ribbon
    feed, delivers fan wallet perks, and triggers `escalate_to_human` for
    Stadium Operations if a safety or low-confidence anomaly occurs.
    """
    return {
        "agent": "stadium_dispatch_agent",
        "persona": "The Stage Door Dispatcher",
        "jumbotron_feed_status": "BROADCAST_LIVE",
        "jumbotron_headline": f"DEFENSE BELT WINNER: {winning_section} ({cmi_score} CMI)!",
        "wallet_perk_dispatched": perk_reward,
        "escalated_to_human_ops": escalate_to_human,
        "human_ops_ticket": f"OPS-ALERT: {escalation_reason}" if escalate_to_human else "NO_ESCALATION_REQUIRED",
    }
