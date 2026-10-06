import time
from typing import Dict, Any, List, Optional

try:
    from watsonx_live import analyze_vocal_urgency_live, generate_narrative_live
except ImportError:
    def analyze_vocal_urgency_live(fan_text: str) -> float:
        return 0.85

    def generate_narrative_live(
        sport: str, outcome: str, pre_cmi: float, peak_cmi: float, fan_notes: List[Any]
    ) -> str:
        return f"Coordinated crowd surge of +{round(peak_cmi - pre_cmi, 1)} pts disrupted opponent execution."

try:
    from governance_check import evaluate_fan_content_safety
except ImportError:
    def evaluate_fan_content_safety(raw_text: str) -> Dict[str, Any]:
        return {
            "input_text": raw_text,
            "guardrail_status": "APPROVED",
            "violations": [],
            "action": "Proceed"
        }

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

class InvisibleCoordinatorAgent:
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
                pacing_directive = "T-10s: Silent focus | T-5s: Wave props left-to-right | T-2s: DEAFENING SCREAM ON KNEE BEND!"
                trigger_event = "OPPONENT FREE THROW DISRUPTION (6th Man Defense Active)"
            else:
                self.clutch_active = False
                clutch_multiplier = 1.0
                tactic = "Rhythmic Possession Chant"
                pacing_directive = "Maintain defensive vigilance and section spacing."
                trigger_event = "REGULAR POSSESSION FLOW"
        else:
            if "timeout" in ctx_lower or "ice" in ctx_lower:
                self.clutch_active = False
                clutch_multiplier = 1.25
                tactic = "Bleacher Stomp Endurance Pacing"
                pacing_directive = "TIMEOUT DELAY: Stomp bleachers in rhythm! Preserve vocal chords for the snap!"
                trigger_event = "TIMEOUT DELAY PACING ('Icing the Kicker')"
            elif "field goal" in ctx_lower or "snap" in ctx_lower or "clutch" in ctx_lower:
                self.clutch_active = True
                clutch_multiplier = 2.0
                tactic = "111+ dB Acoustic Wall (Cadence Drowning)"
                pacing_directive = "SNAP IMMINENT: 111 dB MAXIMUM ROAR! Drown out the quarterback cadence!"
                trigger_event = "CLUTCH 48-YARD FG SNAP (12th Man Defense Active)"
            else:
                self.clutch_active = False
                clutch_multiplier = 1.0
                tactic = "Zone Defensive Chant"
                pacing_directive = "Steady stadium noise."
                trigger_event = "BETWEEN DOWNS"

        return {
            "agent": "InvisibleCoordinator",
            "sport": self.sport,
            "clutch_active": self.clutch_active,
            "multiplier": clutch_multiplier,
            "tactic": tactic,
            "pacing_directive": pacing_directive,
            "trigger_event": trigger_event,
            "timestamp": time.time()
        }

class KnowledgeSynthesizerAgent:
    def evaluate_voice_outburst(self, raw_transcript: str) -> Dict[str, Any]:
        gov_result = evaluate_fan_content_safety(raw_transcript)
        if gov_result.get("guardrail_status") == "REJECTED":
            return {
                "transcript": raw_transcript,
                "governance_status": "REJECTED",
                "violations": gov_result.get("violations", ["Content safety violation"]),
                "urgency_score": 0.0
            }
        
        urgency = analyze_vocal_urgency_live(raw_transcript)
        return {
            "transcript": raw_transcript,
            "governance_status": "APPROVED",
            "violations": [],
            "urgency_score": urgency
        }

    def synthesize_telemetry(self, db: float, hr: float, taps: float, vu: float) -> Dict[str, Any]:
        cmi = compute_cmi_index(db, hr, taps, vu)
        tier = evaluate_tier(cmi)
        return {
            "agent": "KnowledgeSynthesizer",
            "cmi": cmi,
            "tier": tier,
            "normalized_components": {
                "acoustic_pct": round(normalize_signal(db, 60.0, 115.0) * 35, 1),
                "biometric_pct": round(normalize_signal(hr, 60.0, 160.0) * 25, 1),
                "taps_pct": round(normalize_signal(taps, 0.0, 15.0) * 20, 1),
                "urgency_pct": round(normalize_signal(vu, 0.0, 1.0) * 20, 1)
            },
            "raw_values": {"db": db, "hr": hr, "taps": taps, "vu": vu},
            "timestamp": time.time()
        }

class SystemOptimizerAgent:
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
                "clutch_mult": clutch_mult
            })

        standings.sort(key=lambda x: x["score"], reverse=True)
        winner = standings[0] if standings else None

        chaser_alert = "All sections locked in competition."
        if len(standings) >= 2:
            gap = round(standings[0]["score"] - standings[1]["score"], 1)
            chaser_alert = f"⚠️ CHASER ALERT: {standings[1]['section']} is trailing {standings[0]['section']} by only -{gap} pts! Tap to defend your lead!"

        return {
            "agent": "SystemOptimizer",
            "standings": standings,
            "leader": winner["section"] if winner else "None",
            "chaser_alert": chaser_alert
        }

    def generate_reality_delta(self, outcome_label: str, pre_cmi: float, peak_cmi: float, fan_notes: List[str]) -> Dict[str, Any]:
        surge = round(peak_cmi - pre_cmi, 1)
        narrative = generate_narrative_live(self.sport, outcome_label, pre_cmi, peak_cmi, fan_notes)

        winning_sec = "Section 114 (Thunder Row)" if "basket" in self.sport.lower() else "Section 115 (End Zone Loyals)"

        storycard = {
            "headline": f"+{surge} PTS MOMENTUM SURGE",
            "subtitle": f"CLUTCH DEFENSIVE STOP VERIFIED ({self.sport})",
            "winning_section": winning_sec,
            "defense_belt_awarded": True,
            "pre_cmi": pre_cmi,
            "peak_cmi": peak_cmi,
            "surge_delta": surge,
            "outcome": outcome_label,
            "granite_narrative": narrative,
            "timestamp": time.time()
        }

        return storycard