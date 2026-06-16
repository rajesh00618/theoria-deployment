# THEORIA

A research prototype for autonomous scientific discovery.

## What THEORIA Does

THEORIA analyzes real data, finds patterns, generates hypotheses, and makes testable predictions.

## Three Levels

### Level 1: Proven Finding

**RP-001: Persistent Editing in Controversial Wikipedia Articles**

- 82 articles (36 controversial, 46 control)
- p = 0.0004 (statistically significant)
- Cohen's d = 0.80 (large effect)
- 82/82 leave-one-out robust
- Independently reproduced (2 times)

### Level 2: Autonomous Scientist Pipeline

```
Data Ingestion -> Anomaly Detection -> Hypothesis Generation -> Validation -> Prediction
```

Working pipeline that:
- Ingests real data (climate, Wikipedia, citations)
- Detects anomalies and patterns
- Generates hypotheses
- Validates with statistical tests
- Makes testable predictions

### Level 3: Discovery Engine

Makes specific, testable predictions stored immutably:

| Prediction | Test Date | Status |
|------------|-----------|--------|
| Temperature 2030 > 2025 | 2030-01-01 | FROZEN |

## Quick Start

```bash
# Clone
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment

# Install
pip install numpy scipy

# Reproduce RP-001
python rp001_final.py

# Run discovery engine
python discovery_engine.py
```

## Project Structure

```
theoria/
├── rp001_final.py              # RP-001 analysis (bot-excluded)
├── reproduce.py                # Simple reproduction script
├── discovery_engine.py         # Level 3: Discovery engine
├── autonomous_scientist.py     # Level 2: Autonomous scientist
├── data/                       # Real data
│   └── robustness_fast/        # 82 Wikipedia articles
├── results/                    # Results and predictions
├── documents/                  # Paper draft
├── theoria/                    # Core library
├── REPRODUCE.md                # Reproduction guide
├── RELEASE.md                  # Release package
├── SUMMARY.md                  # Project summary
└── requirements.txt            # Dependencies
```

## Results

### RP-001 Results (with bot exclusion)

| Metric | Value |
|--------|-------|
| Articles | 82 |
| Controversial mean | 18.6% |
| Control mean | 14.5% |
| Student t-test | p = 0.000401 |
| Cohen's d | 0.801 |
| Leave-one-out | 82/82 |

### Discovery Engine Results

| Metric | Value |
|--------|-------|
| Datasets analyzed | 3 |
| Patterns detected | 3 |
| Hypotheses generated | 3 |
| Predictions made | 1 |
| Predictions stored | 1 |

## Reproduction

```bash
python rp001_final.py
```

Expected output:
- p ≈ 0.0004
- Effect size ≈ 0.80
- 82/82 robust

## Citation

```
THEORIA: An Autonomous Scientific Discovery System
Rajesh Gurugubelli, 2026
```

## License

See LICENSE file.
