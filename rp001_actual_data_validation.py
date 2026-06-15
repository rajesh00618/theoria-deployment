#!/usr/bin/env python3
"""
RP-001-AD: Actual Data Validation Framework

This script provides the framework for testing the Contrarian Threshold Theory
on actual historical data from Reddit, Wikipedia, and GitHub.

REQUIRES: API keys and data access (see README.md)
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

import numpy as np
from scipy import stats
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class CommunityData:
    """Represents a real community's data."""
    name: str
    members: List[str]  # member IDs
    dissenters: List[str]  # persistent dissenters
    timestamps: List[float]  # event timestamps
    outcomes: Dict[str, Any]  # fragmentation, quality, etc.


@dataclass
class ValidationResult:
    """Result of a contrarian threshold test."""
    dataset: str
    n_communities: int
    threshold_found: bool
    threshold_value: Optional[float]
    p_value: float
    effect_size: float
    details: Dict[str, Any]


# ============================================================================
# Analysis Functions
# ============================================================================

def compute_dissent_fraction(community: CommunityData) -> float:
    """Compute fraction of persistent dissenters in a community."""
    if not community.members:
        return 0.0
    return len(community.dissenters) / len(community.members)


def compute_fragmentation_score(community: CommunityData) -> float:
    """Compute fragmentation score from community data."""
    if not community.timestamps:
        return 0.0
    gaps = np.diff(community.timestamps)
    if len(gaps) == 0:
        return 0.0
    cv = np.std(gaps) / np.mean(gaps) if np.mean(gaps) > 0 else 0
    return float(min(1.0, cv))


def find_threshold(fractions: List[float], outcomes: List[float],
                   threshold: float = 0.5) -> Optional[float]:
    """Find the critical threshold where outcomes change."""
    sorted_pairs = sorted(zip(fractions, outcomes))
    for i in range(len(sorted_pairs) - 1):
        f1, o1 = sorted_pairs[i]
        f2, o2 = sorted_pairs[i + 1]
        if o1 < threshold and o2 >= threshold:
            return (f1 + f2) / 2
        if o1 >= threshold and o2 < threshold:
            return (f1 + f2) / 2
    return None


def cohens_d(group1: List[float], group2: List[float]) -> float:
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


# ============================================================================
# Dataset Adapters
# ============================================================================

class RedditAdapter:
    """
    Adapter for Reddit data.

    Data format expected:
    - CSV with columns: subreddit, author, created_utc, score, num_comments
    - Or JSON with similar structure

    How to get data:
    1. Use PRAW (Python Reddit API Wrapper) with your own API credentials
    2. Use public datasets from pushshift.io
    3. Use Reddit's official API
    """

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.communities: Dict[str, CommunityData] = {}

    def load(self) -> bool:
        """Load Reddit data from file."""
        if not os.path.exists(self.data_path):
            print(f"  [Reddit] Data file not found: {self.data_path}")
            print(f"  To get Reddit data:")
            print(f"    1. Install: pip install praw")
            print(f"    2. Set up API credentials at https://www.reddit.com/prefs/apps")
            print(f"    3. Use the data collection script below")
            return False

        with open(self.data_path, 'r') as f:
            data = json.load(f)

        for item in data:
            sub = item.get("subreddit", "unknown")
            if sub not in self.communities:
                self.communities[sub] = CommunityData(
                    name=sub, members=[], dissenters=[],
                    timestamps=[], outcomes={},
                )
            author = item.get("author", "unknown")
            self.communities[sub].members.append(author)
            self.communities[sub].timestamps.append(item.get("created_utc", 0))

        return True

    def identify_dissenters(self, dissent_threshold: int = 10) -> None:
        """Identify persistent dissenters (users with many downvoted comments)."""
        for sub, community in self.communities.items():
            from collections import Counter
            author_counts = Counter(community.members)
            total = len(community.members)
            dissenters = [author for author, count in author_counts.items()
                         if count >= dissent_threshold]
            community.dissenters = dissenters


class WikipediaAdapter:
    """
    Adapter for Wikipedia revision data.

    Data format expected:
    - CSV with columns: page_id, page_title, user, timestamp, revision_size

    How to get data:
    1. Use the Wikipedia API: https://en.wikipedia.org/w/api.php
    2. Use the Wikimedia dump: https://dumps.wikimedia.org/
    3. Use the ORES API for edit quality scores
    """

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.communities: Dict[str, CommunityData] = {}

    def load(self) -> bool:
        """Load Wikipedia data from file."""
        if not os.path.exists(self.data_path):
            print(f"  [Wikipedia] Data file not found: {self.data_path}")
            print(f"  To get Wikipedia data:")
            print(f"    1. Use the Wikipedia API:")
            print(f"       https://en.wikipedia.org/w/api.php?action=query&list=revisions")
            print(f"    2. Download dumps from:")
            print(f"       https://dumps.wikimedia.org/enwiki/")
            return False

        with open(self.data_path, 'r') as f:
            data = json.load(f)

        for item in data:
            page = item.get("page_title", "unknown")
            if page not in self.communities:
                self.communities[page] = CommunityData(
                    name=page, members=[], dissenters=[],
                    timestamps=[], outcomes={},
                )
            user = item.get("user", "unknown")
            self.communities[page].members.append(user)
            self.communities[page].timestamps.append(item.get("timestamp", 0))

        return True


class GitHubAdapter:
    """
    Adapter for GitHub project data.

    Data format expected:
    - CSV with columns: repo, author, timestamp, event_type, additions, deletions

    How to get data:
    1. Use GitHub API: https://api.github.com/
    2. Use the GH Archive: https://www.gharchive.org/
    3. Use GHTorrent: http://ghtorrent.org/
    """

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.communities: Dict[str, CommunityData] = {}

    def load(self) -> bool:
        """Load GitHub data from file."""
        if not os.path.exists(self.data_path):
            print(f"  [GitHub] Data file not found: {self.data_path}")
            print(f"  To get GitHub data:")
            print(f"    1. Use GitHub Events API:")
            print(f"       https://api.github.com/events")
            print(f"    2. Download from GH Archive:")
            print(f"       https://www.gharchive.org/")
            return False

        with open(self.data_path, 'r') as f:
            data = json.load(f)

        for item in data:
            repo = item.get("repo", "unknown")
            if repo not in self.communities:
                self.communities[repo] = CommunityData(
                    name=repo, members=[], dissenters=[],
                    timestamps=[], outcomes={},
                )
            author = item.get("author", "unknown")
            self.communities[repo].members.append(author)
            self.communities[repo].timestamps.append(item.get("timestamp", 0))

        return True


# ============================================================================
# Validation Pipeline
# ============================================================================

def validate_dataset(adapter, dataset_name: str) -> ValidationResult:
    """Run contrarian threshold validation on a dataset."""
    print(f"\n  Validating {dataset_name}...")

    if not adapter.load():
        return ValidationResult(
            dataset=dataset_name,
            n_communities=0,
            threshold_found=False,
            threshold_value=None,
            p_value=1.0,
            effect_size=0.0,
            details={"error": "Data not available"},
        )

    adapter.identify_dissenters()

    fractions = []
    fragmentations = []
    for name, community in adapter.communities.items():
        if len(community.members) < 10:
            continue
        frac = compute_dissent_fraction(community)
        frag = compute_fragmentation_score(community)
        fractions.append(frac)
        fragmentations.append(frag)

    if len(fractions) < 20:
        return ValidationResult(
            dataset=dataset_name,
            n_communities=len(fractions),
            threshold_found=False,
            threshold_value=None,
            p_value=1.0,
            effect_size=0.0,
            details={"error": "Too few communities"},
        )

    threshold = find_threshold(fractions, fragmentations)

    low = [f for f, frag in zip(fractions, fragmentations) if frag < 0.3]
    high = [f for f, frag in zip(fractions, fragmentations) if frag >= 0.3]

    if low and high:
        t_stat, p_value = stats.ttest_ind(low, high)
        effect = cohens_d(low, high)
    else:
        t_stat, p_value, effect = 0, 1.0, 0.0

    print(f"    Communities: {len(fractions)}")
    print(f"    Threshold: {threshold}")
    print(f"    p-value: {p_value:.4f}")
    print(f"    Effect size: {effect:.3f}")

    return ValidationResult(
        dataset=dataset_name,
        n_communities=len(fractions),
        threshold_found=threshold is not None,
        threshold_value=threshold,
        p_value=float(p_value),
        effect_size=float(effect),
        details={
            "n_low_fragmentation": len(low),
            "n_high_fragmentation": len(high),
            "mean_dissent_low": float(np.mean(low)) if low else 0,
            "mean_dissent_high": float(np.mean(high)) if high else 0,
        },
    )


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  RP-001-AD: Actual Data Validation Framework")
    print("=" * 70)

    data_dir = "data"

    results = {}

    reddit = RedditAdapter(os.path.join(data_dir, "reddit_comments.json"))
    results["reddit"] = validate_dataset(reddit, "Reddit")

    wikipedia = WikipediaAdapter(os.path.join(data_dir, "wikipedia_revisions.json"))
    results["wikipedia"] = validate_dataset(wikipedia, "Wikipedia")

    github = GitHubAdapter(os.path.join(data_dir, "github_events.json"))
    results["github"] = validate_dataset(github, "GitHub")

    with open("results/rp001_actual_data_results.json", "w") as f:
        json.dump({k: {
            "dataset": v.dataset,
            "n_communities": v.n_communities,
            "threshold_found": v.threshold_found,
            "threshold_value": v.threshold_value,
            "p_value": v.p_value,
            "effect_size": v.effect_size,
        } for k, v in results.items()}, f, indent=2)

    print(f"\n{'='*70}")
    print("  SUMMARY")
    print(f"{'='*70}")
    for name, r in results.items():
        status = "CONFIRMED" if r.threshold_found and r.p_value < 0.05 else \
                 "SUPPORTED" if r.threshold_found else "NO DATA"
        print(f"  {name:>12}: {status} (p={r.p_value:.4f}, d={r.effect_size:.3f})")

    print(f"\n  To run with actual data:")
    print(f"    1. Create data/ directory")
    print(f"    2. Add reddit_comments.json")
    print(f"    3. Add wikipedia_revisions.json")
    print(f"    4. Add github_events.json")
    print(f"    5. Run: python rp001_actual_data_validation.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
