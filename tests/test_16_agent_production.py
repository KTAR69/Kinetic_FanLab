#!/usr/bin/env python3
"""
==============================================================================
Kinetic FanLab — Week 6 Enterprise 16-Agent Production Verification Suite
(`tests/test_16_agent_production.py`)
Verifies:
  1. All 16 Native watsonx Orchestrate YAML Agent Manifests (`agents/*.yaml`)
  2. Supervisor Collaborator Graph (15 cast collaborators wired under Showrunner)
  3. All 4 RAG Knowledge Base Markdown Guides (`data/*.md`)
  4. All 6 Hybrid SQLite + Cloudant Database Tables (`db/fanlab_db.py`)
  5. End-to-End 16-Agent Theatre Production Execution & Chain-of-Thought Audit
  6. Two-Sided Unit Economics (< $0.015/seat cost vs. $4.85 sponsor ROI)
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
from agents.production_cast_runtime import (
    EXPECTED_16_AGENTS,
    load_all_16_agent_manifests,
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

    print("=" * 78)
    print("KINETIC FANLAB — 16-AGENT THEATRE PRODUCTION & DB VERIFICATION SUITE")
    print("=" * 78)

    # 1. Verify 16 YAML Manifests
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
            and bool(m.get("instructions"))
            and isinstance(m.get("tools"), list)
            and len(m.get("tools", [])) >= 1
        )
        check(valid_schema, f"Agent YAML schema valid: agents/{agent_name}.yaml")

    sup_collabs = manifests["supervisor_agent"].get("collaborators", [])
    check(
        len(sup_collabs) == 15,
        f"Supervisor (The Showrunner) wires all 15 cast collaborators ({len(sup_collabs)}/15)",
    )

    # 2. Verify 4 RAG Knowledge Base Files in data/
    print("\n2. RAG Knowledge Base Documents (data/):")
    expected_data_files = [
        "cmi_acoustic_biometric_playbook.md",
        "unit_economics_and_sponsor_roi.md",
        "user_discovery_interview_framework.md",
        "governance_dialect_fairness_policy.md",
    ]
    for df in expected_data_files:
        p = ROOT_DIR / "data" / df
        check(p.exists() and p.stat().st_size > 200, f"Knowledge Base file present & populated: data/{df}")

    # 3. Verify 6-Table Hybrid Database in db/fanlab_db.py
    print("\n3. Hybrid Relational + Cloudant Database Engine (db/fanlab_db.py):")
    db_info = init_fanlab_db()
    counts = db_info["table_counts"]
    check(len(counts) == 6, f"All 6 database tables initialized ({len(counts)}/6)")
    check(counts["fan_passports"] == 8, f"8 canonical fan personas seeded in fan_passports ({counts['fan_passports']}/8)")
    check(
        counts["discovery_feature_matrix"] == 5,
        f"5 discovery features seeded in discovery_feature_matrix ({counts['discovery_feature_matrix']}/5)",
    )

    # 4. Run Full 16-Agent Production Pipeline
    print("\n4. End-to-End 16-Agent Theatre Production Execution (FB-02 Clutch):")
    prod_res = run_full_16_agent_production()
    check(
        prod_res["total_agents_executed"] == 16,
        f"Executed all 16 agents in sequence ({prod_res['total_agents_executed']}/16)",
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

    # 5. Verify Chain-of-Thought Audit Trail in SQLite
    db = get_db()
    audit_rows = db.get_trace_audit_trail(prod_res["trace_id"])
    check(
        len(audit_rows) == 16,
        f"SQL audit_trail recorded all 16 Chain-of-Thought steps for trace {prod_res['trace_id']} ({len(audit_rows)}/16)",
    )

    print("\n" + "=" * 78)
    print(f"VERIFICATION SUMMARY: {passed} PASSED | {failed} FAILED")
    print("=" * 78)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_verification())
