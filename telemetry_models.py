import time
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# --- Enums for Grounded Sports Domains ---

class SportType(str, Enum):
    BASKETBALL = "Basketball"
    FOOTBALL = "Football"

class FanRole(str, Enum):
    SIXTH_MAN = "6th Man (Basketball)"
    TWELFTH_MAN = "12th Man (Football)"

class OperationalTier(str, Enum):
    BASELINE = "Baseline"
    MODERATE = "Moderate"
    HIGH = "High"
    MAXIMUM = "Maximum"

class DisruptionTactic(str, Enum):
    OPTICAL_DEPTH_DISRUPTION = "Synchronized Prop Waving (Visual Depth Perception)"
    CADENCE_ACOUSTIC_WALL = "High-Decibel Cadence Drowning (False Start Induction)"
    TIMEOUT_STAMINA_PACING = "Bleacher Stomp Endurance Pacing (Kicker Icing Delay)"
    HIGH_FREQ_PIERCING_SCREAM = "High-Frequency Acoustic Piercing (Motor Stroke Interruption)"

# --- Persona & Identity Registry (Permanent Invariant Hashes) ---

PERSONA_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Marcus Vance": {
        "hash": "0xMV-sec114-8f7a2",
        "sport": SportType.BASKETBALL,
        "section": "Section 114 (Thunder Row)",
        "seat": "Row 1, Seat 1",
        "role": "Student Section Director",
        "tier": "Section Director (Tier 4)",
        "career_games": 34,
        "career_db": "3,820 dB",
        "clutch_stops": 23,
        "respect_taps": 312,
        "wearable": "Apple Watch Ultra 2 (Acoustic + ECG)",
        "neighbors": ["Elena Rostova", "Devon Miller"],
        "accolades": [
            {
                "title": "Thunder Row Legend",
                "rarity": "Legendary",
                "glow_color": "#da1e28",
                "description": "Awarded to the Section 114 conductor who has led 20+ verified clutch free-throw defensive stops.",
                "perks": ["Post-Game Press Pass", "Seat Upgrade Lottery Entry", "VIP Locker Room Tour"]
            },
            {
                "title": "34-Game Iron Streak",
                "rarity": "Epic",
                "glow_color": "#f1c21b",
                "description": "Consecutive 34-game attendance streak without a single absence. Unbreakable dedication.",
                "perks": ["5% Concession Discount", "Priority Queue Arena Entry", "Exclusive Section Director Jersey"]
            }
        ]
    },
    "Elena Rostova": {
        "hash": "0xER-sec114-3c9b1",
        "sport": SportType.BASKETBALL,
        "section": "Section 114 (Thunder Row)",
        "seat": "Row 2, Seat 4",
        "role": "Hype & Prop Captain",
        "tier": "Prop Captain (Tier 2)",
        "career_games": 14,
        "career_db": "1,580 dB",
        "clutch_stops": 9,
        "respect_taps": 168,
        "wearable": "Apple Watch Series 9",
        "neighbors": ["Marcus Vance", "Devon Miller"],
        "accolades": [
            {
                "title": "Thunderstick Maestro",
                "rarity": "Rare",
                "glow_color": "#8a3ffc",
                "description": "Coordinated synchronized thunderstick waves across 50+ fans during a critical free throw sequence.",
                "perks": ["5% Concession Discount", "Free Thunderstick Kit (Season)", "Section Hype Reel Feature"]
            },
            {
                "title": "9-Stop Prop Specialist",
                "rarity": "Rare",
                "glow_color": "#8a3ffc",
                "description": "Credited with visual depth-perception disruption on 9 verified opponent missed free throws.",
                "perks": ["Seat Upgrade Lottery Entry", "Arena Prop Storage Locker Access"]
            }
        ]
    },
    "Devon Miller": {
        "hash": "0xDM-sec114-6d4e8",
        "sport": SportType.BASKETBALL,
        "section": "Section 114 (Thunder Row)",
        "seat": "Row 3, Seat 8",
        "role": "Vocal Tactician",
        "tier": "Vocal Tactician (Tier 3)",
        "career_games": 28,
        "career_db": "3,140 dB",
        "clutch_stops": 19,
        "respect_taps": 245,
        "wearable": "WearOS Pixel Watch 2",
        "neighbors": ["Marcus Vance", "Elena Rostova"],
        "accolades": [
            {
                "title": "Chant Architect",
                "rarity": "Epic",
                "glow_color": "#f1c21b",
                "description": "Originated 3 official section chants now used across all 6th Man defensive possessions.",
                "perks": ["Post-Game Press Pass", "5% Concession Discount", "Chant Archive Feature Credit"]
            },
            {
                "title": "19-Stop Voice Log",
                "rarity": "Rare",
                "glow_color": "#8a3ffc",
                "description": "Maintained a high-frequency vocal urgency score above 0.80 across 19 clutch free-throw stops.",
                "perks": ["Seat Upgrade Lottery Entry", "Section Vocal Tactician Badge"]
            }
        ]
    },
    "Jordan Lee": {
        "hash": "0xJL-sec114-1f4a9",
        "sport": SportType.BASKETBALL,
        "section": "Section 114 (Thunder Row)",
        "seat": "Row 4, Seat 11",
        "role": "Rookie Section Member",
        "tier": "Tier 1",
        "career_games": 3,
        "career_db": "310 dB",
        "clutch_stops": 1,
        "respect_taps": 28,
        "wearable": "Apple Watch SE",
        "neighbors": ["Marcus Vance", "Elena Rostova"],
        "accolades": [
            {
                "title": "First Roar Badge",
                "rarity": "Common",
                "glow_color": "#0f62fe",
                "description": "Awarded after attending your first Section 114 game and contributing to a crowd surge moment.",
                "perks": ["5% Concession Discount", "Rookie Welcome Kit"]
            },
            {
                "title": "Rookie Rising",
                "rarity": "Common",
                "glow_color": "#0f62fe",
                "description": "Progress milestone: Attend 10 games and unlock Tier 2 Prop Specialist status. 7 games remaining.",
                "perks": ["Tier 2 Unlock at 10 Games — Thunderstick Kit + Priority Queue Entry"]
            }
        ]
    },
    "Sarah Jenkins": {
        "hash": "0xSJ-sec115-7b2a5",
        "sport": SportType.FOOTBALL,
        "section": "Section 115 (End Zone Loyals)",
        "seat": "Row 18, Seat 10",
        "role": "10-Year Season Ticket Holder",
        "tier": "Stadium Veteran (Tier 5)",
        "career_games": 62,
        "career_db": "6,850 dB",
        "clutch_stops": 31,
        "respect_taps": 480,
        "wearable": "Garmin Fenix 7X (Cardiac Stress + Altimeter)",
        "neighbors": ["Carlos Mendez", "Maya Patel"],
        "accolades": [
            {
                "title": "End Zone Loyals Hall of Fame",
                "rarity": "Legendary",
                "glow_color": "#da1e28",
                "description": "10-year consecutive season ticket holder. The heartbeat of Section 115 on every 3rd down and redzone stand.",
                "perks": ["Post-Game Press Pass", "VIP Locker Room Tour", "Permanent Section Plaque Recognition"]
            },
            {
                "title": "62-Game Ironclad",
                "rarity": "Legendary",
                "glow_color": "#da1e28",
                "description": "62 verified stadium appearances — the longest active attendance streak in Section 115 history.",
                "perks": ["Lifetime 10% Concession Discount", "Priority Suite Access Lottery", "Stadium Veteran Commemorative Jersey"]
            }
        ]
    },
    "Carlos Mendez": {
        "hash": "0xCM-sec115-4e8f9",
        "sport": SportType.FOOTBALL,
        "section": "Section 115 (End Zone Loyals)",
        "seat": "Row 18, Seat 12",
        "role": "Lot B Tailgate Host",
        "tier": "Tailgate Host (Tier 4)",
        "career_games": 45,
        "career_db": "4,920 dB",
        "clutch_stops": 24,
        "respect_taps": 395,
        "wearable": "Samsung Galaxy Watch 6 Pro",
        "neighbors": ["Sarah Jenkins", "Maya Patel"],
        "accolades": [
            {
                "title": "Lot B Legend",
                "rarity": "Epic",
                "glow_color": "#f1c21b",
                "description": "Hosted 30+ pre-game tailgates that drove Section 115 early check-in rates above 85%.",
                "perks": ["Post-Game Press Pass", "5% Concession Discount", "Lot B Permanent Reserved Spot"]
            },
            {
                "title": "Community Anchor",
                "rarity": "Rare",
                "glow_color": "#8a3ffc",
                "description": "Personally welcomed 50+ first-time Section 115 members at the Lot B tailgate tradition.",
                "perks": ["Seat Upgrade Lottery Entry", "Exclusive Tailgate Host Plaque"]
            }
        ]
    },
    "Maya Patel": {
        "hash": "0xMP-sec115-1a5c3",
        "sport": SportType.FOOTBALL,
        "section": "Section 115 (End Zone Loyals)",
        "seat": "Row 19, Seat 14",
        "role": "Biometric & Tech Superfan",
        "tier": "Tech Superfan (Tier 2)",
        "career_games": 18,
        "career_db": "1,940 dB",
        "clutch_stops": 11,
        "respect_taps": 185,
        "wearable": "Apple Watch SE",
        "neighbors": ["Sarah Jenkins", "Carlos Mendez"],
        "accolades": [
            {
                "title": "Data Pulse Pioneer",
                "rarity": "Rare",
                "glow_color": "#8a3ffc",
                "description": "Logged the highest wearable biometric data accuracy rate across 11 clutch kicker icing moments.",
                "perks": ["5% Concession Discount", "Tech Superfan Exclusive App Features"]
            },
            {
                "title": "Wearable Ambassador",
                "rarity": "Common",
                "glow_color": "#0f62fe",
                "description": "Onboarded 8 Section 115 members to the Kinetic FanLab wearable program.",
                "perks": ["Seat Upgrade Lottery Entry", "Section Tech Lead Recognition"]
            }
        ]
    },
    "Alex Taylor": {
        "hash": "0xAT-sec115-5c2d3",
        "sport": SportType.FOOTBALL,
        "section": "Section 115 (End Zone Loyals)",
        "seat": "Row 20, Seat 3",
        "role": "General Season Ticket Holder",
        "tier": "Tier 1",
        "career_games": 4,
        "career_db": "420 dB",
        "clutch_stops": 2,
        "respect_taps": 45,
        "wearable": "Pixel Watch",
        "neighbors": ["Sarah Jenkins", "Carlos Mendez"],
        "accolades": [
            {
                "title": "End Zone Initiate",
                "rarity": "Common",
                "glow_color": "#0f62fe",
                "description": "Awarded after your first season ticket activation and verified check-in at Section 115.",
                "perks": ["5% Concession Discount", "Section 115 Welcome Pack"]
            },
            {
                "title": "Rookie Rising",
                "rarity": "Common",
                "glow_color": "#0f62fe",
                "description": "Progress milestone: Attend 10 games and unlock Tier 2 Tailgate Crew status. 6 games remaining.",
                "perks": ["Tier 2 Unlock at 10 Games — Lot B Reserved Tailgate Spot + Priority Entry"]
            }
        ]
    }
}

# --- Canonical Benchmark Fixtures (Contract Ground Truth) ---

CANONICAL_FIXTURES: Dict[str, Dict[str, Any]] = {
    "BB-01": {
        "id": "BB-01",
        "name": "Basketball Baseline (Free Throw 1)",
        "sport": SportType.BASKETBALL,
        "is_clutch": False,
        "cmi_target": 37.8,
        "tier": OperationalTier.BASELINE,
        "acoustics": {"db": 82.0, "dominant_hz": 420.0, "status": "Ambient Arena Murmur"},
        "biometrics": {"hr_bpm": 98.0, "stress_index": 0.42, "status": "Resting Anticipation"},
        "taps": {"rate_per_sec": 2.5, "burst_count": 6},
        "voice": {"urgency": 0.55, "sample": "Watch the shooter, need this stop", "status": "APPROVED"},
        "section_leader": "Section 114 (Thunder Row)",
        "game_situation": "Opponent Free Throw 1 of 2 (Regular possession flow)"
    },
    "BB-02": {
        "id": "BB-02",
        "name": "Basketball Clutch (Free Throw 2)",
        "sport": SportType.BASKETBALL,
        "is_clutch": True,
        "cmi_target": 81.9,
        "tier": OperationalTier.MAXIMUM,
        "acoustics": {"db": 106.5, "dominant_hz": 2400.0, "status": "High-Frequency Piercing Roar"},
        "biometrics": {"hr_bpm": 136.0, "stress_index": 0.88, "status": "Clutch Adrenaline Spike"},
        "taps": {"rate_per_sec": 12.2, "burst_count": 32},
        "voice": {"urgency": 0.85, "sample": "MISS IT! OFF THE RIM! BRING THE NOISE!", "status": "APPROVED"},
        "section_leader": "Section 114 (Thunder Row)",
        "game_situation": "Opponent Free Throw 2 of 2 (Late Game 1-and-1, 0:08 Remaining)"
    },
    "FB-01": {
        "id": "FB-01",
        "name": "Football Pre-Kick Timeout",
        "sport": SportType.FOOTBALL,
        "is_clutch": False,
        "cmi_target": 39.0,
        "tier": OperationalTier.BASELINE,
        "acoustics": {"db": 78.5, "dominant_hz": 95.0, "status": "Low-Frequency Bleacher Rumble"},
        "biometrics": {"hr_bpm": 105.0, "stress_index": 0.48, "status": "Timeout Delay Lull"},
        "taps": {"rate_per_sec": 3.0, "burst_count": 8},
        "voice": {"urgency": 0.60, "sample": "Timeout called, make him wait in the cold!", "status": "APPROVED"},
        "section_leader": "Section 115 (End Zone Loyals)",
        "game_situation": "4th Quarter 0:03 Timeout Called by Defense ('Icing the Kicker')"
    },
    "FB-02": {
        "id": "FB-02",
        "name": "Football 48-Yard FG Snap (Clutch)",
        "sport": SportType.FOOTBALL,
        "is_clutch": True,
        "cmi_target": 92.0,
        "tier": OperationalTier.MAXIMUM,
        "acoustics": {"db": 111.8, "dominant_hz": 85.0, "status": "Full Stadium Acoustic Wall"},
        "biometrics": {"hr_bpm": 148.0, "stress_index": 0.95, "status": "Peak Physiological Arousal"},
        "taps": {"rate_per_sec": 14.0, "burst_count": 48},
        "voice": {"urgency": 0.92, "sample": "BLOCK THAT KICK! RATTLE THE KICKER! GET LOUD!", "status": "APPROVED"},
        "section_leader": "Section 115 (End Zone Loyals)",
        "game_situation": "48-Yard Game-Winning Field Goal Snap as Game Clock Hits 0:00"
    }
}

# --- Telemetry Data Classes ---

@dataclass
class AcousticSensorPacket:
    sensor_id: str
    section_id: str
    sport: SportType
    decibels: float
    dominant_frequency_hz: float
    reverberation_decay_ms: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class WearableBiometricPacket:
    user_id: str
    section_id: str
    member_hash: str
    device_model: str
    heart_rate_bpm: float
    stress_index: float
    hrv_rmssd_ms: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class DistractionTapPacket:
    user_id: str
    section_id: str
    member_hash: str
    tap_count: int
    active_rate_per_sec: float
    burst_duration_sec: float
    timestamp: float = field(default_factory=time.time)

@dataclass
class VocalOutburstPacket:
    user_id: str
    section_id: str
    member_hash: str
    transcript: str
    watsonx_vocal_urgency: float
    governance_status: str
    flagged_terms: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

@dataclass
class SectionRosterState:
    section_id: str
    section_name: str
    sport: SportType
    total_physical_seats: int
    checked_in_fans: int
    early_checkin_multiplier: float = 1.0
    clutch_multiplier: float = 1.0

    @property
    def checkin_percentage(self) -> float:
        return round((self.checked_in_fans / max(1, self.total_physical_seats)) * 100, 1)

@dataclass
class SectionTelemetrySnapshot:
    section: SectionRosterState
    avg_decibels: float
    avg_heart_rate: float
    avg_tap_rate: float
    avg_vocal_urgency: float
    raw_cmi: float
    normalized_per_capita_score: float
    tier: OperationalTier
    tactic_active: DisruptionTactic
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section.section_id,
            "section_name": self.section.section_name,
            "sport": self.section.sport.value,
            "checked_in_fans": self.section.checked_in_fans,
            "checkin_pct": f"{self.section.checkin_percentage}%",
            "avg_db": self.avg_decibels,
            "avg_hr": self.avg_heart_rate,
            "avg_taps": self.avg_tap_rate,
            "avg_vu": self.avg_vocal_urgency,
            "cmi": self.raw_cmi,
            "per_capita_score": self.normalized_per_capita_score,
            "tier": self.tier.value,
            "tactic": self.tactic_active.value,
            "timestamp": self.timestamp
        }
