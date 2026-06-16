#!/usr/bin/env python3
"""
THEORIA RP-001 Reproducer v2
==============================

One-command reproduction of RP-001 results.

Usage:
    python reproduce.py

Requirements:
    pip install numpy scipy

Expected output:
    p ≈ 0.0004 (statistically significant)
"""

import os
import sys
import json
import hashlib
from collections import Counter
from datetime import datetime

import numpy as np
from scipy import stats


# Configuration
DATA_DIR = "data/robustness_fast"
DISSENT_THRESHOLD = 3
BOT_PATTERNS = ["bot", "abot", "greenc", "hager", "citation"]

# Article lists
CONTROVERSIAL = [
    "Abortion", "Gun control", "Immigration", "Capital punishment",
    "Same-sex marriage", "Climate change", "Evolution", "Vaccination",
    "Nuclear power", "Brexit", "Donald Trump", "Barack Obama",
    "Global warming", "Genetically modified food", "COVID-19 misinformation",
    "Alternative medicine", "Homeopathy", "Climate change denial",
    "Evolution as fact and theory", "Creationism", "Intelligent design",
    "Holocaust denial", "Slavery in the United States", "Vietnam War",
    "Islam", "Christianity", "Scientology",
    "Net neutrality", "Surveillance capitalism",
    "Capitalism", "Socialism", "Communism", "Marxism",
    "Marijuana", "Opioid epidemic", "Feminism",
]


def load_data():
    """Load Wikipedia revision data."""
    articles = {}
    for article in CONTROVERSIAL:
        cache_file = os.path.join(DATA_DIR, f"{article.replace(' ', '_')}.json")
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                articles[article] = json.load(f)
    
    # Load control articles
    control_files = [f for f in os.listdir(DATA_DIR) 
                    if f.endswith('.json') and f.replace('.json', '').replace('_', ' ') not in CONTROVERSIAL]
    for f in control_files:
        article = f.replace('.json', '').replace('_', ' ')
        with open(os.path.join(DATA_DIR, f)) as fh:
            articles[article] = json.load(fh)
    
    return articles


def compute_metrics(revisions):
    """Compute persistent editor fraction (excluding bots)."""
    if not revisions or len(revisions) < 10:
        return None
    
    user_counts = Counter(r["user"] for r in revisions)
    n_users = len(user_counts)
    
    persistent = sum(1 for u, c in user_counts.items() 
                    if c >= DISSENT_THRESHOLD and not any(b in u.lower() for b in BOT_PATTERNS))
    
    return persistent / max(n_users, 1)


def run_analysis():
    """Run the full analysis."""
    print("=" * 70)
    print("  THEORIA RP-001 Reproducer")
    print("  Persistent Editing in Controversial Wikipedia Articles")
    print("=" * 70)
    
    # Load data
    print("\n  Loading data...")
    articles = load_data()
    print(f"  Loaded {len(articles)} articles")
    
    # Compute metrics
    article_metrics = {}
    for article, revisions in articles.items():
        metrics = compute_metrics(revisions)
        if metrics is not None:
            article_metrics[article] = metrics
    
    cont = {k: v for k, v in article_metrics.items() if k in CONTROVERSIAL}
    ctrl = {k: v for k, v in article_metrics.items() if k not in CONTROVERSIAL}
    
    print(f"  Controversial: {len(cont)}")
    print(f"  Control: {len(ctrl)}")
    
    # Statistical tests
    cont_values = list(cont.values())
    ctrl_values = list(ctrl.values())
    
    t_stat, p_value = stats.ttest_ind(cont_values, ctrl_values)
    t_stat_w, p_value_w = stats.ttest_ind(cont_values, ctrl_values, equal_var=False)
    u_stat, p_value_u = stats.mannwhitneyu(cont_values, ctrl_values, alternative='two-sided')
    
    pooled_std = np.sqrt((np.std(cont_values, ddof=1)**2 + np.std(ctrl_values, ddof=1)**2) / 2)
    cohens_d = (np.mean(cont_values) - np.mean(ctrl_values)) / pooled_std if pooled_std > 0 else 0
    
    # Leave-one-out
    loo_sig = 0
    for excluded in article_metrics:
        remaining = {k: v for k, v in article_metrics.items() if k != excluded}
        c = [v for k, v in remaining.items() if k in CONTROVERSIAL]
        r = [v for k, v in remaining.items() if k not in CONTROVERSIAL]
        if c and r:
            _, p = stats.ttest_ind(c, r)
            if p < 0.05:
                loo_sig += 1
    
    # Results
    print(f"\n  Results:")
    print(f"  Controversial mean: {np.mean(cont_values):.1%}")
    print(f"  Control mean: {np.mean(ctrl_values):.1%}")
    print(f"  Student t-test: p={p_value:.6f}")
    print(f"  Welch t-test: p={p_value_w:.6f}")
    print(f"  Mann-Whitney: p={p_value_u:.6f}")
    print(f"  Cohen's d: {cohens_d:.3f}")
    print(f"  Leave-one-out: {loo_sig}/{len(article_metrics)}")
    
    # Hash
    result_str = json.dumps({
        "n": len(article_metrics),
        "cont_mean": float(np.mean(cont_values)),
        "ctrl_mean": float(np.mean(ctrl_values)),
        "p": float(p_value),
        "d": float(cohens_d),
    }, sort_keys=True)
    result_hash = hashlib.sha256(result_str.encode()).hexdigest()[:16]
    
    print(f"\n  Hash: {result_hash}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"\n{'='*70}")
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_articles": len(article_metrics),
        "controversial_mean": float(np.mean(cont_values)),
        "control_mean": float(np.mean(ctrl_values)),
        "student_p": float(p_value),
        "welch_p": float(p_value_w),
        "mann_whitney_p": float(p_value_u),
        "cohens_d": float(cohens_d),
        "loo_robust": loo_sig,
        "loo_total": len(article_metrics),
        "result_hash": result_hash,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/rp001_reproduction.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Saved to results/rp001_reproduction.json")


if __name__ == "__main__":
    run_analysis()
