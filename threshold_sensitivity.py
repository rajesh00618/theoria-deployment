#!/usr/bin/env python3
"""
RP-001 Threshold Sensitivity Analysis
=======================================

Tests whether the result holds at different dissent thresholds.

Reviewer asked: "Test thresholds of 2, 4, 5, 10 edits."
"""

import os
import json
from collections import Counter

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


def compute_dissent(revisions, threshold):
    """Compute dissent fraction at given threshold."""
    user_counts = Counter(r["user"] for r in revisions)
    total = len(revisions)
    n_users = len(user_counts)
    
    # Exclude bots
    bot_patterns = ["bot", "abot", "greenc", "hager", "citation"]
    persistent = sum(1 for u, c in user_counts.items() 
                    if c >= threshold and not any(b in u.lower() for b in bot_patterns))
    
    return persistent / max(n_users, 1)


# All articles (same as rp001_final.py)
ALL_CONTROVERSIAL = [
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

ALL_CONTROL = [
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


def main():
    print("=" * 70)
    print("  RP-001 THRESHOLD SENSITIVITY ANALYSIS")
    print("=" * 70)
    
    data_dir = "data/robustness_fast"
    
    # Load all articles
    article_data = {}
    all_articles = ALL_CONTROVERSIAL + ALL_CONTROL
    
    for article in all_articles:
        cache_file = os.path.join(data_dir, f"{article.replace(' ', '_')}.json")
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                article_data[article] = json.load(f)
    
    print(f"\n  Loaded {len(article_data)} articles")
    
    # Test different thresholds
    thresholds = [2, 3, 4, 5, 10]
    
    print(f"\n  {'Threshold':<12} {'Cont Mean':>10} {'Ctrl Mean':>10} {'Diff':>8} {'p-value':>10} {'Sig?':>6}")
    print(f"  {'-'*60}")
    
    for threshold in thresholds:
        cont_values = []
        ctrl_values = []
        
        for article, revisions in article_data.items():
            dissent = compute_dissent(revisions, threshold)
            if article in ALL_CONTROVERSIAL:
                cont_values.append(dissent)
            else:
                ctrl_values.append(dissent)
        
        if cont_values and ctrl_values:
            t_stat, p_value = stats.ttest_ind(cont_values, ctrl_values)
            cont_mean = np.mean(cont_values)
            ctrl_mean = np.mean(ctrl_values)
            diff = cont_mean - ctrl_mean
            sig = "YES" if p_value < 0.05 else "NO"
            
            print(f"  >= {threshold:<8} {cont_mean:>9.1%} {ctrl_mean:>9.1%} {diff:>+7.1%} {p_value:>10.4f} {sig:>6}")
    
    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
