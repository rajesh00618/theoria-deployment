#!/usr/bin/env python3
"""Fetch and save all Wikipedia data for RP-001-AD analysis."""

import os
import json
import time

DATA_DIR = "data/wikipedia"

CONTROVERSIAL = [
    "Climate_change", "Evolution", "Vaccination",
    "Nuclear_power", "Gun_control", "Abortion",
]

CONTROL = ["Banana", "Water", "Dog", "Gravity"]


def fetch_wikipedia(title):
    """Fetch Wikipedia revision data via API."""
    import urllib.request
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=revisions&rvprop=user%7Ctimestamp&rvlimit=500&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "THEORIA-RP001/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  Error fetching {title}: {e}")
        return None


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    all_articles = CONTROVERSIAL + CONTROL

    for title in all_articles:
        filename = f"{DATA_DIR}/{title.lower()}.json"
        if os.path.exists(filename):
            print(f"  {title}: already exists")
            continue

        print(f"  Fetching {title}...", end=" ", flush=True)
        data = fetch_wikipedia(title)
        if data:
            with open(filename, "w") as f:
                json.dump(data, f)
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                n_revs = len(pdata.get("revisions", []))
                print(f"OK ({n_revs} revisions)")
        else:
            print("FAILED")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
