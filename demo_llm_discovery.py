"""
LLM-Powered Discovery Demo

Uses THEORIA + local Ollama LLM (gemma3:4b) to autonomously generate
and evaluate novel scientific hypotheses about a chosen concept.
"""

import sys
import time
import json
from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig
from theoria.core.types import StrategyType, CandidateHypothesis


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_section(text):
    print(f"\n--- {text} ---")


def main():
    print_header("THEORIA LLM-Powered Autonomous Discovery")
    print("  Concept: Emergence in Complex Systems")
    print("  Domain: interdisciplinary (physics + biology + information theory)")
    print("  LLM: gemma3:4b via Ollama")
    print()

    # 1. Initialize THEORIA
    print_section("1. Initializing THEORIA")
    config = TheoriaConfig.phase_2_standard()
    config.budget.B_cycle = 1e18
    config.budget.B_life = 1e20
    theoria = TheoriaOrchestrator(config)

    # Check LLM availability
    if theoria.llm_driver.available:
        print("  [OK] gemma3:4b connected via Ollama")
    else:
        print("  [WARN] LLM not available — falling back to algorithmic strategies")
        print("         Make sure Ollama is running: ollama serve")

    # 2. Initialize domains
    print_section("2. Initializing domains")
    theoria.initialize_primitives("physics")
    theoria.initialize_primitives("biology")
    theoria.initialize_primitives("information_theory")
    print(f"  Concepts loaded: {len(theoria.ontogenesis.concepts)}")

    # 3. Ingest seed knowledge
    print_section("3. Ingesting seed knowledge about emergence")

    seed_data = [
        {"concept": "emergence", "level": "micro", "property": "collective_behavior",
         "domain": "physics", "value": 1.0},
        {"concept": "emergence", "level": "macro", "property": "phase_transition",
         "domain": "physics", "value": 0.95},
        {"concept": "emergence", "level": "micro", "property": "self_organization",
         "domain": "biology", "value": 0.88},
        {"concept": "emergence", "level": "macro", "property": "consciousness",
         "domain": "biology", "value": 0.7},
        {"concept": "emergence", "level": "information", "property": "computation",
         "domain": "information_theory", "value": 0.92},
        {"concept": "emergence", "level": "complex", "property": "ant_colony_optimization",
         "domain": "biology", "value": 0.85},
        {"concept": "emergence", "level": "physical", "property": "superconductivity",
         "domain": "physics", "value": 0.9},
        {"concept": "emergence", "level": "social", "property": "market_dynamics",
         "domain": "economics", "value": 0.75},
    ]
    theoria.ingest_data(seed_data)
    print(f"  Ingested {len(seed_data)} seed observations")

    # 4. Run LLM-powered discovery cycles
    print_section("4. Running LLM-powered discovery cycles")

    for cycle in range(1, 4):
        print(f"\n  >> Cycle {cycle}/3")
        start = time.time()
        result = theoria.research_cycle(domain="interdisciplinary")
        elapsed = time.time() - start
        print(f"     Theories proposed: {result.theories_proposed}")
        print(f"     Theories falsified: {result.theories_falsified}")
        print(f"     Anomalies detected: {result.anomalies_detected}")
        print(f"     Duration: {elapsed:.1f}s")

    # 5. Show ALL candidates (including LLM ones that may not have formalized)
    print_section("5. All Generated Candidate Hypotheses")
    all_candidates = theoria.abductive.candidates
    print(f"  Total candidates generated: {len(all_candidates)}")

    # Show S13 (LLM) candidates specifically
    llm_candidates = [c for c in all_candidates if c.strategy_origin == StrategyType.LLM_DRIVEN]
    print(f"  LLM-generated (S13): {len(llm_candidates)}")

    if llm_candidates:
        print_section("6. LLM-Generated Hypotheses (S13)")
        for i, c in enumerate(llm_candidates):
            print(f"\n  Hypothesis {i+1}:")
            # Truncate long descriptions
            desc = c.description[:400]
            print(f"    {desc}")
            print(f"    Confidence: {c.confidence:.2f} | Novelty: {c.novelty:.2f}")
            print(f"    Concepts: {', '.join(c.concepts_used)}")

    # 6. Show any theories that were successfully formalized
    print_section("7. Formalized Theories")
    active_theories = theoria.memory.theory.get_active()
    if active_theories:
        for i, t in enumerate(active_theories[:10]):
            claim = t.core_claim.statement if t.core_claim else "N/A"
            print(f"\n  Theory {i+1}: {t.name}")
            print(f"    Claim: {claim[:200]}")
            print(f"    Posterior: {t.posterior:.3f}")
    else:
        print("  No theories passed formalization (candidates generated but not promoted)")
        print("  This is expected — the LLM generates hypotheses that need experimental validation")

    # 7. Direct LLM test
    print_section("8. Direct LLM Hypothesis Generation")
    if theoria.llm_driver.available:
        print("  Querying gemma3:4b directly about emergence...")
        try:
            hypotheses = theoria.llm_driver.generate_hypotheses(
                concept="emergence",
                domain="complex systems",
                existing_knowledge=[
                    "Phase transitions show emergent macroscopic order from microscopic interactions",
                    "Consciousness may emerge from neural network complexity",
                    "Self-organization arises from local interaction rules",
                ],
                n_hypotheses=3,
            )
            for i, h in enumerate(hypotheses):
                print(f"\n  Direct LLM Hypothesis {i+1}:")
                print(f"    {h.get('description', 'N/A')[:300]}")
                print(f"    Mechanism: {h.get('mechanism', 'N/A')[:200]}")
                print(f"    Confidence: {h.get('confidence', 'N/A')}")
                preds = h.get('testable_predictions', [])
                if preds:
                    print(f"    Predictions: {', '.join(str(p) for p in preds[:2])}")
        except Exception as e:
            print(f"  Error: {e}")

    # 8. System summary
    print_section("9. System Summary")
    summary = theoria.get_system_summary()
    abductive_summary = summary.get("abductive", {})
    print(f"  Total candidates: {abductive_summary.get('total_candidates_generated', 0)}")
    print(f"  Generation cycles: {abductive_summary.get('generation_cycles', 0)}")

    strategy_counts = abductive_summary.get("strategy_counts", {})
    if strategy_counts:
        print("\n  Strategy distribution:")
        for s, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
            print(f"    {s}: {count}")

    print_header("Discovery Run Complete")


if __name__ == "__main__":
    main()
