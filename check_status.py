import os, json

# Check predictions
if os.path.exists('results/prediction_registry.json'):
    with open('results/prediction_registry.json') as f:
        preds = json.load(f)
    print(f"Predictions: {len(preds.get('predictions', {}))} frozen")
else:
    print("No predictions found")

# Check results
if os.path.exists('results/rp001_final.json'):
    with open('results/rp001_final.json') as f:
        results = json.load(f)
    print(f"RP-001: p={results['test_results']['student_t']['p']:.6f}")
    print(f"Hash: {results['result_hash']}")
else:
    print("No RP-001 results")

# Check data
if os.path.exists('data/robustness_fast'):
    n = len([f for f in os.listdir('data/robustness_fast') if f.endswith('.json')])
    print(f"Data: {n} articles")
