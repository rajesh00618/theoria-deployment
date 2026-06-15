#!/usr/bin/env python3
"""
RP-001 Reproducibility Package: Dissent-Fragmentation Hypothesis

Self-contained script that reproduces the Wikipedia validation results.
Run: python reproduce_rp001.py
"""

import os
import sys
import json
from collections import Counter
from datetime import datetime

import numpy as np
from scipy import stats


def parse_wikipedia_data(data):
    revisions = []
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_data in pages.items():
        title = page_data.get("title", "unknown")
        for rev in page_data.get("revisions", []):
            revisions.append({
                "page": title,
                "user": rev.get("user", "unknown"),
                "timestamp": rev.get("timestamp", ""),
            })
    return revisions


def identify_dissenters(revisions, dissent_threshold=5):
    user_counts = Counter(r["user"] for r in revisions)
    total_edits = len(revisions)
    return [{"user": u, "edit_count": c, "fraction": c / total_edits}
            for u, c in user_counts.items() if c >= dissent_threshold]


def compute_fragmentation_metric(revisions):
    if len(revisions) < 10:
        return 0.0
    user_counts = Counter(r["user"] for r in revisions)
    total_edits = len(revisions)
    herfindahl = sum((c / total_edits) ** 2 for c in user_counts.values())
    return 1.0 - herfindahl


def analyze_article(revisions):
    n_edits = len(revisions)
    users = Counter(r["user"] for r in revisions)
    n_users = len(users)
    dissenters = identify_dissenters(revisions, dissent_threshold=3)
    dissent_fraction = len(dissenters) / max(n_users, 1)
    fragmentation = compute_fragmentation_metric(revisions)
    return {
        "n_edits": n_edits,
        "n_users": n_users,
        "n_dissenters": len(dissenters),
        "dissent_fraction": float(dissent_fraction),
        "fragmentation": float(fragmentation),
    }


def main():
    print("=" * 70)
    print("  RP-001 Reproducibility Package")
    print("  Dissent-Fragmentation Hypothesis")
    print("=" * 70)

    data_dir = "data/wikipedia"
    if not os.path.exists(data_dir):
        print(f"\n  Error: {data_dir} not found")
        print("  Run fetch_wikipedia_data.py first")
        return

    articles = {}
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
            revisions = parse_wikipedia_data(data)
            if len(revisions) > 10:
                title = revisions[0]["page"]
                articles[title] = analyze_article(revisions)

    print(f"\n  Analyzed {len(articles)} articles")
    print(f"\n  {'Article':<35} {'Edits':>6} {'Users':>6} {'Dissent%':>9} {'Fragment':>9}")
    print(f"  {'-'*65}")
    for title, m in sorted(articles.items()):
        print(f"  {title:<35} {m['n_edits']:>6} {m['n_users']:>6} "
              f"{m['dissent_fraction']:>8.1%} {m['fragmentation']:>9.3f}")

    controversial = ["Climate change", "Evolution", "Vaccination", "Nuclear power",
                    "Gun control", "Abortion", "Climate change denial",
                    "Evolution as fact and theory", "Nuclear power debate",
                    "Gun violence in the United States", "Abortion in the United States",
                    "Genetically modified food controversies", "COVID-19 misinformation",
                    "Creationism"]
    cont_dissent = [m["dissent_fraction"] for t, m in articles.items() if t in controversial]
    ctrl_dissent = [m["dissent_fraction"] for t, m in articles.items() if t not in controversial]

    if cont_dissent and ctrl_dissent:
        t_stat, p_value = stats.ttest_ind(cont_dissent, ctrl_dissent)
        print(f"\n  Statistical Test:")
        print(f"  Controversial: n={len(cont_dissent)}, mean={np.mean(cont_dissent):.1%}")
        print(f"  Control: n={len(ctrl_dissent)}, mean={np.mean(ctrl_dissent):.1%}")
        print(f"  t={t_stat:.3f}, p={p_value:.4f}")
        if p_value < 0.05:
            print(f"  RESULT: SIGNIFICANT (p < 0.05)")
        else:
            print(f"  RESULT: Not significant (p >= 0.05)")

    with open("results/rp001_reproduction_results.json", "w") as f:
        json.dump({"articles": articles, "n_articles": len(articles)}, f, indent=2)

    print(f"\n  Results saved to results/rp001_reproduction_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
