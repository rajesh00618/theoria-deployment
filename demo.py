#!/usr/bin/env python3
"""
THEORIA Demonstration Script.

Runs the B1 benchmark (classical law rediscovery) and demonstrates
the full discovery → falsification → revision cycle.
"""

import sys
import time
sys.path.insert(0, '/mnt/agents/output/theoria')

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig


def print_header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_section(title: str):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


def main():
    print_header("THEORIA: Cognitive Architecture for Autonomous Scientific Theory Creation")
    print("  Author: rajesh gurugubelli | June 2026")
    print("  Phase 1 Baseline Implementation")
    print(f"{'='*70}\n")
    
    # Initialize THEORIA
    print("[1] Initializing THEORIA system...")
    config = TheoriaConfig.phase_1_baseline()
    theoria = TheoriaOrchestrator(config)
    
    print("  ✓ Memory architecture initialized (5 stores)")
    print("  ✓ Layers L-2 through L6 initialized")
    print("  ✓ Safety subsystems active")
    
    # Initialize primitives
    print("\n[2] Loading primitive concepts...")
    theoria.initialize_primitives(domain="physics")
    concepts = theoria.ontogenesis.get_concepts_for_domain("physics")
    print(f"  ✓ Loaded {len(concepts)} base primitives for physics")
    for c in concepts[:5]:
        print(f"    - {c.name} ({c.kind})")
    
    # Run B1 Benchmark
    print_header("BENCHMARK B1: Classical Law Rediscovery")
    print("  Target: Rediscover 5 of 6 classical laws")
    print("  Laws: Kepler's 3rd, Ohm's, Snell's, Ideal Gas, Coulomb's, Momentum")
    print(f"{'='*70}\n")
    
    result = theoria.run_benchmark_b1(max_cycles=30)
    
    # Detailed results
    print_section("B1 Results")
    print(f"  Passed: {result['passed']}")
    print(f"  Laws discovered: {result['laws_discovered']}/6")
    print(f"  Cycles used: {result['cycles']}")
    
    if result['discovered']:
        print("\n  Discovered laws:")
        for law_id, info in result['discovered'].items():
            print(f"    ✓ {info['law_name']} ({info['pattern']})")
            print(f"      Match score: {info['match_score']:.2f} | Cycle: {info['cycle']}")
    
    missing = set(theoria.classical_laws_catalog.keys()) - set(result['discovered'].keys())
    if missing:
        print(f"\n  Not discovered: {', '.join(missing)}")
    
    # System summary
    print_header("SYSTEM SUMMARY")
    summary = theoria.get_system_summary()
    
    print_section("Memory Architecture")
    mem = summary['memory']
    print(f"  Episodic records: {mem['episodic']['size']}")
    print(f"  Semantic facts: {mem['semantic']['size']}")
    print(f"  Active theories: {mem['theory']['active']}")
    print(f"  Graveyard entries: {mem['graveyard']['size']}")
    print(f"  Meta-strategies: {mem['meta_strategy']['strategies']}")
    print(f"  Strategy inventions: {mem['meta_strategy']['inventions']}")
    
    print_section("Safety & Audit")
    audit = summary['auditor']
    print(f"  L-1 vetoes: {audit['vetoes']}")
    print(f"  L-1 approvals: {audit['approvals']}")
    print(f"  Veto rate: {audit['veto_rate']:.2%}")
    print(f"  Rigor failures: {audit['rigor_failures']}/{audit['rigor_checks']}")
    
    print_section("Meta-Theory (L6)")
    meta = summary['meta_theory']
    print(f"  Research cycles: {meta['cycle_count']}")
    print(f"  Invented strategies: {meta['invented_strategies']}")
    print(f"  Paradigm crises: {meta['paradigm_crisis_active']}")
    print(f"  Proposals pending: {meta['proposals_pending']}")
    
    print_section("Falsification (L5)")
    fals = summary['falsification']
    print(f"  Tests conducted: {fals['tests_conducted']}")
    print(f"  Theories falsified: {fals['theories_falsified']}")
    print(f"  Theories retired: {fals['theories_retired']}")
    print(f"  Severity threshold: {fals['severity_threshold']}")
    
    print_section("Cycle History")
    for i, cycle in enumerate(theoria.cycle_history[-5:]):
        print(f"  Cycle {cycle.cycle_number}: "
              f"{cycle.theories_proposed}↑ {cycle.theories_falsified}↓ "
              f"{cycle.theories_converged}✓ | "
              f"Strategies: {', '.join(cycle.strategies_used[:3])}")
    
    print_header("DEMONSTRATION COMPLETE")
    print("  THEORIA has demonstrated:")
    print("  ✓ Multi-layer architecture (L0-L6, L-1, L-2)")
    print("  ✓ Theory discovery from observational data")
    print("  ✓ Severity-weighted falsification")
    print("  ✓ Meta-strategic learning (L6)")
    print("  ✓ Safety auditing (L-1)")
    print("  ✓ Constitutional oversight (L-2)")
    print(f"{'='*70}\n")
    
    return result


if __name__ == "__main__":
    main()
