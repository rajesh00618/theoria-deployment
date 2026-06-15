# RP-001: Dissent-Fragmentation Hypothesis

## Core Claim

> Controversial Wikipedia articles have significantly higher persistent dissent than non-controversial articles (p = 0.0168).

## Evidence

### Simulation
- Contrarian agents above ~10% destroy consensus in multi-agent models
- Tested across 30 seeds, multiple network topologies

### Wikipedia Validation (22 articles)
- **14 controversial articles**: 22.3% mean dissent
- **8 control articles**: 17.3% mean dissent
- **p = 0.0168** (statistically significant)

## How to Reproduce

```bash
# 1. Install dependencies
pip install numpy scipy

# 2. Fetch Wikipedia data (requires internet)
python fetch_wikipedia_data.py

# 3. Run validation
python reproduce_rp001.py

# 4. Results saved to results/rp001_reproduction_results.json
```

## Expected Output

```
Controversial: n=14, mean=22.3%
Control: n=8, mean=17.3%
t=2.609, p=0.0168
RESULT: SIGNIFICANT (p < 0.05)
```

## Files

- `reproduce_rp001.py` - Self-contained reproduction script
- `../data/wikipedia/` - Wikipedia revision data
- `../results/rp001_reproduction_results.json` - Full results

## Citation

```
THEORIA Project. "Dissent-Fragmentation Hypothesis: Evidence from Wikipedia."
RP-001 Validation Report. June 2026.
```
