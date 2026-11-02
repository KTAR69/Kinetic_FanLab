#!/usr/bin/env python3
"""
Kinetic FanLab — Autonomous Real-Time Schedule Engine Test Suite
Validates that sports schedules, gameday statuses, and win-loss records
auto-advance chronologically without requiring manual code or JSON edits.
"""

import os
import sys
import json
import datetime as dt
import importlib.abc
import importlib.util
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# FUSE filesystem dynamic import support
class StatMetaPathFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        parts = fullname.split(".")
        rel = os.path.join(str(ROOT_DIR), *parts)
        init_py = os.path.join(rel, "__init__.py")
        mod_py = rel + ".py"
        if os.path.isfile(init_py):
            return importlib.util.spec_from_file_location(fullname, init_py, submodule_search_locations=[rel])
        if os.path.isfile(mod_py):
            return importlib.util.spec_from_file_location(fullname, mod_py)
        return None

sys.meta_path.insert(0, StatMetaPathFinder())

import live_schedule_engine as lse

passed = 0
failed = 0

def check(cond: bool, msg: str):
    global passed, failed
    if cond:
        passed += 1
        print("  [PASS] " + msg)
    else:
        failed += 1
        print("  [FAIL] " + msg)

def load_schedules():
    sched_path = os.path.join(str(ROOT_DIR), "data", "gameday_schedules.json")
    with open(sched_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_michigan_chronological_advancement():
    schedules = load_schedules()
    
    # 1. On Monday, Nov 2, 2026: Rutgers is Final, next is Michigan State
    now_nov2 = dt.datetime(2026, 11, 2, 12, 0, 0)
    res_nov2 = lse.resolve_dynamic_team_matchup("Football", "Michigan Wolverines", schedules, reference_now=now_nov2)
    check("Michigan State" in res_nov2["active_game"]["matchup"], "Nov 2: Michigan State automatically promoted to active_game")
    check("Oregon" in res_nov2["upcoming_game"]["matchup"], "Nov 2: Oregon automatically set as subsequent game")
    check(res_nov2["is_game_today"] is False, "Nov 2: is_game_today correctly evaluates to False on non-gameday")
    check("Rutgers" in res_nov2["recent_games"], "Nov 2: Rutgers game correctly recorded in recent_games summary")

    # 2. On Gameday Saturday, Nov 7, 2026: is_game_today flips to True automatically
    now_nov7 = dt.datetime(2026, 11, 7, 12, 0, 0)
    res_nov7 = lse.resolve_dynamic_team_matchup("Football", "Michigan Wolverines", schedules, reference_now=now_nov7)
    check(res_nov7["is_game_today"] is True, "Nov 7: is_game_today automatically flips to True on gameday")
    check("ACTIVE GAMEDAY TONIGHT" in res_nov7["active_game"]["status"], "Nov 7: Status badge automatically updates to ACTIVE GAMEDAY")

    # 3. Post-Game Sunday, Nov 8, 2026: Michigan State is Final, next rolls to Oregon
    now_nov8 = dt.datetime(2026, 11, 8, 12, 0, 0)
    res_nov8 = lse.resolve_dynamic_team_matchup("Football", "Michigan Wolverines", schedules, reference_now=now_nov8)
    check("Oregon" in res_nov8["active_game"]["matchup"], "Nov 8: active_game automatically rolls forward to Oregon")
    check("UCLA" in res_nov8["upcoming_game"]["matchup"], "Nov 8: upcoming_game automatically rolls forward to UCLA")

def test_basketball_opening_night_rollover():
    schedules = load_schedules()

    # On Monday, Nov 2, 2026: Duke Season Opener vs Army is TODAY
    now_nov2 = dt.datetime(2026, 11, 2, 18, 0, 0)
    res_duke = lse.resolve_dynamic_team_matchup("Basketball", "Duke Blue Devils", schedules, reference_now=now_nov2)
    check(res_duke["is_game_today"] is True, "Duke Season Opener automatically identified as active today (Nov 2)")
    check("Army" in res_duke["active_game"]["matchup"], "Duke active matchup correctly targets Army West Point")

    # Texas Basketball Season Opener is also TODAY
    res_texas = lse.resolve_dynamic_team_matchup("Basketball", "Texas Longhorns", schedules, reference_now=now_nov2)
    check(res_texas["is_game_today"] is True, "Texas Basketball Opener automatically identified as active today (Nov 2)")
    check("Chicago State" in res_texas["active_game"]["matchup"], "Texas active matchup correctly targets Chicago State")

def test_dynamic_record_recalculation():
    schedules = load_schedules()
    now_nov2 = dt.datetime(2026, 11, 2, 12, 0, 0)
    res_mich = lse.resolve_dynamic_team_matchup("Football", "Michigan Wolverines", schedules, reference_now=now_nov2)
    check("5-3" in res_mich["record"], "Michigan record automatically reflects 5-3 after Oct 31 Rutgers victory")

def run_all_schedule_tests():
    global passed, failed
    passed = 0
    failed = 0
    print("=" * 80)
    print("KINETIC FANLAB — AUTONOMOUS REAL-TIME SCHEDULE ENGINE VERIFICATION")
    print("=" * 80)
    test_michigan_chronological_advancement()
    test_basketball_opening_night_rollover()
    test_dynamic_record_recalculation()
    print("=" * 80)
    print(f"SCHEDULE ENGINE SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 80)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(run_all_schedule_tests())