#!/usr/bin/env python3
"""
RP-001 Validation v2: 30 seeds for speed, then scale up.
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONIOENCODING"] = "utf-8"

import numpy as np
from experiment_001 import BeliefEmergenceSimulation


def run_single(n_agents, n_dims, k, noise, copy_strength, seed):
    sim = BeliefEmergenceSimulation(
        n_agents=n_agents, n_dims=n_dims, k_neighbors=k,
        noise_level=noise, copy_strength=copy_strength, seed=seed,
    )
    history = sim.run(n_steps=200, verbose=False)
    final = history[-1]
    initial = history[0]
    return {
        "initial_diversity": initial["avg_diversity"],
        "final_diversity": final["avg_diversity"],
        "final_largest_frac": final["largest_cluster_frac"],
        "final_belief_variance": final["belief_variance"],
    }


def sweep_noise(n_seeds):
    noise_levels = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30]
    results = {}
    for noise in noise_levels:
        divs = []
        utils = []
        convs = []
        for seed in range(n_seeds):
            r = run_single(100, 5, 5, noise, 0.3, seed)
            divs.append(r["final_diversity"])
            utils.append(r["final_largest_frac"] * (1.0 - r["final_diversity"]))
            convs.append(1 if r["final_diversity"] < 0.5 else 0)
        divs = np.array(divs)
        utils = np.array(utils)
        results[str(noise)] = {
            "noise": noise,
            "diversity_mean": float(np.mean(divs)),
            "diversity_std": float(np.std(divs)),
            "diversity_ci95": float(1.96 * np.std(divs) / np.sqrt(n_seeds)),
            "utility_mean": float(np.mean(utils)),
            "convergence_rate": float(np.mean(convs)),
        }
    return results


def sweep_topology(n_seeds):
    results = {}
    for topo in ["ring", "random"]:
        divs = []
        for seed in range(n_seeds):
            sim = BeliefEmergenceSimulation(n_agents=100, n_dims=5, k_neighbors=5,
                                           noise_level=0.05, copy_strength=0.3, seed=seed)
            if topo == "random":
                rng = np.random.RandomState(seed)
                adj = {i: [] for i in range(100)}
                for i in range(100):
                    targets = rng.choice([j for j in range(100) if j != i], 5, replace=False)
                    for t in targets:
                        adj[i].append(int(t))
                        adj[t].append(i)
                sim.adjacency = {i: list(set(adj[i])) for i in range(100)}
            history = sim.run(n_steps=200, verbose=False)
            divs.append(history[-1]["avg_diversity"])
        results[topo] = {
            "diversity_mean": float(np.mean(divs)),
            "diversity_std": float(np.std(divs)),
            "convergence_rate": float(np.mean([1 if d < 0.5 else 0 for d in divs])),
        }
    return results


def sweep_agents(n_seeds):
    results = {}
    for n in [50, 100]:
        divs = []
        for seed in range(n_seeds):
            r = run_single(n, 5, 5, 0.05, 0.3, seed)
            divs.append(r["final_diversity"])
        results[str(n)] = {
            "n_agents": n,
            "diversity_mean": float(np.mean(divs)),
            "convergence_rate": float(np.mean([1 if d < 0.5 else 0 for d in divs])),
        }
    return results


def sweep_contrarians(n_seeds):
    results = {}
    for frac in [0.0, 0.05, 0.10, 0.15, 0.20]:
        divs = []
        for seed in range(n_seeds):
            sim = BeliefEmergenceSimulation(n_agents=100, n_dims=5, k_neighbors=5,
                                           noise_level=0.05, copy_strength=0.3, seed=seed)
            rng = np.random.RandomState(seed + 999)
            n_c = int(frac * 100)
            ids = rng.choice(100, n_c, replace=False)
            for cid in ids:
                sim.agents[int(cid)].contrarian = True
            history = sim.run(n_steps=200, verbose=False)
            divs.append(history[-1]["avg_diversity"])
        results[str(frac)] = {
            "contrarian_fraction": frac,
            "diversity_mean": float(np.mean(divs)),
            "convergence_rate": float(np.mean([1 if d < 0.5 else 0 for d in divs])),
        }
    return results


def main():
    N_SEEDS = 30
    t0 = time.time()

    print("=" * 70)
    print(f"  RP-001 VALIDATION ({N_SEEDS} seeds)")
    print("=" * 70)

    print("\n[1/4] Noise sweep...", end=" ", flush=True)
    noise = sweep_noise(N_SEEDS)
    print("done")

    print("[2/4] Topology...", end=" ", flush=True)
    topo = sweep_topology(N_SEEDS)
    print("done")

    print("[3/4] Agent count...", end=" ", flush=True)
    agents = sweep_agents(N_SEEDS)
    print("done")

    print("[4/4] Contrarians...", end=" ", flush=True)
    contr = sweep_contrarians(N_SEEDS)
    print("done")

    dt = time.time() - t0

    # Find optimal noise
    best_noise = max(noise.keys(), key=lambda k: noise[k]["utility_mean"])

    report = {
        "seeds": N_SEEDS,
        "time_seconds": round(dt, 1),
        "noise_sweep": noise,
        "topology": topo,
        "agent_count": agents,
        "contrarians": contr,
        "summary": {
            "optimal_noise": float(best_noise),
            "optimal_utility": noise[best_noise]["utility_mean"],
        },
    }

    with open("results/rp001_validation_results.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*70}")
    print(f"  RESULTS ({dt:.0f}s)")
    print(f"{'='*70}")
    print(f"\n  Noise Sweep:")
    print(f"  {'Noise':>8} {'Diversity':>10} {'±CI95':>8} {'Utility':>8} {'Conv%':>8}")
    for k in sorted(noise.keys(), key=float):
        v = noise[k]
        print(f"  {v['noise']:>8.2f} {v['diversity_mean']:>10.3f} {v['diversity_ci95']:>8.3f} "
              f"{v['utility_mean']:>8.3f} {v['convergence_rate']:>7.0%}")

    print(f"\n  Optimal noise: {best_noise} (utility={noise[best_noise]['utility_mean']:.3f})")

    print(f"\n  Topology:")
    for t, v in topo.items():
        print(f"  {t:>10}: div={v['diversity_mean']:.3f}, conv={v['convergence_rate']:.0%}")

    print(f"\n  Agent Count:")
    for c, v in agents.items():
        print(f"  {c:>5}: div={v['diversity_mean']:.3f}, conv={v['convergence_rate']:.0%}")

    print(f"\n  Contrarians:")
    for c, v in contr.items():
        print(f"  {v['contrarian_fraction']:>5.0%}: div={v['diversity_mean']:.3f}, conv={v['convergence_rate']:.0%}")

    print(f"\n  Saved: results/rp001_validation_results.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
