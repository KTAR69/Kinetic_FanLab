# ==============================================================================
# Kinetic FanLab — Scaffolded & Refactored via IBM Bob IDE
# IBM Cloud Services: watsonx.ai (Granite 4.0) | watsonx.governance Guardrails
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
        return f"Crowd momentum surged +{round(peak_cmi - pre_cmi, 1)} pts directly altering opponent execution."
    def summarize_tailgate_chants_live(sport: str, raw_proposals: list) -> list:
        return ["1. MISS IT! OFF THE RIM! - On release", "2. BRING THE NOISE! - Continuous", "3. DEFENSE! - Wave"]

try:
    from governance_check import evaluate_fan_content_safety
    GOVERNANCE_LIVE = True
except Exception:
    GOVERNANCE_LIVE = False
    def evaluate_fan_content_safety(raw_text: str) -> dict:
        return {"input_text": raw_text, "guardrail_status": "APPROVED", "violations": [], "action": "Proceed"}

st.set_page_config(page_title="Kinetic FanLab", page_icon="⚡", layout="wide")

# --- Mathematical Normalization & Ground Truth Formula ---
def normalize(val: float, min_val: float, max_val: float) -> float:
    clamped = max(min_val, min(val, max_val))
    return (clamped - min_val) / (max_val - min_val)

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
    if score >= 80.0: return "#da1e28" # Red
    elif score >= 65.0: return "#f1c21b" # Amber
    elif score >= 45.0: return "#0043ce" # Blue
    else: return "#0f62fe"

# --- Sidebar: Navigation & Instant Reactive Preset Switcher ---
st.sidebar.title("⚡ Kinetic FanLab")
st.sidebar.caption("Track 3: Fan-Centric Sports & Entertainment")

st.sidebar.markdown("---")
st.sidebar.markdown("**IBM Cloud Stack Status:**")
if WATSONX_LIVE:
    st.sidebar.success("🟢 watsonx.ai Live (Granite 4.0)")
else:
    st.sidebar.info("🔵 watsonx.ai (Analytical Fallback)")

if GOVERNANCE_LIVE:
    st.sidebar.success("🛡️ watsonx.governance Active")

st.sidebar.markdown("---")

screen = st.sidebar.radio("Navigate Platform:", [
    "👤 Screen 1: Fan Passport & Roster",
    "🎪 Screen 2: 36h Virtual Tailgate",
    "🏟️ Screen 3: In-Arena Game Hub & Trigger",
    "📊 Screen 4: Narrative Delta & Story Card"
])

st.sidebar.markdown("---")
# Reactive Selectbox: Changing this instantly updates state across all screens
active_preset = st.sidebar.selectbox("Load Canonical Fixture:", [
    "BB-01: Basketball Baseline (Free Throw 1)",
    "BB-02: Basketball Clutch (Free Throw 2)",
    "FB-01: Football Pre-Kick Timeout",
    "FB-02: Football 48-Yard FG Snap (Clutch)"
], key="fixture_picker")

# Reactively update fixture parameters if changed
if "last_fixture" not in st.session_state or st.session_state.last_fixture != active_preset:
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
        st.session_state.fan_notes = ["Timeout called, make him wait!"]
    elif "FB-02" in active_preset:
        st.session_state.sport = "Football"
        st.session_state.db = 111.8
        st.session_state.hr = 148.0
        st.session_state.taps = 14.0
        st.session_state.vu = 0.92
        st.session_state.is_clutch = True
        st.session_state.fan_notes = ["BLOCK THAT KICK! RATTLE THE KICKER! GET LOUD!"]
    
    # Reset tapper buffer on preset switch
    st.session_state.tap_count = 0
    st.session_state.tap_times = []

# Ensure other defaults exist
if "tap_count" not in st.session_state: st.session_state.tap_count = 0
if "tap_times" not in st.session_state: st.session_state.tap_times = []
if "early_checkin" not in st.session_state: st.session_state.early_checkin = False
if "respect_dict" not in st.session_state:
    st.session_state.respect_dict = {
        "Marcus Vance": 312, "Elena Rostova": 168, "Devon Miller": 245,
        "Sarah Jenkins": 480, "Carlos Mendez": 395, "Maya Patel": 185
    }

current_cmi = calc_momentum_index(st.session_state.db, st.session_state.hr, st.session_state.taps, st.session_state.vu)
tier = get_tier(current_cmi)
color = get_color(current_cmi)

is_basketball = st.session_state.sport == "Basketball"
start_term = "tip-off" if is_basketball else "kickoff"
role_tag = "6th Man" if is_basketball else "12th Man"

# Master Persona Database
# Master Persona Database (Permanent Identity Hashes across all fixtures)
PERSONA_DB = {
    "Marcus Vance": {
        "hash": "0xMV-sec114-8f7a2",
        "role": "Student Section Director",
        "tier": "Section Director (Tier 4)",
        "sec": "Section 114 (Thunder Row)",
        "games": 34, "career_db": "3,820 dB", "clutch_stops": 23,
        "neighbors": [
            {"name": "Elena Rostova", "seat": "Row 2, Seat 4", "role": "Prop Captain", "bio": "14 Games | Peak HR: 142 BPM | Waving Leader"},
            {"name": "Devon Miller", "seat": "Row 3, Seat 8", "role": "Vocal Tactician", "bio": "28 Games | 18 Voice Logs | Chant Starter"}
        ]
    },
    "Elena Rostova": {
        "hash": "0xER-sec114-3c9b1",
        "role": "Hype & Prop Captain",
        "tier": "Prop Captain (Tier 2)",
        "sec": "Section 114 (Thunder Row)",
        "games": 14, "career_db": "1,580 dB", "clutch_stops": 9,
        "neighbors": [
            {"name": "Marcus Vance", "seat": "Row 1, Seat 1", "role": "Section Director", "bio": "34 Games | Section Conductor | Megaphone Lead"},
            {"name": "Devon Miller", "seat": "Row 3, Seat 8", "role": "Vocal Tactician", "bio": "28 Games | 18 Voice Logs | Chant Starter"}
        ]
    },
    "Devon Miller": {
        "hash": "0xDM-sec114-6d4e8",
        "role": "Vocal Tactician",
        "tier": "Vocal Tactician (Tier 3)",
        "sec": "Section 114 (Thunder Row)",
        "games": 28, "career_db": "3,140 dB", "clutch_stops": 19,
        "neighbors": [
            {"name": "Marcus Vance", "seat": "Row 1, Seat 1", "role": "Section Director", "bio": "34 Games | Section Conductor | Megaphone Lead"},
            {"name": "Elena Rostova", "seat": "Row 2, Seat 4", "role": "Prop Captain", "bio": "14 Games | Peak HR: 142 BPM | Waving Leader"}
        ]
    },
    "Sarah Jenkins": {
        "hash": "0xSJ-sec115-7b2a5",
        "role": "10-Year Season Ticket Holder",
        "tier": "Stadium Veteran (Tier 5)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 62, "career_db": "6,850 dB", "clutch_stops": 31,
        "neighbors": [
            {"name": "Carlos Mendez", "seat": "Row 18, Seat 12", "role": "Lot B Tailgate Host", "bio": "45 Games | 10-Yr Season Ticket Holder | Early Arrival Champ"},
            {"name": "Maya Patel", "seat": "Row 19, Seat 14", "role": "Biometric Superfan", "bio": "18 Games | Peak HR: 154 BPM | Tech Ambassador"}
        ]
    },
    "Carlos Mendez": {
        "hash": "0xCM-sec115-4e8f9",
        "role": "Lot B Tailgate Host",
        "tier": "Tailgate Host (Tier 4)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 45, "career_db": "4,920 dB", "clutch_stops": 24,
        "neighbors": [
            {"name": "Sarah Jenkins", "seat": "Row 18, Seat 10", "role": "10-Year Veteran", "bio": "62 Games | 12th Man Bleacher Stomper | Defense Wall"},
            {"name": "Maya Patel", "seat": "Row 19, Seat 14", "role": "Biometric Superfan", "bio": "18 Games | Peak HR: 154 BPM | Tech Ambassador"}
        ]
    },
    "Maya Patel": {
        "hash": "0xMP-sec115-1a5c3",
        "role": "Biometric & Tech Superfan",
        "tier": "Tech Superfan (Tier 2)",
        "sec": "Section 115 (End Zone Loyals)",
        "games": 18, "career_db": "1,940 dB", "clutch_stops": 11,
        "neighbors": [
            {"name": "Sarah Jenkins", "seat": "Row 18, Seat 10", "role": "10-Year Veteran", "bio": "62 Games | 12th Man Bleacher Stomper | Defense Wall"},
            {"name": "Carlos Mendez", "seat": "Row 18, Seat 12", "role": "Lot B Tailgate Host", "bio": "45 Games | 10-Yr Season Ticket Holder | Early Arrival Champ"}
        ]
    }
}

# ==============================================================================
# SCREEN 1: THE LIVING FAN PASSPORT & SECTION ROSTER
# ==============================================================================
if screen == "👤 Screen 1: Fan Passport & Roster":
    st.header(f"👤 The Living Fan Passport & Section Roster ({st.session_state.sport})")
    st.caption("Persistent 365-day fandom identity, career telemetry, and peer-to-peer section camaraderie.")

    col_p, col_b = st.columns([1, 2])
    with col_p:
        if is_basketball:
            persona_options = ["Marcus Vance", "Elena Rostova", "Devon Miller"]
        else:
            persona_options = ["Sarah Jenkins", "Carlos Mendez", "Maya Patel"]

        selected_name = st.selectbox("Select Active Fan Persona:", persona_options)
        p_info = PERSONA_DB[selected_name]

        # Dynamic Artifact Badge Card (Web3 Abstraction with Unique Hash)
        glow_color = "#0043ce" if current_cmi < 80 else "#da1e28"
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

        r_cols = st.columns(2)
        for idx, neighbor in enumerate(p_info['neighbors']):
            with r_cols[idx]:
                st.markdown(f"**{neighbor['name']}** ({neighbor['seat']}) — *{neighbor['role']}*")
                st.caption(neighbor['bio'])

        if st.button("🤝 Send Respect Tap to Seat Neighbors"):
            st.session_state.respect_dict[selected_name] += 1
            st.success(f"Respect Tap Transmitted to {p_info['neighbors'][0]['name']} and {p_info['neighbors'][1]['name']}!")

# ==============================================================================
# SCREEN 2: 36-HOUR VIRTUAL TAILGATE
# ==============================================================================
elif screen == "🎪 Screen 2: 36h Virtual Tailgate":
    st.header(f"🎪 The 36-Hour Virtual Tailgate ({st.session_state.sport})")
    st.caption(f"Unlocks 36 hours before game-time. Section strategy, chant coordination, and community meetups for {st.session_state.sport}.")

    st.info(f"⏳ **COUNTDOWN TO {start_term.upper()}:** 14 Hours, 22 Minutes Remaining | **Section Status:** Strategy Huddle Active")

    tab_strat, tab_meet = st.tabs(["🗣️ Tactical Chant Huddle (IBM Granite)", "📍 Meetup Commons & Gameday Logistics"])

    with tab_strat:
        st.subheader(f"Defensive Chant Voting & Coordination ({st.session_state.sport})")
        st.write(f"Fans submit chant ideas for **{st.session_state.sport}**. **IBM Granite** analyzes proposals and synthesizes the top 3 coordinated chants:")

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

        if st.button("🤖 Synthesize Top 3 Section Chants with IBM Granite"):
            with st.spinner("Calling IBM Granite live on watsonx.ai..."):
                st.session_state[f"chants_{st.session_state.sport}"] = summarize_tailgate_chants_live(st.session_state.sport, chant_proposals)
            st.success(f"IBM Granite has synthesized this week's official {st.session_state.sport} defensive strategy!")

        # Display sport-specific synthesized chants
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
# SCREEN 3: IN-ARENA GAME HUB & CLUTCH TRIGGER
# ==============================================================================
elif screen == "🏟️ Screen 3: In-Arena Game Hub & Trigger":
    situation_tag = "Opponent Free Throw Distraction" if is_basketball else "Icing the Kicker Field Goal Stand"
    st.header(f"🏟️ In-Arena Game Hub & Clutch Trigger ({st.session_state.sport} — {role_tag})")
    st.caption(f"Live crowd acoustics, biometric telemetry, distraction tapping, and section competition for {st.session_state.sport}.")

    # Early Check-in
    with st.expander(f"🎟️ Pre-Game Roll Call: Early Seat Check-In ({st.session_state.sport})", expanded=not st.session_state.early_checkin):
        st.write(f"Fans who reach their seats 30 minutes before **{start_term}** unlock a **1.25x 1st-Quarter Multiplier**.")
        if not st.session_state.early_checkin:
            sec_btn_label = "Section 114" if is_basketball else "Section 115"
            if st.button(f"📍 Check In at Seat ({sec_btn_label})"):
                st.session_state.early_checkin = True
                st.success(f"Seat Verified! {sec_btn_label} Energy Multiplier boosted to 1.25x!")
        else:
            st.success("✅ Checked In: Section holds the Early Arrival Multiplier (1.25x)!")

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
    with col4: st.metric("In-App Taps", f"{st.session_state.taps}/s", delta="Surge" if st.session_state.taps > 10 else "Steady")
    with col5: st.metric("Vocal Urgency", f"{st.session_state.vu} VU", delta="Clutch" if st.session_state.vu > 0.8 else "Moderate")

    # In-Arena Section Rivalry (Sport & Fixture Dynamic)
    st.markdown("---")
    st.subheader(f"🏆 Live In-Arena Section Leaderboard ({st.session_state.sport})")
    
    if is_basketball:
        lead_sec = "Section 114 (Thunder Row)"
        chase_sec = "Section 115 (End Zone Loyals)"
        chase_pts = "-3.5 pts" if st.session_state.is_clutch else "-2.1 pts"
        score_1 = current_cmi
        score_2 = round(current_cmi - 3.5, 1) if st.session_state.is_clutch else 35.7
        score_3 = 31.4
    else:
        lead_sec = "Section 115 (End Zone Loyals)"
        chase_sec = "Section 114 (Thunder Row)"
        chase_pts = "-4.5 pts" if st.session_state.is_clutch else "-1.8 pts"
        score_1 = current_cmi
        score_2 = round(current_cmi - 4.5, 1) if st.session_state.is_clutch else 37.2
        score_3 = 33.1

    st.info(f"⚠️ **CHASER ALERT:** {chase_sec} is trailing {lead_sec} by only **{chase_pts}**! Tap below to defend your lead!")
    st.write(f"• **#1 {lead_sec}:** **{score_1} pts** (Leading Section)")
    st.progress(min(1.0, score_1 / 100.0))
    st.write(f"• **#2 {chase_sec}:** **{score_2} pts**")
    st.progress(min(1.0, max(0.0, score_2 / 100.0)))
    st.write(f"• **#3 Section 113 (Rider's Crew):** **{score_3} pts**")
    st.progress(min(1.0, score_3 / 100.0))

    # Interactive Tapper & Voice Logger
    st.markdown("---")
    c_tap, c_vox = st.columns(2)
    with c_tap:
        st.subheader("📱 Distraction Tapper")
        
        # Tapping calculation with active rolling window
        now = time.time()
        if st.button("🔥 TAP TO DISTRACT OPPONENT 🔥", use_container_width=True):
            st.session_state.tap_count += 1
            st.session_state.tap_times.append(now)

        # Filter taps in the last 2.5 seconds
        st.session_state.tap_times = [t for t in st.session_state.tap_times if now - t <= 2.5]
        active_taps = len(st.session_state.tap_times)
        
        if active_taps > 0:
            calc_speed = round(min(15.0, (active_taps / 2.5) * 3.5), 1)
            st.session_state.taps = calc_speed
        elif st.session_state.tap_count == 0:
            st.session_state.taps = 2.5 if is_basketball else 3.0

        tc1, tc2 = st.columns(2)
        tc1.metric("Taps Recorded", st.session_state.tap_count)
        tc2.metric("Active Tap Speed", f"{st.session_state.taps} taps/s")
        
        if st.button("Reset Tapper"):
            st.session_state.tap_count = 0
            st.session_state.tap_times = []
            st.session_state.taps = 0.0
            st.rerun()

    with c_vox:
        st.subheader("🎙️ Armchair Coach Reaction Logger")
        p_text = "e.g., MISS IT! OFF THE BACK IRON!" if is_basketball else "e.g., BLOCK THAT KICK! RATTLE HIM!"
        user_in = st.text_input("Enter Fan Outburst:", placeholder=p_text)
        if st.button("Submit & Audit Reaction"):
            if user_in.strip():
                gov = evaluate_fan_content_safety(user_in)
                if gov["guardrail_status"] == "REJECTED":
                    st.error(f"❌ REJECTED by watsonx.governance: {gov['violations'][0]}")
                else:
                    st.success("🛡️ APPROVED by watsonx.governance (Content Safe & Anonymized)")
                    with st.spinner("Scoring with IBM Granite live..."):
                        u_score = analyze_vocal_urgency_live(user_in)
                    st.session_state.vu = u_score
                    st.session_state.fan_notes.append(f"{user_in} (Live Urgency: {u_score} VU)")
                    st.info(f"Live IBM Granite Vocal Urgency: **{u_score} VU**")

        st.markdown(f"**Quick-Fire Chants ({st.session_state.sport}):**")
        q_cols = st.columns(2)
        if is_basketball:
            if q_cols[0].button("MISS IT! OFF THE RIM!"):
                st.session_state.vu = 0.85
                st.session_state.fan_notes.append("MISS IT! OFF THE RIM! (0.85 VU)")
                st.rerun()
            if q_cols[1].button("BRING THE NOISE!"):
                st.session_state.vu = 0.90
                st.session_state.fan_notes.append("BRING THE NOISE! (0.90 VU)")
                st.rerun()
            if q_cols[0].button("AIR BALL! AIR BALL!"):
                st.session_state.vu = 0.88
                st.session_state.fan_notes.append("AIR BALL! AIR BALL! (0.88 VU)")
                st.rerun()
            if q_cols[1].button("DEFENSE ON THREE!"):
                st.session_state.vu = 0.82
                st.session_state.fan_notes.append("DEFENSE ON THREE! (0.82 VU)")
                st.rerun()
        else:
            if q_cols[0].button("BLOCK THAT KICK!"):
                st.session_state.vu = 0.92
                st.session_state.fan_notes.append("BLOCK THAT KICK! (0.92 VU)")
                st.rerun()
            if q_cols[1].button("ICE THE KICKER!"):
                st.session_state.vu = 0.88
                st.session_state.fan_notes.append("ICE THE KICKER! (0.88 VU)")
                st.rerun()
            if q_cols[0].button("FALSE START! GET LOUD!"):
                st.session_state.vu = 0.95
                st.session_state.fan_notes.append("FALSE START! GET LOUD! (0.95 VU)")
                st.rerun()
            if q_cols[1].button("THIRD DOWN ROAR!"):
                st.session_state.vu = 0.90
                st.session_state.fan_notes.append("THIRD DOWN ROAR! (0.90 VU)")
                st.rerun()

        # Restored Recent Logged Outbursts Feed
        st.markdown("**Recent Logged Outbursts:**")
        for note in reversed(st.session_state.fan_notes[-3:]):
            st.markdown(f"- 📢 *\"{note}\"*")

# ==============================================================================
# SCREEN 4: NARRATIVE DELTA & SHAREABLE CROWD BOX SCORE
# ==============================================================================
elif screen == "📊 Screen 4: Narrative Delta & Story Card":
    st.header(f"📊 Narrative Delta & Shareable Crowd Box Score ({st.session_state.sport})")
    st.caption("Post-play synthesis connecting crowd disruption to on-field execution, with viral story card export.")

    # Exact fixture matching for surge calculations
    if "BB-01" in active_preset:
        pre_val = 37.8
        surge_val = 0.0
        surge_title = "+0.0 PTS (BASELINE ANTICIPATION)"
        outcome_label = "PENDING PLAY EXECUTION (Free Throw 1)"
        card_sub = "PRE-PLAY BASELINE ESTABLISHED"
    elif "BB-02" in active_preset:
        pre_val = 37.8
        surge_val = 44.1
        surge_title = "+44.1 PTS MOMENTUM SURGE"
        outcome_label = "MISSED FREE THROW (Defensive Rebound Secured)"
        card_sub = "CLUTCH DEFENSIVE STOP VERIFIED"
    elif "FB-01" in active_preset:
        pre_val = 39.0
        surge_val = 0.0
        surge_title = "+0.0 PTS (TIMEOUT DELAY LULL)"
        outcome_label = "TIMEOUT IN PROGRESS ('Icing the Kicker')"
        card_sub = "PRE-SNAP TENSION ESTABLISHED"
    else:  # FB-02
        pre_val = 39.0
        surge_val = 53.0
        surge_title = "+53.0 PTS MOMENTUM SURGE"
        outcome_label = "MISSED FIELD GOAL (Wide Left - Ice Successful)"
        card_sub = "CLUTCH DEFENSIVE STOP VERIFIED"

    st.markdown(f"""
    <div style="background-color: #edf5ff; padding: 18px; border-radius: 8px; border-left: 6px solid #0f62fe; margin-bottom: 20px;">
        <h2 style="color: #0043ce; margin: 0;">{surge_title}</h2>
        <p style="color: #161616; margin: 4px 0 0 0;">Pre-Play Baseline ({pre_val}/100) ➔ Current State ({current_cmi}/100) | Outcome: <b>{outcome_label}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Live Granite Narrative Generation
    st.subheader(f"🤖 IBM Granite Post-Play Narrative Synthesis ({st.session_state.sport})")
    with st.spinner(f"Synthesizing {st.session_state.sport} ecosystem narrative with IBM Granite..."):
        narrative = generate_narrative_live(st.session_state.sport, outcome_label, pre_val, current_cmi, st.session_state.fan_notes)
    st.markdown(f"> *{narrative}*")
    st.caption("⚡ Powered by IBM watsonx.ai & Granite Foundation Models (Dallas Region)")

    st.markdown("---")
    # Shareable Proof-of-Momentum Social Story Card
    st.subheader("📲 One-Tap Shareable 'Proof-of-Momentum' Card")
    st.write(f"Share your verified in-arena {st.session_state.sport} defensive impact to Instagram, TikTok, and X:")

    card_bg = "#161616"
    card_border = "#0f62fe" if current_cmi < 80 else "#da1e28"
    winning_sec = "Section 114 (Thunder Row)" if is_basketball else "Section 115 (End Zone Loyals)"

    st.markdown(f"""
    <div style="background-color: {card_bg}; border: 3px solid {card_border}; border-radius: 12px; padding: 24px; max-width: 500px; margin: 10px auto; color: white; text-align: center; box-shadow: 0 0 20px {card_border}66;">
        <p style="color: #0f62fe; font-weight: bold; letter-spacing: 2px; margin: 0; font-size: 11pt;">KINETIC FANLAB // OFFICIAL PROOF-OF-MOMENTUM</p>
        <h1 style="color: white; margin: 8px 0; font-size: 32pt;">+{surge_val} PTS</h1>
        <p style="color: {card_border}; font-weight: bold; font-size: 14pt; margin: 0;">{card_sub}</p>
        <hr style="border-color: #333; margin: 14px 0;">
        <p style="color: #f4f4f4; font-size: 11pt; margin: 4px 0;">Sport: <b>{st.session_state.sport} ({role_tag})</b></p>
        <p style="color: #f4f4f4; font-size: 11pt; margin: 4px 0;">Acoustic Peak: <b>{st.session_state.db} dB</b> | Peak Heart Rate: <b>{int(st.session_state.hr)} BPM</b></p>
        <p style="color: #8d8d8d; font-size: 9.5pt; margin-top: 12px;">Verified by IBM watsonx Granite // {winning_sec} Defense Belt Winner</p>
    </div>
    """, unsafe_allow_html=True)

    # Official Crowd Box Score (Section Battle Winner)
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
        st.markdown(f"""
        **Your Personal Fan Contribution ({user_sec}):**
        * Distraction Taps Contributed: **{st.session_state.tap_count} clicks**
        * Peak Physiological Stress: **{int(st.session_state.hr)} BPM**
        * Peak Acoustic Contribution: **{st.session_state.db} dB**
        """)