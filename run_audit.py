#!/usr/bin/env python3
"""Quick audit runner - captures validation results."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validation import run_all_validations

results = run_all_validations()
summary = results.get("_summary", {})

print(f"\n{'='*60}")
print(f"  AUDIT SCORE")
print(f"{'='*60}")
print(f"  Passed: {summary.get('passed_count',0)}/{summary.get('total_count',0)}")
print(f"  Rate:   {summary.get('pass_rate',0):.1%}")
print(f"{'='*60}")

# Per-item breakdown
for key in ["A","B","C","D","E","F","G","H","I","R","S","T","U","V","W","X","Y"]:
    r = results.get(key, {})
    status = "PASS" if r.get("passed", False) else "FAIL"
    print(f"  {key}: {status}")
