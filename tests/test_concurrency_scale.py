"""
==============================================================================
Kinetic FanLab — Multi-Agent Concurrency & Performance Load Benchmark
Week 5 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Simulates large-scale in-venue telemetry ingestion across 1,600 BLE mesh
cluster heads (representing 80,000 spectators organized in 50-seat pods).
Benchmarks the 3 IBM Agentic AI Archetypes:
1. Invisible Coordinator (Pacing & Clutch Multipliers)
2. Knowledge Synthesizer (Multimodal Telemetry Fusion & CMI Normalization)
3. System Optimizer (Per-Capita Section Standings & Chaser Alerts)
==============================================================================
"""

import os
import sys
import time
import math
import random
import statistics
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure root directory is in Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestrate_agents import (
    InvisibleCoordinatorAgent,
    KnowledgeSynthesizerAgent,
    SystemOptimizerAgent,
    compute_cmi_index,
    normalize_signal,
    evaluate_tier
)

# Canonical Invariant Benchmarks (Ground Truth)
BENCHMARKS = {
    "BB-01": {"sport": "Basketball", "situation": "Opponent Free Throw 1 (Baseline)", "db": 82.0, "hr": 98.0, "taps": 2.5, "vu": 0.55, "expected_cmi": 37.8},
    "BB-02": {"sport": "Basketball", "situation": "Opponent Free Throw 2 (Clutch)", "db": 106.5, "hr": 136.0, "taps": 12.2, "vu": 0.85, "expected_cmi": 81.9},
    "FB-01": {"sport": "Football", "situation": "Pre-Kick Timeout (Baseline)", "db": 78.5, "hr": 105.0, "taps": 3.0, "vu": 0.60, "expected_cmi": 39.0},
    "FB-02": {"sport": "Football", "situation": "48-Yard Field Goal Snap (Clutch)", "db": 111.8, "hr": 148.0, "taps": 14.0, "vu": 0.92, "expected_cmi": 92.0},
}

class VenueConcurrencyHarness:
    """
    Simulates high-density stadium wireless telemetry ingestion.
    Models 1,600 BLE mesh cluster heads streaming aggregated pod packets at 2.0 Hz (every 500 ms).
    """

    def __init__(self, num_pods: int = 1600, seats_per_pod: int = 50):
        self.num_pods = num_pods
        self.seats_per_pod = seats_per_pod
        self.total_fans = num_pods * seats_per_pod

        # Initialize the 3 Archetype agents
        self.bb_coordinator = InvisibleCoordinatorAgent("Basketball")
        self.fb_coordinator = InvisibleCoordinatorAgent("Football")
        self.synthesizer = KnowledgeSynthesizerAgent()
        self.optimizer_bb = SystemOptimizerAgent("Basketball")
        self.optimizer_fb = SystemOptimizerAgent("Football")

    def generate_pod_packet(self, pod_idx: int, is_clutch: bool, sport: str) -> Dict[str, Any]:
        """Generates a realistic 500ms telemetry packet from a BLE mesh cluster head."""
        section_name = "Section 114" if sport == "Basketball" else "Section 115"
        pod_id = f"POD-{sport[:2].upper()}-{pod_idx:04d}"

        if not is_clutch:
            # Baseline ambient noise
            db = round(random.gauss(80.0, 2.5), 1)
            hr = round(random.gauss(100.0, 4.0), 1)
            taps = round(max(0.0, random.gauss(2.8, 0.5)), 1)
            vu = round(min(1.0, max(0.0, random.gauss(0.58, 0.04))), 2)
            situation = "Regular Game Action"
        else:
            # Clutch defensive pressure state
            if sport == "Basketball":
                db = round(min(115.0, random.gauss(106.5, 2.0)), 1)
                hr = round(min(160.0, random.gauss(136.0, 3.5)), 1)
                taps = round(min(15.0, random.gauss(12.2, 0.8)), 1)
                vu = round(min(1.0, random.gauss(0.85, 0.03)), 2)
                situation = "Opponent Free Throw 2 (Clutch)"
            else:
                db = round(min(115.0, random.gauss(111.8, 1.8)), 1)
                hr = round(min(160.0, random.gauss(148.0, 4.0)), 1)
                taps = round(min(15.0, random.gauss(14.0, 0.6)), 1)
                vu = round(min(1.0, random.gauss(0.92, 0.03)), 2)
                situation = "48-Yard Field Goal Snap (Clutch)"

        return {
            "pod_id": pod_id,
            "section_id": section_name,
            "sport": sport,
            "seat_count": self.seats_per_pod,
            "situation": situation,
            "is_clutch": is_clutch,
            "db": db,
            "hr": hr,
            "taps": taps,
            "vu": vu,
            "timestamp": time.time()
        }

    def process_single_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the multi-agent pipeline for a single telemetry packet:
        1. Invisible Coordinator: evaluates game state & multiplier
        2. Knowledge Synthesizer: computes CMI & classifies tier
        """
        t0 = time.perf_counter()

        # Step 1: Coordinator
        coordinator = self.bb_coordinator if packet["sport"] == "Basketball" else self.fb_coordinator
        coord_state = coordinator.evaluate_game_state(packet["situation"])

        # Step 2: Synthesizer
        synth_result = self.synthesizer.synthesize_telemetry(
            db=packet["db"],
            hr=packet["hr"],
            taps=packet["taps"],
            vu=packet["vu"]
        )

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "pod_id": packet["pod_id"],
            "section_id": packet["section_id"],
            "cmi": synth_result["cmi"],
            "tier": synth_result["tier"],
            "energy_multiplier": coord_state.get("multiplier", 1.0),
            "pacing_directive": coord_state.get("pacing_directive", ""),
            "latency_ms": elapsed_ms
        }

    def run_concurrency_benchmark(self, num_packets: int = 10000, max_workers: int = 32) -> Dict[str, Any]:
        """Executes a high-concurrency stress test simulating parallel cluster-head transmissions."""
        print(f"\n================================================================================")
        print(f"🚀 INITIATING CONCURRENCY LOAD TEST: {num_packets:,} PACKETS | {max_workers} WORKERS")
        print(f"🏟️ Modeled Venue: {self.total_fans:,} Fans across {self.num_pods:,} BLE Mesh Pods (50 seats/pod)")
        print(f"================================================================================")

        packets = []
        for i in range(num_packets):
            sport = "Football" if (i % 2 == 0) else "Basketball"
            is_clutch = (i % 3 == 0)  # ~33% clutch bursts
            packets.append(self.generate_pod_packet(i % self.num_pods, is_clutch, sport))

        latencies = []
        cmi_values = []
        tiers = {"Baseline": 0, "Moderate": 0, "High": 0, "Maximum": 0}

        start_time = time.perf_counter()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(self.process_single_packet, p): i for i, p in enumerate(packets)}
            for future in as_completed(future_to_idx):
                res = future.result()
                latencies.append(res["latency_ms"])
                cmi_values.append(res["cmi"])
                tiers[res["tier"]] += 1

        total_elapsed_s = time.perf_counter() - start_time
        throughput_ops = num_packets / total_elapsed_s

        latencies.sort()
        p50 = statistics.median(latencies)
        p90 = latencies[int(len(latencies) * 0.90)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        max_lat = max(latencies)
        avg_lat = statistics.mean(latencies)

        sub_100ms_compliance = p99 < 100.0
        cmi_bounds_valid = all(0.0 <= c <= 100.0 for c in cmi_values)

        results = {
            "num_packets": num_packets,
            "max_workers": max_workers,
            "total_elapsed_s": round(total_elapsed_s, 4),
            "throughput_ops_per_sec": round(throughput_ops, 1),
            "avg_latency_ms": round(avg_lat, 4),
            "p50_latency_ms": round(p50, 4),
            "p90_latency_ms": round(p90, 4),
            "p95_latency_ms": round(p95, 4),
            "p99_latency_ms": round(p99, 4),
            "max_latency_ms": round(max_lat, 4),
            "sub_100ms_compliance": sub_100ms_compliance,
            "cmi_bounds_valid": cmi_bounds_valid,
            "tier_distribution": tiers
        }

        print(f"\n📊 BENCHMARK RESULTS:")
        print(f"  • Ingestion Throughput:   {throughput_ops:,.1f} packets/second")
        print(f"  • Total Elapsed Time:     {total_elapsed_s:.3f} seconds")
        print(f"  • Average Latency:        {avg_lat:.4f} ms")
        print(f"  • p50 (Median) Latency:   {p50:.4f} ms")
        print(f"  • p95 Latency:            {p95:.4f} ms")
        print(f"  • p99 Latency:            {p99:.4f} ms (SLA < 100 ms: {'✅ PASS' if sub_100ms_compliance else '❌ FAIL'})")
        print(f"  • Max Observed Latency:   {max_lat:.4f} ms")
        print(f"  • CMI Integrity Bounds:   {'✅ 100% IN BOUNDS [0.0–100.0]' if cmi_bounds_valid else '❌ OUT OF BOUNDS'}")
        print(f"  • Tier Classification:    {tiers}")

        return results

    def verify_canonical_fixture_precision(self) -> bool:
        """Verifies canonical fixtures match contract-exact values under load."""
        print(f"\n================================================================================")
        print(f"🎯 VERIFYING CANONICAL FIXTURE MATHEMATICAL PRECISION UNDER LOAD")
        print(f"================================================================================")
        all_passed = True
        for fid, data in BENCHMARKS.items():
            packet = {
                "pod_id": f"POD-{fid}",
                "section_id": "Section 114" if data["sport"] == "Basketball" else "Section 115",
                "sport": data["sport"],
                "seat_count": 50,
                "situation": data["situation"],
                "is_clutch": "Clutch" in data["situation"],
                "db": data["db"],
                "hr": data["hr"],
                "taps": data["taps"],
                "vu": data["vu"],
                "timestamp": time.time()
            }
            res = self.process_single_packet(packet)
            diff = abs(res["cmi"] - data["expected_cmi"])
            passed = diff < 0.01
            status = "✅ PASS" if passed else f"❌ FAIL (Expected {data['expected_cmi']}, got {res['cmi']})"
            print(f"  [{fid}] {data['sport']} {data['situation']} -> Target: {data['expected_cmi']}, Computed: {res['cmi']} | {status}")
            if not passed:
                all_passed = False
        return all_passed

    def test_section_level_aggregation_and_chaser_alert(self) -> Dict[str, Any]:
        """Simulates System Optimizer aggregating pod CMIs into section standings & Chaser Alerts."""
        print(f"\n================================================================================")
        print(f"⚡ SIMULATING SYSTEM OPTIMIZER: SECTION-LEVEL PER-CAPITA AGGREGATION")
        print(f"================================================================================")

        sec_114_pods = [compute_cmi_index(106.5, 136.0, 12.2, 0.85) for _ in range(6)]
        sec_200_pods = [compute_cmi_index(82.0, 95.0, 2.0, 0.50) for _ in range(50)]

        avg_114 = statistics.mean(sec_114_pods)
        avg_200 = statistics.mean(sec_200_pods)

        section_batches = [
            {"name": "Section 114 (Student Bleachers)", "cmi": avg_114, "checked_in_fans": 300, "early_multiplier": 1.25, "clutch_multiplier": 1.0},
            {"name": "Section 200 (Club Level)", "cmi": avg_200, "checked_in_fans": 2500, "early_multiplier": 1.0, "clutch_multiplier": 1.0},
            {"name": "Section 115 (End Zone Loyals)", "cmi": 78.4, "checked_in_fans": 850, "early_multiplier": 1.15, "clutch_multiplier": 1.0}
        ]

        optimizer = SystemOptimizerAgent("Basketball")
        optimizer_res = optimizer.rank_sections_per_capita(section_batches)
        standings = optimizer_res["standings"]

        print("  🏆 Per-Capita Standings:")
        for idx, s in enumerate(standings, 1):
            print(f"    {idx}. {s['section']}: Score = {s['score']} pts (Fans: {s['fans']})")
        print(f"  📢 {optimizer_res['chaser_alert']}")

        storycard = optimizer.generate_reality_delta(
            outcome_label="VISITING SHOOTER MISSED FREE THROW 2",
            pre_cmi=37.8,
            peak_cmi=standings[0]["score"],
            fan_notes=["MISS IT! OFF THE BACK IRON!"]
        )
        print(f"\n  📜 Emitted StoryCard:")
        print(f"    • Headline: {storycard['headline']}")
        print(f"    • Winning Section: {storycard['winning_section']}")

        return {"standings": standings, "storycard": storycard}

if __name__ == "__main__":
    harness = VenueConcurrencyHarness(num_pods=1600, seats_per_pod=50)

    # 1. Verify Precision
    fixtures_ok = harness.verify_canonical_fixture_precision()
    assert fixtures_ok, "Canonical fixtures failed precision validation!"

    # 2. Concurrency Load Benchmark (10,000 packets across 32 threads)
    bench_results = harness.run_concurrency_benchmark(num_packets=10000, max_workers=32)
    assert bench_results["sub_100ms_compliance"], "Failed real-time latency SLA!"
    assert bench_results["cmi_bounds_valid"], "CMI bounds exceeded!"

    # 3. Scale-Up Concurrency Load Benchmark (25,000 packets across 64 threads)
    stress_results = harness.run_concurrency_benchmark(num_packets=25000, max_workers=64)
    assert stress_results["sub_100ms_compliance"], "Failed stress latency SLA!"

    # 4. Optimizer Section Aggregation & Narrative Check
    opt_results = harness.test_section_level_aggregation_and_chaser_alert()

    print(f"\n================================================================================")
    print("✅ ALL WEEK 5 CONCURRENCY & SCALE TESTS COMPLETED WITH 100% PASS RATE")
    print(f"================================================================================\n")
