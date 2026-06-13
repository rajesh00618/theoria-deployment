"""
DISCOVERY-003: Generalization Tests

Tests whether the belief emergence threshold survives changes in:
  1. Network topology
  2. Belief space representation
  3. Interaction rules
  4. Population scale

Core question: Does K ≈ 0.19 hold across all variants?
"""

import numpy as np
import csv
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from collections import Counter


# ============================================================================
# Agent Model (generalized)
# ============================================================================

@dataclass
class Agent:
    id: int
    beliefs: np.ndarray
    belief_type: str = "continuous"  # continuous, binary, categorical, logical
    success: float = 0.0
    alive: bool = True
    contrarian: bool = False
    trust: float = 1.0
    reputation: float = 0.5
    noise_level: float = 0.05


# ============================================================================
# Topology builders
# ============================================================================

def build_topology(topo_type, n, k=5, rng=None):
    if rng is None:
        rng = np.random.RandomState(0)

    if topo_type == "ring":
        adj = {}
        for i in range(n):
            neighbors = []
            for offset in range(1, k + 1):
                neighbors.append((i + offset) % n)
                neighbors.append((i - offset) % n)
            adj[i] = list(set(neighbors))
        return adj

    elif topo_type == "small_world":
        adj = {}
        for i in range(n):
            neighbors = []
            for offset in range(1, k + 1):
                neighbors.append((i + offset) % n)
                neighbors.append((i - offset) % n)
            adj[i] = list(set(neighbors))
        rewire_count = int(0.1 * n * k)
        for _ in range(rewire_count):
            i = rng.randint(0, n)
            if adj[i]:
                old = adj[i][rng.randint(0, len(adj[i]))]
                new_candidate = rng.randint(0, n)
                attempts = 0
                while (new_candidate == i or new_candidate in adj[i]) and attempts < 20:
                    new_candidate = rng.randint(0, n)
                    attempts += 1
                if attempts < 20:
                    adj[i].remove(old)
                    adj[i].append(new_candidate)
        return adj

    elif topo_type == "random":
        adj = {}
        p = min(2 * k / n, 1.0)
        for i in range(n):
            adj[i] = []
            for j in range(n):
                if i != j and rng.random() < p:
                    adj[i].append(j)
        return adj

    elif topo_type == "scale_free":
        adj = {i: [] for i in range(n)}
        for i in range(n):
            targets = list(range(n))
            targets.remove(i)
            weights = np.array([max(len(adj[j]), 1) for j in targets], dtype=float)
            weights /= weights.sum()
            n_edges = min(k, len(targets))
            if n_edges > 0:
                chosen = rng.choice(targets, size=n_edges, replace=False, p=weights)
                for c in chosen:
                    if i not in adj[c]:
                        adj[c].append(i)
                    if c not in adj[i]:
                        adj[i].append(c)
        return adj

    elif topo_type == "hierarchical":
        adj = {i: [] for i in range(n)}
        # Three levels: local (k), mid (k/2), long (k/4)
        for i in range(n):
            for offset in range(1, min(k, n // 2) + 1):
                j = (i + offset) % n
                if j not in adj[i]:
                    adj[i].append(j)
                j2 = (i - offset) % n
                if j2 not in adj[i]:
                    adj[i].append(j2)
            # Add some long-range connections
            for _ in range(max(1, k // 4)):
                j = rng.randint(0, n)
                if j != i and j not in adj[i]:
                    adj[i].append(j)
        return adj

    elif topo_type == "community":
        adj = {i: [] for i in range(n)}
        n_communities = max(2, n // 20)  # 20 agents per community
        community_size = n // n_communities
        for i in range(n):
            comm = i // community_size
            # Connect within community
            for j in range(comm * community_size, min((comm + 1) * community_size, n)):
                if j != i and abs(i - j) <= k:
                    if j not in adj[i]:
                        adj[i].append(j)
            # Sparse inter-community links
            for _ in range(max(1, k // 4)):
                j = rng.randint(0, n)
                if j != i and j not in adj[i]:
                    adj[i].append(j)
        return adj

    else:
        return build_topology("ring", n, k, rng)


# ============================================================================
# Simulation Engine (generalized)
# ============================================================================

class GeneralSimulation:
    def __init__(self, n_agents=100, n_dims=5, belief_type="continuous",
                 noise_level=0.05, copy_strength=0.3, contrarian_frac=0.0,
                 topology="ring", interaction_rule="copy_success",
                 seed=42):
        self.n_agents = n_agents
        self.n_dims = n_dims
        self.belief_type = belief_type
        self.noise_level = noise_level
        self.copy_strength = copy_strength
        self.interaction_rule = interaction_rule
        self.rng = np.random.RandomState(seed)

        self.agents = []
        for i in range(n_agents):
            is_contrad = self.rng.random() < contrarian_frac
            beliefs = self._init_beliefs()
            self.agents.append(Agent(
                id=i,
                beliefs=beliefs,
                belief_type=belief_type,
                noise_level=noise_level,
                contrarian=is_contrad,
                trust=1.0,
                reputation=0.5,
            ))

        self.adjacency = build_topology(topology, n_agents, 5, self.rng)

    def _init_beliefs(self):
        if self.belief_type == "continuous":
            return self.rng.uniform(0, 1, self.n_dims)
        elif self.belief_type == "binary":
            return (self.rng.random(self.n_dims) > 0.5).astype(float)
        elif self.belief_type == "categorical":
            # 5 dimensions, each with 5 categories
            return self.rng.randint(0, 5, self.n_dims).astype(float)
        elif self.belief_type == "logical":
            # 5 boolean propositions
            return (self.rng.random(self.n_dims) > 0.5).astype(float)
        else:
            return self.rng.uniform(0, 1, self.n_dims)

    def run(self, n_steps=300):
        for _ in range(n_steps):
            self._step()
        return self._metrics()

    def _step(self):
        # Compute success
        for a in self.agents:
            if a.alive:
                a.success = self._compute_success(a)

        # Update beliefs
        for a in self.agents:
            if not a.alive:
                continue

            neighbors = [self.agents[j] for j in self.adjacency[a.id]
                         if self.agents[j].alive and self.agents[j].id != a.id]
            if not neighbors:
                continue

            if self.interaction_rule == "copy_success":
                self._rule_copy_success(a, neighbors)
            elif self.interaction_rule == "majority_voting":
                self._rule_majority(a, neighbors)
            elif self.interaction_rule == "bayesian":
                self._rule_bayesian(a, neighbors)
            elif self.interaction_rule == "trust_based":
                self._rule_trust(a, neighbors)
            else:
                self._rule_copy_success(a, neighbors)

            # Add noise
            if self.belief_type == "continuous":
                a.beliefs = a.beliefs + self.rng.normal(0, a.noise_level, self.n_dims)
                a.beliefs = np.clip(a.beliefs, 0.0, 1.0)
            elif self.belief_type == "binary":
                flip_mask = self.rng.random(self.n_dims) < a.noise_level
                a.beliefs[flip_mask] = 1.0 - a.beliefs[flip_mask]
            elif self.belief_type == "categorical":
                for d in range(self.n_dims):
                    if self.rng.random() < a.noise_level:
                        a.beliefs[d] = self.rng.randint(0, 5)
            elif self.belief_type == "logical":
                flip_mask = self.rng.random(self.n_dims) < a.noise_level
                a.beliefs[flip_mask] = 1.0 - a.beliefs[flip_mask]

    def _compute_success(self, agent):
        neighbors = [self.agents[j] for j in self.adjacency[agent.id]
                     if self.agents[j].alive]
        if not neighbors:
            return 0.0
        mean_neighbor = np.mean([n.beliefs for n in neighbors], axis=0)
        dist = np.linalg.norm(agent.beliefs - mean_neighbor)
        return 1.0 / (1.0 + dist)

    def _rule_copy_success(self, agent, neighbors):
        best = max(neighbors, key=lambda x: x.success)
        direction = best.beliefs - agent.beliefs
        if agent.contrarian:
            direction = -direction
        delta = self.copy_strength * direction * (best.success - agent.success + 0.5)
        agent.beliefs = agent.beliefs + delta
        if self.belief_type in ("binary", "logical"):
            agent.beliefs = (agent.beliefs > 0.5).astype(float)
        elif self.belief_type == "categorical":
            agent.beliefs = np.round(np.clip(agent.beliefs, 0, 4))
        else:
            agent.beliefs = np.clip(agent.beliefs, 0.0, 1.0)

    def _rule_majority(self, agent, neighbors):
        if agent.contrarian:
            # Take minority opinion
            for d in range(self.n_dims):
                vals = [n.beliefs[d] for n in neighbors]
                majority = Counter(vals).most_common(1)[0][0]
                agent.beliefs[d] = 1.0 - majority if self.belief_type in ("binary", "logical") else 0.0
        else:
            for d in range(self.n_dims):
                vals = [n.beliefs[d] for n in neighbors]
                agent.beliefs[d] = Counter(vals).most_common(1)[0][0]

    def _rule_bayesian(self, agent, neighbors):
        for d in range(self.n_dims):
            prior = agent.beliefs[d]
            likelihoods = []
            for n in neighbors:
                if self.belief_type in ("binary", "logical"):
                    likelihood = 0.9 if n.beliefs[d] == prior else 0.1
                else:
                    likelihood = max(0.01, 1.0 - abs(n.beliefs[d] - prior))
                likelihoods.append(likelihood)
            posterior = prior * np.prod(likelihoods)
            normalizer = posterior + (1 - prior) * np.prod([1 - l for l in likelihoods])
            if normalizer > 0:
                agent.beliefs[d] = posterior / normalizer

    def _rule_trust(self, agent, neighbors):
        trusted = [n for n in neighbors if n.trust > 0.3]
        if not trusted:
            trusted = neighbors
        best = max(trusted, key=lambda x: x.success * x.trust)
        direction = best.beliefs - agent.beliefs
        if agent.contrarian:
            direction = -direction
        weight = best.trust * (best.success - agent.success + 0.5)
        delta = self.copy_strength * direction * weight
        agent.beliefs = agent.beliefs + delta
        if self.belief_type in ("binary", "logical"):
            agent.beliefs = (agent.beliefs > 0.5).astype(float)
        elif self.belief_type == "categorical":
            agent.beliefs = np.round(np.clip(agent.beliefs, 0, 4))
        else:
            agent.beliefs = np.clip(agent.beliefs, 0.0, 1.0)

    def _metrics(self):
        alive = [a for a in self.agents if a.alive]
        if not alive:
            return {"diversity": 1.0, "clusters": self.n_agents,
                    "largest_frac": 1.0 / self.n_agents, "variance": 1.0}
        beliefs = np.array([a.beliefs for a in alive])

        if self.belief_type == "continuous":
            quantized = np.round(beliefs / 0.2) * 0.2
        else:
            quantized = beliefs.copy()

        clusters = len(set(map(tuple, quantized)))
        cluster_sizes = Counter(map(tuple, quantized))
        largest = max(cluster_sizes.values()) / len(alive)

        diffs = []
        for i in range(len(beliefs)):
            sample = range(i + 1, min(i + 20, len(beliefs)))
            for j in sample:
                diffs.append(np.linalg.norm(beliefs[i] - beliefs[j]))
        diversity = float(np.mean(diffs)) if diffs else 0.0
        variance = float(np.mean(np.var(beliefs, axis=0)))

        return {
            "diversity": diversity,
            "clusters": clusters,
            "largest_frac": float(largest),
            "variance": variance,
        }


# ============================================================================
# Threshold finder
# ============================================================================

def find_threshold(n_agents, belief_type, topology, interaction_rule,
                   n_runs=5, n_steps=300):
    """Find the critical noise threshold for a given configuration."""
    noise_levels = [0.0, 0.05, 0.10, 0.20]
    diversities = []

    for noise in noise_levels:
        trial_divs = []
        for run in range(n_runs):
            sim = GeneralSimulation(
                n_agents=n_agents, belief_type=belief_type,
                noise_level=noise, topology=topology,
                interaction_rule=interaction_rule,
                seed=run * 1000 + int(noise * 10000),
            )
            m = sim.run(n_steps)
            trial_divs.append(m["diversity"])
        diversities.append(float(np.mean(trial_divs)))

    # Find where diversity crosses 0.4 (the emergence threshold)
    threshold_noise = None
    for i in range(len(noise_levels) - 1):
        if diversities[i] < 0.4 and diversities[i + 1] >= 0.4:
            # Linear interpolation
            x1, x2 = noise_levels[i], noise_levels[i + 1]
            y1, y2 = diversities[i], diversities[i + 1]
            threshold_noise = x1 + (0.4 - y1) * (x2 - x1) / (y2 - y1)
            break

    if threshold_noise is None:
        if diversities[0] >= 0.4:
            threshold_noise = 0.0  # No convergence even at zero noise
        else:
            threshold_noise = noise_levels[-1]  # Always converges

    return {
        "n_agents": n_agents,
        "belief_type": belief_type,
        "topology": topology,
        "interaction_rule": interaction_rule,
        "threshold_noise": float(threshold_noise),
        "diversities": diversities,
        "noise_levels": noise_levels,
    }


# ============================================================================
# Main sweeps
# ============================================================================

def sweep_topologies(n_agents=50, n_runs=2):
    """Test all topologies."""
    print("\n  [Sweep A] Topology robustness")
    topologies = ["ring", "small_world", "random", "scale_free", "hierarchical", "community"]
    results = []
    for topo in topologies:
        r = find_threshold(n_agents=n_agents, belief_type="continuous",
                           topology=topo, interaction_rule="copy_success",
                           n_runs=n_runs)
        results.append(r)
        print(f"    {topo:15s}: K = {r['threshold_noise']:.4f}")
    return results


def sweep_belief_types(n_agents=50, n_runs=2):
    """Test all belief space representations."""
    print("\n  [Sweep B] Belief space robustness")
    types = ["continuous", "binary", "categorical", "logical"]
    results = []
    for bt in types:
        r = find_threshold(n_agents=n_agents, belief_type=bt,
                           topology="ring", interaction_rule="copy_success",
                           n_runs=n_runs)
        results.append(r)
        print(f"    {bt:15s}: K = {r['threshold_noise']:.4f}")
    return results


def sweep_interaction_rules(n_agents=50, n_runs=2):
    """Test all interaction rules."""
    print("\n  [Sweep C] Interaction rule robustness")
    rules = ["copy_success", "majority_voting", "bayesian", "trust_based"]
    results = []
    for rule in rules:
        r = find_threshold(n_agents=n_agents, belief_type="continuous",
                           topology="ring", interaction_rule=rule,
                           n_runs=n_runs)
        results.append(r)
        print(f"    {rule:15s}: K = {r['threshold_noise']:.4f}")
    return results


def sweep_scales(n_runs=2):
    """Test at large population sizes."""
    print("\n  [Sweep D] Scale robustness")
    sizes = [50, 100, 200]
    results = []
    for size in sizes:
        r = find_threshold(n_agents=size, belief_type="continuous",
                           topology="small_world", interaction_rule="copy_success",
                           n_runs=n_runs)
        results.append(r)
        print(f"    N={size:5d}: K = {r['threshold_noise']:.4f}")
    return results


def sweep_combined(n_agents=50, n_runs=2):
    """Test worst-case combinations."""
    print("\n  [Sweep E] Worst-case combinations")
    configs = [
        ("community", "binary", "majority_voting"),
        ("scale_free", "logical", "trust_based"),
        ("hierarchical", "categorical", "bayesian"),
        ("random", "binary", "copy_success"),
    ]
    results = []
    for topo, bt, rule in configs:
        r = find_threshold(n_agents=n_agents, belief_type=bt,
                           topology=topo, interaction_rule=rule,
                           n_runs=n_runs)
        results.append(r)
        print(f"    {topo}/{bt}/{rule}: K = {r['threshold_noise']:.4f}")
    return results


# ============================================================================
# Analysis
# ============================================================================

def analyze_stability(all_results):
    """Analyze whether K is stable across all variants."""
    print("\n" + "=" * 70)
    print("  STABILITY ANALYSIS")
    print("=" * 70)

    thresholds = []
    for category, results in all_results.items():
        for r in results:
            thresholds.append(r["threshold_noise"])

    thresholds = np.array(thresholds)
    mean_k = np.mean(thresholds)
    std_k = np.std(thresholds)
    cv = std_k / mean_k if mean_k > 0 else float('inf')

    print(f"\n  Total configurations tested: {len(thresholds)}")
    print(f"  K values: {thresholds}")
    print(f"  Mean K:   {mean_k:.4f}")
    print(f"  Std K:    {std_k:.4f}")
    print(f"  CV:       {cv:.4f}")
    print(f"  Range:    [{thresholds.min():.4f}, {thresholds.max():.4f}]")

    print(f"\n  Per-category analysis:")
    for category, results in all_results.items():
        cat_thresholds = [r["threshold_noise"] for r in results]
        cat_mean = np.mean(cat_thresholds)
        cat_std = np.std(cat_thresholds)
        print(f"    {category:20s}: K = {cat_mean:.4f} ± {cat_std:.4f}")

    # Stability verdict
    if cv < 0.3:
        stability = "STABLE"
        print(f"\n  VERDICT: K is STABLE across all variants (CV = {cv:.3f} < 0.3)")
        print(f"  The emergence threshold is robust to changes in assumptions.")
    elif cv < 0.5:
        stability = "MODERATELY_STABLE"
        print(f"\n  VERDICT: K is MODERATELY STABLE (CV = {cv:.3f})")
        print(f"  The threshold varies but stays within a factor of 2.")
    else:
        stability = "UNSTABLE"
        print(f"\n  VERDICT: K is UNSTABLE (CV = {cv:.3f} > 0.5)")
        print(f"  The threshold depends heavily on assumptions.")

    return {
        "mean_k": float(mean_k),
        "std_k": float(std_k),
        "cv": float(cv),
        "stability": stability,
        "thresholds": thresholds.tolist(),
    }


# ============================================================================
# CSV writer
# ============================================================================

def write_results_csv(filename, all_results):
    rows = []
    for category, results in all_results.items():
        for r in results:
            row = {
                "category": category,
                "n_agents": r["n_agents"],
                "belief_type": r["belief_type"],
                "topology": r["topology"],
                "interaction_rule": r["interaction_rule"],
                "threshold_k": r["threshold_noise"],
            }
            rows.append(row)
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {filename} ({len(rows)} rows)")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  DISCOVERY-003: Generalization Tests")
    print("  Does the emergence threshold survive changes in assumptions?")
    print("=" * 70)

    t0 = time.time()
    all_results = {}

    # Sweep A: Topologies
    all_results["topology"] = sweep_topologies(n_agents=50, n_runs=2)

    # Sweep B: Belief types
    all_results["belief_type"] = sweep_belief_types(n_agents=50, n_runs=2)

    # Sweep C: Interaction rules
    all_results["interaction_rule"] = sweep_interaction_rules(n_agents=50, n_runs=2)

    # Sweep D: Scales
    all_results["scale"] = sweep_scales(n_runs=2)

    # Sweep E: Worst-case combinations
    all_results["combined"] = sweep_combined(n_agents=50, n_runs=2)

    # Analysis
    stability = analyze_stability(all_results)

    # Save
    write_results_csv("generalization_results.csv", all_results)

    with open("generalization_stability.json", "w") as f:
        json.dump(stability, f, indent=2)
    print("  Saved generalization_stability.json")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")

    print("\n" + "=" * 70)
    print("  DISCOVERY-003 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
