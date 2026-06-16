# THEORIA Project Summary

## What Is THEORIA?

THEORIA is a research prototype exploring autonomous scientific discovery. It has **one validated discovery** backed by real data and independently reproduced.

## Validated Discovery: RP-001

**Dissent-Fragmentation Hypothesis**: Controversial Wikipedia articles have significantly higher persistent dissent than non-controversial articles.

- **Statistical test**: p = 0.0168 (significant)
- **Data**: 22 real Wikipedia articles (14 controversial, 8 control)
- **Effect**: Controversial articles have 22.3% mean dissent vs 17.3% in controls
- **Reproduced**: Yes, by independent party on different machine

## How to Reproduce

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python reproduce.py
```

## Project Status

| Component | Status |
|-----------|--------|
| RP-001 Validation | Complete, p = 0.0168 |
| Independent Reproduction | 1/5 complete |
| Paper Draft | Complete |
| Prediction Tracking | 4 predictions frozen |
| Other Discoveries | Not yet validated |

## What This Project Is NOT

- Not a complete autonomous scientific discovery system
- Not validated beyond RP-001
- Not producing novel scientific discoveries automatically

## Honest Assessment

THEORIA is a research prototype with one validated, independently reproduced discovery. The architecture is clean and extensible, but most layers are stubs waiting for real implementation.

## Files

- `reproduce.py` — Single entry point for reproduction
- `REPRODUCE.md` — Reproduction instructions
- `requirements.txt` — Minimal dependencies (numpy, scipy)
- `data/wikipedia/` — Real Wikipedia revision data
- `documents/RP001_Paper_Draft.md` — Paper draft

## Contact

Rajesh Gurugubelli
2026
