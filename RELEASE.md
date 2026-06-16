# THEORIA Release Package

## What's Included

```
rp001_final.py              # Main analysis
reproduce.py                # Simple reproduction
discovery_engine.py         # Discovery engine
autonomous_scientist.py     # Autonomous scientist
data/robustness_fast/       # 82 Wikipedia articles
results/                    # Results and predictions
documents/                  # Paper draft
```

## How to Reproduce

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python rp001_final.py
```

## Expected Results

```
RP-001: p=0.000401, Cohen's d=0.801, 82/82 robust
```

## Verification

1. p-value ≈ 0.0004
2. Cohen's d ≈ 0.80
3. 82/82 leave-one-out
4. Result hash: a07429475b5dab8c

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
RP-001: p = 0.0004, Cohen's d = 0.80
```
