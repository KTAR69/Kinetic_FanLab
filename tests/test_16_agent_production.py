#!/usr/bin/env python3
"""
==============================================================================
Kinetic FanLab — Week 6 Enterprise 16-Agent & 8-Archetype Verification Suite
(`tests/test_16_agent_production.py`)
Verifies:
  1. All 16 Native watsonx Orchestrate YAML Agent Manifests (`agents/*.yaml`)
  2. All 8 Official IBM Agentic AI Archetypes (2-for-1 Redundancy across 16 Agents)
  3. All 8 Python Archetype Classes & Screen 3 Huddle Helper (`orchestrate_agents.py`)
  4. Supervisor Collaborator Graph (15 cast collaborators wired under Showrunner)
  5. All 4 RAG Knowledge Base Markdown Guides (`data/*.md`)
  6. All 6 Hybrid SQLite + Cloudant Database Tables (`db/fanlab_db.py`)
  7. End-to-End 16-Agent Theatre Production Execution & Chain-of-Thought Audit
  8. Two-Sided Unit Economics (< $0.015/seat cost vs. $4.85 sponsor ROI)
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
    EIGHT_IBM_ARCHETYPES,
    CognitiveLoadReducerAgent,
    InvisibleCoordinatorAgent,
    ContextAwareExpertAgent,
    DecisionGatekeeperAgent,
    LongHorizonPlannerAgent,
    KnowledgeSynthesizerAgent,
    HumanAiBoundaryManagerAgent,
    SystemOptimizerAgent,
    FanCoachAgent,
    get_co_captain_huddle,
)
from agents.production_cast_runtime import (
    EXPECTED_16_AGENTS,
    EXPECTED_8_ARCHETYPES,
    load_all_16_agent_manifests,
    verify_8_archetype_coverage,
    unwrap_tool_response,
    run_full_16_agent_production,
)


def run_verification() -> int:
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
    print("KINETIC FANLAB — 16-AGENT CAST & 8 IBM ARCHETYPES VERIFICATION SUITE")
    print("=" * 82)

    # 1. Verify 16 YAML Manifests & 8 Official IBM Archetype Metadata
    print("\n1. Native watsonx Orchestrate YAML Manifests (16 Cast Agents):")
    manifests = load_all_16_agent_manifests()
    check(len(manifests) == 16, f"Loaded all 16 YAML agent manifests ({len(manifests)}/16)")
    for agent_name in EXPECTED_16_AGENTS:
        m = manifests.get(agent_name, {})
        valid_schema = (
            m.get("spec_version") == "v1"
            and m.get("kind") == "native"
            and m.get("name") == agent_name
            and m.get("style") == "react"
            and m.get("ibm_archetype") in EXPECTED_8_ARCHETYPES
            and 1 <= int(m.get("ibm_archetype_id", 0)) <= 8
            and bool(m.get("instructions"))
            and isinstance(m.get("tools"), list)
            and len(m.get("tools", [])) >= 1
        )
        check(
            valid_schema,
            f"YAML valid & mapped to {m.get('ibm_archetype')}: agents/{agent_name}.yaml",
        )

    sup_collabs = manifests["supervisor_agent"].get("collaborators", [])
    check(
        len(sup_collabs) == 15,
        f"Supervisor (The Showrunner) wires all 15 cast collaborators ({len(sup_collabs)}/15)",
    )

    # 2. Verify 2-for-1 Coverage Across All 8 Official IBM Agentic AI Archetypes
    print("\n2. Official 8 IBM Agentic AI Archetypes (Challenge Guide Appendix 1, 2-for-1 Mapping):")
    arch_cov = verify_8_archetype_coverage(manifests)
    check(
        arch_cov["total_archetypes_covered"] == 8 and arch_cov["exact_two_for_one_coverage"],
        f"All 8 IBM Agentic AI Archetypes covered with exact 2-for-1 redundancy ({arch_cov['total_archetypes_covered']}/8)",
    )
    for arch_name, assigned in arch_cov["archetype_agent_map"].items():
        check(
            len(assigned) == 2,
            f"{arch_name} -> {assigned[0]} & {assigned[1]}",
        )

    # 3. Verify Python Archetype Classes & Screen 3 Huddle Helper in orchestrate_agents.py
    print("\n3. Python 8-Archetype Classes & Screen 3 Huddle Integration (orchestrate_agents.py):")
    clr_res = CognitiveLoadReducerAgent().prioritize_and_route("Football", "CLUTCH_SURGE", True, 0.96)
    ic_res = InvisibleCoordinatorAgent("Football").evaluate_game_state("clutch field goal snap")
    cae_res = ContextAwareExpertAgent().coach("Sarah Jenkins", {"role": "Stadium Veteran", "tier": "Tier 5"}, 92.0, True)
    dg_res = DecisionGatekeeperAgent().evaluate_gate(0.0137, 0.0150, 0.953, "APPROVED")
    lhp_res = LongHorizonPlannerAgent().plan_season_milestone("Sarah Jenkins", 62, 75)
    ks_res = KnowledgeSynthesizerAgent("Football").synthesize_telemetry(111.8, 148.0, 14.0, 0.92)
    hab_res = HumanAiBoundaryManagerAgent().evaluate_boundary(0.96, 18.4, "APPROVED")
    so_res = SystemOptimizerAgent("Football").rank_sections_per_capita([{"name": "Section 115", "cmi": 92.0, "checked_in_fans": 150}])
    huddle_res = get_co_captain_huddle("Sarah Jenkins", {"role": "Stadium Veteran", "tier": "Tier 5"}, "Football", 92.0, True)
    check(
        clr_res["proceed"] and ic_res["multiplier"] == 2.0 and "Sarah Jenkins" in cae_res and dg_res["gate_approved"],
        "Archetypes 1-4 (Cognitive Load Reducer, Invisible Coordinator, Context-Aware Expert, Decision Gatekeeper) verified",
    )
    check(
        lhp_res["games_remaining"] == 13 and ks_res["cmi"] == 92.0 and hab_res["autonomous_action_permitted"] and len(so_res["standings"]) == 1 and len(huddle_res["active_ibm_archetypes"]) == 8,
        "Archetypes 5-8 (Long-Horizon Planner, Knowledge Synthesizer, Human-AI Boundary Mgr, System Optimizer) + Huddle verified",
    )

    # 4. Verify 4 RAG Knowledge Base Files in data/
    print("\n4. RAG Knowledge Base Documents (data/):")
    expected_data_files = [
        "cmi_acoustic_biometric_playbook.md",
        "unit_economics_and_sponsor_roi.md",
        "user_discovery_interview_framework.md",
        "governance_dialect_fairness_policy.md",
    ]
    for df in expected_data_files:
        p = ROOT_DIR / "data" / df
        check(p.exists() and p.stat().st_size > 200, f"Knowledge Base file present & populated: data/{df}")

    # 5. Verify 6-Table Hybrid Database in db/fanlab_db.py
    print("\n5. Hybrid Relational + Cloudant Database Engine (db/fanlab_db.py):")
    db_info = init_fanlab_db()
    counts = db_info["table_counts"]
    check(len(counts) == 6, f"All 6 database tables initialized ({len(counts)}/6)")
    check(counts["fan_passports"] == 8, f"8 canonical fan personas seeded in fan_passports ({counts['fan_passports']}/8)")
    check(
        counts["discovery_feature_matrix"] == 5,
        f"5 discovery features seeded in discovery_feature_matrix ({counts['discovery_feature_matrix']}/5)",
    )

    # 6. Run Full 16-Agent Production Pipeline
    print("\n6. End-to-End 16-Agent Theatre Production Execution (FB-02 Clutch):")
    class _SimulatedAdkToolResponse:
        def __init__(self, content):
            self.content = content
    unwrapped_sim = unwrap_tool_response(_SimulatedAdkToolResponse({"guardrail_status": "APPROVED", "cmi_score": 92.0}))
    check(
        isinstance(unwrapped_sim, dict) and unwrapped_sim.get("guardrail_status") == "APPROVED",
        "watsonx Orchestrate ADK ToolResponse wrapper cleanly unwrapped to dict",
    )
    prod_res = run_full_16_agent_production()
    check(
        prod_res["total_agents_executed"] == 16,
        f"Executed all 16 agents in sequence ({prod_res['total_agents_executed']}/16)",
    )
    check(
        prod_res["total_ibm_archetypes_executed"] == 8,
        f"Executed all 8 Official IBM Agentic AI Archetypes in trace ({prod_res['total_ibm_archetypes_executed']}/8)",
    )
    check(
        prod_res["cmi_score"] >= 80.0,
        f"Synthesized Maximum Tier Clutch CMI ({prod_res['cmi_score']}/100)",
    )
    check(
        prod_res["unit_cost_per_seat_usd"] <= 0.0150,
        f"Unit compute cost within ceiling (${prod_res['unit_cost_per_seat_usd']}/seat <= $0.0150)",
    )
    check(
        prod_res["gross_margin_pct"] >= 99.0,
        f"Two-sided Unit Economics Gross Margin verified ({prod_res['gross_margin_pct']}%)",
    )
    check(
        len(prod_res["cos_sha256"]) == 64,
        f"Tamper-evident COS S3 SHA-256 checksum generated ({prod_res['cos_sha256'][:16]}...)",
    )

    # 7. Verify Chain-of-Thought Audit Trail in SQLite
    db = get_db()
    audit_rows = db.get_trace_audit_trail(prod_res["trace_id"])
    check(
        len(audit_rows) == 16,
        f"SQL audit_trail recorded all 16 Chain-of-Thought steps for trace {prod_res['trace_id']} ({len(audit_rows)}/16)",
    )

    print("\n" + "=" * 82)
    print(f"VERIFICATION SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 82)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_verification())
