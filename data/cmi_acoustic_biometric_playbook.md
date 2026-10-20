# Kinetic FanLab — CMI Acoustic & Biometric Telemetry Playbook
## 1. Mathematical Ground Truth Formula (0-100 CMI)
The Crowd Momentum Index (CMI) fuses four normalized sensor streams in real time:
- **Acoustic SPL (35% weight):** Normalized between `60.0 dB` (ambient) and `115.0 dB` (stadium roar).
- **Biometric Heart Rate (25% weight):** Normalized between `60.0 BPM` (resting) and `160.0 BPM` (elevated clutch stress).
- **Distraction Tap Cadence (20% weight):** Normalized between `0.0 taps/s` and `15.0 taps/s` with a `2.5s` exponential decay window.
- **IBM Granite Vocal Urgency (20% weight):** Normalized between `0.00 VU` and `1.00 VU` via event-gated semantic scoring.

## 2. Edge DSP Physics & Zero-Cloud-Cost Acoustic Processing
- **Logarithmic Decibel Summation:** Sound pressure is logarithmic ($L_{total} = 10 \log_{10}(\frac{1}{N}\sum 10^{L_i/10})$). Linear averaging undercounts collective crowd roars by 4 to 6 dB.
- **PA Speaker Bleed Attenuation:** When arena PA speakers are active, a `-3.5 dB` high-pass attenuation filter strips artificial announcer/music bleed so only authentic human crowd energy is credited.
- **Hampel Biometric Outlier Scrubbing:** Smartwatch optical PPG dropouts (`0.0 BPM`) and motion-artifact spikes (`> 205.0 BPM`) are scrubbed locally prior to aggregation.
- **50-Seat BLE Mesh Pod Compression:** 50 neighboring devices form a Bluetooth Low Energy (BLE) pod and compress 50 local telemetry packets into 1 uplink frame (`98.0%` cellular backhaul reduction). Raw audio is never recorded or transmitted to the cloud—only a 4-byte decibel float leaves the phone.
