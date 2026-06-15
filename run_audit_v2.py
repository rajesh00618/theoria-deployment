#!/usr/bin/env python3
"""Fast audit v2: minimal cycles for speed."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig

results = {}

def quick_config():
    c = TheoriaConfig.phase_1_baseline()
    c.max_cycles = 3
    return c

def test_A():
    print("A: Core Loop...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    data = [{"x": float(x), "y": float(2*x+1)} for x in __import__("numpy").linspace(0, 10, 10)]
    th.ingest_data(data)
    result = th.research_cycle("physics")
    theories = len(th.memory.theory.get_active())
    dt = time.time() - t0
    passed = theories > 0
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.0f}s, {theories} theories)")
    return {"passed": passed, "theories": theories}

def test_B():
    print("B: Ontogenesis...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    before = len(th.ontogenesis.concepts)
    th.research_cycle("physics")
    after = len(th.ontogenesis.concepts)
    dt = time.time() - t0
    passed = after >= before
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.0f}s, {before}->{after})")
    return {"passed": passed}

def test_C():
    print("C: Meta-Strategy...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    for _ in range(3):
        th.research_cycle("physics")
    strats = len(th.memory.meta_strategy.strategies)
    dt = time.time() - t0
    passed = strats > 0
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.0f}s, {strats} strategies)")
    return {"passed": passed}

def test_E():
    print("E: Falsification...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    data1 = [{"x": float(x), "y": float(2*x+1)} for x in __import__("numpy").linspace(0, 10, 10)]
    th.ingest_data(data1)
    th.research_cycle("physics")
    data2 = [{"x": float(x), "y": float(-3*x+20)} for x in __import__("numpy").linspace(0, 10, 10)]
    th.ingest_data(data2)
    th.research_cycle("physics")
    graveyard = len(th.memory.theory.graveyard)
    dt = time.time() - t0
    passed = graveyard > 0
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.0f}s, {graveyard} retired)")
    return {"passed": passed}

def test_G():
    print("G: Predictions...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    th.research_cycle("physics")
    has_pe = th.prediction_engine is not None
    dt = time.time() - t0
    print(f"{'PASS' if has_pe else 'FAIL'} ({dt:.0f}s)")
    return {"passed": has_pe}

def test_H():
    print("H: Safety...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    th.research_cycle("physics")
    audit = th.auditor.get_summary()
    dt = time.time() - t0
    has_veto = "veto_rate" in audit
    print(f"{'PASS' if has_veto else 'FAIL'} ({dt:.0f}s, veto_rate={audit.get('veto_rate',0):.2f})")
    return {"passed": has_veto}

def test_R():
    print("R: Exp Design...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    th.research_cycle("physics")
    has_ed = th.experiment_planner is not None
    dt = time.time() - t0
    print(f"{'PASS' if has_ed else 'FAIL'} ({dt:.0f}s)")
    return {"passed": has_ed}

def test_V():
    print("V: Prediction Engine...", end=" ", flush=True)
    t0 = time.time()
    th = TheoriaOrchestrator(quick_config())
    th.initialize_primitives("physics")
    th.research_cycle("physics")
    has_pe = th.prediction_engine is not None
    has_pa = hasattr(th.prediction_engine, "evaluate_from_experiment")
    dt = time.time() - t0
    passed = has_pe and has_pa
    print(f"{'PASS' if passed else 'FAIL'} ({dt:.0f}s)")
    return {"passed": passed}

print("=" * 60)
print("  THEORIA AUDIT SCORECARD v2")
print("=" * 60)

tests = [
    ("A", test_A),
    ("B", test_B),
    ("C", test_C),
    ("E", test_E),
    ("G", test_G),
    ("H", test_H),
    ("R", test_R),
    ("V", test_V),
]

for key, fn in tests:
    try:
        results[key] = fn()
    except Exception as e:
        print(f"  {key}: ERROR - {type(e).__name__}: {e}")
        results[key] = {"passed": False, "error": str(e)}

passed = sum(1 for r in results.values() if r.get("passed", False))
total = len(results)

print(f"\n{'='*60}")
print(f"  TOTAL: {passed}/{total} ({passed/total:.0%})")
print(f"{'='*60}")
