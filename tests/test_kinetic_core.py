"""
Kinetic FanLab — Week 4 Automated Unit & Regression Test Suite
==============================================================================
Validates:
  1. The 4 canonical CMI benchmark values (contract ground truth)
  2. Static invariance of all 8 member hashes (hash drift detection)
  3. End-to-end multi-agent swarm handoffs
       InvisibleCoordinatorAgent → KnowledgeSynthesizerAgent → SystemOptimizerAgent
  4. Graceful fallback resilience in cloud_storage.py and cloudant_db.py

Run from the Kinetic_FanLab/ directory:
    python -m pytest tests/test_kinetic_core.py -v
==============================================================================
"""

import sys
import os
import json
import unittest

# ---------------------------------------------------------------------------
# Path bootstrap — allow running from any directory
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)  # Kinetic_FanLab/
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------
from orchestrate_agents import (
    compute_cmi_index,
    evaluate_tier,
    InvisibleCoordinatorAgent,
    KnowledgeSynthesizerAgent,
    SystemOptimizerAgent,
)
from telemetry_models import PERSONA_REGISTRY, CANONICAL_FIXTURES
import cloudant_db
import cloud_storage


# ==============================================================================
# Part 1 — Canonical Benchmark Regression Tests
# ==============================================================================

class TestCanonicalBenchmarks(unittest.TestCase):
    """
    Validates the four ground-truth CMI values from AGENTS.md contract.
    Tolerance ±0.05 is used to accommodate floating-point rounding in Python.
    """

    TOLERANCE = 0.05

    FIXTURES = {
        "BB-01": {"db": 82.0,  "hr": 98.0,  "taps": 2.5,  "vu": 0.55, "expected": 37.8, "tier": "Baseline"},
        "BB-02": {"db": 106.5, "hr": 136.0, "taps": 12.2, "vu": 0.85, "expected": 81.9, "tier": "Maximum"},
        "FB-01": {"db": 78.5,  "hr": 105.0, "taps": 3.0,  "vu": 0.60, "expected": 39.0, "tier": "Baseline"},
        "FB-02": {"db": 111.8, "hr": 148.0, "taps": 14.0, "vu": 0.92, "expected": 92.0, "tier": "Maximum"},
    }

    def _assert_cmi(self, fixture_id: str, params: dict) -> None:
        cmi = compute_cmi_index(params["db"], params["hr"], params["taps"], params["vu"])
        self.assertAlmostEqual(
            cmi,
            params["expected"],
            delta=self.TOLERANCE,
            msg=f"[{fixture_id}] CMI mismatch — got {cmi}, expected {params['expected']} ±{self.TOLERANCE}",
        )

    def test_bb01_baseline_cmi(self):
        """BB-01: Basketball baseline free throw → 37.8/100 (Baseline)"""
        self._assert_cmi("BB-01", self.FIXTURES["BB-01"])

    def test_bb02_clutch_cmi(self):
        """BB-02: Basketball clutch free throw → 81.9/100 (Maximum)"""
        self._assert_cmi("BB-02", self.FIXTURES["BB-02"])

    def test_fb01_pre_kick_cmi(self):
        """FB-01: Football pre-kick timeout → 39.0/100 (Baseline)"""
        self._assert_cmi("FB-01", self.FIXTURES["FB-01"])

    def test_fb02_clutch_snap_cmi(self):
        """FB-02: Football clutch 48-yd FG snap → 92.0/100 (Maximum)"""
        self._assert_cmi("FB-02", self.FIXTURES["FB-02"])

    def test_bb_surge_delta(self):
        """Basketball surge delta: BB-02 − BB-01 ≈ +44.1 pts"""
        bb_pre = compute_cmi_index(82.0, 98.0, 2.5, 0.55)
        bb_peak = compute_cmi_index(106.5, 136.0, 12.2, 0.85)
        delta = round(bb_peak - bb_pre, 1)
        self.assertAlmostEqual(delta, 44.1, delta=0.2,
            msg=f"BB surge delta mismatch — got {delta}, expected 44.1")

    def test_fb_surge_delta(self):
        """Football surge delta: FB-02 − FB-01 ≈ +53.0 pts"""
        fb_pre = compute_cmi_index(78.5, 105.0, 3.0, 0.60)
        fb_peak = compute_cmi_index(111.8, 148.0, 14.0, 0.92)
        delta = round(fb_peak - fb_pre, 1)
        self.assertAlmostEqual(delta, 53.0, delta=0.2,
            msg=f"FB surge delta mismatch — got {delta}, expected 53.0")

    def test_tier_mapping_baseline(self):
        """Tier mapping: score < 45 → 'Baseline'"""
        self.assertEqual(evaluate_tier(37.8), "Baseline")
        self.assertEqual(evaluate_tier(39.0), "Baseline")

    def test_tier_mapping_maximum(self):
        """Tier mapping: score ≥ 80 → 'Maximum'"""
        self.assertEqual(evaluate_tier(81.9), "Maximum")
        self.assertEqual(evaluate_tier(92.0), "Maximum")

    def test_canonical_fixtures_match_telemetry_models(self):
        """telemetry_models.CANONICAL_FIXTURES CMI targets must match compute_cmi_index output."""
        for fixture_id, data in CANONICAL_FIXTURES.items():
            db  = data["acoustics"]["db"]
            hr  = data["biometrics"]["hr_bpm"]
            tap = data["taps"]["rate_per_sec"]
            vu  = data["voice"]["urgency"]
            cmi_computed = compute_cmi_index(db, hr, tap, vu)
            cmi_target   = data["cmi_target"]
            self.assertAlmostEqual(
                cmi_computed,
                cmi_target,
                delta=self.TOLERANCE,
                msg=f"[{fixture_id}] telemetry_models target {cmi_target} ≠ computed {cmi_computed}",
            )


# ==============================================================================
# Part 2 — Member Hash Static Invariance Tests
# ==============================================================================

class TestMemberHashInvariance(unittest.TestCase):
    """
    All 8 member hashes are immutable contract values.
    Any drift in these strings is a critical regression.
    """

    EXPECTED_HASHES = {
        "Marcus Vance":  "0xMV-sec114-8f7a2",
        "Elena Rostova": "0xER-sec114-3c9b1",
        "Devon Miller":  "0xDM-sec114-6d4e8",
        "Jordan Lee":    "0xJL-sec114-1f4a9",
        "Sarah Jenkins": "0xSJ-sec115-7b2a5",
        "Carlos Mendez": "0xCM-sec115-4e8f9",
        "Maya Patel":    "0xMP-sec115-1a5c3",
        "Alex Taylor":   "0xAT-sec115-5c2d3",
    }

    def test_telemetry_models_hashes(self):
        """PERSONA_REGISTRY in telemetry_models.py contains all 8 correct hashes."""
        for name, expected_hash in self.EXPECTED_HASHES.items():
            with self.subTest(member=name):
                self.assertIn(name, PERSONA_REGISTRY,
                    msg=f"{name} missing from PERSONA_REGISTRY")
                actual = PERSONA_REGISTRY[name].get("hash")
                self.assertEqual(
                    actual,
                    expected_hash,
                    msg=f"Hash drift for {name}: got '{actual}', expected '{expected_hash}'",
                )

    def test_cloudant_module_hashes(self):
        """cloudant_db._MEMBER_HASHES contains all 8 correct hashes."""
        db_hashes = cloudant_db._MEMBER_HASHES  # type: ignore[attr-defined]
        for name, expected_hash in self.EXPECTED_HASHES.items():
            with self.subTest(member=name):
                self.assertIn(name, db_hashes,
                    msg=f"{name} missing from cloudant_db._MEMBER_HASHES")
                self.assertEqual(
                    db_hashes[name],
                    expected_hash,
                    msg=f"cloudant_db hash drift for {name}: got '{db_hashes[name]}', expected '{expected_hash}'",
                )

    def test_hashes_are_immutable_after_save(self):
        """
        save_member_passport must silently overwrite any supplied hash
        with the canonical value — enforcing immutability on every write.
        """
        member = "Marcus Vance"
        tampered = {"member_hash": "TAMPERED-HASH", "respect_taps": 999}
        cloudant_db.save_member_passport(member, tampered)
        passport = cloudant_db.load_member_passport(member)
        self.assertEqual(
            passport["member_hash"],
            self.EXPECTED_HASHES[member],
            msg="save_member_passport did not enforce hash immutability",
        )


# ==============================================================================
# Part 3 — Multi-Agent Swarm Handoff Tests
# ==============================================================================

class TestMultiAgentSwarmHandoffs(unittest.TestCase):
    """
    End-to-end handoff chain:
    InvisibleCoordinatorAgent → KnowledgeSynthesizerAgent → SystemOptimizerAgent
    """

    def setUp(self):
        self.coordinator_bb  = InvisibleCoordinatorAgent(sport="Basketball")
        self.coordinator_fb  = InvisibleCoordinatorAgent(sport="Football")
        self.synthesizer     = KnowledgeSynthesizerAgent()
        self.optimizer_bb    = SystemOptimizerAgent(sport="Basketball")
        self.optimizer_fb    = SystemOptimizerAgent(sport="Football")

    # ------------------------------------------------------------------
    # InvisibleCoordinatorAgent
    # ------------------------------------------------------------------

    def test_coordinator_basketball_clutch_state(self):
        """Coordinator detects clutch state for basketball free throw context."""
        result = self.coordinator_bb.evaluate_game_state("opponent clutch free throw")
        self.assertTrue(result["clutch_active"],
            "Coordinator must activate clutch for 'clutch free throw' context")
        self.assertEqual(result["multiplier"], 2.0)
        self.assertEqual(result["sport"], "Basketball")
        self.assertIn("agent", result)
        self.assertEqual(result["agent"], "InvisibleCoordinator")

    def test_coordinator_football_timeout_state(self):
        """Coordinator returns pacing directive for football timeout/icing context."""
        result = self.coordinator_fb.evaluate_game_state("timeout ice the kicker")
        self.assertFalse(result["clutch_active"])
        self.assertEqual(result["multiplier"], 1.25)
        self.assertIn("Stomp", result["pacing_directive"])

    def test_coordinator_football_clutch_snap(self):
        """Coordinator activates full clutch for 'field goal snap' context."""
        result = self.coordinator_fb.evaluate_game_state("clutch field goal snap")
        self.assertTrue(result["clutch_active"])
        self.assertEqual(result["multiplier"], 2.0)

    def test_coordinator_output_has_required_keys(self):
        """Coordinator output dict must contain all required handoff keys."""
        required_keys = {"agent", "sport", "clutch_active", "multiplier",
                         "tactic", "pacing_directive", "trigger_event", "timestamp"}
        result = self.coordinator_bb.evaluate_game_state("regular possession")
        self.assertTrue(required_keys.issubset(result.keys()),
            f"Missing keys: {required_keys - result.keys()}")

    # ------------------------------------------------------------------
    # KnowledgeSynthesizerAgent
    # ------------------------------------------------------------------

    def test_synthesizer_cmi_bb02_passthrough(self):
        """Synthesizer produces BB-02 canonical CMI from raw telemetry inputs."""
        result = self.synthesizer.synthesize_telemetry(106.5, 136.0, 12.2, 0.85)
        self.assertAlmostEqual(result["cmi"], 81.9, delta=0.05)
        self.assertEqual(result["tier"], "Maximum")
        self.assertEqual(result["agent"], "KnowledgeSynthesizer")

    def test_synthesizer_cmi_fb02_passthrough(self):
        """Synthesizer produces FB-02 canonical CMI from raw telemetry inputs."""
        result = self.synthesizer.synthesize_telemetry(111.8, 148.0, 14.0, 0.92)
        self.assertAlmostEqual(result["cmi"], 92.0, delta=0.05)
        self.assertEqual(result["tier"], "Maximum")

    def test_synthesizer_voice_approved(self):
        """Synthesizer approves clean fan transcript and returns urgency score."""
        result = self.synthesizer.evaluate_voice_outburst("BLOCK THAT KICK! RATTLE THE KICKER!")
        self.assertEqual(result["governance_status"], "APPROVED")
        self.assertGreater(result["urgency_score"], 0.0)
        self.assertEqual(len(result["violations"]), 0)

    def test_synthesizer_voice_rejected_pii(self):
        """Synthesizer rejects transcript containing a PII indicator."""
        result = self.synthesizer.evaluate_voice_outburst("Contact me at user@gmail.com")
        self.assertEqual(result["governance_status"], "REJECTED")
        self.assertGreater(len(result["violations"]), 0)
        self.assertEqual(result["urgency_score"], 0.0)

    def test_synthesizer_normalized_components_sum(self):
        """Synthesizer normalized_components weighted sum ≈ CMI value."""
        result = self.synthesizer.synthesize_telemetry(106.5, 136.0, 12.2, 0.85)
        components = result["normalized_components"]
        approx_cmi = (
            components["acoustic_pct"]
            + components["biometric_pct"]
            + components["taps_pct"]
            + components["urgency_pct"]
        )
        self.assertAlmostEqual(approx_cmi, result["cmi"], delta=0.2,
            msg="Normalized component sum diverges from top-level CMI")

    # ------------------------------------------------------------------
    # SystemOptimizerAgent
    # ------------------------------------------------------------------

    def test_optimizer_section_ranking(self):
        """Optimizer ranks sections correctly and returns chaser alert."""
        sections = [
            {"name": "Section 114", "cmi": 81.9, "checked_in_fans": 150,
             "early_multiplier": 1.25, "clutch_multiplier": 2.0},
            {"name": "Section 115", "cmi": 78.4, "checked_in_fans": 150,
             "early_multiplier": 1.0,  "clutch_multiplier": 1.0},
        ]
        result = self.optimizer_bb.rank_sections_per_capita(sections)
        self.assertEqual(result["agent"], "SystemOptimizer")
        self.assertEqual(result["leader"], "Section 114")
        self.assertIn("CHASER ALERT", result["chaser_alert"])
        self.assertEqual(result["standings"][0]["section"], "Section 114")

    def test_optimizer_reality_delta_bb(self):
        """Optimizer reality delta correctly computes surge and wraps storycard."""
        result = self.optimizer_bb.generate_reality_delta(
            outcome_label="MISSED FREE THROW",
            pre_cmi=37.8,
            peak_cmi=81.9,
            fan_notes=["MISS IT! OFF THE RIM!"],
        )
        self.assertAlmostEqual(result["surge_delta"], 44.1, delta=0.15)
        self.assertTrue(result["defense_belt_awarded"])
        self.assertIn("Section 114", result["winning_section"])

    def test_optimizer_reality_delta_fb(self):
        """Optimizer reality delta correctly computes FB surge and storycard."""
        result = self.optimizer_fb.generate_reality_delta(
            outcome_label="MISSED FIELD GOAL",
            pre_cmi=39.0,
            peak_cmi=92.0,
            fan_notes=["BLOCK THAT KICK!"],
        )
        self.assertAlmostEqual(result["surge_delta"], 53.0, delta=0.15)
        self.assertIn("Section 115", result["winning_section"])

    # ------------------------------------------------------------------
    # Full end-to-end pipeline chain handoff
    # ------------------------------------------------------------------

    def test_end_to_end_bb_pipeline(self):
        """
        Full BB handoff: Coordinator → Synthesizer → Optimizer
        Asserts each agent output feeds correctly into the next.
        """
        # Step 1: Coordinator evaluates game state
        coord_out = self.coordinator_bb.evaluate_game_state("clutch free throw, 0.4s left")
        self.assertTrue(coord_out["clutch_active"])

        # Step 2: Synthesizer fuses telemetry
        synth_out = self.synthesizer.synthesize_telemetry(106.5, 136.0, 12.2, 0.85)
        self.assertAlmostEqual(synth_out["cmi"], 81.9, delta=0.05)

        # Step 3: Optimizer ranks and generates reality delta
        optim_out = self.optimizer_bb.generate_reality_delta(
            outcome_label="MISSED FREE THROW",
            pre_cmi=37.8,
            peak_cmi=synth_out["cmi"],
            fan_notes=["MISS IT! OFF THE RIM!"],
        )
        self.assertGreater(optim_out["surge_delta"], 0)
        self.assertIn("granite_narrative", optim_out)

    def test_end_to_end_fb_pipeline(self):
        """
        Full FB handoff: Coordinator → Synthesizer → Optimizer
        """
        coord_out = self.coordinator_fb.evaluate_game_state("clutch field goal snap")
        self.assertTrue(coord_out["clutch_active"])

        synth_out = self.synthesizer.synthesize_telemetry(111.8, 148.0, 14.0, 0.92)
        self.assertAlmostEqual(synth_out["cmi"], 92.0, delta=0.05)

        optim_out = self.optimizer_fb.generate_reality_delta(
            outcome_label="MISSED FIELD GOAL",
            pre_cmi=39.0,
            peak_cmi=synth_out["cmi"],
            fan_notes=["BLOCK THAT KICK!"],
        )
        self.assertGreater(optim_out["surge_delta"], 0)


# ==============================================================================
# Part 4 — Cloud Services Graceful Fallback Resilience Tests
# ==============================================================================

class TestCloudStorageFallback(unittest.TestCase):
    """
    Verifies cloud_storage.py falls back to local archive when COS is not configured.
    Tests run without any COS credentials (the default dev/CI environment).
    """

    def test_archive_crowd_box_score_local_fallback(self):
        """archive_crowd_box_score must succeed and return ARCHIVED_LOCALLY status."""
        receipt = cloud_storage.archive_crowd_box_score(
            fixture_id="BB-02",
            sport="Basketball",
            cmi=81.9,
            surge=44.1,
            winning_section="Section 114 (Thunder Row)",
            fan_contribution={"tap_count": 32, "peak_hr_bpm": 136, "peak_db": 106.5},
        )
        self.assertIn("status", receipt)
        self.assertIn("ARCHIVED", receipt["status"].upper(),
            msg=f"Unexpected status: {receipt['status']}")
        self.assertIn("bucket", receipt)
        self.assertIn("object_key", receipt)
        self.assertIn("crypto_timestamp", receipt)

    def test_archive_proof_card_local_fallback(self):
        """archive_proof_of_momentum_card must succeed and return ARCHIVED_LOCALLY status."""
        receipt = cloud_storage.archive_proof_of_momentum_card(
            fixture_id="FB-02",
            sport="Football",
            points="+53.0 PTS",
            outcome="MISSED FIELD GOAL (Wide Left)",
            narrative="111.8 dB sustained roar across 148 BPM cardiac stress disrupted kicker cadence.",
        )
        self.assertIn("status", receipt)
        self.assertIn("ARCHIVED", receipt["status"].upper())

    def test_object_key_contains_fixture_id(self):
        """Object key must embed the fixture_id for traceability."""
        receipt = cloud_storage.archive_crowd_box_score(
            fixture_id="TEST-FIXTURE-99",
            sport="Basketball",
            cmi=50.0,
            surge=10.0,
            winning_section="Section 114",
            fan_contribution={},
        )
        self.assertIn("TEST-FIXTURE-99", receipt["object_key"])

    def test_crypto_timestamp_format(self):
        """Crypto timestamp must contain ISO-like date/time segment and a '#' separator."""
        receipt = cloud_storage.archive_crowd_box_score(
            fixture_id="TS-TEST",
            sport="Football",
            cmi=75.0,
            surge=20.0,
            winning_section="Section 115",
            fan_contribution={},
        )
        ts = receipt["crypto_timestamp"]
        self.assertIn("T", ts, msg="Crypto timestamp missing ISO-8601 'T' separator")
        self.assertIn("#", ts, msg="Crypto timestamp missing SHA-256 '#' suffix")


class TestCloudantFallback(unittest.TestCase):
    """
    Verifies cloudant_db.py falls back to local JSON cache when Cloudant is not configured.
    """

    def test_load_member_passport_returns_dict(self):
        """load_member_passport returns a dict with member_hash and respect_taps."""
        for name in ["Marcus Vance", "Sarah Jenkins"]:
            with self.subTest(member=name):
                passport = cloudant_db.load_member_passport(name)
                self.assertIsInstance(passport, dict)
                self.assertIn("member_hash", passport)
                self.assertIn("respect_taps", passport)

    def test_load_unknown_member_returns_default(self):
        """load_member_passport for an unknown member returns a default passport (no crash)."""
        passport = cloudant_db.load_member_passport("Unknown Fan 999")
        self.assertIsInstance(passport, dict)
        self.assertIn("member_hash", passport)

    def test_increment_respect_tap_increases_count(self):
        """increment_respect_tap must return a value > previous total."""
        name = "Jordan Lee"
        before = cloudant_db.load_member_passport(name).get("respect_taps", 0)
        new_total = cloudant_db.increment_respect_tap(name, 1)
        self.assertEqual(new_total, before + 1,
            msg=f"Expected {before + 1}, got {new_total}")

    def test_save_and_reload_passport_roundtrip(self):
        """save_member_passport persists a custom field that load_member_passport retrieves."""
        name = "Devon Miller"
        passport = cloudant_db.load_member_passport(name)
        passport["test_flag"] = "week4_regression"
        cloudant_db.save_member_passport(name, passport)
        reloaded = cloudant_db.load_member_passport(name)
        self.assertEqual(reloaded.get("test_flag"), "week4_regression")

    def test_hash_enforced_on_save(self):
        """
        Even when tampered hash is passed to save_member_passport,
        the loaded passport must still carry the canonical hash.
        """
        name = "Elena Rostova"
        passport = {"member_hash": "SHOULD-BE-OVERWRITTEN", "respect_taps": 100}
        cloudant_db.save_member_passport(name, passport)
        reloaded = cloudant_db.load_member_passport(name)
        self.assertEqual(
            reloaded["member_hash"],
            "0xER-sec114-3c9b1",
            msg="Cloudant module failed to enforce hash immutability",
        )


# ==============================================================================
# Test runner entrypoint
# ==============================================================================

if __name__ == "__main__":
    print("=" * 85)
    print("  KINETIC FANLAB — WEEK 4 AUTOMATED REGRESSION SUITE")
    print("=" * 85)
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    # Register all test classes in execution order
    for klass in [
        TestCanonicalBenchmarks,
        TestMemberHashInvariance,
        TestMultiAgentSwarmHandoffs,
        TestCloudStorageFallback,
        TestCloudantFallback,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(klass))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 85)
    print(f"  TESTS RUN: {result.testsRun}  |  FAILURES: {len(result.failures)}  |  ERRORS: {len(result.errors)}")
    status = "ALL TESTS PASSED ✓" if result.wasSuccessful() else "REGRESSIONS DETECTED ✗"
    print(f"  STATUS: {status}")
    print("  Powered by IBM watsonx & Granite Foundation Models")
    print("=" * 85)
