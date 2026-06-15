#!/usr/bin/env python3
"""
RP-001 Cross-Platform Validation
Analyzes GitHub issues/PRs for dissent-fragmentation patterns.
"""

import json
import os
import sys
from collections import Counter
from datetime import datetime

import numpy as np
from scipy import stats


def analyze_github_issues(issues_data):
    """Analyze GitHub issues for dissent patterns."""
    if not issues_data:
        return None

    # Count contributors
    authors = Counter()
    comment_counts = []
    for issue in issues_data:
        author = issue.get("user", {}).get("login", "unknown")
        authors[author] += 1
        comment_counts.append(issue.get("comments", 0))

    n_issues = len(issues_data)
    n_authors = len(authors)

    # Dissent metric: authors with multiple contributions
    dissenters = {a: c for a, c in authors.items() if c >= 3}
    dissent_fraction = len(dissenters) / max(n_authors, 1)

    # Fragmentation metric: comment distribution
    if comment_counts:
        total_comments = sum(comment_counts)
        if total_comments > 0:
            comment_shares = [c / total_comments for c in comment_counts]
            herfindahl = sum(s ** 2 for s in comment_shares)
            fragmentation = 1.0 - herfindahl
        else:
            fragmentation = 0.0
    else:
        fragmentation = 0.0

    return {
        "n_issues": n_issues,
        "n_authors": n_authors,
        "n_dissenters": len(dissenters),
        "dissent_fraction": float(dissent_fraction),
        "fragmentation": float(fragmentation),
        "mean_comments": float(np.mean(comment_counts)) if comment_counts else 0,
    }


def main():
    print("=" * 70)
    print("  RP-001 Cross-Platform Validation")
    print("=" * 70)

    # Analyze GitHub data
    github_repos = {
        "React": "data/github/facebook_react_issues.json",
        "PyTorch": "data/github/pytorch_pytorch_issues.json",
        "VSCode": "data/github/microsoft_vscode_issues.json",
        "Kubernetes": "data/github/kubernetes_kubernetes_issues.json",
        "Go": "data/github/golang_go_issues.json",
    }

    github_results = {}
    for repo_name, data_file in github_repos.items():
        if os.path.exists(data_file):
            with open(data_file) as f:
                data = json.load(f)
            result = analyze_github_issues(data)
            if result:
                github_results[repo_name] = result
                print(f"\n  {repo_name}:")
                print(f"    Issues: {result['n_issues']}")
                print(f"    Authors: {result['n_authors']}")
                print(f"    Dissenters: {result['n_dissenters']} ({result['dissent_fraction']:.1%})")
                print(f"    Fragmentation: {result['fragmentation']:.3f}")

    # Compare with Wikipedia results
    wiki_file = "results/rp001_full_wikipedia_results.json"
    if os.path.exists(wiki_file):
        with open(wiki_file) as f:
            wiki_data = json.load(f)

        print(f"\n  Wikipedia Comparison:")
        controversial = ["Climate change", "Evolution", "Vaccination", "Nuclear power",
                        "Gun control", "Abortion", "Climate change denial",
                        "Evolution as fact and theory", "Nuclear power debate",
                        "Gun violence in the United States", "Abortion in the United States",
                        "Genetically modified food controversies", "COVID-19 misinformation",
                        "Creationism"]

        cont_dissent = [m["dissent_fraction"] for t, m in wiki_data.items() if t in controversial]
        ctrl_dissent = [m["dissent_fraction"] for t, m in wiki_data.items() if t not in controversial]

        if cont_dissent and ctrl_dissent:
            print(f"    Controversial: n={len(cont_dissent)}, mean={np.mean(cont_dissent):.1%}")
            print(f"    Control: n={len(ctrl_dissent)}, mean={np.mean(ctrl_dissent):.1%}")

    # Cross-platform comparison
    print(f"\n  Cross-Platform Summary:")
    all_dissent = [r["dissent_fraction"] for r in github_results.values()]
    if all_dissent:
        print(f"    GitHub mean dissent: {np.mean(all_dissent):.1%}")
    if cont_dissent:
        print(f"    Wikipedia controversial: {np.mean(cont_dissent):.1%}")
    if ctrl_dissent:
        print(f"    Wikipedia control: {np.mean(ctrl_dissent):.1%}")

    # Save results
    results = {
        "github": github_results,
        "wikipedia": {
            "controversial_mean": float(np.mean(cont_dissent)) if cont_dissent else 0,
            "control_mean": float(np.mean(ctrl_dissent)) if ctrl_dissent else 0,
        },
    }
    with open("results/rp001_cross_platform_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Results saved to results/rp001_cross_platform_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
