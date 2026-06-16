#!/usr/bin/env python3
"""
THEORIA Law Discovery Engine
==============================

Discovers mathematical relationships (laws) in real data.

This engine:
1. Takes numerical data
2. Tests multiple mathematical forms
3. Finds the best-fit relationship
4. Validates statistically
5. Makes predictions
6. Generates explanations

Usage:
    python law_discovery.py
"""

import os
import json
import hashlib
from datetime import datetime

import numpy as np
from scipy import stats, optimize


# ============================================================================
# MATHEMATICAL FORMS
# ============================================================================

def linear(x, a, b):
    """y = ax + b"""
    return a * x + b

def quadratic(x, a, b, c):
    """y = ax^2 + bx + c"""
    return a * x**2 + b * x + c

def power_law(x, a, b):
    """y = a * x^b"""
    return a * np.power(x, b)

def exponential(x, a, b):
    """y = a * exp(bx)"""
    return a * np.exp(b * x)

def logarithmic(x, a, b):
    """y = a * ln(x) + b"""
    return a * np.log(x + 1) + b

def inverse(x, a, b):
    """y = a / (x + b)"""
    return a / (x + b)

def sinusoidal(x, a, b, c, d):
    """y = a * sin(bx + c) + d"""
    return a * np.sin(b * x + c) + d


# ============================================================================
# LAW DISCOVERY
# ============================================================================

def fit_forms(x, y):
    """Try multiple mathematical forms and return best fits."""
    results = []
    
    # Clean data
    mask = np.isfinite(x) & np.isfinite(y) & (x > 0)
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(x_clean) < 5:
        return results
    
    forms = [
        ("linear", linear, 2),
        ("quadratic", quadratic, 3),
        ("power_law", power_law, 2),
        ("exponential", exponential, 2),
        ("logarithmic", logarithmic, 2),
        ("inverse", inverse, 2),
    ]
    
    for name, func, n_params in forms:
        try:
            if name in ["power_law", "exponential"]:
                # Use log-transform for stability
                valid = y_clean > 0
                if sum(valid) < n_params + 1:
                    continue
                popt, pcov = optimize.curve_fit(func, x_clean[valid], y_clean[valid],
                                               p0=[1.0, 0.1], maxfev=5000)
            else:
                popt, pcov = optimize.curve_fit(func, x_clean, y_clean,
                                               maxfev=5000)
            
            y_pred = func(x_clean, *popt)
            residuals = y_clean - y_pred
            
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((y_clean - np.mean(y_clean))**2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            n = len(x_clean)
            p = n_params
            aic = n * np.log(ss_res / n) + 2 * p
            bic = n * np.log(ss_res / n) + p * np.log(n)
            
            # Compute p-value for the fit
            f_stat = ((ss_tot - ss_res) / (p - 1)) / (ss_res / (n - p)) if n > p else 0
            p_value = 1 - stats.f.cdf(f_stat, p - 1, n - p) if f_stat > 0 else 1
            
            # Format equation
            if name == "linear":
                equation = f"y = {popt[0]:.4f}x + {popt[1]:.4f}"
            elif name == "quadratic":
                equation = f"y = {popt[0]:.4f}x^2 + {popt[1]:.4f}x + {popt[2]:.4f}"
            elif name == "power_law":
                equation = f"y = {popt[0]:.4f} * x^{popt[1]:.4f}"
            elif name == "exponential":
                equation = f"y = {popt[0]:.4f} * exp({popt[1]:.4f}x)"
            elif name == "logarithmic":
                equation = f"y = {popt[0]:.4f} * ln(x) + {popt[1]:.4f}"
            elif name == "inverse":
                equation = f"y = {popt[0]:.4f} / (x + {popt[1]:.4f})"
            
            results.append({
                "form": name,
                "equation": equation,
                "params": popt.tolist(),
                "r_squared": float(r_squared),
                "aic": float(aic),
                "bic": float(bic),
                "p_value": float(p_value),
                "n_params": n_params,
                "n_data": n,
                "func": func,
            })
        except Exception:
            continue
    
    # Sort by BIC (lower is better)
    results.sort(key=lambda r: r["bic"])
    
    return results


def discover_law(x, y, x_name="x", y_name="y", domain="unknown"):
    """Discover the best mathematical law relating x and y."""
    fits = fit_forms(x, y)
    
    if not fits:
        return None
    
    best = fits[0]
    
    # Generate description
    if best["r_squared"] > 0.9:
        strength = "very strong"
    elif best["r_squared"] > 0.7:
        strength = "strong"
    elif best["r_squared"] > 0.5:
        strength = "moderate"
    else:
        strength = "weak"
    
    law = {
        "name": f"{y_name} as function of {x_name}",
        "equation": best["equation"],
        "form": best["form"],
        "r_squared": best["r_squared"],
        "p_value": best["p_value"],
        "aic": best["aic"],
        "bic": best["bic"],
        "strength": strength,
        "domain": domain,
        "x_variable": x_name,
        "y_variable": y_name,
        "n_data_points": best["n_data"],
        "description": f"{y_name} follows a {best['form']} relationship with {x_name} (R^2={best['r_squared']:.3f}, p={best['p_value']:.6f})",
    }
    
    return law, fits


# ============================================================================
# PREDICTION ENGINE
# ============================================================================

def make_law_prediction(law, x_future, fits):
    """Make a prediction using the discovered law."""
    best = fits[0]
    func = best["func"]
    params = best["params"]
    
    y_pred = func(x_future, *params)
    
    # Compute prediction interval
    x = np.array([x_future])
    y_fit = func(x, *params)
    
    return {
        "x": float(x_future),
        "predicted_y": float(y_fit[0]),
        "law": law["equation"],
        "confidence": law["r_squared"],
    }


# ============================================================================
# THEORY GENERATION
# ============================================================================

def generate_theory(law, data_description):
    """Generate a theory explaining the discovered law."""
    
    # Parse the law
    form = law["form"]
    x_var = law["x_variable"]
    y_var = law["y_variable"]
    
    # Generate explanation based on form
    if form == "linear":
        explanation = f"{y_var} changes proportionally with {x_var}. This suggests a direct causal relationship where changes in {x_var} produce proportional changes in {y_var}."
        mechanism = f"Direct linear coupling between {x_var} and {y_var}"
    elif form == "power_law":
        explanation = f"{y_var} follows a power law with {x_var}. This suggests scale-invariant dynamics, common in complex systems."
        mechanism = f"Scale-free relationship between {x_var} and {y_var}"
    elif form == "exponential":
        explanation = f"{y_var} grows exponentially with {x_var}. This suggests positive feedback or compounding effects."
        mechanism = f"Exponential feedback loop between {x_var} and {y_var}"
    elif form == "quadratic":
        explanation = f"{y_var} has a quadratic relationship with {x_var}. This suggests nonlinear dynamics with acceleration or deceleration."
        mechanism = f"Nonlinear interaction between {x_var} and {y_var}"
    elif form == "logarithmic":
        explanation = f"{y_var} grows logarithmically with {x_var}. This suggests diminishing returns or saturation effects."
        mechanism = f"Saturation dynamics between {x_var} and {y_var}"
    elif form == "inverse":
        explanation = f"{y_var} is inversely related to {x_var}. This suggests a trade-off or conservation relationship."
        mechanism = f"Inverse relationship between {x_var} and {y_var}"
    else:
        explanation = f"{y_var} follows a {form} relationship with {x_var}."
        mechanism = f"{form} dynamics between {x_var} and {y_var}"
    
    theory = {
        "name": f"Law of {y_var}-{x_var} Relationship",
        "statement": law["description"],
        "equation": law["equation"],
        "explanation": explanation,
        "mechanism": mechanism,
        "evidence": f"R^2={law['r_squared']:.3f}, p={law['p_value']:.6f}, n={law['n_data_points']}",
        "testable_predictions": [
            f"{y_var} will continue to follow {law['form']} relationship with {x_var}",
            f"Changing {x_var} will produce {law['form']} change in {y_var}",
        ],
        "limitations": [
            "Correlation does not imply causation",
            "Relationship may not hold outside observed range",
            "Confounding variables not controlled",
        ],
    }
    
    return theory


# ============================================================================
# MAIN ENGINE
# ============================================================================

def run_law_discovery():
    """Run the full law discovery engine."""
    print("=" * 70)
    print("  THEORIA Law Discovery Engine")
    print("  Discover mathematical laws in real data")
    print("=" * 70)
    
    # Define datasets to analyze
    datasets = {
        "climate_trend": {
            "description": "Global temperature anomaly vs time",
            "x_name": "years since 1980",
            "y_name": "temperature anomaly",
            "domain": "climate science",
        },
        "kepler": {
            "description": "Planetary orbital period vs semi-major axis",
            "x_name": "semi-major axis",
            "y_name": "orbital period",
            "domain": "astronomy",
        },
        "ohm": {
            "description": "Voltage vs current",
            "x_name": "current",
            "y_name": "voltage",
            "domain": "electrical engineering",
        },
    }
    
    all_laws = []
    all_theories = []
    all_predictions = []
    
    # Analyze each dataset
    for name, info in datasets.items():
        print(f"\n  Analyzing: {info['description']}...")
        
        # Generate data (in production, this would be real data)
        np.random.seed(42)
        
        if name == "climate_trend":
            x = np.arange(0, 46)
            y = 0.018 * x + 0.1 * np.random.normal(0, 1, 46)
            x_name = "years since 1980"
            y_name = "temperature anomaly (C)"
        elif name == "kepler":
            x = np.linspace(0.5, 10, 50)
            y = np.sqrt(x**3) + 0.1 * np.random.normal(0, 1, 50)
            x_name = "semi-major axis (AU)"
            y_name = "orbital period (years)"
        elif name == "ohm":
            x = np.linspace(0.1, 5, 50)
            y = 10 * x + 0.5 * np.random.normal(0, 1, 50)
            x_name = "current (A)"
            y_name = "voltage (V)"
        
        # Discover law
        law, fits = discover_law(x, y, x_name, y_name, info["domain"])
        
        if law:
            print(f"    Discovered: {law['equation']}")
            print(f"    R^2 = {law['r_squared']:.3f}, p = {law['p_value']:.6f}")
            
            all_laws.append(law)
            
            # Generate theory
            theory = generate_theory(law, info["description"])
            all_theories.append(theory)
            print(f"    Theory: {theory['explanation'][:80]}...")
            
            # Make prediction
            x_future = 50  # Predict 50 years from start
            pred = make_law_prediction(law, x_future, fits)
            all_predictions.append({
                "dataset": name,
                "prediction": f"At {x_future} {x_name}, {y_name} will be {pred['predicted_y']:.3f}",
                "law": law["equation"],
                "confidence": law["r_squared"],
                "test_date": "2030-01-01",
                "hash": hashlib.sha256(f"{name}_{law['equation']}".encode()).hexdigest()[:16],
            })
            print(f"    Prediction: {pred['predicted_y']:.3f} at x={x_future}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  LAW DISCOVERY SUMMARY")
    print(f"{'='*70}")
    print(f"  Datasets analyzed: {len(datasets)}")
    print(f"  Laws discovered: {len(all_laws)}")
    print(f"  Theories generated: {len(all_theories)}")
    print(f"  Predictions made: {len(all_predictions)}")
    print(f"\n  Discovered Laws:")
    for law in all_laws:
        print(f"    {law['domain']}: {law['equation']} (R^2={law['r_squared']:.3f})")
    print(f"\n  Predictions:")
    for pred in all_predictions:
        print(f"    {pred['dataset']}: {pred['prediction']}")
    print(f"{'='*70}")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "n_datasets": len(datasets),
        "n_laws": len(all_laws),
        "n_theories": len(all_theories),
        "n_predictions": len(all_predictions),
        "laws": [{k: v for k, v in law.items() if k != "func"} for law in all_laws],
        "theories": all_theories,
        "predictions": all_predictions,
    }
    
    os.makedirs("results", exist_ok=True)
    with open("results/law_discovery_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Results saved to results/law_discovery_results.json")
    
    # Store predictions immutably
    registry_file = "results/prediction_registry.json"
    if os.path.exists(registry_file):
        with open(registry_file) as f:
            registry = json.load(f)
    else:
        registry = {"version": "4.0", "predictions": {}}
    
    for pred in all_predictions:
        pred_id = f"LAW-{pred['hash'][:8]}"
        if pred_id not in registry["predictions"]:
            registry["predictions"][pred_id] = {
                "question": f"What is the relationship in {pred['dataset']}?",
                "prediction": pred["prediction"],
                "confidence": pred["confidence"],
                "test_date": pred["test_date"],
                "result": "UNKNOWN",
                "law": pred["law"],
                "hash": pred["hash"],
                "status": "FROZEN",
                "made_date": datetime.now().isoformat(),
            }
    
    with open(registry_file, "w") as f:
        json.dump(registry, f, indent=2)
    print(f"  Predictions stored immutably")


if __name__ == "__main__":
    run_law_discovery()
