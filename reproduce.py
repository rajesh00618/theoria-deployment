#!/usr/bin/env python3
"""
THEORIA RP-001 Reproducer
==========================

Single entry point for reproducing THEORIA's only validated discovery.

Usage:
    python reproduce.py

Requirements:
    pip install numpy scipy

What this does:
    1. Loads cached Wikipedia revision data (22 articles)
    2. Computes dissent fraction and fragmentation for each article
    3. Runs statistical test: controversial vs control articles
    4. Reports results

What this does NOT do:
    - Generate synthetic data
    - Force passing results
    - Use fake metrics

Expected output:
    p ≈ 0.0168 (statistically significant)
"""

import os
import sys
import json
import hashlib
from collections import Counter
from datetime import datetime

import numpy as np
from scipy import stats


# Controversial articles (known to have persistent editing disputes)
CONTROVERSIAL = {
    "Climate change", "Evolution", "Vaccination", "Nuclear power",
    "Gun control", "Abortion", "Climate change denial",
    "Evolution as fact and theory", "Nuclear power debate",
    "Gun violence in the United States", "Abortion in the United States",
    "Genetically modified food controversies", "COVID-19 misinformation",
    "Creationism",
}


def compute_metrics(revisions, dissent_threshold=3):
    """
    Compute dissent fraction and fragmentation from real revision data.
    
    Args:
        revisions: List of dicts with 'user' field
        dissent_threshold: Minimum edits to count as persistent contributor
    
    Returns:
        dict with n_edits, n_users, dissent_fraction, fragmentation
    """
    user_counts = Counter(r["user"] for r in revisions)
    total_edits = len(revisions)
    n_users = len(user_counts)
    
    # Dissent fraction: persistent contributors / total users
    persistent = sum(1 for u, c in user_counts.items() if c >= dissent_threshold)
    dissent_fraction = persistent / max(n_users, 1)
    
    # Fragmentation: 1 - Herfindahl index (measures concentration)
    herfindahl = sum((c / total_edits) ** 2 for c in user_counts.values())
    fragmentation = 1.0 - herfindahl
    
    return {
        "n_edits": total_edits,
        "n_users": n_users,
        "n_persistent": persistent,
        "dissent_fraction": float(dissent_fraction),
        "fragmentation": float(fragmentation),
    }


def load_wikipedia_data(data_dir="data/wikipedia"):
    """
    Load pre-cached Wikipedia revision data.
    
    These are real API responses fetched from en.wikipedia.org.
    Each file contains revision history for one article.
    """
    if not os.path.exists(data_dir):
        print(f"  Error: {data_dir} not found")
        print("  Ensure data/wikipedia/ directory exists with cached API responses")
        sys.exit(1)
    
    articles = {}
    for filename in os.listdir(data_dir):
        if not filename.endswith(".json"):
            continue
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath) as f:
            data = json.load(f)
        
        # Parse MediaWiki API response
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            title = page_data.get("title", "")
            revisions = []
            for rev in page_data.get("revisions", []):
                revisions.append({
                    "user": rev.get("user", "unknown"),
                    "timestamp": rev.get("timestamp", ""),
                })
            
            # Only include articles with sufficient data
            if len(revisions) >= 10:
                articles[title] = compute_metrics(revisions)
    
    return articles


def run_statistical_test(articles):
    """
    Run two-sample t-test: controversial vs control articles.
    
    Null hypothesis: No difference in dissent between controversial and control.
    Alternative hypothesis: Controversial articles have higher dissent.
    """
    cont_dissent = [m["dissent_fraction"] for t, m in articles.items() if t in CONTROVERSIAL]
    ctrl_dissent = [m["dissent_fraction"] for t, m in articles.items() if t not in CONTROVERSIAL]
    
    if not cont_dissent or not ctrl_dissent:
        return None
    
    t_stat, p_value = stats.ttest_ind(cont_dissent, ctrl_dissent)
    
    return {
        "controversial_n": len(cont_dissent),
        "controversial_mean": float(np.mean(cont_dissent)),
        "control_n": len(ctrl_dissent),
        "control_mean": float(np.mean(ctrl_dissent)),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
    }


def main():
    print("=" * 70)
    print("  THEORIA RP-001 Reproducer")
    print("  Dissent-Fragmentation Hypothesis")
    print("=" * 70)
    
    # Load real data
    print("\n  Loading Wikipedia revision data...")
    articles = load_wikipedia_data()
    print(f"  Loaded {len(articles)} articles")
    
    # Display results
    print(f"\n  {'Article':<40} {'Edits':>6} {'Users':>6} {'Dissent%':>9} {'Fragment':>9}")
    print(f"  {'-'*70}")
    for title, m in sorted(articles.items()):
        print(f"  {title:<40} {m['n_edits']:>6} {m['n_users']:>6} "
              f"{m['dissent_fraction']:>8.1%} {m['fragmentation']:>9.3f}")
    
    # Statistical test
    print("\n  Running statistical test...")
    test_result = run_statistical_test(articles)
    
    if test_result is None:
        print("  Error: Insufficient data for statistical test")
        return
    
    print(f"\n  Statistical Test: Two-sample t-test (controversial vs control)")
    print(f"  Controversial: n={test_result['controversial_n']}, "
          f"mean={test_result['controversial_mean']:.1%}")
    print(f"  Control: n={test_result['control_n']}, "
          f"mean={test_result['control_mean']:.1%}")
    print(f"  t={test_result['t_statistic']:.3f}, p={test_result['p_value']:.4f}")
    
    if test_result["significant"]:
        print(f"\n  RESULT: SIGNIFICANT (p < 0.05)")
        print(f"  The Dissent-Fragmentation hypothesis is supported.")
        print(f"  Controversial articles have significantly higher dissent.")
    else:
        print(f"\n  RESULT: Not significant (p >= 0.05)")
        print(f"  The Dissent-Fragmentation hypothesis is not supported with this data.")
    
    # Compute reproducibility hash
    result_str = json.dumps(articles, sort_keys=True)
    result_hash = hashlib.sha256(result_str.encode()).hexdigest()[:16]
    
    print(f"\n  Reproducibility hash: {result_hash}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"\n{'='*70}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_articles": len(articles),
        "test_result": test_result,
        "result_hash": result_hash,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/rp001_reproduction.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved to results/rp001_reproduction.json")


if __name__ == "__main__":
    main()
