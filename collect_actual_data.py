#!/usr/bin/env python3
"""
Data Collection Scripts for RP-001 Actual Data Validation

This script shows how to collect real data from Reddit, Wikipedia, and GitHub.
Run this AFTER setting up API credentials.
"""

import os
import json
import time
from typing import List, Dict


# ============================================================================
# Reddit Data Collection (requires PRAW)
# ============================================================================

def collect_reddit_data(subreddits: List[str], output_path: str,
                        client_id: str, client_secret: str, user_agent: str):
    """
    Collect Reddit comment data for contrarian analysis.

    Setup:
    1. pip install praw
    2. Create Reddit app at https://www.reddit.com/prefs/apps
    3. Set client_id, client_secret, user_agent below
    """
    try:
        import praw
    except ImportError:
        print("  Install PRAW: pip install praw")
        return

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    data = []
    for sub_name in subreddits:
        print(f"  Collecting r/{sub_name}...")
        subreddit = reddit.subreddit(sub_name)

        for post in subreddit.hot(limit=100):
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                data.append({
                    "subreddit": sub_name,
                    "author": str(comment.author),
                    "created_utc": comment.created_utc,
                    "score": comment.score,
                    "num_comments": len(comment.replies),
                    "post_id": post.id,
                })

        time.sleep(1)  # Rate limiting

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {len(data)} comments to {output_path}")


# ============================================================================
# Wikipedia Data Collection
# ============================================================================

def collect_wikipedia_data(pages: List[str], output_path: str):
    """
    Collect Wikipedia revision data.

    Setup:
    1. pip install requests
    2. No API key needed (public API)
    """
    import requests

    data = []
    for page in pages:
        print(f"  Collecting {page}...")
        url = f"https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": page,
            "prop": "revisions",
            "rvprop": "user|timestamp|size|comment",
            "rvlimit": "500",
            "format": "json",
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            pages_data = result.get("query", {}).get("pages", {})
            for page_id, page_data in pages_data.items():
                revisions = page_data.get("revisions", [])
                for rev in revisions:
                    data.append({
                        "page_title": page,
                        "user": rev.get("user", "unknown"),
                        "timestamp": rev.get("timestamp", ""),
                        "size": rev.get("size", 0),
                        "comment": rev.get("comment", ""),
                    })

        time.sleep(0.5)  # Rate limiting

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {len(data)} revisions to {output_path}")


# ============================================================================
# GitHub Data Collection
# ============================================================================

def collect_github_data(repos: List[str], output_path: str,
                        token: str = None):
    """
    Collect GitHub event data.

    Setup:
    1. pip install requests
    2. Optional: Set GitHub token for higher rate limits
    """
    import requests

    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    data = []
    for repo in repos:
        print(f"  Collecting {repo}...")
        url = f"https://api.github.com/repos/{repo}/events"
        params = {"per_page": 100}

        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            events = response.json()
            for event in events:
                data.append({
                    "repo": repo,
                    "author": event.get("actor", {}).get("login", "unknown"),
                    "timestamp": event.get("created_at", ""),
                    "event_type": event.get("type", "unknown"),
                })

        time.sleep(1)  # Rate limiting

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Saved {len(data)} events to {output_path}")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  Data Collection for RP-001 Actual Data Validation")
    print("=" * 70)

    os.makedirs("data", exist_ok=True)

    print("\n[1] Reddit Data Collection")
    print("    Requires: pip install praw")
    print("    Requires: Reddit API credentials")
    print("    Example subreddits: technology, science, politics, gaming")

    print("\n[2] Wikipedia Data Collection")
    print("    Requires: pip install requests")
    print("    No API key needed")
    print("    Example pages: [list of controversial articles]")

    print("\n[3] GitHub Data Collection")
    print("    Requires: pip install requests")
    print("    Optional: GitHub token for higher rate limits")
    print("    Example repos: [list of active open source projects]")

    print("\nTo run collection:")
    print("  1. Set up API credentials")
    print("  2. Edit the lists below")
    print("  3. Run: python collect_actual_data.py")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
