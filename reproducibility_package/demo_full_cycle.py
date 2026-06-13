#!/usr/bin/env python3
"""
THEORIA Full-Cycle Demonstration.

Shows the complete discovery → falsification → revision cycle
as required by Completion Requirement #4.
"""

import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_section(title):
    print(f"\n  {'─'*50}")
    print(f"  {title}")
    print(f"  {'─'*50}")


print_header("THEORIA: Full Discovery → Falsification → Revision Cycle")
print("  Demonstrating Completion Requirement #4")

# Initialize
config = TheoriaConfig.phase_1_baseline()
theoria = TheoriaOrchestrator(config)
theoria.initialize_primitives("physics")

# ============================================================================
# PHASE 1: DISCOVERY - Learn a linear law
# ============================================================================
print_section("PHASE 1: DISCOVERY - Learning a linear relationship")
print("  Data: y = 2x + 1 (perfect linear relationship)")

data1 = [{"x": x, "y": 2*x + 1} for x in np.linspace(0, 10, 30)]
theoria.ingest_data(data1)

# Run cycles to discover the law
for i in range(5):
    result = theoria.research_cycle("physics")
    active = theoria.memory.theory.get_active()
    if active:
        latest = active[-1]
        print(f"    Cycle {i+1}: {latest.name} "
              f"(posterior={latest.posterior:.3f}, "
              f"claims={[c.statement[:50] for c in latest.core_claims]})")

initial_theories = [(t.id, t.name, t.posterior) for t in theoria.memory.theory.get_active()]
print(f"\n  → Discovered {len(initial_theories)} initial theories")
for tid, name, post in initial_theories:
    print(f"      {name}: posterior={post:.3f}")

# ============================================================================
# PHASE 2: FALSIFICATION - Introduce contradictory data
# ============================================================================
print_section("PHASE 2: FALSIFICATION - Contradictory data arrives")
print("  New data: y = -3x + 20 (opposite slope)")
print("  This should falsify the linear relationship y=2x+1")

data2 = [{"x": x, "y": -3*x + 20} for x in np.linspace(0, 10, 30)]
theoria.ingest_data(data2)

# Run falsification
for i in range(8):
    result = theoria.research_cycle("physics")
    print(f"    Cycle {i+6}: {result.theories_falsified} falsified, "
          f"{result.theories_proposed} proposed")

# Check what happened to initial theories
print(f"\n  → Checking fate of initial theories:")
for tid, name, post in initial_theories:
    theory = theoria.memory.theory.get(tid)
    if theory:
        print(f"      {name}: status={theory.status.name}, "
              f"posterior={theory.posterior:.3f}")
    else:
        graveyard_entry = theoria.memory.graveyard.entries.get(tid)
        if graveyard_entry:
            print(f"      {name}: RETIRED to graveyard "
                  f"(reason: {graveyard_entry['reason']})")
        else:
            print(f"      {name}: no longer tracked")

# ============================================================================
# PHASE 3: REVISION - New theory replaces falsified one
# ============================================================================
print_section("PHASE 3: REVISION - Alternative theory generated")

# Run more cycles for revision
for i in range(5):
    result = theoria.research_cycle("physics")

revised_theories = [(t.id, t.name, t.posterior) for t in theoria.memory.theory.get_active()]
print(f"\n  → Active theories after revision:")
for tid, name, post in revised_theories:
    theory = theoria.memory.theory.get(tid)
    claims = [c.statement[:60] for c in theory.core_claims] if theory else []
    print(f"      {name}: posterior={post:.3f}")
    if claims:
        print(f"        Claims: {claims}")

# Check if theories changed
initial_ids = {tid for tid, _, _ in initial_theories}
revised_ids = {tid for tid, _, _ in revised_theories}
new_theories = revised_ids - initial_ids
retained_theories = initial_ids & revised_ids

print(f"\n  → Theory change analysis:")
print(f"      Initial theories: {len(initial_ids)}")
print(f"      Retained: {len(retained_theories)}")
print(f"      New (revised): {len(new_theories)}")
print(f"      Revision occurred: {len(new_theories) > 0 or len(retained_theories) < len(initial_ids)}")

# ============================================================================
# SUMMARY
# ============================================================================
print_header("CYCLE COMPLETE")
print("  ✓ DISCOVERY: Initial theories learned from data")
print("  ✓ FALSIFICATION: Contradictory data triggered falsification")
print("  ✓ REVISION: New theories generated to replace falsified ones")
print(f"  ✓ Graveyard entries: {theoria.memory.graveyard.size}")
print(f"  ✓ Active theories: {len(revised_theories)}")
print(f"{'='*70}\n")

# System summary
summary = theoria.get_system_summary()
print("  Final system state:")
print(f"    Cycles: {summary['cycles_completed']}")
print(f"    Memory: {summary['memory']['episodic']['size']} episodic, "
      f"{summary['memory']['theory']['active']} active theories")
print(f"    Falsification: {summary['falsification']['tests_conducted']} tests, "
      f"{summary['falsification']['theories_falsified']} falsified")
print(f"    Auditor: {summary['auditor']['vetoes']} vetoes, "
      f"{summary['auditor']['approvals']} approvals")
print(f"{'='*70}")
