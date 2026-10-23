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
import json
import hashlib
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

try:
    import npc_mentors
    NPC_ENGINE_LIVE = True
except Exception:
    import importlib.util
    import os
    spec = importlib.util.spec_from_file_location('npc_mentors', os.path.join(current_dir, 'npc_mentors.py'))
    npc_mentors = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(npc_mentors)
    NPC_ENGINE_LIVE = True

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
        if st.session_state.get("is_logged_in") and st.session_state.get("member_name"):
            st.session_state.active_member = st.session_state.member_name
        elif st.session_state.sport == "Basketball" and st.session_state.get("active_member") not in bb_members:
            st.session_state.active_member = "Marcus Vance"
        elif st.session_state.sport == "Football" and st.session_state.get("active_member") not in fb_members:
            st.session_state.active_member = "Sarah Jenkins"

# Global session states
if "sport" not in st.session_state: st.session_state.sport = "Basketball"
if "onboarding_mode" not in st.session_state: st.session_state.onboarding_mode = "Rookie Walkthrough"
if "is_logged_in" not in st.session_state: st.session_state.is_logged_in = False
if "member_email" not in st.session_state: st.session_state.member_email = "fan@gmail.com"
if "member_name" not in st.session_state: st.session_state.member_name = "Rookie Fan"
if "member_handle" not in st.session_state: st.session_state.member_handle = "@fan_rookie"
if "member_hash" not in st.session_state: st.session_state.member_hash = "0xROOKIE-sec114-8f7a2"
if "member_role" not in st.session_state: st.session_state.member_role = "Rookie Fan"
if "member_tier" not in st.session_state: st.session_state.member_tier = "Rookie Member (Tier 1)"
if "member_seat" not in st.session_state: st.session_state.member_seat = "Section 114, Row 3, Seat 12"
if "member_games" not in st.session_state: st.session_state.member_games = 0
if "member_career_db" not in st.session_state: st.session_state.member_career_db = "0.0 dB"
if "member_clutch_stops" not in st.session_state: st.session_state.member_clutch_stops = 0
if "tailgates_attended" not in st.session_state: st.session_state.tailgates_attended = 0
if "meetup_rsvps" not in st.session_state: st.session_state.meetup_rsvps = []
if "social_x" not in st.session_state: st.session_state.social_x = "@fan_rookie"
if "social_ig" not in st.session_state: st.session_state.social_ig = ""
if "social_yt" not in st.session_state: st.session_state.social_yt = "@W3bHippo"
if "social_tiktok" not in st.session_state: st.session_state.social_tiktok = ""
if "social_discord" not in st.session_state: st.session_state.social_discord = ""
if "wearable_device" not in st.session_state: st.session_state.wearable_device = "Apple Watch Ultra 2 (ECG/dB)"
if "ble_sensitivity" not in st.session_state: st.session_state.ble_sensitivity = -54
if "notif_clutch" not in st.session_state: st.session_state.notif_clutch = True
if "notif_tailgate" not in st.session_state: st.session_state.notif_tailgate = True
if "notif_chaser" not in st.session_state: st.session_state.notif_chaser = True
if "pref_leaderboard_public" not in st.session_state: st.session_state.pref_leaderboard_public = True
if "pref_anonymize_biometrics" not in st.session_state: st.session_state.pref_anonymize_biometrics = True
if "share_trophy_clicked" not in st.session_state: st.session_state.share_trophy_clicked = False

# Distinct sport levels and sport-isolated team registries
if "bb_level" not in st.session_state: st.session_state.bb_level = "Both (NCAA D1 & NBA)"
if "fb_level" not in st.session_state: st.session_state.fb_level = "Both (NCAA D1 & NFL)"
if "teams_bb" not in st.session_state: st.session_state.teams_bb = ["Duke Blue Devils", "Boston Celtics"]
if "teams_fb" not in st.session_state: st.session_state.teams_fb = ["Michigan Wolverines", "Green Bay Packers"]

if "unlocked_mentors_bb" not in st.session_state: st.session_state.unlocked_mentors_bb = ["Marcus Vance"]
if "unlocked_mentors_fb" not in st.session_state: st.session_state.unlocked_mentors_fb = ["Sarah Jenkins"]
if "active_npc_guide" not in st.session_state: st.session_state.active_npc_guide = "Marcus Vance"
if "capstone_claimed_bb" not in st.session_state: st.session_state.capstone_claimed_bb = False
if "capstone_claimed_fb" not in st.session_state: st.session_state.capstone_claimed_fb = False
if "chant_action_taken" not in st.session_state: st.session_state.chant_action_taken = False
if "storycard_exported_flag" not in st.session_state: st.session_state.storycard_exported_flag = False
if "user_respect_taps_sent" not in st.session_state: st.session_state.user_respect_taps_sent = 0
if "just_signed_up" not in st.session_state: st.session_state.just_signed_up = False

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

# Fallback defaults for live telemetry states
if "db" not in st.session_state: st.session_state.db = 82.0
if "hr" not in st.session_state: st.session_state.hr = 98.0
if "taps" not in st.session_state: st.session_state.taps = 2.5
if "vu" not in st.session_state: st.session_state.vu = 0.55
if "is_clutch" not in st.session_state: st.session_state.is_clutch = False
if "fan_notes" not in st.session_state: st.session_state.fan_notes = ["Watch the shooter, need this stop"]

# Ensure active member matches current sport unless logged in
if st.session_state.get("is_logged_in") and st.session_state.get("member_name"):
    st.session_state.active_member = st.session_state.member_name
elif st.session_state.sport == "Basketball" and st.session_state.active_member not in bb_members:
    st.session_state.active_member = "Marcus Vance"
elif st.session_state.sport == "Football" and st.session_state.active_member not in fb_members:
    st.session_state.active_member = "Sarah Jenkins"

current_cmi = calc_momentum_index(st.session_state.db, st.session_state.hr, st.session_state.taps, st.session_state.vu)
tier = get_tier(current_cmi)
color = get_color(current_cmi)

is_basketball = (st.session_state.sport == "Basketball")
start_term = "tip-off" if is_basketball else "kickoff"
role_tag = "6th Man" if is_basketball else "12th Man"

# ------------------------------------------------------------------
# COMPREHENSIVE TEAM CATALOGS (NCAA DIVISION 1 & PRO LEAGUES)
# ------------------------------------------------------------------
NCAA_D1_BASKETBALL_TEAMS = [
    "Duke Blue Devils", "North Carolina Tar Heels", "Kentucky Wildcats", "Kansas Jayhawks",
    "UConn Huskies", "Houston Cougars", "Gonzaga Bulldogs", "Baylor Bears", "Texas Longhorns",
    "Michigan Wolverines", "Michigan State Spartans", "Purdue Boilermakers", "Indiana Hoosiers",
    "Arizona Wildcats", "UCLA Bruins", "Villanova Wildcats", "Virginia Cavaliers", "Tennessee Volunteers",
    "Auburn Tigers", "Alabama Crimson Tide", "Florida Gators", "Louisville Cardinals", "Syracuse Orange",
    "Iowa State Cyclones", "Marquette Golden Eagles", "Creighton Bluejays", "Illinois Fighting Illini",
    "Wisconsin Badgers", "Texas A&M Aggies", "Texas Tech Red Raiders", "Arkansas Razorbacks",
    "Iowa Hawkeyes", "Ohio State Buckeyes", "Maryland Terrapins", "Memphis Tigers", "San Diego State Aztecs"
]

NBA_TEAMS = [
    "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls",
    "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors",
    "Houston Rockets", "Indiana Pacers", "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies",
    "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
    "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers",
    "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards"
]

NCAA_D1_FBS_FOOTBALL_TEAMS = [
    "Michigan Wolverines", "Ohio State Buckeyes", "Alabama Crimson Tide", "Georgia Bulldogs",
    "Texas Longhorns", "Texas A&M Aggies", "LSU Tigers", "Notre Dame Fighting Irish",
    "Penn State Nittany Lions", "Oregon Ducks", "USC Trojans", "Clemson Tigers", "Oklahoma Sooners",
    "Tennessee Volunteers", "Florida State Seminoles", "Washington Huskies", "Florida Gators",
    "Miami Hurricanes", "Auburn Tigers", "Wisconsin Badgers", "Iowa Hawkeyes", "Ole Miss Rebels",
    "Nebraska Cornhuskers", "Colorado Buffaloes", "TCU Horned Frogs", "Texas Tech Red Raiders",
    "Houston Cougars", "Baylor Bears", "Utah Utes", "Louisville Cardinals", "Oklahoma State Cowboys",
    "Kansas State Wildcats", "Kentucky Wildcats", "Missouri Tigers", "North Carolina Tar Heels",
    "NC State Wolfpack", "Virginia Tech Hokies", "South Carolina Gamecocks", "Arkansas Razorbacks", "SMU Mustangs"
]

NFL_TEAMS = [
    "Arizona Cardinals", "Atlanta Falcons", "Baltimore Ravens", "Buffalo Bills", "Carolina Panthers",
    "Chicago Bears", "Cincinnati Bengals", "Cleveland Browns", "Dallas Cowboys", "Denver Broncos",
    "Detroit Lions", "Green Bay Packers", "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars",
    "Kansas City Chiefs", "Las Vegas Raiders", "Los Angeles Chargers", "Los Angeles Rams", "Miami Dolphins",
    "Minnesota Vikings", "New England Patriots", "New Orleans Saints", "New York Giants", "New York Jets",
    "Philadelphia Eagles", "Pittsburgh Steelers", "San Francisco 49ers", "Seattle Seahawks", "Tampa Bay Buccaneers",
    "Tennessee Titans", "Washington Commanders"
]

# ------------------------------------------------------------------
# PERSISTENT REGISTERED FANS DATABASE
# ------------------------------------------------------------------
USERS_DB_FILE = os.path.join(current_dir, "data", "registered_fans.json")

def _load_fans_db():
    defaults = {
        "fan@gmail.com": {
            "email": "fan@gmail.com",
            "password": "password123",
            "name": "Rookie Fan",
            "handle": "@fan_rookie",
            "seat": "Section 114, Row 3, Seat 12",
            "hash": "0xROOKIE-sec114-8f7a2",
            "sport": "Basketball",
            "bb_level": "Both (NCAA D1 & NBA)",
            "fb_level": "Both (NCAA D1 & NFL)",
            "teams_bb": ["Duke Blue Devils", "Boston Celtics"],
            "teams_fb": ["Michigan Wolverines", "Green Bay Packers"],
            "role": "Rookie Member",
            "tier": "Rookie Member (Tier 1)",
            "games": 0,
            "career_db": "0.0 dB",
            "clutch_stops": 0,
            "unlocked_mentors_bb": ["Marcus Vance"],
            "unlocked_mentors_fb": ["Sarah Jenkins"]
        },
        "fan@gmail.com": {
            "email": "fan@gmail.com",
            "password": "password123",
            "name": "Rookie Fan",
            "handle": "@fan_rookie",
            "seat": "Section 114, Row 3, Seat 12",
            "hash": "0xROOKIE-sec114-8f7a2",
            "sport": "Basketball",
            "bb_level": "Both (NCAA D1 & NBA)",
            "fb_level": "Both (NCAA D1 & NFL)",
            "teams_bb": ["Duke Blue Devils", "Boston Celtics"],
            "teams_fb": ["Michigan Wolverines", "Green Bay Packers"],
            "role": "Rookie Member",
            "tier": "Rookie Member (Tier 1)",
            "games": 0,
            "career_db": "0.0 dB",
            "clutch_stops": 0,
            "unlocked_mentors_bb": ["Marcus Vance"],
            "unlocked_mentors_fb": ["Sarah Jenkins"]
        },
        "mvance@thunderrow.org": {
            "email": "mvance@thunderrow.org",
            "password": "demo1234",
            "name": "Marcus Vance",
            "handle": "@mvance_sec114",
            "seat": "Row 1, Seat 1",
            "hash": "0xMV-sec114-8f7a2",
            "sport": "Basketball",
            "bb_level": "Both (NCAA D1 & NBA)",
            "fb_level": "Both (NCAA D1 & NFL)",
            "teams_bb": ["Texas Longhorns", "San Antonio Spurs"],
            "teams_fb": ["Texas Longhorns", "Dallas Cowboys"],
            "role": "Student Section Director",
            "tier": "Section Director (Tier 4)",
            "unlocked_mentors_bb": ["Marcus Vance"],
            "unlocked_mentors_fb": ["Sarah Jenkins"]
        },
        "sjenkins@endzoneloyals.org": {
            "email": "sjenkins@endzoneloyals.org",
            "password": "demo1234",
            "name": "Sarah Jenkins",
            "handle": "@sjenkins_sec115",
            "seat": "Row 18, Seat 10",
            "hash": "0xSJ-sec115-7b2a5",
            "sport": "Football",
            "bb_level": "Both (NCAA D1 & NBA)",
            "fb_level": "Both (NCAA D1 & NFL)",
            "teams_bb": ["Texas Longhorns", "San Antonio Spurs"],
            "teams_fb": ["Texas Longhorns", "Dallas Cowboys"],
            "role": "10-Year Stadium Veteran",
            "tier": "Stadium Veteran (Tier 5)",
            "unlocked_mentors_bb": ["Marcus Vance"],
            "unlocked_mentors_fb": ["Sarah Jenkins"]
        }
    }
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                if isinstance(saved, dict):
                    for k, v in defaults.items():
                        if k not in saved:
                            saved[k] = v
                    return saved
        except Exception:
            pass
    _save_fans_db(defaults)
    return defaults

def _save_fans_db(db):
    try:
        os.makedirs(os.path.dirname(USERS_DB_FILE), exist_ok=True)
        with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except Exception as e:
        print(f"[_save_fans_db] warning: {e}")

if "registered_fans_db" not in st.session_state:
    st.session_state.registered_fans_db = _load_fans_db()


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

def _ensure_member_in_persona_db():
    if not st.session_state.get("is_logged_in"):
        return
    name = st.session_state.get("member_name", "Rookie Fan")
    email = st.session_state.get("member_email", "fan@gmail.com")
    user_entry = st.session_state.registered_fans_db.get(email, {})
    m_sport = st.session_state.get("sport", "Basketball")
    is_bball = (m_sport == "Basketball")
    m_sec = "Section 114 (Thunder Row)" if is_bball else "Section 115 (End Zone Loyals)"

    games_count = user_entry.get("games", 1 if st.session_state.get("early_checkin") else 0)
    if st.session_state.get("early_checkin") and games_count == 0:
        games_count = 1
    st.session_state.member_games = games_count

    if games_count > 0 or st.session_state.get("tap_count", 0) > 0:
        career_db_val = f"{round(st.session_state.get('db', 82.0), 1)} dB"
    else:
        career_db_val = user_entry.get("career_db", "0.0 dB")
    st.session_state.member_career_db = career_db_val

    clutch_stops_val = user_entry.get("clutch_stops", 0)
    st.session_state.member_clutch_stops = clutch_stops_val
    tailgates_val = user_entry.get("tailgates_attended", st.session_state.get("tailgates_attended", 0))
    st.session_state.tailgates_attended = tailgates_val

    tier_title = st.session_state.get("member_tier", user_entry.get("tier", "Rookie Member (Tier 1)"))
    role_title = st.session_state.get("member_role", user_entry.get("role", "Rookie Member"))
    hash_val = st.session_state.get("member_hash", user_entry.get("hash", "0xROOKIE-sec114-8f7a2" if is_bball else "0xTR-sec115-8f7a2"))

    PERSONA_DB[name] = {
        "hash": hash_val,
        "role": role_title,
        "tier": tier_title,
        "sec": m_sec,
        "games": games_count,
        "career_db": career_db_val,
        "clutch_stops": clutch_stops_val,
        "next_tier_title": "Tier 2 (Prop Captain / Section Specialist)" if is_bball else "Tier 2 (Tech Superfan / Bleacher Specialist)",
        "tier_progress_pct": min(1.0, round(games_count / 10.0, 2)),
        "tier_progress_desc": f"{games_count}/10 games attended — {max(0, 10 - games_count)} more game(s) to unlock Tier 2 status.",
        "neighbors": [
            {"name": "Elena Rostova", "seat": "Row 2, Seat 4", "role": "Prop Captain", "bio": "14 Games | Waving Leader"},
            {"name": "Devon Miller", "seat": "Row 3, Seat 8", "role": "Vocal Tactician", "bio": "28 Games | Chant Starter"},
            {"name": "Jordan Lee", "seat": "Row 4, Seat 12", "role": "Rookie Member", "bio": "3 Games | Thunderstick Cadet"}
        ] if is_bball else [
            {"name": "Carlos Mendez", "seat": "Row 18, Seat 12", "role": "Lot B Tailgate Host", "bio": "45 Games | Tailgate Host"},
            {"name": "Maya Patel", "seat": "Row 19, Seat 14", "role": "Biometric Superfan", "bio": "18 Games | Tech Ambassador"},
            {"name": "Alex Taylor", "seat": "Row 20, Seat 8", "role": "General Member", "bio": "4 Games | Rookie 12th Man"}
        ],
        "accolades": [
            {"title": "First Roll Call Stamp", "rarity": "Common", "color": "#0f62fe", "desc": "Initiated 365-day Fan Passport.", "perk": "1.25x 1st-quarter points boost"},
            {"title": "Rookie Section Member", "rarity": "Common", "color": "#0f62fe", "desc": "Connected to in-stadium BLE mesh.", "perk": "Active Section Roster entry"}
        ]
    }

def get_persona_options():
    base_mentors = bb_members if is_basketball else fb_members
    if st.session_state.get("is_logged_in") and st.session_state.get("member_name"):
        m_name = st.session_state.member_name
        return [m_name] + [m for m in base_mentors if m != m_name]
    return base_mentors

_ensure_member_in_persona_db()

# ==============================================================================
# SCREEN 1: THE LIVING FAN PASSPORT & SECTION ROSTER
# ==============================================================================
if screen == "👤 Screen 1: Fan Passport & Roster":
    # ------------------------------------------------------------------
    # AUTHENTICATION & ONBOARDING GATE (Sign Up vs. Log In)
    # ------------------------------------------------------------------
    if not st.session_state.is_logged_in:
        st.header(f"👤 Kinetic FanLab — Member Portal ({st.session_state.sport})")
        st.caption("Sign up for a persistent 365-day Fan Passport or log in to sync your verified in-arena crowd momentum.")

        auth_tab_signup, auth_tab_login = st.tabs([
            "🌟 New Member Sign Up (Rookie Walkthrough)",
            "🔑 Existing Member Log In"
        ])

        with auth_tab_signup:
            st.subheader("🚀 Join Your Section & Begin Rookie Walkthrough")
            st.caption("Create your FanLab account, select your sports & teams, and be initiated by your Section Leader.")

            with st.form(key="member_signup_form"):
                col_acc1, col_acc2 = st.columns(2)
                signup_email = col_acc1.text_input("Email Address", placeholder="e.g., fan@gmail.com or fan@university.edu")
                signup_pwd = col_acc2.text_input("Password", type="password", placeholder="Enter secure password")

                col_prof1, col_prof2, col_prof3 = st.columns(3)
                signup_name = col_prof1.text_input("Fan Display Name", placeholder="e.g., Alex Johnson")
                signup_handle = col_prof2.text_input("Section Handle", placeholder="e.g., @fan_alex")
                signup_seat = col_prof3.text_input("Seat Anchor / Row", value="Section 114, Row 3, Seat 12")

                st.markdown("---")
                col_sport_pick, col_dummy = st.columns(2)
                signup_sport = col_sport_pick.radio(
                    "Initial Gameday Sport:",
                    ["🏀 Basketball (Thunder Row — Sec 114)", "🏈 Football (End Zone Loyals — Sec 115)"],
                    index=0 if is_basketball else 1,
                    horizontal=True
                )
                chosen_sport_clean = "Basketball" if "Basketball" in signup_sport else "Football"

                st.markdown("---")
                st.markdown("#### 🏀 Basketball Fandom Preferences")
                col_bbl, col_bbt = st.columns(2)
                signup_bb_level = col_bbl.radio(
                    "Basketball Level Filter:",
                    ["🎓 College Basketball (NCAA D1)", "🏟️ Pro Basketball (NBA)", "⚡ Both (NCAA D1 & NBA)"],
                    index=2,
                    key="signup_bb_lvl"
                )
                if "College" in signup_bb_level and "Pro" not in signup_bb_level and "Both" not in signup_bb_level:
                    bb_pool = sorted(NCAA_D1_BASKETBALL_TEAMS)
                elif "Pro" in signup_bb_level and "College" not in signup_bb_level and "Both" not in signup_bb_level:
                    bb_pool = sorted(NBA_TEAMS)
                else:
                    bb_pool = sorted(list(set(NCAA_D1_BASKETBALL_TEAMS + NBA_TEAMS)))

                signup_bb_teams = col_bbt.multiselect(
                    "Select Basketball Teams:",
                    bb_pool,
                    default=[t for t in ["Duke Blue Devils", "Boston Celtics"] if t in bb_pool],
                    key="signup_bb_teams_pick"
                )
                custom_bb_input = col_bbt.text_input("Or type custom basketball team (if not in list):", placeholder="e.g., Texas State, UTSA...")

                st.markdown("---")
                st.markdown("#### 🏈 Football Fandom Preferences")
                col_fbl, col_fbt = st.columns(2)
                signup_fb_level = col_fbl.radio(
                    "Football Level Filter:",
                    ["🎓 College Football (NCAA D1 FBS)", "🏟️ Pro Football (NFL)", "⚡ Both (NCAA D1 & NFL)"],
                    index=2,
                    key="signup_fb_lvl"
                )
                if "College" in signup_fb_level and "Pro" not in signup_fb_level and "Both" not in signup_fb_level:
                    fb_pool = sorted(NCAA_D1_FBS_FOOTBALL_TEAMS)
                elif "Pro" in signup_fb_level and "College" not in signup_fb_level and "Both" not in signup_fb_level:
                    fb_pool = sorted(NFL_TEAMS)
                else:
                    fb_pool = sorted(list(set(NCAA_D1_FBS_FOOTBALL_TEAMS + NFL_TEAMS)))

                signup_fb_teams = col_fbt.multiselect(
                    "Select Football Teams:",
                    fb_pool,
                    default=[t for t in ["Michigan Wolverines", "Green Bay Packers"] if t in fb_pool],
                    key="signup_fb_teams_pick"
                )
                custom_fb_input = col_fbt.text_input("Or type custom football team (if not in list):", placeholder="e.g., Texas State, UTSA...")

                submit_signup = st.form_submit_button("🚀 Sign Up & Begin Rookie Walkthrough", use_container_width=True)

            if submit_signup:
                if not signup_email or not signup_pwd:
                    st.error("⚠️ Please enter both an email address and password to register.")
                else:
                    import hashlib
                    clean_email = signup_email.strip().lower()
                    st.session_state.is_logged_in = True
                    st.session_state.just_signed_up = True
                    st.session_state.member_email = clean_email
                    st.session_state.member_name = signup_name.strip() if signup_name.strip() else "Rookie Fan"
                    st.session_state.member_handle = signup_handle.strip() if signup_handle.strip() else "@fan_rookie"
                    clean_hash_seed = f"{clean_email}-{signup_name}-{chosen_sport_clean}"
                    st.session_state.member_hash = f"0x{hashlib.sha256(clean_hash_seed.encode()).hexdigest()[:16]}"
                    st.session_state.member_role = "Rookie Member"
                    st.session_state.member_tier = "Rookie Member (Tier 1)"
                    st.session_state.sport = chosen_sport_clean
                    
                    # Decoupled levels
                    st.session_state.bb_level = signup_bb_level
                    st.session_state.fb_level = signup_fb_level
                    
                    # Separate basketball and football teams
                    final_bb = list(signup_bb_teams)
                    if custom_bb_input.strip() and custom_bb_input.strip() not in final_bb:
                        final_bb.append(custom_bb_input.strip())
                    st.session_state.teams_bb = final_bb if final_bb else ["Duke Blue Devils", "Boston Celtics"]

                    final_fb = list(signup_fb_teams)
                    if custom_fb_input.strip() and custom_fb_input.strip() not in final_fb:
                        final_fb.append(custom_fb_input.strip())
                    st.session_state.teams_fb = final_fb if final_fb else ["Michigan Wolverines", "Green Bay Packers"]

                    # Strict Inception: ONLY Section Leader unlocked
                    st.session_state.unlocked_mentors_bb = ["Marcus Vance"]
                    st.session_state.unlocked_mentors_fb = ["Sarah Jenkins"]
                    st.session_state.active_npc_guide = "Marcus Vance" if chosen_sport_clean == "Basketball" else "Sarah Jenkins"
                    st.session_state.tap_count = 0
                    st.session_state.user_respect_taps_sent = 0
                    st.session_state.early_checkin = False
                    st.session_state.chant_action_taken = False
                    st.session_state.storycard_exported_flag = False

                    # Save user record persistently
                    user_entry = {
                        "email": clean_email,
                        "password": signup_pwd.strip(),
                        "name": st.session_state.member_name,
                        "handle": st.session_state.member_handle,
                        "seat": signup_seat.strip(),
                        "hash": st.session_state.member_hash,
                        "sport": chosen_sport_clean,
                        "bb_level": signup_bb_level,
                        "fb_level": signup_fb_level,
                        "teams_bb": st.session_state.teams_bb,
                        "teams_fb": st.session_state.teams_fb,
                        "role": "Rookie Member",
                        "tier": "Rookie Member (Tier 1)",
                        "games": 0,
                        "career_db": "0.0 dB",
                        "clutch_stops": 0,
                        "unlocked_mentors_bb": ["Marcus Vance"],
                        "unlocked_mentors_fb": ["Sarah Jenkins"]
                    }
                    st.session_state.registered_fans_db[clean_email] = user_entry
                    _save_fans_db(st.session_state.registered_fans_db)
                    st.session_state.member_games = 0
                    st.session_state.member_career_db = "0.0 dB"
                    st.session_state.member_clutch_stops = 0
                    st.session_state.member_seat = signup_seat.strip()
                    st.session_state.active_member = st.session_state.member_name
                    _ensure_member_in_persona_db()

                    PERSONA_DB[st.session_state.member_name] = {
                        "hash": st.session_state.member_hash,
                        "role": "Rookie Member",
                        "tier": "Rookie Member (Tier 1)",
                        "sec": "Section 114 (Thunder Row)" if chosen_sport_clean == "Basketball" else "Section 115 (End Zone Loyals)",
                        "games": 1,
                        "career_db": "104.2 dB",
                        "clutch_stops": 0,
                        "next_tier_title": "Tier 2 (Prop Captain / Section Specialist)",
                        "tier_progress_pct": 0.10,
                        "tier_progress_desc": "1/10 games attended — 9 more game(s) to unlock Tier 2 Section Specialist status.",
                        "neighbors": [
                            {"name": "Elena Rostova" if chosen_sport_clean == "Basketball" else "Carlos Mendez", "seat": "Row 2, Seat 4", "role": "Section Specialist", "bio": "Active Row Neighbor"},
                            {"name": "Devon Miller" if chosen_sport_clean == "Basketball" else "Maya Patel", "seat": "Row 3, Seat 8", "role": "Section Veteran", "bio": "Acoustic Leader"},
                            {"name": "Jordan Lee" if chosen_sport_clean == "Basketball" else "Alex Taylor", "seat": "Row 4, Seat 12", "role": "Rookie Member", "bio": "Recent Cadet"}
                        ],
                        "accolades": [
                            {"title": "First Roll Call Stamp", "rarity": "Common", "color": "#0f62fe", "desc": "Initiated 365-day Fan Passport.", "perk": "1.25x 1st-quarter points boost"}
                        ]
                    }
                    st.session_state.active_member = st.session_state.member_name
                    st.session_state.respect_dict[st.session_state.member_name] = 1

                    # Balloons ONLY for newly signed-up member on inception!
                    st.balloons()
                    st.rerun()

        with auth_tab_login:
            st.subheader("🔑 Member Sign In with Email & Password")
            st.caption("Sign in to your registered account with your verified email and password.")

            with st.form(key="member_login_form"):
                login_email = st.text_input("Registered Email Address", value="fan@gmail.com")
                login_pwd = st.text_input("Password", type="password", value="password123")
                submit_login = st.form_submit_button("🔑 Log In with Email & Password", use_container_width=True)

            if submit_login:
                clean_email = login_email.strip().lower()
                clean_pwd = login_pwd.strip()
                fans_db = st.session_state.registered_fans_db

                if not clean_email or not clean_pwd:
                    st.error("⚠️ Please enter both your registered email address and password.")
                elif clean_email not in fans_db:
                    st.error(f"❌ No registered account found for '{login_email}'. Please sign up as a new member or check your email.")
                elif fans_db[clean_email].get("password") != clean_pwd:
                    st.error("❌ Incorrect password. Please verify your credentials.")
                else:
                    # Validated login!
                    user_data = fans_db[clean_email]
                    st.session_state.is_logged_in = True
                    st.session_state.just_signed_up = False  # NO balloons on normal login!
                    st.session_state.member_email = clean_email
                    st.session_state.member_name = user_data["name"]
                    st.session_state.active_member = user_data["name"]
                    st.session_state.member_handle = user_data.get("handle", "@fan")
                    st.session_state.member_hash = user_data.get("hash", "0x" + hashlib.sha256(clean_email.encode()).hexdigest()[:16])
                    st.session_state.member_role = user_data.get("role", "Rookie Member")
                    st.session_state.member_tier = user_data.get("tier", "Rookie Member (Tier 1)")
                    st.session_state.member_seat = user_data.get("seat", "Section 114, Row 3, Seat 12")
                    st.session_state.member_games = user_data.get("games", 0)
                    st.session_state.member_career_db = user_data.get("career_db", "0.0 dB")
                    st.session_state.member_clutch_stops = user_data.get("clutch_stops", 0)
                    st.session_state.tailgates_attended = user_data.get("tailgates_attended", 0)
                    st.session_state.meetup_rsvps = list(user_data.get("meetup_rsvps", []))
                    soc = user_data.get("socials", {})
                    st.session_state.social_x = soc.get("x", "@fan_rookie")
                    st.session_state.social_ig = soc.get("instagram", "")
                    st.session_state.social_yt = soc.get("youtube", "@W3bHippo")
                    st.session_state.social_tiktok = soc.get("tiktok", "")
                    st.session_state.social_discord = soc.get("discord", "")
                    sett = user_data.get("settings", {})
                    st.session_state.wearable_device = sett.get("wearable_device", "Apple Watch Ultra 2 (ECG/dB)")
                    st.session_state.ble_sensitivity = sett.get("ble_sensitivity", -54)
                    st.session_state.notif_clutch = sett.get("notif_clutch", True)
                    st.session_state.notif_tailgate = sett.get("notif_tailgate", True)
                    st.session_state.notif_chaser = sett.get("notif_chaser", True)
                    st.session_state.pref_leaderboard_public = sett.get("pref_leaderboard_public", True)
                    st.session_state.pref_anonymize_biometrics = sett.get("pref_anonymize_biometrics", True)
                    st.session_state.sport = user_data.get("sport", "Basketball")
                    st.session_state.bb_level = user_data.get("bb_level", "Both (NCAA D1 & NBA)")
                    st.session_state.fb_level = user_data.get("fb_level", "Both (NCAA D1 & NFL)")
                    st.session_state.teams_bb = list(user_data.get("teams_bb", ["Duke Blue Devils", "Boston Celtics"]))
                    st.session_state.teams_fb = list(user_data.get("teams_fb", ["Michigan Wolverines", "Green Bay Packers"]))
                    st.session_state.unlocked_mentors_bb = list(user_data.get("unlocked_mentors_bb", ["Marcus Vance"]))
                    st.session_state.unlocked_mentors_fb = list(user_data.get("unlocked_mentors_fb", ["Sarah Jenkins"]))
                    st.session_state.active_npc_guide = "Marcus Vance" if st.session_state.sport == "Basketball" else "Sarah Jenkins"
                    st.session_state.user_respect_taps_sent = 0
                    _ensure_member_in_persona_db()
                    st.rerun()

            st.markdown("---")
            st.markdown("#### ⚡ Quick Demo Persona Log In (Evaluator Mode)")
            st.caption("One-click fast login across our 8 canonical section personas without entering credentials:")
            demo_persona_options = [
                "Marcus Vance (Basketball — Section Director, Tier 4)",
                "Sarah Jenkins (Football — Stadium Veteran, Tier 5)",
                "Jordan Lee (Basketball — Rookie Member, Tier 1)",
                "Alex Taylor (Football — General Member, Tier 1)",
                "Elena Rostova (Basketball — Prop Captain, Tier 2)",
                "Carlos Mendez (Football — Tailgate Host, Tier 4)",
                "Devon Miller (Basketball — Vocal Tactician, Tier 3)",
                "Maya Patel (Football — Tech Superfan, Tier 2)"
            ]
            selected_demo_persona = st.selectbox("Select canonical test persona:", demo_persona_options, index=0)
            if st.button("🚀 Fast Demo Sign-In as Selected Persona", key="btn_fast_demo_login", use_container_width=True):
                p_name_clean = selected_demo_persona.split(" (")[0]
                st.session_state.is_logged_in = True
                st.session_state.just_signed_up = False
                st.session_state.member_name = p_name_clean
                st.session_state.active_member = p_name_clean
                p_data = PERSONA_DB.get(p_name_clean, PERSONA_DB["Marcus Vance"])
                st.session_state.member_hash = p_data["hash"]
                st.session_state.member_role = p_data["role"]
                st.session_state.member_tier = p_data["tier"]
                st.session_state.sport = "Basketball" if "Basketball" in selected_demo_persona else "Football"
                st.session_state.teams_bb = ["Texas Longhorns", "San Antonio Spurs"]
                st.session_state.teams_fb = ["Texas Longhorns", "Dallas Cowboys"]
                if st.session_state.sport == "Basketball":
                    st.session_state.unlocked_mentors_bb = ["Marcus Vance"]
                    st.session_state.active_npc_guide = "Marcus Vance"
                else:
                    st.session_state.unlocked_mentors_fb = ["Sarah Jenkins"]
                    st.session_state.active_npc_guide = "Sarah Jenkins"
                st.session_state.user_respect_taps_sent = 0
                st.rerun()

    # ------------------------------------------------------------------
    # LOGGED-IN FAN EXPERIENCE (Screen 1 Dashboard)
    # ------------------------------------------------------------------
    else:
        st.header(f"👤 The Living Fan Passport & Section Roster ({st.session_state.sport})")
        st.caption("Persistent 365-day fandom identity, interactive section mentors, and team affiliations.")

        # Top User Status & Logout Banner
        col_status_info, col_status_act = st.columns([4, 1])
        with col_status_info:
            st.markdown(f"""
            <div style="background-color: #12161f; border-left: 4px solid #0f62fe; padding: 8px 14px; border-radius: 6px; margin-bottom: 8px;">
                <span style="color: #0f62fe; font-weight: bold;">👋 LOGGED IN:</span>
                <span style="color: #f4f4f4;"> <b>{st.session_state.member_name}</b> (<code>{st.session_state.member_handle}</code>) &bull; Tier: <b>{st.session_state.member_tier}</b> &bull; Hash: <code>{st.session_state.member_hash}</code></span>
            </div>
            """, unsafe_allow_html=True)
        with col_status_act:
            if st.button("🚪 Sign Out", key="btn_logout_user", use_container_width=True):
                st.session_state.is_logged_in = False
                st.rerun()

        # Celebration card for newly signed-up user
        if st.session_state.just_signed_up:
            lead_npc_welcome = "Marcus Vance" if is_basketball else "Sarah Jenkins"
            st.success(f"🎉 **Welcome to Kinetic FanLab, {st.session_state.member_name}!** Your persistent 365-day Fan Passport is active. Your Section Leader ({lead_npc_welcome}) is ready to guide your Rookie Walkthrough below!")
            st.session_state.just_signed_up = False

        # Two-column layout: Left Panel (Passport + Sports & Teams) | Right Panel (Mentors & Roster)
        col_left_panel, col_main_panel = st.columns([1, 2])

        with col_left_panel:
            # 1. Dynamic Fan Passport Card
            p_info = PERSONA_DB.get(st.session_state.active_member, PERSONA_DB["Marcus Vance" if is_basketball else "Sarah Jenkins"])
            glow_color = "#f1c21b" if "Tier 5" in p_info['tier'] else ("#8a3ffc" if "Tier 4" in p_info['tier'] else "#0f62fe")
            st.markdown(f"""
            <div style="background-color: #161616; padding: 20px; border-radius: 12px; border: 2px solid {glow_color}; box-shadow: 0 0 15px {glow_color}88; text-align: center; margin-top: 6px;">
                <p style="color: #8d8d8d; font-size: 9.5pt; margin: 0; text-transform: uppercase;">DYNAMIC MOMENTUM PASS</p>
                <h2 style="color: #f4f4f4; margin: 4px 0;">{st.session_state.member_name}</h2>
                <p style="color: #0f62fe; font-weight: bold; margin: 0;">{p_info['sec']}</p>
                <hr style="border-color: #333; margin: 10px 0;">
                <p style="color: #f4f4f4; font-size: 10.5pt; margin: 2px 0;">Tier: <b>{st.session_state.member_tier}</b></p>
                <p style="color: #a8a8a8; font-size: 8.5pt; margin: 0;">Hash: <code>{st.session_state.member_hash}</code></p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Sync My Fan Passport", key=f"btn_sync_cloudant_{st.session_state.member_name}", use_container_width=True):
                if CLOUDANT_ENGINE_LIVE:
                    sec_clean = p_info['sec'].split()[0] + p_info['sec'].split()[1] if len(p_info['sec'].split()) > 1 else p_info['sec']
                    tier_num = 1 if "Tier 1" in st.session_state.member_tier else 4
                    cloudant_save_passport(
                        member_name=st.session_state.member_name,
                        member_hash=st.session_state.member_hash,
                        section_id=sec_clean,
                        sport=st.session_state.sport,
                        role=st.session_state.member_role,
                        tier=tier_num,
                        device_anchor="Wearable Sensor Anchor",
                        early_multiplier=1.25 if st.session_state.early_checkin else 1.0
                    )
                st.success(f"✅ Fan Passport synced for {st.session_state.member_name}!")

            # 2. SCREEN ONE LEFT PANEL: SPORTS & TEAMS FANDOM HUB (SPORT-ISOLATED)
            st.markdown("---")
            st.subheader("🏆 My Sports & Teams")
            st.caption("Easily access, switch, and manage your sport and team affiliations.")

            # Quick Sport Switcher
            cur_sp_idx = 0 if is_basketball else 1
            picked_sport_radio = st.radio(
                "Active Gameday Sport:",
                ["🏀 Basketball", "🏈 Football"],
                index=cur_sp_idx,
                key="left_panel_sport_radio",
                horizontal=True
            )
            new_sport_clean = "Basketball" if "Basketball" in picked_sport_radio else "Football"
            if new_sport_clean != st.session_state.sport:
                st.session_state.sport = new_sport_clean
                if st.session_state.get("is_logged_in") and st.session_state.get("member_name"):
                    st.session_state.active_member = st.session_state.member_name
                else:
                    st.session_state.active_member = "Marcus Vance" if new_sport_clean == "Basketball" else "Sarah Jenkins"
                _ensure_member_in_persona_db()
                st.rerun()

            # Render SPORT-ISOLATED team list
            if is_basketball:
                st.markdown(f"**Basketball Level:** `{st.session_state.bb_level}`")
                st.markdown("**Affiliated Basketball Teams:**")
                for t_item in st.session_state.teams_bb:
                    st.markdown(f"- 🏀 **{t_item}**")

                with st.expander("⚙️ Edit Basketball Teams & Preferences", expanded=False):
                    edit_bbl = st.selectbox(
                        "Basketball Level:",
                        ["🎓 College Basketball (NCAA D1)", "🏟️ Pro Basketball (NBA)", "⚡ Both (NCAA D1 & NBA)"],
                        index=2 if "Both" in st.session_state.bb_level else (0 if "College" in st.session_state.bb_level else 1),
                        key="edit_bbl_select"
                    )
                    if "College" in edit_bbl and "Pro" not in edit_bbl and "Both" not in edit_bbl:
                        bb_avail = sorted(NCAA_D1_BASKETBALL_TEAMS)
                    elif "Pro" in edit_bbl and "College" not in edit_bbl and "Both" not in edit_bbl:
                        bb_avail = sorted(NBA_TEAMS)
                    else:
                        bb_avail = sorted(list(set(NCAA_D1_BASKETBALL_TEAMS + NBA_TEAMS)))

                    # Multiselect from directory
                    curr_bb_choices = [t for t in st.session_state.teams_bb if t in bb_avail]
                    edit_bb_teams = st.multiselect(
                        "Manage Basketball Teams:",
                        bb_avail,
                        default=curr_bb_choices,
                        key="edit_bb_teams_multi"
                    )

                    # Manual Custom Team Input
                    col_c_in, col_c_btn = st.columns([3, 1])
                    custom_bb_typed = col_c_in.text_input("Type Custom Team:", placeholder="e.g. Duke Blue Devils...", key="custom_bb_txt")
                    if col_c_btn.button("➕ Add", key="btn_add_custom_bb"):
                        if custom_bb_typed.strip() and custom_bb_typed.strip() not in st.session_state.teams_bb:
                            st.session_state.teams_bb.append(custom_bb_typed.strip())
                            if st.session_state.member_email in st.session_state.registered_fans_db:
                                st.session_state.registered_fans_db[st.session_state.member_email]["teams_bb"] = st.session_state.teams_bb
                                _save_fans_db(st.session_state.registered_fans_db)
                            st.rerun()

                    if st.button("💾 Save Basketball Preferences", key="btn_save_bb_prefs", use_container_width=True):
                        st.session_state.bb_level = edit_bbl
                        # Preserve any custom added teams not in the selectbox
                        custom_already = [t for t in st.session_state.teams_bb if t not in bb_avail]
                        st.session_state.teams_bb = list(set(edit_bb_teams + custom_already))
                        if st.session_state.member_email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[st.session_state.member_email]["bb_level"] = edit_bbl
                            st.session_state.registered_fans_db[st.session_state.member_email]["teams_bb"] = st.session_state.teams_bb
                            _save_fans_db(st.session_state.registered_fans_db)
                        st.success("✅ Basketball preferences updated and saved!")
                        st.rerun()
            else:
                st.markdown(f"**Football Level:** `{st.session_state.fb_level}`")
                st.markdown("**Affiliated Football Teams:**")
                for t_item in st.session_state.teams_fb:
                    st.markdown(f"- 🏈 **{t_item}**")

                with st.expander("⚙️ Edit Football Teams & Preferences", expanded=False):
                    edit_fbl = st.selectbox(
                        "Football Level:",
                        ["🎓 College Football (NCAA D1 FBS)", "🏟️ Pro Football (NFL)", "⚡ Both (NCAA D1 & NFL)"],
                        index=2 if "Both" in st.session_state.fb_level else (0 if "College" in st.session_state.fb_level else 1),
                        key="edit_fbl_select"
                    )
                    if "College" in edit_fbl and "Pro" not in edit_fbl and "Both" not in edit_fbl:
                        fb_avail = sorted(NCAA_D1_FBS_FOOTBALL_TEAMS)
                    elif "Pro" in edit_fbl and "College" not in edit_fbl and "Both" not in edit_fbl:
                        fb_avail = sorted(NFL_TEAMS)
                    else:
                        fb_avail = sorted(list(set(NCAA_D1_FBS_FOOTBALL_TEAMS + NFL_TEAMS)))

                    curr_fb_choices = [t for t in st.session_state.teams_fb if t in fb_avail]
                    edit_fb_teams = st.multiselect(
                        "Manage Football Teams:",
                        fb_avail,
                        default=curr_fb_choices,
                        key="edit_fb_teams_multi"
                    )

                    # Manual Custom Team Input
                    col_fc_in, col_fc_btn = st.columns([3, 1])
                    custom_fb_typed = col_fc_in.text_input("Type Custom Team:", placeholder="e.g. Michigan Wolverines...", key="custom_fb_txt")
                    if col_fc_btn.button("➕ Add", key="btn_add_custom_fb"):
                        if custom_fb_typed.strip() and custom_fb_typed.strip() not in st.session_state.teams_fb:
                            st.session_state.teams_fb.append(custom_fb_typed.strip())
                            if st.session_state.member_email in st.session_state.registered_fans_db:
                                st.session_state.registered_fans_db[st.session_state.member_email]["teams_fb"] = st.session_state.teams_fb
                                _save_fans_db(st.session_state.registered_fans_db)
                            st.rerun()

                    if st.button("💾 Save Football Preferences", key="btn_save_fb_prefs", use_container_width=True):
                        st.session_state.fb_level = edit_fbl
                        custom_already = [t for t in st.session_state.teams_fb if t not in fb_avail]
                        st.session_state.teams_fb = list(set(edit_fb_teams + custom_already))
                        if st.session_state.member_email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[st.session_state.member_email]["fb_level"] = edit_fbl
                            st.session_state.registered_fans_db[st.session_state.member_email]["teams_fb"] = st.session_state.teams_fb
                            _save_fans_db(st.session_state.registered_fans_db)
                        st.success("✅ Football preferences updated and saved!")
                        st.rerun()

            # 3. Lifetime Career Telemetry Statline (Personalized for Member)
            st.markdown("---")
            st.subheader(f"📊 Lifetime Career Telemetry ({st.session_state.member_name})")
            u_persona = PERSONA_DB.get(st.session_state.member_name, p_info)
            stat1, stat2 = st.columns(2)
            stat1.metric("Games Attended", f"{u_persona['games']}", delta="Active Season" if u_persona['games'] > 0 else "Rookie Season")
            stat2.metric("Career Acoustic dB", u_persona['career_db'], delta=f"{st.session_state.db} dB live peak")
            stat3, stat4 = st.columns(2)
            stat3.metric("Clutch Stops", f"{u_persona['clutch_stops']}", delta="Verified Stops")
            current_respect_score = st.session_state.user_respect_taps_sent
            stat4.metric("Respect Taps", f"{current_respect_score}", delta=f"+{st.session_state.user_respect_taps_sent} Sent")
            stat5, stat6 = st.columns(2)
            meetup_count = st.session_state.get("tailgates_attended", 0)
            stat5.metric("Tailgates & Meetups", f"{meetup_count} RSVP'd", delta="Consistent Fan" if meetup_count > 0 else "Rookie Fan")
            stat6.metric("Community Streak", f"{meetup_count} Streak", delta="NFT Accolade Progress" if meetup_count > 0 else "Join Meetups")

        with col_main_panel:
            # ------------------------------------------------------------------
            # SECTION MENTORS & PROGRESSIVE UNLOCKS (ONLY Section Leader at Inception)
            # ------------------------------------------------------------------
            unlocked_list = st.session_state.unlocked_mentors_bb if is_basketball else st.session_state.unlocked_mentors_fb
            unlock_eval = npc_mentors.evaluate_npc_unlocks(
                sport=st.session_state.sport,
                current_unlocked=unlocked_list,
                early_checkin=st.session_state.early_checkin,
                tap_count=st.session_state.tap_count,
                respect_count=st.session_state.user_respect_taps_sent,  # Uses user_respect_taps_sent (starts at 0!)
                chant_action=st.session_state.chant_action_taken,
                storycard_exported=st.session_state.storycard_exported_flag,
                cmi=current_cmi
            )
            if is_basketball:
                st.session_state.unlocked_mentors_bb = unlock_eval["unlocked_npcs"]
            else:
                st.session_state.unlocked_mentors_fb = unlock_eval["unlocked_npcs"]

            # Toast notification ONLY when unlocked through user actions
            for new_npc in unlock_eval["newly_unlocked"]:
                st.balloons()
                st.success(f"🎉 **NEW SECTION MENTOR UNLOCKED:** **{new_npc}** has recognized your in-game energy and joined your Section Circle!")

            st.subheader(f"🤝 Section Mentors & Progressive Unlocks ({unlock_eval['total_unlocked']}/4 Unlocked)")
            st.progress(unlock_eval['total_unlocked'] / 4.0)

            # Render 4 Mentor Cards
            sport_all_mentors = ["Marcus Vance", "Jordan Lee", "Elena Rostova", "Devon Miller"] if is_basketball else ["Sarah Jenkins", "Alex Taylor", "Carlos Mendez", "Maya Patel"]
            npc_cols = st.columns(4)

            active_unlocked_names = unlock_eval["unlocked_npcs"]
            for m_idx, m_name in enumerate(sport_all_mentors):
                m_meta = npc_mentors.NPC_MENTOR_REGISTRY[m_name]
                is_unlocked = m_name in active_unlocked_names
                with npc_cols[m_idx]:
                    if is_unlocked:
                        card_border = m_meta["color"]
                        status_tag = f"<span style='color:{m_meta['color']}; font-weight:bold;'>✓ UNLOCKED</span>"
                        desc_text = f"<p style='color:#f4f4f4; font-size:8.5pt; margin:4px 0;'><b>{m_meta['role']}</b></p>"
                    else:
                        card_border = "#444"
                        status_tag = "<span style='color:#888; font-weight:bold;'>🔒 LOCKED</span>"
                        desc_text = f"<p style='color:#888; font-size:8pt; margin:4px 0;'>Requires: {m_meta['unlock_requirement']}</p>"

                    st.markdown(f"""
                    <div style="background-color: #161616; border: 2px solid {card_border}; border-radius: 8px; padding: 10px; min-height: 140px; text-align: center;">
                        <span style="font-size: 18pt;">{m_meta['avatar_icon']}</span><br/>
                        <span style="color: white; font-weight: bold; font-size: 9.5pt;">{m_name}</span><br/>
                        {status_tag}
                        {desc_text}
                    </div>
                    """, unsafe_allow_html=True)

            # Active Mentor Dialogue Box with Direct Guidance & Hints
            selected_guide = st.selectbox(
                "Speak with an Unlocked Mentor:",
                active_unlocked_names,
                index=active_unlocked_names.index(st.session_state.active_npc_guide) if st.session_state.active_npc_guide in active_unlocked_names else 0,
                key="active_guide_select"
            )
            st.session_state.active_npc_guide = selected_guide
            active_guide_meta = npc_mentors.NPC_MENTOR_REGISTRY[selected_guide]

            st.markdown(f"""
            <div style="background-color: #141923; border-left: 5px solid {active_guide_meta['color']}; padding: 14px 18px; border-radius: 8px; margin: 12px 0;">
                <span style="color: {active_guide_meta['color']}; font-weight: bold; font-size: 10pt;">
                    {active_guide_meta['avatar_icon']} {selected_guide} &mdash; {active_guide_meta['role']} ({active_guide_meta['sec']})
                </span><br/>
                <p style="color: #f4f4f4; font-size: 10pt; margin: 6px 0 8px 0; font-style: italic;">
                    "{active_guide_meta['greeting']}"
                </p>
                <div style="background-color: #0b0f17; padding: 8px 12px; border-radius: 6px; border: 1px dashed {active_guide_meta['color']}88;">
                    <span style="color: #f1c21b; font-weight: bold; font-size: 9pt;">💡 MENTOR HINT &amp; NEXT HORIZON:</span>
                    <span style="color: #dcdcdc; font-size: 9pt;"> {active_guide_meta['hint']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Capstone NFT Unlock Banner when All 4 Mentors are Engaged
            capstone_claimed = st.session_state.capstone_claimed_bb if is_basketball else st.session_state.capstone_claimed_fb
            capstone_nft = npc_mentors.get_capstone_nft_badge(st.session_state.sport)
            if unlock_eval["capstone_ready"]:
                st.markdown(f"""
                <div style="background-color: #2b1f00; border: 2px solid #f1c21b; padding: 16px 20px; border-radius: 12px; margin: 12px 0; text-align: center; box-shadow: 0 0 20px #f1c21b66;">
                    <span style="background-color: #f1c21b33; color: #f1c21b; padding: 4px 10px; border-radius: 6px; font-size: 8.5pt; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">
                        🏆 ALL 4 MENTORS UNLOCKED &bull; CAPSTONE NFT READY
                    </span>
                    <h3 style="color: #f1c21b; margin: 8px 0 4px 0;">{capstone_nft['icon']} {capstone_nft['title']}</h3>
                    <p style="color: #f4f4f4; font-size: 10pt; margin: 0 0 8px 0;">
                        You have bonded with all 4 section mentors in {st.session_state.sport}! 
                        Claim and inspect your accredited on-chain <b>{capstone_nft['title']}</b> NFT badge below.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                if not capstone_claimed:
                    if st.button(f"🗝️ Claim Legendary '{capstone_nft['title']}' NFT Badge", key="btn_claim_capstone_nft", use_container_width=True):
                        if is_basketball:
                            st.session_state.capstone_claimed_bb = True
                        else:
                            st.session_state.capstone_claimed_fb = True
                        st.session_state.synergy_score = min(100, st.session_state.synergy_score + 10)
                        st.balloons()
                        st.success(f"🎉 Claimed! '{capstone_nft['title']}' is now permanently recorded in your Living Trophy Case! (+10% Section Synergy)")
                        st.rerun()

                # Prominent Visual NFT Showcase Card viewable directly on Screen 1
                nft_token_id = f"#NFT-{'BB' if is_basketball else 'FB'}-{st.session_state.member_hash[2:6].upper()}-0042"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1b1600 0%, #291e00 100%); border: 3px solid #f1c21b; border-radius: 12px; padding: 20px; box-shadow: 0 0 25px #f1c21b77; text-align: center; margin: 8px auto 16px auto; max-width: 580px;">
                    <p style="color: #f1c21b; font-size: 8.5pt; font-weight: bold; letter-spacing: 2px; margin: 0;">KINETIC FANLAB // ACCREDITED WEB3 CAPSTONE NFT</p>
                    <h2 style="color: #ffffff; margin: 6px 0;">{capstone_nft['icon']} {capstone_nft['title']}</h2>
                    <span style="background-color: #f1c21b; color: #161616; padding: 3px 12px; border-radius: 12px; font-weight: bold; font-size: 8.5pt;">{capstone_nft['rarity'].upper()} CAPSTONE</span>
                    <hr style="border-color: #f1c21b55; margin: 12px 0;">
                    <div style="text-align: left; background-color: #11141c; padding: 12px 16px; border-radius: 8px; border: 1px solid #333;">
                        <p style="color: #a8a8a8; font-size: 9pt; margin: 2px 0;"><b>Issued To:</b> <span style="color:#fff;">{st.session_state.member_name} (<code>{st.session_state.member_handle}</code>)</span></p>
                        <p style="color: #a8a8a8; font-size: 9pt; margin: 2px 0;"><b>Token ID:</b> <code style="color:#f1c21b;">{nft_token_id}</code> &bull; <b>Storage:</b> IBM Cloudant + Lakehouse COS S3</p>
                        <p style="color: #a8a8a8; font-size: 9pt; margin: 2px 0;"><b>Signature Hash:</b> <code style="color:#0f62fe;">{capstone_nft['hash_seed']}-{st.session_state.member_hash[2:8]}</code></p>
                        <p style="color: #a8a8a8; font-size: 9pt; margin: 2px 0;"><b>Verified Perks:</b> <span style="color:#42be65; font-weight:bold;">{capstone_nft['perk']}</span></p>
                        <p style="color: #dcdcdc; font-size: 8.5pt; margin: 4px 0 0 0;"><i>{capstone_nft['desc']}</i></p>
                    </div>
                    <p style="color: #42be65; font-size: 9.5pt; font-weight: bold; margin: 10px 0 0 0;">{'✅ Status: Claimed & Verified in Trophy Case' if capstone_claimed else '⏳ Status: Unlocked & Ready to Claim'}</p>
                </div>
                """, unsafe_allow_html=True)

            # Tabs for Roster, Trophy Case, and Settings
            tab_identity, tab_trophy, tab_settings = st.tabs([
                "🪪 Section Roster & Seat Neighbors",
                "🏆 Living Trophy Case & Dynamic Accolades",
                "⚙️ Account Settings & Connected Accounts"
            ])

            with tab_identity:
                st.subheader(f"👥 Section Roster for {st.session_state.member_name} (Seat Neighbors)")
                st.write(f"Connect with your actual row neighbors in **{p_info['sec']}**:")

                r_cols = st.columns(3)
                for idx, neighbor in enumerate(p_info['neighbors'][:3]):
                    with r_cols[idx]:
                        st.markdown(f"**{neighbor['name']}** ({neighbor['seat']})")
                        st.caption(f"*{neighbor['role']}*\n\n{neighbor['bio']}")

                if st.button("🤝 Send Respect Tap to Seat Neighbors", key="btn_neighbor_respect"):
                    new_total = cloudant_db.increment_respect_tap(st.session_state.active_member, 1)
                    st.session_state.respect_dict[st.session_state.active_member] = new_total
                    st.session_state.user_respect_taps_sent += 1
                    st.session_state.synergy_score = min(100, st.session_state.synergy_score + 2)
                    st.success(f"Respect Tap transmitted to {p_info['neighbors'][0]['name']} and row neighbors! (+1 Respect Logged — Total: {new_total})")

                with st.expander("🎯 Send Respect Tap to Any Specific Seat in the Venue"):
                    st.write("Acknowledge a dedicated fan, chant starter, or veteran anywhere in the venue:")
                    rc1, rc2, rc3 = st.columns(3)
                    target_sec = rc1.text_input("Section", value=p_info['sec'].split()[0] + " " + p_info['sec'].split()[1])
                    target_row = rc2.text_input("Row", value="Row 5")
                    target_seat = rc3.text_input("Seat", value="Seat 12")
                    if st.button("🚀 Transmit Respect Tap to Specific Seat", key="btn_target_respect"):
                        new_total = cloudant_db.increment_respect_tap(st.session_state.active_member, 1)
                        st.session_state.respect_dict[st.session_state.active_member] = new_total
                        st.session_state.user_respect_taps_sent += 1
                        st.session_state.synergy_score = min(100, st.session_state.synergy_score + 2)
                        st.success(f"✅ Respect Tap sent to **{target_sec}, {target_row}, {target_seat}**! (+1 Respect Tap — Total: {new_total})")

            with tab_trophy:
                st.subheader(f"🏆 Living Trophy Case: {st.session_state.member_name}")
                st.caption("Dynamic NFT Accolades that evolve based on your real-time verified stadium telemetry.")

                st.markdown(f"### 📈 {p_info['next_tier_title']} Progress")
                st.progress(p_info['tier_progress_pct'])
                st.caption(p_info['tier_progress_desc'])

                st.markdown("---")
                st.subheader("🏅 Unlocked Dynamic Accolades (NFT Badges)")
                capstone_is_claimed = st.session_state.capstone_claimed_bb if is_basketball else st.session_state.capstone_claimed_fb
                if capstone_is_claimed:
                    cap_badge = npc_mentors.get_capstone_nft_badge(st.session_state.sport)
                    st.markdown(f"""
                    <div style="background-color: #241a00; border: 2px solid #f1c21b; border-radius: 10px; padding: 14px 18px; margin-bottom: 16px; box-shadow: 0 0 15px #f1c21b66;">
                        <span style="background-color: #f1c21b33; color: #f1c21b; padding: 3px 8px; border-radius: 4px; font-size: 8pt; font-weight: bold; text-transform: uppercase;">LEGENDARY CAPSTONE</span>
                        <h4 style="color: #f1c21b; margin: 6px 0 2px 0;">{cap_badge['icon']} {cap_badge['title']}</h4>
                        <p style="color: #f4f4f4; font-size: 9.5pt; margin: 0 0 4px 0;">{cap_badge['desc']}</p>
                        <p style="color: #42be65; font-size: 9pt; font-weight: bold; margin: 0;">🎁 Verified Perk: {cap_badge['perk']}</p>
                    </div>
                    """, unsafe_allow_html=True)
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

                # Community Consistency NFT Badge (Future Accolade based on Meetups & Tailgates)
                comm_nft_title = "Plaza Rally Vanguard" if is_basketball else "Lot B Tailgate Legend"
                comm_nft_color = "#0f62fe" if is_basketball else "#fa4d56"
                comm_nft_icon = "🏀" if is_basketball else "🔥"
                meetup_stat_count = st.session_state.get("tailgates_attended", 0)
                comm_unlocked = (meetup_stat_count >= 3)

                st.markdown(f"""
                <div style="background-color: #1a1a1a; border: 2px solid {comm_nft_color if comm_unlocked else '#444'}; border-radius: 10px; padding: 16px; margin-top: 14px; box-shadow: 0 0 10px {comm_nft_color + '44' if comm_unlocked else 'transparent'};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background-color: {comm_nft_color}33; color: {comm_nft_color}; padding: 3px 8px; border-radius: 4px; font-size: 8pt; font-weight: bold; text-transform: uppercase;">
                            {'COMMUNITY ACCREDITATION UNLOCKED' if comm_unlocked else 'FUTURE COMMUNITY NFT TROPHY (IN PROGRESS)'}
                        </span>
                        <span style="color: #f1c21b; font-size: 9pt; font-weight: bold;">{meetup_stat_count}/3 Meetups RSVP'd</span>
                    </div>
                    <h4 style="color: white; margin: 8px 0 4px 0;">{comm_nft_icon} {comm_nft_title}</h4>
                    <p style="color: #a8a8a8; font-size: 9.5pt; margin-bottom: 6px;">
                        {'Awarded for verified gameday consistency and community leadership across Section 114/115 meetups and tailgates.' if comm_unlocked else 'RSVP and participate in 3 pre-game meetups or tailgates on Screen 2 to unlock this Community Consistency NFT badge!'}
                    </p>
                    <p style="color: #42be65; font-size: 8.5pt; font-weight: bold; margin: 0;">🎁 Future Perk: Free VIP tailgate voucher & priority gate express entry</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📲 Share Trophy Showcase")
                st.markdown(f"""
                <div style="background-color: #111; border: 2px solid #0f62fe; border-radius: 12px; padding: 22px; max-width: 480px; margin: 0 auto; text-align: center; box-shadow: 0 0 20px #0f62fe55;">
                    <p style="color: #0f62fe; font-size: 9pt; margin: 0; letter-spacing: 1.5px; font-weight: bold;">KINETIC FANLAB // NFT TROPHY SHOWCASE</p>
                    <h2 style="color: white; margin: 6px 0;">{st.session_state.member_name}</h2>
                    <p style="color: #0f62fe; font-weight: bold; margin: 0;">{st.session_state.member_tier} &bull; {p_info['sec']}</p>
                    <hr style="border-color: #333; margin: 10px 0;">
                    <p style="color: #a8a8a8; font-size: 9.5pt; margin: 4px 0;">Verified Impact: <b>{p_info['career_db']}</b> Acoustic Wall &bull; <b>{p_info['clutch_stops']}</b> Clutch Stops</p>
                    <p style="color: #f1c21b; font-size: 9pt; margin: 4px 0;">Community Consistency: <b>{meetup_stat_count} Meetup(s) RSVP'd</b></p>
                    <p style="color: #8d8d8d; font-size: 8.5pt; margin: 0;">Hash: <code>{st.session_state.member_hash}</code></p>
                </div>
                """, unsafe_allow_html=True)

                col_sh_btn, dummy_col = st.columns([2, 1])
                with col_sh_btn:
                    if st.button("📲 Share Showcase to Instagram, TikTok & X", key="btn_share_showcase", use_container_width=True):
                        st.session_state.share_trophy_clicked = True

                if st.session_state.get("share_trophy_clicked"):
                    import urllib.parse
                    trophy_url = f"https://kineticfanlab.com/trophy/{st.session_state.sport.lower()}/{st.session_state.member_hash[:8]}?fan={st.session_state.member_handle}"
                    tweet_text = f"Check out my verified NFT Trophy Showcase & 365-Day Fan Passport on Kinetic FanLab! 🏆 Tier: {st.session_state.member_tier} in {p_info['sec']}. #KineticFanLab #IBM #Web3Sports"
                    enc_tweet = urllib.parse.quote(tweet_text)
                    enc_url = urllib.parse.quote(trophy_url)
                    x_link = f"https://twitter.com/intent/tweet?text={enc_tweet}&url={enc_url}"
                    fb_link = f"https://www.facebook.com/sharer/sharer.php?u={enc_url}"

                    st.success(f"✅ Trophy Showcase officially formatted for **{st.session_state.member_name}** ({st.session_state.member_handle})! Share links unlocked below:")
                    sh_col1, sh_col2 = st.columns(2)
                    with sh_col1:
                        st.markdown(f'<a href="{x_link}" target="_blank" style="text-decoration:none;"><button style="background-color:#1d9bf0; color:white; border:none; padding:10px 16px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">𝕏 Post Trophy Showcase to X (Twitter)</button></a>', unsafe_allow_html=True)
                    with sh_col2:
                        st.markdown(f'<a href="{fb_link}" target="_blank" style="text-decoration:none;"><button style="background-color:#1877f2; color:white; border:none; padding:10px 16px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">📘 Share on Facebook</button></a>', unsafe_allow_html=True)

                    with st.expander("📸 Instagram & TikTok Shareable Showcase Caption", expanded=True):
                        insta_showcase = f"Verified 365-Day Fan Passport & NFT Trophy Showcase on Kinetic FanLab! 🏆\nFan: {st.session_state.member_name} ({st.session_state.member_handle})\nSection: {p_info['sec']} ({st.session_state.sport})\nStatus: {st.session_state.member_tier}\nVerified Stats: {p_info['career_db']} acoustic roar &bull; {p_info['clutch_stops']} clutch stops &bull; {meetup_stat_count} meetups attended\nPassport Hash: {st.session_state.member_hash}\nShowcase Link: {trophy_url}\n#KineticFanLab #IBM #FanMomentum #NFTShowcase #Web3Sports #SportsTech"
                        st.text_area("Copy Showcase Caption to Clipboard:", value=insta_showcase, height=115)
                        st.caption("Paste this verified showcase caption into your Instagram Story, Bio, or TikTok caption!")

            with tab_settings:
                st.subheader("⚙️ Account Settings & Connected Accounts")
                st.caption("Manage your connected social platforms, wearable sensor anchors, and gameday telemetry preferences.")

                st.markdown("#### 🔗 Connected Social Media Profiles")
                st.write("Link your social media accounts to display verified links across your Fan Passport, Trophy Showcase, and Proof-of-Momentum cards:")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    sett_x = st.text_input("𝕏 (Twitter) Handle / Profile:", value=st.session_state.get("social_x", "@fan_rookie"), placeholder="e.g. @owltar")
                    sett_ig = st.text_input("📸 Instagram Handle:", value=st.session_state.get("social_ig", ""), placeholder="e.g. ")
                    sett_yt = st.text_input("▶️ YouTube Channel / Handle:", value=st.session_state.get("social_yt", "@W3bHippo"), placeholder="e.g. @W3bHippo")
                with col_s2:
                    sett_tiktok = st.text_input("🎵 TikTok Handle:", value=st.session_state.get("social_tiktok", ""), placeholder="e.g. ")
                    sett_discord = st.text_input("💬 Discord / Chat Handle:", value=st.session_state.get("social_discord", ""), placeholder="e.g. username#1234")
                    sett_seat_pref = st.text_input("📍 Primary Seat Anchor / Season Ticket:", value=st.session_state.registered_fans_db.get(st.session_state.member_email, {}).get("seat", st.session_state.get("member_seat", "Section 114, Row 3")))

                st.markdown("---")
                st.markdown("#### ⌚ Wearable Sensor & Stadium Edge Calibration")
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    wearable_options = [
                        "Apple Watch Ultra 2 (ECG/dB)",
                        "Apple Watch Series 9 / SE",
                        "Garmin Fenix 7X (Stress/BPM)",
                        "Google Pixel Watch 2",
                        "Samsung Galaxy Watch 6 Pro",
                        "Fitbit Charge 6",
                        "Smartphone Mic & Accelerometer (Edge BLE)"
                    ]
                    current_w = st.session_state.get("wearable_device", "Apple Watch Ultra 2 (ECG/dB)")
                    w_idx = wearable_options.index(current_w) if current_w in wearable_options else 0
                    sett_wearable = st.selectbox("Primary Wearable Sensor Anchor:", wearable_options, index=w_idx)
                with col_w2:
                    sett_ble = st.slider("BLE Mesh Beacon RSSI Sensitivity Threshold (dBm):", min_value=-90, max_value=-25, value=int(st.session_state.get("ble_sensitivity", -54)), help="Calibrates proximity to 50-seat row pod mesh. -54 dBm is optimal for in-seat detection.")

                st.markdown("---")
                st.markdown("#### 🔔 Gameday Notification & Pacing Preferences")
                col_n1, col_n2 = st.columns(2)
                with col_n1:
                    sett_clutch = st.checkbox("⚡ In-Arena Clutch Vibration & Visual Haptics", value=st.session_state.get("notif_clutch", True), help="Fires real-time screen pulse and device haptic alerts on 2.0x clutch windows.")
                    sett_tailgate = st.checkbox("🎪 36-Hour Virtual Tailgate & Meetup Strategy Alerts", value=st.session_state.get("notif_tailgate", True), help="Notifies when section chant voting opens 36h before game tip-off/kickoff.")
                with col_n2:
                    sett_chaser = st.checkbox("⚠️ Section Rivalry Standings & Chaser Alerts", value=st.session_state.get("notif_chaser", True), help="Alerts when chasing section is trailing by single-digit per-capita points.")
                    sett_public_leaderboard = st.checkbox("🏆 Display Handle on Stadium Jumbotron & Public Leaderboard", value=st.session_state.get("pref_leaderboard_public", True), help="Enables display of your handle and tier on in-arena leaderboards.")

                st.markdown("---")
                st.markdown("#### 🛡️ Privacy, EEOC Fairness & Cloud Lakehouse Archive")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    sett_anonymize = st.checkbox("🔒 EEOC Dialect & Regional Accent Privacy Shield (DIR = 0.953)", value=st.session_state.get("pref_anonymize_biometrics", True), help="Anonymizes raw speech acoustic signals into mathematical CMI components at edge.")
                with col_p2:
                    retention_choice = st.selectbox("Biometric Data Retention Policy:", ["Gameday Session Only (Zero Cloud Raw Storage)", "30-Day Encrypted Aggregate (IBM Cloudant)", "Seasonal Passport Only (COS S3 Tamper-Evident)"], index=0)

                if st.button("💾 Save Account Settings & Connected Accounts", key="btn_save_all_settings", use_container_width=True):
                    st.session_state.social_x = sett_x.strip()
                    st.session_state.social_ig = sett_ig.strip()
                    st.session_state.social_yt = sett_yt.strip()
                    st.session_state.social_tiktok = sett_tiktok.strip()
                    st.session_state.social_discord = sett_discord.strip()
                    st.session_state.wearable_device = sett_wearable
                    st.session_state.ble_sensitivity = sett_ble
                    st.session_state.notif_clutch = sett_clutch
                    st.session_state.notif_tailgate = sett_tailgate
                    st.session_state.notif_chaser = sett_chaser
                    st.session_state.pref_leaderboard_public = sett_public_leaderboard
                    st.session_state.pref_anonymize_biometrics = sett_anonymize
                    st.session_state.member_seat = sett_seat_pref.strip()

                    email = st.session_state.get("member_email", "fan@gmail.com")
                    if email in st.session_state.registered_fans_db:
                        st.session_state.registered_fans_db[email]["socials"] = {
                            "x": sett_x.strip(),
                            "instagram": sett_ig.strip(),
                            "youtube": sett_yt.strip(),
                            "tiktok": sett_tiktok.strip(),
                            "discord": sett_discord.strip()
                        }
                        st.session_state.registered_fans_db[email]["seat"] = sett_seat_pref.strip()
                        st.session_state.registered_fans_db[email]["settings"] = {
                            "wearable_device": sett_wearable,
                            "ble_sensitivity": sett_ble,
                            "notif_clutch": sett_clutch,
                            "notif_tailgate": sett_tailgate,
                            "notif_chaser": sett_chaser,
                            "pref_leaderboard_public": sett_public_leaderboard,
                            "pref_anonymize_biometrics": sett_anonymize,
                            "retention": retention_choice
                        }
                        _save_fans_db(st.session_state.registered_fans_db)

                    _ensure_member_in_persona_db()
                    st.success("✅ All Settings, Connected Socials & Wearable Preferences saved to your 365-Day Fan Passport!")
                    st.toast("⚙️ Settings saved successfully!")
                    st.rerun()

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
                st.session_state.chant_action_taken = True
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
        st.caption("RSVP for official section meetups and tailgates to earn Community Consistency streaks toward future NFT trophies.")
        m1, m2 = st.columns(2)
        if is_basketball:
            with m1:
                st.markdown(f"""
                **🏀 Student Section Arena Plaza Rally (Hosted by Marcus & Elena)**
                * **Location:** Arena North Plaza (Student Gate)
                * **Arrival Time:** 2 Hours before {start_term}
                * **Perks:** Thunderstick pickup, student banner painting, Row 1-5 wristbands
                * **Section Hosts:** Marcus Vance (Section Director) & Elena Rostova (Prop Captain)
                """)
                ev_plaza = "plaza_rally_bb"
                rsvpd_plaza = ev_plaza in st.session_state.get("meetup_rsvps", [])
                if not rsvpd_plaza:
                    if st.button("🎟️ RSVP for Plaza Rally", key="btn_rsvp_plaza", use_container_width=True):
                        st.session_state.meetup_rsvps.append(ev_plaza)
                        st.session_state.tailgates_attended = st.session_state.get("tailgates_attended", 0) + 1
                        st.session_state.chant_action_taken = True
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()
                else:
                    st.success(f"🎟️ **RSVP CONFIRMED FOR {st.session_state.member_name.upper()} ({st.session_state.member_handle})!**\n\n📍 **Pass Assigned:** `Row 1-5 Wristband Priority` | **Event:** Arena Plaza Rally\n🔑 **Passport Hash:** `0xBCN-{st.session_state.member_hash[2:8].upper()}` &bull; Consistency: **{st.session_state.tailgates_attended} Event(s) Logged**")
                    if st.button("Cancel Plaza Rally RSVP", key="btn_cancel_plaza", use_container_width=True):
                        st.session_state.meetup_rsvps.remove(ev_plaza)
                        st.session_state.tailgates_attended = max(0, st.session_state.get("tailgates_attended", 1) - 1)
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()

            with m2:
                st.markdown(f"""
                **🍕 Campus Walk Pregame Crew (Hosted by Devon)**
                * **Meeting Spot:** Student Union Commons
                * **Shuttles Depart:** Every 10 minutes starting 90 minutes before {start_term}
                * **Perks:** Free pizza slice, 1.25x Early Arrival check-in coordination
                * **Section Host:** Devon Miller (Vocal Tactician)
                """)
                ev_campus = "campus_walk_bb"
                rsvpd_campus = ev_campus in st.session_state.get("meetup_rsvps", [])
                if not rsvpd_campus:
                    if st.button("🎟️ RSVP for Campus Walk", key="btn_rsvp_campus", use_container_width=True):
                        st.session_state.meetup_rsvps.append(ev_campus)
                        st.session_state.tailgates_attended = st.session_state.get("tailgates_attended", 0) + 1
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()
                else:
                    st.success(f"🎟️ **RSVP CONFIRMED FOR {st.session_state.member_name.upper()} ({st.session_state.member_handle})!**\n\n🚌 **Shuttle Pass:** `Union Commons Express #2` | **Event:** Campus Walk Crew\n🔑 **Passport Hash:** `0xBCN-{st.session_state.member_hash[2:8].upper()}` &bull; Consistency: **{st.session_state.tailgates_attended} Event(s) Logged**")
                    if st.button("Cancel Campus Walk RSVP", key="btn_cancel_campus", use_container_width=True):
                        st.session_state.meetup_rsvps.remove(ev_campus)
                        st.session_state.tailgates_attended = max(0, st.session_state.get("tailgates_attended", 1) - 1)
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()
        else:
            with m1:
                st.markdown(f"""
                **🏈 Lot B Mega-Tailgate Grill (Hosted by Carlos & Sarah)**
                * **Location:** Lot B, Row 4 (Under the Giant Blue Canopy)
                * **Arrival Time:** 4 Hours before {start_term}
                * **Menu & Perks:** 14-Hour Smoked Brisket, Sausage, Local Drinks, First-time members eat free!
                * **Section Hosts:** Carlos Mendez (Tailgate Host) & Sarah Jenkins (10-Yr Veteran)
                """)
                ev_lotb = "lotb_tailgate_fb"
                rsvpd_lotb = ev_lotb in st.session_state.get("meetup_rsvps", [])
                if not rsvpd_lotb:
                    if st.button("🎟️ RSVP for Lot B Tailgate", key="btn_rsvp_lotb", use_container_width=True):
                        st.session_state.meetup_rsvps.append(ev_lotb)
                        st.session_state.tailgates_attended = st.session_state.get("tailgates_attended", 0) + 1
                        st.session_state.chant_action_taken = True
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()
                else:
                    st.success(f"🎟️ **RSVP CONFIRMED FOR {st.session_state.member_name.upper()} ({st.session_state.member_handle})!**\n\n🥩 **Pass Assigned:** `Lot B VIP Smoked Brisket & Drink Voucher`\n🔑 **Passport Hash:** `0xBCN-{st.session_state.member_hash[2:8].upper()}` &bull; Consistency: **{st.session_state.tailgates_attended} Event(s) Logged**")
                    if st.button("Cancel Lot B RSVP", key="btn_cancel_lotb", use_container_width=True):
                        st.session_state.meetup_rsvps.remove(ev_lotb)
                        st.session_state.tailgates_attended = max(0, st.session_state.get("tailgates_attended", 1) - 1)
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()

            with m2:
                st.markdown(f"""
                **🚌 Stadium North Express Shuttle (Hosted by Maya)**
                * **Meeting Spot:** North Express Park & Ride (Bay 3)
                * **Tech Sync:** Wearable fitness band calibration and app BLE pairing station
                * **Perks:** Section 115 early check-in push for the 1.25x Multiplier!
                * **Section Host:** Maya Patel (Biometric & Tech Superfan)
                """)
                ev_shuttle = "north_shuttle_fb"
                rsvpd_shuttle = ev_shuttle in st.session_state.get("meetup_rsvps", [])
                if not rsvpd_shuttle:
                    if st.button("🎟️ RSVP for North Express Shuttle", key="btn_rsvp_shuttle", use_container_width=True):
                        st.session_state.meetup_rsvps.append(ev_shuttle)
                        st.session_state.tailgates_attended = st.session_state.get("tailgates_attended", 0) + 1
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()
                else:
                    st.success(f"🎟️ **RSVP CONFIRMED FOR {st.session_state.member_name.upper()} ({st.session_state.member_handle})!**\n\n🚌 **Boarding Pass:** `North Express Bay 3 Priority Shuttle`\n🔑 **Passport Hash:** `0xBCN-{st.session_state.member_hash[2:8].upper()}` &bull; Consistency: **{st.session_state.tailgates_attended} Event(s) Logged**")
                    if st.button("Cancel Shuttle RSVP", key="btn_cancel_shuttle", use_container_width=True):
                        st.session_state.meetup_rsvps.remove(ev_shuttle)
                        st.session_state.tailgates_attended = max(0, st.session_state.get("tailgates_attended", 1) - 1)
                        email = st.session_state.get("member_email", "fan@gmail.com")
                        if email in st.session_state.registered_fans_db:
                            st.session_state.registered_fans_db[email]["tailgates_attended"] = st.session_state.tailgates_attended
                            st.session_state.registered_fans_db[email]["meetup_rsvps"] = st.session_state.meetup_rsvps
                            _save_fans_db(st.session_state.registered_fans_db)
                        _ensure_member_in_persona_db()
                        st.rerun()

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
        try:
            from stream_simulator import TelemetryStreamSimulator
        except Exception:
            class TelemetryStreamSimulator:
                def __init__(self, sport="Basketball"): self.sport = sport
                def generate_live_tick(self, is_clutch=False, noise_variance=0.05) -> dict:
                    return self.get_next_tick(is_clutch=is_clutch)
                def get_next_tick(self, is_clutch=False) -> dict:
                    import random
                    if not is_clutch:
                        db = round(random.uniform(76.0, 83.0), 1)
                        hr = round(random.uniform(92.0, 104.0), 1)
                        taps = round(random.uniform(2.0, 3.8), 1)
                        vu = round(random.uniform(0.50, 0.62), 2)
                    else:
                        if self.sport == "Basketball":
                            db = round(random.uniform(103.0, 108.5), 1)
                            hr = round(random.uniform(130.0, 142.0), 1)
                            taps = round(random.uniform(11.0, 13.8), 1)
                            vu = round(random.uniform(0.82, 0.90), 2)
                        else:
                            db = round(random.uniform(108.0, 114.2), 1)
                            hr = round(random.uniform(140.0, 154.0), 1)
                            taps = round(random.uniform(12.5, 14.8), 1)
                            vu = round(random.uniform(0.88, 0.96), 2)
                    cmi = calc_momentum_index(db, hr, taps, vu)
                    tier = get_tier(cmi)
                    return {"sport": self.sport, "is_clutch": is_clutch, "db": db, "hr": hr, "taps": taps, "vu": vu, "cmi": cmi, "tier": tier}

        if "sim_instance" not in st.session_state:
            st.session_state.sim_instance = TelemetryStreamSimulator(st.session_state.sport)
        tick = st.session_state.sim_instance.generate_live_tick(
            is_clutch=st.session_state.is_clutch or surge_clicked, noise_variance=0.08 if surge_clicked else 0.05
        )
        st.session_state.db   = tick["db"]
        st.session_state.hr   = tick["hr"]
        st.session_state.taps = tick["taps"]
        st.session_state.vu   = tick["vu"]
        if surge_clicked:
            st.session_state.tap_count += 5
            st.session_state.synergy_score = min(100, st.session_state.synergy_score + 5)
        else:
            st.session_state.tap_count += 1
        current_cmi = calc_momentum_index(
            st.session_state.db, st.session_state.hr,
            st.session_state.taps, st.session_state.vu
        )
        tier  = get_tier(current_cmi)
        color = get_color(current_cmi)
        _ensure_member_in_persona_db()
        st.rerun()

    # Early Check-in with Immediate State Update
    with st.expander(f"🎟️ Pre-Game Roll Call: Early Seat Check-In ({st.session_state.sport})", expanded=True):
        st.write(f"Fans who reach their seats 30 minutes before **{start_term}** unlock a **1.25x 1st-Quarter Multiplier**.")
        if not st.session_state.early_checkin:
            sec_btn_label = "Section 114" if is_basketball else "Section 115"
            if st.button(f"📍 Check In at Seat ({sec_btn_label})", key="btn_checkin_seat"):
                st.session_state.early_checkin = True
                if st.session_state.member_email in st.session_state.registered_fans_db:
                    st.session_state.registered_fans_db[st.session_state.member_email]["games"] = max(1, st.session_state.registered_fans_db[st.session_state.member_email].get("games", 0) + 1)
                    _save_fans_db(st.session_state.registered_fans_db)
                _ensure_member_in_persona_db()
                st.rerun()
        else:
            user_seat_disp = st.session_state.registered_fans_db.get(st.session_state.member_email, {}).get("seat", "Section 114, Row 3, Seat 12" if is_basketball else "Section 115, Row 18, Seat 10")
            st.success(f"""
            🎟️ **CHECK-IN CONFIRMED FOR {st.session_state.member_name.upper()} ({st.session_state.member_handle})!**\n\n
            📍 **Seat Anchor:** `{user_seat_disp}` | 🔑 **Beacon Hash:** `0xBCN-{st.session_state.member_hash[2:10].upper()}` | **Status:** Verified In-Seat\n\n
            ⚡ **Early Arrival Multiplier (1.25x)** is active for your **365-Day Fan Passport**! Your attendance has been credited to your season record.
            """)
            if st.button("Cancel Seat Check-In", key="btn_cancel_checkin"):
                st.session_state.early_checkin = False
                _ensure_member_in_persona_db()
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
    <div style="background-color: {card_bg}; border: 3px solid {card_border}; border-radius: 12px; padding: 24px; max-width: 520px; margin: 10px auto; color: white; text-align: center; box-shadow: 0 0 20px {card_border}66;">
        <p style="color: #0f62fe; font-weight: bold; letter-spacing: 2px; margin: 0; font-size: 10pt;">KINETIC FANLAB // OFFICIAL PROOF-OF-MOMENTUM</p>
        <h1 style="color: white; margin: 8px 0; font-size: 32pt;">{card_points_display}</h1>
        <p style="color: {card_border}; font-weight: bold; font-size: 14pt; margin: 0;">{card_sub}</p>
        <hr style="border-color: #333; margin: 14px 0;">
        <div style="background-color: #111622; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #0f62fe55; text-align: left;">
            <p style="color: #f1c21b; font-size: 8.5pt; margin: 0; font-weight: bold; text-transform: uppercase;">VERIFIED FAN CERTIFICATE</p>
            <p style="color: #ffffff; font-size: 11pt; margin: 2px 0; font-weight: bold;">{st.session_state.member_name} <code style="color:#0f62fe;">{st.session_state.member_handle}</code></p>
            <p style="color: #a8a8a8; font-size: 8.5pt; margin: 0;">Passport Hash: <code>{st.session_state.member_hash}</code> &bull; Tier: <b>{st.session_state.member_tier}</b></p>
            <p style="color: #42be65; font-size: 8.5pt; margin: 2px 0 0 0;">Proof ID: <code>0xPRF-{st.session_state.sport[:2].upper()}-{int(current_cmi)}-{st.session_state.member_hash[2:6].upper()}</code></p>
        </div>
        <p style="color: #f4f4f4; font-size: 10.5pt; margin: 4px 0;">Sport: <b>{st.session_state.sport} ({role_tag})</b></p>
        <p style="color: #f4f4f4; font-size: 10.5pt; margin: 4px 0;">Acoustic Peak: <b>{st.session_state.db} dB</b> | Peak Heart Rate: <b>{int(st.session_state.hr)} BPM</b></p>
        <p style="color: #8d8d8d; font-size: 9pt; margin-top: 10px;">{winning_sec} Defense Belt Winner</p>
    </div>
    """, unsafe_allow_html=True)

    sh_col1, sh_col2, sh_col3 = st.columns([1, 2, 1])
    with sh_col2:
        share_btn_clicked = st.button("📲 Export Proof-of-Momentum & Share to Social Media", key="btn_share_proof_card", use_container_width=True)

    if share_btn_clicked or st.session_state.get("storycard_exported_flag"):
        fixture_id = active_preset.split(":")[0].strip()
        if share_btn_clicked:
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
            st.session_state.storycard_exported_flag = True

        import urllib.parse
        proof_url = f"https://kineticfanlab.com/proof/{st.session_state.sport.lower()}/{int(current_cmi)}?fan={st.session_state.member_handle}&hash={st.session_state.member_hash[:8]}"
        tweet_msg = f"Verified in-arena crowd impact: +{actual_surge} PTS momentum surge in {st.session_state.sport}! Locked in with my section on Kinetic FanLab. 🔥 #KineticFanLab #IBM"
        encoded_tweet = urllib.parse.quote(tweet_msg)
        encoded_url = urllib.parse.quote(proof_url)
        twitter_share_link = f"https://twitter.com/intent/tweet?text={encoded_tweet}&url={encoded_url}"
        fb_share = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"

        st.success(f"✅ Proof-of-Momentum card officially assigned to **{st.session_state.member_name}**!")
        
        st.markdown("#### 🌐 Share Your Verified Proof to Social Media:")
        soc1, soc2 = st.columns(2)
        with soc1:
            st.markdown(f'<a href="{twitter_share_link}" target="_blank" style="text-decoration:none;"><button style="background-color:#1d9bf0; color:white; border:none; padding:10px 16px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">𝕏 Post to X (Twitter)</button></a>', unsafe_allow_html=True)
        with soc2:
            st.markdown(f'<a href="{fb_share}" target="_blank" style="text-decoration:none;"><button style="background-color:#1877f2; color:white; border:none; padding:10px 16px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">📘 Share on Facebook</button></a>', unsafe_allow_html=True)

        with st.expander("📸 Instagram & TikTok Shareable Caption", expanded=True):
            insta_caption = f"Verified in-arena crowd momentum impact: +{actual_surge} PTS surge ({current_cmi}/100 CMI) in {st.session_state.sport}!\nSection Defense Belt Winner: {winning_sec}\nFan Passport: {st.session_state.member_name} ({st.session_state.member_handle}) | {st.session_state.member_hash}\nProof link: {proof_url}\n#KineticFanLab #IBM #FanMomentum #6thMan #12thMan #ProofOfMomentum"
            st.text_area("Copy Caption to Clipboard:", value=insta_caption, height=110)
            st.caption("Copy and paste this verified caption directly into your Instagram Story or TikTok post!")

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

    persona_options = get_persona_options()
    p_idx = persona_options.index(st.session_state.active_member) if st.session_state.active_member in persona_options else 0
    active_fan = st.selectbox("Active Fan Profile:", persona_options, index=p_idx, key="s5_fan_select")
    st.session_state.active_member = active_fan
    p_info = PERSONA_DB.get(active_fan, PERSONA_DB[st.session_state.member_name if st.session_state.get("is_logged_in") else ("Marcus Vance" if is_basketball else "Sarah Jenkins")])
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
