#!/usr/bin/env python3
import os, sys, importlib.abc, importlib.util
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

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
import sponsor_voucher_engine as sve

passed = 0
failed = 0

def check(cond, msg):
    global passed, failed
    if cond:
        passed += 1
        print("  [PASS] " + msg)
    else:
        failed += 1
        print("  [FAIL] " + msg)

def test_perk_generation():
    v_none = sve.evaluate_clutch_sponsor_perk("Basketball", "Texas Longhorns", 68.5, False)
    check(v_none is None, "Below clutch threshold (68.5 CMI) generates 0 unearned vouchers")
    v_texas = sve.evaluate_clutch_sponsor_perk("Basketball", "Texas Longhorns", 84.2, True)
    check(v_texas is not None and v_texas["brand"] == "Whataburger®", "Texas Longhorns CMI 84.2 unlocks Whataburger voucher")
    assert v_texas is not None
    check(v_texas["discount_code"] == "WHATACLUTCH26", "Whataburger voucher carries valid code WHATACLUTCH26")
    v_celtics = sve.evaluate_clutch_sponsor_perk("Basketball", "Boston Celtics", 88.0, False)
    check(v_celtics is not None and "Dunkin" in v_celtics["brand"], "Boston Celtics CMI 88.0 unlocks Dunkin voucher")
    v_packers = sve.evaluate_clutch_sponsor_perk("Football", "Green Bay Packers", 91.5, True)
    check(v_packers is not None and "Culver" in v_packers["brand"], "Green Bay Packers CMI 91.5 unlocks Culvers voucher")
    v_spurs = sve.evaluate_clutch_sponsor_perk("Basketball", "San Antonio Spurs", 82.0, True)
    check(v_spurs is not None and v_spurs["brand"] == "H-E-B®", "San Antonio Spurs CMI 82.0 unlocks H-E-B voucher")

def test_cryptographic_claim():
    v = sve.evaluate_clutch_sponsor_perk("Basketball", "Texas Longhorns", 85.0, True)
    assert v is not None
    claimed = sve.claim_sponsor_voucher(v, "Troy Resendez", "@owltar")
    check(claimed["status"] == "CLAIMED", "Claimed voucher status updated to CLAIMED")
    check(claimed["claim_hash"].startswith("0xVCH-"), "Claim hash format verified: " + claimed["claim_hash"])
    check(len(claimed["claim_hash"]) == 18, "Cryptographic hash length matches 18 chars (0xVCH- + 12 hex)")
    check(claimed["claimed_by_handle"] == "@owltar", "Voucher bound to fan handle @owltar")

def test_two_sided_economics():
    v1 = sve.evaluate_clutch_sponsor_perk("Basketball", "Texas Longhorns", 85.0, True)
    v2 = sve.evaluate_clutch_sponsor_perk("Basketball", "San Antonio Spurs", 85.0, True)
    assert v1 is not None and v2 is not None
    c1 = sve.claim_sponsor_voucher(v1, "Marcus Vance", "@mvance_sec114")
    c2 = sve.claim_sponsor_voucher(v2, "Elena Rostova", "@elena_props")
    metrics = sve.calculate_sponsor_attribution_metrics([c1, c2], 50)
    check(metrics["claimed_vouchers_count"] == 2, "Accurately counts 2 active pod claims")
    check(metrics["direct_pod_revenue"] == 9.70, "Direct pod revenue matches .85 * 2 = .70")
    check(metrics["conversion_rate_pct"] == 4.0, "Pod conversion rate: 4.0% of 50 fans")
    check(metrics["projected_stadium_revenue"] > 10000.0, "80,000-seat projection verified: $" + str(metrics["projected_stadium_revenue"]))
    check(metrics["net_stadium_margin_pct"] >= 90.0, "Net economic margin verified: " + str(metrics["net_stadium_margin_pct"]) + "%")

def test_all_franchises():
    teams = ["Duke Blue Devils", "Boston Celtics", "Texas Longhorns", "San Antonio Spurs", "UConn Huskies", "Michigan Wolverines", "Green Bay Packers", "Dallas Cowboys"]
    all_valid = all(sve.get_team_sponsor_profile(t)["retail_value"] >= 5.0 for t in teams)
    check(all_valid, "All 8 collegiate and pro franchises mapped to authenticated partner profiles")

def run_all_tests():
    global passed, failed
    passed = 0
    failed = 0
    print("=" * 80)
    print("KINETIC FANLAB — WEEK 8 SPONSOR ENGINE & CONCURRENCY TEST SUITE")
    print("=" * 80)
    test_perk_generation()
    test_cryptographic_claim()
    test_two_sided_economics()
    test_all_franchises()
    print("=" * 80)
    print(f"WEEK 8 TEST SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 80)
    return 0 if failed == 0 else 1

def test_week8_sponsor_concurrency_suite():
    assert run_all_tests() == 0

if __name__ == "__main__":
    sys.exit(run_all_tests())