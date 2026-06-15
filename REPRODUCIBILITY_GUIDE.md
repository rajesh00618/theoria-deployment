# RP-001-AD: Actual Data Validation

## Goal

Test whether the Contrarian Threshold Theory (~10% threshold) appears in actual historical data from Reddit, Wikipedia, and GitHub.

## Status

**Framework ready. Awaiting actual data.**

## What's Needed

### Reddit Data
- API: PRAW (Python Reddit API Wrapper)
- Credentials: https://www.reddit.com/prefs/apps
- Data: Comment histories from subreddits
- Output: `data/reddit_comments.json`

### Wikipedia Data
- API: Wikipedia API (no key needed)
- Data: Revision histories from articles
- Output: `data/wikipedia_revisions.json`

### GitHub Data
- API: GitHub Events API
- Credentials: Optional (higher rate limits with token)
- Data: Commit/issue/PR events from repos
- Output: `data/github_events.json`

## How to Run

```bash
# 1. Install dependencies
pip install praw requests numpy scipy

# 2. Collect data (edit lists in collect_actual_data.py)
python collect_actual_data.py

# 3. Run validation
python rp001_actual_data_validation.py

# 4. Results saved to results/rp001_actual_data_results.json
```

## Expected Output

If the contrarian threshold exists in real data:

```
Reddit:      CONFIRMED (p<0.05, d>0.5)
Wikipedia:   CONFIRMED (p<0.05, d>0.5)
GitHub:      CONFIRMED (p<0.05, d>0.5)
```

If the threshold does NOT exist:

```
Reddit:      NOT SUPPORTED (p>0.05)
Wikipedia:   NOT SUPPORTED (p>0.05)
GitHub:      NOT SUPPORTED (p>0.05)
```

## What This Would Prove

If confirmed:
- RP-001 moves from simulation result to empirical finding
- The ~10% threshold generalizes beyond THEORIA's models
- Strong candidate for publication

If not confirmed:
- The threshold is specific to THEORIA's simulation family
- Still valuable, but narrower claim
- Need to revise theory

## Files

- `rp001_actual_data_validation.py` — Analysis framework
- `collect_actual_data.py` — Data collection scripts
- `data/` — Directory for actual data files
- `results/rp001_actual_data_results.json` — Results
