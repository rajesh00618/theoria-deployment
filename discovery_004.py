"""
DISCOVERY-004: Real-World Validation Framework

Tests whether the belief emergence threshold appears in realistic
social network models that mimic Reddit, Wikipedia, and citation networks.

Since we cannot access live APIs, we generate synthetic networks with
real-world statistical properties and test the model predictions.
"""

import numpy as np
import csv
import time
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import Counter


# ============================================================================
# Realistic Network Generators
# ============================================================================

def generate_reddit_like(n=1000, rng=None):
    """
    Reddit-like network:
    - Power-law degree (some users highly connected)
    - Community structure (subreddits)
    - Core-periphery (mods/power users vs lurkers)
    """
    if rng is None:
        rng = np.random.RandomState(42)

    # Power-law degree distribution
    degrees = rng.pareto(1.5, n) + 1
    degrees = np.clip(degrees, 1, n // 5).astype(int)

    adj = {i: set() for i in range(n)}

    # Community structure: 10 communities
    n_communities = max(3, n // 50)
    community_size = n // n_communities
    community_of = [min(i // community_size, n_communities - 1) for i in range(n)]

    # Intra-community connections (dense)
    for i in range(n):
        n_edges = min(degrees[i], n - 1)
        # Prefer same community
        same_comm = [j for j in range(n) if j != i and community_of[j] == community_of[i]]
        diff_comm = [j for j in range(n) if j != i and community_of[j] != community_of[i]]

        n_same = min(int(n_edges * 0.8), len(same_comm))
        n_diff = min(n_edges - n_same, len(diff_comm))

        if same_comm:
            chosen_same = rng.choice(same_comm, size=min(n_same, len(same_comm)), replace=False)
            for j in chosen_same:
                adj[i].add(j)
                adj[j].add(i)

        if diff_comm:
            chosen_diff = rng.choice(diff_comm, size=min(n_diff, len(diff_comm)), replace=False)
            for j in chosen_diff:
                adj[i].add(j)
                adj[j].add(i)

    return {i: list(v) for i, v in adj.items()}


def generate_wikipedia_like(n=1000, rng=None):
    """
    Wikipedia-like network:
    - Editor network (who edits which articles)
    - Articles have topics
    - Editors specialize in topics
    - Some editors are generalists
    """
    if rng is None:
        rng = np.random.RandomState(42)

    adj = {i: set() for i in range(n)}

    # 20 topic clusters
    n_topics = max(3, n // 50)
    topic_of = rng.randint(0, n_topics, n)

    # Editors connect when they edit same topic
    topic_members = {}
    for i in range(n):
        t = topic_of[i]
        if t not in topic_members:
            topic_members[t] = []
        topic_members[t].append(i)

    # Each editor connects to a few others in same topic
    for i in range(n):
        t = topic_of[i]
        members = topic_members[t]
        if len(members) > 1:
            n_conn = min(rng.randint(2, 8), len(members) - 1)
            others = [m for m in members if m != i]
            chosen = rng.choice(others, size=min(n_conn, len(others)), replace=False)
            for j in chosen:
                adj[i].add(j)
                adj[j].add(i)

    # Some cross-topic connections (generalist editors)
    for i in range(n):
        if rng.random() < 0.1:  # 10% are generalists
            other_topics = [t for t in range(n_topics) if t != topic_of[i]]
            if other_topics:
                t2 = rng.choice(other_topics)
                if topic_members.get(t2):
                    j = rng.choice(topic_members[t2])
                    adj[i].add(j)
                    adj[j].add(i)

    return {i: list(v) for i, v in adj.items()}


def generate_citation_like(n=1000, rng=None):
    """
    Citation network:
    - Papers cite papers
    - Directed edges (we treat as undirected for opinion dynamics)
    - Preferential attachment (popular papers get more citations)
    - Temporal ordering (newer papers cite older)
    """
    if rng is None:
        rng = np.random.RandomState(42)

    adj = {i: set() for i in range(n)}

    # Preferential attachment
    for i in range(n):
        if i == 0:
            continue
        # Attach to existing nodes with probability proportional to degree
        degrees = np.array([len(adj[j]) + 1 for j in range(i)])
        probs = degrees / degrees.sum()
        n_citations = min(rng.randint(1, 5), i)
        cited = rng.choice(i, size=n_citations, replace=False, p=probs)
        for j in cited:
            adj[i].add(j)
            adj[j].add(i)

    return {i: list(v) for i, v in adj.items()}


def generate_twitter_like(n=1000, rng=None):
    """
    Twitter-like network:
    - Follow graph (directed, we use undirected)
    - Some viral users (high degree)
    - Most users have few connections
    - Retweet dynamics
    """
    if rng is None:
        rng = np.random.RandomState(42)

    adj = {i: set() for i in range(n)}

    # Small number of "viral" users
    n_viral = max(5, n // 100)
    viral_users = rng.choice(n, n_viral, replace=False)

    # Everyone follows a few viral users
    for i in range(n):
        n_follow = rng.randint(1, min(n_viral + 1, 10))
        followed = rng.choice(viral_users, size=min(n_follow, n_viral), replace=False)
        for j in followed:
            if i != j:
                adj[i].add(j)
                adj[j].add(i)

    # Some peer connections
    for i in range(n):
        if rng.random() < 0.3:
            j = rng.randint(0, n)
            while j == i:
                j = rng.randint(0, n)
            adj[i].add(j)
            adj[j].add(i)

    return {i: list(v) for i, v in adj.items()}


# ============================================================================
# Realistic Opinion Dynamics
# ============================================================================

@dataclass
class SocialAgent:
    id: int
    belief: float = 0.5  # single-dimensional belief [0, 1]
    activity: float = 0.5  # how active (0=lurker, 1=power user)
    openness: float = 0.5  # how receptive to new ideas
    influence: float = 0.5  # how much others listen
    community: int = 0
    alive: bool = True
    contrarian: bool = False


class SocialDynamics:
    """
    Realistic social opinion dynamics.

    Features:
    - Heterogeneous agents (lurkers, posters, power users)
    - Community structure
    - Exposure to external information
    - Trust/reputation dynamics
    """

    def __init__(self, n=1000, network_type="reddit", noise_level=0.05,
                 contrarian_frac=0.0, seed=42):
        self.n = n
        self.noise_level = noise_level
        self.rng = np.random.RandomState(seed)

        # Generate network
        if network_type == "reddit":
            self.adjacency = generate_reddit_like(n, self.rng)
        elif network_type == "wikipedia":
            self.adjacency = generate_wikipedia_like(n, self.rng)
        elif network_type == "citation":
            self.adjacency = generate_citation_like(n, self.rng)
        elif network_type == "twitter":
            self.adjacency = generate_twitter_like(n, self.rng)
        else:
            self.adjacency = generate_reddit_like(n, self.rng)

        # Assign communities based on network clusters
        self.communities = self._detect_communities()

        # Create agents
        self.agents = []
        for i in range(n):
            is_contrad = self.rng.random() < contrarian_frac
            self.agents.append(SocialAgent(
                id=i,
                belief=self.rng.uniform(0, 1),
                activity=max(0.1, self.rng.beta(2, 5)),  # most are low activity
                openness=max(0.1, min(1.0, self.rng.normal(0.5, 0.2))),
                influence=max(0.01, self.rng.pareto(2) * 0.1),
                community=self.communities.get(i, 0),
                contrarian=is_contrad,
            ))

    def _detect_communities(self):
        """Simple community detection via BFS."""
        communities = {}
        visited = set()
        comm_id = 0

        for start in range(self.n):
            if start in visited:
                continue
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node in visited:
                    continue
                visited.add(node)
                communities[node] = comm_id
                for neighbor in self.adjacency.get(node, []):
                    if neighbor not in visited:
                        queue.append(neighbor)
            comm_id += 1
            if comm_id > 20:  # Cap at 20 communities
                break

        return communities

    def run(self, n_steps=300):
        history = []
        for t in range(n_steps):
            self._step()
            metrics = self._metrics()
            metrics["step"] = t
            history.append(metrics)
        return history

    def _step(self):
        # Shuffle order to avoid bias
        order = self.rng.permutation(self.n)

        for i in order:
            agent = self.agents[i]
            if not agent.alive:
                continue

            neighbors = [self.agents[j] for j in self.adjacency.get(i, [])
                         if self.agents[j].alive]

            if not neighbors:
                continue

            # Weighted social influence
            weights = []
            for n_agent in neighbors:
                # Weight by activity * influence * trust
                w = n_agent.activity * n_agent.influence
                if agent.community == n_agent.community:
                    w *= 1.5  # In-group bonus
                weights.append(w)

            weights = np.array(weights)
            if weights.sum() > 0:
                weights /= weights.sum()

            # Compute weighted neighbor belief
            neighbor_beliefs = np.array([n.belief for n in neighbors])
            weighted_mean = np.dot(weights, neighbor_beliefs)

            # Agent updates toward weighted mean (or away if contrarian)
            if agent.contrarian:
                direction = agent.belief - weighted_mean
            else:
                direction = weighted_mean - agent.belief

            # Update strength depends on agent openness and neighbor influence
            strength = agent.openness * 0.3
            agent.belief += direction * strength

            # Add noise (scaled by agent activity)
            agent.belief += self.rng.normal(0, self.noise_level * agent.activity)
            agent.belief = np.clip(agent.belief, 0.0, 1.0)

            # Update influence based on belief alignment with neighbors
            if neighbor_beliefs.size > 0:
                alignment = 1.0 - abs(agent.belief - weighted_mean)
                agent.influence = 0.5 * agent.influence + 0.5 * alignment

    def _metrics(self):
        alive = [a for a in self.agents if a.alive]
        if not alive:
            return {"diversity": 1.0, "variance": 1.0, "n_alive": 0}

        beliefs = np.array([a.belief for a in alive])
        diversity = float(np.mean([abs(b1 - b2) for i, b1 in enumerate(beliefs)
                                   for b2 in beliefs[i+1:i+20]])) if len(beliefs) > 1 else 0.0
        variance = float(np.var(beliefs))

        return {
            "diversity": diversity,
            "variance": variance,
            "n_alive": len(alive),
            "mean_belief": float(np.mean(beliefs)),
        }


# ============================================================================
# Threshold finder for real-world models
# ============================================================================

def find_realistic_threshold(network_type, n=500, n_runs=3, n_steps=200):
    """Find threshold for a realistic network type."""
    noise_levels = [0.0, 0.02, 0.05, 0.08, 0.12, 0.20, 0.30]
    diversities = []

    for noise in noise_levels:
        trial_divs = []
        for run in range(n_runs):
            dyn = SocialDynamics(n=n, network_type=network_type,
                                 noise_level=noise, seed=run * 1000 + int(noise * 10000))
            history = dyn.run(n_steps)
            final_div = history[-1]["diversity"]
            trial_divs.append(final_div)
        diversities.append(float(np.mean(trial_divs)))

    # Find threshold
    threshold = None
    for i in range(len(noise_levels) - 1):
        if diversities[i] < 0.3 and diversities[i + 1] >= 0.3:
            x1, x2 = noise_levels[i], noise_levels[i + 1]
            y1, y2 = diversities[i], diversities[i + 1]
            threshold = x1 + (0.3 - y1) * (x2 - x1) / (y2 - y1)
            break

    if threshold is None:
        if diversities[0] >= 0.3:
            threshold = 0.0
        else:
            threshold = noise_levels[-1]

    return {
        "network_type": network_type,
        "n_agents": n,
        "threshold": float(threshold),
        "noise_levels": noise_levels,
        "diversities": diversities,
    }


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  DISCOVERY-004: Real-World Validation Framework")
    print("  Testing threshold on realistic social network models")
    print("=" * 70)

    t0 = time.time()
    results = []

    # Test on 4 realistic network types
    for net_type in ["reddit", "wikipedia", "citation", "twitter"]:
        print(f"\n  Testing {net_type}-like network...")
        r = find_realistic_threshold(net_type, n=500, n_runs=3, n_steps=200)
        results.append(r)
        print(f"    Threshold: K = {r['threshold']:.4f}")
        print(f"    Diversities: {[f'{d:.3f}' for d in r['diversities']]}")

    # Compare with model predictions
    print("\n" + "=" * 70)
    print("  COMPARISON: Real-World vs Model Prediction")
    print("=" * 70)

    model_k = 0.075  # From DISCOVERY-003

    for r in results:
        diff = abs(r["threshold"] - model_k)
        ratio = r["threshold"] / model_k if model_k > 0 else float('inf')
        print(f"\n  {r['network_type']:12s}: K = {r['threshold']:.4f} "
              f"(model predicts {model_k:.4f}, ratio = {ratio:.2f}x)")

    # Analysis
    thresholds = [r["threshold"] for r in results]
    mean_k = np.mean(thresholds)
    std_k = np.std(thresholds)

    print(f"\n  Real-world mean K: {mean_k:.4f} ± {std_k:.4f}")
    print(f"  Model prediction:  {model_k:.4f}")
    print(f"  Ratio: {mean_k / model_k:.2f}x" if model_k > 0 else "  Ratio: N/A")

    if abs(mean_k - model_k) / model_k < 0.5:
        print(f"\n  VERDICT: Model predictions are within 50% of real-world thresholds")
        print(f"  The model generalizes to realistic social networks.")
    else:
        print(f"\n  VERDICT: Model predictions differ significantly from real-world thresholds")
        print(f"  The model needs refinement for realistic networks.")

    # Save results
    with open("realworld_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n  Saved realworld_validation_results.json")

    # CSV
    with open("realworld_validation.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["network_type", "n_agents", "threshold"])
        writer.writeheader()
        for r in results:
            writer.writerow({"network_type": r["network_type"],
                             "n_agents": r["n_agents"],
                             "threshold": r["threshold"]})
    print("  Saved realworld_validation.csv")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")

    print("\n" + "=" * 70)
    print("  DISCOVERY-004 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
