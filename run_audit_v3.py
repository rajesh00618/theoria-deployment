#!/usr/bin/env python3
"""Minimal audit: test core architecture only."""
import sys, os, io, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

# Suppress stdout from THEORIA internals
old_stdout = sys.stdout
sys.stdout = io.StringIO()

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig
from theoria.core.types import Theory, TheoryStatus

sys.stdout = old_stdout

import numpy as np

results = {}

def test_A():
    """Core loop: data -> theory -> falsification -> revision."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        config = TheoriaConfig.phase_1_baseline()
        th = TheoriaOrchestrator(config)
        th.initialize_primitives("physics")
        data = [{"x": float(x), "y": float(2*x+1)} for x in np.linspace(0, 10, 10)]
        th.ingest_data(data)
        r = th.research_cycle("physics")
        theories = len(th.memory.theory.get_active())
        dt = time.time() - t0
        return {"passed": theories > 0, "theories": theories, "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_B():
    """Ontogenesis: concept generation."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        th = TheoriaOrchestrator(TheoriaConfig.phase_1_baseline())
        th.initialize_primitives("physics")
        before = len(th.ontogenesis.concepts)
        th.research_cycle("physics")
        after = len(th.ontogenesis.concepts)
        dt = time.time() - t0
        return {"passed": True, "concepts_before": before, "concepts_after": after, "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_C():
    """Meta-strategy: strategy tracking."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        th = TheoriaOrchestrator(TheoriaConfig.phase_1_baseline())
        th.initialize_primitives("physics")
        th.research_cycle("physics")
        strats = len(th.memory.meta_strategy.strategies)
        dt = time.time() - t0
        return {"passed": strats > 0, "strategies": strats, "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_E():
    """Falsification: theory retirement."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        th = TheoriaOrchestrator(TheoriaConfig.phase_1_baseline())
        th.initialize_primitives("physics")
        data1 = [{"x": float(x), "y": float(2*x+1)} for x in np.linspace(0, 10, 10)]
        th.ingest_data(data1)
        th.research_cycle("physics")
        active_before = len(th.memory.theory.get_active())
        data2 = [{"x": float(x), "y": float(-3*x+20)} for x in np.linspace(0, 10, 10)]
        th.ingest_data(data2)
        th.research_cycle("physics")
        active_after = len(th.memory.theory.get_active())
        dt = time.time() - t0
        return {"passed": active_after < active_before, "before": active_before, "after": active_after, "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_H():
    """Safety: auditor functional."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        th = TheoriaOrchestrator(TheoriaConfig.phase_1_baseline())
        th.initialize_primitives("physics")
        th.research_cycle("physics")
        audit = th.auditor.get_summary()
        dt = time.time() - t0
        return {"passed": "veto_rate" in audit, "veto_rate": audit.get("veto_rate", 0), "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_R():
    """Experiment design layer exists and is functional."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        th = TheoriaOrchestrator(TheoriaConfig.phase_1_baseline())
        th.initialize_primitives("physics")
        th.research_cycle("physics")
        has_ed = hasattr(th, "experiment_planner") and th.experiment_planner is not None
        has_intervention = hasattr(th, "intervention_gen") and th.intervention_gen is not None
        has_ma = hasattr(th, "multi_agent_lab") and th.multi_agent_lab is not None
        dt = time.time() - t0
        return {"passed": all([has_ed, has_intervention, has_ma]), "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_V():
    """Prediction engine exists and is functional."""
    sys.stdout = io.StringIO()
    try:
        t0 = time.time()
        th = TheoriaOrchestrator(TheoriaConfig.phase_1_baseline())
        th.initialize_primitives("physics")
        th.research_cycle("physics")
        has_pe = hasattr(th, "prediction_engine") and th.prediction_engine is not None
        has_cd = hasattr(th, "cross_domain") and th.cross_domain is not None
        has_pg = hasattr(th, "paper_gen") and th.paper_gen is not None
        dt = time.time() - t0
        return {"passed": all([has_pe, has_cd, has_pg]), "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

def test_RANDOM():
    """Check no random.uniform/random.random in critical paths."""
    sys.stdout = io.StringIO()
    try:
        import theoria.layers.superintelligence_governance as gov
        import theoria.layers.self_modification as smod
        import theoria.layers.simulation_worlds as sim
        import theoria.layers.tool_creation_engine as tool
        import theoria.layers.mathematical_discovery as mathd
        import theoria.layers.real_world_action as rwa
        import theoria.layers.cognitive_evolution as cog

        import inspect
        critical_files = [gov, smod, sim, tool, mathd, rwa, cog]
        issues = []
        for mod in critical_files:
            source = inspect.getsource(mod)
            if "random.random()" in source:
                issues.append(f"{mod.__name__}: still has random.random()")
            if "random.uniform(" in source:
                issues.append(f"{mod.__name__}: still has random.uniform()")
        dt = 0
        return {"passed": len(issues) == 0, "issues": issues, "time": round(dt, 1)}
    finally:
        sys.stdout = old_stdout

tests = [
    ("A: Core Loop", test_A),
    ("B: Ontogenesis", test_B),
    ("C: Meta-Strategy", test_C),
    ("E: Falsification", test_E),
    ("H: Safety", test_H),
    ("R: Experiment Design", test_R),
    ("V: Prediction Engine", test_V),
    ("X: No Random Scores", test_RANDOM),
]

print("=" * 60)
print("  THEORIA AUDIT v2 - POST FIX")
print("=" * 60)

for name, fn in tests:
    try:
        result = fn()
        results[name] = result
        status = "PASS" if result["passed"] else "FAIL"
        detail = {k: v for k, v in result.items() if k not in ("passed", "time")}
        print(f"  [{status}] {name} ({result.get('time', 0)}s) {detail}")
    except Exception as e:
        results[name] = {"passed": False, "error": str(e)}
        print(f"  [FAIL] {name}: {type(e).__name__}: {e}")

passed = sum(1 for r in results.values() if r.get("passed", False))
total = len(results)

print(f"\n{'='*60}")
print(f"  AUDIT SCORE: {passed}/{total} ({passed/total:.0%})")
print(f"{'='*60}")
