"""
Phase 3: Scientific Prediction Engine (P3.6).

Makes falsifiable predictions before seeing the answer.
Stronger than rediscovery — true predictive science.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import (
    Theory, ScientificPrediction, ExperimentResult,
)


class PredictionEngine:
    """
    Extracts falsifiable predictions from theories and tracks their accuracy.
    Benchmark: Can THEORIA predict something before seeing the answer?
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.predictions: Dict[str, ScientificPrediction] = {}
        self.calibration_history: List[Dict[str, Any]] = []

    def extract_predictions(self, theory: Theory) -> List[ScientificPrediction]:
        predictions = []
        for i, claim in enumerate(theory.core_claims):
            pred = ScientificPrediction(
                description=f"Prediction from {theory.name}: {claim.statement[:80]}",
                target_variable=f"claim_{i}_outcome",
                predicted_value=float(theory.posterior),
                confidence_interval=(float(max(0, theory.posterior - 0.2)),
                                     float(min(1, theory.posterior + 0.2))),
                prediction_interval=(0.0, 1.0),
                theory_id=theory.id,
                domain=theory.domain.conditions[0] if theory.domain.conditions else "general",
                time_horizon=f"{10 * (i+1)}_cycles",
            )
            predictions.append(pred)
            self.predictions[pred.id] = pred

        return predictions

    def predict_outcome(self, theory: Theory, design: Any) -> ScientificPrediction:
        n_trials = getattr(design, 'num_trials', 10)
        effect = theory.posterior * 0.5

        pred = ScientificPrediction(
            description=f"Predicted outcome of testing {theory.name}",
            target_variable="experimental_outcome",
            predicted_value=float(effect),
            confidence_interval=(float(max(-1, effect - 0.3)), float(min(1, effect + 0.3))),
            prediction_interval=(float(max(-2, effect - 0.5)), float(min(2, effect + 0.5))),
            theory_id=theory.id,
            domain=theory.domain.conditions[0] if theory.domain.conditions else "general",
            time_horizon=f"{n_trials}_trials",
        )
        self.predictions[pred.id] = pred
        return pred

    def record_actual(self, prediction_id: str, actual_value: float) -> Dict[str, Any]:
        pred = self.predictions.get(prediction_id)
        if not pred:
            return {"error": "Prediction not found"}

        pred.actual_value = actual_value
        pred.error = abs(pred.predicted_value - actual_value)
        pred.verified = True

        within_ci = (pred.confidence_interval[0] <= actual_value <= pred.confidence_interval[1])
        within_pi = (pred.prediction_interval[0] <= actual_value <= pred.prediction_interval[1])

        entry = {
            "prediction_id": prediction_id,
            "predicted": pred.predicted_value,
            "actual": actual_value,
            "error": pred.error,
            "within_ci": within_ci,
            "within_pi": within_pi,
            "timestamp": time.time(),
        }
        self.calibration_history.append(entry)
        return entry

    def evaluate_from_experiment(self, prediction: ScientificPrediction,
                                 result: ExperimentResult) -> Dict[str, Any]:
        actual = result.mean_raw if result.mean_raw != 0.0 else result.effect_size
        return self.record_actual(prediction.id, actual)

    def calibration_score(self) -> float:
        if not self.calibration_history:
            return 0.5

        within_ci = sum(1 for e in self.calibration_history if e.get("within_ci", False))
        total = len(self.calibration_history)
        ci_based = float(within_ci / max(total, 1))

        errors = []
        for e in self.calibration_history:
            actual = abs(e.get("actual", 1.0))
            err = abs(e.get("error", 0))
            normalized = err / max(actual, 0.01)
            errors.append(min(normalized, 2.0))
        mean_norm_error = float(np.mean(errors)) if errors else 1.0
        error_based = max(0.0, min(1.0, 1.0 - mean_norm_error))

        return (ci_based + error_based) / 2.0

    def mean_prediction_error(self) -> float:
        errors = [e.get("error", 1.0) for e in self.calibration_history]
        return float(np.mean(errors)) if errors else 1.0

    def get_predictions_for_theory(self, theory_id: str) -> List[ScientificPrediction]:
        return [p for p in self.predictions.values() if p.theory_id == theory_id]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_predictions": len(self.predictions),
            "verified": sum(1 for p in self.predictions.values() if p.verified),
            "pending": sum(1 for p in self.predictions.values() if not p.verified),
            "calibration": self.calibration_score(),
            "mean_error": self.mean_prediction_error(),
        }
