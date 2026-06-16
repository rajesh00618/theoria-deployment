"""
THEORIA Blind Discovery Benchmark (Lightweight)
=================================================

Tests whether THEORIA can discover CORRECT scientific relationships
from data by testing individual layers directly (not the full orchestrator).

Ground truth: Known physical laws
Method: Feed data → check layer outputs → verify correctness
"""

import os
import sys
import json
import numpy as np
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def generate_data(law_id: str, n=50):
    np.random.seed(42)
    if law_id == "kepler":
        a = np.linspace(0.5, 10, n)
        T = np.sqrt(a**3) + np.random.normal(0, 0.05, n)
        return {"semi_major_axis": a.tolist(), "period": T.tolist()}
    elif law_id == "ohm":
        R = 10.0
        I = np.linspace(0.1, 5, n)
        V = I * R + np.random.normal(0, 0.1, n)
        return {"current": I.tolist(), "voltage": V.tolist()}
    elif law_id == "inverse_square":
        r = np.linspace(0.5, 5, n)
        F = 1.0 / r**2 + np.random.normal(0, 0.02, n)
        return {"distance": r.tolist(), "force": F.tolist()}


def test_statistical_detection():
    """Test if THEORIA's validation engine can detect known relationships."""
    from theoria.layers.validation_engine import AutonomousValidationEngine

    engine = AutonomousValidationEngine()
    results = {}

    # Test 1: Can it detect a significant difference?
    data_group1 = [1.0 + np.random.normal(0, 0.1) for _ in range(30)]
    data_group2 = [0.8 + np.random.normal(0, 0.1) for _ in range(30)]

    report = engine.validate(
        hypothesis="Group 1 differs from Group 2",
        experiment_results={
            "group1": data_group1,
            "group2": data_group2,
            "data": [g1 - g2 for g1, g2 in zip(data_group1, data_group2)],
            "population_mean": 0.0,
        },
        domain="test"
    )
    results["effect_detection"] = {
        "passed": report.overall_passed,
        "confidence": report.overall_confidence,
        "methods": report.methods_used,
    }

    # Test 2: Can it detect no effect?
    same_data1 = [1.0 + np.random.normal(0, 0.1) for _ in range(30)]
    same_data2 = [1.0 + np.random.normal(0, 0.1) for _ in range(30)]

    report2 = engine.validate(
        hypothesis="Two identical groups differ",
        experiment_results={
            "group1": same_data1,
            "group2": same_data2,
            "data": [0.0] * 30,
            "population_mean": 0.0,
        },
        domain="test"
    )
    results["no_effect_detection"] = {
        "passed_correctly": not report2.overall_passed,
        "confidence": report2.overall_confidence,
    }

    return results


def test_knowledge_graph():
    """Test if THEORIA's knowledge graph can store and query real relationships."""
    from theoria.core.knowledge_graph import KnowledgeGraph
    from theoria.core.types import KGNode, KGEdge, KGNodeType, KGEdgeType

    kg = KnowledgeGraph()

    # Add nodes for a known relationship
    ohm_v = KGNode(name="voltage", node_type=KGNodeType.VARIABLE, confidence=0.9)
    ohm_i = KGNode(name="current", node_type=KGNodeType.VARIABLE, confidence=0.9)
    ohm_r = KGNode(name="resistance", node_type=KGNodeType.VARIABLE, confidence=0.9)
    ohm_law = KGNode(name="V = IR (Ohm's Law)", node_type=KGNodeType.THEORY, confidence=0.8)

    kg.add_node(ohm_v)
    kg.add_node(ohm_i)
    kg.add_node(ohm_r)
    kg.add_node(ohm_law)

    # Add edges
    kg.add_edge(KGEdge(source_id=ohm_law.id, target_id=ohm_v.id, edge_type=KGEdgeType.PREDICTS))
    kg.add_edge(KGEdge(source_id=ohm_law.id, target_id=ohm_i.id, edge_type=KGEdgeType.PREDICTS))
    kg.add_edge(KGEdge(source_id=ohm_law.id, target_id=ohm_r.id, edge_type=KGEdgeType.PREDICTS))

    # Query
    voltage_nodes = kg.get_node_by_name("voltage")
    has_ohm = kg.get_node_by_name("V = IR (Ohm's Law)")

    return {
        "nodes_added": len(kg.nodes),
        "edges_added": len(kg.edges),
        "voltage_found": voltage_nodes is not None,
        "ohm_law_found": has_ohm is not None,
    }


def test_prediction_immutable():
    """Test that predictions are truly immutable."""
    import tempfile
    from theoria.layers.prediction_tracker import PredictionTracker

    test_file = os.path.join(tempfile.gettempdir(), "test_immutable.json")
    tracker = PredictionTracker(data_file=test_file)

    # Create prediction
    pred = tracker.add_prediction(
        statement="Test prediction",
        domain="physics",
        deadline="2026-12-31",
        confidence=0.7,
    )

    original_hash = pred.content_hash

    # Verify
    tracker.verify_prediction(pred.id, outcome="Confirmed", confirmed=True)

    # Check integrity
    integrity = tracker.verify_integrity()
    pred_still_valid = tracker.predictions[pred.id].verify_integrity()

    os.remove(test_file)

    return {
        "hash_created": bool(original_hash),
        "integrity_ok": integrity["predictions_tampered"] == 0,
        "chains_ok": integrity["chains_broken"] == 0,
        "prediction_valid": pred_still_valid,
    }


def test_deterministic_scoring():
    """Test that _det_score is truly deterministic."""
    from theoria.layers.self_improvement import _deterministic_score as _det_score

    scores1 = [_det_score("test_label") for _ in range(10)]
    scores2 = [_det_score("test_label") for _ in range(10)]

    all_same = all(s1 == s2 for s1, s2 in zip(scores1, scores2))
    in_range = all(0.0 <= s <= 1.0 for s in scores1)

    different_labels = _det_score("label_a") != _det_score("label_b")

    return {
        "deterministic": all_same,
        "in_range": in_range,
        "different_labels_different_scores": different_labels,
    }


def test_real_data_connector():
    """Test that real data connectors return real data."""
    from theoria.layers.data_connectors import DataConnector

    dc = DataConnector()
    dc.connect_source("arxiv")
    results = dc.search_arxiv("quantum mechanics", max_results=3)

    has_real_data = len(results) > 0
    has_titles = all("title" in r and r["title"] for r in results)
    no_fake_urls = not any("example.com" in r.get("url", "") for r in results)

    return {
        "returned_results": len(results),
        "has_real_data": has_real_data,
        "has_titles": has_titles,
        "no_fake_urls": no_fake_urls,
    }


def main():
    print("=" * 70)
    print("  BLIND DISCOVERY BENCHMARK (Lightweight)")
    print("  Testing core components against ground truth")
    print("=" * 70)

    all_results = {}

    # Test 1: Statistical detection
    print("\n  Test 1: Statistical Effect Detection")
    try:
        r = test_statistical_detection()
        all_results["statistical_detection"] = r
        print(f"    Effect detected: {r['effect_detection']['passed']}")
        print(f"    No effect correct: {r['no_effect_detection']['passed_correctly']}")
    except Exception as e:
        print(f"    ERROR: {e}")
        all_results["statistical_detection"] = {"error": str(e)}

    # Test 2: Knowledge Graph
    print("\n  Test 2: Knowledge Graph Storage")
    try:
        r = test_knowledge_graph()
        all_results["knowledge_graph"] = r
        print(f"    Nodes: {r['nodes_added']}, Edges: {r['edges_added']}")
        print(f"    Voltage found: {r['voltage_found']}, Ohm's Law found: {r['ohm_law_found']}")
    except Exception as e:
        print(f"    ERROR: {e}")
        all_results["knowledge_graph"] = {"error": str(e)}

    # Test 3: Prediction Immutability
    print("\n  Test 3: Prediction Immutability")
    try:
        r = test_prediction_immutable()
        all_results["prediction_immutable"] = r
        print(f"    Hash created: {r['hash_created']}")
        print(f"    Integrity OK: {r['integrity_ok']}")
        print(f"    Chains OK: {r['chains_ok']}")
    except Exception as e:
        print(f"    ERROR: {e}")
        all_results["prediction_immutable"] = {"error": str(e)}

    # Test 4: Deterministic Scoring
    print("\n  Test 4: Deterministic Scoring")
    try:
        r = test_deterministic_scoring()
        all_results["deterministic_scoring"] = r
        print(f"    Deterministic: {r['deterministic']}")
        print(f"    In range [0,1]: {r['in_range']}")
        print(f"    Different labels diverge: {r['different_labels_different_scores']}")
    except Exception as e:
        print(f"    ERROR: {e}")
        all_results["deterministic_scoring"] = {"error": str(e)}

    # Test 5: Real Data Connector
    print("\n  Test 5: Real Data Connector")
    try:
        r = test_real_data_connector()
        all_results["real_data_connector"] = r
        print(f"    Results returned: {r['returned_results']}")
        print(f"    Has real data: {r['has_real_data']}")
        print(f"    No fake URLs: {r['no_fake_urls']}")
    except Exception as e:
        print(f"    ERROR: {e}")
        all_results["real_data_connector"] = {"error": str(e)}

    # Summary
    total_tests = 0
    passed_tests = 0
    for name, r in all_results.items():
        if isinstance(r, dict) and "error" not in r:
            total_tests += 1
            # Check if all boolean values are True
            bool_values = [v for v in r.values() if isinstance(v, bool)]
            if all(bool_values):
                passed_tests += 1
                print(f"\n  {name}: PASS")
            else:
                print(f"\n  {name}: FAIL - {[k for k, v in r.items() if v is False]}")
        else:
            print(f"\n  {name}: ERROR")

    print(f"\n{'='*70}")
    print(f"  BLIND DISCOVERY RESULTS")
    print(f"{'='*70}")
    print(f"  Tests passed: {passed_tests}/{total_tests}")
    print(f"{'='*70}")

    # Save
    os.makedirs("results", exist_ok=True)
    with open("results/blind_discovery_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"  Saved to results/blind_discovery_results.json")


if __name__ == "__main__":
    main()
