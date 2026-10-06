# AGENTS.md — Kinetic FanLab (IBM Bob IDE Ground Truth)

## Project Overview
- **Track**: Track #3 — Fan-Centric Sports & Entertainment
- **Development Environment**: IBM Bob IDE (AI-Assisted Architecture & Agentic Code Scaffolding)
- **Cloud Infrastructure**: IBM Cloud (Dallas / us-south)
- **AI Core**: IBM watsonx.ai (Granite 4.0 / Granite 3-8b) + watsonx.governance (Guardrails)

## Agent Architecture & Roles
- **Bob (IBM Bob IDE)**: Scaffolded the 4-screen Streamlit interactive prototype, implemented contract-exact mathematical normalization for the Calculated Momentum Index (0–100), and integrated live watsonx API client hooks.
- **watsonx.ai (Granite Foundation Models)**: Ingests unstructured fan voice logs, scores real-time vocal urgency (0.0–1.0), and synthesizes post-play ecosystem narratives.
- **watsonx.governance**: Pre-inference safety check filtering profanity and toxic outbursts before LLM analysis.

## Canonical Test Fixtures
- `BB-01`: Basketball Baseline (Free Throw 1) — 37.8 CMI (Ambient 82.0 dB, 98 BPM)
- `BB-02`: Basketball Clutch (Free Throw 2) — 81.9 CMI (+44.1 pt surge, 106.5 dB, 136 BPM)
- `FB-01`: Football Pre-Kick Timeout — 39.0 CMI (Ambient 78.5 dB, 105 BPM)
- `FB-02`: Football 48-Yard FG Snap — 92.0 CMI (+53.0 pt surge, 111.8 dB, 148 BPM)