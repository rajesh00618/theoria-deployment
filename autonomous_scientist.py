#!/usr/bin/env python3
"""
THEORIA Autonomous Scientist Pipeline
=======================================

Level 2: A system that can:
1. Ingest real scientific data
2. Detect anomalies
3. Generate hypotheses
4. Validate hypotheses
5. Make predictions

Usage:
    python autonomous_scientist.py

Requirements:
    pip install numpy scipy
"""

import os
import sys
import json
import hashlib
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np
from scipy import stats


# ============================================================================
# DATA INGESTION
# ============================================================================

def load_wikipedia_data(data_dir="data/robustness_fast"):
    """Load Wikipedia revision data."""
    articles = {}
    if not os.path.exists(data_dir):
        return articles
    
    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
        article = filename.replace('.json', '').replace('_', ' ')
        with open(os.path.join(data_dir, filename)) as f:
            articles[article] = json.load(f)
    
    return articles


def load_nasa_data():
    """
    Load NASA climate data (simulated for demonstration).
    In production, this would fetch real data from NASA APIs.
    """
    np.random.seed(42)
    
    # Simulate global temperature anomalies (1980-2025)
    years = np.arange(1980, 2026)
    # Real trend: ~0.018°C per year
    trend = 0.018 * (years - 1980)
    # Add natural variability
    noise = np.random.normal(0, 0.1, len(years))
    # Add El Niño/La Niña cycles
    enso = 0.3 * np.sin(2 * np.pi * years / 7)
    
    temperatures = trend + noise + enso
    
    return {
        "years": years.tolist(),
        "temperatures": temperatures.tolist(),
        "source": "NASA GISS (simulated for demonstration)",
    }


def load_genomics_data():
    """
    Load genomics data (simulated for demonstration).
    In production, this would fetch real data from NCBI/UniProt.
    """
    np.random.seed(42)
    
    # Simulate gene expression data
    n_genes = 1000
    n_conditions = 4
    
    # Base expression
    base = np.random.lognormal(0, 1, n_genes)
    
    # Condition effects
    conditions = ["control", "treatment_A", "treatment_B", "combined"]
    effects = [0, 0.5, 0.3, 0.8]
    
    expression = np.zeros((n_genes, n_conditions))
    for j, effect in enumerate(effects):
        expression[:, j] = base * np.exp(effect + np.random.normal(0, 0.2, n_genes))
    
    # Find differentially expressed genes
    fc_threshold = 2.0
    de_genes = []
    for i in range(n_genes):
        fc = expression[i, 1] / expression[i, 0]  # treatment_A vs control
        if fc > fc_threshold or fc < 1/fc_threshold:
            de_genes.append(i)
    
    return {
        "n_genes": n_genes,
        "n_conditions": n_conditions,
        "conditions": conditions,
        "expression": expression.tolist(),
        "de_genes": de_genes,
        "source": "Simulated for demonstration",
    }


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

def detect_anomalies(data, method="zscore", threshold=3.0):
    """
    Detect anomalies in data using z-score method.
    
    Returns list of anomalies with their indices and scores.
    """
    anomalies = []
    
    if isinstance(data, dict) and "temperatures" in data:
        values = np.array(data["temperatures"])
        years = np.array(data["years"])
    elif isinstance(data, list):
        values = np.array(data)
        years = np.arange(len(data))
    else:
        return anomalies
    
    # Compute z-scores
    mean = np.mean(values)
    std = np.std(values)
    z_scores = (values - mean) / max(std, 1e-10)
    
    # Find anomalies
    for i, (z, v) in enumerate(zip(z_scores, values)):
        if abs(z) > threshold:
            anomalies.append({
                "index": int(i),
                "value": float(v),
                "z_score": float(z),
                "year": int(years[i]) if i < len(years) else None,
                "type": "high" if z > 0 else "low",
            })
    
    return anomalies


def detect_trend_changes(data, window=10):
    """
    Detect trend changes in time series data.
    
    Returns list of potential change points.
    """
    if isinstance(data, dict) and "temperatures" in data:
        values = np.array(data["temperatures"])
        years = np.array(data["years"])
    else:
        return []
    
    changes = []
    
    for i in range(window, len(values) - window):
        before = values[i-window:i]
        after = values[i:i+window]
        
        # Test if means are significantly different
        t_stat, p_value = stats.ttest_ind(before, after)
        
        if p_value < 0.01:
            changes.append({
                "index": int(i),
                "year": int(years[i]),
                "before_mean": float(np.mean(before)),
                "after_mean": float(np.mean(after)),
                "p_value": float(p_value),
                "direction": "increasing" if np.mean(after) > np.mean(before) else "decreasing",
            })
    
    return changes


# ============================================================================
# HYPOTHESIS GENERATION
# ============================================================================

def generate_hypotheses(anomalies, trend_changes, data_type="climate"):
    """
    Generate hypotheses to explain detected anomalies.
    
    Returns list of hypotheses with confidence scores.
    """
    hypotheses = []
    
    if data_type == "climate":
        # Climate-specific hypotheses
        if anomalies:
            high_anomalies = [a for a in anomalies if a["type"] == "high"]
            if len(high_anomalies) > 3:
                hypotheses.append({
                    "id": "H1",
                    "statement": "Global temperatures are increasing faster than historical baseline",
                    "evidence": f"{len(high_anomalies)} high-temperature anomalies detected",
                    "confidence": min(0.9, 0.5 + len(high_anomalies) * 0.05),
                    "testable": True,
                    "prediction": "Temperature anomalies will continue to increase",
                })
        
        if trend_changes:
            increasing = [c for c in trend_changes if c["direction"] == "increasing"]
            if len(increasing) > 2:
                hypotheses.append({
                    "id": "H2",
                    "statement": "There are multiple acceleration points in global warming",
                    "evidence": f"{len(increasing)} increasing trend changes detected",
                    "confidence": min(0.8, 0.4 + len(increasing) * 0.1),
                    "testable": True,
                    "prediction": "Future trend changes will be predominantly increasing",
                })
    
    elif data_type == "genomics":
        # Genomics-specific hypotheses
        hypotheses.append({
            "id": "H1",
            "statement": "Treatment A has stronger effect than Treatment B",
            "evidence": "Differential expression analysis",
            "confidence": 0.7,
            "testable": True,
            "prediction": "Treatment A genes will show larger fold changes",
        })
    
    return hypotheses


# ============================================================================
# HYPOTHESIS VALIDATION
# ============================================================================

def validate_hypothesis(hypothesis, data, data_type="climate"):
    """
    Validate a hypothesis using statistical tests.
    
    Returns validation result with p-value and effect size.
    """
    result = {
        "hypothesis_id": hypothesis["id"],
        "statement": hypothesis["statement"],
        "validated": False,
        "p_value": None,
        "effect_size": None,
        "method": None,
        "notes": "",
    }
    
    if data_type == "climate" and "temperatures" in data:
        temperatures = np.array(data["temperatures"])
        
        # Split into early and late periods
        mid = len(temperatures) // 2
        early = temperatures[:mid]
        late = temperatures[mid:]
        
        # Test if late period is significantly higher
        t_stat, p_value = stats.ttest_ind(late, early)
        cohens_d = (np.mean(late) - np.mean(early)) / np.sqrt((np.std(early)**2 + np.std(late)**2) / 2)
        
        result["p_value"] = float(p_value)
        result["effect_size"] = float(cohens_d)
        result["method"] = "Two-sample t-test (early vs late)"
        result["validated"] = p_value < 0.05 and cohens_d > 0.2
        result["notes"] = f"t={t_stat:.3f}, d={cohens_d:.3f}"
    
    return result


# ============================================================================
# PREDICTION ENGINE
# ============================================================================

def make_predictions(validated_hypotheses, data):
    """
    Make predictions based on validated hypotheses.
    
    Returns list of predictions with deadlines.
    """
    predictions = []
    
    for hyp in validated_hypotheses:
        if hyp["validated"] and hyp.get("prediction"):
            predictions.append({
                "id": f"PRED-{len(predictions)+1:03d}",
                "hypothesis_id": hyp["hypothesis_id"],
                "prediction": hyp["prediction"],
                "confidence": hyp.get("confidence", 0.5),
                "made_date": datetime.now().isoformat(),
                "test_date": "2027-01-01",
                "status": "FROZEN",
                "hash": hashlib.sha256(hyp["prediction"].encode()).hexdigest()[:16],
            })
    
    return predictions


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline():
    """Run the full autonomous scientist pipeline."""
    print("=" * 70)
    print("  THEORIA Autonomous Scientist Pipeline")
    print("  Level 2: Observe -> Detect -> Hypothesize -> Validate -> Predict")
    print("=" * 70)
    
    # Step 1: Ingest data
    print("\n  Step 1: Ingesting data...")
    climate_data = load_nasa_data()
    print(f"  Climate data: {len(climate_data['years'])} years")
    
    # Step 2: Detect anomalies
    print("\n  Step 2: Detecting anomalies...")
    anomalies = detect_anomalies(climate_data, threshold=2.0)
    trend_changes = detect_trend_changes(climate_data, window=10)
    print(f"  Anomalies found: {len(anomalies)}")
    print(f"  Trend changes found: {len(trend_changes)}")
    
    # Step 3: Generate hypotheses
    print("\n  Step 3: Generating hypotheses...")
    hypotheses = generate_hypotheses(anomalies, trend_changes, "climate")
    print(f"  Hypotheses generated: {len(hypotheses)}")
    for h in hypotheses:
        print(f"    {h['id']}: {h['statement'][:60]}...")
    
    # Step 4: Validate hypotheses
    print("\n  Step 4: Validating hypotheses...")
    validated = []
    for h in hypotheses:
        result = validate_hypothesis(h, climate_data, "climate")
        status = "VALIDATED" if result["validated"] else "NOT VALIDATED"
        print(f"    {h['id']}: {status} (p={result['p_value']:.4f}, d={result['effect_size']:.3f})")
        if result["validated"]:
            validated.append({**h, **result})
    
    # Step 5: Make predictions
    print("\n  Step 5: Making predictions...")
    predictions = make_predictions(validated, climate_data)
    for p in predictions:
        print(f"    {p['id']}: {p['prediction'][:60]}...")
        print(f"      Confidence: {p['confidence']:.0%}, Test date: {p['test_date']}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  PIPELINE SUMMARY")
    print(f"{'='*70}")
    print(f"  Data points: {len(climate_data['years'])}")
    print(f"  Anomalies detected: {len(anomalies)}")
    print(f"  Trend changes detected: {len(trend_changes)}")
    print(f"  Hypotheses generated: {len(hypotheses)}")
    print(f"  Hypotheses validated: {len(validated)}")
    print(f"  Predictions made: {len(predictions)}")
    print(f"{'='*70}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "data_points": len(climate_data["years"]),
        "anomalies": len(anomalies),
        "trend_changes": len(trend_changes),
        "hypotheses": len(hypotheses),
        "validated": len(validated),
        "predictions": len(predictions),
        "prediction_details": predictions,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/autonomous_scientist_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to results/autonomous_scientist_results.json")


if __name__ == "__main__":
    run_pipeline()
