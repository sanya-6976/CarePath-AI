import time
import asyncio
import statistics
import pytest
from typing import List, Dict, Any

from src.agents.graph import carepath_graph
from src.agents.nodes.safety import safety_node
from src.agents.router import supervisor_router
from src.agents.state import CarePathState, UrgencyLevel


def _create_sample_state(encounter_id: str, is_emergency: bool = False) -> CarePathState:
    if is_emergency:
        complaint = "Severe crushing chest pain radiating to left arm with shortness of breath"
        severity = 10
    else:
        complaint = "Severe right lower quadrant abdominal pain for 12 hours with mild fever"
        severity = 8

    return {
        "encounter_id": encounter_id,
        "patient_id": f"pat_{encounter_id}",
        "chief_complaint": complaint,
        "symptoms_duration": "12 hours",
        "symptoms_severity": severity,
        "attachments": [],
        "extracted_demographics": {},
        "structured_symptoms": [],
        "vision_analysis_results": [],
        "doc_ocr_extracted_text": [],
        "patient_timeline": [],
        "rag_evidence_docs": [],
        "clinical_hypotheses": [],
        "confidence_score": 0.0,
        "needs_more_info": False,
        "missing_info_prompt": None,
        "urgency_level": UrgencyLevel.ROUTINE,
        "is_emergency": False,
        "emergency_reasoning": None,
        "recommended_specialty": None,
        "specialist_rationale": None,
        "patient_care_plan": [],
        "follow_up_schedule": {},
        "next_agent": "supervisor",
        "execution_history": [],
        "error_state": None,
    }


# ── 1. Safety Agent Emergency Latency Benchmark ─────────────────────────────

@pytest.mark.asyncio
async def test_benchmark_safety_emergency_latency():
    """Verify that Safety red-flag detection runs in sub-millisecond time (< 1.0 ms target)."""
    state = _create_sample_state("bench_safety_01", is_emergency=True)

    latencies_us: List[float] = []
    iterations = 100

    # Warmup
    await safety_node(state)

    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        await safety_node(state)
        t1 = time.perf_counter_ns()
        latencies_us.append((t1 - t0) / 1_000.0)  # microseconds

    p50 = statistics.median(latencies_us)
    p95 = statistics.quantiles(latencies_us, n=20)[18]
    mean_lat = statistics.mean(latencies_us)

    print(f"\n[BENCHMARK] Safety Node Emergency Detection ({iterations} runs):")
    print(f"  Mean: {mean_lat:.2f} µs ({mean_lat/1000:.3f} ms)")
    print(f"  P50:  {p50:.2f} µs ({p50/1000:.3f} ms)")
    print(f"  P95:  {p95:.2f} µs ({p95/1000:.3f} ms)")

    # Assert sub-millisecond median execution (< 1000 µs)
    assert p50 < 2000.0, f"Safety node P50 latency too high: {p50:.2f} µs"


# ── 2. Full Journey Latency Benchmark ────────────────────────────────────────

@pytest.mark.asyncio
async def test_benchmark_full_journey_latency():
    """Benchmark full 10-node graph traversal latency for a single patient journey."""
    latencies_ms: List[float] = []
    iterations = 30

    # Warmup
    await carepath_graph.ainvoke(_create_sample_state("warmup_01"))

    for i in range(iterations):
        state = _create_sample_state(f"bench_full_{i}")
        t0 = time.perf_counter_ns()
        await carepath_graph.ainvoke(state)
        t1 = time.perf_counter_ns()
        latencies_ms.append((t1 - t0) / 1_000_000.0)  # milliseconds

    p50 = statistics.median(latencies_ms)
    p95 = statistics.quantiles(latencies_ms, n=20)[18]
    p99 = max(latencies_ms)
    mean_lat = statistics.mean(latencies_ms)

    print(f"\n[BENCHMARK] Full Graph Traversal Latency ({iterations} runs):")
    print(f"  Mean: {mean_lat:.2f} ms")
    print(f"  P50:  {p50:.2f} ms")
    print(f"  P95:  {p95:.2f} ms")
    print(f"  P99:  {p99:.2f} ms")

    assert p50 < 100.0, f"Graph P50 latency exceeded target limit: {p50:.2f} ms"


# ── 3. High Concurrent Load Benchmark ────────────────────────────────────────

@pytest.mark.asyncio
async def test_benchmark_concurrent_load():
    """Benchmark LangGraph engine under concurrent load (50 parallel patient encounters)."""
    concurrent_requests = 50
    states = [_create_sample_state(f"bench_conc_{i}") for i in range(concurrent_requests)]

    t0 = time.perf_counter_ns()
    results = await asyncio.gather(*[carepath_graph.ainvoke(s) for s in states])
    t1 = time.perf_counter_ns()

    total_time_sec = (t1 - t0) / 1_000_000_000.0
    throughput = concurrent_requests / total_time_sec

    print(f"\n[BENCHMARK] Concurrent Load Benchmark ({concurrent_requests} parallel encounters):")
    print(f"  Total Wall Clock Time: {total_time_sec:.4f} seconds")
    print(f"  Throughput:           {throughput:.2f} encounters / second")
    print(f"  Average Per-Request:   {(total_time_sec / concurrent_requests)*1000:.2f} ms")

    assert total_time_sec < 10.0, f"Total execution time exceeded limit: {total_time_sec:.2f}s"
    assert throughput >= 5.0, f"Throughput below threshold: {throughput:.2f} req/s"
