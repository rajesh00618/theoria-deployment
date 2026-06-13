# THEORIA Reproducibility Guide

## Prerequisites
- Python 3.10+
- pip

## Installation
```bash
pip install -r requirements.txt
```

## Verify Installation
```bash
python3 -c "from theoria import *; print('THEORIA imported successfully')"
```

## Run Benchmarks
```bash
# Option 1: All-in-one script
bash run_all.sh

# Option 2: Individual runs
python3 demo.py                    # B1 Classical Law Rediscovery
python3 demo_full_cycle.py         # Full discovery-falsification-revision cycle
python3 validation.py              # Comprehensive validation suite
```

## Expected Results
- B1: 5/6 classical laws in <30 cycles
- Core loop: Discovery -> Falsification -> Revision demonstrated
- Validation: All items A-I with pass/fail results
- CSV: `benchmark_results.csv` with structured scores
- Report: `THEORIA_VALIDATION_REPORT.txt` with detailed evidence

## Datasets
All data is procedurally generated. No external datasets required.

## Troubleshooting
- Ensure numpy, scipy are installed
- Check Python 3.10+ compatibility
- Run from project root directory
