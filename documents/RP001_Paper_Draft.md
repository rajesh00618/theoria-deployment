# Persistent Editing in Controversial Wikipedia Articles: A Replication and Extension

**Note**: This paper was revised after external review. The original title ("Dissent-Fragmentation Hypothesis") was misleading because fragmentation was never measured. The revised title accurately reflects what was tested.

## Abstract

We investigate whether controversial Wikipedia articles have higher fractions of persistent editors than non-controversial articles. Analysis of 82 articles (36 controversial, 46 control) shows that controversial articles have significantly more persistent editors (20.8% vs 16.5%, p = 0.0007, Cohen's d = 0.77). However, this result is partially driven by bots being counted as persistent editors. When bots are excluded, the effect weakens but remains in the same direction. The finding is robust to leave-one-out sensitivity analysis (82/82). We discuss limitations including construct validity, selection bias, and the need for ground-truth validation of the dissent metric.

## 1. Introduction

Wikipedia articles on controversial topics are known to have active editing histories. We investigate whether this activity can be measured systematically.

**Research question**: Do controversial Wikipedia articles have higher fractions of persistent editors than non-controversial articles?

**Note on terminology**: The original draft used the term "dissent" to describe persistent editing. This was misleading because persistent editing does not necessarily indicate disagreement. We now use "persistent editing" to accurately describe what was measured.

## 2. Methods

### 2.1 Article Selection

We selected 82 Wikipedia articles:
- **36 controversial articles**: Topics with known editing disputes (e.g., Climate change, Evolution, Gun control)
- **46 control articles**: Topics with low controversy potential (e.g., Photosynthesis, DNA, Gravity)

**Limitation**: Article selection was not blinded. Future work should use objective selection criteria or blinded classification.

### 2.2 Data Collection

For each article, we collected revision histories via the MediaWiki API:
- Up to 1000 revisions per article
- User identifiers for each revision

### 2.3 Metrics

**Persistent editor fraction**: Fraction of unique editors with >= 3 edits, excluding known bots.

**Bot exclusion**: Users matching common bot patterns (e.g., "bot", "abot", "greenc", "citation") were excluded from the persistent editor count.

### 2.4 Statistical Tests

1. Student's t-test
2. Welch's t-test (unequal variances)
3. Mann-Whitney U test (non-parametric)
4. Bootstrap 95% confidence interval
5. Leave-one-out sensitivity analysis
6. Threshold sensitivity analysis (thresholds: 2, 3, 4, 5, 10 edits)

## 3. Results

### 3.1 Descriptive Statistics

| Group | n | Mean Persistent | Std Dev |
|-------|---|-----------------|---------|
| Controversial | 36 | 20.8% | 6.4% |
| Control | 46 | 16.5% | 4.5% |

### 3.2 Statistical Tests

| Test | Statistic | p-value |
|------|-----------|---------|
| Student t | t = 3.536 | p = 0.000679 |
| Welch t | t = 3.390 | p = 0.001240 |
| Mann-Whitney U | U = 1196.0 | p = 0.000595 |

### 3.3 Effect Size

Cohen's d = 0.77 (large effect)

Absolute difference: 4.3 percentage points

### 3.4 Sensitivity Analysis

**Leave-one-out**: 82/82 — result remains significant when any single article is removed.

**Threshold sensitivity** (with bot exclusion):

| Threshold | Cont Mean | Ctrl Mean | p-value | Significant? |
|-----------|-----------|-----------|---------|--------------|
| >= 2 | 33.5% | 28.9% | 0.0012 | Yes |
| >= 3 | 18.6% | 14.5% | 0.0004 | Yes |
| >= 4 | 12.8% | 9.3% | 0.0002 | Yes |
| >= 5 | 9.6% | 6.6% | 0.0001 | Yes |
| >= 10 | 4.1% | 2.7% | 0.0009 | Yes |

**Finding**: The result is significant at ALL thresholds, even with bot exclusion. The effect is robust to threshold choice.

### 3.5 Bot Analysis

Across sampled articles, 8-18% of "persistent" editors were bots:
- Citation bot
- GreenC bot
- AnomieBOT
- OAbot

These bots perform maintenance tasks (adding citations, fixing links) and do not express editorial disagreement.

## 4. Discussion

### 4.1 Main Finding

Controversial Wikipedia articles have more persistent editors than control articles. This difference is statistically significant at all thresholds (p < 0.002), even after excluding bots.

### 4.2 Interpretation

Controversial articles attract more persistent human editors. This is consistent with the idea that controversial topics generate sustained engagement.

### 4.3 Limitations

1. **Construct validity**: "Persistent editing" does not necessarily indicate "dissent." It measures sustained engagement, which could be constructive editing, maintenance, or genuine disagreement.
2. **Selection bias**: Articles were manually classified without blinding.
3. **Truncation**: 80/82 articles truncated at 1000 revisions.
4. **No ground truth**: The metric has not been validated against actual disagreement measures (e.g., talk page conflicts, revert wars).

### 4.3 Limitations

1. **Construct validity**: "Persistent editing" does not measure "dissent." Bots and maintenance editors inflate the count.
2. **Selection bias**: Articles were manually classified without blinding.
3. **Truncation**: 80/82 articles truncated at 1000 revisions.
4. **No ground truth**: The dissent metric has not been validated against actual disagreement.

### 4.4 Future Work

1. Validate the metric against ground truth (e.g., talk page conflicts, revert wars)
2. Use objective article selection criteria
3. Test on additional platforms (GitHub, Reddit)
4. Exclude bots systematically using Wikipedia's bot list

## 5. Reproducibility

```bash
git clone https://github.com/rajesh00618/theoria-deployment.git
cd theoria-deployment
pip install numpy scipy
python rp001_final.py
```

## References

1. Deffuant, G., et al. (2000). Mixing beliefs among interacting agents. *Advances in Complex Systems*.
2. Hegselmann, R., & Krause, U. (2002). Opinion dynamics and bounded confidence models. *JASSS*.
3. Yasseri, T., et al. (2012). Dynamics of conflicts in Wikipedia. *PLoS ONE*.
4. Kittur, A., et al. (2007). He says, she says: conflict and coordination in Wikipedia. *CHI*.
5. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*.
