import time
import math
import random
from typing import Dict, Any, List

class TelemetryStreamSimulator:
    def __init__(self, sport: str = "Basketball"):
        self.sport = sport.capitalize()
        self.tick_counter = 0

    def get_canonical_benchmark(self, fixture_id: str) -> Dict[str, Any]:
        benchmarks = {
            "BB-01": {
                "id": "BB-01",
                "sport": "Basketball",
                "name": "Basketball Baseline (Free Throw 1)",
                "is_clutch": False,
                "db": 82.0,
                "hr": 98.0,
                "taps": 2.5,
                "vu": 0.55,
                "cmi": 37.8,
                "tier": "Baseline",
                "disruption_tactic": "Ambient Defensive Attention",
                "notes": ["Watch the shooter, need this stop"]
            },
            "BB-02": {
                "id": "BB-02",
                "sport": "Basketball",
                "name": "Basketball Clutch (Free Throw 2)",
                "is_clutch": True,
                "db": 106.5,
                "hr": 136.0,
                "taps": 12.2,
                "vu": 0.85,
                "cmi": 81.9,
                "tier": "Maximum",
                "disruption_tactic": "Synchronized Visual Waving & Piercing Scream",
                "notes": ["MISS IT! OFF THE RIM! BRING THE NOISE!"]
            },
            "FB-01": {
                "id": "FB-01",
                "sport": "Football",
                "name": "Football Pre-Kick Timeout",
                "is_clutch": False,
                "db": 78.5,
                "hr": 105.0,
                "taps": 3.0,
                "vu": 0.60,
                "cmi": 39.0,
                "tier": "Baseline",
                "disruption_tactic": "Bleacher Stomp Endurance Pacing",
                "notes": ["Timeout called, make him wait in the cold!"]
            },
            "FB-02": {
                "id": "FB-02",
                "sport": "Football",
                "name": "Football 48-Yard FG Snap (Clutch)",
                "is_clutch": True,
                "db": 111.8,
                "hr": 148.0,
                "taps": 14.0,
                "vu": 0.92,
                "cmi": 92.0,
                "tier": "Maximum",
                "disruption_tactic": "111+ dB Full Stadium Acoustic Wall",
                "notes": ["BLOCK THAT KICK! RATTLE THE KICKER! GET LOUD!"]
            }
        }
        return benchmarks.get(fixture_id, benchmarks["BB-01"])

    def generate_live_tick(self, is_clutch: bool = False, noise_variance: float = 0.05) -> Dict[str, Any]:
        self.tick_counter += 1
        is_basketball = "basket" in self.sport.lower()

        if not is_clutch:
            target_db = 82.0 if is_basketball else 78.5
            target_hr = 98.0 if is_basketball else 105.0
            target_taps = 2.5 if is_basketball else 3.0
            target_vu = 0.55 if is_basketball else 0.60
            tactic = "Ambient Section Alertness"
        else:
            target_db = 106.5 if is_basketball else 111.8
            target_hr = 136.0 if is_basketball else 148.0
            target_taps = 12.2 if is_basketball else 14.0
            target_vu = 0.85 if is_basketball else 0.92
            tactic = "Visual Waving & Piercing Roar" if is_basketball else "111 dB Bleacher Acoustic Wall"

        drift = math.sin(self.tick_counter * 0.4) * noise_variance
        live_db = round(target_db + (drift * 2.0) + random.uniform(-0.4, 0.4), 1)
        live_hr = round(target_hr + (drift * 3.0) + random.uniform(-1.0, 1.0), 1)
        live_taps = round(max(0.0, target_taps + (drift * 1.5) + random.uniform(-0.3, 0.3)), 1)
        live_vu = round(min(1.0, max(0.0, target_vu + (drift * 0.05) + random.uniform(-0.02, 0.02))), 2)

        n_db = max(0.0, min(1.0, (live_db - 60.0) / (115.0 - 60.0)))
        n_hr = max(0.0, min(1.0, (live_hr - 60.0) / (160.0 - 60.0)))
        n_taps = max(0.0, min(1.0, (live_taps - 0.0) / (15.0 - 0.0)))
        n_vu = max(0.0, min(1.0, (live_vu - 0.0) / (1.0 - 0.0)))
        live_cmi = round((n_db * 0.35 + n_hr * 0.25 + n_taps * 0.20 + n_vu * 0.20) * 100, 1)

        tier = "Maximum" if live_cmi >= 80.0 else "High" if live_cmi >= 65.0 else "Moderate" if live_cmi >= 45.0 else "Baseline"

        return {
            "sport": self.sport,
            "is_clutch": is_clutch,
            "tick": self.tick_counter,
            "db": live_db,
            "hr": live_hr,
            "taps": live_taps,
            "vu": live_vu,
            "cmi": live_cmi,
            "tier": tier,
            "tactic": tactic,
            "timestamp": time.time()
        }