# Persistent Editing in Controversial Wikipedia Articles

## Abstract

We investigate whether controversial Wikipedia articles have higher fractions of persistent editors than non-controversial articles. Analysis of 82 articles (36 controversial, 46 control) shows that controversial articles have significantly more persistent editors (18.6% vs 14.5%, p = 0.0004, Cohen's d = 0.80). The result is robust to leave-one-out sensitivity analysis (82/82) and holds at all tested thresholds (2-10 edits). We discuss limitations including construct validity, selection bias, and the need for ground-truth validation.

## 1. Introduction

Wikipedia articles on controversial topics are known to have active editing histories. We investigate whether this activity can be measured systematically.

**Research question**: Do controversial Wikipedia articles have higher fractions of persistent editors than non-controversial articles?

## 2. Methods

### 2.1 Article Selection

We selected 82 Wikipedia articles:
- **36 controversial articles**: Topics with known editing disputes (e.g., Climate change, Evolution, Gun control)
- **46 control articles**: Topics with low controversy potential (e.g., Photosynthesis, DNA, Gravity)

**Limitation**: Article selection was not blinded. Future work should use objective selection criteria.

### 2.2 Data Collection

For each article, we collected revision histories via the MediaWiki API:
- Up to 1000 revisions per article
- User identifiers for each revision

### 2.3 Metrics

**Persistent editor fraction**: Fraction of unique editors with >= 3 edits, excluding known bots.

**Bot exclusion**: Users matching common bot patterns (e.g., "bot", "abot", "greenc", "citation") were excluded.

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
| Controversial | 36 | 18.6% | 6.1% |
| Control | 46 | 14.5% | 4.0% |

### 3.2 Statistical Tests

| Test | Statistic | p-value |
|------|-----------|---------|
| Student t | t = 3.695 | p = 0.000401 |
| Welch t | t = 3.512 | p = 0.000877 |
| Mann-Whitney U | U = 1201.0 | p = 0.000500 |

### 3.3 Effect Size

Cohen's d = 0.80 (large effect)

Absolute difference: 4.1 percentage points

### 3.4 Sensitivity Analysis

**Leave-one-out**: 82/82 — result remains significant when any single article is removed.

**Threshold sensitivity**:

| Threshold | Cont Mean | Ctrl Mean | p-value | Significant? |
|-----------|-----------|-----------|---------|--------------|
| >= 2 | 33.5% | 28.9% | 0.0012 | Yes |
| >= 3 | 18.6% | 14.5% | 0.0004 | Yes |
| >= 4 | 12.8% | 9.3% | 0.0002 | Yes |
| >= 5 | 9.6% | 6.6% | 0.0001 | Yes |
| >= 10 | 4.1% | 2.7% | 0.0009 | Yes |

The result is significant at ALL thresholds.

### 3.5 Bot Analysis

Across sampled articles, 8-18% of "persistent" editors were bots (Citation bot, GreenC bot, AnomieBOT, OAbot). These perform maintenance tasks and do not express editorial disagreement.

## 4. Discussion

### 4.1 Main Finding

Controversial Wikipedia articles have more persistent editors than control articles. This difference is statistically significant at all thresholds (p < 0.002), even after excluding bots.

### 4.2 Interpretation

Controversial articles attract more persistent human editors. This is consistent with the idea that controversial topics generate sustained engagement.

### 4.3 Limitations

1. **Construct validity**: "Persistent editing" does not necessarily indicate "dissent." It measures sustained engagement.
2. **Selection bias**: Articles were manually classified without blinding.
3. **Truncation**: 80/82 articles truncated at 1000 revisions.
4. **No ground truth**: The metric has not been validated against actual disagreement measures.

### 4.4 Future Work

1. Validate the metric against ground truth (e.g., talk page conflicts, revert wars)
2. Use objective article selection criteria
3. Test on additional platforms (GitHub, Reddit)
4. Use Wikipedia's official bot list for exclusion

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
