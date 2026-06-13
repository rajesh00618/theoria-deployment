"""
DISCOVERY-006: Optimal Noise Principle

Finds the noise level that maximizes:
  Utility = Consensus x Information Flow

Key insight from DISCOVERY-005:
  - Low noise: high consensus, low information flow
  - High noise: low consensus, high information flow
  - Optimal noise: maximum product of both
"""

import numpy as np
import csv
import json
import time
from dataclasses import dataclass
from typing import List, Dict


# ============================================================================
# Simulation Engine
# ============================================================================

class OptimalNoiseSimulation:
    """Measure consensus and information flow at each noise level."""

    def __init__(self, n_agents=200, n_dims=5, noise_level=0.05,
                 copy_strength=0.3, contrarian_frac=0.0, seed=42):
        self.n_agents = n_agents
        self.n_dims = n_dims
        self.noise_level = noise_level
        self.copy_strength = copy_strength
        self.rng = np.random.RandomState(seed)

        # Initialize agents
        self.beliefs = self.rng.uniform(0, 1, (n_agents, n_dims))

        # Information signal (agent 0 holds unique signal)
        self.info_signal = np.ones(n_dims) * 0.5  # Distinct from random
        self.beliefs[0] = self.info_signal.copy()
        self.signal_reached = {0}

        # Ring topology
        self.adjacency = {}
        k = 5
        for i in range(n_agents):
            neighbors = []
            for offset in range(1, k + 1):
                neighbors.append((i + offset) % n_agents)
                neighbors.append((i - offset) % n_agents)
            self.adjacency[i] = list(set(neighbors))

        # Contrarians
        self.contrarian = self.rng.random(n_agents) < contrarian_frac

    def run(self, n_steps=300):
        """Run simulation and return metrics."""
        diversity_history = []
        signal_history = []

        for t in range(n_steps):
            self._step()

            # Track metrics every 10 steps
            if t % 10 == 0:
                alive_beliefs = self.beliefs
                diversity = self._compute_diversity(alive_beliefs)
                signal_pct = len(self.signal_reached) / self.n_agents
                diversity_history.append(diversity)
                signal_history.append(signal_pct)

        # Final metrics
        final_diversity = self._compute_diversity(self.beliefs)
        final_signal = len(self.signal_reached) / self.n_agents

        # Consensus = 1 - normalized diversity
        # Max possible diversity in 5D unit cube ~ sqrt(5) * 0.5
        max_diversity = np.sqrt(self.n_dims) * 0.5
        consensus = max(0, 1 - final_diversity / max_diversity)

        # Information flow = final signal reach
        info_flow = final_signal

        # Utility = Consensus x Information Flow
        utility = consensus * info_flow

        return {
            "consensus": float(consensus),
            "info_flow": float(info_flow),
            "utility": float(utility),
            "final_diversity": float(final_diversity),
            "diversity_history": diversity_history,
            "signal_history": signal_history,
        }

    def _step(self):
        """One simulation step."""
        # Compute success
        success = np.zeros(self.n_agents)
        for i in range(self.n_agents):
            neighbors = [j for j in self.adjacency[i]]
            if not neighbors:
                continue
            mean_neighbor = np.mean([self.beliefs[j] for j in neighbors], axis=0)
            dist = np.linalg.norm(self.beliefs[i] - mean_neighbor)
            success[i] = 1.0 / (1.0 + dist)

        # Update beliefs
        for i in range(self.n_agents):
            neighbors = [j for j in self.adjacency[i] if j != i]
            if not neighbors:
                continue

            # Pick best neighbor
            neighbor_success = [success[j] for j in neighbors]
            best_idx = np.argmax(neighbor_success)
            best = neighbors[best_idx]

            # Social influence
            direction = self.beliefs[best] - self.beliefs[i]
            if self.contrarian[i]:
                direction = -direction

            delta = self.copy_strength * direction * (success[best] - success[i] + 0.5)
            self.beliefs[i] = self.beliefs[i] + delta

            # Noise
            self.beliefs[i] += self.rng.normal(0, self.noise_level, self.n_dims)
            self.beliefs[i] = np.clip(self.beliefs[i], 0.0, 1.0)

        # Track information propagation
        for i in range(self.n_agents):
            if i not in self.signal_reached:
                dist_to_signal = np.linalg.norm(self.beliefs[i] - self.info_signal)
                if dist_to_signal < 0.3:
                    self.signal_reached.add(i)

    def _compute_diversity(self, beliefs):
        """Average pairwise distance (sampled)."""
        n = len(beliefs)
        if n < 2:
            return 0.0
        diffs = []
        for i in range(min(n, 50)):
            for j in range(i + 1, min(i + 20, n)):
                diffs.append(np.linalg.norm(beliefs[i] - beliefs[j]))
        return float(np.mean(diffs)) if diffs else 0.0


# ============================================================================
# Noise Sweep
# ============================================================================

def sweep_noise(n_agents=200, n_dims=5, n_runs=5, n_steps=300):
    """Sweep noise levels and find optimal."""
    noise_levels = np.arange(0.0, 0.52, 0.02)
    results = []

    print(f"  Sweeping {len(noise_levels)} noise levels x {n_runs} runs")
    print(f"  {'Noise':>6s}  {'Consensus':>10s}  {'InfoFlow':>10s}  {'Utility':>10s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}")

    for noise in noise_levels:
        trial_utils = []
        trial_consensus = []
        trial_infoflow = []

        for run in range(n_runs):
            sim = OptimalNoiseSimulation(
                n_agents=n_agents, n_dims=n_dims,
                noise_level=noise, seed=run * 1000 + int(noise * 10000),
            )
            m = sim.run(n_steps)
            trial_utils.append(m["utility"])
            trial_consensus.append(m["consensus"])
            trial_infoflow.append(m["info_flow"])

        avg_utility = float(np.mean(trial_utils))
        avg_consensus = float(np.mean(trial_consensus))
        avg_infoflow = float(np.mean(trial_infoflow))

        results.append({
            "noise": float(noise),
            "consensus": avg_consensus,
            "info_flow": avg_infoflow,
            "utility": avg_utility,
        })

        print(f"  {noise:6.2f}  {avg_consensus:10.4f}  {avg_infoflow:10.4f}  {avg_utility:10.4f}")

    return results


# ============================================================================
# Analysis
# ============================================================================

def find_optimal(results):
    """Find noise* that maximizes utility."""
    utilities = [r["utility"] for r in results]
    noises = [r["noise"] for r in results]

    optimal_idx = np.argmax(utilities)
    noise_star = noises[optimal_idx]
    utility_star = utilities[optimal_idx]

    # Find where utility is within 90% of maximum
    threshold_90 = utility_star * 0.9
    optimal_range = [r["noise"] for r in results if r["utility"] >= threshold_90]
    noise_range = (min(optimal_range), max(optimal_range)) if optimal_range else (noise_star, noise_star)

    print(f"\n  OPTIMAL NOISE PRINCIPLE")
    print(f"  {'='*50}")
    print(f"  Noise*:     {noise_star:.3f}")
    print(f"  Utility*:   {utility_star:.4f}")
    print(f"  Consensus:  {results[optimal_idx]['consensus']:.4f}")
    print(f"  Info Flow:  {results[optimal_idx]['info_flow']:.4f}")
    print(f"  Optimal range (90%): [{noise_range[0]:.3f}, {noise_range[1]:.3f}]")

    # Three regimes
    print(f"\n  THREE REGIMES")
    print(f"  {'='*50}")

    # Low noise regime
    low_noise = [r for r in results if r["noise"] < noise_star * 0.5]
    if low_noise:
        avg_low = np.mean([r["utility"] for r in low_noise])
        print(f"  Regime 1 (noise < {noise_star*0.5:.2f}): STAGNATION")
        print(f"    Utility: {avg_low:.4f} (low - consensus high but no information flow)")

    # Optimal regime
    print(f"  Regime 2 (noise ~ {noise_star:.2f}): OPTIMAL")
    print(f"    Utility: {utility_star:.4f} (maximum - balanced)")

    # High noise regime
    high_noise = [r for r in results if r["noise"] > noise_star * 2]
    if high_noise:
        avg_high = np.mean([r["utility"] for r in high_noise])
        print(f"  Regime 3 (noise > {noise_star*2:.2f}): CHAOS")
        print(f"    Utility: {avg_high:.4f} (low - information flows but no consensus)")

    # The principle
    print(f"\n  THE OPTIMAL NOISE PRINCIPLE")
    print(f"  {'='*50}")
    print(f"")
    print(f"  Too little noise -> stagnation (consensus but no innovation)")
    print(f"  Too much noise   -> chaos (innovation but no consensus)")
    print(f"  Optimal noise    -> maximum utility (balanced)")
    print(f"")
    print(f"  This is analogous to:")
    print(f"    - Exploration vs exploitation in reinforcement learning")
    print(f"    - Temperature in simulated annealing")
    print(f"    - Mutation rate in genetic algorithms")
    print(f"    - Diversity vs cohesion in team management")
    print(f"")

    return {
        "noise_star": float(noise_star),
        "utility_star": float(utility_star),
        "optimal_range": (float(noise_range[0]), float(noise_range[1])),
        "consensus_at_optimal": float(results[optimal_idx]["consensus"]),
        "info_flow_at_optimal": float(results[optimal_idx]["info_flow"]),
    }


# ============================================================================
# Visualization (text-based)
# ============================================================================

def plot_utility_curve(results, optimal):
    """Text-based plot of utility curve."""
    print(f"\n  UTILITY CURVE")
    print(f"  {'='*50}")

    max_utility = max(r["utility"] for r in results)
    width = 40

    for r in results:
        bar_len = int(r["utility"] / max_utility * width) if max_utility > 0 else 0
        bar = "#" * bar_len
        marker = " <-- OPTIMAL" if abs(r["noise"] - optimal["noise_star"]) < 0.02 else ""
        print(f"  {r['noise']:5.2f} |{bar:<{width}s}| {r['utility']:.3f}{marker}")

    print(f"  {'':5s} +{'-'*width}+")
    print(f"  {'':5s}  0{' '*(width//2-2)}Utility{' '*(width//2-4)}Max")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  DISCOVERY-006: Optimal Noise Principle")
    print("  Find noise* that maximizes Consensus x Information Flow")
    print("=" * 70)

    t0 = time.time()

    # Sweep
    results = sweep_noise(n_agents=200, n_dims=5, n_runs=5, n_steps=300)

    # Find optimal
    optimal = find_optimal(results)

    # Plot
    plot_utility_curve(results, optimal)

    # Save
    with open("optimal_noise_results.json", "w") as f:
        json.dump({"sweep": results, "optimal": optimal}, f, indent=2)
    print("\n  Saved optimal_noise_results.json")

    with open("optimal_noise_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["noise", "consensus", "info_flow", "utility"])
        writer.writeheader()
        writer.writerows(results)
    print("  Saved optimal_noise_results.csv")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")

    print("\n" + "=" * 70)
    print("  DISCOVERY-006 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
