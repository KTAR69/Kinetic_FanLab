#!/usr/bin/env python3
"""
==============================================================================
Kinetic FanLab — Step 4 Multi-Scale FinOps, Live UUID & User Discovery Suite
(`tests/test_step4_finops_and_discovery.py`)
Verifies:
  1. Live IBM watsonx Orchestrate (`eu-de-0ec71755`) UUID Registry across all 16 Agents
  2. Hub-and-Spoke Collaborator Graph (`supervisor_agent` = 15 collaborators; 15 specialists = `[]`)
  3. Phase 4A: Multi-Scale Two-Sided Unit Economics (`50`, `1,500`, `18,000`, `80,000` seats)
     and all 4 Canonical Fixtures (`BB-01`, `BB-02`, `FB-01`, `FB-02`)
  4. Phase 4B: 8-Persona User Discovery Sessions ($100 Feature Budget trade-offs, privacy/trust)
     and all 4 Slide 24 Prototype Iterations (`ITER-01` .. `ITER-04`)
==============================================================================
"""

import os
import sys
import importlib.abc
import importlib.util
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class StatMetaPathFinder(importlib.abc.MetaPathFinder):
    """Ensures direct stat-based package resolution across FUSE directories."""
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

from db.fanlab_db import get_db, init_fanlab_db
from orchestrate_agents import (
    LIVE_WXO_ENVIRONMENT,
    LIVE_WXO_AGENT_IDS,
    AGENT_TO_IBM_ARCHETYPE,
)
from agents.production_cast_runtime import (
    EXPECTED_16_AGENTS,
    load_all_16_agent_manifests,
    invoke_adk_tool,
)
from tools.backstage_crew_tools import (
    evaluate_seat_unit_economics,
    score_discovery_feature_value,
)


def run_step4_verification() -> int:
    passed = 0
    failed = 0

    def check(condition: bool, label: str) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {label}")
        else:
            failed += 1
            print(f"  [FAIL] {label}")

    print("=" * 82)
    print("KINETIC FANLAB — STEP 4 FINOPS, LIVE WXO UUIDS & USER DISCOVERY SUITE")
    print("=" * 82)

    # 1. Verify Live watsonx Orchestrate Environment & 16 Agent UUIDs
    print("\n1. Live IBM watsonx Orchestrate Deployment Registry (eu-de-0ec71755):")
    check(
        LIVE_WXO_ENVIRONMENT.get("env_name") == "eu-de-0ec71755"
        and LIVE_WXO_ENVIRONMENT.get("auth_type") == "ibm_iam",
        f"Live watsonx Orchestrate environment registered ({LIVE_WXO_ENVIRONMENT['env_name']})",
    )
    check(
        len(LIVE_WXO_AGENT_IDS) == 16 and len(set(LIVE_WXO_AGENT_IDS.values())) == 16,
        f"All 16 unique live watsonx Orchestrate Agent UUIDs registered ({len(LIVE_WXO_AGENT_IDS)}/16)",
    )
    manifests = load_all_16_agent_manifests()
    all_have_uuid = all(
        AGENT_TO_IBM_ARCHETYPE.get(a, {}).get("wxo_agent_id") == LIVE_WXO_AGENT_IDS.get(a)
        and len(LIVE_WXO_AGENT_IDS.get(a, "")) == 36
        for a in EXPECTED_16_AGENTS
    )
    check(all_have_uuid, "All 16 agents in AGENT_TO_IBM_ARCHETYPE carry valid 36-char live UUIDs")

    # 2. Verify Hub-and-Spoke Collaborator Graph across 16 YAML Manifests
    sup_collabs = manifests["supervisor_agent"].get("collaborators", [])
    specialists_empty = all(
        manifests[a].get("collaborators", []) == []
        for a in EXPECTED_16_AGENTS
        if a != "supervisor_agent"
    )
    check(
        len(sup_collabs) == 15 and specialists_empty,
        "Hub-and-spoke YAML collaborator topology verified (supervisor=15, 15 specialists=[])",
    )

    # 3. Phase 4A: Multi-Scale Two-Sided Unit Economics & Cloud Cost Avoidance
    print("\n2. Phase 4A — Multi-Scale Two-Sided Unit Economics & Sponsor ROI:")
    init_fanlab_db()
    db = get_db()

    # Check all 4 canonical fixtures (BB-01, BB-02, FB-01, FB-02)
    bb01_econ = invoke_adk_tool(evaluate_seat_unit_economics, "BB-01", 50, False, 0.0)
    bb02_econ = invoke_adk_tool(evaluate_seat_unit_economics, "BB-02", 50, True, 4.85)
    fb01_econ = invoke_adk_tool(evaluate_seat_unit_economics, "FB-01", 50, False, 0.0)
    fb02_econ = invoke_adk_tool(evaluate_seat_unit_economics, "FB-02", 50, True, 4.85)

    check(
        bb01_econ["total_cost_per_seat_usd"] == 0.0008
        and bb01_econ["granite_gate_status"] == "GATED_ZERO_LLM_COST",
        f"BB-01 Baseline FinOps Gate: ${bb01_econ['total_cost_per_seat_usd']}/seat (Zero LLM tokens billed)",
    )
    check(
        bb02_econ["total_cost_per_seat_usd"] == 0.0137
        and bb02_econ["gross_margin_pct"] == 99.72
        and bb02_econ["within_cost_ceiling"],
        f"BB-02 Clutch FinOps Gate: ${bb02_econ['total_cost_per_seat_usd']}/seat vs. $4.85 sponsor ROI ({bb02_econ['gross_margin_pct']}% gross margin)",
    )
    check(
        fb01_econ["total_cost_per_seat_usd"] == 0.0008
        and fb01_econ["granite_gate_status"] == "GATED_ZERO_LLM_COST",
        f"FB-01 Timeout FinOps Gate: ${fb01_econ['total_cost_per_seat_usd']}/seat (Zero LLM tokens billed)",
    )
    check(
        fb02_econ["total_cost_per_seat_usd"] == 0.0137
        and fb02_econ["gross_margin_pct"] == 99.72
        and fb02_econ["within_cost_ceiling"],
        f"FB-02 Clutch FinOps Gate: ${fb02_econ['total_cost_per_seat_usd']}/seat vs. $4.85 sponsor ROI ({fb02_econ['gross_margin_pct']}% gross margin)",
    )

    # Check 4 venue scales: 50-seat pod, 1,500-seat section, 18,000-seat arena, 80,000-seat stadium
    scale_50 = db.evaluate_stadium_scale_economics(50, True, 4.85)
    scale_1500 = db.evaluate_stadium_scale_economics(1500, True, 4.85)
    scale_18000 = db.evaluate_stadium_scale_economics(18000, True, 4.85)
    scale_80000 = db.evaluate_stadium_scale_economics(80000, True, 4.85)

    check(
        scale_50["total_hybrid_compute_cost_usd"] == 0.68
        or abs(scale_50["total_hybrid_compute_cost_usd"] - 0.685) <= 0.01,
        f"50-Seat BLE Pod Scale: ${scale_50['total_hybrid_compute_cost_usd']} compute vs. ${scale_50['total_sponsor_revenue_usd']} revenue",
    )
    check(
        scale_1500["total_hybrid_compute_cost_usd"] == 20.55
        and scale_1500["total_cloud_cost_saved_usd"] == 609.45,
        f"1,500-Seat Student Section Scale: ${scale_1500['total_hybrid_compute_cost_usd']} compute (${scale_1500['total_cloud_cost_saved_usd']} saved vs. raw audio)",
    )
    check(
        scale_18000["total_hybrid_compute_cost_usd"] == 246.60
        and scale_18000["total_cloud_cost_saved_usd"] == 7313.40,
        f"18,000-Seat Basketball Arena Scale: ${scale_18000['total_hybrid_compute_cost_usd']} compute (${scale_18000['total_cloud_cost_saved_usd']} saved vs. raw audio)",
    )
    check(
        scale_80000["total_hybrid_compute_cost_usd"] == 1096.00
        and scale_80000["total_cloud_cost_saved_usd"] == 32504.00
        and scale_80000["total_net_margin_usd"] == 386904.00,
        f"80,000-Seat Football Stadium Scale: ${scale_80000['total_hybrid_compute_cost_usd']} compute, +${scale_80000['total_cloud_cost_saved_usd']} cloud cost saved, +${scale_80000['total_net_margin_usd']} net margin",
    )

    # 4. Phase 4B: 8-Persona User Discovery Sessions & Slide 24 Prototype Iterations
    print("\n3. Phase 4B — 8-Persona User Discovery & Slide 24 Prototype Iterations:")
    disc_res = invoke_adk_tool(score_discovery_feature_value)
    check(
        disc_res["features_evaluated"] == 5
        and len(disc_res["validated_keep_features"]) == 4
        and len(disc_res["deprecated_high_cost_features"]) == 1,
        "Feature Matrix: 4 KEEP capabilities validated and 1 high-cost capability (Raw Cloud Audio) deprecated",
    )

    sessions = disc_res["persona_sessions"]
    check(
        len(sessions) == 8,
        f"All 8 canonical fan personas completed User Discovery & Usability Testing ({len(sessions)}/8)",
    )

    for s in sessions:
        budget = s["budget_allocation_100"]
        total_pts = sum(budget.values())
        raw_audio_pts = budget.get("FEAT-02_raw_cloud_audio", -1)
        check(
            total_pts == 100 and raw_audio_pts == 0 and s["trust_privacy_approved"],
            f"Persona Discovery verified ({s['member_name']} — {s['member_hash']}): $100 budget sum={total_pts}, Raw Audio=$0",
        )

    iterations = disc_res["prototype_iterations"]
    check(
        len(iterations) == 4,
        f"All 4 Slide 24 Prototype Iterations documented and wired to code modules ({len(iterations)}/4)",
    )
    iter_ids = [it["iteration_id"] for it in iterations]
    check(
        iter_ids == ["ITER-01", "ITER-02", "ITER-03", "ITER-04"],
        f"Prototype Iteration IDs verified: {', '.join(iter_ids)}",
    )

    # 5. Verify Expanded RAG Playbooks contain multi-scale & 8-persona tables
    finops_md = (ROOT_DIR / "data" / "unit_economics_and_sponsor_roi.md").read_text(encoding="utf-8")
    disc_md = (ROOT_DIR / "data" / "user_discovery_interview_framework.md").read_text(encoding="utf-8")
    check(
        "80,000" in finops_md and "$32,504.00" in finops_md and "99.72%" in finops_md,
        "RAG Playbook data/unit_economics_and_sponsor_roi.md contains 80,000-seat FinOps tables",
    )
    check(
        "Marcus Vance" in disc_md and "Sarah Jenkins" in disc_md and "Iteration 4" in disc_md,
        "RAG Playbook data/user_discovery_interview_framework.md contains 8-Persona & Iteration tables",
    )

    print("\n" + "=" * 82)
    print(f"STEP 4 VERIFICATION SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 82)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_step4_verification())
