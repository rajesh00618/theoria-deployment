# REPRODUCIBILITY_REPORT.md

## Overview
Verification of THEORIA's reproducibility, including RP-001 reproduction package, Wikipedia validation, and GitHub validation.

---

## RP-001: Reproduction Package

### Status: ⚠️ PARTIALLY REPRODUCIBLE

The `reproducibility_package/` directory contains:
- `REPRODUCTION.md` — Step-by-step reproduction guide
- `rp001/` — Reproduction scripts and data
- `run_all.sh` — Shell script to run all reproduction steps

### Known Issues

1. **Data connectors were fake**: Before this audit, the reproduction package relied on simulated API responses. Now that real connectors are implemented, the reproduction results will differ from original benchmarks.

2. **Benchmark results in `results/` are from old runs**: The 48 JSON/CSV files in `results/` were generated with the pre-audit codebase (fake data connectors, random metric fabrication). These results are **not reproducible** with the fixed codebase.

3. **Seeded RNG**: The orchestrator uses `np.random.seed(42)` for data generation, which ensures reproducibility for the B1 classical law benchmark. However, other benchmarks used unseeded random state.

### Recommendation

Re-run all benchmarks with the fixed codebase and overwrite `results/` files. The new results will be:
- Based on real API data (where connectors are used)
- Using deterministic metric computations (no random score fabrication)
- Verifiably reproducible (same inputs → same outputs)

---

## Wikipedia Validation

### Status: ✅ NOW REPRODUCIBLE

**Before**: `real_data.py` generated fake Wikipedia results using seeded hash.

**After**: `real_data.py` and `data_connectors.py` both make real HTTP requests to `https://en.wikipedia.org/w/api.php`.

Verified working:
```
Query: "quantum mechanics"
Results:
  1. Quantum mechanics
  2. History of quantum mechanics
  3. Interpretations of quantum mechanics
```

**Caveat**: Results depend on Wikipedia's search algorithm and current article state. The specific results returned at different times may vary slightly, but the connector is real and functional.

---

## GitHub Validation

### Status: ✅ NOW REPRODUCIBLE

**Before**: `real_data.py` generated fake GitHub results.

**After**: Both connectors make real HTTP requests to `https://api.github.com/search/repositories`.

Verified working:
```
Query: "machine learning"
Results:
  1. tensorflow/tensorflow (stars: 187k+)
  2. huggingface/transformers (stars: 140k+)
  3. microsoft/ML-For-Beginners (stars: 73k+)
```

**Caveat**: Results depend on GitHub's search ranking and current repository state. Star counts change over time.

---

## Prediction Tracker Reproducibility

### Status: ✅ NOW IMMUTABLE AND REPRODUCIBLE

**Before**: Predictions could be modified after creation. No integrity checking.

**After**: 
- SHA256 hash computed at creation time from immutable fields
- Verification records are append-only with chain hashing
- Integrity verification detects any tampering
- All hashes validated on load

---

## Validation Engine Reproducibility

### Status: ✅ NOW REPRODUCIBLE

**Before**: P-values were hardcoded or passed through from input without computation.

**After**: 
- One-sample t-test computed from actual data
- Cohen's d effect size computed from group means and pooled standard deviation
- Confidence intervals computed from data standard error
- All statistics are deterministic given the same input data

---

## Recommendations for Full Reproducibility

1. **Re-run benchmarks**: Execute `python -m theoria.benchmarks.suite phase1` through `phase10` with the fixed codebase
2. **Version-pin dependencies**: Add exact version pins to `requirements.txt`
3. **Add deterministic seeds**: Ensure all stochastic processes use seeded RNG
4. **Store API responses**: Cache real API responses for offline reproducibility
5. **Add hash verification**: Include SHA256 hashes of result files in reproduction manifest
