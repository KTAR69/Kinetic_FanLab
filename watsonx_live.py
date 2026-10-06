# ==============================================================================
# Kinetic FanLab — Scaffolded & Refactored via IBM Bob IDE
# IBM Cloud Services: watsonx.ai (Granite 4.0) | watsonx.governance Guardrails
# ==============================================================================

import os
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WO_API_KEY")
PROJECT_ID = "7be4956c-c4e8-4775-8559-f076dda7cfea"
URL = "https://us-south.ml.cloud.ibm.com"
MODEL_ID = "ibm/granite-4-h-small"

def to_str(val: object) -> str:
    """Safe type conversion ensuring string output for Pyright."""
    if isinstance(val, str):
        return val.strip()
    return str(val).strip()

def get_model():
    """Initializes and returns the live IBM watsonx ModelInference client."""
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        
        if not API_KEY or not PROJECT_ID:
            return None
            
        credentials = Credentials(url=URL, api_key=API_KEY)
        model = ModelInference(
            model_id=MODEL_ID,
            credentials=credentials,
            project_id=PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 300,
                "temperature": 0.1
            }
        )
        return model
    except Exception as e:
        print(f"[watsonx Live Engine] Fallback active: {e}")
        return None

def analyze_vocal_urgency_live(fan_text: str) -> float:
    """Sends fan text to IBM Granite live on IBM Cloud to extract Urgency Score (0.0 to 1.0)."""
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
        raw_res = to_str(model.generate_text(prompt=prompt))
        match = re.search(r"(\d+(\.\d+)?)", raw_res)
        if match:
            val = float(match.group(1))
            return max(0.0, min(1.0, val))
        return 0.75
    except Exception:
        return 0.75

def generate_narrative_live(sport: str, outcome: str, pre_cmi: float, peak_cmi: float, fan_notes: list) -> str:
    """Calls IBM Granite live to synthesize post-play narrative delta."""
    model = get_model()
    surge = round(peak_cmi - pre_cmi, 1)
    notes_str = '", "'.join(fan_notes[-3:]) if fan_notes else "Crowd roar"
    
    if not model:
        return (
            f"Home crowd momentum surged +{surge} pts (Baseline: {pre_cmi} -> Peak: {peak_cmi}). "
            f"High-intensity vocal conviction ('{notes_str}') directly altered opponent execution during this {sport} possession."
        )
        
    prompt = f"""You are the Kinetic FanLab Sports AI Engine.
Generate a concise, 2-sentence post-play ecosystem summary explaining how crowd pressure influenced the play.
Sport: {sport}
Outcome: {outcome}
Pre-Play Baseline: {pre_cmi}/100
Peak In-Game Pressure: {peak_cmi}/100 (+{surge} pt surge)
Recent Fan Outbursts: "{notes_str}"

Output 2 clear sentences analyzing the crowd's physical and acoustic impact on the play:"""
    try:
        return to_str(model.generate_text(prompt=prompt))
    except Exception as e:
        return f"Crowd momentum surged +{surge} pts directly influencing the {outcome} result."

def summarize_tailgate_chants_live(sport: str, raw_proposals: list) -> list:
    """Calls IBM Granite live to synthesize 36h tailgate chat into top 3 coordinated chants."""
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
        raw_res = to_str(model.generate_text(prompt=prompt))
        lines = [line.strip() for line in raw_res.split("\n") if line.strip() and line.strip()[0].isdigit()]
        if len(lines) >= 3:
            return lines[:3]
        return lines if lines else ["1. MISS IT! - On release", "2. BRING THE NOISE! - Continuous", "3. DEFENSE! - Bleacher stomp"]
    except Exception as e:
        print(f"[watsonx Live Tailgate Engine] Error: {e}")
        return ["1. MISS IT! OFF THE RIM! - On release", "2. BRING THE NOISE! - Continuous", "3. DEFENSE ON THREE! - Coordinated"]