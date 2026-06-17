# THEORIA

An autonomous scientific discovery system that continuously expands human knowledge.

## What THEORIA Does

THEORIA analyzes real data, finds patterns, generates hypotheses, designs experiments, and makes testable predictions — all autonomously.

---

## How THEORIA Works — One Research Cycle

When you call `research_cycle("physics")`, here's exactly what happens:

### Step 1: L2 Ontogenesis (Concept Management)
- Evaluates existing primitive concepts (mass, velocity, force, etc.)
- Checks for "Einstein moment" — a novel concept combination
- Finds analogies between domains
- Returns: list of active concepts for the domain

### Step 2: Get Observations from Memory
- Pulls the last 100 observations from episodic memory
- These could be from previously ingested data (Wikipedia, climate, etc.)

### Step 3: L3 Abductive Imagination (Hypothesis Generation)
- Runs **13 strategies** in parallel:
  - S1: Pattern Completion — finds patterns in data
  - S2: Causal Structural Search — looks for cause-effect
  - S3: Analogical Transfer — maps from other domains
  - S4: Evolutionary Search — mutates/crosses hypotheses
  - S5: Dream-State — random creative combinations
  - S6: Rare-Event Hunter — focuses on anomalies
  - S7: Literature-Informed — uses ingested papers
  - S8: Cross-Domain — maps between fields
  - S9: Causal Reasoning — causal chains
  - S10: Counterfactual — "what if" scenarios
  - S11: Concept Blending — merges concepts
  - S12: Mechanistic — mechanism-based explanations
  - S13: LLM-Driven — uses local LLM (gemma3:4b)
- Uses Thompson Sampling to allocate compute across strategies
- Returns: **10 candidate hypotheses** with scores

### Step 4: L4 Theory Constructor (Formalization)
- Takes each candidate hypothesis
- Formalizes it into a proper theory with:
  - Core claims (statements)
  - Reference class (variables it applies to)
  - Intervention (what it predicts)
  - Domain of validity
- Registers valid theories in memory
- Checks if any match known classical laws (B1 benchmark)

### Step 5: Create Evidence for New Theories
- For each new theory, checks if observation variables overlap with theory variables
- If overlap: creates confirming evidence (likelihood 0.60)
- If no overlap: creates disconfirming evidence (likelihood 0.20)
- Updates theory posteriors using Bayes

### Step 6: L5 Falsification Engine
- For each theory, queries its evidence
- Evaluates severity of tests (Mayo e-value)
- Compares competing theories
- Falsifies weak theories → moves to graveyard
- Identifies converged theories (survived severe tests)

### Step 7: Phase 2 — Literature Pipeline
- Detects gaps in knowledge graph (missing links, contradictions)
- Generates research questions from gaps
- Critiques each theory (logical, evidence, methodological flaws)
- Creates research program if enough gaps exist

### Step 8: Phase 3 — Experiment Pipeline
- For each top theory:
  - Generates causal intervention
  - Designs experiment (randomization, blinding, power)
  - Simulates experiment
  - Multi-agent review (6 agents debate)
  - If passes review: generates paper
  - Makes prediction, evaluates against results
- Cross-domain transfer (physics → biology)

### Step 9: Phase 5 — Self-Improvement
- Proposes architecture modifications for weak layers
- Evolves algorithms via genetic search
- Evolves hypothesis generation strategies
- Generates benchmarks
- Runs simulation worlds (50 experiments)
- Knowledge compression (extracts meta-concepts)

### Step 10: Phase 6 — General Intelligence
- Runs all 10 reasoning modes on the domain
- Generates mathematical conjectures
- Creates software projects
- Sets open-ended goals
- Creates long-horizon plans
- Scales agent society (500+ agents)
- Solves problems
- Updates world models
- Evolves knowledge fabric

### Step 11: L6 Meta-Theory (Self-Reflection)
- Tracks which strategies performed best
- Detects paradigm crisis (too many anomalies)
- Invents new strategies if needed

### Step 12: L-1 Auditor (Safety)
- Audits all modifications
- Checks aggregate effect monitor
- Escalates if safety thresholds breached

### Step 13: Memory + Dashboard
- Updates all memory stores
- Takes metrics snapshot

---

## One Cycle Output Example

```
Research Cycle "physics" →
  3 theories proposed
  0 falsified
  0 converged
  3 gaps detected
  10 questions generated
  3 critiques issued
  3 experiments designed
  3 papers generated
  10 reasoning traces
  3 conjectures
  150 agents active
  5 world models
```

---

## Six Stages Validated

### Stage 1: Proven Finding
- RP-001: Persistent editing in controversial Wikipedia articles
- p = 0.0004, Cohen's d = 0.80, 82/82 leave-one-out robust
- Independently reproduced 2 times
- Classical law rediscovery (Momentum, Ohm, Kepler, etc.)

### Stage 2: Autonomous Scientist
- Literature ingestion, knowledge graph, gap detection, question generation
- Research planning, scientific critique, discovery dashboard

### Stage 3: Experimental Pipeline
- Experiment design, causal intervention, counterfactual simulation
- Multi-agent debates (6 agents), paper generation, predictions
- Cross-domain knowledge transfer

### Stage 4: Scientific Civilization
- Real data sources (arXiv, PubMed, Semantic Scholar, NASA)
- Scientific society (100+ agents), ethics review, adversarial testing
- Prediction market, scientific economy, research programs

### Stage 5: Self-Improving Civilization
- Architecture search, algorithm discovery, strategy evolution
- Simulation worlds, safe self-modification, knowledge compression
- Meta-civilization analytics and goal generation

### Stage 6: General Research Intelligence
- 10 reasoning modes (deduction, induction, abduction, causal, etc.)
- Mathematical conjecture generation and proof search
- 500+ agent society, world models, universal knowledge fabric

---

## Honest Assessment

What's working:
- Full pipeline from data to theories to experiments to papers
- 13 hypothesis generation strategies
- 10 reasoning modes
- Multi-agent debates
- Self-improvement loop
- Knowledge graph that grows each cycle

What's not yet real:
- 500 agents simulate a society, not parallel researchers
- Theories are template-based, not deep semantic understanding
- Experiments are simulated, not real lab experiments
- Papers are structured, not publication-ready prose
- LLM (gemma3:4b) is optional, falls back to heuristics

---

## Quick Start

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy

# Run all validations (Stages 1-6)
python validate_stages.py

# Reproduce RP-001
python rp001_final.py

# Run autonomous scientist
python autonomous_scientist.py

# Run discovery engine
python discovery_engine.py
```

## Project Structure

```
theoria/
├── validate_stages.py           # Stage 1-6 validation
├── rp001_final.py               # RP-001 analysis (frozen)
├── reproduce.py                 # One-command reproduction
├── discovery_engine.py          # Discovery engine
├── autonomous_scientist.py      # Autonomous scientist pipeline
├── data/                        # Real data
│   ├── robustness_fast/         # 82 Wikipedia articles
│   ├── wikipedia/               # Full Wikipedia datasets
│   ├── github/                  # GitHub issues data
│   └── ...
├── results/                     # Results and validation
├── documents/                   # Paper draft
├── theoria/                     # Core library
│   ├── core/                    # Config, memory, types, knowledge graph
│   ├── layers/                  # 117 layer modules (Stages 1-10)
│   └── orchestrator.py          # Main system controller
├── stages.md                    # Detailed stage documentation
├── REPRODUCE.md                 # Reproduction guide
├── RELEASE.md                   # Release package
├── SUMMARY.md                   # Project summary
└── requirements.txt             # Dependencies
```

## Validation Results

| Stage | Name | Status | Key Metrics |
|-------|------|--------|-------------|
| 1 | RP-001 Baseline | PASS | p=0.0004, d=0.80, Momentum discovered |
| 2 | Autonomous Scientist | PASS | 3 gaps, 10 questions, 3 critiques |
| 3 | Experimental Pipeline | PASS | 3 experiments, 3 papers, 12 cross-domain maps |
| 4 | Scientific Civilization | PASS | Full pipeline operational |
| 5 | Self-Improving Civilization | PASS | 2 arch proposals, 18 algorithms, 50 simulations |
| 6 | General Research Intelligence | PASS | 10 reasoning traces, 3 conjectures, 150 agents |

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```

## License

See LICENSE file.
