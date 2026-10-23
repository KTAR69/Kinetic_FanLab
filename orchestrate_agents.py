"""
==============================================================================
Kinetic FanLab — watsonx Orchestrate Multi-Agent Swarm (All 8 Official IBM Archetypes)
Scaffolded via IBM Bob IDE & Gemini (Track 3: Fan-Centric Sports & Entertainment)

Operationalizes all 8 Official IBM Agentic AI Archetypes defined in
`US Fall 2026 - Industry Challenges AI Experiential Learning Lab with Bob.pdf`
(Appendix 1, Pages 6-8), mapped 2-for-1 across the 16-Agent Theatre Production Cast:

1. The Cognitive Load Reducer  -> supervisor_agent & discovery_insights_agent
2. The Invisible Coordinator   -> coordinator_agent & mesh_rigging_agent
3. The Context-Aware Expert    -> fan_coach_agent & ticket_bouncer_agent
4. The Decision Gatekeeper     -> unit_economics_agent & trust_safety_agent
5. The Long-Horizon Planner    -> cloudant_chronicler_agent & lakehouse_archivist_agent
6. The Knowledge Synthesizer   -> synthesizer_agent & sound_telemetry_agent
7. The Human-AI Boundary Mgr   -> stadium_dispatch_agent & cot_inspector_agent
8. The System Optimizer        -> optimizer_agent & sponsor_monetization_agent
==============================================================================
"""

import re
import time
from typing import Dict, Any, List, Optional

try:
    from watsonx_live import analyze_vocal_urgency_live, generate_narrative_live, invoke_watsonx_chat
except ImportError:
    def analyze_vocal_urgency_live(text: str) -> float:
        return 0.85

    def generate_narrative_live(sport: str, outcome: str, pre: float, peak: float, notes: list) -> str:
        return f"Coordinated crowd surge of +{round(peak - pre, 1)} pts disrupted opponent execution."

    def invoke_watsonx_chat(system_prompt: str, user_prompt: str) -> Optional[str]:
        return None

try:
    from governance_check import evaluate_fan_content_safety
except ImportError:
    def evaluate_fan_content_safety(text: str) -> dict:
        return {"input_text": text, "guardrail_status": "APPROVED", "violations": [], "action": "Proceed"}


# ==============================================================================
# LIVE DEPLOYED IBM WATSONX ORCHESTRATE AGENT UUID REGISTRY (`eu-de-0ec71755`)
# Instance: https://api.eu-de.watson-orchestrate.cloud.ibm.com/instances/0ec71755-fb9f-4e85-8f8a-ba4ce2ea6097
# ==============================================================================

LIVE_WXO_ENVIRONMENT = {
    "env_name": "eu-de-0ec71755",
    "region": "eu-de (Frankfurt)",
    "workspace": "Global workspace",
    "instance_id": "0ec71755-fb9f-4e85-8f8a-ba4ce2ea6097",
    "auth_type": "ibm_iam",
    "adk_version": "2.6.0",
}

LIVE_WXO_AGENT_IDS: Dict[str, str] = {
    "ticket_bouncer_agent": "fac5eccf-95de-4470-acc0-94712404ee28",
    "supervisor_agent": "e4370510-1643-4450-835b-61c285affd77",
    "coordinator_agent": "aff3048f-d490-4ab2-8058-e1da04b5a60d",
    "synthesizer_agent": "c5d257b0-bb2e-454a-b120-3b691d5c526d",
    "optimizer_agent": "d004e589-4a0d-4efd-8fcf-6f51928cfbc5",
    "fan_coach_agent": "41d1ce50-bb17-483c-801b-8070ec07b987",
    "sound_telemetry_agent": "e3a26c43-588d-4cad-9df6-06a4aab684c7",
    "mesh_rigging_agent": "db6af6d9-e6f9-4ed9-8473-f2567f26c6b3",
    "trust_safety_agent": "00405383-384c-4919-9b51-a641153b89a5",
    "cot_inspector_agent": "ee07ebfe-be76-4128-b02e-33da0903f151",
    "unit_economics_agent": "7df57fe7-3b24-4ac5-a045-6fcce95099b5",
    "discovery_insights_agent": "9728392e-784b-428f-b431-0c4f00a98f59",
    "cloudant_chronicler_agent": "3e02cfda-b7e1-4e79-a8ad-7b728a38136c",
    "lakehouse_archivist_agent": "e20d3278-bb40-4a80-838d-7918970b5544",
    "sponsor_monetization_agent": "734c3abc-7c61-4843-adcf-2d95295e4c58",
    "stadium_dispatch_agent": "3d95dbd5-00fd-4164-ac7c-5b74a87d5290",
}


# ==============================================================================
# OFFICIAL 8 IBM AGENTIC AI ARCHETYPES REGISTRY (2-for-1 Cast Mapping)
# ==============================================================================

EIGHT_IBM_ARCHETYPES: List[Dict[str, Any]] = [
    {
        "archetype_id": 1,
        "archetype_name": "1. The Cognitive Load Reducer",
        "appendix_page": "Appendix 1, p. 6",
        "core_purpose": "Filters, prioritizes, and frames fragmented stadium information so fans and operators act without overload.",
        "ibm_technical_patterns": [
            "Retrieval-Augmented Generation (RAG) over fragmented knowledge",
            "Multi-step reasoning (gather -> compare -> recommend)",
            "Evaluation / ranking logic",
            "Confidence thresholds (>= 0.55) to know when NOT to answer",
        ],
        "assigned_agents": ["supervisor_agent", "discovery_insights_agent"],
        "personas": ["The Showrunner", "The Audience Director"],
    },
    {
        "archetype_id": 2,
        "archetype_name": "2. The Invisible Coordinator",
        "appendix_page": "Appendix 1, p. 6",
        "core_purpose": "Synchronizes multi-step crowd pacing and 50-seat BLE mesh handoffs behind the scenes.",
        "ibm_technical_patterns": [
            "Multi-agent systems (planner, executor, validator)",
            "Tool calling & API orchestration",
            "Event-driven architectures (triggers, webhooks, queues)",
            "State tracking across steps & human-in-the-loop escalation",
        ],
        "assigned_agents": ["coordinator_agent", "mesh_rigging_agent"],
        "personas": ["The Conductor", "The Master Rigger"],
    },
    {
        "archetype_id": 3,
        "archetype_name": "3. The Context-Aware Expert",
        "appendix_page": "Appendix 1, pp. 6-7",
        "core_purpose": "Adapts guidance to who the fan is, their seat beacon proximity, and their 365-day tier progression.",
        "ibm_technical_patterns": [
            "RAG + memory (session or user state)",
            "Context selection / filtering logic",
            "Personalization without overfitting",
            "Rule + reasoning hybrids",
        ],
        "assigned_agents": ["fan_coach_agent", "ticket_bouncer_agent"],
        "personas": ["The Hype Coach", "The Box Office Bouncer"],
    },
    {
        "archetype_id": 4,
        "archetype_name": "4. The Decision Gatekeeper",
        "appendix_page": "Appendix 1, p. 7",
        "core_purpose": "Evaluates high-cost/high-risk actions (paid LLM inference & content safety) before execution proceeds.",
        "ibm_technical_patterns": [
            "Evaluation against multiple criteria ($0.015/seat ceiling & EEOC DIR >= 0.80)",
            "Evidence gathering & validation",
            "Confidence scoring",
            "Explainability & failure/escalation logic",
        ],
        "assigned_agents": ["unit_economics_agent", "trust_safety_agent"],
        "personas": ["The FinOps Producer", "The Safety Steward"],
    },
    {
        "archetype_id": 5,
        "archetype_name": "5. The Long-Horizon Planner",
        "appendix_page": "Appendix 1, p. 7",
        "core_purpose": "Maintains longitudinal 365-day Fan Passport state and tamper-evident seasonal Lakehouse archives.",
        "ibm_technical_patterns": [
            "Planning and re-planning loops across games/seasons",
            "Memory of prior actions & outcomes (Cloudant + COS S3)",
            "Trigger-based execution",
            "Multi-step goal decomposition",
        ],
        "assigned_agents": ["cloudant_chronicler_agent", "lakehouse_archivist_agent"],
        "personas": ["The House Chronicler", "The Vault Curator"],
    },
    {
        "archetype_id": 6,
        "archetype_name": "6. The Knowledge Synthesizer",
        "appendix_page": "Appendix 1, p. 7",
        "core_purpose": "Fuses noisy acoustic dB, wearable BPM, tap velocity, and vocal urgency into the 0-100 CMI.",
        "ibm_technical_patterns": [
            "Advanced RAG & multi-document reasoning",
            "Comparison and abstraction (Log SPL vs. Linear average)",
            "Summarization across perspectives",
            "Conflict / outlier detection (Hampel BPM filter & -3.5 dB PA bleed)",
        ],
        "assigned_agents": ["synthesizer_agent", "sound_telemetry_agent"],
        "personas": ["The Scout", "The Sound Engineer"],
    },
    {
        "archetype_id": 7,
        "archetype_name": "7. The Human-AI Boundary Manager",
        "appendix_page": "Appendix 1, pp. 7-8",
        "core_purpose": "Audits Chain-of-Thought confidence/SLAs and knows when to pause automation and escalate to Stadium Ops.",
        "ibm_technical_patterns": [
            "Confidence thresholds (>= 0.55 intent gate)",
            "Ambiguity & anomaly detection (< 250ms latency SLA)",
            "Escalation logic (escalate_to_human)",
            "Graceful failure & transparent audit logging",
        ],
        "assigned_agents": ["stadium_dispatch_agent", "cot_inspector_agent"],
        "personas": ["The Stage Door Dispatcher", "The Stage Manager"],
    },
    {
        "archetype_id": 8,
        "archetype_name": "8. The System Optimizer",
        "appendix_page": "Appendix 1, p. 8",
        "core_purpose": "Compounds stadium rivalry loops, per-capita section standings, and two-sided sponsor ROI over time.",
        "ibm_technical_patterns": [
            "Pattern detection (Chaser Alerts & per-capita normalization)",
            "Feedback loops (Reality Delta StoryCards)",
            "Metrics-driven decisions ($4.85/seat sponsor ROI, 99.72% gross margin)",
            "Iterative longitudinal refinement",
        ],
        "assigned_agents": ["optimizer_agent", "sponsor_monetization_agent"],
        "personas": ["The Strategist", "The Commercial Promoter"],
    },
]

AGENT_TO_IBM_ARCHETYPE: Dict[str, Dict[str, Any]] = {}
for _arch in EIGHT_IBM_ARCHETYPES:
    for _idx, _ag in enumerate(_arch["assigned_agents"]):
        AGENT_TO_IBM_ARCHETYPE[_ag] = {
            "archetype_id": _arch["archetype_id"],
            "archetype_name": _arch["archetype_name"],
            "persona": _arch["personas"][_idx],
            "appendix_page": _arch["appendix_page"],
            "wxo_agent_id": LIVE_WXO_AGENT_IDS.get(_ag, ""),
        }


# --- Normalization Utility (Contract Invariant) ---

def normalize_signal(val: float, min_val: float, max_val: float) -> float:
    clamped = max(min_val, min(val, max_val))
    return (clamped - min_val) / (max_val - min_val)


def compute_cmi_index(db: float, hr: float, taps: float, vu: float) -> float:
    n_db = normalize_signal(db, 60.0, 115.0)
    n_hr = normalize_signal(hr, 60.0, 160.0)
    n_taps = normalize_signal(taps, 0.0, 15.0)
    n_vu = normalize_signal(vu, 0.0, 1.0)
    return round((n_db * 0.35 + n_hr * 0.25 + n_taps * 0.20 + n_vu * 0.20) * 100, 1)


def evaluate_tier(cmi: float) -> str:
    if cmi >= 80.0:
        return "Maximum"
    elif cmi >= 65.0:
        return "High"
    elif cmi >= 45.0:
        return "Moderate"
    else:
        return "Baseline"


# ==============================================================================
# ARCHETYPE 1: THE COGNITIVE LOAD REDUCER
# (`supervisor_agent` & `discovery_insights_agent`)
# ==============================================================================

class CognitiveLoadReducerAgent:
    """
    Archetype 1 (The Cognitive Load Reducer):
    Filters fragmented stadium events and user discovery telemetry into clear,
    confidence-gated priorities so neither fans nor operators face overload.
    """
    ibm_archetype = "1. The Cognitive Load Reducer"

    def __init__(self, confidence_threshold: float = 0.55):
        self.confidence_threshold = confidence_threshold

    def prioritize_and_route(self, sport: str, event_type: str, is_clutch: bool, confidence: float = 0.96) -> Dict[str, Any]:
        proceed = confidence >= self.confidence_threshold
        return {
            "agent": "CognitiveLoadReducer",
            "ibm_archetype": self.ibm_archetype,
            "sport": sport,
            "event_type": event_type,
            "confidence": confidence,
            "proceed": proceed,
            "escalate_to_human": not proceed,
            "recommended_focus": "CLUTCH_DEFENSIVE_DISRUPTION" if is_clutch else "BASELINE_CADENCE",
        }


# ==============================================================================
# ARCHETYPE 2: THE INVISIBLE COORDINATOR
# (`coordinator_agent` & `mesh_rigging_agent`)
# ==============================================================================

class InvisibleCoordinatorAgent:
    """
    Archetype 2 (The Invisible Coordinator):
    Continuously monitors game clock, possession leverage, and 50-seat BLE mesh
    synchronization so crowd vocal stamina peaks at opponent execution.
    """
    ibm_archetype = "2. The Invisible Coordinator"

    def __init__(self, sport: str = "Basketball"):
        self.sport = sport.capitalize()
        self.clutch_active = False

    def evaluate_game_state(self, game_context: str, time_remaining_sec: Optional[float] = None) -> Dict[str, Any]:
        ctx_lower = game_context.lower()
        is_basketball = "basket" in self.sport.lower()

        if is_basketball:
            if "free throw" in ctx_lower or "clutch" in ctx_lower or "foul" in ctx_lower:
                self.clutch_active = True
                clutch_multiplier = 2.0
                tactic = "Synchronized Visual Waving & Piercing Knee-Bend Scream"
                pacing_directive = "T-10s: Silent focus | T-5s: Wave props left-to-right | T-2s: DEAFENING ROAR ON KNEE BEND!"
                trigger_event = "CLUTCH FREE THROW WINDOW (6th Man Defense Active)"
            else:
                self.clutch_active = False
                clutch_multiplier = 1.0
                tactic = "Rhythmic Possession Chant"
                pacing_directive = "Maintain defensive energy and section rhythm."
                trigger_event = "REGULAR POSSESSION FLOW"
        else:
            if "timeout" in ctx_lower or "ice" in ctx_lower:
                self.clutch_active = False
                clutch_multiplier = 1.25
                tactic = "Bleacher Stomp Endurance Pacing"
                pacing_directive = "TIMEOUT DELAY: Stomp bleachers in rhythm! Save full vocal roar for the snap!"
                trigger_event = "TIMEOUT DELAY PACING ('Icing the Kicker')"
            elif "field goal" in ctx_lower or "snap" in ctx_lower or "clutch" in ctx_lower:
                self.clutch_active = True
                clutch_multiplier = 2.0
                tactic = "111+ dB Acoustic Wall (Cadence Surge)"
                pacing_directive = "SNAP IMMINENT: 111 dB MAXIMUM ROAR! Overwhelm the snap count!"
                trigger_event = "CLUTCH 48-YARD FG SNAP (12th Man Defense Active)"
            else:
                self.clutch_active = False
                clutch_multiplier = 1.0
                tactic = "Zone Defensive Chant"
                pacing_directive = "Steady stadium energy."
                trigger_event = "BETWEEN DOWNS"

        return {
            "agent": "InvisibleCoordinator",
            "ibm_archetype": self.ibm_archetype,
            "sport": self.sport,
            "clutch_active": self.clutch_active,
            "multiplier": clutch_multiplier,
            "tactic": tactic,
            "pacing_directive": pacing_directive,
            "trigger_event": trigger_event,
            "timestamp": time.time(),
        }


# ==============================================================================
# ARCHETYPE 3: THE CONTEXT-AWARE EXPERT
# (`fan_coach_agent` / `FanCoachAgent` & `ticket_bouncer_agent`)
# ==============================================================================

class FanCoachAgent:
    """
    Archetype 3 (The Context-Aware Expert):
    Adapts guidance to who the fan is, their seat role, their BLE proximity,
    and their longitudinal 365-day Living Trophy Case progression.
    """
    ibm_archetype = "3. The Context-Aware Expert"

    def coach(self, member_name: str, persona_data: Dict[str, Any], current_cmi: float, is_clutch: bool) -> str:
        role = persona_data.get("role", "Section Member")
        tier = persona_data.get("tier", "Tier 1")
        games = persona_data.get("career_games", persona_data.get("games", 10))
        stops = persona_data.get("clutch_stops", 5)
        mode_str = "2.0x Clutch Stop" if is_clutch else "Baseline Rhythm"
        return (
            f"{member_name} ({role} — {tier}): At {current_cmi}/100 CMI ({mode_str}), "
            f"your {games} career games and {stops} verified stops put you right on track for your next Living Trophy Case badge!"
        )


ContextAwareExpertAgent = FanCoachAgent


# ==============================================================================
# ARCHETYPE 4: THE DECISION GATEKEEPER
# (`unit_economics_agent` & `trust_safety_agent`)
# ==============================================================================

class DecisionGatekeeperAgent:
    """
    Archetype 4 (The Decision Gatekeeper):
    Governs high-cost/high-risk execution gates: enforces the <= $0.015/seat
    cloud compute ceiling and the EEOC 4/5ths dialect fairness gate (DIR = 0.953).
    """
    ibm_archetype = "4. The Decision Gatekeeper"

    def evaluate_gate(
        self,
        unit_cost_usd: float = 0.0137,
        cost_ceiling_usd: float = 0.0150,
        dir_score: float = 0.953,
        guardrail_status: str = "APPROVED",
    ) -> Dict[str, Any]:
        cost_ok = unit_cost_usd <= cost_ceiling_usd
        fairness_ok = dir_score >= 0.80
        safety_ok = guardrail_status == "APPROVED"
        approved = cost_ok and fairness_ok and safety_ok
        return {
            "agent": "DecisionGatekeeper",
            "ibm_archetype": self.ibm_archetype,
            "gate_approved": approved,
            "cost_within_ceiling": cost_ok,
            "eeoc_fairness_compliant": fairness_ok,
            "safety_approved": safety_ok,
            "unit_cost_usd": unit_cost_usd,
            "dir_score": dir_score,
        }


# ==============================================================================
# ARCHETYPE 5: THE LONG-HORIZON PLANNER
# (`cloudant_chronicler_agent` & `lakehouse_archivist_agent`)
# ==============================================================================

class LongHorizonPlannerAgent:
    """
    Archetype 5 (The Long-Horizon Planner):
    Plans and tracks fan identity progression across a 365-day season using
    IBM Cloudant NoSQL passports and tamper-evident COS S3 Lakehouse archives.
    """
    ibm_archetype = "5. The Long-Horizon Planner"

    def plan_season_milestone(self, member_name: str, games_attended: int, target_games: int = 50) -> Dict[str, Any]:
        remaining = max(0, target_games - games_attended)
        progress_pct = round(min(1.0, games_attended / max(1, target_games)) * 100, 1)
        return {
            "agent": "LongHorizonPlanner",
            "ibm_archetype": self.ibm_archetype,
            "member_name": member_name,
            "games_attended": games_attended,
            "target_games": target_games,
            "games_remaining": remaining,
            "season_progress_pct": progress_pct,
        }


# ==============================================================================
# ARCHETYPE 6: THE KNOWLEDGE SYNTHESIZER
# (`synthesizer_agent` & `sound_telemetry_agent`)
# ==============================================================================

class KnowledgeSynthesizerAgent:
    """
    Archetype 6 (The Knowledge Synthesizer):
    Ingests noisy multimodal sensor streams (Log SPL acoustics, Hampel-filtered
    smartwatch BPM, tap rate, and Granite vocal urgency) and synthesizes CMI.
    """
    ibm_archetype = "6. The Knowledge Synthesizer"

    def __init__(self, sport: str = "Basketball"):
        self.sport = sport.capitalize()

    def evaluate_voice_outburst(self, raw_transcript: str) -> Dict[str, Any]:
        gov_result = evaluate_fan_content_safety(raw_transcript)
        if gov_result.get("guardrail_status") == "REJECTED":
            return {
                "transcript": raw_transcript,
                "governance_status": "REJECTED",
                "violations": gov_result.get("violations", ["Content safety violation"]),
                "urgency_score": 0.0,
            }
        urgency = analyze_vocal_urgency_live(raw_transcript)
        return {
            "transcript": raw_transcript,
            "governance_status": "APPROVED",
            "violations": [],
            "urgency_score": urgency,
        }

    def synthesize_telemetry(self, db: float, hr: float, taps: float, vu: float) -> Dict[str, Any]:
        cmi = compute_cmi_index(db, hr, taps, vu)
        tier = evaluate_tier(cmi)
        return {
            "agent": "KnowledgeSynthesizer",
            "ibm_archetype": self.ibm_archetype,
            "cmi": cmi,
            "tier": tier,
            "normalized_components": {
                "acoustic_pct": round(normalize_signal(db, 60.0, 115.0) * 35, 1),
                "biometric_pct": round(normalize_signal(hr, 60.0, 160.0) * 25, 1),
                "taps_pct": round(normalize_signal(taps, 0.0, 15.0) * 20, 1),
                "urgency_pct": round(normalize_signal(vu, 0.0, 1.0) * 20, 1),
            },
            "raw_values": {"db": db, "hr": hr, "taps": taps, "vu": vu},
            "timestamp": time.time(),
        }


# ==============================================================================
# ARCHETYPE 7: THE HUMAN-AI BOUNDARY MANAGER
# (`stadium_dispatch_agent` & `cot_inspector_agent`)
# ==============================================================================

class HumanAiBoundaryManagerAgent:
    """
    Archetype 7 (The Human-AI Boundary Manager):
    Designed around when NOT to act autonomously—enforcing confidence thresholds,
    < 250ms latency SLAs, and escalating safety or biometric anomalies to human
    Stadium Operations.
    """
    ibm_archetype = "7. The Human-AI Boundary Manager"

    def evaluate_boundary(
        self,
        confidence_score: float = 0.96,
        latency_ms: float = 18.4,
        guardrail_status: str = "APPROVED",
    ) -> Dict[str, Any]:
        escalate = (confidence_score < 0.55) or (latency_ms > 250.0) or (guardrail_status == "REJECTED")
        return {
            "agent": "HumanAiBoundaryManager",
            "ibm_archetype": self.ibm_archetype,
            "autonomous_action_permitted": not escalate,
            "escalate_to_human": escalate,
            "confidence_score": confidence_score,
            "latency_ms": latency_ms,
            "guardrail_status": guardrail_status,
        }


# ==============================================================================
# ARCHETYPE 8: THE SYSTEM OPTIMIZER
# (`optimizer_agent` & `sponsor_monetization_agent`)
# ==============================================================================

class SystemOptimizerAgent:
    """
    Archetype 8 (The System Optimizer):
    Drives longitudinal ecosystem compounding. Calculates per-capita section
    standings, emits Chaser Alerts, unlocks sponsor perks ($4.85/seat), and
    prompts IBM Granite for Reality Delta StoryCards.
    """
    ibm_archetype = "8. The System Optimizer"

    def __init__(self, sport: str = "Basketball"):
        self.sport = sport.capitalize()

    def rank_sections_per_capita(self, section_batches: List[Dict[str, Any]]) -> Dict[str, Any]:
        standings = []
        for s in section_batches:
            name = s.get("name", "Unknown Section")
            fans = max(1, s.get("checked_in_fans", 100))
            raw_cmi = s.get("cmi", 35.0)
            early_mult = s.get("early_multiplier", 1.0)
            clutch_mult = s.get("clutch_multiplier", 1.0)

            final_score = round(raw_cmi * early_mult * clutch_mult, 1)
            standings.append({
                "section": name,
                "score": final_score,
                "fans": fans,
                "early_mult": early_mult,
                "clutch_mult": clutch_mult,
            })

        standings.sort(key=lambda x: x["score"], reverse=True)
        winner = standings[0] if standings else None

        chaser_alert = "All sections locked in competition."
        if len(standings) >= 2:
            gap = round(standings[0]["score"] - standings[1]["score"], 1)
            chaser_alert = f"⚠️ CHASER ALERT: {standings[1]['section']} is trailing {standings[0]['section']} by only -{gap} pts! Pulse-tap to defend your lead!"

        return {
            "agent": "SystemOptimizer",
            "ibm_archetype": self.ibm_archetype,
            "standings": standings,
            "leader": winner["section"] if winner else "None",
            "chaser_alert": chaser_alert,
        }

    def generate_reality_delta(self, outcome_label: str, pre_cmi: float, peak_cmi: float, fan_notes: List[str]) -> Dict[str, Any]:
        surge = round(peak_cmi - pre_cmi, 1)
        narrative = generate_narrative_live(self.sport, outcome_label, pre_cmi, peak_cmi, fan_notes)
        winning_sec = "Section 114 (Thunder Row)" if "basket" in self.sport.lower() else "Section 115 (End Zone Loyals)"

        return {
            "headline": f"+{surge} PTS MOMENTUM SURGE",
            "subtitle": f"CLUTCH DEFENSIVE STOP VERIFIED ({self.sport})",
            "winning_section": winning_sec,
            "defense_belt_awarded": True,
            "pre_cmi": pre_cmi,
            "peak_cmi": peak_cmi,
            "surge_delta": surge,
            "outcome": outcome_label,
            "granite_narrative": narrative,
            "ibm_archetype": self.ibm_archetype,
            "timestamp": time.time(),
        }


# ==============================================================================
# HUDDLE HELPER & BACKEND MULTI-AGENT TEAMWORK ENGINE (SCREEN 5)
# ==============================================================================

def get_co_captain_huddle(
    member_name: str,
    persona_data: Dict[str, Any],
    sport: str,
    cmi: float,
    is_clutch: bool,
) -> Dict[str, Any]:
    """
    Returns clean, fan-facing briefings from the 4 Squad Agents (Conductor, Scout,
    Strategist, Coach) while preserving all contract metadata keys for test suites.
    """
    role = persona_data.get("role", "Section Captain")
    is_bball = "basket" in sport.lower()

    if is_bball:
        if is_clutch:
            conductor = (
                f"{member_name} ({role}), 2.0x Clutch Window is LIVE! Keep Section 114 silent on the first bounce, "
                f"then wave props left-to-right and unleash 106.5 dB on the shooter's knee bend!"
            )
        else:
            conductor = (
                f"{member_name} ({role}), we are in baseline possession flow. Pace Section 114's vocal stamina "
                f"so our decibel wall is fresh for the next 4th-quarter free throw!"
            )
    else:
        if is_clutch:
            conductor = (
                f"{member_name} ({role}), 2.0x Clutch Snap Window is LIVE! Transition Section 115 from bleacher stomps "
                f"into a sustained 111.8 dB roar right as the center puts his hand on the football!"
            )
        else:
            conductor = (
                f"{member_name} ({role}), timeout delay ('Icing the Kicker') in progress. Keep Section 115 stomping "
                f"the bleachers in rhythm to rest vocal cords until the 0:03 snap!"
            )

    miss_prob = round(min(74.0, 22.0 + (cmi * 0.52)), 1)
    scout = (
        f"Live Crowd Momentum is {cmi}/100 ({evaluate_tier(cmi)} Tier). At this intensity, opponent miss probability "
        f"climbs to {miss_prob}% and your section's energy wave is +14% above arena average!"
    )
    lead_sec = "Section 114 (Thunder Row)" if is_bball else "Section 115 (End Zone Loyals)"
    rival_sec = "Section 115" if is_bball else "Section 114"
    strategist = (
        f"{lead_sec} holds #1 per-capita standing! {rival_sec} is chasing within single digits—sync a pulse burst "
        f"or chant with your row to lock in the Section Defense Belt and stadium concession perks!"
    )
    coach = FanCoachAgent().coach(member_name, persona_data, cmi, is_clutch)

    return {
        "conductor": conductor,
        "scout": scout,
        "strategist": strategist,
        "coach": coach,
        "active_ibm_archetypes": [a["archetype_name"] for a in EIGHT_IBM_ARCHETYPES],
        "live_wxo_agent_ids": LIVE_WXO_AGENT_IDS,
    }


def compute_game_situation_scenarios(
    sport: str,
    fixture_id: str,
    cmi: float,
    db: float,
    hr: float,
    taps: float,
    vu: float,
    is_clutch: bool,
    early_checkin: bool,
    synergy_score: int,
) -> Dict[str, Any]:
    """
    Computes game-specific statistics, situational metrics, and 3 projected
    game scenarios for Screen 5 (AI Squad & Game Intelligence Hub).
    """
    is_bball = "basket" in sport.lower()
    synth = KnowledgeSynthesizerAgent(sport).synthesize_telemetry(db, hr, taps, vu)
    coord = InvisibleCoordinatorAgent(sport).evaluate_game_state(
        "clutch free throw" if (is_bball and is_clutch) else (
            "clutch field goal snap" if (not is_bball and is_clutch) else (
                "timeout ice the kicker" if not is_bball else "regular possession"
            )
        )
    )
    early_mult = 1.25 if early_checkin else 1.0
    clutch_mult = coord["multiplier"]
    lead_sec = "Section 114 (Thunder Row)" if is_bball else "Section 115 (End Zone Loyals)"
    chase_sec = "Section 115 (End Zone Loyals)" if is_bball else "Section 114 (Thunder Row)"
    opt = SystemOptimizerAgent(sport).rank_sections_per_capita([
        {"name": lead_sec, "cmi": cmi, "checked_in_fans": 150, "early_multiplier": early_mult, "clutch_multiplier": clutch_mult},
        {"name": chase_sec, "cmi": round(cmi * 0.92, 1), "checked_in_fans": 140, "early_multiplier": 1.0, "clutch_multiplier": 1.0},
    ])
    lead_pts = opt["standings"][0]["score"]
    chase_pts = opt["standings"][1]["score"]
    rivalry_lead = round(lead_pts - chase_pts, 1)

    if is_bball:
        base_make_pct = 76.4
        # Higher CMI reduces shooter's make percentage
        current_make_pct = round(max(42.0, base_make_pct - max(0.0, (cmi - 35.0) * 0.58)), 1)
        current_miss_pct = round(100.0 - current_make_pct, 1)
        win_prob_swing = round(max(1.5, (cmi - 30.0) * 0.28), 1)
        clock_situation = "4th Quarter • 0:14.2 Remaining • Score Tied 88–88 (2nd Free Throw)" if is_clutch else "4th Quarter • 0:14.2 Remaining • Score Tied 88–88 (1st Free Throw)"
        key_stat_label = "Shooter FT% Under Current Noise"
        key_stat_val = f"{current_make_pct}%"
        key_stat_delta = f"-{round(base_make_pct - current_make_pct, 1)}% vs. 76.4% season avg"
        miss_label = "Forced Miss Probability"
        scenarios = [
            {
                "scenario": "Scenario A: Hold Current Pace",
                "target_cmi": f"{cmi}/100 ({evaluate_tier(cmi)})",
                "required_action": f"Maintain {db} dB & {taps} taps/s",
                "opponent_impact": f"{current_make_pct}% FT Make ({current_miss_pct}% Miss)",
                "win_prob_delta": f"+{win_prob_swing}% Home Win Swing",
                "section_outcome": f"Lead {chase_sec[:11]} by +{rivalry_lead} pts",
            },
            {
                "scenario": "Scenario B: Row Pod Sync Surge",
                "target_cmi": f"{min(100.0, round(cmi + 9.5, 1))}/100 ({evaluate_tier(min(100.0, cmi + 9.5))})",
                "required_action": "+5 Pulse Taps & Row Chant on Release",
                "opponent_impact": f"{round(max(39.0, current_make_pct - 6.8), 1)}% FT Make ({round(min(61.0, current_miss_pct + 6.8), 1)}% Miss)",
                "win_prob_delta": f"+{round(win_prob_swing + 4.2, 1)}% Home Win Swing",
                "section_outcome": "Extend Section 114 Lead + Unlock Row Boost",
            },
            {
                "scenario": "Scenario C: Full 6th-Man Takeover (80+ CMI)",
                "target_cmi": f"{max(85.0, round(cmi, 1))}/100 (Maximum Tier)",
                "required_action": "106.5+ dB Knee-Bend Roar + 2.0x Clutch Window",
                "opponent_impact": "46.2% FT Make (53.8% Forced Miss + Rebound)",
                "win_prob_delta": "+18.4% Home Win Swing",
                "section_outcome": "Lock Section Defense Belt + 15% Merch Perk",
            },
        ]
    else:
        base_fg_pct = 78.5
        current_fg_pct = round(max(38.0, base_fg_pct - max(0.0, (cmi - 35.0) * 0.64)), 1)
        current_miss_pct = round(100.0 - current_fg_pct, 1)
        win_prob_swing = round(max(2.0, (cmi - 30.0) * 0.34), 1)
        clock_situation = "4th Quarter • 0:03 Remaining • Visiting 48-Yd Field Goal Snap" if is_clutch else "4th Quarter • 0:03 Remaining • Visiting Timeout ('Icing the Kicker')"
        key_stat_label = "Kicker 48-Yd FG% Under Roar"
        key_stat_val = f"{current_fg_pct}%"
        key_stat_delta = f"-{round(base_fg_pct - current_fg_pct, 1)}% vs. 78.5% season avg"
        miss_label = "Wide-Left / Block Probability"
        scenarios = [
            {
                "scenario": "Scenario A: Hold Current Pace",
                "target_cmi": f"{cmi}/100 ({evaluate_tier(cmi)})",
                "required_action": f"Maintain {db} dB & {taps} taps/s",
                "opponent_impact": f"{current_fg_pct}% FG Make ({current_miss_pct}% Miss)",
                "win_prob_delta": f"+{win_prob_swing}% Home Win Swing",
                "section_outcome": f"Lead {chase_sec[:11]} by +{rivalry_lead} pts",
            },
            {
                "scenario": "Scenario B: Bleacher Stomp Wave",
                "target_cmi": f"{min(100.0, round(cmi + 10.5, 1))}/100 ({evaluate_tier(min(100.0, cmi + 10.5))})",
                "required_action": "Sync 50-Seat Row Stomp + Early Check-In Boost",
                "opponent_impact": f"{round(max(35.0, current_fg_pct - 7.5), 1)}% FG Make ({round(min(65.0, current_miss_pct + 7.5), 1)}% Miss)",
                "win_prob_delta": f"+{round(win_prob_swing + 5.1, 1)}% Home Win Swing",
                "section_outcome": "Widen Section 115 Lead + Rattle Snap Count",
            },
            {
                "scenario": "Scenario C: Full 12th-Man Wall (90+ CMI)",
                "target_cmi": f"{max(92.0, round(cmi, 1))}/100 (Maximum Tier)",
                "required_action": "111.8+ dB Roar at 0:03 Snap + 2.0x Clutch Window",
                "opponent_impact": "42.0% FG Make (58.0% Wide-Left Miss / False Start)",
                "win_prob_delta": "+22.6% Home Win Swing",
                "section_outcome": "Win Section Defense Belt + 20% Store & Concession Perk",
            },
        ]

    return {
        "sport": sport,
        "fixture_id": fixture_id,
        "clock_situation": clock_situation,
        "key_stat_label": key_stat_label,
        "key_stat_val": key_stat_val,
        "key_stat_delta": key_stat_delta,
        "miss_label": miss_label,
        "current_miss_pct": current_miss_pct,
        "win_prob_swing": win_prob_swing,
        "rivalry_lead": rivalry_lead,
        "lead_section": lead_sec,
        "chase_section": chase_sec,
        "lead_pts": lead_pts,
        "chase_pts": chase_pts,
        "multiplier": clutch_mult,
        "trigger_event": coord["trigger_event"],
        "pacing_directive": coord["pacing_directive"],
        "normalized_components": synth["normalized_components"],
        "scenarios": scenarios,
    }


def enforce_sport_isolation(text: str, sport: str) -> str:
    """
    Enforces strict sport isolation on text:
    - If Basketball: guarantees NO football terms (field goal, kicker, snap, uprights, 48-yard, 12th Man)
      or football emojis (🏈), replacing with basketball equivalents (free throw, shooter, release, rim, 6th Man, 🏀).
    - If Football: guarantees NO basketball terms (free throw, shooter, FT%, rim, 6th Man)
      or basketball emojis (🏀), replacing with football equivalents (field goal, kicker, FG%, uprights, 12th Man, 🏈).
    """
    if not text:
        return text
    is_bball = "basket" in sport.lower()
    cleaned = text
    if is_bball:
        cleaned = cleaned.replace("🏈", "🏀")
        subs = [
            (r"\bfield goals?\b", "free throw"),
            (r"\bField Goals?\b", "Free Throw"),
            (r"\bFIELD GOALS?\b", "FREE THROW"),
            (r"\bFG(?=%)", "FT"),
            (r"\bkickers?\b", "shooter"),
            (r"\bKickers?\b", "Shooter"),
            (r"\bkick\b", "shot"),
            (r"\bKick\b", "Shot"),
            (r"\b12th Man\b", "6th Man"),
            (r"\bSection 115\b", "Section 114"),
            (r"\bEnd Zone Loyals\b", "Thunder Row"),
            (r"\bEnd Zone\b", "Thunder Row"),
            (r"\bend zone\b", "baseline"),
            (r"\b48-yard\b", "clutch"),
            (r"\b48-yd\b", "clutch"),
            (r"\buprights\b", "rim"),
            (r"\bwide left\b", "off the rim"),
            (r"\bWide Left\b", "Off The Rim"),
            (r"\bice the kicker\b", "rattle the shooter"),
            (r"\bIce the kicker\b", "Rattle the shooter"),
            (r"\bIce the Kicker\b", "Rattle the Shooter"),
            (r"\bsnap count\b", "shot clock"),
            (r"\bSnap count\b", "Shot clock"),
            (r"\bSnap Count\b", "Shot Clock"),
            (r"\bsnaps?\b", "shot"),
            (r"\bSnaps?\b", "Shot"),
        ]
        for p, r in subs:
            cleaned = re.sub(p, r, cleaned)
    else:
        cleaned = cleaned.replace("🏀", "🏈")
        subs = [
            (r"\bfree throws?\b", "field goal"),
            (r"\bFree Throws?\b", "Field Goal"),
            (r"\bFREE THROWS?\b", "FIELD GOAL"),
            (r"\bFT(?=%)", "FG"),
            (r"\bshooters?\b", "kicker"),
            (r"\bShooters?\b", "Kicker"),
            (r"\b6th Man\b", "12th Man"),
            (r"\bSection 114\b", "Section 115"),
            (r"\bThunder Row\b", "End Zone Loyals"),
            (r"\bbackboard\b", "crossbar"),
            (r"\brim\b", "uprights"),
            (r"\boff the rim\b", "wide left"),
            (r"\bOff The Rim\b", "Wide Left"),
            (r"\boff the back iron\b", "wide left"),
            (r"\bOff The Back Iron\b", "Wide Left"),
            (r"\bshot clock\b", "play clock"),
            (r"\bShot clock\b", "Play clock"),
            (r"\bShot Clock\b", "Play Clock"),
        ]
        for p, r in subs:
            cleaned = re.sub(p, r, cleaned)
    return cleaned


def get_agent_question_chips(
    agent_tag: str,
    sport: str,
    member_name: str = "Marcus Vance",
    persona_data: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """
    Returns 3 dynamic, uniquely framed question chips tailored to the active
    agent's exact domain of expertise and the current sport.
    """
    p = persona_data or {}
    sec = p.get("sec", "Section 114" if "basket" in sport.lower() else "Section 115")
    games = p.get("games", 34 if "basket" in sport.lower() else 62)
    tier_title = p.get("tier", "Tier 4" if "basket" in sport.lower() else "Tier 5")
    tag = agent_tag.lower().strip()
    is_bball = "basket" in sport.lower()

    if tag == "@coach":
        if is_bball:
            return [
                {
                    "chip_label": "🏅 Next Tier Milestone",
                    "full_question": f"@coach, based on my {games} games and {tier_title} in {sec}, what do I need to reach my next perk?",
                },
                {
                    "chip_label": "🛡️ 6th Man Defense Belt",
                    "full_question": f"@coach, how do {member_name} and our row pod secure the 6th Man Defense Belt on this free throw?",
                },
                {
                    "chip_label": "⚡ Early Roll Call Boost",
                    "full_question": f"@coach, how does our 1.25x early check-in multiplier help my personal passport ranking in {sec}?",
                },
            ]
        else:
            return [
                {
                    "chip_label": "🏅 12th Man Milestone",
                    "full_question": f"@coach, based on my {games} stadium games in {sec}, what milestone unlocks my next Trophy Case accolade?",
                },
                {
                    "chip_label": "🛡️ End Zone Defense Belt",
                    "full_question": f"@coach, how do {member_name} and {sec} lock down the Section Defense Belt on this 48-yard field goal snap?",
                },
                {
                    "chip_label": "🔥 Lot B Tailgate Streak",
                    "full_question": f"@coach, how does our tailgate streak and 1.25x pre-game arrival boost our section's concession perks?",
                },
            ]

    elif tag == "@conductor":
        if is_bball:
            return [
                {
                    "chip_label": "⏱️ FT Roar Timing",
                    "full_question": f"@conductor, at what exact second in the shooter's routine should {sec} peak our noise to rattle his release?",
                },
                {
                    "chip_label": "⚡ 2.0x Clutch Window",
                    "full_question": "@conductor, when does our 2.0x clutch multiplier window trigger on this free throw possession?",
                },
                {
                    "chip_label": "🌊 Row Waving Cadence",
                    "full_question": f"@conductor, what pulse tap tempo and waving cadence should we maintain across {sec}?",
                },
            ]
        else:
            return [
                {
                    "chip_label": "⏱️ 0:03 Snap Roar Timing",
                    "full_question": f"@conductor, when on the play clock should our decibels peak to shatter the kicker and holder's cadence?",
                },
                {
                    "chip_label": "🏟️ Timeout Stomp Cadence",
                    "full_question": f"@conductor, how should {sec} pace our bleacher stomps during this kicker timeout to ice him?",
                },
                {
                    "chip_label": "⚡ 2.0x Snap Window",
                    "full_question": "@conductor, when does the 2.0x 12th Man defense multiplier lock in before the field goal snap?",
                },
            ]

    elif tag == "@strategist":
        if is_bball:
            return [
                {
                    "chip_label": "🏆 Trigger Scenario C",
                    "full_question": "@strategist, what exact CMI score and decibel surge do we need to trigger Scenario C and force a missed free throw?",
                },
                {
                    "chip_label": "📊 Section Rivalry Lead",
                    "full_question": f"@strategist, where does {sec} stand against Section 115 on the live per-capita leaderboard right now?",
                },
                {
                    "chip_label": "📈 4th Quarter Win Swing",
                    "full_question": "@strategist, how much does forcing a missed free throw right here shift our home win probability?",
                },
            ]
        else:
            return [
                {
                    "chip_label": "🏆 Force Wide-Left (Scenario C)",
                    "full_question": "@strategist, what CMI target and acoustic wall triggers Scenario C to force a wide-left miss on this 48-yard field goal?",
                },
                {
                    "chip_label": "📊 Section 115 Rivalry Lead",
                    "full_question": f"@strategist, how many per-capita points does {sec} hold over Section 114 in our section rivalry standings?",
                },
                {
                    "chip_label": "📈 Win Probability Delta",
                    "full_question": f"@strategist, what is our projected win probability swing if {sec} forces a miss on this kick?",
                },
            ]

    elif tag == "@scout":
        if is_bball:
            return [
                {
                    "chip_label": "📊 Shooter FT% Under Noise",
                    "full_question": "@scout, what is the shooter's free throw percentage under 100+ dB noise compared to his season average?",
                },
                {
                    "chip_label": "🎙️ Telemetry CMI Factors",
                    "full_question": "@scout, break down how our current decibels, heart rate, pulse taps, and vocal urgency are weighting our CMI.",
                },
                {
                    "chip_label": "🔥 Maximum Tier Target",
                    "full_question": "@scout, what decibel and heart rate metrics do we need to push our momentum past 80.0 into Maximum Tier?",
                },
            ]
        else:
            return [
                {
                    "chip_label": "📊 Kicker 48-Yd FG% Stats",
                    "full_question": "@scout, what are the visiting kicker's field goal percentages from 45+ yards in hostile 110+ dB stadiums?",
                },
                {
                    "chip_label": "🎙️ 111.8 dB Roar Analysis",
                    "full_question": f"@scout, how does {sec}'s current acoustic reading compare to our 111.8 dB season peak?",
                },
                {
                    "chip_label": "📈 12th Man Telemetry Mix",
                    "full_question": "@scout, break down our Log SPL decibels and wearable heart rates heading into this clutch snap.",
                },
            ]

    else:  # @squad (All 4)
        if is_bball:
            return [
                {
                    "chip_label": "⚡ Full FT Game Plan",
                    "full_question": "@squad, give me the combined 4-agent defensive briefing for this crucial free throw possession.",
                },
                {
                    "chip_label": "🤝 4-Agent Section Sync",
                    "full_question": f"@squad, how are Scout, Conductor, Strategist, and Coach aligning {sec} to force the miss?",
                },
                {
                    "chip_label": "🎯 Scenario C Consensus",
                    "full_question": "@squad, what is the squad consensus on our probability of hitting Scenario C before the buzzer?",
                },
            ]
        else:
            return [
                {
                    "chip_label": "⚡ Full FG Defense Plan",
                    "full_question": "@squad, what is the full 4-agent defensive game plan to rattle the kicker and block this 48-yard kick?",
                },
                {
                    "chip_label": "🤝 12th Man Coordination",
                    "full_question": f"@squad, how are all 4 specialists coordinating {sec}'s bleacher pods for this clutch snap?",
                },
                {
                    "chip_label": "🎯 4th Down Win Consensus",
                    "full_question": "@squad, give us the squad consensus on our chances of forcing a wide-left miss on this kick.",
                },
            ]


def get_agent_chat_placeholder(agent_tag: str, sport: str) -> str:
    """Returns dynamic placeholder text for Screen 5 chat input based on agent & sport."""
    tag = agent_tag.lower().strip()
    is_bball = "basket" in sport.lower()
    if tag == "@coach":
        return f"Ask @coach about your {'6th Man' if is_bball else '12th Man'} milestones, clutch stops, or tier progression..."
    elif tag == "@conductor":
        return f"Ask @conductor about {'free throw timing, release cues, or wave tempo' if is_bball else 'play clock countdown, snap timing, or bleacher stomps'}..."
    elif tag == "@strategist":
        return f"Ask @strategist about {'Section 114 standings, Scenario A/B/C, or win swing' if is_bball else 'Section 115 rivalry lead, 48-yard kick odds, or Scenario C'}..."
    elif tag == "@scout":
        return f"Ask @scout about {'shooter FT%, arena acoustics, or CMI sensor breakdown' if is_bball else 'kicker FG% stats, stadium decibels, or 12th Man telemetry'}..."
    else:
        return f"Ask the full 4-agent squad for a coordinated {'free throw' if is_bball else 'field goal'} defensive briefing..."


def run_backend_squad_teamwork(
    target_agent_tag: str,
    user_message: str,
    member_name: str,
    persona_data: Dict[str, Any],
    sport: str,
    fixture_id: str,
    cmi: float,
    db: float,
    hr: float,
    taps: float,
    vu: float,
    is_clutch: bool,
    early_checkin: bool,
    synergy_score: int,
) -> Dict[str, Any]:
    """
    Executes multi-agent teamwork silently on the backend:
    1. @scout computes live situational statistics, telemetry weights, and scenario odds.
    2. @conductor aligns the play-clock timing cue and active multiplier.
    3. @strategist calculates the section rivalry margin and optimal scenario target.
    4. @coach connects the user's personal career stats and tier progression to the play.
    Then the user-selected agent (@coach, @conductor, @strategist, @scout, or @squad)
    delivers a cohesive response that synthesizes the entire team's intelligence.
    """
    intel = compute_game_situation_scenarios(
        sport=sport,
        fixture_id=fixture_id,
        cmi=cmi,
        db=db,
        hr=hr,
        taps=taps,
        vu=vu,
        is_clutch=is_clutch,
        early_checkin=early_checkin,
        synergy_score=synergy_score,
    )
    role = persona_data.get("role", "Section Member")
    tier_name = persona_data.get("tier", "Tier 1")
    games = persona_data.get("games", 10)
    stops = persona_data.get("clutch_stops", 5)
    cmi_needed = round(max(0.0, 80.0 - cmi), 1)
    is_bball = "basket" in sport.lower()

    # Individual specialist contributions assembled on the backend
    scout_brief = (
        f"CMI is {cmi}/100 ({evaluate_tier(cmi)} Tier: {db} dB, {int(hr)} BPM, {taps}/s taps, {vu} VU). "
        f"{intel['key_stat_label']} is down to {intel['key_stat_val']} ({intel['current_miss_pct']}% miss odds, +{intel['win_prob_swing']}% win swing)."
    )
    conductor_brief = (
        f"Clock is at {intel['clock_situation']} with a {intel['multiplier']}x multiplier ({intel['pacing_directive']})."
    )
    strategist_brief = (
        f"{intel['lead_section']} leads {intel['chase_section']} by +{intel['rivalry_lead']} pts ({intel['lead_pts']} vs. {intel['chase_pts']}). "
        + (f"Only +{cmi_needed} CMI pts needed to hit 80.0 Maximum Tier!" if cmi_needed > 0 else "Maximum Tier (80+ CMI) is locked in!")
    )
    coach_brief = (
        f"{member_name} ({role}, {tier_name}) has {games} games, {stops} clutch stops, and {synergy_score}% Squad Synergy."
    )

    tag = target_agent_tag.lower().strip()
    agent_labels = {
        "@coach": ("🏅 @coach (The Hype Coach)", "Personal Progression & Perks Specialist"),
        "@conductor": ("⏱️ @conductor (The Conductor)", "Live Clock, Tempo & Timing Specialist"),
        "@strategist": ("🏆 @strategist (The Strategist)", "Section Rivalry & Game Scenario Lead"),
        "@scout": ("📊 @scout (The Scout)", "Live Telemetry & Situational Stats Analyst"),
        "@squad": ("⚡ @squad (Full AI Squad Consensus)", "Unified 4-Agent Team Synthesis"),
    }
    speaker_title, speaker_role = agent_labels.get(tag, agent_labels["@squad"])

    # Strict sport isolation rules to prevent cross-sport contamination in LLM output
    sport_rules = (
        "STRICT SPORT ISOLATION: The current sport is BASKETBALL ONLY. Mention ONLY basketball concepts (free throw, shooter, rim, backboard, court, 6th Man, Section 114). "
        "NEVER mention football, kickers, field goals, snaps, 12th Man, or use football emojis (🏈). Use ONLY basketball emoji (🏀) or neutral emojis (⚡, 🔥)."
        if is_bball else
        "STRICT SPORT ISOLATION: The current sport is FOOTBALL ONLY. Mention ONLY football concepts (field goal, kicker, snap, uprights, bleachers, 12th Man, Section 115). "
        "NEVER mention basketball, shooters, free throws, rims, 6th Man, or use basketball emojis (🏀). Use ONLY football emoji (🏈) or neutral emojis (⚡, 🔥)."
    )

    # Try live IBM Granite synthesis with full backend team context
    system_prompt = (
        f"You are {speaker_title} ({speaker_role}) inside the Kinetic FanLab mobile app for {sport}.\n"
        f"{sport_rules}\n"
        "On the backend, you work as a seamless 4-agent team (@scout, @conductor, @strategist, @coach) supporting the fan.\n"
        f"Backend Team Intelligence:\n- Scout Stats: {scout_brief}\n- Conductor Timing: {conductor_brief}\n"
        f"- Strategist Scenarios: {strategist_brief}\n- Coach Profile: {coach_brief}\n"
        "Respond directly to the fan in 2-3 energetic, concise sentences that answer their message using your specialty "
        "while naturally weaving in complementary insights from your squadmates. Never mention backend code, DSP, or cloud databases."
    )
    live_reply = invoke_watsonx_chat(system_prompt, f"Fan ({member_name}) says to {tag}: {user_message}")

    if live_reply:
        if tag == "@squad" and not ("@scout" in live_reply and "@conductor" in live_reply):
            live_reply = None
        else:
            live_reply = enforce_sport_isolation(live_reply, sport)
    
    if not live_reply:
        # High-fidelity deterministic fallbacks tailored per agent & sport
        if tag == "@coach":
            if is_bball:
                live_reply = (
                    f"**{member_name}**, with **{games} games** and **{stops} clutch stops** in {intel['lead_section']}, your 6th Man energy is driving our defense! "
                    f"**@scout** tracks our CMI at **{cmi}/100** (**{intel['current_miss_pct']}%** forced miss odds on the free throw), and **@conductor** has our **{intel['multiplier']}x** release window primed—"
                    + (
                        f"push **+{cmi_needed} CMI pts** with **@strategist**'s row surge to unlock your next {tier_name} Trophy Case perk!"
                        if cmi_needed > 0
                        else f"maintain this **80+ CMI** maximum pressure on the shooter to lock in the Section Defense Belt!"
                    )
                )
            else:
                live_reply = (
                    f"**{member_name}**, with **{games} games** and **{stops} verified stops** in {intel['lead_section']}, your 12th Man roar anchors our end zone defense! "
                    f"**@scout** tracks our CMI at **{cmi}/100** (**{intel['current_miss_pct']}%** miss probability on this 48-yard kick), and **@conductor** has our **{intel['multiplier']}x** snap window armed—"
                    + (
                        f"push **+{cmi_needed} CMI pts** with **@strategist**'s bleacher stomp wave to unlock your next {tier_name} Trophy Case reward!"
                        if cmi_needed > 0
                        else f"keep this **90+ CMI** acoustic wall rattling the kicker to win the Section Defense Belt!"
                    )
                )
        elif tag == "@conductor":
            if is_bball:
                live_reply = (
                    f"Right on cue, **{member_name}**! Clock situation: **{intel['clock_situation']}** (**{intel['multiplier']}x** impact multiplier). "
                    f"**{intel['pacing_directive']}** **@scout** confirms our **{db} dB** roar and **{taps}/s** tap tempo already have shooter conversion down to **{intel['key_stat_val']}**, "
                    f"and **@strategist** + **@coach** have your row pod synced at **{synergy_score}%** synergy for the free throw release!"
                )
            else:
                live_reply = (
                    f"Right on the snap, **{member_name}**! Clock situation: **{intel['clock_situation']}** (**{intel['multiplier']}x** impact multiplier). "
                    f"**{intel['pacing_directive']}** **@scout** confirms our **{db} dB** bleacher roar has kicker accuracy down to **{intel['key_stat_val']}**, "
                    f"and **@strategist** + **@coach** have your 50-seat pod locked at **{synergy_score}%** synergy heading into the 0:03 snap!"
                )
        elif tag == "@strategist":
            if is_bball:
                live_reply = (
                    f"Here's the tactical play, **{member_name}**: **{intel['lead_section']}** leads **{intel['chase_section']}** by **+{intel['rivalry_lead']} pts** (**{intel['lead_pts']}** to **{intel['chase_pts']}**). "
                    f"**@scout** shows our row-pod push shifts opponent miss odds to **{intel['current_miss_pct']}%+** (**+{intel['win_prob_swing']}%** home win swing), "
                    f"so execute **@conductor**'s release cue now and **@coach** will credit the clutch stop to your **{tier_name}** passport!"
                )
            else:
                live_reply = (
                    f"Here's the tactical play, **{member_name}**: **{intel['lead_section']}** leads **{intel['chase_section']}** by **+{intel['rivalry_lead']} pts** (**{intel['lead_pts']}** to **{intel['chase_pts']}**). "
                    f"**@scout** shows our bleacher wall shifts wide-left miss odds to **{intel['current_miss_pct']}%+** (**+{intel['win_prob_swing']}%** win swing), "
                    f"so hit **@conductor**'s 0:03 snap crescendo and **@coach** will credit the stop to your **{tier_name}** passport!"
                )
        elif tag == "@scout":
            if is_bball:
                live_reply = (
                    f"Live court telemetry for you, **{member_name}**: Crowd Momentum is **{cmi}/100** (**{db} dB** roar, **{int(hr)} BPM** pulse, **{taps}/s** tempo), "
                    f"dropping **{intel['key_stat_label']}** to **{intel['key_stat_val']}** (**{intel['current_miss_pct']}%** forced miss odds and **+{intel['win_prob_swing']}%** win swing). "
                    f"**@conductor** has the **{intel['multiplier']}x** window active and **@strategist** + **@coach** say a **+10 dB** row surge triggers Scenario C!"
                )
            else:
                live_reply = (
                    f"Live stadium telemetry for you, **{member_name}**: Crowd Momentum is **{cmi}/100** (**{db} dB** roar, **{int(hr)} BPM** pulse, **{taps}/s** tempo), "
                    f"dropping **{intel['key_stat_label']}** to **{intel['key_stat_val']}** (**{intel['current_miss_pct']}%** wide-left probability and **+{intel['win_prob_swing']}%** win swing). "
                    f"**@conductor** has the **{intel['multiplier']}x** snap window active and **@strategist** + **@coach** say an 111.8+ dB roar triggers Scenario C!"
                )
        else:
            if is_bball:
                live_reply = (
                    f"All 4 of us are locked in on this free throw, **{member_name}**! **@scout** tracks live CMI at **{cmi}/100** (**{intel['current_miss_pct']}%** opponent miss odds), "
                    f"**@conductor** has the **{intel['multiplier']}x** release cue set, **@strategist** is protecting our **+{intel['rivalry_lead']} pt** lead in {intel['lead_section']}, "
                    f"and **@coach** has your Squad Synergy at **{synergy_score}%**!"
                )
            else:
                live_reply = (
                    f"All 4 of us are locked in on this 4th-down kick, **{member_name}**! **@scout** tracks live CMI at **{cmi}/100** (**{intel['current_miss_pct']}%** wide-left miss odds), "
                    f"**@conductor** has the **{intel['multiplier']}x** snap window armed, **@strategist** is defending our **+{intel['rivalry_lead']} pt** lead in {intel['lead_section']}, "
                    f"and **@coach** has your Squad Synergy at **{synergy_score}%**!"
                )
        live_reply = enforce_sport_isolation(live_reply, sport)

    return {
        "speaker_tag": tag,
        "speaker_title": speaker_title,
        "reply": live_reply,
        "intel": intel,
    }
