"""
==============================================================================
Kinetic FanLab — IBM watsonx.ai Modern Chat Engine (/ml/v1/text/chat)
Week 5 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Refactored to eliminate SDK deprecation warnings:
1. Migrated from legacy /ml/v1/text/generation to modern /ml/v1/text/chat.
2. Uses `max_tokens` (Chat API contract) instead of `max_new_tokens` to prevent
   `unspecified_max_token` and `invalid_params_warning` on ModelInference.chat().
3. Structured System/User message separation with robust JSON/text extraction.
==============================================================================
"""

import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WO_API_KEY")
PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "7be4956c-c4e8-4775-8559-f076dda7cfea")
URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
MODEL_ID = os.getenv("WATSONX_MODEL_ID", "ibm/granite-4-h-small")

def extract_content(response: Any) -> str:
    """Robustly extracts generated text from both Chat API responses and legacy fallback objects."""
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        # 1. Modern /ml/v1/text/chat response shape
        if "choices" in response and len(response["choices"]) > 0:
            first_choice = response["choices"][0]
            if isinstance(first_choice, dict):
                msg = first_choice.get("message", {})
                if isinstance(msg, dict) and "content" in msg:
                    return str(msg["content"])
        # 2. Legacy /ml/v1/text/generation shape fallback
        if "results" in response and len(response["results"]) > 0:
            return str(response["results"][0].get("generated_text", ""))
        if "generated_text" in response:
            return str(response["generated_text"])
    return str(response)

def get_model():
    """Initializes IBM watsonx.ai ModelInference client with modern parameters."""
    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        if not API_KEY or not PROJECT_ID:
            return None

        credentials = Credentials(url=URL, api_key=API_KEY)
        
        # Modern /ml/v1/text/chat parameters: uses max_tokens (not max_new_tokens)
        model = ModelInference(
            model_id=MODEL_ID,
            credentials=credentials,
            project_id=PROJECT_ID,
            params={
                "max_tokens": 300,
                "temperature": 0.1,
                "top_p": 0.9,
            }
        )
        return model
    except Exception as e:
        print(f"[watsonx Live Engine] Model client initialization fallback: {e}")
        return None

def invoke_watsonx_chat(system_prompt: str, user_prompt: str) -> Optional[str]:
    """
    Invokes the modern watsonx.ai /ml/v1/text/chat API with structured role separation.
    Gracefully falls back to generate_text if the installed SDK version lacks chat.
    """
    model = get_model()
    if not model:
        return None

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        # Use modern /ml/v1/text/chat API
        if hasattr(model, "chat"):
            raw_res = model.chat(messages=messages)
            return extract_content(raw_res).strip()
        elif hasattr(model, "generate_text"):
            # Fallback for older SDK versions
            full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
            raw_res = model.generate_text(prompt=full_prompt)
            return extract_content(raw_res).strip()
    except Exception as e:
        print(f"[watsonx Live Engine] API call exception: {e}")
        return None
    return None

def analyze_vocal_urgency_live(fan_text: str) -> float:
    """
    Evaluates emotional urgency and distraction intensity of fan outburst (0.00–1.00 VU).
    Powered by IBM Granite via modern /ml/v1/text/chat.
    """
    if not fan_text.strip():
        return 0.50

    system_prompt = (
        "You are the Kinetic FanLab Vocal Urgency Scorer.\n"
        "Evaluate the emotional urgency and distraction intensity of a sports fan outburst.\n"
        "Respond with ONLY a single decimal number between 0.00 and 1.00 representing vocal urgency."
    )
    user_prompt = f'Evaluate this fan outburst:\n"{fan_text}"\n\nScore:'

    res = invoke_watsonx_chat(system_prompt, user_prompt)
    if res:
        match = re.search(r"(\d+(\.\d+)?)", res)
        if match:
            val = float(match.group(1))
            return max(0.0, min(1.0, round(val, 2)))

    # Deterministic heuristic fallback if offline
    urgent_words = ["miss", "block", "loud", "defense", "freeze", "rattle", "stop", "noise", "vamos", "ruido"]
    hits = sum(1 for w in urgent_words if w in fan_text.lower())
    return min(1.0, round(0.55 + hits * 0.10, 2))

def generate_narrative_live(sport: str, outcome: str, pre_cmi: float, peak_cmi: float, fan_notes: list) -> str:
    """
    Uses IBM Granite to synthesize post-play reality delta narrative.
    Strictly synchronizes narrative points with the official proof of momentum card.
    """
    surge = round(max(0.0, peak_cmi - pre_cmi), 1)
    is_basketball = "basket" in sport.lower()
    defense_role = "6th Man" if is_basketball else "12th Man"
    section_name = "Section 114 (Thunder Row)" if is_basketball else "Section 115 (End Zone Loyals)"
    notes_str = "; ".join(fan_notes[-2:]) if fan_notes else ("Unified crowd chant" if is_basketball else "Bleacher stomps")

    # Deterministic fallback text
    if surge == 0.0:
        fallback = f"The {sport} atmosphere holds at a focused baseline of {pre_cmi}/100 CMI (+0.0 pts), with {section_name} maintaining position as the play develops."
    else:
        fallback = f"The crowd's acoustic pressure surged by +{surge} pts (peaking at {peak_cmi}/100), amplifying tension on the opponent and directly influencing the {outcome} result."

    system_prompt = (
        f"You are the Kinetic FanLab Sports AI Engine analyzing the in-game impact of {section_name} ({defense_role}).\n"
        "Write exactly 2 clear, punchy sentences explaining how the crowd's acoustic pressure impacted the play."
    )

    if surge == 0.0:
        user_prompt = (
            f"Sport: {sport}\n"
            f"Play Status: {outcome}\n"
            f"Baseline Momentum: {pre_cmi}/100 CMI (+0.0 pts surge)\n"
            f"Atmosphere: {notes_str}\n\n"
            "Explain the tense, focused baseline anticipation before the play execution:"
        )
    else:
        user_prompt = (
            f"Sport: {sport}\n"
            f"Play Outcome: {outcome}\n"
            f"Pre-Play Baseline: {pre_cmi}/100 CMI\n"
            f"Peak In-Game Momentum: {peak_cmi}/100 CMI (+{surge} pt surge)\n"
            f"Fan Outbursts: {notes_str}\n\n"
            "Explain how the verified crowd surge disrupted the opponent's focus and mechanics:"
        )

    res = invoke_watsonx_chat(system_prompt, user_prompt)
    return res if res else fallback

def summarize_tailgate_chants_live(sport: str, raw_proposals: list) -> list:
    """
    Synthesizes raw fan chant proposals into the top 3 unified stadium chants.
    """
    is_basketball = "basket" in sport.lower()
    default_chants = [
        "1. MISS IT! OFF THE RIM! - Synchronized side-to-side waving at 10s release",
        "2. BRING THE NOISE! - Piercing acoustic roar on shooter knee bend",
        "3. DEFENSE ON THREE! - Section 114 unified wave prompt"
    ] if is_basketball else [
        "1. BLOCK THAT KICK! - Sustained 111 dB roar on 0:03 snap",
        "2. ICE THE KICKER! - Rhythmic low-end bleacher stomps during timeout delay",
        "3. THIRD DOWN WALL! - Pre-snap acoustic crescendo breaking QB cadence"
    ]

    if not raw_proposals:
        return default_chants

    proposals_text = "\n".join([f"- {p}" for p in raw_proposals])
    system_prompt = (
        "You are the Kinetic FanLab Tailgate Coordinator powered by IBM Granite.\n"
        f"Synthesize raw fan chant proposals for this week's {sport} game into the TOP 3 unified defensive stadium chants.\n"
        "Each chant must be punchy, rhythmic, and include an exact timing cue.\n"
        "Format ONLY as:\n1. [Chant] - [Timing Cue]\n2. [Chant] - [Timing Cue]\n3. [Chant] - [Timing Cue]"
    )
    user_prompt = f"Raw Fan Proposals:\n{proposals_text}"

    res = invoke_watsonx_chat(system_prompt, user_prompt)
    if res:
        lines = [line.strip() for line in res.split("\n") if line.strip() and line.strip()[0].isdigit()]
        if len(lines) >= 3:
            return lines[:3]
        if lines:
            return lines

    return default_chants
