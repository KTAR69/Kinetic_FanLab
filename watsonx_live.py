# ==============================================================================
# Kinetic FanLab — Scaffolded & Refactored via IBM Bob IDE
# IBM Cloud Services: watsonx.ai (Granite 4.0) | watsonx.governance Guardrails
# ==============================================================================

import os
import re
from typing import Any
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WO_API_KEY")
# PROJECT_ID is read from the environment so it never needs to be changed in source.
# Add WO_PROJECT_ID to your .env file. The literal below is the fallback default.
PROJECT_ID = os.getenv("WO_PROJECT_ID", "7be4956c-c4e8-4775-8559-f076dda7cfea")
URL = "https://us-south.ml.cloud.ibm.com"
MODEL_ID = "ibm/granite-4-h-small"

# ---------------------------------------------------------------------------
# Lazy singleton — ModelInference is expensive to construct; build it once.
# ---------------------------------------------------------------------------
_model_instance = None


def to_str(val: Any) -> str:
    """Helper to ensure return type from ModelInference is always a string for Pyright."""
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        return " ".join([to_str(item) for item in val])
    if isinstance(val, dict):
        return str(val.get("generated_text", val))
    return str(val)


def get_model():
    global _model_instance
    if _model_instance is not None:
        return _model_instance
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        if not API_KEY or not PROJECT_ID:
            return None

        credentials = Credentials(url=URL, api_key=API_KEY)
        _model_instance = ModelInference(
            model_id=MODEL_ID,
            credentials=credentials,
            project_id=PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 300,
                "temperature": 0.1,
            },
        )
        return _model_instance
    except Exception as e:
        print(f"[watsonx Live Engine] Fallback active: {e}")
        return None

def analyze_vocal_urgency_live(fan_text: str) -> float:
    model = get_model()
    if not model or not fan_text.strip():
        urgent_words = ["miss", "block", "loud", "defense", "freeze", "rattle", "stop", "noise"]
        hits = sum(1 for w in urgent_words if w in fan_text.lower())
        return min(1.0, round(0.40 + hits * 0.15, 2))
    
    prompt = f"""You are the Kinetic FanLab Vocal Urgency Scorer.
Evaluate the emotional urgency and distraction intensity of this sports fan outburst:
Outburst: "{fan_text}"

Respond with ONLY a single decimal number between 0.00 and 1.00 representing vocal urgency.
Score:"""
    try:
        raw_res = to_str(model.generate_text(prompt=prompt)).strip()
        match = re.search(r"(\d+(\.\d+)?)", raw_res)
        if match:
            val = float(match.group(1))
            return max(0.0, min(1.0, val))
        return 0.75
    except Exception:
        return 0.75

def generate_narrative_live(sport: str, outcome: str, pre_cmi: float, peak_cmi: float, fan_notes: list) -> str:
    """
    Uses IBM Granite to synthesize post-play reality delta.
    Strictly synchronizes narrative points with the official proof of momentum card.
    """
    surge = round(max(0.0, peak_cmi - pre_cmi), 1)
    model = get_model()
    is_basketball = "basket" in sport.lower()
    defense_role = "6th Man" if is_basketball else "12th Man"
    section_name = "Section 114" if is_basketball else "Section 115"
    notes_str = "; ".join(fan_notes[-2:]) if fan_notes else ("Unified cheering" if is_basketball else "Bleacher stomping")

    if not model:
        if surge == 0.0:
            return f"The {sport} atmosphere holds at a focused baseline of {pre_cmi}/100 CMI (+0.0 pts), with {section_name} maintaining position as the play develops."
        else:
            return f"The crowd's acoustic pressure surged by +{surge} pts (peaking at {peak_cmi}/100), amplifying tension on the opponent and directly influencing the {outcome} result."

    if surge == 0.0:
        prompt = f"""You are the Kinetic FanLab Sports AI Engine.
Generate a concise, 2-sentence pre-play baseline anticipation summary explaining the crowd atmosphere before the play begins.
Sport: {sport} ({defense_role})
Situation: {outcome}
Baseline Pressure: {pre_cmi}/100 (+0.0 pts surge)
Recent Fan Atmosphere: "{notes_str}"

Output 2 clear sentences describing the tense, focused baseline concentration of {section_name} awaiting the play at +0.0 pts:"""
    else:
        prompt = f"""You are the Kinetic FanLab Sports AI Engine.
Generate a concise, 2-sentence post-play ecosystem summary explaining how crowd pressure surged and influenced the play.
Sport: {sport} ({defense_role})
Outcome: {outcome}
Pre-Play Baseline: {pre_cmi}/100
Peak In-Game Pressure: {peak_cmi}/100 (+{surge} pt surge)
Recent Fan Outbursts: "{notes_str}"

Output 2 clear sentences explaining how the +{surge} pt crowd surge affected the athlete's concentration and mechanics:"""

    try:
        return to_str(model.generate_text(prompt=prompt)).strip()
    except Exception as e:
        if surge == 0.0:
            return f"The {sport} atmosphere holds at a focused baseline of {pre_cmi}/100 CMI (+0.0 pts), with {section_name} maintaining position as the play develops."
        return f"Crowd momentum surged +{surge} pts directly influencing the {outcome} result."

def summarize_tailgate_chants_live(sport: str, raw_proposals: list) -> list:
    model = get_model()
    proposals_text = "\n".join([f"- {p}" for p in raw_proposals])
    
    if not model:
        if "basket" in sport.lower():
            return [
                "1. MISS IT! OFF THE RIM! - Synchronized side-to-side waving at 10s release",
                "2. BRING THE NOISE! - High-frequency piercing chant on shooter knee-bend",
                "3. DEFENSE ON THREE! - Section 114 unified wave prompt"
            ]
        else:
            return [
                "1. BLOCK THAT KICK! - Sustained 111 dB roar on 0:03 snap",
                "2. ICE THE KICKER! - Rhythmic low-end bleacher stomps during timeout delay",
                "3. THIRD DOWN WALL! - Pre-snap acoustic crescendo breaking QB cadence"
            ]
            
    prompt = f"""You are the Kinetic FanLab Tailgate Coordinator powered by IBM Granite.
Synthesize the following raw fan chant proposals for this week's {sport} game into the TOP 3 unified defensive stadium chants.
Each chant must be punchy, rhythmic, and include an exact timing cue.

Raw Fan Proposals:
{proposals_text}

Output ONLY the top 3 synthesized chants formatted as:
1. [Chant Text] - [Timing Cue]
2. [Chant Text] - [Timing Cue]
3. [Chant Text] - [Timing Cue]"""

    try:
        raw_res = to_str(model.generate_text(prompt=prompt)).strip()
        lines = [line.strip() for line in raw_res.split("\n") if line.strip() and line.strip()[0].isdigit()]
        if len(lines) >= 3:
            return lines[:3]
        return lines if lines else ["1. MISS IT! - On release", "2. BRING THE NOISE! - Continuous", "3. DEFENSE! - Bleacher stomp"]
    except Exception as e:
        print(f"[watsonx Live Tailgate Engine] Error: {e}")
        return ["1. MISS IT! OFF THE RIM! - On release", "2. BRING THE NOISE! - Continuous", "3. DEFENSE ON THREE! - Coordinated"]