# THEORIA Project Summary

## What Is THEORIA?

THEORIA is a research prototype exploring autonomous scientific discovery. It has **one validated finding** backed by real data and independently reproduced.

## Validated Finding: RP-001

**Persistent Editing in Controversial Wikipedia Articles**: Controversial Wikipedia articles have significantly more persistent editors than non-controversial articles.

- **Statistical test**: p = 0.0004 (significant)
- **Data**: 82 real Wikipedia articles (36 controversial, 46 control)
- **Effect**: Controversial articles have 18.6% mean persistent editing vs 14.5% in controls
- **Robustness**: 82/82 leave-one-out, significant at all thresholds (2-10 edits)
- **Reproduced**: Yes, by 2 independent parties

## How to Reproduce

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python rp001_final.py
```

## Project Status

| Component | Status |
|-----------|--------|
| RP-001 Validation | Complete, p = 0.0004 |
| Independent Reproduction | 2/5 complete |
| Paper Draft | Complete |
| Robustness Analysis | Complete |

## What This Project Is NOT

- Not a complete autonomous scientific discovery system
- Not validated beyond RP-001
- Not producing novel scientific discoveries automatically

## Honest Assessment

THEORIA is a research prototype with one validated, independently reproduced finding. The architecture is clean and extensible, but most layers are stubs waiting for real implementation.

## Files

- `rp001_final.py` — Main analysis (bot-excluded)
- `REPRODUCE.md` — Reproduction instructions
- `requirements.txt` — Minimal dependencies (numpy, scipy)
- `data/robustness_fast/` — Real Wikipedia revision data
- `documents/RP001_Paper_Draft.md` — Paper draft

## Contact

Rajesh Gurugubelli
2026
