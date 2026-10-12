"""
==============================================================================
Kinetic FanLab — Telemetry Signal Processing & Physical Acoustics Tests
Week 5 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Verifies:
1. Logarithmic decibel energy summation (vs faulty linear averages).
2. Biometric sensor detachment (0 BPM) and motion artifact (240 BPM) rejection.
3. Stadium PA speaker bleed attenuation isolating organic fan chants.
==============================================================================
"""

import os
import sys

# Ensure root directory is in Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telemetry_dsp import (
    calculate_logarithmic_decibels,
    filter_biometric_outliers,
    sanitize_pod_telemetry
)

def test_logarithmic_acoustics():
    print("\n🔊 TEST 1: Physical Acoustics vs Faulty Arithmetic Averaging")
    # In physics, two 80 dB sounds sum to ~83 dB, NOT 80 dB
    samples = [80.0, 80.0]
    log_spl = calculate_logarithmic_decibels(samples)
    print(f"  • Input Samples:         {samples} dB")
    print(f"  • Arithmetic Mean:       {sum(samples)/len(samples):.1f} dB (Incorrect)")
    print(f"  • Logarithmic Energy:    {log_spl:.1f} dB (Physical Ground Truth)")
    
    # Pod with 45 quiet fans (70 dB) and 5 screaming fans (105 dB)
    mixed_pod = [70.0] * 45 + [105.0] * 5
    arith_mean = sum(mixed_pod) / len(mixed_pod)
    log_energy = calculate_logarithmic_decibels(mixed_pod)
    print(f"  • Mixed Pod (45 @ 70dB, 5 @ 105dB):")
    print(f"    - Arithmetic Average:  {arith_mean:.1f} dB (severely undercounts screams)")
    print(f"    - Acoustic Log SPL:    {log_energy:.1f} dB (accurately captures roar)")
    
    assert log_energy > arith_mean + 15.0, "Acoustic physics failed to weight high energy spikes!"
    print("  ✅ Logarithmic sound pressure calculation verified.")

def test_biometric_outlier_rejection():
    print("\n❤️ TEST 2: Biometric Artifact & Sensor Detachment Rejection")
    # 20 normal cheering fans (130-145 BPM) with 2 detached sensors (0 BPM) and 1 extreme motion glitch (235 BPM)
    noisy_bpms = [135.0, 138.0, 140.0, 132.0, 142.0, 136.0, 139.0, 141.0] * 2 + [0.0, 0.0, 235.0]
    clean_bpms, dropped = filter_biometric_outliers(noisy_bpms)
    
    print(f"  • Raw Sensor Samples:    {len(noisy_bpms)} total (including 0.0 BPM and 235.0 BPM)")
    print(f"  • Cleaned Samples:       {len(clean_bpms)} valid fans")
    print(f"  • Rejected Artifacts:    {dropped} glitch spikes scrubbed")
    print(f"  • Resulting Pod Mean HR: {sum(clean_bpms)/len(clean_bpms):.1f} BPM")
    
    assert 0.0 not in clean_bpms, "Detached sensor 0 BPM leaked into clean dataset!"
    assert all(b <= 205.0 for b in clean_bpms), "Glitch spike > 205 BPM leaked!"
    assert dropped == 3, f"Expected 3 dropped artifacts, got {dropped}"
    print("  ✅ Biometric outlier filtering verified.")

def test_full_pod_dsp_pipeline():
    print("\n🏟️ TEST 3: 50-Seat Pod DSP Ingestion Pipeline")
    dbs = [104.0, 107.0, 109.0, 106.0] * 12 + [112.0, 114.0] # 50 seats
    bpms = [135.0, 138.0, 140.0] * 16 + [0.0, 225.0] # 50 seats with 2 glitches
    taps = [11.5, 12.0, 13.0] * 16 + [14.0, 18.0] # 18 taps/s should be capped at 15
    vus = [0.75, 0.82, 0.88, 0.92] * 12 + [0.95, 0.90]

    # Without PA speaker bleed
    clean_clean = sanitize_pod_telemetry(dbs, bpms, taps, vus, pa_speaker_active=False)
    # With PA speaker music bleed
    clean_pa = sanitize_pod_telemetry(dbs, bpms, taps, vus, pa_speaker_active=True)

    print(f"  • Pure Organic Fan dB:   {clean_clean['clean_db']} dB")
    print(f"  • PA-Attenuated Fan dB:  {clean_pa['clean_db']} dB (Attenuated -3.5 dB for stadium music)")
    print(f"  • Sanitized Pod BPM:     {clean_clean['clean_hr']} BPM ({clean_clean['rejected_biometric_artifacts']} artifacts removed)")
    print(f"  • Peak Pod Vocal Urgency:{clean_clean['clean_vu']} VU")

    assert clean_pa["clean_db"] < clean_clean["clean_db"]
    assert clean_clean["rejected_biometric_artifacts"] == 2
    print("  ✅ 50-Seat Pod DSP pipeline verified.")

if __name__ == "__main__":
    test_logarithmic_acoustics()
    test_biometric_outlier_rejection()
    test_full_pod_dsp_pipeline()
    print("\n================================================================================")
    print("✅ ALL TELEMETRY DSP & ACOUSTICS TESTS PASSED (100% OPERATIONAL)")
    print("================================================================================\n")