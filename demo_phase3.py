#!/usr/bin/env python3
"""
THEORIA Phase 3 Demonstration: Experimental Scientist.

Demonstrates:
  P3.1 Experiment Design Engine
  P3.2 Intervention Engine
  P3.3 Multi-Agent Research Lab + P3.4 Autonomous Debate
  P3.5 Paper Generation
  P3.6 Scientific Prediction Engine
  P3.7 Cross-Domain Transfer
  P3.8 Real Data Connectors
"""

import sys
import time
import numpy as np
sys.path.insert(0, '/mnt/agents/output/theoria')

from theoria.orchestrator import TheoriaOrchestrator
from theoria.core.config import TheoriaConfig
from theoria.core.types import (
    AgentRole, ExperimentDesign, VariableSpec, ControlSpec, Concept,
    CandidateHypothesis, StrategyType, Theory, CoreClaim,
)


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_section(title):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


def main():
    print_header("THEORIA Phase 3: Experimental Scientist")
    print("  Author: rajesh gurugubelli | June 2026")
    print(f"{'='*70}\n")

    config = TheoriaConfig.phase_3_experimental()
    theoria = TheoriaOrchestrator(config)

    print("[1] Initializing Phase 3 system...")
    theoria.initialize_primitives("physics")
    theoria.initialize_primitives("biology")
    theoria.initialize_primitives("economics")
    print("  ✓ Phase 3 components initialized")
    print(f"  ✓ {len(theoria.multi_agent_lab.agents)} research agents registered")
    for role, agent in theoria.multi_agent_lab.agents.items():
        print(f"    - {role.name}: {agent.profile.name}")
    print(f"  ✓ Data connectors: {len(theoria.data_connector.sources)} sources")
    for name, src in theoria.data_connector.sources.items():
        print(f"    - {src.name} ({src.url})")

    print_header("P3.1 + P3.2: Experiment Design & Intervention Engine")
    print("  Testing: Hypothesis -> Experiment Design -> Intervention -> Simulation\n")

    hypothesis = CandidateHypothesis(
        id="demo_hyp_001",
        description="Increasing temperature causes increased reaction rate in chemical systems",
        strategy_origin=StrategyType.CAUSAL_REASONING,
        concepts_used=["temperature", "reaction_rate", "catalyst"],
        explanatory_power=0.75,
        falsifiability=0.85,
        novelty=0.4,
    )

    design = theoria.experiment_planner.design_from_hypothesis(hypothesis, "chemistry")
    print(f"  Design: {design.name}")
    print(f"  Independent variables: {[v.name for v in design.independent_variables]}")
    print(f"  Dependent variables: {design.dependent_variables}")
    print(f"  Controls: {[c.variable for c in design.controls]}")
    print(f"  Trials: {design.num_trials}")
    print(f"  Feasibility: {design.feasibility:.2f}")
    print(f"  Power: {design.predicted_power:.2f}")
    print(f"  Expected outcomes:")
    for o in design.expected_outcomes:
        print(f"    • {o}")

    print(f"\n  Protocol steps:")
    for step in design.protocol:
        print(f"    {step}")

    theory = Theory(
        name="Temperature-Reaction Rate Theory",
        core_claims=[CoreClaim(statement="Reaction rate increases with temperature")],
        reference_class=["temperature", "reaction_rate", "activation_energy"],
        posterior=0.75,
    )

    intervention = theoria.intervention_gen.generate_from_theory(theory)
    print(f"\n  Intervention: {intervention.name}")
    print(f"  Target variables: {intervention.target_variables}")
    print(f"  Realizability: {intervention.realizability:.2f}")

    print_section("Simulating Experiment")
    ground_truth = {"temperature": 0.5, "reaction_rate": 0.0, "catalyst": 0.3}
    result = theoria.experiment_planner.simulate_experiment(design.id, ground_truth)
    if result:
        print(f"  Effect size: {result.effect_size:.3f}")
        print(f"  p-value: {result.p_value:.3f}")
        print(f"  Bayes factor: {result.bayes_factor:.3f}")
        print(f"  Supports hypothesis: {result.supports_hypothesis}")
        print(f"  Contradicts hypothesis: {result.contradicts_hypothesis}")

    evaluation = theoria.experiment_eval.evaluate(design, result)
    print(f"\n  Evaluation quality: {evaluation['quality_score']:.2f}")
    print(f"  Recommendation: {evaluation['recommendation']}")

    print_header("P3.3 + P3.4: Multi-Agent Research Lab & Autonomous Debate")
    print("  Running peer review simulation...\n")

    review = theoria.multi_agent_lab.review_theory_pipeline(theory, design, result)
    print(f"  Review verdict: {'PASS' if review['passes_review'] else 'NEEDS REVISION'}")

    print_section("Agent Debate")
    topic = "Does temperature directly cause increased reaction rate?"
    participants = [AgentRole.THEORIST, AgentRole.CRITIC, AgentRole.REVIEWER, AgentRole.SAFETY_OFFICER]
    debate = theoria.multi_agent_lab.run_debate(topic, participants, max_rounds=2)
    print(f"  Debate rounds: {debate.round_number}")
    print(f"  Statements made: {len(debate.statements)}")
    print(f"  Consensus reached: {debate.consensus_reached}")
    if debate.consensus_reached:
        print(f"  Consensus: {debate.consensus_statement}")
    else:
        print(f"  Status: {debate.consensus_statement}")

    print_header("P3.5: Paper Generation")
    print("  Auto-generating scientific paper from experiment...\n")

    paper = theoria.paper_gen.generate(theory, design, result)
    print(f"  Title: {paper.title}")
    print(f"  Abstract: {paper.abstract[:200]}...")
    print(f"  Sections: {[s.heading for s in paper.sections]}")
    print(f"  Word count: {paper.word_count}")
    print(f"  Quality score: {paper.quality_score:.2f}")

    print_section("Results Section")
    print(f"  {paper.results.content[:300]}...")

    print_section("Discussion Section")
    print(f"  {paper.discussion.content[:300]}...")

    print_header("P3.6: Scientific Prediction Engine")
    print("  Making falsifiable predictions before seeing answers...\n")

    pred = theoria.prediction_engine.predict_outcome(theory, design)
    print(f"  Prediction: {pred.description}")
    print(f"  Predicted value: {pred.predicted_value:.3f}")
    print(f"  Confidence interval: ({pred.confidence_interval[0]:.3f}, {pred.confidence_interval[1]:.3f})")
    print(f"  Status: {pred.status}")

    eval_result = theoria.prediction_engine.evaluate_from_experiment(pred, result)
    print(f"  Actual value: {eval_result.get('actual', 'N/A')}")
    print(f"  Error: {eval_result.get('error', 'N/A')}")
    print(f"  Within CI: {eval_result.get('within_ci', 'N/A')}")

    predictions = theoria.prediction_engine.extract_predictions(theory)
    print(f"\n  Extracted {len(predictions)} predictions from theory")

    print_header("P3.7: Cross-Domain Transfer")
    print("  Applying physics insights to economics...\n")

    source_concepts = [
        Concept(name="temperature", kind="base", role="cause",
                domains_where_useful={"physics", "chemistry"}),
        Concept(name="reaction_rate", kind="base", role="effect",
                domains_where_useful={"physics", "chemistry"}),
    ]
    target_concepts = [
        Concept(name="market_temperature", kind="base", role="cause",
                domains_where_useful={"economics"}),
        Concept(name="transaction_rate", kind="base", role="effect",
                domains_where_useful={"economics"}),
    ]

    mappings = theoria.cross_domain.find_mappings(
        "physics", "economics", source_concepts, target_concepts
    )
    print(f"  Found {len(mappings)} cross-domain mappings")
    for m in mappings:
        print(f"    • {m.source_domain}.{m.source_concept} ↔ {m.target_domain}.{m.target_concept}")
        print(f"      Isomorphism: {m.isomorphism_score:.2f}")
        for p in m.predictions_generated:
            print(f"      → {p}")

    if mappings:
        hypothesis = theoria.cross_domain.apply_mapping(mappings[0], theory)
        print(f"\n  Transferred hypothesis: {hypothesis.description[:120]}...")
        print(f"  Novelty: {hypothesis.novelty:.2f}")

    print_header("P3.8: Real Data Connectors")
    print("  Connecting to external data sources...\n")

    for source_name in ["arxiv", "kaggle", "openml"]:
        connected = theoria.data_connector.connect_source(source_name)
        print(f"  {'✓' if connected else '✗'} Connected to {source_name}")

    dataset = theoria.data_connector.import_dataset("kaggle", "chemical_reactions", "chemistry")
    if dataset:
        print(f"\n  Imported dataset: {dataset.name}")
        print(f"  Domain: {dataset.domain}")
        print(f"  Features: {dataset.features[:5]}...")
        print(f"  Samples: {dataset.n_samples}")

    all_ds = theoria.data_connector.list_datasets()
    print(f"\n  Total datasets available: {len(all_ds)}")

    print_header("PHASE 3 RESEARCH CYCLE")
    print("  Running integrated Phase 3 cycle...\n")

    data = [{"temperature": t, "rate": np.exp(t / 10) + np.random.normal(0, 0.1)}
            for t in np.linspace(0, 10, 30)]
    theoria.ingest_data(data)

    result = theoria.research_cycle("physics")

    print(f"  Cycle {result.cycle_number}:")
    print(f"    Theories proposed: {result.theories_proposed}")
    print(f"    Experiments designed: {result.experiments_designed}")
    print(f"    Experiments executed: {result.experiments_executed}")
    print(f"    Interventions generated: {result.interventions_generated}")
    print(f"    Papers generated: {result.papers_generated}")
    print(f"    Predictions made: {result.predictions_made}")
    print(f"    Cross-domain mappings: {result.cross_domain_mappings}")
    print(f"    Debates held: {result.debates_held}")
    print(f"    Agents active: {result.agents_active}")

    print_header("SYSTEM SUMMARY")
    summary = theoria.get_system_summary()

    print_section("Phase 3 Components")
    if "phase_3" in summary:
        p3 = summary["phase_3"]
        print(f"  Experiment Planner: {p3['experiment_planner']['total_designs']} designs, {p3['experiment_planner']['total_results']} results")
        print(f"  Intervention Generator: {p3['intervention_generator']['total_interventions']} interventions")
        print(f"  Counterfactual Simulator: {p3['counterfactual_simulator']['total_counterfactuals']} simulations")
        print(f"  Experiment Evaluator: {p3['experiment_evaluator']['total_evaluations']} evaluations")
        print(f"  Multi-Agent Lab: {p3['multi_agent_lab']['agents']} agents, {p3['multi_agent_lab']['debates']} debates")
        print(f"  Paper Generator: {p3['paper_generator']['total_papers']} papers")
        print(f"  Prediction Engine: {p3['prediction_engine']['total_predictions']} predictions, calibration={p3['prediction_engine']['calibration']:.2f}")
        print(f"  Cross-Domain Transfer: {p3['cross_domain']['total_mappings']} mappings")
        print(f"  Data Connector: {p3['data_connector']['datasets_imported']} datasets")

    print_header("PHASE 3 DEMONSTRATION COMPLETE")
    print("  THEORIA Phase 3 has demonstrated:")
    print("  ✓ Experiment Design Engine (P3.1) — hypothesis → design → protocol")
    print("  ✓ Intervention Engine (P3.2) — intervention → counterfactual → evaluation")
    print("  ✓ Multi-Agent Research Lab (P3.3) — planner, theorist, experimenter, critic, reviewer, safety")
    print("  ✓ Autonomous Debate (P3.4) — peer review simulation with consensus")
    print("  ✓ Paper Generation (P3.5) — abstract, methods, results, discussion")
    print("  ✓ Prediction Engine (P3.6) — falsifiable predictions with calibration tracking")
    print("  ✓ Cross-Domain Transfer (P3.7) — physics ↔ economics isomorphism mapping")
    print("  ✓ Real Data Connectors (P3.8) — ArXiv, Kaggle, OpenML integration")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
