"""
==============================================================================
Kinetic FanLab — Telemetry Digital Signal Processing (DSP) Engine
Week 5 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Implements physical acoustics and biometric sanitization:
1. Logarithmic sound pressure level (SPL) acoustic summation.
2. Biometric outlier rejection (Hampel/rolling filter for sensor detachment).
3. Venue PA speaker frequency attenuation to isolate organic crowd chants.
==============================================================================
"""

import math
import statistics
from typing import Dict, Any, List, Tuple

# Biometric human physical bounds for cheering sports fans
BPM_MIN_PHYSIOLOGICAL = 50.0   # Below this is sensor drop/detachment
BPM_MAX_PHYSIOLOGICAL = 205.0  # Above this is motion artifact spike

def filter_biometric_outliers(bpm_samples: List[float]) -> Tuple[List[float], int]:
    """
    Sanitizes raw smartwatch heart rate samples:
    - Rejects physiological impossibilities (< 50 BPM or > 205 BPM).
    - Uses median absolute deviation (MAD) to filter motion artifact spikes.
    Returns (clean_samples, rejected_count).
    """
    if not bpm_samples:
        return [95.0], 0

    # 1. Hard physiological filter
    physio_clean = [b for b in bpm_samples if BPM_MIN_PHYSIOLOGICAL <= b <= BPM_MAX_PHYSIOLOGICAL]
    rejected_count = len(bpm_samples) - len(physio_clean)

    if not physio_clean:
        return [95.0], len(bpm_samples)

    if len(physio_clean) < 4:
        return physio_clean, rejected_count

    # 2. Hampel / Median Absolute Deviation (MAD) filter
    med = statistics.median(physio_clean)
    abs_deviations = [abs(x - med) for x in physio_clean]
    mad = statistics.median(abs_deviations)

    if mad == 0.0:
        return physio_clean, rejected_count

    threshold = 3.0 * mad
    hampel_clean = [x for x in physio_clean if abs(x - med) <= threshold]
    rejected_count += (len(physio_clean) - len(hampel_clean))

    return hampel_clean if hampel_clean else [med], rejected_count


def calculate_logarithmic_decibels(db_samples: List[float], pa_bleed_attenuation_db: float = 0.0) -> float:
    """
    Calculates true acoustic Sound Pressure Level (SPL) using logarithmic energy summation.
    db_samples: list of individual mic decibel readings (e.g. 50 seats in a pod).
    pa_bleed_attenuation_db: decibels subtracted when venue PA speaker music is detected.
    """
    if not db_samples:
        return 75.0

    # Linear acoustic energy: E = 10^(dB / 10)
    linear_energies = [10.0 ** (d / 10.0) for d in db_samples]
    mean_energy = sum(linear_energies) / len(linear_energies)

    # Convert back to logarithmic SPL
    spl = 10.0 * math.log10(max(1.0, mean_energy))

    # Apply canned speaker PA bleed attenuation if detected
    isolated_fan_spl = max(55.0, spl - pa_bleed_attenuation_db)
    return round(isolated_fan_spl, 1)


def sanitize_pod_telemetry(
    raw_dbs: List[float],
    raw_bpms: List[float],
    raw_taps: List[float],
    raw_vus: List[float],
    pa_speaker_active: bool = False
) -> Dict[str, Any]:
    """
    Full DSP pipeline for a 50-seat pod cluster head:
    Combines acoustic logarithmic math, biometric outlier scrubbing, and PA attenuation.
    """
    # 1. Acoustic filtering (attenuates 3.5 dB if stadium PA music is active)
    pa_attenuation = 3.5 if pa_speaker_active else 0.0
    clean_db = calculate_logarithmic_decibels(raw_dbs, pa_bleed_attenuation_db=pa_attenuation)

    # 2. Biometric sanitization
    clean_bpms, dropped_bpm_count = filter_biometric_outliers(raw_bpms)
    mean_hr = round(statistics.mean(clean_bpms), 1)

    # 3. Tapping rate (capped at physical human limit of 15.0 taps/s)
    clean_taps = [max(0.0, min(15.0, t)) for t in raw_taps]
    mean_taps = round(statistics.mean(clean_taps), 1)

    # 4. Vocal urgency peak
    clean_vus = [max(0.0, min(1.0, v)) for v in raw_vus]
    peak_vu = round(max(clean_vus) if clean_vus else 0.50, 2)

    return {
        "clean_db": clean_db,
        "clean_hr": mean_hr,
        "clean_taps": mean_taps,
        "clean_vu": peak_vu,
        "rejected_biometric_artifacts": dropped_bpm_count,
        "pa_bleed_applied": pa_speaker_active
    }