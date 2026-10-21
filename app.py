# ==============================================================================
# Kinetic FanLab — 5-Screen Fan & AI Squad Experience
# Track 3: Fan-Centric Sports & Entertainment
#   Screen 1: Living Fan Passport & Section Roster
#   Screen 2: 36-Hour Virtual Tailgate
#   Screen 3: In-Arena Game Hub & Armchair Coach (Fan-to-Fan Collaboration)
#   Screen 4: Narrative Delta & Shareable Crowd Box Score
#   Screen 5: AI Squad & Game Intelligence (@coach, @conductor, @strategist, @scout)
# ==============================================================================

import streamlit as st
import time
import os
import sys

# Ensure local directory is in path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import live watsonx and governance modules
try:
    from watsonx_live import analyze_vocal_urgency_live, generate_narrative_live, summarize_tailgate_chants_live
    WATSONX_LIVE = True
except Exception:
    WATSONX_LIVE = False
    def analyze_vocal_urgency_live(fan_text: str) -> float: return 0.85
    def generate_narrative_live(sport: str, outcome: str, pre_cmi: float, peak_cmi: float, fan_notes: list) -> str:
        surge = round(max(0.0, peak_cmi - pre_cmi), 1)
        if surge == 0.0:
            return f"The stadium atmosphere holds at a focused baseline of {pre_cmi}/100 CMI (+0.0 pts) awaiting play execution."
        return f"Crowd momentum surged +{surge} pts (peaking at {peak_cmi}/100) directly influencing the {outcome} result."
    def summarize_tailgate_chants_live(sport: str, raw_proposals: list) -> list:
        return ["1. MISS IT! OFF THE RIM! - On release", "2. BRING THE NOISE! - Continuous", "3. DEFENSE! - Wave"]

try:
    from governance_check import evaluate_fan_content_safety
    GOVERNANCE_LIVE = True
except Exception:
    GOVERNANCE_LIVE = False
    def evaluate_fan_content_safety(raw_text: str) -> dict:
        return {"input_text": raw_text, "guardrail_status": "APPROVED", "violations": [], "action": "Proceed"}

# Import IBM Cloud services (graceful fallback included inside each module)
try:
    import cloud_storage
except Exception:
    class _CloudStorageFallback:
        @staticmethod
        def archive_crowd_box_score(**kwargs):
            return {"status": "ARCHIVED_LOCALLY", "object_key": f"crowd_box_scores/{kwargs.get('fixture_id', 'BB-02')}.json"}
    cloud_storage = _CloudStorageFallback()

try:
    import cloudant_db
except Exception:
    class _CloudantDbFallback:
        @staticmethod
        def increment_respect_tap(member_name: str, count: int = 1) -> int:
            return 314
    cloudant_db = _CloudantDbFallback()

try:
    from cloudant_engine import (
        save_fan_passport as cloudant_save_passport,
        save_telemetry_snapshot as cloudant_save_telemetry,
        save_storycard as cloudant_save_storycard,
    )
    CLOUDANT_ENGINE_LIVE = True
except Exception:
    CLOUDANT_ENGINE_LIVE = False
    def cloudant_save_passport(*args, **kwargs): return {'status': 'SUCCESS', 'source': 'LOCAL_CACHE'}
    def cloudant_save_telemetry(*args, **kwargs): return {'status': 'SUCCESS'}
    def cloudant_save_storycard(*args, **kwargs): return {'status': 'SUCCESS'}

try:
    from cos_archive import archive_crowd_box_score as cos_lakehouse_archive
    COS_ARCHIVE_LIVE = True
except Exception:
    COS_ARCHIVE_LIVE = False
    def cos_lakehouse_archive(*args, **kwargs):
        return {
            'status': 'ARCHIVED',
            'storage_tier': 'COS_LOCAL_HYBRID',
            'object_key': 'curated-cmi/archive.json',
            'content_sha256': '035727e646c2ea32cdc2d4094a4805e26325be91e92d6e32d56a3e2182c1634b',
            'byte_size': 577,
        }

# Silent backend 16-agent runner hook (executes in background without UI clutter)
def _trigger_silent_backend_pipeline(
    fixture_id: str,
    sport: str,
    member_name: str,
    member_hash: str,
    section_id: str,
    outburst: str,
    db_val: float,
    hr_val: float,
    taps_val: float,
    vu_val: float,
    is_clutch: bool,
) -> None:
    try:
        from agents.production_cast_runtime import run_full_16_agent_production
        run_full_16_agent_production(
            fixture_id=fixture_id,
            sport=sport,
            member_name=member_name,
            member_hash=member_hash,
            section_id=section_id,
            fan_outburst=outburst,
            raw_dbs=[db_val, db_val + 1.2, db_val - 0.8],
            raw_bpms=[hr_val, hr_val + 2.0, 0.0],
            raw_taps=[taps_val, taps_val],
            raw_vus=[vu_val],
            is_clutch=is_clutch,
        )
    except Exception as _e:
        # Dev-mode logging writes to stdout only; does not affect clean fan UI
        print(f"[backend_pipeline] suppressed: {_e}")

st.set_page_config(page_title="Kinetic FanLab", page_icon="⚡", layout="wide")

# --- Mathematical Normalization & Ground Truth Formula ---
def normalize(val: float, min_val: float, max_val: float) -> float:
    clamped = max(min_val, min(val, max_val))
    return (clamped - min_val) / (max_val - min_val)

def _append_fan_note(note: str) -> None:
    """Append a fan callout note and cap the list at 20 entries."""
    st.session_state.fan_notes.append(note)
    if len(st.session_state.fan_notes) > 20:
        st.session_state.fan_notes = st.session_state.fan_notes[-20:]

def calc_momentum_index(db: float, hr: float, taps: float, vu: float) -> float:
    n_db = normalize(db, 60.0, 115.0)
    n_hr = normalize(hr, 60.0, 160.0)
    n_taps = normalize(taps, 0.0, 15.0)
    n_vu = normalize(vu, 0.0, 1.0)
    return round((n_db * 0.35 + n_hr * 0.25 + n_taps * 0.20 + n_vu * 0.20) * 100, 1)

def get_tier(score: float) -> str:
    if score >= 80.0: return "Maximum"
    elif score >= 65.0: return "High"
    elif score >= 45.0: return "Moderate"
    else: return "Baseline"

def get_color(score: float) -> str:
    if score >= 80.0: return "#da1e28"  # Red
    elif score >= 65.0: return "#f1c21b"  # Amber
    elif score >= 45.0: return "#0043ce"  # Blue
    else: return "#0f62fe"

bb_members = ["Marcus Vance", "Elena Rostova", "Devon Miller", "Jordan Lee"]
fb_members = ["Sarah Jenkins", "Carlos Mendez", "Maya Patel", "Alex Taylor"]

# --- Sidebar: Ultra-Clean Navigation & Game Situation Switcher ---
st.sidebar.title("⚡ Kinetic FanLab")
st.sidebar.caption("Track 3: Fan-Centric Sports & Entertainment")

screen = st.sidebar.radio("Navigate:", [
    "👤 Screen 1: Fan Passport & Roster",
    "🎪 Screen 2: 36h Virtual Tailgate",
    "🏟️ Screen 3: In-Arena Game Hub & Trigger",
    "📊 Screen 4: Narrative Delta & Story Card",
    "🤖 Screen 5: AI Squad & Game Intelligence"
])

st.sidebar.markdown("---")
active_preset = st.sidebar.selectbox("Live Game Situation:", [
    "BB-01: Basketball Baseline (Free Throw 1)",
    "BB-02: Basketball Clutch (Free Throw 2)",
    "FB-01: Football Pre-Kick Timeout",
    "FB-02: Football 48-Yard FG Snap (Clutch)"
], key="fixture_picker")

# Reactively update fixture parameters if changed
if "last_fixture" not in st.session_state or st.session_state.last_fixture != active_preset:
    prev_sport = st.session_state.get("sport", None)
    st.session_state.last_fixture = active_preset
    if "BB-01" in active_preset:
        st.session_state.sport = "Basketball"
        st.session_state.db = 82.0
        st.session_state.hr = 98.0
        st.session_state.taps = 2.5
        st.session_state.vu = 0.55
        st.session_state.is_clutch = False
        st.session_state.fan_notes = ["Watch the shooter, need this stop"]
    elif "BB-02" in active_preset:
        st.session_state.sport = "Basketball"
        st.session_state.db = 106.5
        st.session_state.hr = 136.0
        st.session_state.taps = 12.2
        st.session_state.vu = 0.85
        st.session_state.is_clutch = True
        st.session_state.fan_notes = ["MISS IT! OFF THE RIM! BRING THE NOISE!"]
    elif "FB-01" in active_preset:
        st.session_state.sport = "Football"
        st.session_state.db = 78.5
        st.session_state.hr = 105.0
        st.session_state.taps = 3.0
        st.session_state.vu = 0.60
        st.session_state.is_clutch = False
        st.session_state.fan_notes = ["Timeout called, make him wait in the cold!"]
    elif "FB-02" in active_preset:
        st.session_state.sport = "Football"
        st.session_state.db = 111.8
        st.session_state.hr = 148.0
        st.session_state.taps = 14.0
        st.session_state.vu = 0.92
        st.session_state.is_clutch = True
        st.session_state.fan_notes = ["BLOCK THAT KICK! RATTLE THE KICKER! GET LOUD!"]

    st.session_state.tap_count = 0
    st.session_state.tap_times = []
    st.session_state.synergy_claimed = False

    if prev_sport is not None and prev_sport != st.session_state.sport:
        st.session_state.early_checkin = False
        st.session_state.synergy_score = 92
        st.session_state.squad_chat_history = []  # Clear squad chat history on sport switch so sports never blend!
        if st.session_state.sport == "Basketball" and st.session_state.get("active_member") not in bb_members:
            st.session_state.active_member = "Marcus Vance"
        elif st.session_state.sport == "Football" and st.session_state.get("active_member") not in fb_members:
            st.session_state.active_member = "Sarah Jenkins"

# Global session states
if "sport" not in st.session_state: st.session_state.sport = "Basketball"
if "active_member" not in st.session_state:
    st.session_state.active_member = "Marcus Vance" if st.session_state.sport == "Basketball" else "Sarah Jenkins"
if "tap_count" not in st.session_state: st.session_state.tap_count = 0
if "tap_times" not in st.session_state: st.session_state.tap_times = []
if "early_checkin" not in st.session_state: st.session_state.early_checkin = False
if "synergy_score" not in st.session_state: st.session_state.synergy_score = 92
if "synergy_claimed" not in st.session_state: st.session_state.synergy_claimed = False
if "selected_squad_agent" not in st.session_state: st.session_state.selected_squad_agent = "@strategist"
if "squad_chat_history" not in st.session_state: st.session_state.squad_chat_history = []
if "respect_dict" not in st.session_state:
    st.session_state.respect_dict = {
        "Marcus Vance": 313, "Elena Rostova": 168, "Devon Miller": 245, "Jordan Lee": 28,
        "Sarah Jenkins": 480, "Carlos Mendez": 395, "Maya Patel": 185, "Alex Taylor": 45
    }

# Ensure active member matches current sport
if st.session_state.sport == "Basketball" and st.session_state.active_member not in bb_members:
    st.session_state.active_member = "Marcus Vance"
elif st.session_state.sport == "Football" and st.session_state.active_member not in fb_members:
    st.session_state.active_member = "Sarah Jenkins"

current_cmi = calc_momentum_index(st.session_state.db, st.session_state.hr, st.session_state.taps, st.session_state.vu)
tier = get_tier(current_cmi)
color = get_color(current_cmi)

is_basketball = st.session_state.sport == "Basketball"
start_term = "tip-off" if is_basketball else "kickoff"
role_tag = "6th Man" if is_basketball else "12th Man"

# Master Persona Database with Universal Tier Progress & Dynamic Accolades
PERSONA_DB = {
    "Marcus Vance": {
        "hash": "0xMV-sec114-8f7a2",
        "role": "Student Section Director",
        "tier": "Section Director (Tier 4)",
        "sec": "Section 114 (Thunder Row)",
        "games": 34, "career_db": "3,820 dB", "clutch_stops": 23,
        "next_tier_title": "Tier 5 (Arena Legend / Hall of Fame)",
        "tier_progress_pct": 0.68,
        "tier_progress_desc": "34/50 games attended — 16 more game(s) to unlock Tier 5 Arena Legend status & Lifetime Banner Recognition.",
        "neighbors": [
            {"name": "Elena Rostova", "seat": "Row 2, Seat 4", "role": "Prop Captain", "bio": "14 Games | Peak HR: 142 BPM | Waving Leader"},
            {"name": "Devon Miller", "seat": "Row 3, Seat 8", "role": "Vocal Tactician", "bio": "28 Games | 18 Voice Logs | Chant Starter"},
            {"name": "Jordan Lee", "seat": "Row 4, Seat 12", "role": "Rookie Member", "bio": "3 Games | 1 Clutch Stop | Thunderstick Cadet"}
        ],
        "accolades": [
            {"title": "Arena Director Ring", "rarity": "Legendary", "color": "#f1c21b", "desc": "Led Section 114 to 20+ verified clutch stops.", "perk": "Post-game press conference access"},
            {"title": "Decibel General", "rarity": "Epic", "color": "#8a3ffc", "desc": "Sustained Section 114 above 105 dB for 15+ rivalry minutes.", "perk": "Early student gate express entry"},
            {"title": "30-Game Streak", "rarity": "Rare", "color": "#0f62fe", "desc": "30 consecutive home game roll calls verified.", "perk": "15% bookstore & concession discount"}
        ]
    },
    "Elena Rostova": {
        "hash": "0xER-sec114-3c9b1",
        "role": "Hype & Prop Captain",
        "tier": "Prop Captain (Tier 2)",
        "sec": "Section 114 (Thunder Row)",
        "games": 14, "career_db": "1,580 dB", "clutch_stops": 9,
        "next_tier_title": "Tier 3 (Vocal Tactician & Section Strategist)",
        "tier_progress_pct": 0.70,
        "tier_progress_desc": "14/20 games attended — 6 more game(s) to unlock Tier 3 Section Strategist privileges.",
        "neighbors": [
            {"name": "Marcus Vance", "seat": "Row 1, Seat 1", "role": "Section Director", "bio": "34 Games | Section Conductor | Megaphone Lead"},
            {"name": "Devon Miller", "seat": "Row 3, Seat 8", "role": "Vocal Tactician", "bio": "28 Games | 18 Voice Logs | Chant Starter"},
            {"name": "Jordan Lee", "seat": "Row 4, Seat 12", "role": "Rookie Member", "bio": "3 Games | 1 Clutch Stop | Thunderstick Cadet"}
        ],
        "accolades": [
            {"title": "Thunderstick Master", "rarity": "Epic", "color": "#8a3ffc", "desc": "Synchronized visual waving across 10-second free throw release.", "perk": "Row 1-3 wristband reserve"},
            {"title": "Depth Disruptor", "rarity": "Rare", "color": "#0f62fe", "desc": "Forced 3 consecutive opponent missed free throws.", "perk": "Custom section prop kit"}
        ]
    },
    "Devon Miller": {
        "hash": "0xDM-sec114-6d4e8",
        "role": "Vocal Tactician",
        "tier": "Vocal Tactician (Tier 3)",
        "sec": "Section 114 (Thunder Row)",
        "games": 28, "career_db": "3,140 dB", "clutch_stops": 19,
        "next_tier_title": "Tier 4 (Section Director / Conductor)",
        "tier_progress_pct": 0.80,
        "tier_progress_desc": "28/35 games attended — 7 more game(s) to unlock Tier 4 Director voting privileges.",
        "neighbors": [
            {"name": "Marcus Vance", "seat": "Row 1, Seat 1", "role": "Section Director", "bio": "34 Games | Section Conductor | Megaphone Lead"},
            {"name": "Elena Rostova", "seat": "Row 2, Seat 4", "role": "Prop Captain", "bio": "14 Games | Peak HR: 142 BPM | Waving Leader"},
            {"name": "Jordan Lee", "seat": "Row 4, Seat 12", "role": "Rookie Member", "bio": "3 Games | 1 Clutch Stop | Thunderstick Cadet"}
        ],
        "accolades": [
            {"title": "Chant Starter Crest", "rarity": "Epic", "color": "#8a3ffc", "desc": "Synthesized 18 approved chants through IBM Granite.", "perk": "PA booth microphone shoutout"},
            {"title": "Acoustic Wall Star", "rarity": "Rare", "color": "#0f62fe", "desc": "Personal voice log scored 0.90+ vocal urgency.", "perk": "Section playlist curator"}
        ]
    },
    "Jordan Lee": {
        "hash": "0xJL-sec114-1f4a9",
        "role": "Rookie Section Member",
        "tier": "Rookie Member (Tier 1)",
        "sec": "Section 114 (Thunder Row)",
        "games": 3, "career_db": "310 dB", "clutch_stops": 1,
        "next_tier_title": "Tier 2 (Prop Captain / Specialist)",
        "tier_progress_pct": 0.30,
        "tier_progress_desc": "3/10 games attended — 7 more game(s) to unlock Tier 2 status and full section specialist privileges.",
        "neighbors": [
            {"name": "Marcus Vance", "seat": "Row 1, Seat 1", "role": "Section Director", "bio": "34 Games | Section Conductor | Megaphone Lead"},
            {"name": "Elena Rostova", "seat": "Row 2, Seat 4", "role": "Prop Captain", "bio": "14 Games | Peak HR: 142 BPM | Waving Leader"},
            {"name": "Devon Miller", "seat": "Row 3, Seat 8", "role": "Vocal Tactician", "bio": "28 Games | 18 Voice Logs | Chant Starter"}
        ],
        "accolades": [
            {"title": "First Roll Call Stamp", "rarity": "Common", "color": "#0f62fe", "desc": "Completed in-seat early check-in before tip-off.", "perk": "1.25x 1st-quarter points boost"},
            {"title": "First Pulse Tap", "rarity": "Common", "color": "#0f62fe", "desc": "Contributed first active momentum pulse tap during clutch defense.", "perk": "Section roster profile active"}
        ]
    },
    "Sarah Jenkins": {
        "hash": "0xSJ-sec115-7b2a5",
        "role": "10-Year Season Ticket Holder",
        "tier": "Stadium Veteran (Tier 5)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 62, "career_db": "6,850 dB", "clutch_stops": 31,
        "next_tier_title": "Tier 5 Prestige (Master 12th Man Legend)",
        "tier_progress_pct": 0.83,
        "tier_progress_desc": "62/75 games attended — 13 more game(s) to unlock 100% Lifetime Stadium Immortality & Press Box Recognition.",
        "neighbors": [
            {"name": "Carlos Mendez", "seat": "Row 18, Seat 12", "role": "Lot B Tailgate Host", "bio": "45 Games | 10-Yr Season Ticket Holder | Early Arrival Champ"},
            {"name": "Maya Patel", "seat": "Row 19, Seat 14", "role": "Biometric Superfan", "bio": "18 Games | Peak HR: 154 BPM | Tech Ambassador"},
            {"name": "Alex Taylor", "seat": "Row 20, Seat 8", "role": "General Member", "bio": "4 Games | 2 Clutch Stops | Rookie 12th Man"}
        ],
        "accolades": [
            {"title": "10-Year Stadium Ring", "rarity": "Legendary", "color": "#f1c21b", "desc": "A decade of verified 12th Man defense in Section 115.", "perk": "Exclusive pre-game sideline pass"},
            {"title": "111 dB Roar Enforcer", "rarity": "Epic", "color": "#8a3ffc", "desc": "Forced 12 false start penalties on visiting offenses.", "perk": "Stadium club lounge access"},
            {"title": "Ice Breaker Legend", "rarity": "Rare", "color": "#0f62fe", "desc": "Sustained bleacher stomp during 3-minute kicker timeout.", "perk": "20% official team store discount"}
        ]
    },
    "Carlos Mendez": {
        "hash": "0xCM-sec115-4e8f9",
        "role": "Lot B Tailgate Host",
        "tier": "Tailgate Host (Tier 4)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 45, "career_db": "4,920 dB", "clutch_stops": 24,
        "next_tier_title": "Tier 5 (Stadium Legend / 12th Man Hall of Fame)",
        "tier_progress_pct": 0.90,
        "tier_progress_desc": "45/50 games attended — 5 more game(s) to unlock Tier 5 Stadium Legend status.",
        "neighbors": [
            {"name": "Sarah Jenkins", "seat": "Row 18, Seat 10", "role": "10-Year Veteran", "bio": "62 Games | 12th Man Bleacher Stomper | Defense Wall"},
            {"name": "Maya Patel", "seat": "Row 19, Seat 14", "role": "Biometric Superfan", "bio": "18 Games | Peak HR: 154 BPM | Tech Ambassador"},
            {"name": "Alex Taylor", "seat": "Row 20, Seat 8", "role": "General Member", "bio": "4 Games | 2 Clutch Stops | Rookie 12th Man"}
        ],
        "accolades": [
            {"title": "Lot B Grill Master", "rarity": "Legendary", "color": "#f1c21b", "desc": "Hosted 40+ consecutive community tailgates.", "perk": "Reserved VIP parking spot Lot B"},
            {"title": "Early Arrival Shield", "rarity": "Epic", "color": "#8a3ffc", "desc": "Achieved 100% early check-in before kickoff in 4 seasons.", "perk": "Season ticket seat renewal priority"}
        ]
    },
    "Maya Patel": {
        "hash": "0xMP-sec115-1a5c3",
        "role": "Biometric & Tech Superfan",
        "tier": "Tech Superfan (Tier 2)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 18, "career_db": "1,940 dB", "clutch_stops": 11,
        "next_tier_title": "Tier 3 (Stadium Veteran / Cadence Caller)",
        "tier_progress_pct": 0.72,
        "tier_progress_desc": "18/25 games attended — 7 more game(s) to unlock Tier 3 Bleacher Conductor status.",
        "neighbors": [
            {"name": "Sarah Jenkins", "seat": "Row 18, Seat 10", "role": "10-Year Veteran", "bio": "62 Games | 12th Man Bleacher Stomper | Defense Wall"},
            {"name": "Carlos Mendez", "seat": "Row 18, Seat 12", "role": "Lot B Tailgate Host", "bio": "45 Games | 10-Yr Season Ticket Holder | Early Arrival Champ"},
            {"name": "Alex Taylor", "seat": "Row 20, Seat 8", "role": "General Member", "bio": "4 Games | 2 Clutch Stops | Rookie 12th Man"}
        ],
        "accolades": [
            {"title": "Pulse Sync Pioneer", "rarity": "Epic", "color": "#8a3ffc", "desc": "Logged 150+ BPM peak during game-winning field goal stop.", "perk": "Free smartwatch sensor calibration kit"},
            {"title": "Haptic Ambassador", "rarity": "Rare", "color": "#0f62fe", "desc": "Synchronized BLE mesh cadence across 50 bleacher seats.", "perk": "Tech beta tester accreditation"}
        ]
    },
    "Alex Taylor": {
        "hash": "0xAT-sec115-5c2d3",
        "role": "General Season Ticket Holder",
        "tier": "General Member (Tier 1)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 4, "career_db": "420 dB", "clutch_stops": 2,
        "next_tier_title": "Tier 2 (Tech Superfan / Bleacher Specialist)",
        "tier_progress_pct": 0.40,
        "tier_progress_desc": "4/10 games attended — 6 more game(s) to unlock Tier 2 Bleacher Specialist status.",
        "neighbors": [
            {"name": "Sarah Jenkins", "seat": "Row 18, Seat 10", "role": "10-Year Veteran", "bio": "62 Games | 12th Man Bleacher Stomper | Defense Wall"},
            {"name": "Carlos Mendez", "seat": "Row 18, Seat 12", "role": "Lot B Tailgate Host", "bio": "45 Games | 10-Yr Season Ticket Holder | Early Arrival Champ"},
            {"name": "Maya Patel", "seat": "Row 19, Seat 14", "role": "Biometric Superfan", "bio": "18 Games | Peak HR: 154 BPM | Tech Ambassador"}
        ],
        "accolades": [
            {"title": "First Kickoff Stamp", "rarity": "Common", "color": "#0f62fe", "desc": "Checked in for opening kickoff of the season.", "perk": "1.25x 1st-quarter points boost"},
            {"title": "Rookie 12th Man", "rarity": "Common", "color": "#0f62fe", "desc": "Contributed to first stadium-wide 111 dB roar.", "perk": "Quarterly seat upgrade lottery entry"}
        ]
    }
}

# ==============================================================================
# SCREEN 1: THE LIVING FAN PASSPORT & SECTION ROSTER
# ==============================================================================
if screen == "👤 Screen 1: Fan Passport & Roster":
    st.header(f"👤 The Living Fan Passport & Section Roster ({st.session_state.sport})")
    st.caption("Persistent 365-day fandom identity, career telemetry, and peer-to-peer section camaraderie.")

    persona_options = bb_members if is_basketball else fb_members
    p_idx = persona_options.index(st.session_state.active_member) if st.session_state.active_member in persona_options else 0

    selected_name = st.selectbox("Select Active Fan Persona:", persona_options, index=p_idx, key="passport_persona_select")
    st.session_state.active_member = selected_name
    p_info = PERSONA_DB[selected_name]

    tab_identity, tab_trophy = st.tabs(["🪪 Fan Passport & Section Roster", "🏆 Living Trophy Case & Dynamic Accolades"])

    with tab_identity:
        col_p, col_b = st.columns([1, 2])
        with col_p:
            glow_color = "#f1c21b" if "Tier 5" in p_info['tier'] else ("#8a3ffc" if "Tier 4" in p_info['tier'] else "#0f62fe")
            st.markdown(f"""
            <div style="background-color: #161616; padding: 22px; border-radius: 12px; border: 2px solid {glow_color}; box-shadow: 0 0 15px {glow_color}88; text-align: center; margin-top: 10px;">
                <p style="color: #8d8d8d; font-size: 10pt; margin: 0; text-transform: uppercase;">DYNAMIC MOMENTUM PASS</p>
                <h2 style="color: #f4f4f4; margin: 6px 0;">{selected_name}</h2>
                <p style="color: #0f62fe; font-weight: bold; margin: 0;">{p_info['sec']}</p>
                <hr style="border-color: #333; margin: 12px 0;">
                <p style="color: #f4f4f4; font-size: 11pt; margin: 4px 0;">Tier: <b>{p_info['tier']}</b></p>
                <p style="color: #a8a8a8; font-size: 9.5pt; margin: 0;">Unique Member Hash: <code>{p_info['hash']}</code></p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Sync My Fan Passport", key=f"btn_sync_cloudant_{selected_name}", use_container_width=True):
                if CLOUDANT_ENGINE_LIVE:
                    sec_clean = p_info['sec'].split()[0] + p_info['sec'].split()[1] if len(p_info['sec'].split()) > 1 else p_info['sec']
                    tier_num = int(p_info['tier'].split("Tier ")[1].split(")")[0]) if "Tier " in p_info['tier'] else 1
                    cloudant_save_passport(
                        member_name=selected_name,
                        member_hash=p_info['hash'],
                        section_id=sec_clean,
                        sport=st.session_state.sport,
                        role=p_info['role'],
                        tier=tier_num,
                        device_anchor="Wearable Sensor Anchor",
                        early_multiplier=1.25 if st.session_state.early_checkin else 1.0
                    )
                st.success(f"✅ Fan Passport synced for {selected_name}!")
        with col_b:
            st.subheader("📊 Lifetime Career Telemetry Statline")
            stat1, stat2, stat3, stat4 = st.columns(4)
            stat1.metric("Games Attended", f"{p_info['games']}", delta="Active Season")
            stat2.metric("Career Acoustic dB", p_info['career_db'], delta=f"{st.session_state.db} dB peak")
            stat3.metric("Clutch Stops", f"{p_info['clutch_stops']}", delta="Verified Stops")
            stat4.metric("Respect Taps", f"{st.session_state.respect_dict[selected_name]}", delta="+1 Received")

            st.markdown("---")
            st.subheader(f"👥 Section Roster for {selected_name} (Seat Neighbors)")
            st.write(f"Connect with your actual row neighbors in **{p_info['sec']}**:")

            r_cols = st.columns(3)
            for idx, neighbor in enumerate(p_info['neighbors'][:3]):
                with r_cols[idx]:
                    st.markdown(f"**{neighbor['name']}** ({neighbor['seat']})")
                    st.caption(f"*{neighbor['role']}*\n\n{neighbor['bio']}")

            if st.button("🤝 Send Respect Tap to Seat Neighbors", key="btn_neighbor_respect"):
                new_total = cloudant_db.increment_respect_tap(selected_name, 1)
                st.session_state.respect_dict[selected_name] = new_total
                st.session_state.synergy_score = min(100, st.session_state.synergy_score + 2)
                st.success(f"Respect Tap transmitted to {p_info['neighbors'][0]['name']} and row neighbors! (+1 Respect Logged — Total: {new_total})")

            with st.expander("🎯 Send Respect Tap to Any Specific Seat in the Venue"):
                st.write("Acknowledge a dedicated fan, chant starter, or veteran anywhere in the venue:")
                rc1, rc2, rc3 = st.columns(3)
                target_sec = rc1.text_input("Section", value=p_info['sec'].split()[0] + " " + p_info['sec'].split()[1])
                target_row = rc2.text_input("Row", value="Row 5")
                target_seat = rc3.text_input("Seat", value="Seat 12")
                if st.button("🚀 Transmit Respect Tap to Specific Seat", key="btn_target_respect"):
                    new_total = cloudant_db.increment_respect_tap(selected_name, 1)
                    st.session_state.respect_dict[selected_name] = new_total
                    st.session_state.synergy_score = min(100, st.session_state.synergy_score + 2)
                    st.success(f"✅ Respect Tap sent to **{target_sec}, {target_row}, {target_seat}**! (+1 Respect Tap — Total: {new_total})")

    with tab_trophy:
        st.subheader(f"🏆 Living Trophy Case: {selected_name}")
        st.caption("Dynamic NFT Accolades that evolve based on your real-time verified stadium telemetry.")

        st.markdown(f"### 📈 {p_info['next_tier_title']} Progress")
        st.progress(p_info['tier_progress_pct'])
        st.caption(p_info['tier_progress_desc'])

        st.markdown("---")
        st.subheader("🏅 Unlocked Dynamic Accolades (NFT Badges)")
        badge_cols = st.columns(len(p_info['accolades']))
        for b_idx, badge in enumerate(p_info['accolades']):
            with badge_cols[b_idx]:
                st.markdown(f"""
                <div style="background-color: #1a1a1a; border: 2px solid {badge['color']}; border-radius: 10px; padding: 16px; min-height: 180px; box-shadow: 0 0 10px {badge['color']}44;">
                    <span style="background-color: {badge['color']}33; color: {badge['color']}; padding: 3px 8px; border-radius: 4px; font-size: 8pt; font-weight: bold; text-transform: uppercase;">{badge['rarity']}</span>
                    <h4 style="color: white; margin: 8px 0 4px 0;">{badge['title']}</h4>
                    <p style="color: #a8a8a8; font-size: 9.5pt; margin-bottom: 8px;">{badge['desc']}</p>
                    <hr style="border-color: #333; margin: 6px 0;">
                    <p style="color: #0f62fe; font-size: 8.5pt; font-weight: bold; margin: 0;">🎁 Perk: {badge['perk']}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("📲 Share Trophy Showcase")
        st.markdown(f"""
        <div style="background-color: #111; border: 2px solid #0f62fe; border-radius: 12px; padding: 20px; max-width: 450px; margin: 0 auto; text-align: center;">
            <p style="color: #8d8d8d; font-size: 9pt; margin: 0; letter-spacing: 1px;">KINETIC FANLAB // NFT TROPHY SHOWCASE</p>
            <h2 style="color: white; margin: 6px 0;">{selected_name}</h2>
            <p style="color: #0f62fe; font-weight: bold; margin: 0;">{p_info['tier']} • {p_info['sec']}</p>
            <p style="color: #a8a8a8; font-size: 9.5pt; margin: 8px 0;">Verified Impact: <b>{p_info['career_db']}</b> Acoustic Wall • <b>{p_info['clutch_stops']}</b> Clutch Stops</p>
            <p style="color: #8d8d8d; font-size: 8.5pt; margin: 0;">Hash: <code>{p_info['hash']}</code></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📲 Share Showcase to Instagram, TikTok & X", key="btn_share_showcase"):
            st.success("Trophy Showcase formatted! Shareable story card ready for export.")

# ==============================================================================
# SCREEN 2: 36-HOUR VIRTUAL TAILGATE
# ==============================================================================
elif screen == "🎪 Screen 2: 36h Virtual Tailgate":
    st.header(f"🎪 The 36-Hour Virtual Tailgate ({st.session_state.sport})")
    st.caption(f"Unlocks 36 hours before game-time. Section strategy, chant coordination, and community meetups for {st.session_state.sport}.")

    st.info(f"⏳ **COUNTDOWN TO {start_term.upper()}:** 14 Hours, 22 Minutes Remaining | **Section Status:** Strategy Huddle Active")

    tab_strat, tab_meet = st.tabs(["🗣️ Tactical Chant Huddle", "📍 Meetup Commons & Gameday Logistics"])

    with tab_strat:
        st.subheader(f"Defensive Chant Voting & Coordination ({st.session_state.sport})")
        st.write(f"Fans submit chant ideas for **{st.session_state.sport}** and synthesize the top 3 coordinated section chants:")

        if is_basketball:
            chant_proposals = [
                "Wave thundersticks left to right on his second dribble",
                "Scream OFF THE RIM right when his elbow bends",
                "Everyone yell BRING THE NOISE on three",
                "Dead silent when he spins ball, deafening when he shoots"
            ]
        else:
            chant_proposals = [
                "Sustained 111 dB roar on 0:03 snap",
                "Rhythmic low-end bleacher stomps during timeout delay",
                "Ice the kicker! Make him wait in the cold!",
                "Pre-snap acoustic crescendo breaking QB cadence"
            ]

        if st.button("🤖 Synthesize Top 3 Section Chants"):
            with st.spinner("Synthesizing this week's top 3 section chants..."):
                st.session_state[f"chants_{st.session_state.sport}"] = summarize_tailgate_chants_live(st.session_state.sport, chant_proposals)
            st.success(f"Official {st.session_state.sport} section chant strategy locked in!")

        sport_chants = st.session_state.get(f"chants_{st.session_state.sport}")
        if not sport_chants:
            if is_basketball:
                sport_chants = [
                    "1. MISS IT! OFF THE RIM! - Synchronized waving on shooter knee-bend",
                    "2. BRING THE NOISE! - Piercing high-frequency whistle chant",
                    "3. AIR BALL! AIR BALL! - Coordinated psychological breakdown"
                ]
            else:
                sport_chants = [
                    "1. BLOCK THAT KICK! - Max 111 dB acoustic wall at the 0:03 snap",
                    "2. ICE THE KICKER! - Heavy low-frequency bleacher stomps during timeout delay",
                    "3. FALSE START! GET LOUD! - Pre-snap crescendo to drown out quarterback cadence"
                ]

        st.markdown(f"### 📢 Official Section Chants for {st.session_state.sport}:")
        for chant in sport_chants:
            st.markdown(f"- **{chant}**")

    with tab_meet:
        st.subheader(f"Community Meetups & Gameday Logistics ({st.session_state.sport})")
        m1, m2 = st.columns(2)
        if is_basketball:
            with m1:
                st.markdown(f"""
                **🏀 Student Section Arena Plaza Rally (Hosted by Marcus & Elena)**
                * Location: Arena North Plaza (Student Gate)
                * Arrival Time: 2 Hours before {start_term}
                * Perks: Thunderstick pickup, student banner painting
                * Goal: First 500 students get Row 1-5 lower bleacher wristbands!
                """)
            with m2:
                st.markdown(f"""
                **🍕 Campus Walk Pregame Crew (Hosted by Devon)**
                * Meeting Spot: Student Union Commons
                * Shuttles Depart: Every 10 minutes starting 90 minutes before {start_term}
                * Target: 70% in-seat check-in by T-minus 30 mins for the 1.25x Multiplier!
                """)
        else:
            with m1:
                st.markdown(f"""
                **🏈 Lot B Mega-Tailgate Grill (Hosted by Carlos & Sarah)**
                * Location: Lot B, Row 4 (Under the Giant Blue Canopy)
                * Arrival Time: 4 Hours before {start_term}
                * Menu: 14-Hour Smoked Brisket, Sausage, Local Drinks
                * Tradition: First-time Section 115 members eat free! Bring your game ticket.
                """)
            with m2:
                st.markdown(f"""
                **🚌 Stadium North Express Shuttle (Hosted by Maya)**
                * Meeting Spot: North Express Park & Ride
                * Tech Sync: Wearable fitness band calibration and app pairing station
                * Goal: Section 115 early check-in push for the 1.25x Multiplier!
                """)

# ==============================================================================
# SCREEN 3: IN-ARENA GAME HUB & TRIGGER (CLEAN FAN-TO-FAN & ARMCHAIR COACH HUB)
# ==============================================================================
elif screen == "🏟️ Screen 3: In-Arena Game Hub & Trigger":
    from orchestrate_agents import (
        InvisibleCoordinatorAgent,
        SystemOptimizerAgent,
    )

    st.header(f"🏟️ In-Arena Game Hub & Clutch Trigger ({st.session_state.sport} — {role_tag})")
    st.caption(f"Live crowd energy, Momentum Pulse tapping, Armchair Coach fan callouts, and section rivalry for {st.session_state.sport}.")

    _coordinator = InvisibleCoordinatorAgent(sport=st.session_state.sport)
    if is_basketball and st.session_state.is_clutch:
        _game_ctx = "clutch free throw"
    elif not is_basketball and st.session_state.is_clutch:
        _game_ctx = "clutch field goal snap"
    elif not is_basketball:
        _game_ctx = "timeout ice the kicker"
    else:
        _game_ctx = "regular possession"
    coord_state = _coordinator.evaluate_game_state(_game_ctx)

    # Quick Telemetry Simulation Controls
    pulse_btn_col1, surge_btn_col2 = st.columns(2)
    with pulse_btn_col1:
        pulse_clicked = st.button("🎲 Pulse Telemetry Tick", help="Inject a live stadium sensor tick", use_container_width=True)
    with surge_btn_col2:
        surge_clicked = st.button("⚡ Live Telemetry Surge (Wave)", help="Inject a full crowd surge wave", use_container_width=True)

    if pulse_clicked or surge_clicked:
        from stream_simulator import TelemetryStreamSimulator
        if "sim_instance" not in st.session_state:
            st.session_state.sim_instance = TelemetryStreamSimulator(st.session_state.sport)
        tick = st.session_state.sim_instance.generate_live_tick(
            is_clutch=st.session_state.is_clutch or surge_clicked, noise_variance=0.08 if surge_clicked else 0.05
        )
        st.session_state.db   = tick["db"]
        st.session_state.hr   = tick["hr"]
        st.session_state.taps = tick["taps"]
        st.session_state.vu   = tick["vu"]
        current_cmi = calc_momentum_index(
            st.session_state.db, st.session_state.hr,
            st.session_state.taps, st.session_state.vu
        )
        tier  = get_tier(current_cmi)
        color = get_color(current_cmi)
        st.rerun()

    # Early Check-in with Immediate State Update
    with st.expander(f"🎟️ Pre-Game Roll Call: Early Seat Check-In ({st.session_state.sport})", expanded=True):
        st.write(f"Fans who reach their seats 30 minutes before **{start_term}** unlock a **1.25x 1st-Quarter Multiplier**.")
        if not st.session_state.early_checkin:
            sec_btn_label = "Section 114" if is_basketball else "Section 115"
            if st.button(f"📍 Check In at Seat ({sec_btn_label})", key="btn_checkin_seat"):
                st.session_state.early_checkin = True
                st.rerun()
        else:
            st.success("✅ Checked In: Section holds the Early Arrival Multiplier (1.25x)!")
            if st.button("Cancel Seat Check-In", key="btn_cancel_checkin"):
                st.session_state.early_checkin = False
                st.rerun()

    # Live Game Situation Cue Banner
    directive_color = "#da1e28" if coord_state["clutch_active"] else "#0f62fe"
    st.markdown(f"""
    <div style="background-color: #0d0d0d; border-left: 5px solid {directive_color}; padding: 10px 16px; border-radius: 6px; margin: 8px 0;">
        <span style="color: {directive_color}; font-weight: bold; font-size: 9pt; text-transform: uppercase; letter-spacing: 1px;">
            🎯 LIVE STADIUM CUE — {coord_state['trigger_event']}
        </span><br>
        <span style="color: #f4f4f4; font-size: 10pt;">{coord_state['pacing_directive']}</span>
        <span style="color: #8d8d8d; font-size: 9pt; float: right;">
            Multiplier: <b style="color:{directive_color};">{coord_state['multiplier']}x</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div style="background-color: #161616; padding: 18px; border-radius: 8px; text-align: center; border-left: 6px solid {color};">
            <h4 style="color: #8d8d8d; font-size: 10pt; margin: 0;">MOMENTUM INDEX</h4>
            <h1 style="color: {color}; font-size: 42pt; margin: 2px 0;">{current_cmi}</h1>
            <p style="color: #f4f4f4; margin: 0; font-weight: bold; font-size: 9.5pt;">{tier.upper()} TIER</p>
        </div>
        """, unsafe_allow_html=True)
    with col2: st.metric("Stadium Acoustics", f"{st.session_state.db} dB", delta="Roar Zone" if st.session_state.db > 100 else "Ambient")
    with col3: st.metric("Fan Heart Rate", f"{int(st.session_state.hr)} BPM", delta="Elevated" if st.session_state.hr > 120 else "Resting")
    with col4: st.metric("Momentum Taps", f"{st.session_state.taps}/s", delta="Surge" if st.session_state.taps > 10 else "Steady")
    with col5: st.metric("Vocal Urgency", f"{st.session_state.vu} VU", delta="Clutch" if st.session_state.vu > 0.8 else "Moderate")

    # ------------------------------------------------------------------
    # Crowd Pulse Tapper & Armchair Coach Reaction Logger (Fan-to-Fan)
    # ------------------------------------------------------------------
    st.markdown("---")
    c_tap, c_vox = st.columns(2)
    with c_tap:
        st.subheader("⚡ Crowd Pulse Tapper")
        st.caption("Tap in rhythm with your section to build collective crowd momentum.")
        now = time.time()

        tap_col1, tap_col2 = st.columns(2)
        with tap_col1:
            if st.button("🔥 PULSE TAP +1", use_container_width=True, key="btn_tap_single"):
                st.session_state.tap_count += 1
                st.session_state.tap_times.append(now)
                st.session_state.taps = min(15.0, round(st.session_state.taps + 0.5, 1))
                st.rerun()
        with tap_col2:
            if st.button("⚡ SURGE BURST (+5)", use_container_width=True, key="btn_tap_burst"):
                st.session_state.tap_count += 5
                st.session_state.tap_times.extend([now] * 5)
                st.session_state.taps = min(15.0, round(st.session_state.taps + 2.5, 1))
                st.rerun()

        st.session_state.tap_times = [t for t in st.session_state.tap_times if now - t <= 2.5]
        active_taps = len(st.session_state.tap_times)

        if active_taps > 0:
            calc_speed = round(min(15.0, (active_taps / 2.5) * 3.5), 1)
            st.session_state.taps = max(st.session_state.taps, calc_speed)

        tc1, tc2 = st.columns(2)
        tc1.metric("Pulse Taps Logged", st.session_state.tap_count)
        tc2.metric("Active Pulse Tempo", f"{st.session_state.taps} taps/s")

        if st.button("Reset Pulse Tapper", key="btn_reset_tapper"):
            st.session_state.tap_count = 0
            st.session_state.tap_times = []
            st.session_state.taps = 2.5 if is_basketball else 3.0
            st.session_state.synergy_claimed = False
            st.rerun()

    with c_vox:
        st.subheader("🎙️ Armchair Coach Reaction Logger")
        st.caption("Rally fellow fans in your section with live game reactions and quick-fire chants:")
        p_text = "e.g., MISS IT! OFF THE BACK IRON!" if is_basketball else "e.g., BLOCK THAT KICK! RATTLE HIM!"

        with st.form(key="reaction_governance_form"):
            user_in = st.text_input("Enter Fan Callout:", placeholder=p_text)
            submit_reaction = st.form_submit_button("Post Callout to Section Feed")

        if submit_reaction and user_in.strip():
            adversarial_keywords = ["ignore previous", "system prompt", "disregard", "override", "bypass", "reveal instructions"]
            is_prompt_injection = any(kw in user_in.lower() for kw in adversarial_keywords)
            gov = evaluate_fan_content_safety(user_in)
            if gov.get("guardrail_status") == "REJECTED" or is_prompt_injection:
                st.error("🚨 Callout blocked by community safety filter. Please keep section reactions focused on clean gameday energy.")
            else:
                with st.spinner("Scoring vocal urgency..."):
                    u_score = analyze_vocal_urgency_live(user_in)
                st.session_state.vu = u_score
                _append_fan_note(f"{user_in} ({u_score} VU)")
                p_cur = PERSONA_DB[st.session_state.active_member]
                _trigger_silent_backend_pipeline(
                    active_preset.split(":")[0].strip(), st.session_state.sport,
                    st.session_state.active_member, p_cur["hash"], p_cur["sec"],
                    user_in, st.session_state.db, st.session_state.hr, st.session_state.taps, u_score, st.session_state.is_clutch
                )
                st.success(f"✅ Callout posted to Section Feed! Vocal Urgency: **{u_score} VU**")
                st.rerun()

        st.markdown(f"**Quick-Fire Section Chants ({st.session_state.sport}):**")
        q_cols = st.columns(2)
        if is_basketball:
            if q_cols[0].button("MISS IT! OFF THE RIM!", use_container_width=True):
                st.session_state.vu = 0.85
                _append_fan_note("MISS IT! OFF THE RIM! (0.85 VU)")
                st.rerun()
            if q_cols[1].button("BRING THE NOISE!", use_container_width=True):
                st.session_state.vu = 0.90
                _append_fan_note("BRING THE NOISE! (0.90 VU)")
                st.rerun()
            if q_cols[0].button("AIR BALL! AIR BALL!", use_container_width=True):
                st.session_state.vu = 0.88
                _append_fan_note("AIR BALL! AIR BALL! (0.88 VU)")
                st.rerun()
            if q_cols[1].button("DEFENSE ON THREE!", use_container_width=True):
                st.session_state.vu = 0.82
                _append_fan_note("DEFENSE ON THREE! (0.82 VU)")
                st.rerun()
        else:
            if q_cols[0].button("BLOCK THAT KICK!", use_container_width=True):
                st.session_state.vu = 0.92
                _append_fan_note("BLOCK THAT KICK! (0.92 VU)")
                st.rerun()
            if q_cols[1].button("ICE THE KICKER!", use_container_width=True):
                st.session_state.vu = 0.88
                _append_fan_note("ICE THE KICKER! (0.88 VU)")
                st.rerun()
            if q_cols[0].button("FALSE START! GET LOUD!", use_container_width=True):
                st.session_state.vu = 0.95
                _append_fan_note("FALSE START! GET LOUD! (0.95 VU)")
                st.rerun()
            if q_cols[1].button("THIRD DOWN ROAR!", use_container_width=True):
                st.session_state.vu = 0.90
                _append_fan_note("THIRD DOWN ROAR! (0.90 VU)")
                st.rerun()

        st.markdown("**Live Section Fan Feed:**")
        for note in reversed(st.session_state.fan_notes[-3:]):
            st.markdown(f"- 📢 *\"{note}\"*")

    # ------------------------------------------------------------------
    # Section Co-Op Synergy & Live Section Leaderboard
    # ------------------------------------------------------------------
    st.markdown("---")
    has_contributed_telemetry = (st.session_state.tap_count >= 1 or len(st.session_state.fan_notes) > 1)
    syn_col1, syn_col2 = st.columns([2, 1])
    with syn_col1:
        if not has_contributed_telemetry:
            st.info(f"⏳ **SECTION CO-OP ({coord_state['trigger_event']}):** Log at least 1 Pulse Tap or post a Fan Callout above to sync your energy with your section.")
        else:
            st.success(f"✅ **IN-ARENA ENERGY READY:** {st.session_state.tap_count} pulse tap(s) & section callout active!")

        if st.button("🤝 Sync My Energy With Section Co-Op", key="btn_synergy"):
            if not has_contributed_telemetry:
                st.warning("⚠️ Log at least 1 Pulse Tap or post a Fan Callout above first!")
            elif st.session_state.synergy_claimed:
                st.info(f"✅ Already synced for this play! Section Co-Op Synergy: {st.session_state.synergy_score}%.")
            else:
                synergy_gain = round(5 * coord_state["multiplier"])
                st.session_state.synergy_score = min(100, st.session_state.synergy_score + synergy_gain)
                st.session_state.synergy_claimed = True
                st.success(f"🎉 +{synergy_gain}% Section Synergy added (x{coord_state['multiplier']} multiplier)! Section Co-Op is now at {st.session_state.synergy_score}%!")
                st.rerun()
    with syn_col2:
        st.write(f"**Section Co-Op Synergy:** `{st.session_state.synergy_score}% Synchronized`")
        st.progress(st.session_state.synergy_score / 100.0)

    st.markdown("---")
    st.subheader(f"🏆 Live In-Arena Section Leaderboard ({st.session_state.sport})")

    _optimizer = SystemOptimizerAgent(sport=st.session_state.sport)
    if is_basketball:
        lead_sec  = "Section 114 (Thunder Row)"
        chase_sec = "Section 115 (End Zone Loyals)"
        third_sec = "Section 113 (Rider's Crew)"
    else:
        lead_sec  = "Section 115 (End Zone Loyals)"
        chase_sec = "Section 114 (Thunder Row)"
        third_sec = "Section 113 (Rider's Crew)"

    _standings = _optimizer.rank_sections_per_capita([
        {
            "name": lead_sec,
            "cmi": current_cmi,
            "checked_in_fans": 150,
            "early_multiplier": 1.25 if st.session_state.early_checkin else 1.0,
            "clutch_multiplier": coord_state["multiplier"],
        },
        {
            "name": chase_sec,
            "cmi": round(current_cmi * 0.92, 1),
            "checked_in_fans": 140,
            "early_multiplier": 1.0,
            "clutch_multiplier": 1.0,
        },
        {
            "name": third_sec,
            "cmi": round(current_cmi * 0.85, 1),
            "checked_in_fans": 120,
            "early_multiplier": 1.0,
            "clutch_multiplier": 1.0,
        },
    ])

    st.info(_standings["chaser_alert"])
    for rank, entry in enumerate(_standings["standings"], start=1):
        label = f"• **#{rank} {entry['section']}:** **{entry['score']} pts**"
        if rank == 1:
            label += " (Leading Section)"
        st.write(label)
        st.progress(min(1.0, entry["score"] / 100.0))

# ==============================================================================
# SCREEN 4: NARRATIVE DELTA & SHAREABLE CROWD BOX SCORE
# ==============================================================================
elif screen == "📊 Screen 4: Narrative Delta & Story Card":
    st.header(f"📊 Narrative Delta & Shareable Crowd Box Score ({st.session_state.sport})")
    st.caption("Post-play synthesis connecting crowd momentum to on-field execution, with viral story card export.")

    if "BB-01" in active_preset:
        pre_val = 37.8
        outcome_label = "PENDING PLAY EXECUTION (Free Throw 1)"
    elif "BB-02" in active_preset:
        pre_val = 37.8
        outcome_label = "MISSED FREE THROW (Defensive Rebound Secured)"
    elif "FB-01" in active_preset:
        pre_val = 39.0
        outcome_label = "TIMEOUT IN PROGRESS ('Icing the Kicker')"
    else:  # FB-02
        pre_val = 39.0
        outcome_label = "MISSED FIELD GOAL (Wide Left - Ice Successful)"

    actual_surge = round(max(0.0, current_cmi - pre_val), 1)

    if actual_surge == 0.0:
        surge_title = "+0.0 PTS (BASELINE ANTICIPATION)"
        card_sub = "PRE-PLAY BASELINE ESTABLISHED"
        card_points_display = "+0.0 PTS"
    else:
        surge_title = f"+{actual_surge} PTS MOMENTUM SURGE"
        card_sub = "CLUTCH DEFENSIVE IMPACT VERIFIED"
        card_points_display = f"+{actual_surge} PTS"

    st.markdown(f"""
    <div style="background-color: #edf5ff; padding: 18px; border-radius: 8px; border-left: 6px solid #0f62fe; margin-bottom: 20px;">
        <h2 style="color: #0043ce; margin: 0;">{surge_title}</h2>
        <p style="color: #161616; margin: 4px 0 0 0;">Pre-Play Baseline ({pre_val}/100) ➔ Current State ({current_cmi}/100) | Outcome: <b>{outcome_label}</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader(f"🤖 Post-Play Narrative Breakdown ({st.session_state.sport})")
    _narrative_key = f"narrative_{active_preset}_{current_cmi}"
    if _narrative_key not in st.session_state:
        with st.spinner(f"Synthesizing {st.session_state.sport} post-play narrative..."):
            st.session_state[_narrative_key] = generate_narrative_live(
                st.session_state.sport, outcome_label, pre_val, current_cmi, st.session_state.fan_notes
            )
    narrative = st.session_state[_narrative_key]
    st.markdown(f"> *{narrative}*")

    st.markdown("---")
    st.subheader("📲 One-Tap Shareable 'Proof-of-Momentum' Card")
    st.write(f"Share your verified in-arena {st.session_state.sport} impact to Instagram, TikTok, and X:")

    card_bg = "#161616"
    card_border = "#0f62fe" if current_cmi < 80 else "#da1e28"
    winning_sec = "Section 114 (Thunder Row)" if is_basketball else "Section 115 (End Zone Loyals)"

    st.markdown(f"""
    <div style="background-color: {card_bg}; border: 3px solid {card_border}; border-radius: 12px; padding: 24px; max-width: 500px; margin: 10px auto; color: white; text-align: center; box-shadow: 0 0 20px {card_border}66;">
        <p style="color: #0f62fe; font-weight: bold; letter-spacing: 2px; margin: 0; font-size: 11pt;">KINETIC FANLAB // OFFICIAL PROOF-OF-MOMENTUM</p>
        <h1 style="color: white; margin: 8px 0; font-size: 32pt;">{card_points_display}</h1>
        <p style="color: {card_border}; font-weight: bold; font-size: 14pt; margin: 0;">{card_sub}</p>
        <hr style="border-color: #333; margin: 14px 0;">
        <p style="color: #f4f4f4; font-size: 11pt; margin: 4px 0;">Sport: <b>{st.session_state.sport} ({role_tag})</b></p>
        <p style="color: #f4f4f4; font-size: 11pt; margin: 4px 0;">Acoustic Peak: <b>{st.session_state.db} dB</b> | Peak Heart Rate: <b>{int(st.session_state.hr)} BPM</b></p>
        <p style="color: #8d8d8d; font-size: 9.5pt; margin-top: 12px;">{winning_sec} Defense Belt Winner</p>
    </div>
    """, unsafe_allow_html=True)

    sh_col1, sh_col2, sh_col3 = st.columns([1, 2, 1])
    with sh_col2:
        if st.button("📲 Share Proof-of-Momentum to Instagram, TikTok & X", key="btn_share_proof_card", use_container_width=True):
            fixture_id = active_preset.split(":")[0].strip()
            if COS_ARCHIVE_LIVE:
                cos_lakehouse_archive(
                    fixture_id=fixture_id,
                    sport=st.session_state.sport,
                    cmi=current_cmi,
                    surge=actual_surge,
                    winning_section=winning_sec,
                    outcome=outcome_label,
                    granite_narrative=narrative,
                    fan_notes=st.session_state.fan_notes[-3:]
                )
            cloud_storage.archive_crowd_box_score(
                fixture_id=fixture_id,
                sport=st.session_state.sport,
                cmi=current_cmi,
                surge=actual_surge,
                winning_section=winning_sec,
                fan_contribution={
                    "tap_count": st.session_state.tap_count,
                    "peak_hr_bpm": int(st.session_state.hr),
                    "peak_db": st.session_state.db,
                    "vocal_urgency": st.session_state.vu,
                    "fan_notes": st.session_state.fan_notes[-3:],
                },
            )
            st.success(f"✅ Proof-of-Momentum card exported! Link copied: kineticfanlab.com/proof/{st.session_state.sport.lower()}/{int(current_cmi)}")

    st.markdown("---")
    st.subheader(f"🏆 Official Crowd Box Score: Section of the Game ({st.session_state.sport})")
    c1, c2 = st.columns(2)
    with c1:
        if is_basketball:
            st.markdown("""
            **Final Section Standings (Basketball):**
            * 🥇 **Section 114 (Thunder Row):** **96.8 pts** — *Winner: Section Defense Belt*
            * 🥈 **Section 115 (End Zone Loyals):** **92.4 pts**
            * 🥉 **Section 113 (Rider's Crew):** **85.6 pts**
            """)
        else:
            st.markdown("""
            **Final Section Standings (Football):**
            * 🥇 **Section 115 (End Zone Loyals):** **98.2 pts** — *Winner: Section Defense Belt*
            * 🥈 **Section 114 (Thunder Row):** **93.7 pts**
            * 🥉 **Section 216 (Upper North):** **81.4 pts**
            """)
    with c2:
        user_sec = "Section 114" if is_basketball else "Section 115"
        st.markdown(f"**Your Personal Fan Contribution ({user_sec}):**")
        st.write(f"* Momentum Pulse Taps Contributed: **{st.session_state.tap_count} taps**")
        st.write(f"* Peak Heart Rate Logged: **{int(st.session_state.hr)} BPM**")
        st.write(f"* Peak Acoustic Contribution: **{st.session_state.db} dB**")

# ==============================================================================
# SCREEN 5: AI SQUAD & GAME INTELLIGENCE (@coach, @conductor, @strategist, @scout)
# ==============================================================================
elif screen == "🤖 Screen 5: AI Squad & Game Intelligence":
    from orchestrate_agents import (
        compute_game_situation_scenarios,
        run_backend_squad_teamwork,
        get_agent_question_chips,
        get_agent_chat_placeholder,
    )

    st.header(f"🤖 Your AI Squad & Live Game Intelligence ({st.session_state.sport})")
    st.caption("Select an AI Squad member (`@coach`, `@conductor`, `@strategist`, `@scout`) to talk strategy and view live game scenarios.")

    persona_options = bb_members if is_basketball else fb_members
    p_idx = persona_options.index(st.session_state.active_member) if st.session_state.active_member in persona_options else 0
    active_fan = st.selectbox("Active Fan Profile:", persona_options, index=p_idx, key="s5_fan_select")
    st.session_state.active_member = active_fan
    p_info = PERSONA_DB[active_fan]
    fixture_code = active_preset.split(":")[0].strip()

    # Compute live game statistics & 3 scenarios via backend teamwork
    intel = compute_game_situation_scenarios(
        sport=st.session_state.sport,
        fixture_id=fixture_code,
        cmi=current_cmi,
        db=st.session_state.db,
        hr=st.session_state.hr,
        taps=st.session_state.taps,
        vu=st.session_state.vu,
        is_clutch=st.session_state.is_clutch,
        early_checkin=st.session_state.early_checkin,
        synergy_score=st.session_state.synergy_score,
    )

    # ------------------------------------------------------------------
    # PART 1: GAME-SPECIFIC STATISTICS, SITUATION & POSSIBLE SCENARIOS
    # ------------------------------------------------------------------
    banner_color = "#da1e28" if st.session_state.is_clutch else "#0f62fe"
    st.markdown(f"""
    <div style="background-color: #12161f; border-left: 5px solid {banner_color}; padding: 12px 16px; border-radius: 8px; margin-bottom: 14px;">
        <span style="color: {banner_color}; font-weight: bold; font-size: 9.5pt; text-transform: uppercase;">
            📊 LIVE GAME SITUATION — {intel['clock_situation']}
        </span>
        <span style="color: #f1c21b; font-weight: bold; font-size: 9.5pt; float: right;">
            Squad Synergy: {st.session_state.synergy_score}% | Multiplier: {intel['multiplier']}x
        </span><br>
        <span style="color: #f4f4f4; font-size: 10pt;">Active Cue: <b>{intel['pacing_directive']}</b></span>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric(intel["key_stat_label"], intel["key_stat_val"], delta=intel["key_stat_delta"])
    m2.metric(intel["miss_label"], f"{intel['current_miss_pct']}%", delta=f"At {current_cmi}/100 CMI")
    m3.metric("Home Win Prob Swing", f"+{intel['win_prob_swing']}%", delta="Live Crowd Factor")
    m4.metric("Section Rivalry Lead", f"+{intel['rivalry_lead']} pts", delta=f"#1 {p_info['sec'][:11]}")

    st.subheader("🔮 Possible Game Scenarios & Crowd Impact Projections")
    sc_cols = st.columns(3)
    scenario_colors = ["#0f62fe", "#8a3ffc", "#42be65"]
    for idx, sc in enumerate(intel["scenarios"]):
        sc_col = scenario_colors[idx % len(scenario_colors)]
        with sc_cols[idx]:
            st.markdown(f"""
            <div style="background-color: #161616; border-top: 4px solid {sc_col}; border-radius: 8px; padding: 14px; min-height: 175px;">
                <h5 style="color: {sc_col}; margin: 0 0 6px 0;">{sc['scenario']}</h5>
                <p style="color: #f4f4f4; font-size: 9.5pt; margin: 4px 0;"><b>Target Momentum:</b> {sc['target_cmi']}</p>
                <p style="color: #a8a8a8; font-size: 9pt; margin: 4px 0;"><b>Play Needed:</b> {sc['required_action']}</p>
                <p style="color: #f1c21b; font-size: 9.5pt; margin: 4px 0;"><b>On-Field Odds:</b> {sc['opponent_impact']}</p>
                <p style="color: #42be65; font-size: 9pt; margin: 4px 0;"><b>Win Swing:</b> {sc['win_prob_delta']} • {sc['section_outcome']}</p>
            </div>
            """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # PART 2: QUICK @AGENT SELECTOR BUTTONS & TWO-WAY SQUAD CHAT
    # ------------------------------------------------------------------
    st.markdown("---")
    st.subheader("💬 Direct Comms With Your AI Squad")
    st.caption("Click a button below to choose which Squad specialist you're talking to—on the backend, all 4 agents share live insights as one team.")

    btn_c1, btn_c2, btn_c3, btn_c4, btn_c5 = st.columns(5)
    if btn_c1.button("🏅 @coach", use_container_width=True, key="sel_coach"):
        st.session_state.selected_squad_agent = "@coach"
    if btn_c2.button("⏱️ @conductor", use_container_width=True, key="sel_conductor"):
        st.session_state.selected_squad_agent = "@conductor"
    if btn_c3.button("🏆 @strategist", use_container_width=True, key="sel_strategist"):
        st.session_state.selected_squad_agent = "@strategist"
    if btn_c4.button("📊 @scout", use_container_width=True, key="sel_scout"):
        st.session_state.selected_squad_agent = "@scout"
    if btn_c5.button("⚡ @squad (All 4)", use_container_width=True, key="sel_squad"):
        st.session_state.selected_squad_agent = "@squad"

    active_tag = st.session_state.selected_squad_agent
    tag_descriptions = {
        "@coach": ("🏅 @coach — The Hype Coach", "Personal Tier Progression, Clutch Stops & Trophy Perks", "#42be65"),
        "@conductor": ("⏱️ @conductor — The Conductor", "Play Clock Timing, Wave Sync & Multiplier Windows", "#0f62fe"),
        "@strategist": ("🏆 @strategist — The Strategist", "Section Rivalry Standings, Matchups & Game Scenarios", "#f1c21b"),
        "@scout": ("📊 @scout — The Scout", "Live Game Statistics, Shooter/Kicker Odds & Telemetry", "#8a3ffc"),
        "@squad": ("⚡ @squad — Full AI Squad", "Combined Briefing From All 4 Squad Specialists", "#0f62fe"),
    }
    ag_title, ag_desc, ag_color = tag_descriptions.get(active_tag, tag_descriptions["@strategist"])

    st.markdown(f"""
    <div style="background-color: #1a1a1a; border-left: 5px solid {ag_color}; padding: 10px 16px; border-radius: 6px; margin: 6px 0 12px 0;">
        <span style="color: {ag_color}; font-weight: bold; font-size: 10.5pt;">Speaking to: {ag_title}</span><br>
        <span style="color: #a8a8a8; font-size: 9pt;">Specialty: {ag_desc} (Backed by real-time teamwork from all 4 Squad agents)</span>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic Situational Question Chips Framed Specifically for the Active Agent & Sport
    chips = get_agent_question_chips(
        active_tag,
        st.session_state.sport,
        active_fan,
        p_info,
    )
    q_chip1, q_chip2, q_chip3 = st.columns(3)
    quick_prompt = None
    if q_chip1.button(chips[0]["chip_label"], use_container_width=True, key=f"qp_0_{active_tag}_{st.session_state.sport}"):
        quick_prompt = chips[0]["full_question"]
    if q_chip2.button(chips[1]["chip_label"], use_container_width=True, key=f"qp_1_{active_tag}_{st.session_state.sport}"):
        quick_prompt = chips[1]["full_question"]
    if q_chip3.button(chips[2]["chip_label"], use_container_width=True, key=f"qp_2_{active_tag}_{st.session_state.sport}"):
        quick_prompt = chips[2]["full_question"]

    with st.form(key="squad_direct_chat_form", clear_on_submit=True):
        chat_col_in, chat_col_btn = st.columns([4, 1])
        with chat_col_in:
            chat_ph = get_agent_chat_placeholder(active_tag, st.session_state.sport)
            typed_msg = st.text_input(
                f"Message {active_tag}:",
                placeholder=chat_ph,
                label_visibility="collapsed",
            )
        with chat_col_btn:
            send_chat = st.form_submit_button(f"Send to {active_tag}", use_container_width=True)

    final_user_msg = quick_prompt if quick_prompt else (typed_msg.strip() if (send_chat and typed_msg.strip()) else None)

    if final_user_msg:
        # Support inline @tag switching if the user types @coach, @conductor, @strategist, or @scout in the message
        for candidate_tag in ("@coach", "@conductor", "@strategist", "@scout", "@squad"):
            if candidate_tag in final_user_msg.lower():
                active_tag = candidate_tag
                st.session_state.selected_squad_agent = candidate_tag
                break

        team_res = run_backend_squad_teamwork(
            target_agent_tag=active_tag,
            user_message=final_user_msg,
            member_name=active_fan,
            persona_data=p_info,
            sport=st.session_state.sport,
            fixture_id=fixture_code,
            cmi=current_cmi,
            db=st.session_state.db,
            hr=st.session_state.hr,
            taps=st.session_state.taps,
            vu=st.session_state.vu,
            is_clutch=st.session_state.is_clutch,
            early_checkin=st.session_state.early_checkin,
            synergy_score=st.session_state.synergy_score,
        )
        # Boost synergy & momentum slightly as user and squad collaborate
        st.session_state.synergy_score = min(100, st.session_state.synergy_score + 3)
        st.session_state.taps = min(15.0, round(st.session_state.taps + 0.5, 1))
        st.session_state.squad_chat_history.append({
            "fan": active_fan,
            "target": active_tag,
            "user_msg": final_user_msg,
            "speaker_title": team_res["speaker_title"],
            "reply": team_res["reply"],
        })
        if len(st.session_state.squad_chat_history) > 10:
            st.session_state.squad_chat_history = st.session_state.squad_chat_history[-10:]

        _trigger_silent_backend_pipeline(
            fixture_code, st.session_state.sport, active_fan, p_info["hash"], p_info["sec"],
            final_user_msg, st.session_state.db, st.session_state.hr, st.session_state.taps, st.session_state.vu, st.session_state.is_clutch
        )
        st.rerun()

    # Render Conversation Feed (Most Recent First)
    sport_icon = "🏀" if is_basketball else "🏈"
    if not st.session_state.squad_chat_history:
        default_team = run_backend_squad_teamwork(
            target_agent_tag=active_tag,
            user_message=f"Give me our live {'free throw' if is_basketball else 'field goal'} defensive situation breakdown.",
            member_name=active_fan,
            persona_data=p_info,
            sport=st.session_state.sport,
            fixture_id=fixture_code,
            cmi=current_cmi,
            db=st.session_state.db,
            hr=st.session_state.hr,
            taps=st.session_state.taps,
            vu=st.session_state.vu,
            is_clutch=st.session_state.is_clutch,
            early_checkin=st.session_state.early_checkin,
            synergy_score=st.session_state.synergy_score,
        )
        st.markdown(f"""
        <div style="background-color: #141923; border: 1px solid {ag_color}; border-radius: 8px; padding: 14px 16px; margin-top: 8px;">
            <span style="color: {ag_color}; font-weight: bold; font-size: 9.5pt;">{sport_icon} {default_team['speaker_title']} — Ready on Channel:</span>
            <p style="color: #f4f4f4; font-size: 10pt; margin: 6px 0 0 0;">{default_team['reply']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in reversed(st.session_state.squad_chat_history[-5:]):
            st.markdown(f"""
            <div style="background-color: #161616; border-left: 3px solid #8d8d8d; padding: 8px 14px; border-radius: 6px; margin-top: 8px;">
                <span style="color: #a8a8a8; font-size: 9pt;"><b>You ({msg['fan']})</b> ➔ <code>{msg['target']}</code>:</span>
                <span style="color: #f4f4f4; font-size: 10pt;"> "{msg['user_msg']}"</span>
            </div>
            <div style="background-color: #141923; border-left: 4px solid #42be65; padding: 10px 16px; border-radius: 6px; margin-bottom: 10px;">
                <span style="color: #42be65; font-weight: bold; font-size: 9.5pt;">{sport_icon} {msg['speaker_title']}:</span>
                <p style="color: #f4f4f4; font-size: 10pt; margin: 4px 0 0 0;">{msg['reply']}</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("Clear Squad Chat History", key="btn_clear_sq_chat"):
            st.session_state.squad_chat_history = []
            st.rerun()
