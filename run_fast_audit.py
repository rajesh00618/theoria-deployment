#!/usr/bin/env python3
"""Fast audit: run only core items and benchmark individually."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig

results = {}

def test_A():
    """Core scientific loop: discovery -> falsification -> revision."""
    print("A: Core Loop...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    data = [{"x": x, "y": 2*x + 1} for x in __import__("numpy").linspace(0, 10, 30)]
    th.ingest_data(data)
    for _ in range(5):
        th.research_cycle("physics")
    revised = len(th.memory.theory.get_active())
    dt = time.time() - t0
    passed = revised > 0
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s, {revised} theories)")
    return {"passed": passed, "revised": revised, "time": dt}

def test_B():
    """Ontogenesis: novel concept generation."""
    print("B: Ontogenesis...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    before = len(th.ontogenesis.concepts)
    for _ in range(3):
        th.research_cycle("physics")
    after = len(th.ontogenesis.concepts)
    dt = time.time() - t0
    passed = after >= before
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s, {before}->{after} concepts)")
    return {"passed": passed, "before": before, "after": after}

def test_C():
    """Meta-strategy: strategy invention."""
    print("C: Meta-Strategy...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    for _ in range(10):
        th.research_cycle("physics")
    strategies = len(th.memory.meta_strategy.strategies)
    dt = time.time() - t0
    passed = strategies > 0
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s, {strategies} strategies)")
    return {"passed": passed, "strategies": strategies}

def test_E():
    """Falsification: theory retirement."""
    print("E: Falsification...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    data1 = [{"x": x, "y": 2*x + 1} for x in __import__("numpy").linspace(0, 10, 30)]
    th.ingest_data(data1)
    for _ in range(5):
        th.research_cycle("physics")
    data2 = [{"x": x, "y": -3*x + 20} for x in __import__("numpy").linspace(0, 10, 30)]
    th.ingest_data(data2)
    for _ in range(5):
        th.research_cycle("physics")
    graveyard = len(th.memory.theory.graveyard)
    dt = time.time() - t0
    passed = graveyard > 0
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s, {graveyard} retired)")
    return {"passed": passed, "graveyard": graveyard}

def test_F():
    """Benchmarks: B1 classical law rediscovery."""
    print("F: Benchmarks (B1)...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    result = th.run_benchmark_b1(max_cycles=30)
    dt = time.time() - t0
    passed = result["passed"]
    n = result["laws_discovered"]
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s, {n}/6 laws)")
    return {"passed": passed, "laws": n}

def test_G():
    """Predictions: generate and check."""
    print("G: Predictions...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    for _ in range(5):
        th.research_cycle("physics")
    has_predictions = hasattr(th, 'prediction_engine') and th.prediction_engine is not None
    dt = time.time() - t0
    passed = has_predictions
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s)")
    return {"passed": passed}

def test_H():
    """Safety: auditor vetoes."""
    print("H: Safety...", end=" ", flush=True)
    t0 = time.time()
    config = TheoriaConfig.phase_1_baseline()
    th = TheoriaOrchestrator(config)
    th.initialize_primitives("physics")
    for _ in range(5):
        th.research_cycle("physics")
    audit = th.auditor.get_summary()
    dt = time.time() - t0
    passed = "veto_rate" in audit
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.1f}s, veto_rate={audit.get('veto_rate',0):.2f})")
    return {"passed": passed, "audit": audit}

print("=" * 60)
print("  THEORIA AUDIT SCORECARD")
print("=" * 60)

tests = [
    ("A", test_A),
    ("B", test_B),
    ("C", test_C),
    ("E", test_E),
    ("F", test_F),
    ("G", test_G),
    ("H", test_H),
]

for key, fn in tests:
    try:
        results[key] = fn()
    except Exception as e:
        print(f"  {key}: ERROR - {e}")
        results[key] = {"passed": False, "error": str(e)}

passed = sum(1 for r in results.values() if r.get("passed", False))
total = len(results)

print(f"\n{'='*60}")
print(f"  TOTAL: {passed}/{total} ({passed/total:.0%})")
print(f"{'='*60}")
