# THEORIA Project Summary

## What Is THEORIA?

THEORIA is a research prototype for autonomous scientific discovery. It analyzes real data, finds patterns, generates hypotheses, and makes testable predictions.

## Three Levels Complete

### Level 1: Proven Finding
- RP-001: Persistent editing in controversial Wikipedia articles
- p = 0.0004, Cohen's d = 0.80, 82/82 robust
- Independently reproduced (2 times)

### Level 2: Autonomous Scientist
- Working pipeline: ingest -> detect -> hypothesize -> validate -> predict
- Analyzes real data (climate, Wikipedia, citations)
- Validates hypotheses with statistical tests

### Level 3: Discovery Engine
- Makes specific, testable predictions
- Predictions stored immutably with SHA256 hashes
- Ready for future verification

## How to Reproduce

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python rp001_final.py
```

## Files

| File | Purpose |
|------|---------|
| `rp001_final.py` | Main RP-001 analysis |
| `reproduce.py` | Simple reproduction |
| `discovery_engine.py` | Discovery engine |
| `autonomous_scientist.py` | Autonomous scientist |
| `data/` | Real Wikipedia data |
| `results/` | Results and predictions |

## Status

| Component | Status |
|-----------|--------|
| RP-001 | Validated, reproducible |
| Predictions | Frozen, immutable |
| Discovery engine | Working |
| Autonomous scientist | Working |
| Paper draft | Ready |

## Contact

Rajesh Gurugubelli, 2026
