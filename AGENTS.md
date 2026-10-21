# AGENTS.md — Kinetic FanLab (IBM Bob IDE Ground Truth — Weeks 1–6 Complete)

## 1. Project & Environment Identity
- **Track**: Track #3 — Fan-Centric Sports & Entertainment
- **Program**: IBM SkillsBuild AI Experiential Learning Lab
- **Team**: Kinetic FanLab | **Team Lead**: Troy Resendez
- **Team Composition**: Troy Resendez (Team Lead), IBM Bob IDE (Autonomous Agentic Scaffolding), and Gemini (Enterprise Architecture, FinOps & Multi-Agent Co-Architect)
- **Primary IDE & Scaffolding**: IBM Bob IDE (Autonomous Agentic Scaffolding with Custom Modes, Subagents, Skills, Rules, MCP & `.bobignore`)
- **Cloud Infrastructure**: IBM Cloud (`us-south` / Dallas region for `watsonx.ai` & `eu-de-0ec71755` / Frankfurt `Global workspace` for live `watsonx Orchestrate`)
- **Foundation Models**: IBM watsonx.ai (`ibm/granite-4.0` / `ibm/granite-3-8b-instruct`)
- **Safety & Trust Layer**: IBM watsonx.governance (Content Auditing, Prompt-Injection Shield & Dialect Fairness `DIR = 0.953`)
- **Multi-Agent Orchestration**: IBM watsonx Orchestrate ADK (`v2.6.0` CLI — 16-Agent Theatre Production Cast mapped 2-for-1 across all 8 Official IBM Agentic AI Archetypes)

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

## 3. All 8 Official IBM Agentic AI Archetypes (`Challenge Guide Appendix 1, Pages 6–8`)
Per `US Fall 2026 - Industry Challenges AI Experiential Learning Lab with Bob.pdf` (Appendix 1, pp. 6–8), IBM defines **8 Official Agentic AI Archetypes**. Kinetic FanLab operationalizes **all 8 IBM Archetypes with 2-for-1 redundancy** across our 16-Agent Theatre Production Cast (`orchestrate_agents.py` & `agents/*.yaml`):

| # | Official IBM Archetype (Appendix 1) | Core Technical Patterns | Assigned Theatre Cast Agents (2-for-1 Redundancy) |
| :--- | :--- | :--- | :--- |
| **1** | **The Cognitive Load Reducer** *(p. 6)* | RAG over fragmented knowledge, multi-step reasoning (`gather -> compare -> recommend`), ranking logic, confidence gate $\ge 0.55$ | `supervisor_agent.yaml` (*The Showrunner*) & `discovery_insights_agent.yaml` (*The Audience Director*) |
| **2** | **The Invisible Coordinator** *(p. 6)* | Multi-agent systems, event-driven orchestration, 50-seat BLE mesh state tracking, human-in-the-loop handoffs | `coordinator_agent.yaml` (*The Conductor*) & `mesh_rigging_agent.yaml` (*The Master Rigger*) |
| **3** | **The Context-Aware Expert** *(pp. 6–7)* | Situational awareness, RAG + session memory, BLE seat proximity filtering, personalized tier coaching without overfitting | `fan_coach_agent.yaml` (*The Hype Coach*) & `ticket_bouncer_agent.yaml` (*The Box Office Bouncer*) |
| **4** | **The Decision Gatekeeper** *(p. 7)* | Multi-criteria evaluation on high-cost/high-risk gates (`<= $0.015/seat` LLM ceiling & `DIR = 0.953` EEOC dialect fairness) | `unit_economics_agent.yaml` (*The FinOps Producer*) & `trust_safety_agent.yaml` (*The Safety Steward*) |
| **5** | **The Long-Horizon Planner** *(p. 7)* | Longitudinal 365-day planning & re-planning loops, persistent Cloudant NoSQL memory & COS S3 SHA-256 seasonal archives | `cloudant_chronicler_agent.yaml` (*The House Chronicler*) & `lakehouse_archivist_agent.yaml` (*The Vault Curator*) |
| **6** | **The Knowledge Synthesizer** *(p. 7)* | Multimodal sensory fusion (35% dB, 25% BPM, 20% Taps, 20% VU), Log SPL vs. Linear comparison, Hampel BPM outlier detection | `synthesizer_agent.yaml` (*The Scout*) & `sound_telemetry_agent.yaml` (*The Sound Engineer*) |
| **7** | **The Human–AI Boundary Manager** *(pp. 7–8)* | Designed around when **NOT** to act autonomously; `< 250ms` SLA checks, confidence thresholds, `escalate_to_human` Stadium Ops dispatch | `stadium_dispatch_agent.yaml` (*The Stage Door Dispatcher*) & `cot_inspector_agent.yaml` (*The Stage Manager*) |
| **8** | **The System Optimizer** *(p. 8)* | Longitudinal pattern detection, per-capita section standings, Chaser Alerts, Reality Delta StoryCards & `$4.85/seat` Sponsor ROI | `optimizer_agent.yaml` (*The Strategist*) & `sponsor_monetization_agent.yaml` (*The Commercial Promoter*) |

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

## 5. IBM Cloud Services & Orchestrate Skill Integration

### IBM Cloud Object Storage (COS) — Archival Architecture
`cloud_storage.py` and Week 5's `cos_archive.py` provide resilient S3-compatible archiving for verified post-game records (`curated-cmi/{sport}/{season}/{fixture_id}_boxscore.json`) with 64-hex `SHA-256` cryptographic integrity receipts and automatic local hybrid fallback (`cos_archive_store/`).

### IBM Cloudant NoSQL — Fan Passport Document Schema
`cloudant_db.py` and Week 5's `cloudant_engine.py` persist the 8 member Fan Passports (`passport:{member_hash}`), CMI telemetry snapshots, and StoryCards in `kinetic-fan-passports` with a thread-safe local circuit-breaker cache (`cloudant_engine_cache.json`).

### OpenAPI 3.0 Skill Registration Manifests — `kinetic_fanlab_skill.json` & `orchestrate_specs/`
Endpoints registered for IBM watsonx Orchestrate skill discovery (`/calculate_cmi`, `/evaluate_pacing`, `/generate_narrative`, plus declarative OpenAPI specs in `orchestrate_specs/`).

---

## 6. Week 5 Enterprise Hardening Modules (51 / 51 Automated Checks Passing)

| Module | Purpose | Key Verified Metric |
| :--- | :--- | :--- |
| **`telemetry_dsp.py`** | Logarithmic SPL summation ($10 \log_{10}(\frac{1}{N}\sum 10^{L_i/10})$), `-3.5 dB` PA speaker bleed filter & Hampel BPM outlier scrubbing (`0.0` & `>205` BPM drops). | `$0.00` local edge compute cost |
| **`edge_mesh_resilience.py`** | 50-seat Bluetooth Low Energy (BLE) mesh pod clustering (`BleMeshPodCluster`) with store-and-forward queue and adaptive EMA decay. | **`98.0%`** cellular backhaul reduction |
| **`governance_fairness.py`** | 21-pattern adversarial prompt-injection defense, PII scrubbing, and 5-cohort regional dialect fairness auditing. | **`DIR = 0.953`** (EEOC 4/5ths compliant) |
| **`cloudant_engine.py`** | Formal document schemas (`passport:`, `cmi:`, `storycard:`) with thread-safe local cache circuit breaker. | Zero data loss during Wi-Fi drops |
| **`cos_archive.py`** | Partitioned S3 key layout (`curated-cmi/{sport}/{season}/{fixture_id}_boxscore.json`) with `SHA-256` checksum receipts. | 64-hex cryptographic integrity |
| **`tests/test_full_suite_week5.py`** | Master 8-suite certification runner validating all Week 5 contracts. | **51 / 51 PASS (100%)** |

---

## 7. Week 6 Enterprise Upgrade: 16-Agent Theatre Production Cast (`eu-de-0ec71755` Live Deployment)

All 16 native YAML agents and 16 Python `@tool` functions are live-deployed in IBM Cloud `watsonx Orchestrate` (`eu-de-0ec71755` / `Global workspace`), while keeping `app.py` strictly as a **5-Screen Fan & AI Squad HUD**:

### 7.1 The 16-Agent Production Cast & Live IBM Cloud Agent UUIDs

| Theatre Tier | # | Agent Manifest (`agents/`) | Live `watsonx Orchestrate` UUID (`eu-de-0ec71755`) | Persona | Official IBM Archetype | Tool Module (`tools/`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **🚪 1. Front Door** | 1 | `ticket_bouncer_agent.yaml` | `fac5eccf-95de-4470-acc0-94712404ee28` | **The Box Office Bouncer** | **#3 Context-Aware Expert** | `front_door_tools.py` |
| **🚪 1. Front Door** | 2 | `supervisor_agent.yaml` | `e4370510-1643-4450-835b-61c285affd77` | **The Showrunner** | **#1 Cognitive Load Reducer** | `front_door_tools.py` |
| **🏟️ 2. Front Stage** | 3 | `coordinator_agent.yaml` | `aff3048f-d490-4ab2-8058-e1da04b5a60d` | **The Conductor** | **#2 Invisible Coordinator** | `front_stage_tools.py` |
| **🏟️ 2. Front Stage** | 4 | `synthesizer_agent.yaml` | `c5d257b0-bb2e-454a-b120-3b691d5c526d` | **The Scout** | **#6 Knowledge Synthesizer** | `front_stage_tools.py` |
| **🏟️ 2. Front Stage** | 5 | `optimizer_agent.yaml` | `d004e589-4a0d-4efd-8fcf-6f51928cfbc5` | **The Strategist** | **#8 System Optimizer** | `front_stage_tools.py` |
| **🏟️ 2. Front Stage** | 6 | `fan_coach_agent.yaml` | `41d1ce50-bb17-483c-801b-8070ec07b987` | **The Hype Coach** | **#3 Context-Aware Expert** | `front_stage_tools.py` |
| **🛠️ 3. Backstage Crew** | 7 | `sound_telemetry_agent.yaml` | `e3a26c43-588d-4cad-9df6-06a4aab684c7` | **The Sound Engineer** | **#6 Knowledge Synthesizer** | `backstage_crew_tools.py` |
| **🛠️ 3. Backstage Crew** | 8 | `mesh_rigging_agent.yaml` | `db6af6d9-e6f9-4ed9-8473-f2567f26c6b3` | **The Master Rigger** | **#2 Invisible Coordinator** | `backstage_crew_tools.py` |
| **🛠️ 3. Backstage Crew** | 9 | `trust_safety_agent.yaml` | `00405383-384c-4919-9b51-a641153b89a5` | **The Safety Steward** | **#4 Decision Gatekeeper** | `backstage_crew_tools.py` |
| **🛠️ 3. Backstage Crew** | 10 | `cot_inspector_agent.yaml` | `ee07ebfe-be76-4128-b02e-33da0903f151` | **The Stage Manager** | **#7 Human–AI Boundary Mgr** | `backstage_crew_tools.py` |
| **🛠️ 3. Backstage Crew** | 11 | `unit_economics_agent.yaml` | `7df57fe7-3b24-4ac5-a045-6fcce95099b5` | **The FinOps Producer** | **#4 Decision Gatekeeper** | `backstage_crew_tools.py` |
| **🛠️ 3. Backstage Crew** | 12 | `discovery_insights_agent.yaml` | `9728392e-784b-428f-b431-0c4f00a98f59` | **The Audience Director** | **#1 Cognitive Load Reducer** | `backstage_crew_tools.py` |
| **🔐 4. Back Door** | 13 | `cloudant_chronicler_agent.yaml` | `3e02cfda-b7e1-4e79-a8ad-7b728a38136c` | **The House Chronicler** | **#5 Long-Horizon Planner** | `back_door_tools.py` |
| **🔐 4. Back Door** | 14 | `lakehouse_archivist_agent.yaml` | `e20d3278-bb40-4a80-838d-7918970b5544` | **The Vault Curator** | **#5 Long-Horizon Planner** | `back_door_tools.py` |
| **🔐 4. Back Door** | 15 | `sponsor_monetization_agent.yaml` | `734c3abc-7c61-4843-adcf-2d95295e4c58` | **The Commercial Promoter** | **#8 System Optimizer** | `back_door_tools.py` |
| **🔐 4. Back Door** | 16 | `stadium_dispatch_agent.yaml` | `3d95dbd5-00fd-4164-ac7c-5b74a87d5290` | **The Stage Door Dispatcher** | **#7 Human–AI Boundary Mgr** | `back_door_tools.py` |

### 7.2 RAG Knowledge Base (`data/`), Hybrid Database (`db/fanlab_db.py`) & Verification (`151 / 151 PASS`)
- **`data/` (4 RAG Markdown Playbooks):** `cmi_acoustic_biometric_playbook.md`, `unit_economics_and_sponsor_roi.md`, `user_discovery_interview_framework.md`, and `governance_dialect_fairness_policy.md`.
- **`db/fanlab_db.py` + `db/kinetic_fanlab_tables.json` (6 Relational Tables + 8-Persona Discovery & Slide 24 Iteration Logs):** `fan_passports`, `cmi_telemetry_logs`, `section_standings`, `audit_trail`, `unit_economics_ledger`, and `discovery_feature_matrix`.
- **Automated Verification Suites (`151 / 151 PASS — 100%`):**
  - `tests/test_full_suite_week5.py`: **51 / 51 PASS (100%)**
  - `tests/test_16_agent_production.py`: **44 / 44 PASS (100%)**
  - `tests/test_step4_finops_and_discovery.py`: **26 / 26 PASS (100%)**
