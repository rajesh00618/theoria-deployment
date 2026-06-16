# THEORIA Reproduction Guide

## What This Project Is

THEORIA is a research prototype exploring autonomous scientific discovery. It has **one validated finding** backed by real data:

**RP-001: Persistent Editing in Controversial Wikipedia Articles**
- Controversial Wikipedia articles have significantly more persistent editors
- Statistical test: p = 0.0004 (significant)
- Data: Real Wikipedia revision histories (82 articles)

## Quick Start

```bash
# Clone
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment

# Install
pip install numpy scipy

# Reproduce RP-001
python rp001_final.py
```

## Expected Output

```
THEORIA RP-001 FINAL
======================================================================

  Loaded 82 articles
  Controversial: 36
  Control: 46

  Statistical Tests:
  Controversial mean: 18.6%
  Control mean: 14.5%
  Student t-test: p=0.000401
  Welch t-test: p=0.000877
  Mann-Whitney: p=0.000500
  Cohen's d: 0.801

  Leave-One-Out: 82/82 robust

  Result: SIGNIFICANT
```

## What You Need

- Python 3.10+
- numpy
- scipy

## What You Should Verify

1. **p-value matches**: Should be approximately 0.0004
2. **Direction matches**: Controversial mean > Control mean
3. **Hash matches**: Result hash should be a07429475b5dab8c

## Limitations

- Only 82 articles (36 controversial, 46 control)
- Wikipedia data changes over time
- Single platform (Wikipedia only)
- "Persistent editing" does not measure "dissent"

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```
