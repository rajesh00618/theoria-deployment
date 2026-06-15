#!/usr/bin/env python3
"""
RP-001 Reproducibility: Contrarian Threshold Theory

Self-contained script that reproduces the key finding:
contrarian agents above ~10% destroy consensus.

Run: python reproduce_rp001.py
"""

import numpy as np
import json
import time
from typing import List, Dict


class Agent:
    def __init__(self, id, beliefs, noise_level=0.05, contrarian=False):
        self.id = id
        self.beliefs = beliefs.copy()
        self.success = 0.0
        self.alive = True
        self.contrarian = contrarian
        self.noise_level = noise_level


class BeliefEmergenceSimulation:
    def __init__(self, n_agents=100, n_dims=5, k_neighbors=5,
                 noise_level=0.05, copy_strength=0.3, seed=42):
        self.n_agents = n_agents
        self.n_dims = n_dims
        self.k_neighbors = k_neighbors
        self.noise_level = noise_level
        self.copy_strength = copy_strength
        self.rng = np.random.RandomState(seed)
        self.agents = []
        for i in range(n_agents):
            beliefs = self.rng.uniform(0, 1, n_dims)
            self.agents.append(Agent(i, beliefs, noise_level))
        self.adjacency = self._build_ring()

    def _build_ring(self):
        adj = {}
        for i in range(self.n_agents):
            neighbors = []
            for offset in range(1, self.k_neighbors + 1):
                neighbors.append((i + offset) % self.n_agents)
                neighbors.append((i - offset) % self.n_agents)
            adj[i] = list(set(neighbors))
        return adj

    def step(self):
        for agent in self.agents:
            if agent.alive:
                neighbors = self.adjacency[agent.id]
                neighbor_beliefs = np.array([self.agents[j].beliefs for j in neighbors if self.agents[j].alive])
                if len(neighbor_beliefs) > 0:
                    mean_neighbor = neighbor_beliefs.mean(axis=0)
                    distance = np.linalg.norm(agent.beliefs - mean_neighbor)
                    agent.success = 1.0 / (1.0 + distance)

        for agent in self.agents:
            if not agent.alive:
                continue
            neighbors = [self.agents[j] for j in self.adjacency[agent.id]
                         if self.agents[j].alive and self.agents[j].id != agent.id]
            if neighbors:
                role_model = max(neighbors, key=lambda a: a.success)
                direction = role_model.beliefs - agent.beliefs
                if agent.contrarian:
                    direction = -direction
                delta = self.copy_strength * direction * (role_model.success - agent.success + 0.5)
                agent.beliefs = agent.beliefs + delta
            noise = self.rng.normal(0, agent.noise_level, self.n_dims)
            agent.beliefs = agent.beliefs + noise
            agent.beliefs = np.clip(agent.beliefs, 0.0, 1.0)

        alive = [a for a in self.agents if a.alive]
        beliefs = np.array([a.beliefs for a in alive])
        if len(beliefs) > 1:
            diffs = []
            for i in range(len(beliefs)):
                for j in range(i + 1, min(i + 20, len(beliefs))):
                    diffs.append(np.linalg.norm(beliefs[i] - beliefs[j]))
            avg_diversity = np.mean(diffs) if diffs else 0.0
        else:
            avg_diversity = 0.0
        return {"avg_diversity": avg_diversity, "n_alive": len(alive)}

    def run(self, n_steps=200):
        for _ in range(n_steps):
            self.step()
        return self.step()


def run_contrarian_sweep(n_seeds=30, n_agents=100, noise=0.05, steps=200):
    """Sweep contrarian fractions and measure convergence."""
    fractions = [0.0, 0.05, 0.10, 0.15, 0.20]
    results = {}

    for frac in fractions:
        divs = []
        convs = []
        for seed in range(n_seeds):
            sim = BeliefEmergenceSimulation(
                n_agents=n_agents, n_dims=5, k_neighbors=5,
                noise_level=noise, copy_strength=0.3, seed=seed,
            )
            rng = np.random.RandomState(seed + 999)
            n_c = int(frac * n_agents)
            if n_c > 0:
                ids = rng.choice(n_agents, n_c, replace=False)
                for cid in ids:
                    sim.agents[int(cid)].contrarian = True
            final = sim.run(n_steps=steps)
            divs.append(final["avg_diversity"])
            convs.append(1 if final["avg_diversity"] < 0.5 else 0)

        results[str(frac)] = {
            "contrarian_fraction": frac,
            "diversity_mean": float(np.mean(divs)),
            "diversity_std": float(np.std(divs)),
            "convergence_rate": float(np.mean(convs)),
            "n_seeds": n_seeds,
        }

    return results


def main():
    print("=" * 60)
    print("  RP-001: Contrarian Threshold Theory")
    print("  Reproducibility Test")
    print("=" * 60)

    t0 = time.time()
    results = run_contrarian_sweep(n_seeds=30)
    dt = time.time() - t0

    print(f"\n  Time: {dt:.0f}s")
    print(f"\n  {'Contrarian%':>12} {'Diversity':>10} {'±Std':>8} {'Conv%':>8}")
    print(f"  {'-'*42}")
    for k in sorted(results.keys(), key=float):
        v = results[k]
        print(f"  {v['contrarian_fraction']:>11.0%} {v['diversity_mean']:>10.3f} "
              f"{v['diversity_std']:>8.3f} {v['convergence_rate']:>7.0%}")

    threshold_found = False
    for k in sorted(results.keys(), key=float):
        v = results[k]
        if v["convergence_rate"] < 0.5:
            print(f"\n  Critical threshold found at {v['contrarian_fraction']:.0%} contrarians")
            threshold_found = True
            break

    if not threshold_found:
        print("\n  No critical threshold found (all fractions converged)")

    with open("results/rp001_reproduction_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results: results/rp001_reproduction_results.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
