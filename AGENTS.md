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

## 6. IBM Cloud Services & Orchestrate Skill Integration (Session 4)

### IBM Cloud Object Storage (COS) — Archival Architecture

`cloud_storage.py` provides a resilient, Pyright-clean COS module for archiving verified post-game records.

**Environment variables (set in `.env` or IBM Cloud Secrets Manager):**

| Variable | Description |
|---|---|
| `COS_APIKEY` | IBM Cloud IAM API key with Writer access to the bucket |
| `COS_RESOURCE_CRN` | CRN of the COS service instance |
| `COS_ENDPOINT` | Regional endpoint (e.g., `https://s3.us-south.cloud-object-storage.appdomain.cloud`) |
| `COS_BUCKET` | Target bucket name (default: `kinetic-fanlab-archive`) |

**Graceful fallback:** When credentials are absent or the SDK is unavailable, the module operates in **local mock mode**, writing JSON files to `cloud_storage_archive/` and returning `status: "ARCHIVED_LOCALLY (Simulated IBM COS)"`.

**Bucket object schema (two record types):**

_Crowd Box Score_ — `crowd_box_scores/{sport}/{fixture_id}_{timestamp}.json`:
```json
{
  "schema_version": "1.0",
  "record_type": "crowd_box_score",
  "fixture_id": "BB-02",
  "sport": "Basketball",
  "calculated_momentum_index": 81.9,
  "momentum_surge_pts": 44.1,
  "winning_section": "Section 114 (Thunder Row)",
  "fan_contribution": { "tap_count": 12, "peak_hr_bpm": 136, "peak_db": 106.5, "vocal_urgency": 0.85, "fan_notes": [] },
  "crypto_timestamp": "2025-07-14T18:30:00Z#a1b2c3d4",
  "powered_by": "IBM watsonx & Granite Foundation Models"
}
```

_Proof-of-Momentum Card_ — `proof_of_momentum/{sport}/{fixture_id}_{timestamp}.json`:
```json
{
  "schema_version": "1.0",
  "record_type": "proof_of_momentum_card",
  "fixture_id": "FB-02",
  "sport": "Football",
  "points_display": "+53.0 PTS",
  "outcome": "MISSED FIELD GOAL (Wide Left - Ice Successful)",
  "granite_narrative": "111.8 dB sustained roar across 148 BPM cardiac stress disrupted kicker cadence.",
  "crypto_timestamp": "2025-07-14T18:31:00Z#e5f6a7b8",
  "powered_by": "IBM watsonx & Granite Foundation Models"
}
```

---

### IBM Cloudant NoSQL — Fan Passport Document Schema

`cloudant_db.py` persists the 8 member Fan Passports in the `kinetic-fan-passports` database.

**Environment variables:**

| Variable | Description |
|---|---|
| `CLOUDANT_APIKEY` | IBM Cloud IAM API key with Reader/Writer access to Cloudant |
| `CLOUDANT_URL` | Cloudant service URL (e.g., `https://<account>.cloudantnosqldb.appdomain.cloud`) |

**Graceful fallback:** When credentials are absent, the module uses `cloudant_cache.json` (local JSON) so respect taps and accolades persist across app reloads without any crash.

**Cloudant document schema per member:**
```json
{
  "_id": "Marcus Vance",
  "member_hash": "0xMV-sec114-8f7a2",
  "respect_taps": 314,
  "nft_badges_unlocked": []
}
```

**Immutable member hash table (never change):**

| Member | Invariant Hash |
|---|---|
| Marcus Vance | `0xMV-sec114-8f7a2` |
| Elena Rostova | `0xER-sec114-3c9b1` |
| Devon Miller | `0xDM-sec114-6d4e8` |
| Jordan Lee | `0xJL-sec114-1f4a9` |
| Sarah Jenkins | `0xSJ-sec115-7b2a5` |
| Carlos Mendez | `0xCM-sec115-4e8f9` |
| Maya Patel | `0xMP-sec115-1a5c3` |
| Alex Taylor | `0xAT-sec115-5c2d3` |

**Public API:**
- `load_member_passport(member_name)` → full passport `dict`
- `save_member_passport(member_name, updated_data)` → `bool` (enforces immutable hash)
- `increment_respect_tap(member_name, count=1)` → new `int` total

---

### OpenAPI 3.0 Skill Registration Manifest — `kinetic_fanlab_skill.json`

**Title:** Kinetic FanLab Telemetry & Momentum Engine  
**Version:** 1.0.0  
**Security:** IBM Cloud IAM Bearer Token  
**Base URL:** `https://kineticfanlab.ibm.com/api/v1`

Endpoints registered for IBM watsonx Orchestrate skill discovery:

| Endpoint | Method | Operation ID | Purpose |
|---|---|---|---|
| `/calculate_cmi` | POST | `calculateCmi` | Fuse dB + BPM + tap rate + vocal urgency → CMI (0–100) + tier |
| `/evaluate_pacing` | POST | `evaluatePacing` | Return InvisibleCoordinator directive, clutch multiplier, tactic |
| `/generate_narrative` | POST | `generateNarrative` | IBM Granite post-play reality delta narrative with live telemetry values |

All endpoints accept and return `application/json`. Error responses follow the `ErrorResponse` schema `{ "error": string, "message": string }`.

To register this skill in watsonx Orchestrate:
```bash
orchestrate skills import --file kinetic_fanlab_skill.json --kind openapi
```
