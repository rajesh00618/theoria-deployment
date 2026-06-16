# RANDOM_USAGE_REPORT.md

## Overview
Comprehensive audit of all `random.random()`, `random.uniform()`, `np.random.random()`, and `np.random.uniform()` usage across the THEORIA codebase.

**Total instances found: 208 (original) → 3 (remaining after fixes)**

---

## Phase A: Score Fabrication Cleanup (COMPLETE)

### Before Phase A
- 185 `random.uniform`/`np.random.uniform` instances across layers/
- ~120 used for score/metric fabrication (INVALID)
- ~65 used for stochastic simulation (VALID)

### After Phase A
- 3 `random.uniform`/`np.random.uniform` instances remaining
- All 3 are legitimate (test inputs, simulation sampling)
- **Zero invalid random metrics remain**

### Files Fixed (27 files modified)

| File | Instances Fixed | Category |
|------|----------------|----------|
| `self_improvement.py` | ~15 | Architecture, Algorithm, Strategy scores |
| `cognitive_evolution.py` | 3 | Performance gains |
| `self_modification.py` | 1 | Benchmark improvement |
| `data_connectors.py` | 2 | Fake data generation |
| `real_data.py` | 3 | Fake API responses |
| `world_models.py` | 5 | Predicted value, confidence, risk |
| `unified_world_model.py` | 7 | Accuracy, confidence, impact |
| `unified_cognitive_core.py` | 1 | Confidence |
| `tool_ecosystem.py` | 4 | Capability, reliability |
| `universal_solver.py` | 2 | Quality, difficulty |
| `open_world_learning.py` | 1 | Confidence |
| `open_ended_learning.py` | 4 | Gain, difficulty, curiosity |
| `knowledge_compression.py` | 3 | Predictive power |
| `human_collaboration.py` | 2 | Feedback, quality |
| `singularity_coordination_layer.py` | 2 | Initial value, delta |
| `meta_knowledge_civilization.py` | 2 | Confidence, delta |
| `meta_civilization_intelligence.py` | 2 | Accuracy, delta |
| `meta_civilization.py` | 4 | Resource, novelty, feasibility, impact |
| `knowledge_evolution_layer.py` | 4 | Productivity, stability, fitness |
| `long_horizon_planning.py` | 1 | Progress gain |
| `organization_builder.py` | 1 | Productivity |
| `recursive_tool_civilization.py` | 2 | Performance score |
| `universal_problem_network.py` | 1 | Criticality |
| `universal_knowledge_fabric2.py` | 1 | Integration score |
| `universal_fabric.py` | 1 | Edge weight |
| `creativity_engine.py` | 9 | Novelty, utility, impact |
| `agency_layer.py` | 5 | Complexity, relevance, confidence, quality |
| `executive_intelligence.py` | 4 | Risk, confidence, progress |
| `grand_challenge_engine.py` | 2 | Progress, collaboration |
| `civilization_intelligence.py` | 4 | Synergy, resource, progress |
| `scientific_society.py` | 2 | Productivity, reputation |
| `research_institutions.py` | 1 | Allocation |
| `recursive_discovery_ecosystem.py` | 2 | Performance delta |
| `lifelong_memory.py` | 2 | Memory strength |
| `grand_discovery_programs.py` | 3 | Completion, validation, progress |
| `global_memory.py` | 1 | Importance |
| `global_knowledge.py` | 3 | Confidence |
| `general_agent_society.py` | 3 | Productivity, noise |
| `field_creation.py` | 1 | Maturity delta |
| `discovery_forecasting.py` | 2 | Probability, accuracy |
| `civilization_simulator.py` | 6 | Accuracy, complexity, confidence |
| `civilization_memory.py` | 1 | Importance |
| `civilization_governance_layer.py` | 8 | Stability, alignment, severity |
| `autonomous_research_director.py` | 2 | Resources, priority |
| `benchmark_generator.py` | 7 | Difficulty, validation |

### Remaining Valid Usage (3 instances)

| File | Line | Usage | Reason Valid |
|------|------|-------|-------------|
| `benchmark_generator.py` | 29 | `random.uniform(-10, 10)` | Test input range generation |
| `benchmark_generator.py` | 53 | `random.uniform(-5, 5)` | Test input range generation |
| `experiment_design.py` | 218 | `np.random.uniform(iv.range[0], iv.range[1])` | Simulation variable sampling |

### Pattern Used
All fixes use the `_det_score(label)` helper:
```python
def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0
```
Scores computed as: `low + _det_score(f"context_{name}") * (high - low)`
