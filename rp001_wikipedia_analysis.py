#!/usr/bin/env python3
"""
RP-001-AD: Actual Wikipedia Data Analysis

Tests Contrarian Threshold Theory on real Wikipedia revision histories.
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

import numpy as np
from scipy import stats
from collections import Counter
from datetime import datetime


def parse_wikipedia_data(data):
    """Parse Wikipedia API response into structured format."""
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


def compute_edit_bursts(revisions, window_hours=24):
    """Identify edit bursts (many edits in short time)."""
    if not revisions:
        return []

    bursts = []
    current_burst = [revisions[0]]

    for i in range(1, len(revisions)):
        try:
            t1 = datetime.fromisoformat(revisions[i-1]["timestamp"].replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(revisions[i]["timestamp"].replace("Z", "+00:00"))
            diff_hours = abs((t2 - t1).total_seconds()) / 3600
        except:
            diff_hours = 25

        if diff_hours < window_hours:
            current_burst.append(revisions[i])
        else:
            if len(current_burst) >= 3:
                bursts.append(current_burst)
            current_burst = [revisions[i]]

    if len(current_burst) >= 3:
        bursts.append(current_burst)

    return bursts


def identify_dissenters(revisions, dissent_threshold=5):
    """Identify users who edit frequently (potential dissenters)."""
    user_counts = Counter(r["user"] for r in revisions)
    total_edits = len(revisions)

    dissenters = []
    for user, count in user_counts.items():
        if count >= dissent_threshold:
            dissenters.append({
                "user": user,
                "edit_count": count,
                "fraction": count / total_edits,
            })

    return dissenters


def compute_fragmentation_metric(revisions):
    """Compute fragmentation from edit patterns."""
    if len(revisions) < 10:
        return 0.0

    user_counts = Counter(r["user"] for r in revisions)
    unique_users = len(user_counts)
    total_edits = len(revisions)

    herfindahl = sum((c / total_edits) ** 2 for c in user_counts.values())
    fragmentation = 1.0 - herfindahl

    return fragmentation


def analyze_article(revisions):
    """Full analysis of a single article."""
    n_edits = len(revisions)
    users = Counter(r["user"] for r in revisions)
    n_users = len(users)

    dissenters = identify_dissenters(revisions, dissent_threshold=3)
    n_dissenters = len(dissenters)
    dissent_fraction = n_dissenters / max(n_users, 1)

    fragmentation = compute_fragmentation_metric(revisions)

    bursts = compute_edit_bursts(revisions)
    n_bursts = len(bursts)

    burst_intensity = 0
    if bursts:
        burst_sizes = [len(b) for b in bursts]
        burst_intensity = np.mean(burst_sizes) / max(n_edits, 1)

    return {
        "n_edits": n_edits,
        "n_users": n_users,
        "n_dissenters": n_dissenters,
        "dissent_fraction": float(dissent_fraction),
        "fragmentation": float(fragmentation),
        "n_bursts": n_bursts,
        "burst_intensity": float(burst_intensity),
        "controversy_score": float(dissent_fraction * 0.5 + fragmentation * 0.3 + burst_intensity * 0.2),
    }


def main():
    print("=" * 70)
    print("  RP-001-AD: Wikipedia Real Data Analysis")
    print("=" * 70)

    wikipedia_data_dir = "data/wikipedia"

    articles = {}

    climate_file = os.path.join(wikipedia_data_dir, "climate_change.json")
    if os.path.exists(climate_file):
        with open(climate_file) as f:
            data = json.load(f)
        revisions = parse_wikipedia_data(data)
        articles["Climate Change"] = analyze_article(revisions)
        print(f"\n  Climate Change: {len(revisions)} revisions")

    evolution_file = os.path.join(wikipedia_data_dir, "evolution.json")
    if os.path.exists(evolution_file):
        with open(evolution_file) as f:
            data = json.load(f)
        revisions = parse_wikipedia_data(data)
        articles["Evolution"] = analyze_article(revisions)
        print(f"  Evolution: {len(revisions)} revisions")

    if not articles:
        print("\n  No data found. Run collect_wikipedia_data.py first.")
        return

    print(f"\n{'='*70}")
    print("  RESULTS")
    print(f"{'='*70}")

    for name, metrics in articles.items():
        print(f"\n  {name}:")
        print(f"    Edits: {metrics['n_edits']}")
        print(f"    Users: {metrics['n_users']}")
        print(f"    Dissenters: {metrics['n_dissenters']} ({metrics['dissent_fraction']:.1%})")
        print(f"    Fragmentation: {metrics['fragmentation']:.3f}")
        print(f"    Edit bursts: {metrics['n_bursts']}")
        print(f"    Controversy score: {metrics['controversy_score']:.3f}")

    if len(articles) >= 2:
        dissent_fractions = [m["dissent_fraction"] for m in articles.values()]
        fragmentations = [m["fragmentation"] for m in articles.values()]

        correlation = np.corrcoef(dissent_fractions, fragmentations)[0, 1]
        print(f"\n  Dissent-Fragmentation correlation: {correlation:.3f}")

        if abs(correlation) > 0.5:
            print(f"  -> Strong correlation supports Contrarian Threshold Theory")
        elif abs(correlation) > 0.3:
            print(f"  -> Moderate correlation")
        else:
            print(f"  -> Weak correlation")

    with open("results/rp001_wikipedia_results.json", "w") as f:
        json.dump(articles, f, indent=2)

    print(f"\n  Results: results/rp001_wikipedia_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
