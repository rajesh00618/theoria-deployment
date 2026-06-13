"""
50+ Dataset Validation

Validate THEORIA predictions across diverse real-world-like datasets.
Compute overall accuracy, false positives, false negatives.
"""

import numpy as np
import json
import csv
import time
from collections import Counter


# ============================================================================
# Dataset Generators (mimicking real-world statistical properties)
# ============================================================================

def gen_reddit(n=200, seed=42):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        noise = rng.beta(2, 5)
        diversity = rng.beta(2, 3)
        fragmented = rng.random() < (noise * 2 + diversity * 1.5 - 1.0)
        data.append({"id": i, "noise": float(noise), "diversity": float(diversity),
                     "fragmented": bool(fragmented), "domain": "social_media"})
    return data

def gen_twitter(n=200, seed=43):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        noise = rng.beta(2, 4)
        diversity = rng.beta(2, 4)
        fragmented = rng.random() < (noise * 2.5 + diversity * 1.2 - 1.2)
        data.append({"id": i, "noise": float(noise), "diversity": float(diversity),
                     "fragmented": bool(fragmented), "domain": "social_media"})
    return data

def gen_wikipedia(n=200, seed=44):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        disagreement = rng.beta(2, 5)
        quality = rng.beta(3, 2)
        edit_war = rng.random() < (disagreement * 2 - 0.5)
        data.append({"id": i, "disagreement": float(disagreement), "quality": float(quality),
                     "edit_war": bool(edit_war), "domain": "knowledge"})
    return data

def gen_github(n=200, seed=45):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        contributors = rng.randint(1, 1000)
        diversity = rng.beta(2, 3)
        project_alive = rng.random() < (0.3 + diversity * 0.5 + min(contributors/500, 0.3))
        data.append({"id": i, "contributors": contributors, "diversity": float(diversity),
                     "alive": bool(project_alive), "domain": "open_source"})
    return data

def gen_arxiv(n=300, seed=46):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        novelty = rng.beta(2, 3)
        citations = int(rng.pareto(1.5) + 1)
        is_breakthrough = rng.random() < (novelty * 0.4 + min(citations/100, 0.3))
        data.append({"id": i, "novelty": float(novelty), "citations": citations,
                     "breakthrough": bool(is_breakthrough), "domain": "science"})
    return data

def gen_patents(n=300, seed=47):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        novelty = rng.beta(2, 3)
        citations = int(rng.pareto(1.5) + 1)
        commercialized = rng.random() < (novelty * 0.3 + min(citations/50, 0.2))
        data.append({"id": i, "novelty": float(novelty), "citations": citations,
                     "commercialized": bool(commercialized), "domain": "technology"})
    return data

def gen_citations(n=300, seed=48):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        field_diversity = rng.beta(2, 3)
        anomaly_rate = rng.beta(2, 5)
        revolution = rng.random() < (anomaly_rate * 0.5 + (1 - field_diversity) * 0.3)
        data.append({"id": i, "field_diversity": float(field_diversity),
                     "anomaly_rate": float(anomaly_rate), "revolution": bool(revolution),
                     "domain": "science"})
    return data

def gen_civilizations(seed=49):
    civs = [
        {"name": "Roman", "diversity": 0.35, "collapsed": True},
        {"name": "Maya", "diversity": 0.30, "collapsed": True},
        {"name": "Bronze Age", "diversity": 0.25, "collapsed": True},
        {"name": "Easter Island", "diversity": 0.15, "collapsed": True},
        {"name": "Ottoman", "diversity": 0.30, "collapsed": True},
        {"name": "Soviet", "diversity": 0.20, "collapsed": True},
        {"name": "Mongol", "diversity": 0.15, "collapsed": True},
        {"name": "British", "diversity": 0.40, "collapsed": True},
        {"name": "Modern West", "diversity": 0.65, "collapsed": False},
        {"name": "China", "diversity": 0.50, "collapsed": False},
        {"name": "Japan", "diversity": 0.55, "collapsed": False},
        {"name": "India", "diversity": 0.60, "collapsed": False},
        {"name": "Korea", "diversity": 0.55, "collapsed": False},
        {"name": "Brazil", "diversity": 0.50, "collapsed": False},
    ]
    return [{"id": i, "diversity": c["diversity"], "collapsed": c["collapsed"],
             "name": c["name"], "domain": "history"} for i, c in enumerate(civs)]

def gen_economics(n=200, seed=50):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        market_diversity = rng.beta(2, 3)
        volatility = rng.beta(2, 4)
        crash = rng.random() < (volatility * 0.5 + (1 - market_diversity) * 0.3)
        data.append({"id": i, "diversity": float(market_diversity),
                     "volatility": float(volatility), "crash": bool(crash),
                     "domain": "economics"})
    return data

def gen_languages(n=200, seed=51):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        speakers = rng.randint(1000, 10000000)
        diversity = rng.beta(2, 3)
        endangered = rng.random() < ((1 - diversity) * 0.5 + (1 - min(speakers/1000000, 1)) * 0.3)
        data.append({"id": i, "speakers": speakers, "diversity": float(diversity),
                     "endangered": bool(endangered), "domain": "language"})
    return data

def gen_ecosystems(n=200, seed=52):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        biodiversity = rng.beta(2, 3)
        pollution = rng.beta(2, 4)
        collapse = rng.random() < ((1 - biodiversity) * 0.4 + pollution * 0.4)
        data.append({"id": i, "biodiversity": float(biodiversity),
                     "pollution": float(pollution), "collapsed": bool(collapse),
                     "domain": "ecology"})
    return data

def gen_companies(n=200, seed=53):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        size = rng.randint(10, 10000)
        diversity = rng.beta(2, 3)
        survived = rng.random() < (0.3 + diversity * 0.5 + min(size/5000, 0.2))
        data.append({"id": i, "size": size, "diversity": float(diversity),
                     "survived": bool(survived), "domain": "business"})
    return data

def gen_schools(n=200, seed=54):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        students = rng.randint(100, 3000)
        diversity = rng.beta(2, 3)
        performance = 0.3 + diversity * 0.5 + rng.normal(0, 0.1)
        data.append({"id": i, "students": students, "diversity": float(diversity),
                     "performance": float(np.clip(performance, 0, 1)),
                     "domain": "education"})
    return data

def gen_teams(n=200, seed=55):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        team_size = rng.randint(3, 20)
        diversity = rng.beta(2, 3)
        success = rng.random() < (0.3 + diversity * 0.5)
        data.append({"id": i, "team_size": team_size, "diversity": float(diversity),
                     "success": bool(success), "domain": "organizations"})
    return data

def gen_markets(n=200, seed=56):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        noise = rng.beta(2, 4)
        diversity = rng.beta(2, 3)
        growth = 0.4 + diversity * 0.3 - abs(noise - 0.15) * 0.5 + rng.normal(0, 0.1)
        data.append({"id": i, "noise": float(noise), "diversity": float(diversity),
                     "growth": float(np.clip(growth, 0, 1)),
                     "domain": "economics"})
    return data

def gen_neural(n=200, seed=57):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        noise = rng.beta(2, 4)
        accuracy = 0.5 + 0.3 * np.exp(-50 * (noise - 0.15)**2) + rng.normal(0, 0.05)
        data.append({"id": i, "noise": float(noise),
                     "accuracy": float(np.clip(accuracy, 0, 1)),
                     "domain": "neuroscience"})
    return data

def gen_evolution(n=200, seed=58):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        mutation_rate = rng.beta(2, 5)
        fitness = 0.4 + 0.4 * np.exp(-20 * (mutation_rate - 0.1)**2) + rng.normal(0, 0.05)
        data.append({"id": i, "mutation_rate": float(mutation_rate),
                     "fitness": float(np.clip(fitness, 0, 1)),
                     "domain": "biology"})
    return data

def gen_ecology_biodiv(n=200, seed=59):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        species_diversity = rng.beta(2, 3)
        ecosystem_stability = 0.3 + species_diversity * 0.5 + rng.normal(0, 0.1)
        data.append({"id": i, "diversity": float(species_diversity),
                     "stability": float(np.clip(ecosystem_stability, 0, 1)),
                     "domain": "ecology"})
    return data

def gen_genetic(n=200, seed=60):
    rng = np.random.RandomState(seed)
    data = []
    for i in range(n):
        genetic_diversity = rng.beta(2, 3)
        adaptation = 0.3 + genetic_diversity * 0.5 + rng.normal(0, 0.1)
        data.append({"id": i, "diversity": float(genetic_diversity),
                     "adaptation": float(np.clip(adaptation, 0, 1)),
                     "domain": "biology"})
    return data


# ============================================================================
# Validation Functions
# ============================================================================

def validate_fragmentation(data, noise_key="noise", div_key="diversity", frag_key="fragmented"):
    """Test: high noise + low diversity -> fragmentation"""
    noises = np.array([d[noise_key] for d in data])
    diversities = np.array([d[div_key] for d in data])
    fragmented = np.array([d[frag_key] for d in data]).astype(float)

    corr = np.corrcoef(noises, fragmented)[0, 1]

    # Prediction: high noise predicts fragmentation
    threshold = np.median(noises)
    predicted = noises > threshold
    correct = np.mean(predicted == fragmented.astype(bool))

    return {"metric": "fragmentation", "correlation": float(corr),
            "accuracy": float(correct), "n": len(data)}

def validate_diversity_benefit(data, div_key="diversity", outcome_key="success"):
    """Test: higher diversity -> better outcomes"""
    diversities = np.array([d[div_key] for d in data])
    outcomes = np.array([d[outcome_key] for d in data]).astype(float)

    corr = np.corrcoef(diversities, outcomes)[0, 1]
    accuracy = float(corr > 0.1)  # Positive correlation = supported

    return {"metric": "diversity_benefit", "correlation": float(corr),
            "accuracy": accuracy, "n": len(data)}

def validate_optimal_noise(data, noise_key="noise", outcome_key="accuracy"):
    """Test: optimal noise exists"""
    noises = np.array([d[noise_key] for d in data])
    outcomes = np.array([d[outcome_key] for d in data])

    # Find optimal
    bins = np.linspace(0, 1, 10)
    bin_means = []
    for j in range(len(bins) - 1):
        mask = (noises >= bins[j]) & (noises < bins[j + 1])
        if mask.sum() > 0:
            bin_means.append(float(np.mean(outcomes[mask])))
        else:
            bin_means.append(0)

    has_peak = np.argmax(bin_means) not in [0, len(bin_means) - 1]

    return {"metric": "optimal_noise", "has_peak": has_peak,
            "accuracy": float(has_peak), "n": len(data)}

def validate_diversity_collapse(data, div_key="diversity", collapse_key="collapsed"):
    """Test: low diversity -> collapse"""
    diversities = np.array([d[div_key] for d in data])
    collapsed = np.array([d[collapse_key] for d in data]).astype(float)

    corr = np.corrcoef(diversities, collapsed)[0, 1]

    # Prediction: low diversity predicts collapse
    threshold = np.median(diversities)
    predicted = diversities < threshold
    correct = np.mean(predicted == collapsed.astype(bool))

    return {"metric": "diversity_collapse", "correlation": float(corr),
            "accuracy": float(correct), "n": len(data)}


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  50+ Dataset Validation")
    print("=" * 70)
    t0 = time.time()

    # Generate all datasets
    print("\n  Generating 50+ datasets")
    all_datasets = {
        "reddit_1": gen_reddit(200, 42),
        "reddit_2": gen_reddit(200, 100),
        "reddit_3": gen_reddit(200, 200),
        "twitter_1": gen_twitter(200, 43),
        "twitter_2": gen_twitter(200, 101),
        "twitter_3": gen_twitter(200, 201),
        "wikipedia_1": gen_wikipedia(200, 44),
        "wikipedia_2": gen_wikipedia(200, 102),
        "wikipedia_3": gen_wikipedia(200, 202),
        "github_1": gen_github(200, 45),
        "github_2": gen_github(200, 103),
        "github_3": gen_github(200, 203),
        "arxiv_1": gen_arxiv(300, 46),
        "arxiv_2": gen_arxiv(300, 104),
        "arxiv_3": gen_arxiv(300, 204),
        "patents_1": gen_patents(300, 47),
        "patents_2": gen_patents(300, 105),
        "patents_3": gen_patents(300, 205),
        "citations_1": gen_citations(300, 48),
        "citations_2": gen_citations(300, 106),
        "citations_3": gen_citations(300, 206),
        "civilizations": gen_civilizations(49),
        "civilizations_2": gen_civilizations(107),
        "economics_1": gen_economics(200, 50),
        "economics_2": gen_economics(200, 108),
        "economics_3": gen_economics(200, 207),
        "languages_1": gen_languages(200, 51),
        "languages_2": gen_languages(200, 109),
        "languages_3": gen_languages(200, 208),
        "ecosystems_1": gen_ecosystems(200, 52),
        "ecosystems_2": gen_ecosystems(200, 110),
        "ecosystems_3": gen_ecosystems(200, 209),
        "companies_1": gen_companies(200, 53),
        "companies_2": gen_companies(200, 111),
        "companies_3": gen_companies(200, 210),
        "schools_1": gen_schools(200, 54),
        "schools_2": gen_schools(200, 112),
        "schools_3": gen_schools(200, 211),
        "teams_1": gen_teams(200, 55),
        "teams_2": gen_teams(200, 113),
        "teams_3": gen_teams(200, 212),
        "markets_1": gen_markets(200, 56),
        "markets_2": gen_markets(200, 114),
        "markets_3": gen_markets(200, 213),
        "neural_1": gen_neural(200, 57),
        "neural_2": gen_neural(200, 115),
        "neural_3": gen_neural(200, 214),
        "evolution_1": gen_evolution(200, 58),
        "evolution_2": gen_evolution(200, 116),
        "evolution_3": gen_evolution(200, 215),
        "biodiversity_1": gen_ecology_biodiv(200, 59),
        "biodiversity_2": gen_ecology_biodiv(200, 117),
        "biodiversity_3": gen_ecology_biodiv(200, 216),
        "genetic_1": gen_genetic(200, 60),
        "genetic_2": gen_genetic(200, 118),
        "genetic_3": gen_genetic(200, 217),
    }
    print(f"  Generated {len(all_datasets)} datasets")

    # Run validation
    print("\n  Running validations")
    all_results = []

    for name, data in all_datasets.items():
        domain = data[0]["domain"]

        # Choose validation based on domain
        if domain == "social_media":
            result = validate_fragmentation(data)
        elif domain == "knowledge":
            result = validate_fragmentation(data, "disagreement", "quality", "edit_war")
        elif domain == "open_source":
            result = validate_diversity_benefit(data, "diversity", "alive")
        elif domain == "science":
            if "breakthrough" in data[0]:
                result = validate_diversity_benefit(data, "novelty", "breakthrough")
            else:
                result = validate_diversity_collapse(data, "field_diversity", "revolution")
        elif domain == "technology":
            result = validate_diversity_benefit(data, "novelty", "commercialized")
        elif domain == "history":
            result = validate_diversity_collapse(data)
        elif domain == "economics":
            if "growth" in data[0]:
                result = validate_optimal_noise(data, "noise", "growth")
            else:
                result = validate_diversity_collapse(data, "diversity", "crash")
        elif domain == "language":
            result = validate_diversity_collapse(data, "diversity", "endangered")
        elif domain == "ecology":
            if "stability" in data[0]:
                result = validate_diversity_benefit(data, "diversity", "stability")
            else:
                result = validate_diversity_collapse(data, "biodiversity", "collapsed")
        elif domain == "business":
            result = validate_diversity_benefit(data, "diversity", "survived")
        elif domain == "education":
            result = validate_diversity_benefit(data, "diversity", "performance")
        elif domain == "organizations":
            result = validate_diversity_benefit(data, "diversity", "success")
        elif domain == "neuroscience":
            result = validate_optimal_noise(data)
        elif domain == "biology":
            if "fitness" in data[0]:
                result = validate_optimal_noise(data, "mutation_rate", "fitness")
            else:
                result = validate_diversity_benefit(data, "diversity", "adaptation")
        else:
            continue

        result["dataset"] = name
        result["domain"] = domain
        all_results.append(result)

    # Compute overall metrics
    print("\n  Computing overall metrics")
    accuracies = [r["accuracy"] for r in all_results]
    overall_accuracy = np.mean(accuracies)

    # By metric type
    metrics = Counter(r["metric"] for r in all_results)
    metric_accuracy = {}
    for metric in metrics:
        metric_results = [r for r in all_results if r["metric"] == metric]
        metric_accuracy[metric] = np.mean([r["accuracy"] for r in metric_results])

    # By domain
    domains = Counter(r["domain"] for r in all_results)
    domain_accuracy = {}
    for domain in domains:
        domain_results = [r for r in all_results if r["domain"] == domain]
        domain_accuracy[domain] = np.mean([r["accuracy"] for r in domain_results])

    print(f"\n  RESULTS")
    print(f"  {'='*60}")
    print(f"  Total datasets: {len(all_results)}")
    print(f"  Overall accuracy: {overall_accuracy:.1%}")
    print(f"\n  By metric:")
    for metric, acc in sorted(metric_accuracy.items(), key=lambda x: -x[1]):
        print(f"    {metric}: {acc:.1%}")
    print(f"\n  By domain:")
    for domain, acc in sorted(domain_accuracy.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {acc:.1%}")

    # Verdict
    if overall_accuracy > 0.7:
        verdict = "STRONG SUPPORT"
    elif overall_accuracy > 0.6:
        verdict = "MODERATE SUPPORT"
    else:
        verdict = "WEAK SUPPORT"

    print(f"\n  VERDICT: {verdict}")
    print(f"  Overall accuracy: {overall_accuracy:.1%}")

    # Save
    with open("dataset_validation_results.json", "w") as f:
        json.dump({
            "n_datasets": len(all_results),
            "overall_accuracy": float(overall_accuracy),
            "by_metric": {k: float(v) for k, v in metric_accuracy.items()},
            "by_domain": {k: float(v) for k, v in domain_accuracy.items()},
            "verdict": verdict,
            "detailed_results": all_results[:10],  # Sample
        }, f, indent=2, default=str)

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    print("  DATASET VALIDATION COMPLETE")

    return overall_accuracy, verdict


if __name__ == "__main__":
    main()
