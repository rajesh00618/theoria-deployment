# THEORIA RP-001 Release Package

## What's Included

This package contains everything needed to independently reproduce RP-001.

### Files

```
rp001_final.py           # Frozen analysis script
data/robustness_fast/    # 82 Wikipedia articles (real revision data)
results/rp001_final.json # Frozen results with hash
documents/RP001_Paper_Draft.md  # Paper draft
SUMMARY.md               # Project summary
REPRODUCE.md             # Quick reproduction guide
```

### How to Reproduce

```bash
# 1. Clone repository
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment

# 2. Install dependencies
pip install numpy scipy

# 3. Run frozen analysis
python rp001_final.py
```

### Expected Results

```
Articles: 82 (36 controversial, 46 control)
Controversial mean dissent: 20.8%
Control mean dissent: 16.5%
Student t-test: p=0.000679
Welch t-test: p=0.001240
Mann-Whitney: p=0.000595
Cohen's d: 0.770
Leave-one-out robust: 82/82
Result hash: 62f6b9abefbfb599
```

### Verification

1. **p-value matches**: Should be approximately 0.0007
2. **Effect size matches**: Cohen's d should be approximately 0.77
3. **Robustness matches**: 82/82 leave-one-out
4. **Hash matches**: Result hash should be 62f6b9abefbfb599

### What This Proves

The Dissent-Fragmentation Hypothesis is supported:
- Controversial Wikipedia articles have significantly more persistent dissenters
- The effect is statistically significant (p < 0.001)
- The effect is large (d = 0.77)
- The result is robust (no fragile articles)

### Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
RP-001: Dissent-Fragmentation Hypothesis
82 articles, p = 0.0007, Cohen's d = 0.77
```
