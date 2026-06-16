#!/usr/bin/env python3
"""
THEORIA RP-001 Standalone Reproducer
======================================

One-command reproduction of RP-001 results.

Usage:
    python reproduce.py

Requirements:
    pip install numpy scipy

Expected output:
    - Statistical test results
    - p-value for dissent-fragmentation hypothesis
    - Reproducibility confirmation
"""

import os
import sys
import json
import hashlib
from collections import Counter
from datetime import datetime

import numpy as np
from scipy import stats


def compute_dissent_fragmentation(revisions, dissent_threshold=3):
    """
    Compute dissent fraction and fragmentation for a set of revisions.
    
    Args:
        revisions: List of dicts with 'user' field
        dissent_threshold: Minimum edits to count as persistent contributor
    
    Returns:
        dict with dissent_fraction and fragmentation
    """
    user_counts = Counter(r["user"] for r in revisions)
    total_edits = len(revisions)
    n_users = len(user_counts)
    
    # Dissent fraction: persistent contributors / total users
    persistent = sum(1 for u, c in user_counts.items() if c >= dissent_threshold)
    dissent_fraction = persistent / max(n_users, 1)
    
    # Fragmentation: 1 - Herfindahl index
    herfindahl = sum((c / total_edits) ** 2 for c in user_counts.values())
    fragmentation = 1.0 - herfindahl
    
    return {
        "n_edits": total_edits,
        "n_users": n_users,
        "n_persistent": persistent,
        "dissent_fraction": float(dissent_fraction),
        "fragmentation": float(fragmentation),
    }


def analyze_article(revisions):
    """Analyze a single article's revisions."""
    return compute_dissent_fragmentation(revisions)


def fetch_wikipedia_revisions(title, limit=500):
    """
    Fetch Wikipedia revisions via public API.
    
    Returns list of dicts with 'user' field.
    """
    import urllib.request
    import urllib.parse
    
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvprop": "user|timestamp",
        "rvlimit": str(limit),
        "format": "json",
    }
    
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full_url, headers={"User-Agent": "THEORIA-RP001/1.0"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    revisions = []
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        for rev in page_data.get("revisions", []):
            revisions.append({
                "user": rev.get("user", "unknown"),
                "timestamp": rev.get("timestamp", ""),
            })
    
    return revisions


def run_validation():
    """Run the full RP-001 validation."""
    print("=" * 70)
    print("  THEORIA RP-001 Reproducibility Package")
    print("  Dissent-Fragmentation Hypothesis")
    print("=" * 70)
    
    # Define controversial and control articles
    controversial = [
        "Climate change", "Evolution", "Vaccination", "Nuclear power",
        "Gun control", "Abortion", "Climate change denial",
        "Evolution as fact and theory", "Nuclear power debate",
        "Gun violence in the United States", "Abortion in the United States",
        "Genetically modified food controversies", "COVID-19 misinformation",
        "Creationism",
    ]
    
    # Check for cached data
    data_dir = "data/wikipedia"
    use_cache = os.path.exists(data_dir)
    
    if use_cache:
        print("\n  Using cached Wikipedia data...")
        results = {}
        for filename in os.listdir(data_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(data_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                title = page_data.get("title", "")
                revisions = []
                for rev in page_data.get("revisions", []):
                    revisions.append({"user": rev.get("user", "unknown")})
                
                if len(revisions) >= 10:
                    results[title] = analyze_article(revisions)
    else:
        print("\n  Fetching Wikipedia data (this may take a minute)...")
        articles = [
            "Climate change", "Evolution", "Vaccination", "Nuclear power",
            "Gun control", "Abortion", "Dog", "Banana", "Water", "Gravity",
        ]
        results = {}
        for article in articles:
            try:
                revisions = fetch_wikipedia_revisions(article)
                if len(revisions) >= 10:
                    results[article] = analyze_article(revisions)
                    print(f"    Fetched: {article} ({len(revisions)} revisions)")
            except Exception as e:
                print(f"    Error fetching {article}: {e}")
    
    if not results:
        print("\n  No data available. Cannot validate.")
        return
    
    # Display results
    print(f"\n  Analyzed {len(results)} articles")
    print(f"\n  {'Article':<35} {'Edits':>6} {'Users':>6} {'Dissent%':>9} {'Fragment':>9}")
    print(f"  {'-'*65}")
    for title, m in sorted(results.items()):
        print(f"  {title:<35} {m['n_edits']:>6} {m['n_users']:>6} "
              f"{m['dissent_fraction']:>8.1%} {m['fragmentation']:>9.3f}")
    
    # Statistical test
    cont_dissent = [m["dissent_fraction"] for t, m in results.items() if t in controversial]
    ctrl_dissent = [m["dissent_fraction"] for t, m in results.items() if t not in controversial]
    
    if cont_dissent and ctrl_dissent:
        t_stat, p_value = stats.ttest_ind(cont_dissent, ctrl_dissent)
        
        print(f"\n  Statistical Test:")
        print(f"  Controversial: n={len(cont_dissent)}, mean={np.mean(cont_dissent):.1%}")
        print(f"  Control: n={len(ctrl_dissent)}, mean={np.mean(ctrl_dissent):.1%}")
        print(f"  t={t_stat:.3f}, p={p_value:.4f}")
        
        if p_value < 0.05:
            print(f"\n  RESULT: SIGNIFICANT (p < 0.05)")
            print(f"  The Dissent-Fragmentation hypothesis is supported.")
        else:
            print(f"\n  RESULT: Not significant (p >= 0.05)")
            print(f"  The Dissent-Fragmentation hypothesis is not supported with this data.")
    else:
        print("\n  Insufficient data for statistical test.")
    
    # Compute hash for reproducibility verification
    result_str = json.dumps(results, sort_keys=True)
    result_hash = hashlib.sha256(result_str.encode()).hexdigest()[:16]
    print(f"\n  Result hash: {result_hash}")
    print(f"  Timestamp: {datetime.now().isoformat()}")
    print(f"\n{'='*70}")


if __name__ == "__main__":
    run_validation()
