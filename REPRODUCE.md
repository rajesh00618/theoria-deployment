# THEORIA Reproduction Guide

## What This Project Is

THEORIA is a research prototype for autonomous scientific discovery. It has one validated finding and a working discovery engine.

## Quick Start

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python rp001_final.py
```

## Expected Output

```
Articles: 82 (36 controversial, 46 control)
Controversial mean: 18.6%
Control mean: 14.5%
Student t-test: p=0.000401
Cohen's d: 0.801
Leave-one-out: 82/82
Result: SIGNIFICANT
```

## What You Need

- Python 3.10+
- numpy
- scipy

## What You Should Verify

1. p-value ≈ 0.0004
2. Controversial mean > Control mean
3. 82/82 leave-one-out
4. Result hash matches

## Scripts

| Script | Purpose |
|--------|---------|
| `rp001_final.py` | Main RP-001 analysis |
| `reproduce.py` | Simple reproduction |
| `discovery_engine.py` | Discovery engine |
| `autonomous_scientist.py` | Autonomous scientist pipeline |

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```
