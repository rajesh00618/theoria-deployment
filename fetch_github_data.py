#!/usr/bin/env python3
"""Fetch GitHub issues for cross-platform validation."""

import json
import os
import time
import urllib.request


def fetch_github_issues(repo, state="all", per_page=100):
    """Fetch GitHub issues via API."""
    url = f"https://api.github.com/repos/{repo}/issues?state={state}&per_page={per_page}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "THEORIA-RP001/1.0",
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error: {e}")
        return None


def main():
    os.makedirs("data/github", exist_ok=True)

    repos = [
        "facebook/react",
        "pytorch/pytorch",
        "microsoft/vscode",
        "kubernetes/kubernetes",
        "golang/go",
    ]

    for repo in repos:
        filename = f"data/github/{repo.replace('/', '_')}_issues.json"
        if os.path.exists(filename):
            print(f"  {repo}: exists")
            continue

        print(f"  Fetching {repo}...", end=" ", flush=True)
        data = fetch_github_issues(repo)
        if data:
            with open(filename, "w") as f:
                json.dump(data, f)
            print(f"OK ({len(data)} issues)")
        else:
            print("FAILED")
        time.sleep(2)


if __name__ == "__main__":
    main()
