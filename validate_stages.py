#!/usr/bin/env python3
"""
THEORIA Stage 2-6 Validation
==============================

Validates all phases of the THEORIA system through Stage 6 (Research AGI).

Usage:
    python validate_stages.py

Tests:
    Stage 1: RP-001 (baseline)
    Stage 2: Autonomous Scientist (Literature, KG, Gaps, Questions, Critic)
    Stage 3: Experiment Design, Multi-Agent, Paper Generation, Predictions
    Stage 4: Real Data, Embodied, Society, Ethics, Adversarial
    Stage 5: Self-Improving Civilization
    Stage 6: General Research Intelligence (Universal Reasoning, Math Discovery, etc.)

Requirements:
    pip install numpy scipy
"""

import sys
import os
import time
import json
import hashlib
import traceback
from datetime import datetime
from typing import Dict, Any, List, Tuple

import numpy as np

from theoria.core.config import (
    TheoriaConfig, BudgetConfig, LiteratureConfig, KnowledgeGraphConfig,
    GapDetectionConfig, QuestionConfig, HypothesisGenConfig, PlannerConfig,
    CriticConfig, DashboardConfig, PersistentMemoryConfig,
    ExperimentDesignConfig, InterventionConfig, MultiAgentConfig,
    PaperGenConfig, PredictionConfig, CrossDomainConfig, DataConnectorConfig,
    EmbodiedConfig, SocietyConfig, CommunicationConfig, EthicsConfig,
    AdversarialConfig, PredictionMarketConfig, EconomyConfig,
    ResearchProgramConfig, EvolutionConfig,
    SelfImprovementConfig, MetaCivilizationConfig, BenchmarkGeneratorConfig,
    SimulationWorldsConfig, SelfModificationConfig, KnowledgeCompressionConfig,
    UniversalReasoningConfig, MathematicalDiscoveryConfig, SoftwareIntelligenceConfig,
    CrossDomainTransferConfig, OpenEndedLearningConfig, LongHorizonPlanningConfig,
    GeneralAgentSocietyConfig, UniversalProblemSolverConfig, WorldModelConfig,
    KnowledgeFabricConfig,
)


class ValidationResult:
    """Result of a stage validation."""
    def __init__(self, stage: str, name: str):
        self.stage = stage
        self.name = name
        self.passed = False
        self.error = None
        self.metrics = {}
        self.duration = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage,
            "name": self.name,
            "passed": self.passed,
            "error": self.error,
            "metrics": self.metrics,
            "duration_seconds": round(self.duration, 2),
        }


def validate_stage1() -> ValidationResult:
    """Validate Stage 1: RP-001 baseline."""
    result = ValidationResult("Stage 1", "RP-001 Baseline")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_1_baseline()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        cycle = orchestrator.research_cycle("physics")

        result.passed = True
        result.metrics = {
            "cycles_completed": orchestrator.cycle_count,
            "theories_proposed": cycle.theories_proposed,
            "theories_falsified": cycle.theories_falsified,
            "duration_seconds": round(cycle.duration, 2),
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def validate_stage2() -> ValidationResult:
    """Validate Stage 2: Autonomous Scientist (Literature, KG, Gaps, Questions, Critic)."""
    result = ValidationResult("Stage 2", "Autonomous Scientist")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_2_standard()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        cycle = orchestrator.research_cycle("physics")

        result.passed = True
        result.metrics = {
            "cycles_completed": orchestrator.cycle_count,
            "theories_proposed": cycle.theories_proposed,
            "papers_ingested": cycle.papers_ingested,
            "gaps_detected": cycle.gaps_detected,
            "questions_generated": cycle.questions_generated,
            "critiques_issued": cycle.critiques_issued,
            "programs_active": cycle.programs_active,
            "duration_seconds": round(cycle.duration, 2),
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def validate_stage3() -> ValidationResult:
    """Validate Stage 3: Experiment Design, Multi-Agent, Predictions."""
    result = ValidationResult("Stage 3", "Experimental Pipeline")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_3_experimental()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        cycle = orchestrator.research_cycle("physics")

        result.passed = True
        result.metrics = {
            "cycles_completed": orchestrator.cycle_count,
            "experiments_designed": cycle.experiments_designed,
            "experiments_executed": cycle.experiments_executed,
            "interventions_generated": cycle.interventions_generated,
            "papers_generated": cycle.papers_generated,
            "predictions_made": cycle.predictions_made,
            "cross_domain_mappings": cycle.cross_domain_mappings,
            "debates_held": cycle.debates_held,
            "agents_active": cycle.agents_active,
            "duration_seconds": round(cycle.duration, 2),
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def validate_stage4() -> ValidationResult:
    """Validate Stage 4: Real Data, Society, Ethics, Adversarial."""
    result = ValidationResult("Stage 4", "Scientific Civilization")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_4_civilization()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        cycle = orchestrator.research_cycle("physics")

        result.passed = True
        result.metrics = {
            "cycles_completed": orchestrator.cycle_count,
            "real_papers_found": cycle.real_papers_found,
            "embodied_experiments": cycle.embodied_experiments,
            "society_papers": cycle.society_papers,
            "ethics_reviews": cycle.ethics_reviews,
            "adversarial_challenges": cycle.adversarial_challenges,
            "market_predictions": cycle.market_predictions,
            "economy_allocations": cycle.economy_allocations,
            "programs_running": cycle.programs_running,
            "duration_seconds": round(cycle.duration, 2),
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def validate_stage5() -> ValidationResult:
    """Validate Stage 5: Self-Improving Civilization."""
    result = ValidationResult("Stage 5", "Self-Improving Civilization")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_5_self_improving()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        cycle = orchestrator.research_cycle("physics")

        result.passed = True
        result.metrics = {
            "cycles_completed": orchestrator.cycle_count,
            "architecture_proposals": cycle.architecture_proposals,
            "algorithm_candidates": cycle.algorithm_candidates,
            "strategy_population": cycle.strategy_population,
            "benchmarks_generated": cycle.benchmarks_generated,
            "simulation_experiments": cycle.simulation_experiments,
            "self_modifications_proposed": cycle.self_modifications_proposed,
            "self_modifications_approved": cycle.self_modifications_approved,
            "meta_findings": cycle.meta_findings,
            "abstractions_created": cycle.abstractions_created,
            "agendas_generated": cycle.agendas_generated,
            "civilization_health": round(cycle.civilization_health, 3),
            "civilization_innovation": round(cycle.civilization_innovation, 3),
            "duration_seconds": round(cycle.duration, 2),
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def validate_stage6() -> ValidationResult:
    """Validate Stage 6: General Research Intelligence."""
    result = ValidationResult("Stage 6", "General Research Intelligence")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_6_gri()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        cycle = orchestrator.research_cycle("physics")

        result.passed = True
        result.metrics = {
            "cycles_completed": orchestrator.cycle_count,
            "reasoning_traces": cycle.reasoning_traces,
            "conjectures_generated": cycle.conjectures_generated,
            "proofs_found": cycle.proofs_found,
            "software_projects": cycle.software_projects,
            "open_goals": cycle.open_goals,
            "plans_active": cycle.plans_active,
            "agent_society_size": cycle.agent_society_size,
            "problems_solved": cycle.problems_solved,
            "world_models_active": cycle.world_models_active,
            "fabric_nodes": cycle.fabric_nodes,
            "cross_domain_mappings_p6": cycle.cross_domain_mappings_p6,
            "duration_seconds": round(cycle.duration, 2),
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def validate_system_summary() -> ValidationResult:
    """Validate the full system summary across all active phases."""
    result = ValidationResult("Summary", "Full System Summary")
    start = time.time()

    try:
        from theoria.core.config import TheoriaConfig
        from theoria.orchestrator import TheoriaOrchestrator

        config = TheoriaConfig.phase_6_gri()
        orchestrator = TheoriaOrchestrator(config)
        orchestrator.initialize_primitives("physics")

        summary = orchestrator.get_system_summary()

        required_keys = ["cycles_completed", "memory", "auditor", "phase_2", "phase_3",
                         "phase_5", "phase_6"]
        missing = [k for k in required_keys if k not in summary]

        result.passed = len(missing) == 0
        result.metrics = {
            "summary_keys": list(summary.keys()),
            "missing_keys": missing,
            "phase_2_active": "phase_2" in summary,
            "phase_3_active": "phase_3" in summary,
            "phase_5_active": "phase_5" in summary,
            "phase_6_active": "phase_6" in summary,
        }
    except Exception as e:
        result.error = f"{type(e).__name__}: {e}"
        traceback.print_exc()

    result.duration = time.time() - start
    return result


def main():
    print("=" * 70)
    print("  THEORIA Stage 2-6 Validation")
    print("  Testing all phases through General Research Intelligence")
    print("=" * 70)
    print()

    validators = [
        validate_stage1,
        validate_stage2,
        validate_stage3,
        validate_stage4,
        validate_stage5,
        validate_stage6,
        validate_system_summary,
    ]

    results = []
    for validator in validators:
        print(f"  Running {validator.__doc__ or validator.__name__}...")
        v_result = validator()
        results.append(v_result)

        status = "PASS" if v_result.passed else "FAIL"
        print(f"  [{status}] {v_result.name} ({v_result.duration:.2f}s)")
        if v_result.error:
            print(f"         Error: {v_result.error}")
        if v_result.metrics:
            for k, v in v_result.metrics.items():
                if k not in ("summary_keys", "missing_keys") and not isinstance(v, list):
                    print(f"         {k}: {v}")
        print()

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    print("=" * 70)
    print(f"  RESULTS: {passed}/{total} stages passed")
    print("=" * 70)

    if passed == total:
        print("\n  ALL STAGES VALIDATED SUCCESSFULLY")
        print("  THEORIA is operational through Stage 6 (Research AGI)")
    else:
        print("\n  Some stages failed. See errors above.")
        for r in results:
            if not r.passed:
                print(f"  - {r.name}: {r.error}")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_stages": total,
        "passed": passed,
        "failed": total - passed,
        "results": [r.to_dict() for r in results],
    }

    os.makedirs("results", exist_ok=True)
    with open("results/stage_validation.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to results/stage_validation.json")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
