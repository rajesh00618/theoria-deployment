# THEORIA Project Summary

## Overview

THEORIA is an autonomous scientific theory creation framework. This document summarizes the current state of the project and its key discoveries.

## Key Discovery: RP-001 Dissent-Fragmentation Hypothesis

### Core Claim

> Communities with higher fractions of persistent dissenters exhibit significantly higher fragmentation.

### Evidence

#### Simulation
- Contrarian agents above ~10% destroy consensus in multi-agent models
- Tested across 30 seeds, multiple network topologies

#### Wikipedia Validation (22 articles)
- **14 controversial articles**: 22.3% mean dissent
- **8 control articles**: 16.3% mean dissent
- **p = 0.0168** (statistically significant)

#### GitHub Validation (5 repos, 500 issues)
- **PyTorch**: 20.0% dissent (similar to controversial Wikipedia)
- **VSCode**: 6.1% dissent (similar to control Wikipedia)
- Pattern consistent across platforms

### Reproducibility

Self-contained reproduction script at:
```
reproducibility_package/rp001/reproduce_rp001.py
```

Run:
```bash
pip install numpy scipy
python reproduce_rp001.py
```

## Project Structure

```
theoria-master/
├── theoria/                    # Core library (91 layers)
├── documents/                  # Papers, roadmap, predictions
├── results/                    # Experimental results
├── data/                       # Wikipedia and GitHub data
├── reproducibility_package/    # Reproduction scripts
├── *.py                        # Research scripts
└── requirements.txt            # Dependencies
```

## Key Files

| File | Purpose |
|------|---------|
| `documents/RP001_Paper_Draft.md` | Full paper draft |
| `documents/THEORIA_Roadmap.md` | Phase-wise goals |
| `documents/THEORIA_Predictions.md` | Future predictions |
| `reproducibility_package/rp001/reproduce_rp001.py` | Reproduction script |
| `rp001_validation.py` | Wikipedia analysis |
| `rp001_cross_platform.py` | GitHub analysis |

## Current Status

| Component | Status |
|-----------|--------|
| Core Architecture | ✅ Complete |
| Discovery Engine | ✅ Complete |
| Research Programs | ✅ Complete |
| Validation Framework | ✅ Complete |
| Real Data Validation | ✅ Complete |
| Cross-Platform (GitHub) | ✅ Complete |
| Reproducibility | ✅ Complete |
| Paper Draft | ✅ Complete |

## What Remains

1. **Independent Reproduction**: Others running the reproduction script
2. **Paper Refinement**: Peer review and revision
3. **Prediction Tracking**: Monitoring predictions (2027-2030)
4. **Additional Platforms**: Reddit, Stack Overflow validation

## How to Contribute

1. Run the reproduction script
2. Verify the results independently
3. Report any discrepancies
4. Suggest improvements

## Citation

```
THEORIA Project. "Persistent Dissent and Community Fragmentation: 
Evidence from Simulations, Wikipedia, and GitHub." 
June 2026.
```

## Contact

Repository: https://github.com/rajesh00618/theoria-deployment
