"""
Kinetic FanLab — watsonx.governance & AI Ethics Guardrail Test
IBM SkillsBuild AI Experiential Learning Lab
"""

def evaluate_fan_content_safety(raw_text: str) -> dict:
    """
    Evaluates fan speech against IBM watsonx.governance HAP 
    (Hate, Abuse, Profanity) and PII guardrails.
    """
    profane_terms = ["hate", "kill", "threat", "curse", "bitch", "damn"]
    pii_indicators = ["@gmail.com", "@yahoo.com", "phone:", "ssn:", "address:"]
    
    violations = []
    text_lower = raw_text.lower()
    
    # 1. HAP / Profanity Check
    for word in profane_terms:
        if word in text_lower:
            violations.append(f"HAP Violation: Inappropriate term ('{word}')")
            
    # 2. PII / Privacy Check
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