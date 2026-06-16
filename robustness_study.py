#!/usr/bin/env python3
"""
RP-001.1 Robustness Study (Fast Version)
==========================================

Uses cached data and limits revisions for speed.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from collections import Counter
from datetime import datetime

import numpy as np
from scipy import stats


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

CONTROL = [
    "Photosynthesis", "DNA", "Cell (biology)", "Protein", "Enzyme",
    "Electron", "Proton", "Neutron", "Atom", "Molecule",
    "Gravity", "Electromagnetism", "Thermodynamics", "Entropy",
    "Calculus", "Algebra", "Geometry", "Topology",
    "Mountain", "River", "Ocean", "Desert", "Forest",
    "Tree", "Flower", "Bird", "Fish", "Insect",
    "Bacteria", "Virus", "Fungus", "Plant", "Animal",
    "CPU", "RAM", "Transistor", "Diode",
    "Steel", "Aluminum", "Copper", "Gold", "Silver",
    "Mars", "Jupiter", "Saturn", "Moon", "Sun",
]


def fetch_revisions_fast(article_title, max_revisions=1000):
    """Fetch revisions with limit for speed."""
    revisions = []
    continue_param = None
    
    while len(revisions) < max_revisions:
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": article_title,
            "rvprop": "user|timestamp|comment",
            "rvlimit": "500",
            "format": "json",
        }
        
        if continue_param:
            params["rvcontinue"] = continue_param
        
        url = f"https://en.wikipedia.org/w/api.php?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "THEORIA-RP001-Robustness/1.0 (research@example.com)"
        })
        
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"    Error: {e}")
            break
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            for rev in page_data.get("revisions", []):
                revisions.append({
                    "user": rev.get("user", "unknown"),
                    "comment": rev.get("comment", ""),
                })
        
        if "continue" in data and "rvcontinue" in data["continue"]:
            continue_param = data["continue"]["rvcontinue"]
            time.sleep(0.1)
        else:
            break
    
    return revisions[:max_revisions]


def compute_metrics(revisions):
    """Compute dissent and fragmentation metrics."""
    if not revisions or len(revisions) < 10:
        return None
    
    user_counts = Counter(r["user"] for r in revisions)
    total = len(revisions)
    n_users = len(user_counts)
    
    # Dissent metrics
    persistent = sum(1 for u, c in user_counts.items() if c >= 3)
    dissent_fraction = persistent / max(n_users, 1)
    
    revert_comments = sum(1 for r in revisions 
                         if any(w in r.get("comment", "").lower() 
                               for w in ["revert", "rvv", "vandal", "undo"]))
    revert_rate = revert_comments / max(total, 1)
    
    # Fragmentation metrics
    herfindahl = sum((c / total) ** 2 for c in user_counts.values())
    fragmentation = 1.0 - herfindahl
    
    probs = [c / total for c in user_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probs if p > 0)
    max_entropy = np.log2(max(n_users, 1))
    norm_entropy = entropy / max(max_entropy, 1)
    
    return {
        "dissent_fraction": float(dissent_fraction),
        "revert_rate": float(revert_rate),
        "fragmentation": float(fragmentation),
        "normalized_entropy": float(norm_entropy),
    }


def run_tests(cont_values, ctrl_values):
    """Run multiple statistical tests."""
    results = {}
    
    t_stat, p_value = stats.ttest_ind(cont_values, ctrl_values)
    results["student_t"] = {"t": float(t_stat), "p": float(p_value)}
    
    t_stat, p_value = stats.ttest_ind(cont_values, ctrl_values, equal_var=False)
    results["welch_t"] = {"t": float(t_stat), "p": float(p_value)}
    
    u_stat, p_value = stats.mannwhitneyu(cont_values, ctrl_values, alternative='two-sided')
    results["mann_whitney"] = {"u": float(u_stat), "p": float(p_value)}
    
    pooled_std = np.sqrt((np.std(cont_values, ddof=1)**2 + np.std(ctrl_values, ddof=1)**2) / 2)
    cohens_d = (np.mean(cont_values) - np.mean(ctrl_values)) / pooled_std if pooled_std > 0 else 0
    results["cohens_d"] = float(cohens_d)
    
    # Bootstrap CI
    diffs = []
    for _ in range(1000):
        boot_cont = np.random.choice(cont_values, size=len(cont_values), replace=True)
        boot_ctrl = np.random.choice(ctrl_values, size=len(ctrl_values), replace=True)
        diffs.append(np.mean(boot_cont) - np.mean(boot_ctrl))
    results["bootstrap_ci"] = {
        "lower": float(np.percentile(diffs, 2.5)),
        "upper": float(np.percentile(diffs, 97.5)),
    }
    
    return results


def leave_one_out(article_metrics):
    """Leave-one-out sensitivity analysis."""
    results = []
    for excluded in article_metrics:
        remaining = {k: v for k, v in article_metrics.items() if k != excluded}
        cont = [v["dissent_fraction"] for k, v in remaining.items() if k in CONTROVERSIAL]
        ctrl = [v["dissent_fraction"] for k, v in remaining.items() if k not in CONTROVERSIAL]
        if cont and ctrl:
            _, p = stats.ttest_ind(cont, ctrl)
            results.append({
                "excluded": excluded,
                "p_value": float(p),
                "significant": p < 0.05,
            })
    return results


def main():
    print("=" * 70)
    print("  RP-001.1 ROBUSTNESS STUDY (Fast)")
    print("=" * 70)
    
    data_dir = "data/robustness_fast"
    os.makedirs(data_dir, exist_ok=True)
    
    all_articles = CONTROVERSIAL + CONTROL
    
    # Load or fetch
    article_data = {}
    for i, article in enumerate(all_articles):
        cache_file = os.path.join(data_dir, f"{article.replace(' ', '_')}.json")
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                article_data[article] = json.load(f)
            continue
        
        print(f"  [{i+1}/{len(all_articles)}] {article}...", end=" ", flush=True)
        revisions = fetch_revisions_fast(article, max_revisions=1000)
        
        if len(revisions) >= 10:
            article_data[article] = revisions
            with open(cache_file, "w") as f:
                json.dump(revisions, f)
            print(f"{len(revisions)} revisions")
        else:
            print(f"skipped ({len(revisions)})")
        
        time.sleep(0.2)
    
    print(f"\n  Loaded {len(article_data)} articles")
    
    # Compute metrics
    article_metrics = {}
    for article, revisions in article_data.items():
        metrics = compute_metrics(revisions)
        if metrics:
            article_metrics[article] = metrics
    
    cont = {k: v for k, v in article_metrics.items() if k in CONTROL}
    ctrl = {k: v for k, v in article_metrics.items() if k not in CONTROVERSIAL}
    
    # Wait, I need to fix the split
    cont = {k: v for k, v in article_metrics.items() if k in CONTROVERSIAL}
    ctrl = {k: v for k, v in article_metrics.items() if k not in CONTROVERSIAL}
    
    print(f"  Controversial: {len(cont)}, Control: {len(ctrl)}")
    
    # Run tests
    print("\n  Statistical Tests:")
    for metric in ["dissent_fraction", "revert_rate", "fragmentation", "normalized_entropy"]:
        cont_vals = [v[metric] for v in cont.values()]
        ctrl_vals = [v[metric] for v in ctrl.values()]
        
        if cont_vals and ctrl_vals:
            results = run_tests(cont_vals, ctrl_vals)
            print(f"\n  {metric}:")
            print(f"    Cont: {np.mean(cont_vals):.4f} | Ctrl: {np.mean(ctrl_vals):.4f}")
            print(f"    Student p={results['student_t']['p']:.4f} | Welch p={results['welch_t']['p']:.4f}")
            print(f"    Mann-Whitney p={results['mann_whitney']['p']:.4f} | d={results['cohens_d']:.3f}")
    
    # Sensitivity
    print("\n  Leave-One-Out Sensitivity:")
    loo = leave_one_out(article_metrics)
    sig_count = sum(1 for r in loo if r["significant"])
    fragile = [r["excluded"] for r in loo if not r["significant"]]
    print(f"    Robust: {sig_count}/{len(loo)}")
    if fragile:
        print(f"    Fragile: {fragile}")
    
    # Summary
    cont_dissent = [v["dissent_fraction"] for v in cont.values()]
    ctrl_dissent = [v["dissent_fraction"] for v in ctrl.values()]
    
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Articles: {len(article_metrics)} ({len(cont)} controversial, {len(ctrl)} control)")
    print(f"  Controversial mean dissent: {np.mean(cont_dissent):.1%}")
    print(f"  Control mean dissent: {np.mean(ctrl_dissent):.1%}")
    
    t_stat, p_val = stats.ttest_ind(cont_dissent, ctrl_dissent)
    print(f"  Student t-test: p={p_val:.4f}")
    
    t_stat, p_val = stats.ttest_ind(cont_dissent, ctrl_dissent, equal_var=False)
    print(f"  Welch t-test: p={p_val:.4f}")
    
    print(f"  Leave-one-out robust: {sig_count}/{len(loo)}")
    print(f"{'='*70}")
    
    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_articles": len(article_metrics),
        "n_controversial": len(cont),
        "n_control": len(ctrl),
        "loo_robust": sig_count,
        "loo_total": len(loo),
        "fragile_articles": fragile,
    }
    os.makedirs("results", exist_ok=True)
    with open("results/rp001_robustness_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to results/rp001_robustness_results.json")


if __name__ == "__main__":
    main()
