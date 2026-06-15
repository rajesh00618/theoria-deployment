# RP-001: Contrarian Threshold Theory

## Hypothesis

> Consensus systems remain stable until contrarian agents exceed a critical fraction (~10%), after which consensus rapidly breaks down.

## Original Claim (Deprecated)

The original "Optimal Diversity Principle" claimed noise=0.02 was optimal. Rigorous testing with 30 seeds showed this was not supported. Zero noise produced best convergence.

## Revised Claim

The critical variable is not noise level but contrarian fraction. The system exhibits a phase transition at ~10% contrarian agents.

## Predictions

1. Below 10% contrarians: consensus forms reliably
2. At 10% contrarians: convergence becomes unstable
3. Above 10% contrarians: consensus cannot form
4. The threshold is robust across network topologies and agent counts

## How to Reproduce

```bash
# Install dependencies
pip install numpy scipy

# Run validation (30 seeds, ~8 minutes)
python rp001_validation.py

# Results saved to results/rp001_validation_results.json
```

## Expected Results

```
Contrarian Fraction | Convergence Rate
0%                  | 100%
5%                  | 100%
10%                 | ~23%  ← Critical threshold
15%                 | 0%
20%                 | 0%
```

## Files

- `experiment_001.py` — Original simulation engine
- `rp001_validation.py` — Rigorous validation suite
- `results/rp001_validation_results.json` — Full results with statistics

## Dependencies

- Python 3.8+
- numpy
- scipy (for statistical analysis)

## Citation

```
THEORIA Project. "Contrarian Threshold Theory in Multi-Agent Consensus Systems."
RP-001 Validation Report. June 2026.
```
