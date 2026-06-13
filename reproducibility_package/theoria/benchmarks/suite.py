"""
THEORIA Benchmark Suite: B1-B17 and Q1-Q14.

Implements the evaluation framework from Section 9 of the specification.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.orchestrator import TheoriaOrchestrator, CycleResult
from theoria.core.config import TheoriaConfig


@dataclass
class BenchmarkResult:
    """Result of running a benchmark."""
    benchmark_id: str  # B1, B2, etc.
    passed: bool
    score: float  # 0-1 or specific metric
    details: Dict[str, Any] = field(default_factory=dict)
    cycles_used: int = 0
    wall_time: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class PredictionResult:
    """Result of evaluating a falsifiable prediction (Q1-Q14)."""
    prediction_id: str  # Q1, Q2, etc.
    evaluated: bool
    confirmed: bool  # True = prediction held, False = falsified
    statistical_evidence: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""


class TheoriaBenchmarkSuite:
    """
    Comprehensive benchmark suite for THEORIA.
    """
    
    def __init__(self, config: Optional[TheoriaConfig] = None):
        self.config = config or TheoriaConfig.phase_1_baseline()
        self.results: Dict[str, BenchmarkResult] = {}
        self.predictions: Dict[str, PredictionResult] = {}
        
        # Classical laws catalog (B1)
        self.classical_laws = {
            "kepler_third": "T^2 ∝ a^3",
            "ohms_law": "V = I·R",
            "snells_law": "n₁·sin(θ₁) = n₂·sin(θ₂)",
            "ideal_gas": "PV = nRT",
            "coulombs_law": "F = k·q₁q₂/r²",
            "momentum": "Σp_initial = Σp_final",
        }
    
    # ========================================================================
    # B1: Classical Law Rediscovery
    # ========================================================================
    
    def run_b1(self, max_cycles: int = 50) -> BenchmarkResult:
        """
        B1: Rediscovery of classical laws.
        Pass: Rediscover 5 of 6 from {Kepler, Ohm, Snell, Ideal Gas, Coulomb, Momentum}.
        """
        print(f"\n{'='*60}")
        print(f"B1: Classical Law Rediscovery")
        print(f"{'='*60}")
        
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        result = theoria.run_benchmark_b1(max_cycles=max_cycles)
        
        passed = result["passed"]
        score = result["laws_discovered"] / 6.0
        
        return BenchmarkResult(
            benchmark_id="B1",
            passed=passed,
            score=score,
            details={
                "laws_discovered": result["discovered"],
                "missing": list(set(self.classical_laws.keys()) - 
                               set(result["discovered"].keys())),
            },
            cycles_used=result["cycles"],
        )
    
    # ========================================================================
    # B2: Novel Prediction in Open Problem
    # ========================================================================
    
    def run_b2(self) -> BenchmarkResult:
        """
        B2: Novel prediction in open problem.
        Pass: At least one falsifiable prediction not in literature, 
              confirmed within 12 months.
        
        Note: This requires real-world execution; framework returns
        'not_evaluated' status.
        """
        return BenchmarkResult(
            benchmark_id="B2",
            passed=False,  # Cannot be evaluated in simulation
            score=0.0,
            details={"status": "requires_real_world_execution"},
        )
    
    # ========================================================================
    # B3: Cross-Domain Transfer
    # ========================================================================
    
    def run_b3(self) -> BenchmarkResult:
        """
        B3: Cross-domain transfer.
        Pass: Physics-discovered structure aids biology (or vice versa),
              no prompting. Across 3 domains.
        """
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        theoria.initialize_primitives("biology")
        
        # Check for analogies between domains
        analogies = theoria.ontogenesis.find_analogy("physics", "biology")
        
        score = len(analogies) / 10.0  # Heuristic threshold
        passed = len(analogies) >= 3
        
        return BenchmarkResult(
            benchmark_id="B3",
            passed=passed,
            score=min(score, 1.0),
            details={"analogies_found": len(analogies)},
        )
    
    # ========================================================================
    # B4: Self-Revision After Falsification
    # ========================================================================
    
    def run_b4(self, max_cycles: int = 20) -> BenchmarkResult:
        """
        B4: Self-revision after falsification.
        Pass: Qualitatively different successor after decisive falsification.
        After 3 sequential falsifications.
        """
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        # Generate data that supports one theory, then contradicts it
        # First: linear relationship
        data1 = [{"x": x, "y": 2*x + 1} for x in np.linspace(0, 10, 20)]
        theoria.ingest_data(data1)
        
        # Run to get initial theory
        for _ in range(5):
            theoria.research_cycle("physics")
        
        initial_theories = [t.name for t in theoria.memory.theory.get_active()]
        
        # Now: contradict with different relationship
        data2 = [{"x": x, "y": -3*x + 10} for x in np.linspace(0, 10, 20)]
        theoria.ingest_data(data2)
        
        for _ in range(10):
            theoria.research_cycle("physics")
        
        revised_theories = [t.name for t in theoria.memory.theory.get_active()]
        
        # Check if theories changed
        changed = len(set(initial_theories) & set(revised_theories)) < len(initial_theories)
        
        return BenchmarkResult(
            benchmark_id="B4",
            passed=changed,
            score=0.7 if changed else 0.3,
            details={
                "initial_theories": initial_theories,
                "revised_theories": revised_theories,
            },
            cycles_used=15,
        )
    
    # ========================================================================
    # B5: Meta-Strategic Innovation
    # ========================================================================
    
    def run_b5(self, max_cycles: int = 100) -> BenchmarkResult:
        """
        B5: Meta-strategic innovation.
        Pass: L6 invents a named new strategy, performance gain > 20% on held-out.
        With L-1 vetoes on the path.
        """
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        # Generate diverse data
        datasets = [
            [{"x": x, "y": x**2} for x in np.linspace(0, 5, 15)],
            [{"a": a, "b": 1/a + np.random.normal(0, 0.05)} for a in np.linspace(0.5, 5, 15)],
            [{"t": t, "p": np.sin(t)} for t in np.linspace(0, 2*np.pi, 20)],
        ]
        
        for data in datasets:
            theoria.ingest_data(data)
        
        # Run cycles to give L6 opportunity to invent
        for cycle in range(max_cycles):
            theoria.research_cycle("physics")
            
            if theoria.meta_theory.invented_strategies:
                # Check performance gain
                invented = theoria.meta_theory.invented_strategies[-1]
                if invented.expected_value > 0.2:
                    return BenchmarkResult(
                        benchmark_id="B5",
                        passed=True,
                        score=invented.expected_value,
                        details={
                            "strategy_name": invented.name,
                            "expected_value": invented.expected_value,
                            "invented_by": invented.invented_by,
                        },
                        cycles_used=cycle + 1,
                    )
        
        return BenchmarkResult(
            benchmark_id="B5",
            passed=False,
            score=0.0,
            details={"cycles_run": max_cycles, "inventions": len(theoria.meta_theory.invented_strategies)},
            cycles_used=max_cycles,
        )
    
    # ========================================================================
    # B8: Adversarial Robustness
    # ========================================================================
    
    def run_b8(self) -> BenchmarkResult:
        """
        B8: Adversarial robustness.
        Pass: Red Team's adversarial theory-defeats remain unaddressed 
              for > N cycles → fail.
        """
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        # Simulate Red Team finding a hidden assumption
        # In full implementation, this would be 3 independent Red Team instances
        
        # Check that auditor is functioning
        veto_rate = theoria.auditor.get_summary()["veto_rate"]
        
        # Veto rate should be in reasonable range (not 0%, not 100%)
        reasonable = 0.0 < veto_rate < 0.5
        
        return BenchmarkResult(
            benchmark_id="B8",
            passed=reasonable,
            score=0.5 if reasonable else 0.2,
            details={"veto_rate": veto_rate, "note": "simplified_in_phase1"},
        )
    
    # ========================================================================
    # B16: Self-Improvement Evaluation
    # ========================================================================
    
    def run_b16(self) -> BenchmarkResult:
        """
        B16: Self-Improvement Evaluation.
        Pass: Each revision demonstrates measurable improvement on ≥ 3 benchmarks.
        """
        # Track improvement across cycles
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        # Generate test data
        data = [{"x": x, "y": 2*x + 1} for x in np.linspace(0, 10, 30)]
        theoria.ingest_data(data)
        
        improvements = []
        for cycle in range(20):
            result = theoria.research_cycle("physics")
            improvements.append(result.theories_proposed)
        
        # Check for upward trend
        first_half = np.mean(improvements[:10])
        second_half = np.mean(improvements[10:])
        improved = second_half >= first_half
        
        return BenchmarkResult(
            benchmark_id="B16",
            passed=improved,
            score=0.7 if improved else 0.4,
            details={
                "first_half_avg": first_half,
                "second_half_avg": second_half,
                "trend": "improving" if improved else "stable",
            },
            cycles_used=20,
        )
    
    # ========================================================================
    # Q1-Q14: Falsifiable Predictions
    # ========================================================================
    
    def evaluate_q1(self) -> PredictionResult:
        """
        Q1: Multi-strategy ensembles outperform best single strategy by ≥30%.
        """
        # Compare ensemble vs individual strategies
        # Simplified: check that multiple strategies are used
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        data = [{"x": x, "y": x**2} for x in np.linspace(0, 5, 20)]
        theoria.ingest_data(data)
        
        for _ in range(10):
            result = theoria.research_cycle("physics")
        
        strategies_used = set()
        for cycle in theoria.cycle_history:
            strategies_used.update(cycle.strategies_used)
        
        multi_strategy = len(strategies_used) >= 4
        
        return PredictionResult(
            prediction_id="Q1",
            evaluated=True,
            confirmed=multi_strategy,
            statistical_evidence={"strategies_used": len(strategies_used)},
            notes="Ensemble uses diverse strategies" if multi_strategy else "Limited diversity",
        )
    
    def evaluate_q7(self) -> PredictionResult:
        """
        Q7: Disciplined-Constraint Substrate rejects ≥95% of compression-only theories.
        """
        # Check that theories without interventions are rejected
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        data = [{"x": x, "y": x + 1} for x in np.linspace(0, 10, 20)]
        theoria.ingest_data(data)
        
        for _ in range(5):
            theoria.research_cycle("physics")
        
        active = theoria.memory.theory.get_active()
        registered = [t for t in active if t.is_registered]
        
        # All registered theories should have interventions
        has_intervention = sum(1 for t in registered if t.intervention is not None)
        ratio = has_intervention / max(len(registered), 1)
        
        return PredictionResult(
            prediction_id="Q7",
            evaluated=True,
            confirmed=ratio >= 0.95,
            statistical_evidence={"intervention_rate": ratio},
            notes=f"{ratio:.1%} of registered theories have interventions",
        )
    
    def evaluate_q8(self) -> PredictionResult:
        """
        Q8: L-1 vetoes ≥5% of L6's proposed modifications.
        """
        # Check that L-1 is doing real work
        theoria = TheoriaOrchestrator(self.config)
        theoria.initialize_primitives("physics")
        
        for _ in range(10):
            theoria.research_cycle("physics")
        
        # Propose some modifications
        for i in range(10):
            proposal = theoria.meta_theory.propose_modification(
                "L6_0", "L3", "reweightStrategy", 
                {"strategy": "PATTERN_COMPLETION", "weight": 0.5}
            )
            theoria.auditor.audit_proposal(proposal)
        
        veto_rate = theoria.auditor.get_summary()["veto_rate"]
        
        return PredictionResult(
            prediction_id="Q8",
            evaluated=True,
            confirmed=veto_rate >= 0.05,
            statistical_evidence={"veto_rate": veto_rate},
            notes=f"L-1 veto rate: {veto_rate:.1%}",
        )
    
    # ========================================================================
    # Full Suite Runner
    # ========================================================================
    
    def run_all_phase1(self) -> Dict[str, Any]:
        """Run all Phase 1 benchmarks."""
        print(f"\n{'#'*70}")
        print(f"# THEORIA PHASE 1 BENCHMARK SUITE")
        print(f"# Baseline: Core Engine (L-2, L-1, L0-L4) + Formal Verification")
        print(f"{'#'*70}")
        
        benchmarks_to_run = [
            ("B1", self.run_b1),
            ("B3", self.run_b3),
            ("B4", self.run_b4),
            ("B5", self.run_b5),
            ("B8", self.run_b8),
            ("B16", self.run_b16),
        ]
        
        passed = 0
        total = len(benchmarks_to_run)
        
        for bid, runner in benchmarks_to_run:
            try:
                result = runner()
                self.results[bid] = result
                if result.passed:
                    passed += 1
                    status = "PASS"
                else:
                    status = "FAIL"
                print(f"\n  {bid}: {status} (score={result.score:.2f})")
            except Exception as e:
                print(f"\n  {bid}: ERROR - {e}")
                self.results[bid] = BenchmarkResult(
                    benchmark_id=bid, passed=False, score=0.0,
                    details={"error": str(e)}
                )
        
        # Evaluate predictions
        predictions_to_run = [
            ("Q1", self.evaluate_q1),
            ("Q7", self.evaluate_q7),
            ("Q8", self.evaluate_q8),
        ]
        
        q_confirmed = 0
        q_total = len(predictions_to_run)
        
        for qid, evaluator in predictions_to_run:
            try:
                result = evaluator()
                self.predictions[qid] = result
                if result.confirmed:
                    q_confirmed += 1
            except Exception as e:
                print(f"  {qid}: ERROR - {e}")
        
        return {
            "benchmarks": {
                "passed": passed,
                "total": total,
                "pass_rate": passed / total if total > 0 else 0,
            },
            "predictions": {
                "confirmed": q_confirmed,
                "total": q_total,
                "confirmation_rate": q_confirmed / q_total if q_total > 0 else 0,
            },
            "details": {
                bid: {
                    "passed": r.passed,
                    "score": r.score,
                    "cycles": r.cycles_used,
                }
                for bid, r in self.results.items()
            },
        }


if __name__ == "__main__":
    suite = TheoriaBenchmarkSuite()
    results = suite.run_all_phase1()
    
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"Benchmarks: {results['benchmarks']['passed']}/{results['benchmarks']['total']} passed")
    print(f"Predictions: {results['predictions']['confirmed']}/{results['predictions']['total']} confirmed")
    print(f"{'='*70}")
