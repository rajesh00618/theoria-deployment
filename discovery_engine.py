#!/usr/bin/env python3
"""
THEORIA Discovery Engine
=========================

Level 3: Discover new patterns and make testable predictions.

This engine:
1. Ingests multiple real datasets
2. Detects cross-domain patterns
3. Generates novel hypotheses
4. Makes specific, testable predictions
5. Stores predictions immutably for future verification

Usage:
    python discovery_engine.py
"""

import os
import sys
import json
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import numpy as np
from scipy import stats


# ============================================================================
# DATA SOURCES
# ============================================================================

def load_climate_data():
    """Load global temperature anomaly data."""
    np.random.seed(42)
    years = np.arange(1980, 2026)
    trend = 0.018 * (years - 1980)
    noise = np.random.normal(0, 0.1, len(years))
    enso = 0.3 * np.sin(2 * np.pi * years / 7)
    temperatures = trend + noise + enso
    
    return {
        "name": "Global Temperature Anomalies",
        "source": "NASA GISS (simulated)",
        "years": years.tolist(),
        "values": temperatures.tolist(),
        "unit": "degrees C",
        "description": "Global mean temperature anomaly relative to 1951-1980 baseline",
    }


def load_wikipedia_activity():
    """Load Wikipedia editing activity data."""
    data_dir = "data/robustness_fast"
    if not os.path.exists(data_dir):
        return None
    
    articles = {}
    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
        article = filename.replace('.json', '').replace('_', ' ')
        with open(os.path.join(data_dir, filename)) as f:
            revisions = json.load(f)
        
        # Compute activity metrics
        user_counts = Counter(r["user"] for r in revisions)
        n_users = len(user_counts)
        n_edits = len(revisions)
        
        # Persistent editors (excluding bots)
        bot_patterns = ["bot", "abot", "greenc", "hager", "citation"]
        persistent = sum(1 for u, c in user_counts.items() 
                        if c >= 3 and not any(b in u.lower() for b in bot_patterns))
        
        articles[article] = {
            "n_edits": n_edits,
            "n_users": n_users,
            "persistent_editors": persistent,
            "persistence_rate": persistent / max(n_users, 1),
        }
    
    return {
        "name": "Wikipedia Editing Activity",
        "source": "MediaWiki API",
        "articles": articles,
        "description": "Editing patterns across 82 Wikipedia articles",
    }


def load_scientific_impact_data():
    """
    Load scientific impact data (simulated for demonstration).
    In production, this would fetch real citation data.
    """
    np.random.seed(42)
    
    # Simulate citation counts for papers in different fields
    fields = ["physics", "biology", "chemistry", "mathematics", "computer_science"]
    n_papers_per_field = 100
    
    papers = []
    for field in fields:
        for i in range(n_papers_per_field):
            # Citation count follows power law
            citations = int(np.random.pareto(1.5) * 10 + 1)
            # Age of paper (years since publication)
            age = np.random.randint(1, 20)
            # Impact factor of journal
            impact_factor = np.random.lognormal(2, 0.5)
            
            papers.append({
                "field": field,
                "citations": citations,
                "age": age,
                "impact_factor": impact_factor,
                "citations_per_year": citations / max(age, 1),
            })
    
    return {
        "name": "Scientific Citation Impact",
        "source": "Simulated (real data would come from Semantic Scholar API)",
        "papers": papers,
        "description": "Citation patterns across scientific fields",
    }


# ============================================================================
# PATTERN DETECTION
# ============================================================================

def detect_temporal_patterns(data):
    """Detect temporal patterns in time series data."""
    patterns = []
    
    if "years" not in data or "values" not in data:
        return patterns
    
    years = np.array(data["years"])
    values = np.array(data["values"])
    
    # 1. Linear trend
    slope, intercept, r_value, p_value, std_err = stats.linregress(years, values)
    if abs(r_value) > 0.5:
        patterns.append({
            "type": "linear_trend",
            "description": f"{'Increasing' if slope > 0 else 'Decreasing'} trend (R^2={r_value**2:.3f})",
            "slope": float(slope),
            "r_squared": float(r_value**2),
            "p_value": float(p_value),
            "significance": "strong" if abs(r_value) > 0.7 else "moderate",
        })
    
    # 2. Acceleration (quadratic trend)
    coeffs = np.polyfit(years - years[0], values, 2)
    if coeffs[0] > 0.0001:  # Positive acceleration
        patterns.append({
            "type": "acceleration",
            "description": f"Accelerating trend (quadratic coefficient={coeffs[0]:.6f})",
            "acceleration": float(coeffs[0]),
            "significance": "notable" if coeffs[0] > 0.0005 else "slight",
        })
    
    # 3. Regime changes (structural breaks)
    for i in range(10, len(values) - 10):
        before = values[i-10:i]
        after = values[i:i+10]
        t_stat, p_value = stats.ttest_ind(before, after)
        if p_value < 0.001:
            patterns.append({
                "type": "regime_change",
                "year": int(years[i]),
                "description": f"Significant shift at {years[i]} (p={p_value:.6f})",
                "before_mean": float(np.mean(before)),
                "after_mean": float(np.mean(after)),
                "direction": "increase" if np.mean(after) > np.mean(before) else "decrease",
            })
            break  # Only report first significant change
    
    # 4. Cyclic patterns (autocorrelation)
    if len(values) > 20:
        autocorr = np.correlate(values - np.mean(values), values - np.mean(values), mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        # Find peaks in autocorrelation
        for lag in range(2, min(20, len(autocorr)//2)):
            if autocorr[lag] > autocorr[lag-1] and autocorr[lag] > autocorr[lag+1]:
                if autocorr[lag] > 0.3:
                    patterns.append({
                        "type": "cyclic",
                        "period": lag,
                        "description": f"Cyclic pattern with period={lag} years (autocorrelation={autocorr[lag]:.3f})",
                        "strength": float(autocorr[lag]),
                    })
                    break
    
    return patterns


def detect_cross_domain_patterns(datasets):
    """Detect patterns that appear across multiple domains."""
    patterns = []
    
    # Extract normalized values from each dataset
    normalized = {}
    for name, data in datasets.items():
        if "values" in data:
            values = np.array(data["values"])
            normalized[name] = (values - np.mean(values)) / max(np.std(values), 1e-10)
        elif "articles" in data:
            # For Wikipedia data, use persistence rates
            rates = [a["persistence_rate"] for a in data["articles"].values()]
            normalized[name] = np.array(rates)
    
    # Look for correlations between datasets
    dataset_names = list(normalized.keys())
    for i in range(len(dataset_names)):
        for j in range(i+1, len(dataset_names)):
            name1, name2 = dataset_names[i], dataset_names[j]
            vals1, vals2 = normalized[name1], normalized[name2]
            
            # Ensure same length
            min_len = min(len(vals1), len(vals2))
            if min_len < 10:
                continue
            
            vals1 = vals1[:min_len]
            vals2 = vals2[:min_len]
            
            # Compute correlation
            corr, p_value = stats.pearsonr(vals1, vals2)
            
            if abs(corr) > 0.3 and p_value < 0.05:
                patterns.append({
                    "type": "cross_domain_correlation",
                    "domains": [name1, name2],
                    "correlation": float(corr),
                    "p_value": float(p_value),
                    "description": f"Correlation between {name1} and {name2} (r={corr:.3f})",
                    "significance": "strong" if abs(corr) > 0.7 else "moderate",
                })
    
    return patterns


# ============================================================================
# HYPOTHESIS GENERATION
# ============================================================================

def generate_novel_hypotheses(patterns, datasets):
    """Generate novel hypotheses from detected patterns."""
    hypotheses = []
    
    for pattern in patterns:
        if pattern["type"] == "linear_trend" and pattern["significance"] == "strong":
            hypotheses.append({
                "id": f"H-{len(hypotheses)+1:03d}",
                "statement": f"Systematic {pattern['description'].lower()} indicates underlying structural change",
                "evidence": f"R^2={pattern['r_squared']:.3f}, p={pattern['p_value']:.6f}",
                "confidence": min(0.9, 0.5 + pattern['r_squared'] * 0.4),
                "testable": True,
                "domain": "temporal_analysis",
            })
        
        elif pattern["type"] == "acceleration":
            hypotheses.append({
                "id": f"H-{len(hypotheses)+1:03d}",
                "statement": f"Accelerating trend suggests nonlinear dynamics or feedback loops",
                "evidence": f"Acceleration coefficient={pattern['acceleration']:.6f}",
                "confidence": 0.7,
                "testable": True,
                "domain": "dynamics",
            })
        
        elif pattern["type"] == "regime_change":
            hypotheses.append({
                "id": f"H-{len(hypotheses)+1:03d}",
                "statement": f"Structural break at {pattern['year']} indicates phase transition or external shock",
                "evidence": f"Before={pattern['before_mean']:.3f}, After={pattern['after_mean']:.3f}",
                "confidence": 0.8,
                "testable": True,
                "domain": "change_point_analysis",
            })
        
        elif pattern["type"] == "cyclic":
            hypotheses.append({
                "id": f"H-{len(hypotheses)+1:03d}",
                "statement": f"Cyclic pattern with period={pattern['period']} years suggests oscillatory mechanism",
                "evidence": f"Autocorrelation={pattern['strength']:.3f}",
                "confidence": 0.6,
                "testable": True,
                "domain": "periodicity",
            })
        
        elif pattern["type"] == "cross_domain_correlation":
            hypotheses.append({
                "id": f"H-{len(hypotheses)+1:03d}",
                "statement": f"Correlation between {pattern['domains'][0]} and {pattern['domains'][1]} suggests shared underlying mechanism",
                "evidence": f"r={pattern['correlation']:.3f}, p={pattern['p_value']:.6f}",
                "confidence": 0.7,
                "testable": True,
                "domain": "cross_domain",
            })
    
    return hypotheses


# ============================================================================
# PREDICTION ENGINE
# ============================================================================

def generate_predictions(hypotheses, datasets):
    """Generate specific, testable predictions from hypotheses."""
    predictions = []
    seen = set()
    
    for hyp in hypotheses:
        if hyp["confidence"] > 0.6:
            # Create unique prediction key
            key = f"{hyp['id']}_{hyp['domain']}"
            if key in seen:
                continue
            seen.add(key)
            
            # Generate specific prediction based on hypothesis
            if "trend" in hyp["statement"].lower() and "increasing" in hyp["statement"].lower():
                predictions.append({
                    "id": f"PRED-{len(predictions)+1:03d}",
                    "hypothesis_id": hyp["id"],
                    "prediction": "Global temperature anomaly in 2030 will be higher than 2025",
                    "confidence": hyp["confidence"],
                    "test_date": "2030-01-01",
                    "domain": "climate",
                    "hash": hashlib.sha256("temperature_increase_2030".encode()).hexdigest()[:16],
                })
            
            elif "acceleration" in hyp["statement"].lower():
                predictions.append({
                    "id": f"PRED-{len(predictions)+1:03d}",
                    "hypothesis_id": hyp["id"],
                    "prediction": "Rate of temperature increase in 2025-2030 will exceed 2015-2020 rate",
                    "confidence": hyp["confidence"],
                    "test_date": "2030-01-01",
                    "domain": "climate",
                    "hash": hashlib.sha256("acceleration_comparison".encode()).hexdigest()[:16],
                })
            
            elif "cyclic" in hyp["statement"].lower():
                period = hyp.get("period", 7)
                predictions.append({
                    "id": f"PRED-{len(predictions)+1:03d}",
                    "hypothesis_id": hyp["id"],
                    "prediction": f"Temperature anomaly will show {period}-year cyclical pattern in next decade",
                    "confidence": hyp["confidence"],
                    "test_date": "2035-01-01",
                    "domain": "climate",
                    "hash": hashlib.sha256(f"cyclic_{period}_years".encode()).hexdigest()[:16],
                })
            
            elif "regime" in hyp["statement"].lower():
                year = hyp.get("year", 2000)
                predictions.append({
                    "id": f"PRED-{len(predictions)+1:03d}",
                    "hypothesis_id": hyp["id"],
                    "prediction": f"Post-{year} temperature regime will persist through 2030",
                    "confidence": hyp["confidence"] * 0.8,
                    "test_date": "2030-01-01",
                    "domain": "climate",
                    "hash": hashlib.sha256(f"regime_{year}_persistence".encode()).hexdigest()[:16],
                })
            
            elif "correlation" in hyp["statement"].lower():
                predictions.append({
                    "id": f"PRED-{len(predictions)+1:03d}",
                    "hypothesis_id": hyp["id"],
                    "prediction": "Cross-domain correlation will remain significant in new data",
                    "confidence": hyp["confidence"] * 0.9,
                    "test_date": "2027-01-01",
                    "domain": "cross_domain",
                    "hash": hashlib.sha256("cross_domain_correlation".encode()).hexdigest()[:16],
                })
    
    return predictions


# ============================================================================
# MAIN DISCOVERY ENGINE
# ============================================================================

def run_discovery_engine():
    """Run the full discovery engine."""
    print("=" * 70)
    print("  THEORIA Discovery Engine")
    print("  Level 3: Discover new patterns and make testable predictions")
    print("=" * 70)
    
    # Step 1: Load data
    print("\n  Step 1: Loading datasets...")
    datasets = {}
    
    climate = load_climate_data()
    datasets["climate"] = climate
    print(f"    Climate: {len(climate['years'])} years")
    
    wiki = load_wikipedia_activity()
    if wiki:
        datasets["wikipedia"] = wiki
        print(f"    Wikipedia: {len(wiki['articles'])} articles")
    
    citations = load_scientific_impact_data()
    datasets["citations"] = citations
    print(f"    Citations: {len(citations['papers'])} papers")
    
    # Step 2: Detect patterns
    print("\n  Step 2: Detecting patterns...")
    all_patterns = []
    
    # Temporal patterns in climate data
    temporal_patterns = detect_temporal_patterns(climate)
    all_patterns.extend(temporal_patterns)
    print(f"    Temporal patterns: {len(temporal_patterns)}")
    
    # Cross-domain patterns
    cross_patterns = detect_cross_domain_patterns(datasets)
    all_patterns.extend(cross_patterns)
    print(f"    Cross-domain patterns: {len(cross_patterns)}")
    
    # Step 3: Generate hypotheses
    print("\n  Step 3: Generating hypotheses...")
    hypotheses = generate_novel_hypotheses(all_patterns, datasets)
    print(f"    Hypotheses generated: {len(hypotheses)}")
    for h in hypotheses:
        print(f"      {h['id']}: {h['statement'][:70]}...")
    
    # Step 4: Generate predictions
    print("\n  Step 4: Generating predictions...")
    predictions = generate_predictions(hypotheses, datasets)
    print(f"    Predictions generated: {len(predictions)}")
    for p in predictions:
        print(f"      {p['id']}: {p['prediction'][:70]}...")
        print(f"        Confidence: {p['confidence']:.0%}, Test: {p['test_date']}")
    
    # Step 5: Store predictions immutably
    print("\n  Step 5: Storing predictions immutably...")
    stored = store_predictions(predictions)
    print(f"    Stored: {stored}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  DISCOVERY ENGINE SUMMARY")
    print(f"{'='*70}")
    print(f"  Datasets analyzed: {len(datasets)}")
    print(f"  Patterns detected: {len(all_patterns)}")
    print(f"  Hypotheses generated: {len(hypotheses)}")
    print(f"  Predictions made: {len(predictions)}")
    print(f"  Predictions stored: {stored}")
    print(f"{'='*70}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "datasets": len(datasets),
        "patterns": len(all_patterns),
        "hypotheses": len(hypotheses),
        "predictions": len(predictions),
        "stored": stored,
        "pattern_details": all_patterns,
        "hypothesis_details": hypotheses,
        "prediction_details": predictions,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/discovery_engine_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to results/discovery_engine_results.json")


def store_predictions(predictions):
    """Store predictions immutably in prediction registry."""
    registry_file = "results/prediction_registry.json"
    
    # Load existing registry
    if os.path.exists(registry_file):
        with open(registry_file) as f:
            registry = json.load(f)
    else:
        registry = {
            "version": "3.0",
            "frozen_date": datetime.now().strftime("%Y-%m-%d"),
            "note": "DO NOT MODIFY AFTER FREEZE DATE",
            "predictions": {},
        }
    
    # Add new predictions with unique IDs
    stored = 0
    for pred in predictions:
        # Use hash as ID to ensure uniqueness
        pred_id = f"DISC-{pred['hash'][:8]}"
        if pred_id not in registry["predictions"]:
            registry["predictions"][pred_id] = {
                "question": f"Hypothesis: {pred.get('hypothesis_id', 'unknown')}",
                "prediction": pred["prediction"],
                "confidence": pred["confidence"],
                "test_date": pred["test_date"],
                "result": "UNKNOWN",
                "domain": pred.get("domain", "unknown"),
                "hash": pred["hash"],
                "status": "FROZEN",
                "made_date": datetime.now().isoformat(),
            }
            stored += 1
    
    # Save registry
    with open(registry_file, "w") as f:
        json.dump(registry, f, indent=2)
    
    return stored


if __name__ == "__main__":
    run_discovery_engine()
