# THEORIA Reproduction Guide

## Quick Start (5 minutes)

```bash
# 1. Clone the repository
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment

# 2. Install dependencies
pip install numpy scipy

# 3. Run reproduction
python reproduce.py
```

## What You Should See

```
THEORIA RP-001 Reproducibility Package
Dissent-Fragmentation Hypothesis
======================================================================

  Analyzed 22 articles

  Article                              Edits  Users  Dissent%  Fragment
  -----------------------------------------------------------------
  Abortion                               500    150    24.7%     0.960
  Climate change                         484    129    24.8%     0.941
  ...

  Statistical Test:
  Controversial: n=14, mean=22.3%
  Control: n=8, mean=17.3%
  t=2.609, p=0.0168

  RESULT: SIGNIFICANT (p < 0.05)
  The Dissent-Fragmentation hypothesis is supported.
```

## Expected Results

- **p-value**: ~0.0168 (significant at p < 0.05)
- **Controversial articles**: ~22.3% dissent
- **Control articles**: ~17.3% dissent
- **Effect**: Controversial articles have significantly higher dissent

## If Results Differ

1. **Different p-value**: Wikipedia data changes over time. This is expected.
2. **Different article count**: Some articles may have fewer revisions.
3. **Different dissent percentages**: Threshold or calculation method may differ.

## Validation Criteria

The hypothesis is supported if:
- p < 0.05 (statistically significant)
- Controversial mean > Control mean (direction matches prediction)

## Additional Validations

```bash
# RP-002: Dream Theory
python rp002_validation.py

# RP-003: Creativity Theory
python rp003_validation.py

# RP-004 to RP-012
python rp006_012_validation.py

# Cross-platform validation
python cross_platform_validation.py

# Blind discovery benchmark
python blind_discovery_benchmark.py
```

## Dependencies

```
numpy>=1.24.0
scipy>=1.11.0
```

No other dependencies required. No API keys needed. No external services.

## Troubleshooting

**Windows encoding error**: Set `PYTHONIOENCODING=utf-8` before running.

**Network error**: Wikipedia API may be temporarily unavailable. Try again later.

**Different results**: Wikipedia data is dynamic. Results may vary by date.

## Citation

If you reproduce these results, please cite:

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```
