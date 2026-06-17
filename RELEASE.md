# THEORIA Release Package

## What's Included

```
validate_stages.py           # Stage 1-6 validation
rp001_final.py               # Main analysis (frozen)
reproduce.py                 # Simple reproduction
discovery_engine.py          # Discovery engine
autonomous_scientist.py      # Autonomous scientist pipeline
stages.md                    # Detailed stage documentation
data/robustness_fast/        # 82 Wikipedia articles
results/                     # Results and validation
documents/                   # Paper draft
theoria/                     # Core library (117 modules)
```

## How to Reproduce

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy

# Run all validations
python validate_stages.py

# Or reproduce RP-001 only
python rp001_final.py
```

## Expected Results

### RP-001
```
Articles: 82 (36 controversial, 46 control)
Controversial mean: 18.6%
Control mean: 14.5%
Student t-test: p=0.000401
Cohen's d: 0.801
Leave-one-out: 82/82
```

### Full Validation (Stages 1-6)
```
Stage 1: PASS - 3 theories proposed
Stage 2: PASS - 3 gaps, 10 questions, 3 critiques
Stage 3: PASS - 3 experiments, 3 papers, 12 cross-domain maps
Stage 4: PASS - Full pipeline operational
Stage 5: PASS - 2 arch proposals, 18 algorithms, 50 simulations
Stage 6: PASS - 10 reasoning traces, 3 conjectures, 150 agents
Result: 7/7 stages passed
```

## Verification

1. p-value ≈ 0.0004
2. Cohen's d ≈ 0.80
3. 82/82 leave-one-out
4. All 6 stages pass validation
5. Result hash: a07429475b5dab8c

## Dependencies

- Python 3.10+
- numpy >= 1.24.0
- scipy >= 1.11.0

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
RP-001: p = 0.0004, Cohen's d = 0.80
Stages 1-6: Validated and operational
```
