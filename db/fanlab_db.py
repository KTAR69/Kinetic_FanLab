"""
==============================================================================
Kinetic FanLab — Hybrid Relational & NoSQL Audit Database (db/fanlab_db.py)
Scaffolded & Refactored via IBM Bob IDE & Gemini (Track 3: Sports & Entertainment)
==============================================================================
Implements the 6-table enterprise relational schema modeled after the IBM
SkillsBuild watsonx Orchestrate Technical Session (`resolve_ai` DB pattern),
bridged with our existing IBM Cloudant NoSQL engine (`cloudant_engine.py`).

Tables:
  1. fan_passports            — 365-day fan identity, hashes, BLE anchors & Respect Taps
  2. cmi_telemetry_logs       — Sanitized Log SPL dB, Hampel BPM, Taps, VU & BLE reduction
  3. section_standings        — Per-capita section leaderboards, multipliers & Chaser Alerts
  4. audit_trail              — 16-Agent Chain-of-Thought traces, DIR fairness & latency SLAs
  5. unit_economics_ledger    — Two-sided FinOps ledger: compute cost vs. sponsor ROI per seat
  6. discovery_feature_matrix — User Discovery Interview scores & feature value-to-cost index
==============================================================================
"""

import os
import sqlite3
import json
import tempfile
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(DB_DIR, "kinetic_fanlab.sqlite3")
JSON_MIRROR_PATH = os.path.join(DB_DIR, "kinetic_fanlab_tables.json")


# ==============================================================================
# STEP 4B: 8-PERSONA USER DISCOVERY SESSIONS & PROTOTYPE ITERATIONS (SLIDE 24)
# ==============================================================================

USER_DISCOVERY_PERSONA_SESSIONS: List[Dict[str, Any]] = [
    {
        "member_name": "Marcus Vance",
        "member_hash": "0xMV-sec114-8f7a2",
        "sport": "Basketball",
        "section_id": "Section 114 (Thunder Row)",
        "tier": 4,
        "role": "Student Section Director",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 35,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 20,
            "FEAT-04_granite_storycard": 25,
            "FEAT-05_sponsor_perks": 20,
        },
        "usability_finding": "Needs instant <250ms visual cue (T-10s to T-2s) without looking down at phone during free-throw release.",
        "prototype_iteration_id": "ITER-03",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Elena Rostova",
        "member_hash": "0xER-sec114-3c9b1",
        "sport": "Basketball",
        "section_id": "Section 114 (Thunder Row)",
        "tier": 2,
        "role": "Hype & Prop Captain",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 30,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 25,
            "FEAT-04_granite_storycard": 20,
            "FEAT-05_sponsor_perks": 25,
        },
        "usability_finding": "Wanted prop-waving cadence synchronized with adjacent rows even when arena Wi-Fi congests.",
        "prototype_iteration_id": "ITER-03",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Devon Miller",
        "member_hash": "0xDM-sec114-6d4e8",
        "sport": "Basketball",
        "section_id": "Section 114 (Thunder Row)",
        "tier": 3,
        "role": "Vocal Tactician",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 35,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 15,
            "FEAT-04_granite_storycard": 25,
            "FEAT-05_sponsor_perks": 25,
        },
        "usability_finding": "Uses regional student slang; worried automated safety filters would falsely block clean hype chants.",
        "prototype_iteration_id": "ITER-04",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Jordan Lee",
        "member_hash": "0xJL-sec114-1f4a9",
        "sport": "Basketball",
        "section_id": "Section 114 (Thunder Row)",
        "tier": 1,
        "role": "Rookie Section Member",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 30,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 20,
            "FEAT-04_granite_storycard": 20,
            "FEAT-05_sponsor_perks": 30,
        },
        "usability_finding": "Felt intimidated by 30-game veterans dominating raw cumulative leaderboards.",
        "prototype_iteration_id": "ITER-03",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Sarah Jenkins",
        "member_hash": "0xSJ-sec115-7b2a5",
        "sport": "Football",
        "section_id": "Section 115 (End Zone Loyals)",
        "tier": 5,
        "role": "10-Year Season Ticket Holder",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 40,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 15,
            "FEAT-04_granite_storycard": 20,
            "FEAT-05_sponsor_perks": 25,
        },
        "usability_finding": "Refuses any app that uploads raw voice audio to the cloud and noted PA music inflates decibel meters.",
        "prototype_iteration_id": "ITER-01",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Carlos Mendez",
        "member_hash": "0xCM-sec115-4e8f9",
        "sport": "Football",
        "section_id": "Section 115 (End Zone Loyals)",
        "tier": 4,
        "role": "Lot B Tailgate Host",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 35,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 15,
            "FEAT-04_granite_storycard": 20,
            "FEAT-05_sponsor_perks": 30,
        },
        "usability_finding": "Wanted Lot B tailgate chant ideas synthesized before kickoff and tied to real concession perks.",
        "prototype_iteration_id": "ITER-01",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Maya Patel",
        "member_hash": "0xMP-sec115-1a5c3",
        "sport": "Football",
        "section_id": "Section 115 (End Zone Loyals)",
        "tier": 2,
        "role": "Biometric & Tech Superfan",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 35,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 20,
            "FEAT-04_granite_storycard": 20,
            "FEAT-05_sponsor_perks": 25,
        },
        "usability_finding": "Observed smartwatch optical HR sensors drop to 0 BPM or spike >205 BPM when clapping hard on bleachers.",
        "prototype_iteration_id": "ITER-02",
        "trust_privacy_approved": True,
    },
    {
        "member_name": "Alex Taylor",
        "member_hash": "0xAT-sec115-5c2d3",
        "sport": "Football",
        "section_id": "Section 115 (End Zone Loyals)",
        "tier": 1,
        "role": "General Season Ticket Holder",
        "budget_allocation_100": {
            "FEAT-01_edge_spl": 32,
            "FEAT-02_raw_cloud_audio": 0,
            "FEAT-03_tapper_ble": 16,
            "FEAT-04_granite_storycard": 18,
            "FEAT-05_sponsor_perks": 34,
        },
        "usability_finding": "Wanted verifiable cryptographic proof that Section 115 caused the missed 48-yard FG to share on social media.",
        "prototype_iteration_id": "ITER-04",
        "trust_privacy_approved": True,
    },
]

PROTOTYPE_ITERATIONS_SLIDE24: List[Dict[str, Any]] = [
    {
        "iteration_id": "ITER-01",
        "title": "Edge-Only Acoustic Log SPL & -3.5 dB PA Bleed Filter",
        "module": "telemetry_dsp.py",
        "triggered_by": "Sarah Jenkins (Privacy) & Coach Denis Zakharov (FinOps Cloud Cost)",
        "before_state": "Continuous raw audio streaming ($0.4200/seat) vulnerable to stadium PA speaker bleed.",
        "after_state": "On-device Logarithmic SPL summation + -3.5 dB PA attenuation transmitting a 4-byte float ($0.0000 cloud DSP cost).",
        "quantified_impact": "100% raw audio privacy compliance & $0.4063/seat compute savings ($32,504/game saved at 80,000 seats).",
    },
    {
        "iteration_id": "ITER-02",
        "title": "Biometric Hampel Outlier Filter (50-205 BPM)",
        "module": "telemetry_dsp.py",
        "triggered_by": "Maya Patel (Wearable Sensor Motion Artifacts)",
        "before_state": "Clapping and bleacher stomping injected 0.0 BPM dropouts and 225.0 BPM optical sensor spikes.",
        "after_state": "Local Hampel filter rejects <50 BPM and >205 BPM artifacts prior to 25%-weighted HR normalization.",
        "quantified_impact": "Eliminated 100% of synthetic HR distortion across canonical fixtures BB-01..FB-02.",
    },
    {
        "iteration_id": "ITER-03",
        "title": "Eyes-Free Burst Tapper (+5) & Per-Capita Section Normalization",
        "module": "app.py & tools/front_stage_tools.py",
        "triggered_by": "Marcus Vance, Elena Rostova & Jordan Lee (In-Arena Usability)",
        "before_state": "Single-tap button required looking down at screen; raw cumulative points favored large veteran sections.",
        "after_state": "Added single-thumb Burst Tap (+5), 50-seat BLE mesh pod sync (98% backhaul reduction), and per-capita Chaser Alerts.",
        "quantified_impact": "<250ms eyes-free interaction latency and fair rookie/veteran section competition.",
    },
    {
        "iteration_id": "ITER-04",
        "title": "EEOC 4/5ths Dialect Fairness Gate & SHA-256 Proof Cards",
        "module": "governance_fairness.py & cos_archive.py",
        "triggered_by": "Devon Miller (Dialect Fairness) & Alex Taylor (Verifiable Social Proof)",
        "before_state": "Generic toxicity filter risked false positives on student slang; post-game cards lacked cryptographic verification.",
        "after_state": "5-cohort dialect fairness calibration (DIR = 0.953 >= 0.80) + IBM COS S3 64-hex SHA-256 box-score receipts.",
        "quantified_impact": "Zero false-positive dialect rejections (DIR = 0.953) & 100% tamper-evident social story cards.",
    },
]


class FanLabDatabase:
    """Thread-safe 6-table relational audit and FinOps database for Kinetic FanLab."""

    _lock = threading.Lock()

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.requested_db_path = db_path
        self.db_path = self._resolve_writable_sqlite_path(db_path)
        self.json_mirror_path = JSON_MIRROR_PATH
        self._init_schema()
        self._seed_canonical_data()
        self._sync_json_mirror()

    def _resolve_writable_sqlite_path(self, candidate_path: str) -> str:
        """Uses candidate_path on native OS filesystems; falls back to tempdir if FUSE blocks fcntl locks."""
        try:
            conn = sqlite3.connect(candidate_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=MEMORY;")
            conn.execute("CREATE TABLE IF NOT EXISTS _lock_probe (id INT);")
            conn.commit()
            conn.close()
            return candidate_path
        except sqlite3.OperationalError:
            fallback = os.path.join(tempfile.gettempdir(), "kinetic_fanlab.sqlite3")
            return fallback

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            cur = conn.cursor()

            # 1. fan_passports
            cur.execute("""
                CREATE TABLE IF NOT EXISTS fan_passports (
                    member_hash TEXT PRIMARY KEY,
                    member_name TEXT NOT NULL,
                    section_id TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    role TEXT NOT NULL,
                    tier INTEGER NOT NULL,
                    games_attended INTEGER NOT NULL,
                    career_db REAL NOT NULL,
                    clutch_stops INTEGER NOT NULL,
                    respect_taps INTEGER NOT NULL,
                    ble_anchor_verified INTEGER NOT NULL DEFAULT 1,
                    early_multiplier REAL NOT NULL DEFAULT 1.0,
                    updated_at TEXT NOT NULL
                )
            """)

            # 2. cmi_telemetry_logs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cmi_telemetry_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    section_id TEXT NOT NULL,
                    raw_db REAL NOT NULL,
                    clean_log_db REAL NOT NULL,
                    pa_bleed_db REAL NOT NULL,
                    clean_hr_bpm REAL NOT NULL,
                    taps_per_sec REAL NOT NULL,
                    granite_vu REAL NOT NULL,
                    cmi_score REAL NOT NULL,
                    ble_pod_id TEXT NOT NULL,
                    backhaul_reduction_pct REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 3. section_standings
            cur.execute("""
                CREATE TABLE IF NOT EXISTS section_standings (
                    standing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    section_name TEXT NOT NULL,
                    raw_cmi REAL NOT NULL,
                    checked_in_fans INTEGER NOT NULL,
                    early_multiplier REAL NOT NULL,
                    clutch_multiplier REAL NOT NULL,
                    per_capita_score REAL NOT NULL,
                    rank_position INTEGER NOT NULL,
                    chaser_alert TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 4. audit_trail
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    theatre_tier TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    guardrail_status TEXT NOT NULL,
                    dir_fairness_score REAL NOT NULL,
                    latency_ms REAL NOT NULL,
                    chain_of_thought TEXT NOT NULL,
                    escalated_to_human INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)

            # 5. unit_economics_ledger
            cur.execute("""
                CREATE TABLE IF NOT EXISTS unit_economics_ledger (
                    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fixture_id TEXT NOT NULL,
                    seat_count INTEGER NOT NULL,
                    edge_dsp_cost_usd REAL NOT NULL,
                    granite_tokens_used INTEGER NOT NULL,
                    granite_compute_cost_usd REAL NOT NULL,
                    total_cost_per_seat_usd REAL NOT NULL,
                    sponsor_campaign_id TEXT NOT NULL,
                    sponsor_revenue_per_seat_usd REAL NOT NULL,
                    net_margin_per_seat_usd REAL NOT NULL,
                    gross_margin_pct REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # 6. discovery_feature_matrix
            cur.execute("""
                CREATE TABLE IF NOT EXISTS discovery_feature_matrix (
                    feature_id TEXT PRIMARY KEY,
                    feature_name TEXT NOT NULL,
                    theatre_agent_owner TEXT NOT NULL,
                    interviews_conducted INTEGER NOT NULL,
                    fan_demand_score_10 REAL NOT NULL,
                    willingness_to_keep_pct REAL NOT NULL,
                    compute_cost_per_seat_usd REAL NOT NULL,
                    value_to_cost_index REAL NOT NULL,
                    verdict TEXT NOT NULL,
                    interview_notes TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _seed_canonical_data(self) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as conn:
            cur = conn.cursor()

            # Seed 8 canonical fan personas if empty
            cur.execute("SELECT COUNT(*) FROM fan_passports")
            if cur.fetchone()[0] == 0:
                personas = [
                    ("0xMV-sec114-8f7a2", "Marcus Vance", "Section 114", "Basketball", "Student Section Director", 4, 34, 3820.0, 23, 313, 1, 1.25, now_iso),
                    ("0xER-sec114-3c9b1", "Elena Rostova", "Section 114", "Basketball", "Hype & Prop Captain", 2, 14, 1580.0, 9, 168, 1, 1.0, now_iso),
                    ("0xDM-sec114-6d4e8", "Devon Miller", "Section 114", "Basketball", "Vocal Tactician", 3, 28, 3140.0, 19, 245, 1, 1.25, now_iso),
                    ("0xJL-sec114-1f4a9", "Jordan Lee", "Section 114", "Basketball", "Rookie Section Member", 1, 3, 310.0, 1, 28, 1, 1.0, now_iso),
                    ("0xSJ-sec115-7b2a5", "Sarah Jenkins", "Section 115", "Football", "10-Year Season Ticket Holder", 5, 62, 6850.0, 31, 480, 1, 1.25, now_iso),
                    ("0xCM-sec115-4e8f9", "Carlos Mendez", "Section 115", "Football", "Lot B Tailgate Host", 4, 45, 4920.0, 24, 395, 1, 1.25, now_iso),
                    ("0xMP-sec115-1a5c3", "Maya Patel", "Section 115", "Football", "Biometric & Tech Superfan", 2, 18, 1940.0, 11, 185, 1, 1.0, now_iso),
                    ("0xAT-sec115-5c2d3", "Alex Taylor", "Section 115", "Football", "General Season Ticket Holder", 1, 4, 420.0, 2, 45, 1, 1.0, now_iso),
                ]
                cur.executemany("""
                    INSERT INTO fan_passports VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, personas)

            # Seed canonical Discovery Feature Matrix if empty
            cur.execute("SELECT COUNT(*) FROM discovery_feature_matrix")
            if cur.fetchone()[0] == 0:
                features = [
                    (
                        "FEAT-01",
                        "Edge Acoustic Decibel Wall (Log SPL + PA Filter)",
                        "sound_telemetry_agent",
                        12,
                        9.4,
                        91.7,
                        0.0000,
                        99.9,
                        "KEEP_CORE_EDGE",
                        "Fans love proving their section hit 111 dB. Because DSP runs locally on mobile silicon (4-byte float over BLE mesh), cloud compute cost is $0.00.",
                        now_iso,
                    ),
                    (
                        "FEAT-02",
                        "Raw Uncompressed Cloud Audio Streaming",
                        "unit_economics_agent",
                        12,
                        2.1,
                        8.3,
                        0.4200,
                        5.0,
                        "DEPRECATED_BY_DESIGN",
                        "Denis flagged raw audio cost & privacy concern. Discovery confirms fans reject raw mic recording and FinOps proves $0.42/seat kills margin. Eliminated in favor of local SPL float.",
                        now_iso,
                    ),
                    (
                        "FEAT-03",
                        "Clutch Distraction Tapper & BLE Pod Sync",
                        "mesh_rigging_agent",
                        12,
                        8.8,
                        83.3,
                        0.0005,
                        96.5,
                        "KEEP_CORE_EDGE",
                        "High engagement during free throws and field goal snaps; 50-seat BLE pod aggregation cuts cellular backhaul by 98.0%.",
                        now_iso,
                    ),
                    (
                        "FEAT-04",
                        "Event-Gated IBM Granite Chant & Delta StoryCards",
                        "synthesizer_agent",
                        12,
                        9.1,
                        88.0,
                        0.0112,
                        94.2,
                        "KEEP_EVENT_GATED",
                        "Gating Granite calls strictly to 36h Tailgate synthesis and Clutch stops keeps LLM cost at $0.0112/fan while driving viral social sharing.",
                        now_iso,
                    ),
                    (
                        "FEAT-05",
                        "Dynamic Sponsor Concession & Merch Perks",
                        "sponsor_monetization_agent",
                        12,
                        9.6,
                        95.0,
                        0.0025,
                        98.8,
                        "KEEP_REVENUE_DRIVER",
                        "Primary monetization engine generating $3.00-$8.00 per active seat in sponsor attribution and concession lift.",
                        now_iso,
                    ),
                ]
                cur.executemany("""
                    INSERT INTO discovery_feature_matrix VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, features)

            # Seed multi-fixture & multi-scale Unit Economics baseline if empty
            cur.execute("SELECT COUNT(*) FROM unit_economics_ledger")
            if cur.fetchone()[0] == 0:
                seed_entries = [
                    # 4 Canonical Fixtures at 50-seat BLE Pod scale
                    ("BB-01", 50, 0.0000, 0, 0.0400, 0.0008, "SPON-BASELINE-IDLE", 0.0000, -0.0008, 0.00, now_iso),
                    ("BB-02", 50, 0.0000, 1420, 0.6850, 0.0137, "SPON-111DB-CONCESSION", 4.8500, 4.8363, 99.72, now_iso),
                    ("FB-01", 50, 0.0000, 0, 0.0400, 0.0008, "SPON-BASELINE-IDLE", 0.0000, -0.0008, 0.00, now_iso),
                    ("FB-02", 50, 0.0000, 1420, 0.6850, 0.0137, "SPON-111DB-CONCESSION", 4.8500, 4.8363, 99.72, now_iso),
                    # Multi-scale stadium benchmarks (Section, Arena, Stadium)
                    ("BB-02-SECTION-1500", 1500, 0.0000, 42600, 20.5500, 0.0137, "SPON-111DB-CONCESSION", 4.8500, 4.8363, 99.72, now_iso),
                    ("BB-02-ARENA-18000", 18000, 0.0000, 511200, 246.6000, 0.0137, "SPON-111DB-CONCESSION", 4.8500, 4.8363, 99.72, now_iso),
                    ("FB-02-STADIUM-80000", 80000, 0.0000, 2272000, 1096.0000, 0.0137, "SPON-111DB-CONCESSION", 4.8500, 4.8363, 99.72, now_iso),
                ]
                cur.executemany("""
                    INSERT INTO unit_economics_ledger (
                        fixture_id, seat_count, edge_dsp_cost_usd, granite_tokens_used,
                        granite_compute_cost_usd, total_cost_per_seat_usd, sponsor_campaign_id,
                        sponsor_revenue_per_seat_usd, net_margin_per_seat_usd, gross_margin_pct, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, seed_entries)

            conn.commit()

    def _sync_json_mirror(self) -> None:
        """Writes a human-readable JSON snapshot of all 6 relational tables to db/kinetic_fanlab_tables.json."""
        tables = [
            "fan_passports",
            "cmi_telemetry_logs",
            "section_standings",
            "audit_trail",
            "unit_economics_ledger",
            "discovery_feature_matrix",
        ]
        snapshot: Dict[str, Any] = {}
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            for t in tables:
                cur.execute(f"SELECT * FROM {t}")
                snapshot[t] = [dict(r) for r in cur.fetchall()]
        snapshot["user_discovery_persona_sessions"] = USER_DISCOVERY_PERSONA_SESSIONS
        snapshot["prototype_iterations_slide24"] = PROTOTYPE_ITERATIONS_SLIDE24
        try:
            with open(self.json_mirror_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # CRUD & Audit Helper Methods for the 16-Agent Pipeline
    # ------------------------------------------------------------------
    def log_telemetry(
        self,
        fixture_id: str,
        sport: str,
        section_id: str,
        raw_db: float,
        clean_log_db: float,
        pa_bleed_db: float,
        clean_hr_bpm: float,
        taps_per_sec: float,
        granite_vu: float,
        cmi_score: float,
        ble_pod_id: str = "POD-SEC114-01",
        backhaul_reduction_pct: float = 98.0,
    ) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO cmi_telemetry_logs (
                    fixture_id, sport, section_id, raw_db, clean_log_db, pa_bleed_db,
                    clean_hr_bpm, taps_per_sec, granite_vu, cmi_score, ble_pod_id,
                    backhaul_reduction_pct, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fixture_id, sport, section_id, raw_db, clean_log_db, pa_bleed_db,
                clean_hr_bpm, taps_per_sec, granite_vu, cmi_score, ble_pod_id,
                backhaul_reduction_pct, now_iso
            ))
            conn.commit()
            row_id = int(cur.lastrowid or 0)
        self._sync_json_mirror()
        return row_id

    def log_audit_step(
        self,
        trace_id: str,
        agent_name: str,
        theatre_tier: str,
        event_type: str,
        confidence_score: float,
        guardrail_status: str,
        dir_fairness_score: float,
        latency_ms: float,
        chain_of_thought: str,
        escalated_to_human: bool = False,
    ) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_trail (
                    trace_id, agent_name, theatre_tier, event_type, confidence_score,
                    guardrail_status, dir_fairness_score, latency_ms, chain_of_thought,
                    escalated_to_human, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace_id, agent_name, theatre_tier, event_type, confidence_score,
                guardrail_status, dir_fairness_score, latency_ms, chain_of_thought,
                1 if escalated_to_human else 0, now_iso
            ))
            conn.commit()
            row_id = int(cur.lastrowid or 0)
        self._sync_json_mirror()
        return row_id

    def log_unit_economics(
        self,
        fixture_id: str,
        seat_count: int,
        edge_dsp_cost_usd: float,
        granite_tokens_used: int,
        granite_compute_cost_usd: float,
        sponsor_campaign_id: str,
        sponsor_revenue_per_seat_usd: float,
    ) -> Dict[str, Any]:
        now_iso = datetime.now(timezone.utc).isoformat()
        total_cost_per_seat = round((edge_dsp_cost_usd + granite_compute_cost_usd) / max(1, seat_count), 4)
        net_margin_per_seat = round(sponsor_revenue_per_seat_usd - total_cost_per_seat, 4)
        gross_margin_pct = round(
            (net_margin_per_seat / sponsor_revenue_per_seat_usd) * 100.0, 2
        ) if sponsor_revenue_per_seat_usd > 0 else 0.0

        raw_cloud_audio_cost_total = round(0.4200 * seat_count, 2)
        hybrid_cost_total = round(total_cost_per_seat * seat_count, 2)
        cloud_savings_total = round(raw_cloud_audio_cost_total - hybrid_cost_total, 2)

        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO unit_economics_ledger (
                    fixture_id, seat_count, edge_dsp_cost_usd, granite_tokens_used,
                    granite_compute_cost_usd, total_cost_per_seat_usd, sponsor_campaign_id,
                    sponsor_revenue_per_seat_usd, net_margin_per_seat_usd, gross_margin_pct, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fixture_id, seat_count, edge_dsp_cost_usd, granite_tokens_used,
                granite_compute_cost_usd, total_cost_per_seat, sponsor_campaign_id,
                sponsor_revenue_per_seat_usd, net_margin_per_seat, gross_margin_pct, now_iso
            ))
            conn.commit()
            entry_id = int(cur.lastrowid or 0)

        self._sync_json_mirror()
        return {
            "entry_id": entry_id,
            "fixture_id": fixture_id,
            "seat_count": seat_count,
            "total_cost_per_seat_usd": total_cost_per_seat,
            "raw_cloud_audio_cost_per_seat_usd": 0.4200,
            "cloud_cost_saved_per_seat_usd": round(0.4200 - total_cost_per_seat, 4),
            "cloud_cost_saved_total_usd": cloud_savings_total,
            "sponsor_revenue_per_seat_usd": sponsor_revenue_per_seat_usd,
            "net_margin_per_seat_usd": net_margin_per_seat,
            "gross_margin_pct": gross_margin_pct,
            "within_cost_ceiling": total_cost_per_seat <= 0.0150,
        }

    def evaluate_stadium_scale_economics(
        self,
        seat_count: int = 80000,
        is_clutch_or_tailgate: bool = True,
        sponsor_revenue_per_seat_usd: float = 4.85,
    ) -> Dict[str, Any]:
        """
        Computes full venue-scale Two-Sided Unit Economics & Cloud Cost Avoidance
        across 50-seat pods, 1,500-seat sections, 18,000-seat arenas, or 80,000-seat stadiums.
        """
        pods = max(1, seat_count // 50)
        unit_cost = 0.0137 if is_clutch_or_tailgate else 0.0008
        raw_audio_unit_cost = 0.4200
        total_hybrid_cost = round(unit_cost * seat_count, 2)
        total_raw_audio_cost = round(raw_audio_unit_cost * seat_count, 2)
        total_cloud_savings = round(total_raw_audio_cost - total_hybrid_cost, 2)
        total_sponsor_rev = round(sponsor_revenue_per_seat_usd * seat_count, 2) if is_clutch_or_tailgate else 0.0
        total_net_margin = round(total_sponsor_rev - total_hybrid_cost, 2)
        gross_margin_pct = round((total_net_margin / total_sponsor_rev) * 100.0, 2) if total_sponsor_rev > 0 else 0.0

        return {
            "seat_count": seat_count,
            "ble_pods_50_to_1": pods,
            "unit_cost_per_seat_usd": unit_cost,
            "raw_cloud_audio_unit_cost_usd": raw_audio_unit_cost,
            "total_hybrid_compute_cost_usd": total_hybrid_cost,
            "total_raw_cloud_audio_cost_usd": total_raw_audio_cost,
            "total_cloud_cost_saved_usd": total_cloud_savings,
            "cost_reduction_vs_raw_audio_pct": round((1.0 - (unit_cost / raw_audio_unit_cost)) * 100.0, 2),
            "sponsor_revenue_per_seat_usd": sponsor_revenue_per_seat_usd if is_clutch_or_tailgate else 0.0,
            "total_sponsor_revenue_usd": total_sponsor_rev,
            "total_net_margin_usd": total_net_margin,
            "gross_margin_pct": gross_margin_pct,
            "within_cost_ceiling": unit_cost <= 0.0150,
        }

    def log_section_standing(
        self,
        fixture_id: str,
        sport: str,
        section_name: str,
        raw_cmi: float,
        checked_in_fans: int,
        early_multiplier: float,
        clutch_multiplier: float,
        per_capita_score: float,
        rank_position: int,
        chaser_alert: str,
    ) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO section_standings (
                    fixture_id, sport, section_name, raw_cmi, checked_in_fans,
                    early_multiplier, clutch_multiplier, per_capita_score,
                    rank_position, chaser_alert, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fixture_id, sport, section_name, raw_cmi, checked_in_fans,
                early_multiplier, clutch_multiplier, per_capita_score,
                rank_position, chaser_alert, now_iso
            ))
            conn.commit()
            row_id = int(cur.lastrowid or 0)
        self._sync_json_mirror()
        return row_id

    def get_passport(self, member_name_or_hash: str) -> Optional[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM fan_passports
                WHERE member_hash = ? OR member_name = ?
                LIMIT 1
            """, (member_name_or_hash, member_name_or_hash))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_table_counts(self) -> Dict[str, int]:
        tables = [
            "fan_passports",
            "cmi_telemetry_logs",
            "section_standings",
            "audit_trail",
            "unit_economics_ledger",
            "discovery_feature_matrix",
        ]
        counts: Dict[str, int] = {}
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            for t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                counts[t] = int(cur.fetchone()[0])
        return counts

    def get_trace_audit_trail(self, trace_id: str) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM audit_trail
                WHERE trace_id = ?
                ORDER BY audit_id ASC
            """, (trace_id,))
            return [dict(r) for r in cur.fetchall()]

    def get_discovery_matrix(self) -> List[Dict[str, Any]]:
        with self._lock, self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM discovery_feature_matrix ORDER BY value_to_cost_index DESC")
            return [dict(r) for r in cur.fetchall()]

    def get_user_discovery_persona_sessions(self) -> List[Dict[str, Any]]:
        return list(USER_DISCOVERY_PERSONA_SESSIONS)

    def get_prototype_iterations(self) -> List[Dict[str, Any]]:
        return list(PROTOTYPE_ITERATIONS_SLIDE24)


_GLOBAL_DB: Optional[FanLabDatabase] = None


def get_db(db_path: str = DEFAULT_DB_PATH) -> FanLabDatabase:
    global _GLOBAL_DB
    if _GLOBAL_DB is None:
        _GLOBAL_DB = FanLabDatabase(db_path=db_path)
    return _GLOBAL_DB


def init_fanlab_db(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    db = get_db(db_path)
    return {
        "db_path": db.db_path,
        "json_mirror_path": db.json_mirror_path,
        "status": "READY",
        "table_counts": db.get_table_counts(),
    }
