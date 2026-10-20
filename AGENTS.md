# AGENTS.md — Kinetic FanLab (IBM Bob IDE Ground Truth — Weeks 1–6 Complete)

## 1. Project & Environment Identity
- **Track**: Track #3 — Fan-Centric Sports & Entertainment
- **Program**: IBM SkillsBuild AI Experiential Learning Lab
- **Team**: Kinetic FanLab | **Team Lead**: Troy Resendez
- **Team Composition**: Troy Resendez (Team Lead), IBM Bob IDE (Autonomous Agentic Scaffolding), and Gemini (Enterprise Architecture, FinOps & Multi-Agent Co-Architect)
- **Primary IDE & Scaffolding**: IBM Bob IDE (Autonomous Agentic Scaffolding)
- **Cloud Infrastructure**: IBM Cloud (`us-south` / Dallas region)
- **Foundation Models**: IBM watsonx.ai (`ibm/granite-4.0` / `ibm/granite-3-8b-instruct`)
- **Safety & Trust Layer**: IBM watsonx.governance (Content Auditing, Prompt-Injection Shield & Dialect Fairness `DIR = 0.953`)
- **Multi-Agent Orchestration**: IBM watsonx Orchestrate ADK (v2.18.0 — 16-Agent Theatre Production Cast)

---

## 2. Invariant Web3 Identity Registry (Static Member Hashes)
The unique member hash IDs below represent permanent 365-day Fan Passport identities. Under no circumstance should a member's hash fluctuate or recompute when switching fixtures, game phases, or operational states:

| Member Name | Sport & Section | Role & Tier | Permanent Unique Hash ID | Wearable Device Anchor |
| :--- | :--- | :--- | :--- | :--- |
| **Marcus Vance** | Basketball — Sec 114 | Section Director (Tier 4) | `0xMV-sec114-8f7a2` | Apple Watch Ultra 2 (ECG/dB) |
| **Elena Rostova** | Basketball — Sec 114 | Prop Captain (Tier 2) | `0xER-sec114-3c9b1` | Apple Watch Series 9 |
| **Devon Miller** | Basketball — Sec 114 | Vocal Tactician (Tier 3) | `0xDM-sec114-6d4e8` | WearOS Pixel Watch 2 |
| **Jordan Lee** | Basketball — Sec 114 | Rookie Member (Tier 1) | `0xJL-sec114-1f4a9` | Apple Watch SE (2nd Gen) |
| **Sarah Jenkins** | Football — Sec 115 | Stadium Veteran (Tier 5) | `0xSJ-sec115-7b2a5` | Garmin Fenix 7X (Stress/BPM) |
| **Carlos Mendez** | Football — Sec 115 | Tailgate Host (Tier 4) | `0xCM-sec115-4e8f9` | Samsung Galaxy Watch 6 Pro |
| **Maya Patel** | Football — Sec 115 | Tech Superfan (Tier 2) | `0xMP-sec115-1a5c3` | Apple Watch SE |
| **Alex Taylor** | Football — Sec 115 | General Member (Tier 1) | `0xAT-sec115-5c2d3` | Fitbit Charge 6 |

---

## 3. watsonx Orchestrate Multi-Agent Swarm (The 3 Core Archetypes + Fan Coach)
The platform operationalizes the three official IBM Agentic AI Archetypes defined in Challenge Guide Appendix 1 (plus the Fan Progression Coach on Screen 3):

1. **The Invisible Coordinator (`InvisibleCoordinatorAgent` / `coordinator_agent.yaml` — *The Conductor*)**:
   - **Role**: Play-clock monitoring and synchronized crowd pacing conductor.
   - **Basketball**: Coordinates 10-second opponent free-throw routine (silent focus ➔ synchronized prop waving ➔ 106.5 dB peak scream on knee bend).
   - **Football**: Conducts multi-minute timeout delay pacing (rhythmic bleacher stomps to preserve vocal cords) surging to a 111.8 dB wall at 0:03 snap.
   - **Trigger**: Activates the **2.0x Clutch Multiplier** during defensive stands.

2. **The Knowledge Synthesizer (`KnowledgeSynthesizerAgent` / `synthesizer_agent.yaml` — *The Scout*)**:
   - **Role**: Multimodal sensory fusion and real-time state normalization.
   - **Ingestion**: Normalizes 4 noisy telemetry streams (Acoustics dB, Heart Rate BPM, App Taps, Vocal Urgency).
   - **Trust**: Filters toxic or profane rants through **watsonx.governance** before prompting **IBM Granite** for vocal urgency scoring (0.00–1.00 VU).
   - **Engine**: Computes the contract-exact Calculated Momentum Index (0–100 CMI).

3. **The System Optimizer (`SystemOptimizerAgent` / `optimizer_agent.yaml` — *The Strategist*)**:
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
```

### Canonical Invariant Fixtures
| Fixture ID | Sport | Game Situation | Decibels | Heart Rate | Taps/s | Vocal Urgency | Target CMI | Operational Tier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`BB-01`** | Basketball | Opponent Free Throw 1 (Baseline) | `82.0 dB` | `98.0 BPM` | `2.5` | `0.55 VU` | **`37.8`** | Baseline Tier |
| **`BB-02`** | Basketball | Opponent Free Throw 2 (Clutch) | `106.5 dB` | `136.0 BPM` | `12.2` | `0.85 VU` | **`81.9`** | Maximum Tier (`+44.1` pt surge) |
| **`FB-01`** | Football | Pre-Kick Timeout ("Icing") | `78.5 dB` | `105.0 BPM` | `3.0` | `0.60 VU` | **`39.0`** | Baseline Tier |
| **`FB-02`** | Football | 48-Yard Field Goal Snap (Clutch) | `111.8 dB` | `148.0 BPM` | `14.0` | `0.92 VU` | **`92.0`** | Maximum Tier (`+53.0` pt surge) |

---

## 6. IBM Cloud Services & Orchestrate Skill Integration (Session 4)

### IBM Cloud Object Storage (COS) — Archival Architecture

`cloud_storage.py` (and Week 5's `cos_archive.py`) provides a resilient, Pyright-clean COS module for archiving verified post-game records.

**Environment variables (set in `.env` or IBM Cloud Secrets Manager):**

| Variable | Description |
|---|---|
| `COS_APIKEY` | IBM Cloud IAM API key with Writer access to the bucket |
| `COS_RESOURCE_CRN` | CRN of the COS service instance |
| `COS_ENDPOINT` | Regional endpoint (e.g., `https://s3.us-south.cloud-object-storage.appdomain.cloud`) |
| `COS_BUCKET` | Target bucket name (default: `kinetic-fanlab-archive`) |

**Graceful fallback:** When credentials are absent or the SDK is unavailable, the module operates in **local mock mode**, writing JSON files to `cloud_storage_archive/` (and `cos_archive_store/`) and returning `status: "ARCHIVED_LOCALLY (Simulated IBM COS)"`.

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

`cloudant_db.py` (and Week 5's `cloudant_engine.py`) persists the 8 member Fan Passports in the `kinetic-fan-passports` database.

**Environment variables:**

| Variable | Description |
|---|---|
| `CLOUDANT_APIKEY` | IBM Cloud IAM API key with Reader/Writer access to Cloudant |
| `CLOUDANT_URL` | Cloudant service URL (e.g., `https://<account>.cloudantnosqldb.appdomain.cloud`) |

**Graceful fallback:** When credentials are absent, the module uses `cloudant_cache.json` / `cloudant_engine_cache.json` (local JSON) so respect taps and accolades persist across app reloads without any crash.

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

### OpenAPI 3.0 Skill Registration Manifest — `kinetic_fanlab_skill.json` & `orchestrate_specs/`

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

---

## 7. Week 5 Enterprise Hardening Modules (51 / 51 Automated Checks Passing)

| Module | Purpose | Key Verified Metric |
| :--- | :--- | :--- |
| **`telemetry_dsp.py`** | Logarithmic SPL summation ($10 \log_{10}(\frac{1}{N}\sum 10^{L_i/10})$), `-3.5 dB` PA speaker bleed filter & Hampel BPM outlier scrubbing (`0.0` & `>205` BPM drops). | `$0.00` local edge compute cost |
| **`edge_mesh_resilience.py`** | 50-seat Bluetooth Low Energy (BLE) mesh pod clustering (`BleMeshPodCluster`) with store-and-forward queue and adaptive EMA decay. | **`98.0%`** cellular backhaul reduction |
| **`governance_fairness.py`** | 21-pattern adversarial prompt-injection defense, PII scrubbing, and 5-cohort regional dialect fairness auditing. | **`DIR = 0.953`** (EEOC 4/5ths compliant) |
| **`cloudant_engine.py`** | Formal document schemas (`passport:`, `cmi:`, `storycard:`) with thread-safe local cache circuit breaker. | Zero data loss during Wi-Fi drops |
| **`cos_archive.py`** | Partitioned S3 key layout (`curated-cmi/{sport}/{season}/{fixture_id}_boxscore.json`) with `SHA-256` checksum receipts. | 64-hex cryptographic integrity |
| **`tests/test_full_suite_week5.py`** | Master 8-suite certification runner validating all Week 5 contracts. | **51 / 51 PASS (100%)** |

---

## 8. Week 6 Enterprise Upgrade: 16-Agent Theatre Production Cast (`agents/`, `tools/`, `data/`, `db/`)

Modeled after the native `watsonx Orchestrate` multi-agent architecture (`spec_version: v1`, `kind: native`, `style: react`), while keeping `app.py` strictly as a **4-Screen Fan HUD** (1,219 lines):

### 8.1 The 16-Agent Production Cast (`agents/*.yaml`)

| Theatre Tier | # | Agent Manifest (`agents/`) | Persona | Tool Module (`tools/`) | Primary Function |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **🚪 1. Front Door** | 1 | `ticket_bouncer_agent.yaml` | **The Box Office Bouncer** | `front_door_tools.py` | Verifies cryptographic `member_hash`, BLE beacon RSSI (`-90` to `-25 dBm`) & `1.25x` Early Arrival Multiplier. |
| **🚪 1. Front Door** | 2 | `supervisor_agent.yaml` | **The Showrunner** | `front_door_tools.py` | Master ReAct Supervisor; enforces intent confidence $\ge 0.55$ and orchestrates all 15 cast collaborators. |
| **🏟️ 2. Front Stage** | 3 | `coordinator_agent.yaml` | **The Conductor** | `front_stage_tools.py` | Monitors live play clock, 36h Virtual Tailgate countdowns & triggers `2.0x` Clutch Multiplier. |
| **🏟️ 2. Front Stage** | 4 | `synthesizer_agent.yaml` | **The Scout** | `front_stage_tools.py` | Fuses sanitized SPL dB (35%), BPM (25%), Taps (20%) & Granite VU (20%) into the 0–100 CMI score. |
| **🏟️ 2. Front Stage** | 5 | `optimizer_agent.yaml` | **The Strategist** | `front_stage_tools.py` | Computes per-capita section standings, fires Chaser Alerts & generates Reality Delta StoryCards. |
| **🏟️ 2. Front Stage** | 6 | `fan_coach_agent.yaml` | **The Hype Coach** | `front_stage_tools.py` | Tracks lifetime games, Career dB & Clutch Stops to guide Tier and dynamic NFT badge unlocks. |
| **🛠️ 3. Backstage Crew** | 7 | `sound_telemetry_agent.yaml` | **The Sound Engineer** | `backstage_crew_tools.py` | Executes local Log SPL math, `-3.5 dB` PA bleed filter & Hampel BPM outlier scrubbing at `$0.00` cloud cost. |
| **🛠️ 3. Backstage Crew** | 8 | `mesh_rigging_agent.yaml` | **The Master Rigger** | `backstage_crew_tools.py` | Aggregates 50 BLE seat packets into 1 Pod Leader uplink (`98.0%` cellular backhaul reduction). |
| **🛠️ 3. Backstage Crew** | 9 | `trust_safety_agent.yaml` | **The Safety Steward** | `backstage_crew_tools.py` | Runs `watsonx.governance` prompt-injection defense, PII scrubbing & EEOC 4/5ths dialect fairness (`DIR = 0.953`). |
| **🛠️ 3. Backstage Crew** | 10 | `cot_inspector_agent.yaml` | **The Stage Manager** | `backstage_crew_tools.py` | Verifies multi-agent Chain-of-Thought traces, `< 250ms` latency SLAs & logs to SQL `audit_trail`. |
| **🛠️ 3. Backstage Crew** | 11 | `unit_economics_agent.yaml` | **The FinOps Producer** | `backstage_crew_tools.py` | **Cost Side:** Gates paid Granite LLM calls to clutch/tailgate moments (`$0.0137/seat` $\le \$0.015$ ceiling). |
| **🛠️ 3. Backstage Crew** | 12 | `discovery_insights_agent.yaml` | **The Audience Director** | `backstage_crew_tools.py` | Evaluates User Discovery Interview scores vs. compute cost per feature in `discovery_feature_matrix`. |
| **🔐 4. Back Door** | 13 | `cloudant_chronicler_agent.yaml` | **The House Chronicler** | `back_door_tools.py` | Persists Fan Passports, Respect Taps & standings to `db/fanlab_db.py` and IBM Cloudant NoSQL. |
| **🔐 4. Back Door** | 14 | `lakehouse_archivist_agent.yaml` | **The Vault Curator** | `back_door_tools.py` | Archives Crowd Box Scores with tamper-evident `SHA-256` checksums to IBM COS S3 Lakehouse. |
| **🔐 4. Back Door** | 15 | `sponsor_monetization_agent.yaml` | **The Commercial Promoter** | `back_door_tools.py` | **Revenue Side:** Unlocks dynamic sponsor concession perks (`$4.85/seat`, `99.72%` gross margin). |
| **🔐 4. Back Door** | 16 | `stadium_dispatch_agent.yaml` | **The Stage Door Dispatcher** | `back_door_tools.py` | Broadcasts Section Defense Belt winners to Jumbotron feed & triggers `escalate_to_human` Stadium Ops alerts. |

### 8.2 RAG Knowledge Base (`data/`) & Hybrid Database (`db/fanlab_db.py`)
- **`data/` (4 RAG Markdown Playbooks):** `cmi_acoustic_biometric_playbook.md`, `unit_economics_and_sponsor_roi.md`, `user_discovery_interview_framework.md`, and `governance_dialect_fairness_policy.md`.
- **`db/fanlab_db.py` + `db/kinetic_fanlab_tables.json` (6 Relational Tables):** `fan_passports`, `cmi_telemetry_logs`, `section_standings`, `audit_trail`, `unit_economics_ledger`, and `discovery_feature_matrix`.
- **Verification Suite (`tests/test_16_agent_production.py`):** **31 / 31 PASS (100%)** (82 / 82 total checks passing with `tests/test_full_suite_week5.py`).
