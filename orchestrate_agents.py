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

# ---------------------------------------------------------------------------
# Section AI Co-Captains — role-aware, warm, motivating dialogue agents
# ---------------------------------------------------------------------------

_BASKETBALL_LEADERS = {"Student Section Director"}
_BASKETBALL_SPECIALISTS = {"Hype & Prop Captain", "Vocal Tactician"}
_BASKETBALL_ROOKIES = {"Rookie Section Member"}

_FOOTBALL_LEADERS = {"10-Year Season Ticket Holder"}
_FOOTBALL_SPECIALISTS = {"Lot B Tailgate Host", "Biometric & Tech Superfan"}
_FOOTBALL_ROOKIES = {"General Season Ticket Holder"}


def _build_conductor_line(
    member_name: str,
    role: str,
    sport: str,
    tier: str,
    is_clutch: bool,
) -> str:
    """The Conductor — sets the tempo, reads the room, deploys the synchronized wave."""
    is_basketball = "basket" in sport.lower()

    if role in _BASKETBALL_LEADERS or role in _FOOTBALL_LEADERS:
        if is_basketball:
            signal = "DEAFENING SCREAM" if is_clutch else "steady hoop chant"
            return (
                f"🎵 The Conductor — {member_name}, you ARE the 6th Man heartbeat right now. "
                f"Section 114 eyes are on you. Call the {signal} on that 10-second free-throw clock. "
                f"Let's make this hoop feel impossible for them."
            )
        else:
            signal = "111 dB WALL" if is_clutch else "bleacher stomp rhythm"
            return (
                f"🎵 The Conductor — {member_name}, ten years in Section 115 says you know exactly when "
                f"to lift the crowd. Hold the {signal} through the timeout. "
                f"That kicker is already feeling the 12th Man pressure."
            )

    if role in _BASKETBALL_SPECIALISTS:
        if role == "Hype & Prop Captain":
            wave = "thunderstick wave" if not is_clutch else "LEFT-RIGHT synchronized wave on knee bend"
            return (
                f"🎵 The Conductor — Elena, your {wave} is the visual anchor for the whole section. "
                f"When that shooter grips the ball, you lead — Section 114 follows. "
                f"We trust your timing completely. The hoop is ours to defend."
            )
        else:
            chant = "MISS IT! OFF THE RIM!" if is_clutch else "keep the defensive chant alive"
            return (
                f"🎵 The Conductor — Devon, your vocal cadence sets the tempo for everyone around you. "
                f"Hit {chant} right when the elbow bends. "
                f"Your voice log is already elite — let's add another clutch stop to Section 114's record."
            )

    if role in _FOOTBALL_SPECIALISTS:
        if role == "Lot B Tailgate Host":
            energy = "3rd down redzone roar" if is_clutch else "sustained bleacher stomp"
            return (
                f"🎵 The Conductor — Carlos, that tailgate energy you brought from Lot B? "
                f"Carry it straight to row 18. Lead the {energy} and Section 115 will lock in. "
                f"The kicker is about to hear the whole End Zone Loyals crew."
            )
        else:
            beat = "sync your heart rate spike" if is_clutch else "keep your biometric pacing steady"
            return (
                f"🎵 The Conductor — Maya, your wearable data is the section's pulse monitor. "
                f"{beat.capitalize()} with the crowd wave. "
                f"When Section 115 sees your tap rate go up, they know it's time to get loud at the 0:03 snap."
            )

    # Rookies / General members — welcoming, zero pressure
    if is_basketball:
        return (
            f"🎵 The Conductor — Welcome, {member_name}! Section 114 is really glad you're here. "
            f"You don't need to do anything special — just cheer along with us at the hoop when the free throw goes up. "
            f"Every voice in Thunder Row counts, and yours matters just as much as everyone else's. Enjoy the game! 🏀"
        )
    else:
        return (
            f"🎵 The Conductor — Hey {member_name}, so glad you joined Section 115! "
            f"There's no pressure at all — just feel the bleacher energy and stomp along when the crowd rises. "
            f"Every single fan in the End Zone Loyals makes the 12th Man wall stronger. Welcome home! 🏈"
        )


def _build_scout_line(
    member_name: str,
    role: str,
    sport: str,
    tier: str,
    cmi: float,
) -> str:
    """The Scout — reads live telemetry, surfaces situational insight, encourages action."""
    is_basketball = "basket" in sport.lower()

    if role in _BASKETBALL_LEADERS or role in _FOOTBALL_LEADERS:
        if is_basketball:
            return (
                f"🔭 The Scout — {member_name}, live CMI is at {cmi}/100. "
                f"Acoustic trend shows the section is coiling for a big push. "
                f"Historical data says a 6th Man surge above 80 pts correlates with a 68% miss rate on clutch free throws. "
                f"You know what to call — we're ready to back you up."
            )
        else:
            return (
                f"🔭 The Scout — {member_name}, CMI sitting at {cmi}/100 going into this snap. "
                f"The last three timeout-iced kickers facing 111+ dB missed two of them. "
                f"Section 115's bleacher stomp frequency is already pushing the low-frequency wall. "
                f"Your leadership sets the ceiling — take us there."
            )

    if role in _BASKETBALL_SPECIALISTS:
        if role == "Hype & Prop Captain":
            return (
                f"🔭 The Scout — Elena, current acoustic CMI is {cmi}/100. "
                f"Visual disruption props are most effective when timed within the 10-second free-throw clock window. "
                f"Section 114 hoop defense is locked in — your thundersticks are the X-factor right now."
            )
        else:
            return (
                f"🔭 The Scout — Devon, vocal urgency readings on the section are tracking strong. "
                f"CMI at {cmi}/100. Your chant leadership in the last clutch possession pushed the section's "
                f"vocal score +0.12 VU. Keep the high-frequency energy alive around the hoop."
            )

    if role in _FOOTBALL_SPECIALISTS:
        if role == "Lot B Tailgate Host":
            return (
                f"🔭 The Scout — Carlos, fan energy data shows Section 115 early check-in is at 87%. "
                f"The tailgate rally you led is directly reflected in that number — CMI is at {cmi}/100. "
                f"3rd down redzone stands are where that community cohesion pays off. Great work getting everyone here."
            )
        else:
            return (
                f"🔭 The Scout — Maya, your wearable data sync is giving us the cleanest biometric signal in the section. "
                f"Current heart rate variance suggests the crowd is primed for a cardiac stress spike at the 0:03 snap. "
                f"CMI at {cmi}/100. You're our most accurate data anchor in Section 115. Keep it coming!"
            )

    if is_basketball:
        return (
            f"🔭 The Scout — {member_name}, Section 114 CMI is at {cmi}/100 — every fan in Thunder Row is contributing to that. "
            f"Your presence here today literally adds to the crowd pressure on the free-throw line. "
            f"No experience needed — just stay loud and have fun at the hoop! 🏀"
        )
    else:
        return (
            f"🔭 The Scout — {member_name}, Section 115 CMI is reading {cmi}/100 and every person in the bleachers helps. "
            f"Your cheering adds real acoustic pressure on that kicker at the 0:03 snap. "
            f"Just be yourself and enjoy — you're already part of the 12th Man wall! 🏈"
        )


def _build_strategist_line(
    member_name: str,
    role: str,
    sport: str,
    tier: str,
    is_clutch: bool,
    cmi: float,
) -> str:
    """The Strategist — game-plan advisor, tactic deployer, section synergy builder."""
    is_basketball = "basket" in sport.lower()

    if role in _BASKETBALL_LEADERS or role in _FOOTBALL_LEADERS:
        if is_basketball:
            tactic = "synchronized thunderstick wave + piercing scream on knee bend" if is_clutch else "rhythmic possession chant to wear down the shooter"
            return (
                f"🧠 The Strategist — {member_name}, the play call for this possession is {tactic}. "
                f"Signal the section at T-5 seconds on the free-throw clock. "
                f"A 6th Man wall above 100 dB at the hoop release is our defensive target. You've done it before. Let's go!"
            )
        else:
            tactic = "sustained 111 dB acoustic wall at the 0:03 snap" if is_clutch else "bleacher stomp endurance pacing through the full timeout delay"
            return (
                f"🧠 The Strategist — {member_name}, game plan is {tactic}. "
                f"Section 115's 12th Man protocol says the kicker has already heard 62 games worth of End Zone Loyals pressure. "
                f"Hold the wall through the snap — this is what we've been building toward."
            )

    if role in _BASKETBALL_SPECIALISTS:
        if role == "Hype & Prop Captain":
            tactic = "left-right wave on the shooter's second dribble, hold through the release" if is_clutch else "steady prop visibility to maintain baseline hoop disruption"
            return (
                f"🧠 The Strategist — Elena, execute the {tactic}. "
                f"Your prop timing is the visual trigger that sets the whole section in motion. "
                f"The 6th Man needs that synchronized moment to hit maximum disruption on the free throw. You've got this."
            )
        else:
            chant = "MISS IT! OFF THE RIM! right as the elbow snaps up" if is_clutch else "start a low-level DEFENSE chant to build tension"
            return (
                f"🧠 The Strategist — Devon, call the {chant}. "
                f"Your chant leadership is the sonic blueprint for Section 114 around the hoop. "
                f"Own the 6th Man moment — we're all following your lead."
            )

    if role in _FOOTBALL_SPECIALISTS:
        if role == "Lot B Tailgate Host":
            tactic = "pump up the bleacher stomp in rows 17-20 for the redzone snap" if is_clutch else "coordinate a rolling timeout stomp wave to keep the kicker cold"
            return (
                f"🧠 The Strategist — Carlos, your assignment is to {tactic}. "
                f"The community you built at Lot B is Section 115's social backbone. "
                f"Channel that into one loud, unified 12th Man roar when that 0:03 snap hits."
            )
        else:
            tactic = "flag peak cardiac stress window for the snap — that's when wearable-synced taps hit maximum" if is_clutch else "log baseline biometrics through the timeout to track the crowd's stress buildup"
            return (
                f"🧠 The Strategist — Maya, {tactic}. "
                f"Your tech lens on Section 115 turns raw fan energy into real defensive intelligence. "
                f"The 12th Man wall is stronger because you're tracking it. Keep that data flowing!"
            )

    if is_basketball:
        return (
            f"🧠 The Strategist — {member_name}, here's the only thing we need from you: "
            f"when the crowd rises at the free-throw line, rise with them. Clap, shout, wave — whatever feels natural. "
            f"Section 114 Thunder Row is a family, and every 6th Man voice builds the wall around the hoop. "
            f"You're going to have a blast — we promise! 🏀"
        )
    else:
        return (
            f"🧠 The Strategist — {member_name}, your only playbook tonight: "
            f"when Section 115 stomps, stomp. When they roar at the snap, roar with them. "
            f"The 12th Man isn't about experience — it's about heart. "
            f"You've got that already or you wouldn't be here in the End Zone Loyals bleachers! 🏈"
        )


def get_co_captain_huddle(
    member_name: str,
    persona_data: Dict[str, Any],
    sport: str,
    cmi: float,
    is_clutch: bool,
) -> Dict[str, str]:
    """
    Returns a dict of three Co-Captain speech lines tailored to the active member.

    Args:
        member_name: Display name of the fan (e.g. "Marcus Vance").
        persona_data: The persona dict from PERSONA_REGISTRY.
        sport: "Basketball" or "Football".
        cmi: Current Calculated Momentum Index float (0–100).
        is_clutch: Whether a clutch moment is active.

    Returns:
        {"conductor": str, "scout": str, "strategist": str}
    """
    role: str = persona_data.get("role", "General Member")
    tier: str = persona_data.get("tier", "Tier 1")

    return {
        "conductor": _build_conductor_line(member_name, role, sport, tier, is_clutch),
        "scout": _build_scout_line(member_name, role, sport, tier, cmi),
        "strategist": _build_strategist_line(member_name, role, sport, tier, is_clutch, cmi),
    }


# ---------------------------------------------------------------------------
# Existing agent classes (unchanged)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# FanCoachAgent — tier-aware progression advisor (4th Co-Captain)
# ---------------------------------------------------------------------------

class FanCoachAgent:
    """
    Generates a personalized, one-line coaching message for a fan based on
    their current passport data (tier progress, career stats) and the live
    game moment (CMI, clutch state).

    This is the fourth Co-Captain alongside The Conductor, The Scout, and
    The Strategist. It creates the progression feedback loop that converts
    a static accolade display into an in-game call to action.
    """

    # Games required to reach each tier boundary
    _TIER_THRESHOLDS: dict = {
        "Rookie Member (Tier 1)":            10,
        "Tier 1":                            10,
        "Prop Captain (Tier 2)":             20,
        "Tech Superfan (Tier 2)":            25,
        "Vocal Tactician (Tier 3)":          35,
        "Section Director (Tier 4)":         50,
        "Tailgate Host (Tier 4)":            50,
        "Stadium Veteran (Tier 5)":          75,
        "General Season Ticket Holder":      10,
        "General Member (Tier 1)":           10,
    }

    def coach(
        self,
        member_name: str,
        persona_data: Dict[str, Any],
        cmi: float,
        is_clutch: bool,
    ) -> str:
        """
        Returns a single coaching line tailored to this fan's tier progress
        and the current game moment.

        Args:
            member_name:  Fan display name.
            persona_data: Dict from PERSONA_REGISTRY with tier, career stats.
            cmi:          Current CMI float (0–100).
            is_clutch:    Whether a clutch moment is active.

        Returns:
            A non-empty coaching string.
        """
        tier: str  = persona_data.get("tier", "Tier 1")
        games: int = int(persona_data.get("career_games", 0))
        stops: int = int(persona_data.get("clutch_stops", 0))
        taps:  int = int(persona_data.get("respect_taps", 0))
        role:  str = persona_data.get("role", "Fan")
        is_basketball = "basket" in str(persona_data.get("sport", "Basketball")).lower()

        # Find how many games until the next tier
        threshold = self._TIER_THRESHOLDS.get(tier, 10)
        remaining = max(0, threshold - games)

        # Build the clutch-moment performance nudge
        if is_clutch and cmi >= 80.0:
            performance = (
                f"CMI is peaking at {cmi}/100 right now — this clutch stop counts double toward your Proof-of-Momentum record."
            )
        elif is_clutch:
            performance = (
                f"CMI is at {cmi}/100 — push the section energy higher and this clutch moment will register on your career ledger."
            )
        else:
            performance = (
                f"Live CMI is {cmi}/100. Every tap and chant you contribute tonight compounds your Acoustic Wall career total."
            )

        # Tier-progress message
        if remaining == 0:
            progress_msg = f"You have reached the top of your current tier ({tier}). Lead by example tonight — your actions inspire the whole section."
        elif remaining <= 3:
            progress_msg = f"Only {remaining} more game(s) to unlock your next tier upgrade. Tonight could be the one."
        else:
            progress_msg = f"{remaining} game(s) remaining to unlock your next tier. Keep showing up — {games} games of verified impact already on record."

        # Role-specific achievement nudge
        if stops >= 20:
            achievement = f"With {stops} verified clutch stops, you are already operating at Hall of Fame pace."
        elif stops >= 10:
            achievement = f"{stops} verified clutch stops and counting — you are the defensive backbone of this section."
        else:
            achievement = f"Every clutch stop adds to your {stops} career total and boosts the section's Season Defense Rating."

        sport_emoji = "🏀" if is_basketball else "🏈"
        return (
            f"{sport_emoji} Coach to {member_name} ({role}): {performance} "
            f"{progress_msg} {achievement}"
        )
