# THEORIA Reproduction Guide

## What This Project Is

THEORIA is a research prototype exploring autonomous scientific discovery. It has **one validated discovery** backed by real data:

**RP-001: Dissent-Fragmentation Hypothesis**
- Controversial Wikipedia articles have significantly higher persistent dissent than non-controversial articles
- Statistical test: p = 0.0168 (significant)
- Data: Real Wikipedia revision histories (22 articles)

## What This Project Is NOT

- Not a complete autonomous scientific discovery system
- Not validated beyond RP-001
- Not producing novel scientific discoveries

## Quick Start

```bash
# Clone
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment

# Install
pip install numpy scipy

# Reproduce RP-001
python reproduce.py
```

## Expected Output

```
THEORIA RP-001 Reproducer
Dissent-Fragmentation Hypothesis
======================================================================

  Loaded 22 articles

  Article                              Edits  Users  Dissent%  Fragment
  -----------------------------------------------------------------
  Abortion                               500    150    24.7%     0.960
  Climate change                         484    129    24.8%     0.941
  ...

  Statistical Test: Two-sample t-test (controversial vs control)
  Controversial: n=14, mean=22.3%
  Control: n=8, mean=17.3%
  t=2.609, p=0.0168

  RESULT: SIGNIFICANT (p < 0.05)
  The Dissent-Fragmentation hypothesis is supported.
```

## What You Need

- Python 3.10+
- numpy
- scipy
- Internet (for initial data fetch, or use cached data)

## What You Should Verify

1. **p-value matches**: Should be approximately 0.0168
2. **Direction matches**: Controversial mean > Control mean
3. **Hash matches**: Result hash should be reproducible

## Limitations

- Only 22 articles (14 controversial, 8 control)
- Wikipedia data changes over time
- Single platform (Wikipedia only)
- Effect size is moderate (not large)

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```
