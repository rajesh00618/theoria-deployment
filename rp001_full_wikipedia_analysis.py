#!/usr/bin/env python3
"""
RP-001-AD: Full Wikipedia Analysis
6 controversial + 4 control articles from real Wikipedia data.
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

import numpy as np
from scipy import stats
from collections import Counter
from datetime import datetime


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


def compute_edit_bursts(revisions, window_hours=24):
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
    user_counts = Counter(r["user"] for r in revisions)
    total_edits = len(revisions)
    dissenters = []
    for user, count in user_counts.items():
        if count >= dissent_threshold:
            dissenters.append({"user": user, "edit_count": count, "fraction": count / total_edits})
    return dissenters


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
    n_dissenters = len(dissenters)
    dissent_fraction = n_dissenters / max(n_users, 1)
    fragmentation = compute_fragmentation_metric(revisions)
    bursts = compute_edit_bursts(revisions)
    burst_intensity = len(bursts) / max(n_edits, 1)
    return {
        "n_edits": n_edits,
        "n_users": n_users,
        "n_dissenters": n_dissenters,
        "dissent_fraction": float(dissent_fraction),
        "fragmentation": float(fragmentation),
        "burst_intensity": float(burst_intensity),
    }


def main():
    print("=" * 70)
    print("  RP-001-AD: Full Wikipedia Analysis")
    print("  6 controversial + 4 control articles")
    print("=" * 70)

    data_dir = "data/wikipedia"
    articles = {}

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath) as f:
                data = json.load(f)
            revisions = parse_wikipedia_data(data)
            if revisions:
                title = revisions[0]["page"]
                articles[title] = analyze_article(revisions)
                print(f"  {title}: {len(revisions)} revisions")

    if len(articles) < 2:
        print("  Need at least 2 articles")
        return

    print(f"\n{'='*70}")
    print("  RESULTS")
    print(f"{'='*70}")

    controversial = ["Climate change", "Evolution", "Vaccination", "Nuclear power", "Gun control", "Abortion",
                     "Climate change denial", "Evolution as fact and theory", "Nuclear power debate",
                     "Gun violence in the United States", "Abortion in the United States",
                     "Genetically modified food controversies", "COVID-19 misinformation", "Creationism"]
    control = ["Banana", "Water", "Dog", "Gravity", "Photosynthesis", "DNA", "Physics", "Biology"]

    cont_data = []
    ctrl_data = []

    print(f"\n  {'Article':<25} {'Edits':>6} {'Users':>6} {'Dissent%':>9} {'Fragment':>9}")
    print(f"  {'-'*55}")
    for title, metrics in sorted(articles.items()):
        label = "CONT" if title in controversial else "CTRL"
        print(f"  {title:<25} {metrics['n_edits']:>6} {metrics['n_users']:>6} "
              f"{metrics['dissent_fraction']:>8.1%} {metrics['fragmentation']:>9.3f}")
        if title in controversial:
            cont_data.append(metrics)
        elif title in control:
            ctrl_data.append(metrics)

    if cont_data and ctrl_data:
        cont_dissent = [m["dissent_fraction"] for m in cont_data]
        ctrl_dissent = [m["dissent_fraction"] for m in ctrl_data]
        cont_frag = [m["fragmentation"] for m in cont_data]
        ctrl_frag = [m["fragmentation"] for m in ctrl_data]

        print(f"\n  {'Group':<15} {'Mean Dissent':>13} {'Mean Frag':>10}")
        print(f"  {'-'*40}")
        print(f"  {'Controversial':<15} {np.mean(cont_dissent):>12.1%} {np.mean(cont_frag):>10.3f}")
        print(f"  {'Control':<15} {np.mean(ctrl_dissent):>12.1%} {np.mean(ctrl_frag):>10.3f}")

        t_stat, p_value = stats.ttest_ind(cont_dissent, ctrl_dissent)
        print(f"\n  T-test (dissent): t={t_stat:.3f}, p={p_value:.4f}")

        t_stat2, p_value2 = stats.ttest_ind(cont_frag, ctrl_frag)
        print(f"  T-test (fragmentation): t={t_stat2:.3f}, p={p_value2:.4f}")

        all_dissent = cont_dissent + ctrl_dissent
        all_frag = cont_frag + ctrl_frag
        correlation = np.corrcoef(all_dissent, all_frag)[0, 1]
        print(f"\n  Correlation (dissent vs fragmentation): {correlation:.3f}")

        print(f"\n  {'CONCLUSION':}")
        if p_value < 0.05:
            print(f"  Controversial articles have SIGNIFICANTLY higher dissent (p={p_value:.4f})")
        else:
            print(f"  No significant difference in dissent (p={p_value:.4f})")

        if p_value2 < 0.05:
            print(f"  Controversial articles have SIGNIFICANTLY higher fragmentation (p={p_value2:.4f})")
        else:
            print(f"  No significant difference in fragmentation (p={p_value2:.4f})")

        if correlation > 0.5:
            print(f"  Strong positive correlation supports Contrarian Threshold Theory")
        elif correlation > 0.3:
            print(f"  Moderate correlation")
        else:
            print(f"  Weak correlation")

    with open("results/rp001_full_wikipedia_results.json", "w") as f:
        json.dump(articles, f, indent=2)

    print(f"\n  Results: results/rp001_full_wikipedia_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
