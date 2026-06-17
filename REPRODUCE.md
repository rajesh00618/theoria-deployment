# THEORIA Reproduction Guide

## What This Project Is

THEORIA is an autonomous scientific discovery system with 6 validated stages, from proven findings to general research intelligence.

## Quick Start

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python validate_stages.py
```

## What You Need

- Python 3.10+
- numpy >= 1.24.0
- scipy >= 1.11.0

## Scripts

| Script | Purpose |
|--------|---------|
| `validate_stages.py` | Run all 6 stage validations |
| `rp001_final.py` | RP-001 frozen analysis |
| `reproduce.py` | Simple reproduction |
| `discovery_engine.py` | Discovery engine |
| `autonomous_scientist.py` | Autonomous scientist pipeline |

## What You Should Verify

### RP-001 (Stage 1)
1. p-value ≈ 0.0004
2. Controversial mean > Control mean
3. 82/82 leave-one-out
4. Result hash matches

### Full Validation (Stages 1-6)
1. All 7 tests pass
2. Stage 1: theories proposed > 0
3. Stage 2: gaps detected > 0, questions generated > 0
4. Stage 3: experiments designed > 0, papers generated > 0
5. Stage 4: full pipeline operational
6. Stage 5: architecture proposals > 0, simulations > 0
7. Stage 6: reasoning traces > 0, agent society > 0

## Expected Output

### RP-001
```
Articles: 82 (36 controversial, 46 control)
Controversial mean: 18.6%
Control mean: 14.5%
Student t-test: p=0.000401
Cohen's d: 0.801
Leave-one-out: 82/82
Result: SIGNIFICANT
```

### Full Validation
```
Stage 1: PASS - RP-001 Baseline (39s)
Stage 2: PASS - Autonomous Scientist (36s)
Stage 3: PASS - Experimental Pipeline (42s)
Stage 4: PASS - Scientific Civilization (39s)
Stage 5: PASS - Self-Improving Civilization (45s)
Stage 6: PASS - General Research Intelligence (39s)
Summary: PASS - Full System Summary (2s)
RESULTS: 7/7 stages passed
```

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```
