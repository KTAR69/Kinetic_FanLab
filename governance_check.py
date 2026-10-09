"""
Kinetic FanLab — watsonx.governance & AI Ethics Guardrail Test
IBM SkillsBuild AI Experiential Learning Lab
"""

import re


# Adversarial patterns that indicate a prompt injection attempt.
# Checked before HAP/PII — any match is an immediate hard reject.
_INJECTION_PATTERNS: list = [
    "ignore previous",
    "ignore all previous",
    "system:",
    "you are now",
    "disregard",
    "act as",
    "<|",
    "]]>",
    "jailbreak",
    "override instructions",
    "forget your instructions",
    "new instructions:",
    "prompt injection",
]


def evaluate_fan_content_safety(raw_text: str) -> dict:
    """
    Evaluates fan speech against IBM watsonx.governance guardrails in order:

      0. Prompt injection defense  — checked first, hard reject
      1. HAP / Profanity check     — whole-word regex, hard reject
      2. PII / Privacy check       — substring match on structured patterns

    HAP matching uses whole-word regex so substrings inside legitimate words
    (e.g. "adamant", "Amsterdam") do not trigger false positives.
    "damn" is intentionally excluded — it appears routinely in acceptable
    sports chants and does not meet the threshold for a hard reject.
    """
    # Hard-reject HAP terms — whole-word match only
    profane_terms = ["hate", "kill", "threat", "curse", "bitch"]
    pii_indicators = ["@gmail.com", "@yahoo.com", "phone:", "ssn:", "address:"]

    violations = []
    text_lower = raw_text.lower()

    # 0. Prompt injection defense — runs before any other check.
    #    Fan text is interpolated directly into Granite prompts; adversarial
    #    inputs must be stopped here before they reach watsonx_live.py.
    for pattern in _INJECTION_PATTERNS:
        if pattern in text_lower:
            violations.append(f"PROMPT_INJECTION: Adversarial pattern detected ('{pattern}')")

    # Short-circuit: if injection detected, skip further checks and return immediately
    if violations:
        return {
            "input_text": raw_text,
            "guardrail_status": "REJECTED",
            "violations": violations,
            "action": "Discard / Block — Adversarial input detected by watsonx.governance",
        }

    # 1. HAP / Profanity Check — whole-word boundary match
    for word in profane_terms:
        if re.search(r"\b" + re.escape(word) + r"\b", text_lower):
            violations.append(f"HAP Violation: Inappropriate term ('{word}')")

    # 2. PII / Privacy Check — substring match is correct for structured patterns
    for pii in pii_indicators:
        if pii in text_lower:
            violations.append(f"PII Violation: Personal identifier ('{pii}')")
            
    passed = len(violations) == 0
    return {
        "input_text": raw_text,
        "guardrail_status": "APPROVED" if passed else "REJECTED",
        "violations": violations,
        "action": "Proceed to Granite Urgency Scoring" if passed else "Discard / Prompt Fan to Rephrase"
    }

if __name__ == "__main__":
    print("=" * 70)
    print("  KINETIC FANLAB: WATSONX.GOVERNANCE & SAFETY AUDIT")
    print("=" * 70)
    
    test_cases = [
        "MISS IT! OFF THE BACK IRON! BRING THE NOISE!",
        "Contact me at user@gmail.com to buy tickets",
        "BLOCK THAT KICK! RATTLE THE KICKER!"
    ]
    
    for case in test_cases:
        res = evaluate_fan_content_safety(case)
        print(f"\n[Test Input]: '{case}'")
        print(f"  • Guardrail Verdict: {res['guardrail_status']}")
        print(f"  • Pipeline Action:   {res['action']}")
        if res['violations']:
            print(f"  • Flags:             {res['violations']}")
    print("\n" + "=" * 70)