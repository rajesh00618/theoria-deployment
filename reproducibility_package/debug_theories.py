#!/usr/bin/env python3
"""Debug script to inspect what theories are generated."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig

config = TheoriaConfig.phase_1_baseline()
theoria = TheoriaOrchestrator(config)
theoria.initialize_primitives(domain="physics")

# Generate data
theoria._generate_classical_law_data()

# Run a few cycles and inspect theories
for cycle in range(5):
    result = theoria.research_cycle(domain="physics")
    print(f"\n--- Cycle {cycle+1} ---")
    
    # Get the most recent theories
    recent = list(theoria.memory.theory.theories.values())[-5:]
    for t in recent:
        print(f"Theory: {t.name}")
        print(f"  Reference class: {t.reference_class}")
        print(f"  Intervention targets: {t.intervention.target_variables if t.intervention else 'None'}")
        print(f"  Core claims: {[c.statement for c in t.core_claims]}")
        print(f"  Origin: {t.origin_strategy}")
        print()

# Check what concepts exist
print("\n--- All Concepts ---")
for c in theoria.ontogenesis.concepts.values():
    print(f"  {c.name} (domains: {c.domains_where_useful})")
