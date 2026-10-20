# Kinetic FanLab — AI Governance, Dialect Fairness & Human Escalation Policy
## 1. Pre-Inference Edge Guardrails (`watsonx.governance`)
All fan-submitted chants and Armchair Coach outbursts are screened prior to IBM Granite inference:
- **Adversarial Prompt Injection Defense:** Immediate rejection of system-prompt extraction or override patterns (`ignore previous`, `system prompt`, `disregard`, `override`, `bypass`).
- **Profanity, Hate Speech & PII Scrubbing:** Blocks abusive slurs and strips phone numbers, emails, and raw device MAC addresses at the edge.

## 2. EEOC 4/5ths Dialect Fairness Gate (`DIR = 0.953`)
Passionate sports vernacular (e.g., *"ICE THE KICKER!"*, *"OFF THE BACK IRON!"*, *"BALL DON'T LIE!"*, *"COOK HIM!"*) must never be misclassified as toxic hostility by standard corporate sentiment models.
- Kinetic FanLab enforces a Disparate Impact Ratio (`DIR`) threshold of `>= 0.80` (EEOC 4/5ths rule) across regional and student section dialects.
- Current verified benchmark across canonical fixtures: **`DIR = 0.953` (PASS)**.

## 3. Human-in-the-Loop Escalation (`escalate_to_human`)
When `cot_inspector_agent` or `trust_safety_agent` detects:
- Intent confidence `< 0.55`,
- Repeated adversarial prompt injection attempts from a seat hash, or
- Biometric/safety anomaly requiring physical usher assistance,
`stadium_dispatch_agent` invokes `escalate_to_human` to alert live Stadium Operations and Section Directors.
