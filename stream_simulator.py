"""
Kinetic FanLab — Live Sensor Stream Simulator
Scaffolded via IBM Bob IDE (Track 3: Fan-Centric Sports & Entertainment)
Simulates background acoustic, wearable biometric, and tap telemetry ticks.
"""
import random
from typing import Dict, Any

class TelemetryStreamSimulator:
    def __init__(self, sport: str = "Basketball"):
        self.sport = sport

    def generate_live_tick(self, is_clutch: bool = False, noise_variance: float = 0.05) -> Dict[str, Any]:
        """Generate a simulated sensor telemetry tick with variance."""
        return self.get_next_tick(is_clutch=is_clutch)

    def get_next_tick(self, is_clutch: bool = False) -> Dict[str, Any]:
        if not is_clutch:
            # Baseline ambient state
            db = round(random.uniform(76.0, 83.0), 1)
            hr = round(random.uniform(92.0, 104.0), 1)
            taps = round(random.uniform(2.0, 3.8), 1)
            vu = round(random.uniform(0.50, 0.62), 2)
        else:
            # Clutch defensive pressure state
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

        # Compute CMI
        n_db = max(0.0, min(1.0, (db - 60.0) / (115.0 - 60.0)))
        n_hr = max(0.0, min(1.0, (hr - 60.0) / (160.0 - 60.0)))
        n_taps = max(0.0, min(1.0, (taps - 0.0) / (15.0 - 0.0)))
        n_vu = max(0.0, min(1.0, (vu - 0.0) / (1.0 - 0.0)))
        cmi = round((n_db * 0.35 + n_hr * 0.25 + n_taps * 0.20 + n_vu * 0.20) * 100, 1)
        tier = "Maximum" if cmi >= 80.0 else "High" if cmi >= 65.0 else "Moderate" if cmi >= 45.0 else "Baseline"

        return {
            "sport": self.sport,
            "is_clutch": is_clutch,
            "db": db,
            "hr": hr,
            "taps": taps,
            "vu": vu,
            "cmi": cmi,
            "tier": tier
        }
