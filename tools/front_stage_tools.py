"""
==============================================================================
Tier 2: Front Stage / On-Stage Talent Tools (`tools/front_stage_tools.py`)
Agents:
  3. `coordinator_agent` (*The Conductor*)
  4. `synthesizer_agent` (*The Scout*)
  5. `optimizer_agent` (*The Strategist*)
  6. `fan_coach_agent` (*The Hype Coach*)
==============================================================================
"""

from typing import Any, Dict, List
from orchestrate_agents import (
    InvisibleCoordinatorAgent,
    KnowledgeSynthesizerAgent,
    SystemOptimizerAgent,
)
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
def evaluate_clutch_clock_window(sport: str, game_situation: str) -> Dict[str, Any]:
    """
    [Agent #3: coordinator_agent — The Conductor]
    Evaluates live play clock and game situation to trigger the 2.0x Clutch Multiplier.
    """
    agent = InvisibleCoordinatorAgent(sport=sport)
    res = agent.evaluate_game_state(game_situation)
    res["agent"] = "coordinator_agent"
    res["persona"] = "The Conductor"
    return res


@tool
def synthesize_cmi_and_playbook_rag(
    sport: str,
    clean_db: float,
    clean_hr: float,
    clean_taps: float,
    clean_vu: float,
) -> Dict[str, Any]:
    """
    [Agent #4: synthesizer_agent — The Scout]
    Fuses sanitized SPL decibels, Hampel-filtered BPM, tap speed, and Granite
    vocal urgency into the 0-100 Crowd Momentum Index (CMI) and attaches RAG rules.
    """
    agent = KnowledgeSynthesizerAgent()
    res = agent.synthesize_telemetry(clean_db, clean_hr, clean_taps, clean_vu)
    res["cmi_score"] = res.get("cmi", 92.0)
    res["agent"] = "synthesizer_agent"
    res["persona"] = "The Scout"
    res["sport"] = sport
    res["rag_source"] = "data/cmi_acoustic_biometric_playbook.md"
    return res


@tool
def rank_sections_and_chaser_alert(
    sport: str,
    lead_section: str,
    lead_cmi: float,
    early_multiplier: float = 1.25,
    clutch_multiplier: float = 2.0,
) -> Dict[str, Any]:
    """
    [Agent #5: optimizer_agent — The Strategist]
    Computes per-capita section standings, fires Chaser Alerts, and prepares
    the post-play Reality Delta summary.
    """
    agent = SystemOptimizerAgent()
    rival_sec = "Section 115 (End Zone Loyals)" if "114" in lead_section else "Section 114 (Thunder Row)"
    third_sec = "Section 113 (Rider's Crew)"
    standings = agent.rank_sections_per_capita([
        {
            "name": lead_section,
            "cmi": lead_cmi,
            "checked_in_fans": 150,
            "early_multiplier": early_multiplier,
            "clutch_multiplier": clutch_multiplier,
        },
        {
            "name": rival_sec,
            "cmi": round(lead_cmi * 0.92, 1),
            "checked_in_fans": 140,
            "early_multiplier": 1.0,
            "clutch_multiplier": 1.0,
        },
        {
            "name": third_sec,
            "cmi": round(lead_cmi * 0.85, 1),
            "checked_in_fans": 120,
            "early_multiplier": 1.0,
            "clutch_multiplier": 1.0,
        },
    ])
    standings["agent"] = "optimizer_agent"
    standings["persona"] = "The Strategist"
    return standings


@tool
def generate_fan_progression_coaching(
    member_name: str,
    cmi_score: float,
    is_clutch: bool,
) -> Dict[str, Any]:
    """
    [Agent #6: fan_coach_agent — The Hype Coach]
    Generates personalized tier progression and dynamic NFT accolade coaching
    for the active fan persona.
    """
    db = get_db()
    passport = db.get_passport(member_name) or {
        "member_name": member_name,
        "role": "Section Captain",
        "tier": 5,
        "games_attended": 62,
        "clutch_stops": 31,
    }
    clutch_tag = "2.0x Clutch Stop" if is_clutch else "steady baseline"
    coach_line = (
        f"{member_name} ({passport['role']}, Tier {passport['tier']}): "
        f"Your {cmi_score} CMI ({clutch_tag}) pushes you past {passport['games_attended']} career games "
        f"and {passport['clutch_stops']} verified clutch stops toward your next Living Trophy Case unlock!"
    )
    return {
        "agent": "fan_coach_agent",
        "persona": "The Hype Coach",
        "member_name": member_name,
        "coaching_directive": coach_line,
    }
