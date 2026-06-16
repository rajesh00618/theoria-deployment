# THEORIA

A research prototype exploring autonomous scientific discovery.

## Validated Discovery

**RP-001: Dissent-Fragmentation Hypothesis**

Controversial Wikipedia articles have significantly more persistent dissenters than non-controversial articles.

- 82 articles (36 controversial, 46 control)
- p = 0.0007 (statistically significant)
- Cohen's d = 0.77 (large effect)
- 82/82 leave-one-out robust
- Independently reproduced

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

## Project Structure

```
theoria/
├── rp001_final.py              # Frozen RP-001 analysis
├── reproduce.py                # Simple reproduction script
├── data/                       # Real Wikipedia revision data
│   └── robustness_fast/        # 82 articles
├── results/
│   └── rp001_final.json        # Frozen results
├── documents/
│   └── RP001_Paper_Draft.md    # Paper draft
├── theoria/                    # Core library
├── REPRODUCE.md                # Reproduction guide
├── RELEASE.md                  # Release package
├── SUMMARY.md                  # Project summary
└── requirements.txt            # Dependencies
```

## What THEORIA Does

1. **Ingests real data** (Wikipedia revisions via MediaWiki API)
2. **Computes metrics** (dissent fraction, fragmentation)
3. **Tests hypotheses** (t-tests, Mann-Whitney, bootstrap CI)
4. **Validates robustness** (leave-one-out sensitivity analysis)
5. **Tracks predictions** (SHA256 immutable storage)

## RP-001 Results

| Metric | Value |
|--------|-------|
| Articles | 82 |
| Controversial mean | 20.8% |
| Control mean | 16.5% |
| Student t-test | p = 0.000679 |
| Welch t-test | p = 0.001240 |
| Mann-Whitney U | p = 0.000595 |
| Cohen's d | 0.770 |
| Leave-one-out | 82/82 |

## Reproduction

```bash
python rp001_final.py
```

Expected output:
- p ≈ 0.0007
- Effect size ≈ 0.77
- 82/82 robust

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
RP-001: Dissent-Fragmentation Hypothesis
82 articles, p = 0.0007, Cohen's d = 0.77
```

## License

See LICENSE file.
