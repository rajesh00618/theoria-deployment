# THEORIA RP-001 Release Package

## What's Included

This package contains everything needed to independently reproduce RP-001.

### Files

```
rp001_final.py           # Main analysis (bot-excluded)
data/robustness_fast/    # 82 Wikipedia articles (real revision data)
results/rp001_final.json # Results with hash
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

# 3. Run analysis
python rp001_final.py
```

### Expected Results

```
Articles: 82 (36 controversial, 46 control)
Controversial mean: 18.6%
Control mean: 14.5%
Student t-test: p=0.000401
Welch t-test: p=0.000877
Mann-Whitney: p=0.000500
Cohen's d: 0.801
Leave-one-out robust: 82/82
Result hash: a07429475b5dab8c
```

### Verification

1. **p-value matches**: Should be approximately 0.0004
2. **Effect size matches**: Cohen's d should be approximately 0.80
3. **Robustness matches**: 82/82 leave-one-out
4. **Hash matches**: Result hash should be a07429475b5dab8c

### What This Proves

Controversial Wikipedia articles have significantly more persistent editors than non-controversial articles:
- The effect is statistically significant (p < 0.001)
- The effect is large (d = 0.80)
- The result is robust (no fragile articles)
- The result holds at all thresholds (2-10 edits)

### Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
RP-001: Persistent Editing in Controversial Wikipedia Articles
82 articles, p = 0.0004, Cohen's d = 0.80
```
