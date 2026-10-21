"""
==================================================================================
KINETIC FANLAB — SCREEN 5 AI SQUAD & GAME INTELLIGENCE TEST SUITE
IBM SkillsBuild AI Experiential Learning Lab (Track #3)
Audits:
  1. Bidirectional Sport Isolation (enforce_sport_isolation)
  2. 5-Agent x 2-Sport Question Chips (get_agent_question_chips)
  3. Dynamic Situational Placeholders (get_agent_chat_placeholder)
  4. Multi-Scenario Projection Engine (compute_game_situation_scenarios)
  5. 4-Agent Silent Backend Teamwork (run_backend_squad_teamwork)
==================================================================================
"""

import sys
import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from orchestrate_agents import (
    enforce_sport_isolation,
    get_agent_question_chips,
    get_agent_chat_placeholder,
    compute_game_situation_scenarios,
    run_backend_squad_teamwork,
)

passed_checks = 0
failed_checks = 0


def record_check(description: str, condition: bool, detail: str = ""):
    global passed_checks, failed_checks
    if condition:
        print(f"  [PASS] {description}")
        passed_checks += 1
    else:
        print(f"  [FAIL] {description} — {detail}")
        failed_checks += 1


def test_sport_isolation():
    print("\n1. Bidirectional Sport Isolation Enforcement (enforce_sport_isolation):")

    # Basketball Isolation Tests
    bb_raw = "Rattle the kicker on this 48-yard field goal snap count! Section 115 12th Man wide left 🏈"
    bb_clean = enforce_sport_isolation(bb_raw, "Basketball")
    record_check(
        "Basketball sanitization replaces football emoji with basketball emoji",
        "🏀" in bb_clean and "🏈" not in bb_clean,
        f"Result: {bb_clean}",
    )
    record_check(
        "Basketball sanitization replaces field goal with free throw",
        "free throw" in bb_clean and "field goal" not in bb_clean,
        f"Result: {bb_clean}",
    )
    record_check(
        "Basketball sanitization replaces kicker with shooter",
        "shooter" in bb_clean and "kicker" not in bb_clean,
        f"Result: {bb_clean}",
    )
    record_check(
        "Basketball sanitization replaces snap count with shot clock",
        "shot clock" in bb_clean and "snap count" not in bb_clean,
        f"Result: {bb_clean}",
    )
    record_check(
        "Basketball sanitization replaces 12th Man with 6th Man",
        "6th Man" in bb_clean and "12th Man" not in bb_clean,
        f"Result: {bb_clean}",
    )

    # Football Isolation Tests
    fb_raw = "Rattle the shooter on this clutch free throw off the rim! Section 114 6th Man FT% 🏀"
    fb_clean = enforce_sport_isolation(fb_raw, "Football")
    record_check(
        "Football sanitization replaces basketball emoji with football emoji",
        "🏈" in fb_clean and "🏀" not in fb_clean,
        f"Result: {fb_clean}",
    )
    record_check(
        "Football sanitization replaces free throw with field goal",
        "field goal" in fb_clean and "free throw" not in fb_clean,
        f"Result: {fb_clean}",
    )
    record_check(
        "Football sanitization replaces shooter with kicker",
        "kicker" in fb_clean and "shooter" not in fb_clean,
        f"Result: {fb_clean}",
    )
    record_check(
        "Football sanitization replaces FT% with FG%",
        "FG%" in fb_clean and "FT%" not in fb_clean,
        f"Result: {fb_clean}",
    )
    record_check(
        "Football sanitization replaces 6th Man with 12th Man",
        "12th Man" in fb_clean and "6th Man" not in fb_clean,
        f"Result: {fb_clean}",
    )

    # Edge cases
    record_check("Empty string passes safely through isolation filter", enforce_sport_isolation("", "Basketball") == "")
    record_check("None passes safely through isolation filter", enforce_sport_isolation(None, "Football") is None)


def test_question_chips_matrix():
    print("\n2. Dynamic Agent-Framed Question Chips Matrix (get_agent_question_chips):")
    agents = ["@coach", "@conductor", "@strategist", "@scout", "@squad"]
    sports = ["Basketball", "Football"]

    total_matrix_valid = True
    sport_contamination_detected = False

    for ag in agents:
        for sp in sports:
            chips = get_agent_question_chips(
                agent_tag=ag,
                sport=sp,
                member_name="Marcus Vance" if sp == "Basketball" else "Sarah Jenkins",
                persona_data={
                    "sec": "Section 114" if sp == "Basketball" else "Section 115",
                    "games": 34 if sp == "Basketball" else 62,
                    "tier": "Tier 4" if sp == "Basketball" else "Tier 5",
                },
            )
            if len(chips) != 3:
                total_matrix_valid = False
            for c in chips:
                if not c.get("chip_label") or not c.get("full_question"):
                    total_matrix_valid = False
                q_text = c["full_question"].lower()
                if sp == "Basketball" and any(k in q_text for k in ["kicker", "field goal", "12th man"]):
                    sport_contamination_detected = True
                if sp == "Football" and any(k in q_text for k in ["free throw", "shooter", "6th man"]):
                    sport_contamination_detected = True

    record_check(
        "All 10 (5 agents x 2 sports) question chip sets return exactly 3 well-formed chips",
        total_matrix_valid,
    )
    record_check(
        "Zero cross-sport terminology contamination in any generated question chip",
        not sport_contamination_detected,
    )


def test_placeholders():
    print("\n3. Dynamic Chat Input Placeholders (get_agent_chat_placeholder):")
    ph_coach_bb = get_agent_chat_placeholder("@coach", "Basketball")
    ph_coach_fb = get_agent_chat_placeholder("@coach", "Football")
    ph_cond_bb = get_agent_chat_placeholder("@conductor", "Basketball")
    ph_cond_fb = get_agent_chat_placeholder("@conductor", "Football")

    record_check("@coach Basketball placeholder highlights 6th Man / tier progression", "6th Man" in ph_coach_bb)
    record_check("@coach Football placeholder highlights 12th Man / tailgate status", "12th Man" in ph_coach_fb)
    record_check("@conductor Basketball placeholder highlights free throw release timing", "free throw" in ph_cond_bb)
    record_check("@conductor Football placeholder highlights play clock snap timing", "play clock" in ph_cond_fb or "snap" in ph_cond_fb)


def test_game_scenarios():
    print("\n4. Multi-Scenario Projection Engine (compute_game_situation_scenarios):")
    # BB-01 Baseline
    bb_intel = compute_game_situation_scenarios(
        sport="Basketball", fixture_id="BB-01", cmi=37.8, db=82.0, hr=98.0, taps=2.5, vu=0.55,
        is_clutch=False, early_checkin=True, synergy_score=92
    )
    record_check("Basketball scenario engine returns 3 discrete Scenarios (A, B, C)", len(bb_intel["scenarios"]) == 3)
    record_check("BB-01 returns key stat for Shooter FT%", "FT%" in bb_intel["key_stat_label"])
    record_check("BB-01 Scenario C targets Maximum Tier takeover", "Scenario C" in bb_intel["scenarios"][2]["scenario"])

    # FB-02 Clutch
    fb_intel = compute_game_situation_scenarios(
        sport="Football", fixture_id="FB-02", cmi=92.0, db=111.8, hr=148.0, taps=14.0, vu=0.92,
        is_clutch=True, early_checkin=True, synergy_score=95
    )
    record_check("Football scenario engine returns 3 discrete Scenarios (A, B, C)", len(fb_intel["scenarios"]) == 3)
    record_check("FB-02 returns key stat for Kicker FG%", "FG%" in fb_intel["key_stat_label"])
    record_check("FB-02 miss probability increases with high CMI", fb_intel["current_miss_pct"] > 50.0)


def test_backend_squad_teamwork():
    print("\n5. 4-Agent Backend Teamwork & Consensus Engine (run_backend_squad_teamwork):")
    # Test @coach in Basketball
    coach_res = run_backend_squad_teamwork(
        target_agent_tag="@coach",
        user_message="How do we force a miss on this free throw?",
        member_name="Marcus Vance",
        persona_data={"role": "Section Director", "tier": "Tier 4", "games": 34, "clutch_stops": 23, "sec": "Section 114 (Thunder Row)"},
        sport="Basketball", fixture_id="BB-01", cmi=37.8, db=82.0, hr=98.0, taps=2.5, vu=0.55,
        is_clutch=False, early_checkin=True, synergy_score=92
    )
    record_check("@coach response contains speaker metadata", "coach" in coach_res["speaker_tag"])
    record_check("@coach basketball response contains zero football emojis", "🏈" not in coach_res["reply"])
    record_check("@coach basketball response references 6th Man / Section 114", "Section 114" in coach_res["reply"] or "6th Man" in coach_res["reply"])

    # Test @conductor in Football
    cond_res = run_backend_squad_teamwork(
        target_agent_tag="@conductor",
        user_message="When do we stomp the bleachers?",
        member_name="Sarah Jenkins",
        persona_data={"role": "Stadium Veteran", "tier": "Tier 5", "games": 62, "clutch_stops": 31, "sec": "Section 115 (End Zone Loyals)"},
        sport="Football", fixture_id="FB-02", cmi=92.0, db=111.8, hr=148.0, taps=14.0, vu=0.92,
        is_clutch=True, early_checkin=True, synergy_score=95
    )
    record_check("@conductor football response contains zero basketball emojis", "🏀" not in cond_res["reply"])
    record_check("@conductor football response references snap / bleacher roar", "snap" in cond_res["reply"].lower() or "roar" in cond_res["reply"].lower())

    # Test @squad Consensus
    squad_res = run_backend_squad_teamwork(
        target_agent_tag="@squad",
        user_message="Give us the full squad briefing.",
        member_name="Marcus Vance",
        persona_data={"role": "Section Director", "tier": "Tier 4", "games": 34, "clutch_stops": 23, "sec": "Section 114 (Thunder Row)"},
        sport="Basketball", fixture_id="BB-02", cmi=81.9, db=106.5, hr=136.0, taps=12.2, vu=0.85,
        is_clutch=True, early_checkin=True, synergy_score=95
    )
    record_check("@squad returns 4-agent unified synthesis", "@scout" in squad_res["reply"] and "@conductor" in squad_res["reply"])


def main():
    print("=" * 82)
    print("KINETIC FANLAB — SCREEN 5 SQUAD INTELLIGENCE VERIFICATION SUITE")
    print("=" * 82)

    test_sport_isolation()
    test_question_chips_matrix()
    test_placeholders()
    test_game_scenarios()
    test_backend_squad_teamwork()

    print("\n" + "=" * 82)
    print(f"SCREEN 5 SUITE SUMMARY: {passed_checks} PASSED | {failed_checks} FAILED")
    print("=" * 82)

    if failed_checks > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
