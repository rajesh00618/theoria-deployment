#!/usr/bin/env bash
# THEORIA Reproducibility Runner
set -e

echo "======================================================================"
echo "  THEORIA: Reproducibility Runner"
echo "======================================================================"

# Check Python
python3 --version || { echo "Python3 required"; exit 1; }

# Install dependencies
echo ""
echo "[1/4] Installing dependencies..."
pip3 install -r requirements.txt

# Run demo
echo ""
echo "[2/4] Running B1 benchmark..."
python3 demo.py

# Run full cycle
echo ""
echo "[3/4] Running full discovery-falsification-revision cycle..."
python3 demo_full_cycle.py

# Run validation suite
echo ""
echo "[4/4] Running comprehensive validation..."
python3 validation.py

echo ""
echo "======================================================================"
echo "  All benchmarks complete."
echo "  See benchmark_results.csv and THEORIA_VALIDATION_REPORT.txt"
echo "======================================================================"
