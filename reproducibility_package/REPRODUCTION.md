# THEORIA Reproducibility Guide

## Prerequisites
- Python 3.10+
- pip
- Internet connection (for real API connectors)

## Installation
```bash
git clone <repository>
cd theoria-master
pip install -r requirements.txt
```

## Verify Installation
```bash
python -c "import theoria; print(f'THEORIA v{theoria.__version__} imported successfully')"
```

## Run Validations

### RP-001: Dissent-Fragmentation Hypothesis
```bash
python reproducibility_package/rp001/reproduce_rp001.py
```
Expected: p=0.0168 (significant), 22 Wikipedia articles analyzed.

### RP-002: Dream Theory
```bash
python rp002_validation.py
```
Expected: 4/4 tests pass.

### RP-003: Creativity Theory
```bash
python rp003_validation.py
```
Expected: 4/4 tests pass.

### Cross-Platform Validation
```bash
python cross_platform_validation.py
```
Expected: Wikipedia significant, GitHub pattern inconclusive (5 repos).

### Blind Discovery Benchmark
```bash
python blind_discovery_benchmark.py
```
Expected: 5/5 tests pass.

### Phase 5-10 Benchmarks
```bash
python -m theoria.benchmarks.suite phase5
python -m theoria.benchmarks.suite phase6
python -m theoria.benchmarks.suite phase7
python -m theoria.benchmarks.suite phase8
python -m theoria.benchmarks.suite phase9
python -m theoria.benchmarks.suite phase10
```
Expected: 54/56 benchmarks pass (96.4%).

## Expected Results Summary
| Validation | Expected | Metric |
|------------|----------|--------|
| RP-001 | Significant | p < 0.05 |
| RP-002 | Validated | 4/4 tests |
| RP-003 | Validated | 4/4 tests |
| Cross-Platform | Validated | Wikipedia p < 0.05 |
| Blind Discovery | Validated | 5/5 tests |
| Benchmarks | 96.4% | 54/56 pass |

## Datasets
- Wikipedia data: `data/wikipedia/` (24 articles, pre-fetched)
- GitHub data: `data/github/` (5 repos, pre-fetched)
- No external datasets required for core validations.

## Key Files
- `results/rp001_reproduction_results.json` — RP-001 results
- `results/rp002_validation_results.json` — RP-002 results
- `results/rp003_validation_results.json` — RP-003 results
- `results/cross_platform_validation_results.json` — Cross-platform results
- `results/blind_discovery_results.json` — Blind benchmark results
- `results/post_audit_benchmark_results.json` — Phase 5-10 benchmarks

## Troubleshooting
- Windows encoding: Set `PYTHONIOENCODING=utf-8` before running
- API errors: Real connectors need internet; Wikipedia/GitHub data is pre-cached
- Timeout: Phase 1-3 benchmarks may be slow; use phase5-10 for quick validation

## Deterministic Scoring
All scores use `_det_score(label)` with SHA256 hashing for reproducibility.
Same input → same output, every time.
