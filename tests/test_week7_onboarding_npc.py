"""
==================================================================================
KINETIC FANLAB — SUITE 6: WEEK 7 ONBOARDING & NPC MENTOR UNLOCK SUITE
Audits:
  1. Default Initialization (Marcus Vance for BB, Sarah Jenkins for FB)
  2. Rookie Baton Pass Unlock (Jordan Lee & Alex Taylor after 3 taps/check-in)
  3. Mid-Tier Specialist Unlock (Elena Rostova waving / Carlos Mendez tailgate)
  4. Capstone 4-Mentor Unlock (Devon Miller / Maya Patel & Capstone Badges)
  5. Deterministic Dialogue & In-App Hints Registry Integrity
==================================================================================
"""

import sys
import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import importlib.util
spec = importlib.util.spec_from_file_location("npc_mentors", os.path.join(PROJECT_ROOT, "npc_mentors.py"))
npc_mentors = importlib.util.module_from_spec(spec)
spec.loader.exec_module(npc_mentors)

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


def test_initial_state():
    print("\n1. Default Inception State & Lead Mentor Assignments:")
    init_bb = npc_mentors.get_initial_npc_state("Basketball")
    init_fb = npc_mentors.get_initial_npc_state("Football")

    record_check(
        "Basketball starts with Marcus Vance unlocked as lead guide",
        init_bb["unlocked_npcs"] == ["Marcus Vance"] and init_bb["active_npc_guide"] == "Marcus Vance",
        f"Result: {init_bb['unlocked_npcs']}",
    )
    record_check(
        "Football starts with Sarah Jenkins unlocked as lead guide",
        init_fb["unlocked_npcs"] == ["Sarah Jenkins"] and init_fb["active_npc_guide"] == "Sarah Jenkins",
        f"Result: {init_fb['unlocked_npcs']}",
    )
    record_check(
        "Initial onboarding mode is 'Rookie Tour'",
        init_bb["onboarding_mode"] == "Rookie Tour" and init_fb["onboarding_mode"] == "Rookie Tour",
        f"Result: {init_bb['onboarding_mode']}",
    )


def test_rookie_baton_pass():
    print("\n2. Rookie Baton Pass (Jordan Lee & Alex Taylor):")
    # Low-barrier trigger: 3 taps
    bb_res = npc_mentors.evaluate_npc_unlocks(
        sport="Basketball",
        current_unlocked=["Marcus Vance"],
        early_checkin=False,
        tap_count=3,
        respect_count=0,
        chant_action=False,
        storycard_exported=False,
        cmi=37.8,
    )
    record_check(
        "Jordan Lee unlocks after 3 pulse taps",
        "Jordan Lee" in bb_res["unlocked_npcs"] and "Jordan Lee" in bb_res["newly_unlocked"],
        f"Result: {bb_res['unlocked_npcs']}",
    )

    # Low-barrier trigger: seat check-in
    fb_res = npc_mentors.evaluate_npc_unlocks(
        sport="Football",
        current_unlocked=["Sarah Jenkins"],
        early_checkin=True,
        tap_count=0,
        respect_count=0,
        chant_action=False,
        storycard_exported=False,
        cmi=39.0,
    )
    record_check(
        "Alex Taylor unlocks after pre-game seat check-in",
        "Alex Taylor" in fb_res["unlocked_npcs"] and "Alex Taylor" in fb_res["newly_unlocked"],
        f"Result: {fb_res['unlocked_npcs']}",
    )


def test_specialist_and_capstone_progression():
    print("\n3. Specialist & Capstone 4-Mentor Unlocks:")
    # Basketball: Progress through Elena to Devon
    bb_step2 = npc_mentors.evaluate_npc_unlocks(
        sport="Basketball",
        current_unlocked=["Marcus Vance", "Jordan Lee"],
        early_checkin=True,
        tap_count=10,
        respect_count=1,
        chant_action=False,
        storycard_exported=False,
        cmi=70.0,
    )
    record_check(
        "Elena Rostova unlocks after 10 taps and elevated CMI",
        "Elena Rostova" in bb_step2["unlocked_npcs"],
        f"Result: {bb_step2['unlocked_npcs']}",
    )

    bb_step3 = npc_mentors.evaluate_npc_unlocks(
        sport="Basketball",
        current_unlocked=bb_step2["unlocked_npcs"],
        early_checkin=True,
        tap_count=15,
        respect_count=2,
        chant_action=True,
        storycard_exported=True,
        cmi=81.9,
    )
    record_check(
        "Devon Miller unlocks after chant action & clutch surge (All 4 Unlocked)",
        "Devon Miller" in bb_step3["unlocked_npcs"] and bb_step3["capstone_ready"],
        f"Result: {bb_step3['unlocked_npcs']}, Capstone: {bb_step3['capstone_ready']}",
    )

    # Football: Progress through Carlos to Maya
    fb_step2 = npc_mentors.evaluate_npc_unlocks(
        sport="Football",
        current_unlocked=["Sarah Jenkins", "Alex Taylor"],
        early_checkin=True,
        tap_count=5,
        respect_count=1,
        chant_action=True,
        storycard_exported=False,
        cmi=40.0,
    )
    record_check(
        "Carlos Mendez unlocks after tailgate chant action",
        "Carlos Mendez" in fb_step2["unlocked_npcs"],
        f"Result: {fb_step2['unlocked_npcs']}",
    )

    fb_step3 = npc_mentors.evaluate_npc_unlocks(
        sport="Football",
        current_unlocked=fb_step2["unlocked_npcs"],
        early_checkin=True,
        tap_count=14,
        respect_count=2,
        chant_action=True,
        storycard_exported=True,
        cmi=92.0,
    )
    record_check(
        "Maya Patel unlocks after StoryCard export & 92 CMI snap (All 4 Unlocked)",
        "Maya Patel" in fb_step3["unlocked_npcs"] and fb_step3["capstone_ready"],
        f"Result: {fb_step3['unlocked_npcs']}, Capstone: {fb_step3['capstone_ready']}",
    )


def test_dialogue_and_hints_integrity():
    print("\n4. Dialogue & In-App Hint Integrity:")
    all_names = ["Marcus Vance", "Jordan Lee", "Elena Rostova", "Devon Miller", "Sarah Jenkins", "Alex Taylor", "Carlos Mendez", "Maya Patel"]
    all_valid = all(
        name in npc_mentors.NPC_MENTOR_REGISTRY
        and len(npc_mentors.NPC_MENTOR_REGISTRY[name]["greeting"]) > 20
        and len(npc_mentors.NPC_MENTOR_REGISTRY[name]["hint"]) > 20
        for name in all_names
    )
    record_check(
        "All 8 mentors carry rich greetings, persona roles, and actionable unlock hints",
        all_valid,
        f"Checked {len(all_names)} mentors",
    )

    badge_bb = npc_mentors.get_capstone_nft_badge("Basketball")
    badge_fb = npc_mentors.get_capstone_nft_badge("Football")
    record_check(
        "Basketball Capstone is 'Thunder Row Inner Circle Key'",
        badge_bb["title"] == "Thunder Row Inner Circle Key" and badge_bb["rarity"] == "Legendary",
        f"Title: {badge_bb['title']}",
    )
    record_check(
        "Football Capstone is 'End Zone Loyals Founding Shield'",
        badge_fb["title"] == "End Zone Loyals Founding Shield" and badge_fb["rarity"] == "Legendary",
        f"Title: {badge_fb['title']}",
    )


def run_all_tests():
    print("=" * 80)
    print("KINETIC FANLAB — SUITE 6: WEEK 7 ONBOARDING & NPC MENTOR TEST RUNNER")
    print("=" * 80)
    test_initial_state()
    test_rookie_baton_pass()
    test_specialist_and_capstone_progression()
    test_dialogue_and_hints_integrity()
    print("\n" + "=" * 80)
    print(f"SUITE 6 SUMMARY: {passed_checks} PASSED | {failed_checks} FAILED")
    print("=" * 80)
    return 0 if failed_checks == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
