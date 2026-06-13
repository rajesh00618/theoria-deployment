"""
DISCOVERY-002: Belief Emergence Law Discovery

Systematic parameter sweeps to find the mathematical law governing
collective belief emergence in multi-agent systems.

Sweeps:
  1. Noise threshold mapping
  2. Contrarian threshold mapping
  3. Network topology mapping
  4. Agent scale mapping

Then curve-fit all data to discover an emergence equation.
"""

import numpy as np
import csv
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from collections import Counter
from scipy.optimize import curve_fit
from scipy.stats import pearsonr


# ============================================================================
# Simulation Engine (reuse from EXP-001)
# ============================================================================

@dataclass
class Agent:
    id: int
    beliefs: np.ndarray
    success: float = 0.0
    alive: bool = True
    contrarian: bool = False
    noise_level: float = 0.05


class BeliefSimulation:
    def __init__(self, n_agents=100, n_dims=5, k_neighbors=5,
                 noise_level=0.05, copy_strength=0.3, contrarian_frac=0.0,
                 topology="ring", seed=42):
        self.n_agents = n_agents
        self.n_dims = n_dims
        self.noise_level = noise_level
        self.copy_strength = copy_strength
        self.rng = np.random.RandomState(seed)

        self.agents = []
        for i in range(n_agents):
            is_contrad = self.rng.random() < contrarian_frac
            self.agents.append(Agent(
                id=i,
                beliefs=self.rng.uniform(0, 1, n_dims),
                noise_level=noise_level,
                contrarian=is_contrad,
            ))

        self.adjacency = self._build_topology(topology, k_neighbors)

    def _build_topology(self, topology, k):
        n = self.n_agents
        if topology == "ring":
            adj = {}
            for i in range(n):
                neighbors = []
                for offset in range(1, k + 1):
                    neighbors.append((i + offset) % n)
                    neighbors.append((i - offset) % n)
                adj[i] = list(set(neighbors))
            return adj

        elif topology == "small_world":
            adj = {}
            for i in range(n):
                neighbors = []
                for offset in range(1, k + 1):
                    neighbors.append((i + offset) % n)
                    neighbors.append((i - offset) % n)
                adj[i] = list(set(neighbors))
            # Rewire 10% of edges
            rewire_count = int(0.1 * n * k)
            for _ in range(rewire_count):
                i = self.rng.randint(0, n)
                if adj[i]:
                    old = adj[i][self.rng.randint(0, len(adj[i]))]
                    new = self.rng.randint(0, n)
                    while new == i or new in adj[i]:
                        new = self.rng.randint(0, n)
                    adj[i].remove(old)
                    adj[i].append(new)
            return adj

        elif topology == "random":
            adj = {}
            p = min(2 * k / n, 1.0)
            for i in range(n):
                adj[i] = []
                for j in range(n):
                    if i != j and self.rng.random() < p:
                        adj[i].append(j)
            return adj

        elif topology == "scale_free":
            adj = {i: [] for i in range(n)}
            for i in range(n):
                targets = list(range(n))
                targets.remove(i)
                weights = np.array([max(len(adj[j]), 1) for j in targets], dtype=float)
                weights /= weights.sum()
                chosen = self.rng.choice(targets, size=min(k, len(targets)),
                                         replace=False, p=weights)
                for c in chosen:
                    if i not in adj[c]:
                        adj[c].append(i)
                    if c not in adj[i]:
                        adj[i].append(c)
            return adj

        elif topology == "fully_connected":
            adj = {i: [j for j in range(n) if j != i] for i in range(n)}
            return adj

        else:
            return self._build_topology("ring", k)

    def run(self, n_steps=500) -> Dict[str, float]:
        for t in range(n_steps):
            self._step()
        return self._metrics()

    def _step(self):
        for a in self.agents:
            if a.alive:
                a.success = self._compute_success(a)

        for a in self.agents:
            if not a.alive:
                continue
            neighbors = [self.agents[j] for j in self.adjacency[a.id]
                         if self.agents[j].alive and self.agents[j].id != a.id]
            if neighbors:
                best = max(neighbors, key=lambda x: x.success)
                direction = best.beliefs - a.beliefs
                if a.contrarian:
                    direction = -direction
                delta = self.copy_strength * direction * (best.success - a.success + 0.5)
                a.beliefs = a.beliefs + delta

            a.beliefs = a.beliefs + self.rng.normal(0, a.noise_level, self.n_dims)
            a.beliefs = np.clip(a.beliefs, 0.0, 1.0)

    def _compute_success(self, agent):
        neighbors = [self.agents[j] for j in self.adjacency[agent.id]
                     if self.agents[j].alive]
        if not neighbors:
            return 0.0
        mean_neighbor = np.mean([n.beliefs for n in neighbors], axis=0)
        dist = np.linalg.norm(agent.beliefs - mean_neighbor)
        return 1.0 / (1.0 + dist)

    def _metrics(self):
        alive = [a for a in self.agents if a.alive]
        if not alive:
            return {"diversity": 0, "clusters": 0, "largest_frac": 0,
                    "convergence_speed": 0, "variance": 0}
        beliefs = np.array([a.beliefs for a in alive])
        quantized = np.round(beliefs / 0.2) * 0.2
        clusters = len(set(map(tuple, quantized)))
        cluster_sizes = Counter(map(tuple, quantized))
        largest = max(cluster_sizes.values()) / len(alive)

        diffs = []
        for i in range(len(beliefs)):
            for j in range(i + 1, min(i + 20, len(beliefs))):
                diffs.append(np.linalg.norm(beliefs[i] - beliefs[j]))
        diversity = np.mean(diffs) if diffs else 0.0
        variance = float(np.mean(np.var(beliefs, axis=0)))

        return {
            "diversity": float(diversity),
            "clusters": clusters,
            "largest_frac": float(largest),
            "variance": variance,
        }


# ============================================================================
# Parameter Sweeps
# ============================================================================

def sweep_noise(n_runs=100, n_steps=500) -> List[Dict]:
    """Sweep noise level from 0.00 to 0.50."""
    print("  [Sweep 1] Noise level mapping")
    noise_values = np.arange(0.00, 0.52, 0.1)
    results = []

    for noise in noise_values:
        trial_diversities = []
        trial_clusters = []
        trial_largest = []
        trial_variance = []

        for run in range(n_runs):
            sim = BeliefSimulation(n_agents=100, noise_level=noise,
                                   seed=run * 100 + int(noise * 1000))
            m = sim.run(n_steps)
            trial_diversities.append(m["diversity"])
            trial_clusters.append(m["clusters"])
            trial_largest.append(m["largest_frac"])
            trial_variance.append(m["variance"])

        row = {
            "noise": float(noise),
            "diversity_mean": float(np.mean(trial_diversities)),
            "diversity_std": float(np.std(trial_diversities)),
            "clusters_mean": float(np.mean(trial_clusters)),
            "clusters_std": float(np.std(trial_clusters)),
            "largest_mean": float(np.mean(trial_largest)),
            "largest_std": float(np.std(trial_largest)),
            "variance_mean": float(np.mean(trial_variance)),
        }
        results.append(row)

    print(f"    Completed {len(noise_values)} noise levels x {n_runs} runs")
    return results


def sweep_contrarians(n_runs=100, n_steps=500) -> List[Dict]:
    """Sweep contrarian fraction from 0% to 50%."""
    print("  [Sweep 2] Contrarian fraction mapping")
    fractions = np.arange(0.0, 0.55, 0.1)
    results = []

    for frac in fractions:
        trial_diversities = []
        trial_clusters = []
        trial_largest = []
        trial_variance = []

        for run in range(n_runs):
            sim = BeliefSimulation(n_agents=100, contrarian_frac=frac,
                                   seed=run * 100 + int(frac * 10000))
            m = sim.run(n_steps)
            trial_diversities.append(m["diversity"])
            trial_clusters.append(m["clusters"])
            trial_largest.append(m["largest_frac"])
            trial_variance.append(m["variance"])

        row = {
            "contrarian_frac": float(frac),
            "diversity_mean": float(np.mean(trial_diversities)),
            "diversity_std": float(np.std(trial_diversities)),
            "clusters_mean": float(np.mean(trial_clusters)),
            "largest_mean": float(np.mean(trial_largest)),
            "variance_mean": float(np.mean(trial_variance)),
        }
        results.append(row)

    print(f"    Completed {len(fractions)} contrarian levels x {n_runs} runs")
    return results


def sweep_topology(n_runs=50, n_steps=500) -> List[Dict]:
    """Sweep network topologies."""
    print("  [Sweep 3] Network topology mapping")
    topologies = ["ring", "small_world", "random", "scale_free", "fully_connected"]
    results = []

    for topo in topologies:
        trial_diversities = []
        trial_clusters = []
        trial_largest = []
        trial_variance = []

        for run in range(n_runs):
            sim = BeliefSimulation(n_agents=100, topology=topo,
                                   seed=run * 100 + hash(topo) % 10000)
            m = sim.run(n_steps)
            trial_diversities.append(m["diversity"])
            trial_clusters.append(m["clusters"])
            trial_largest.append(m["largest_frac"])
            trial_variance.append(m["variance"])

        row = {
            "topology": topo,
            "diversity_mean": float(np.mean(trial_diversities)),
            "diversity_std": float(np.std(trial_diversities)),
            "clusters_mean": float(np.mean(trial_clusters)),
            "largest_mean": float(np.mean(trial_largest)),
            "variance_mean": float(np.mean(trial_variance)),
            "connectivity": _avg_connectivity(topo, 100),
        }
        results.append(row)

    print(f"    Completed {len(topologies)} topologies x {n_runs} runs")
    return results


def _avg_connectivity(topo, n):
    sim = BeliefSimulation(n_agents=n, topology=topo, seed=0)
    adj = sim.adjacency
    return float(np.mean([len(v) for v in adj.values()]))


def sweep_scale(n_runs=50, n_steps=500) -> List[Dict]:
    """Sweep population size."""
    print("  [Sweep 4] Agent scale mapping")
    sizes = [50, 100, 200, 500]
    results = []

    for size in sizes:
        trial_diversities = []
        trial_clusters = []
        trial_largest = []
        trial_variance = []

        for run in range(n_runs):
            sim = BeliefSimulation(n_agents=size, seed=run * 100 + size)
            m = sim.run(n_steps)
            trial_diversities.append(m["diversity"])
            trial_clusters.append(m["clusters"])
            trial_largest.append(m["largest_frac"])
            trial_variance.append(m["variance"])

        row = {
            "n_agents": size,
            "diversity_mean": float(np.mean(trial_diversities)),
            "diversity_std": float(np.std(trial_diversities)),
            "clusters_mean": float(np.mean(trial_clusters)),
            "largest_mean": float(np.mean(trial_largest)),
            "variance_mean": float(np.mean(trial_variance)),
        }
        results.append(row)

    print(f"    Completed {len(sizes)} population sizes x {n_runs} runs")
    return results


# ============================================================================
# Law Discovery — Curve Fitting
# ============================================================================

def discover_law(noise_data, contrarian_data, topology_data, scale_data):
    """Fit mathematical relationships across all sweep data."""
    print("\n" + "=" * 60)
    print("  LAW DISCOVERY")
    print("=" * 60)

    # --- Noise relationship ---
    # Hypothesis: diversity ~ base / (1 + k * exp(-noise * scale))
    noise_vals = np.array([r["noise"] for r in noise_data])
    div_vals = np.array([r["diversity_mean"] for r in noise_data])
    var_vals = np.array([r["variance_mean"] for r in noise_data])

    # Fit: diversity = a + b * noise^c
    def noise_model(x, a, b, c):
        return a + b * np.power(x + 0.001, c)

    try:
        popt_noise, _ = curve_fit(noise_model, noise_vals, div_vals,
                                  p0=[0.2, 0.5, 0.5], maxfev=5000)
        r_noise = pearsonr(div_vals, noise_model(noise_vals, *popt_noise))[0]
        print(f"\n  Noise-Diversity: diversity = {popt_noise[0]:.3f} + "
              f"{popt_noise[1]:.3f} * noise^{popt_noise[2]:.3f}")
        print(f"    R² = {r_noise**2:.4f}")
    except Exception:
        popt_noise = None
        r_noise = 0
        print("  Noise-Diversity: fit failed")

    # --- Contrarian relationship ---
    contra_vals = np.array([r["contrarian_frac"] for r in contrarian_data])
    contra_div = np.array([r["diversity_mean"] for r in contrarian_data])

    def contra_model(x, a, b, c):
        return a + b * np.power(x + 0.001, c)

    try:
        popt_contra, _ = curve_fit(contra_model, contra_vals, contra_div,
                                   p0=[0.2, 0.8, 0.5], maxfev=5000)
        r_contra = pearsonr(contra_div, contra_model(contra_vals, *popt_contra))[0]
        print(f"\n  Contrarian-Diversity: diversity = {popt_contra[0]:.3f} + "
              f"{popt_contra[1]:.3f} * contrarian^{popt_contra[2]:.3f}")
        print(f"    R² = {r_contra**2:.4f}")
    except Exception:
        popt_contra = None
        r_contra = 0
        print("  Contrarian-Diversity: fit failed")

    # --- Topology relationship ---
    topo_conn = np.array([r["connectivity"] for r in topology_data])
    topo_div = np.array([r["diversity_mean"] for r in topology_data])
    topo_var = np.array([r["variance_mean"] for r in topology_data])

    if len(topo_conn) > 2:
        try:
            def conn_model(x, a, b):
                return a * np.exp(-b * x) + 0.15
            popt_conn, _ = curve_fit(conn_model, topo_conn, topo_div,
                                     p0=[0.5, 0.01], maxfev=5000)
            r_conn = pearsonr(topo_div, conn_model(topo_conn, *popt_conn))[0]
            print(f"\n  Connectivity-Diversity: diversity = {popt_conn[0]:.3f} * "
                  f"exp(-{popt_conn[1]:.4f} * connectivity) + 0.15")
            print(f"    R² = {r_conn**2:.4f}")
        except Exception:
            popt_conn = None
            r_conn = 0
    else:
        popt_conn = None
        r_conn = 0

    # --- Scale relationship ---
    scale_n = np.array([r["n_agents"] for r in scale_data], dtype=float)
    scale_div = np.array([r["diversity_mean"] for r in scale_data])

    try:
        def scale_model(x, a, b, c):
            return a + b / np.power(x, c)
        popt_scale, _ = curve_fit(scale_model, scale_n, scale_div,
                                  p0=[0.2, 2.0, 0.3], maxfev=5000)
        r_scale = pearsonr(scale_div, scale_model(scale_n, *popt_scale))[0]
        print(f"\n  Scale-Diversity: diversity = {popt_scale[0]:.3f} + "
              f"{popt_scale[1]:.3f} / N^{popt_scale[2]:.3f}")
        print(f"    R² = {r_scale**2:.4f}")
    except Exception:
        popt_scale = None
        r_scale = 0

    # --- Unified Law ---
    print("\n" + "-" * 60)
    print("  UNIFIED BELIEF EMERGENCE LAW")
    print("-" * 60)

    # Build combined dataset for multivariate fit
    # Each row: (noise, contrarian_frac, connectivity, n_agents) -> diversity
    X_all = []
    Y_all = []

    for r in noise_data:
        X_all.append([r["noise"], 0.0, 10.0, 100])  # ring k=5 -> ~10 neighbors
        Y_all.append(r["diversity_mean"])

    for r in contrarian_data:
        X_all.append([0.05, r["contrarian_frac"], 10.0, 100])
        Y_all.append(r["diversity_mean"])

    for r in topology_data:
        X_all.append([0.05, 0.0, r["connectivity"], 100])
        Y_all.append(r["diversity_mean"])

    for r in scale_data:
        X_all.append([0.05, 0.0, 10.0, r["n_agents"]])
        Y_all.append(r["diversity_mean"])

    X_all = np.array(X_all)
    Y_all = np.array(Y_all)

    def unified_law(X, alpha, beta, gamma, delta, epsilon):
        noise, contra, conn, N = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
        influence = alpha * conn / (conn + beta)
        resistance = gamma * noise + delta * np.power(contra + 0.001, 1.5)
        scale_factor = 1.0 + epsilon / np.sqrt(N + 1)
        return (influence / (resistance + 0.01)) * scale_factor * 0.1 + 0.15

    try:
        popt_unified, pcov = curve_fit(unified_law, X_all, Y_all,
                                       p0=[1.0, 5.0, 2.0, 1.0, 0.5],
                                       maxfev=10000)
        Y_pred = unified_law(X_all, *popt_unified)
        r_unified = pearsonr(Y_all, Y_pred)[0]

        alpha, beta, gamma, delta, epsilon = popt_unified
        print(f"\n  Belief Diversity = f(noise, contrarians, connectivity, N)")
        print(f"    alpha   = {alpha:.4f}  (influence strength)")
        print(f"    beta    = {beta:.4f}  (connectivity half-saturation)")
        print(f"    gamma   = {gamma:.4f}  (noise resistance)")
        print(f"    delta   = {delta:.4f}  (contrarian resistance)")
        print(f"    epsilon = {epsilon:.4f}  (scale correction)")
        print(f"\n  R² = {r_unified**2:.4f}")

        print(f"\n  Equation:")
        print(f"    diversity = (alpha * conn / (conn + beta)) / (gamma * noise + delta * contra^1.5)")
        print(f"              * (1 + epsilon / sqrt(N)) * 0.1 + 0.15")
        print(f"\n  Critical threshold (emergence occurs when diversity < 0.4):")
        print(f"    Solve for noise_c: noise_c = (influence / (0.4 - 0.15) * scale - delta * contra^1.5) / gamma")

        law_params = {
            "alpha": float(alpha),
            "beta": float(beta),
            "gamma": float(gamma),
            "delta": float(delta),
            "epsilon": float(epsilon),
            "r_squared": float(r_unified**2),
        }
    except Exception as e:
        print(f"  Unified fit failed: {e}")
        law_params = {}

    return {
        "noise_fit": {"params": popt_noise.tolist() if popt_noise is not None else None,
                      "r_squared": float(r_noise**2) if r_noise else 0},
        "contrarian_fit": {"params": popt_contra.tolist() if popt_contra is not None else None,
                           "r_squared": float(r_contra**2) if r_contra else 0},
        "connectivity_fit": {"params": popt_conn.tolist() if popt_conn is not None else None,
                             "r_squared": float(r_conn**2) if r_conn else 0},
        "scale_fit": {"params": popt_scale.tolist() if popt_scale is not None else None,
                      "r_squared": float(r_scale**2) if r_scale else 0},
        "unified_law": law_params,
    }


# ============================================================================
# CSV Writers
# ============================================================================

def write_csv(filename, rows, fieldnames):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {filename} ({len(rows)} rows)")


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  DISCOVERY-002: Belief Emergence Law Discovery")
    print("  Parameter sweeps + mathematical law fitting")
    print("=" * 70)

    t0 = time.time()

    # --- Sweep 1: Noise ---
    noise_data = sweep_noise(n_runs=10, n_steps=200)
    write_csv("noise_results.csv", noise_data,
              ["noise", "diversity_mean", "diversity_std", "clusters_mean",
               "clusters_std", "largest_mean", "largest_std", "variance_mean"])

    # --- Sweep 2: Contrarians ---
    contrarian_data = sweep_contrarians(n_runs=10, n_steps=200)
    write_csv("contrarian_results.csv", contrarian_data,
              ["contrarian_frac", "diversity_mean", "diversity_std",
               "clusters_mean", "largest_mean", "variance_mean"])

    # --- Sweep 3: Topology ---
    topology_data = sweep_topology(n_runs=10, n_steps=200)
    write_csv("topology_results.csv", topology_data,
              ["topology", "diversity_mean", "diversity_std", "clusters_mean",
               "largest_mean", "variance_mean", "connectivity"])

    # --- Sweep 4: Scale ---
    scale_data = sweep_scale(n_runs=10, n_steps=200)
    write_csv("scale_results.csv", scale_data,
              ["n_agents", "diversity_mean", "diversity_std", "clusters_mean",
               "largest_mean", "variance_mean"])

    # --- Law Discovery ---
    law_results = discover_law(noise_data, contrarian_data, topology_data, scale_data)

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")

    # Save law results
    with open("belief_emergence_law.json", "w") as f:
        json.dump(law_results, f, indent=2)
    print("  Saved belief_emergence_law.json")

    print("\n" + "=" * 70)
    print("  DISCOVERY-002 COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
