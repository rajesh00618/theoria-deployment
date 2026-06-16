#!/usr/bin/env python3
"""
RP-001 Metric Validation
=========================

Validates what users are actually counted as "persistent dissenters."

The reviewer asked: "Manually inspect a random sample of users counted
as 'persistent dissenters' to determine what fraction are actually
expressing dissent vs. doing maintenance."
"""

import os
import json
import random
from collections import Counter


def analyze_users(revisions, dissent_threshold=3):
    """Analyze what types of users are counted as persistent."""
    user_counts = Counter(r["user"] for r in revisions)
    
    persistent = {u: c for u, c in user_counts.items() if c >= dissent_threshold}
    
    # Classify users
    bots = []
    admins = []
    anonymous = []
    regular = []
    
    for user, count in persistent.items():
        user_lower = user.lower()
        
        # Bot detection
        if any(bot in user_lower for bot in ["bot", "abot", "greenc", "hager", "citation"]):
            bots.append((user, count))
        # Admin patterns
        elif any(admin in user_lower for admin in ["admin", "sysop", "bureaucrat"]):
            admins.append((user, count))
        # Anonymous/IP
        elif user.startswith("IP ") or user.count(".") == 3:
            anonymous.append((user, count))
        else:
            regular.append((user, count))
    
    return {
        "total_persistent": len(persistent),
        "bots": len(bots),
        "admins": len(admins),
        "anonymous": len(anonymous),
        "regular": len(regular),
        "bot_examples": bots[:5],
        "regular_examples": regular[:5],
    }


def main():
    print("=" * 70)
    print("  RP-001 METRIC VALIDATION")
    print("  What users are counted as 'persistent dissenters'?")
    print("=" * 70)
    
    data_dir = "data/robustness_fast"
    
    # Analyze a sample of articles
    articles = ["Climate change", "Abortion", "Dog", "Photosynthesis", "Gravity"]
    
    for article in articles:
        cache_file = os.path.join(data_dir, f"{article.replace(' ', '_')}.json")
        if not os.path.exists(cache_file):
            continue
        
        with open(cache_file) as f:
            revisions = json.load(f)
        
        result = analyze_users(revisions)
        
        print(f"\n  {article}:")
        print(f"    Total persistent (>=3 edits): {result['total_persistent']}")
        print(f"    Bots: {result['bots']} ({result['bots']/max(result['total_persistent'],1)*100:.0f}%)")
        print(f"    Admins: {result['admins']} ({result['admins']/max(result['total_persistent'],1)*100:.0f}%)")
        print(f"    Anonymous: {result['anonymous']} ({result['anonymous']/max(result['total_persistent'],1)*100:.0f}%)")
        print(f"    Regular users: {result['regular']} ({result['regular']/max(result['total_persistent'],1)*100:.0f}%)")
        
        if result['bot_examples']:
            print(f"    Bot examples: {[b[0] for b in result['bot_examples'][:3]]}")
        if result['regular_examples']:
            print(f"    Regular examples: {[r[0] for r in result['regular_examples'][:3]]}")
    
    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
