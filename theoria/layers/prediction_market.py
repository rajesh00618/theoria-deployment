"""
Phase 4: Prediction Market (P4.7).

Every theory must make predictions about future observations,
experiments, and discoveries. Tracks accuracy, calibration, and confidence.
Trust earned through prediction success.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import MarketPrediction, Theory, ExperimentResult


class PredictionMarket:
    """
    Market-based prediction tracking. Every theory predicts.
    Accuracy, calibration, and confidence are tracked over time.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.predictions: Dict[str, MarketPrediction] = {}
        self.resolved_predictions: List[MarketPrediction] = []

    def register_prediction(self, theory: Theory, description: str,
                            predicted_value: float,
                            confidence: float = 0.5) -> MarketPrediction:
        pred = MarketPrediction(
            theory_id=theory.id,
            description=description,
            predicted_value=predicted_value,
            confidence=min(max(confidence, 0.0), 1.0),
        )
        self.predictions[pred.id] = pred
        return pred

    def resolve_prediction(self, prediction_id: str,
                           actual_value: float) -> Optional[MarketPrediction]:
        pred = self.predictions.get(prediction_id)
        if not pred:
            return None
        pred.actual_value = actual_value
        pred.error = abs(pred.predicted_value - actual_value)
        pred.resolved = True
        self.resolved_predictions.append(pred)
        return pred

    def accuracy(self) -> float:
        resolved = [p for p in self.predictions.values() if p.resolved]
        if not resolved:
            return 0.5
        errors = [min(p.error / max(abs(p.actual_value or 1), 0.01), 2.0) for p in resolved]
        normalized = [max(0.0, 1.0 - e) for e in errors]
        return float(np.mean(normalized)) if normalized else 0.5

    def calibration(self) -> float:
        resolved = [p for p in self.predictions.values() if p.resolved]
        if not resolved:
            return 0.5
        well_calibrated = sum(1 for p in resolved
                              if p.error is not None and p.error < (1 - p.confidence) * 2)
        return well_calibrated / max(len(resolved), 1)

    def get_predictions_for_theory(self, theory_id: str) -> List[MarketPrediction]:
        return [p for p in self.predictions.values() if p.theory_id == theory_id]

    def get_summary(self) -> Dict[str, Any]:
        total = len(self.predictions)
        resolved = sum(1 for p in self.predictions.values() if p.resolved)
        return {
            "total_predictions": total,
            "resolved": resolved,
            "pending": total - resolved,
            "accuracy": self.accuracy(),
            "calibration": self.calibration(),
        }
