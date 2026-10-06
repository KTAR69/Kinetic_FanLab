# AGENTS.md — Kinetic FanLab (IBM Bob IDE Ground Truth)

## 1. Project & Environment Identity
- **Track**: Track #3 — Fan-Centric Sports & Entertainment
- **Program**: IBM SkillsBuild AI Experiential Learning Lab
- **Team**: Kinetic FanLab | **Team Lead**: Troy Resendez
- **Primary IDE & Scaffolding**: IBM Bob IDE (Autonomous Agentic Scaffolding)
- **Cloud Infrastructure**: IBM Cloud (`us-south` / Dallas region)
- **Foundation Models**: IBM watsonx.ai (`ibm/granite-4.0` / `ibm/granite-3-8b-instruct`)
- **Safety & Trust Layer**: IBM watsonx.governance (Content Auditing & Anonymization)
- **Multi-Agent Orchestration**: IBM watsonx Orchestrate ADK (v2.18.0)

---

## 2. Invariant Web3 Identity Registry (Static Member Hashes)
The unique member hash IDs below represent permanent 365-day Fan Passport identities. Under no circumstance should a member's hash fluctuate or recompute when switching fixtures, game phases, or operational states:

| Member Name | Sport & Section | Role & Tier | Permanent Unique Hash ID | Wearable Device Anchor |
| :--- | :--- | :--- | :--- | :--- |
| **Marcus Vance** | Basketball — Sec 114 | Section Director (Tier 4) | `0xMV-sec114-8f7a2` | Apple Watch Ultra 2 (ECG/dB) |
| **Elena Rostova** | Basketball — Sec 114 | Prop Captain (Tier 2) | `0xER-sec114-3c9b1` | Apple Watch Series 9 |
| **Devon Miller** | Basketball — Sec 114 | Vocal Tactician (Tier 3) | `0xDM-sec114-6d4e8` | WearOS Pixel Watch 2 |
| **Sarah Jenkins** | Football — Sec 115 | Stadium Veteran (Tier 5) | `0xSJ-sec115-7b2a5` | Garmin Fenix 7X (Stress/BPM) |
| **Carlos Mendez** | Football — Sec 115 | Tailgate Host (Tier 4) | `0xCM-sec115-4e8f9` | Samsung Galaxy Watch 6 Pro |
| **Maya Patel** | Football — Sec 115 | Tech Superfan (Tier 2) | `0xMP-sec115-1a5c3` | Apple Watch SE |

---

## 3. watsonx Orchestrate Multi-Agent Swarm (The 3 Archetypes)
The platform operationalizes the three official IBM Agentic AI Archetypes defined in Challenge Guide Appendix 1:

1. **The Invisible Coordinator (`InvisibleCoordinatorAgent`)**:
   - **Role**: Play-clock monitoring and synchronized crowd pacing conductor.
   - **Basketball**: Coordinates 10-second opponent free-throw routine (silent focus ➔ synchronized prop waving ➔ 106.5 dB peak scream on knee bend).
   - **Football**: Conducts multi-minute timeout delay pacing (rhythmic bleacher stomps to preserve vocal cords) surging to a 111.8 dB wall at 0:03 snap.
   - **Trigger**: Activates the **2.0x Clutch Multiplier** during defensive stands.

2. **The Knowledge Synthesizer (`KnowledgeSynthesizerAgent`)**:
   - **Role**: Multimodal sensory fusion and real-time state normalization.
   - **Ingestion**: Normalizes 4 noisy telemetry streams (Acoustics dB, Heart Rate BPM, App Taps, Vocal Urgency).
   - **Trust**: Filters toxic or profane rants through **watsonx.governance** before prompting **IBM Granite** for vocal urgency scoring (0.00–1.00 VU).
   - **Engine**: Computes the contract-exact Calculated Momentum Index (0–100 CMI).

3. **The System Optimizer (`SystemOptimizerAgent`)**:
   - **Role**: Ecosystem compounding and fairness enforcement.
   - **Per-Capita Standings**: Normalizes raw section scores by active checked-in fan volume, ensuring a section of 300 students can legitimately out-cheer 2,500 quiet club seats.
   - **Rivalry Engine**: Issues real-time Chaser Alerts (e.g., *Sec 115 is trailing by -2.1 pts!*) and awards the **Section Defense Belt**.
   - **Reality Delta**: Invokes IBM Granite to synthesize post-play broadcast narratives and one-tap social story cards.

---

## 4. Contract-Exact Mathematical Ground Truth

### Normalization Formula
```python
def normalize(val, min_v, max_v):
    return max(0.0, min(1.0, (val - min_v) / (max_v - min_v)))

cmi = round((
    normalize(db, 60.0, 115.0) * 0.35 +
    normalize(hr, 60.0, 160.0) * 0.25 +
    normalize(taps, 0.0, 15.0) * 0.20 +
    normalize(vu, 0.0, 1.0) * 0.20
) * 100, 1)