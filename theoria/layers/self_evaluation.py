from __future__ import annotations

import random
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import CapabilityAssessment


@dataclass
class EvaluationResult:
    capabilities_assessed: int = 0
    strengths_identified: int = 0
    weaknesses_detected: int = 0
    calibration_score: float = 0.0
    overall_confidence: float = 0.0
    improvement_suggestions: List[str] = field(default_factory=list)


class SelfEvaluation:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.assessments: List[CapabilityAssessment] = []
        self.calibration_target = (getattr(config, "calibration_target", 0.9)
                                   if config else 0.9)
        self.cycle_count = 0

    def assess_capability(self, capability_name: str,
                          actual_score: float,
                          predicted_score: float) -> CapabilityAssessment:
        assessment = CapabilityAssessment(
            capability_name=capability_name,
            self_assessed_score=predicted_score,
            actual_performance=actual_score,
            calibration_error=abs(predicted_score - actual_score),
        )
        self.assessments.append(assessment)
        return assessment

    def detect_weaknesses(self) -> List[CapabilityAssessment]:
        return [a for a in self.assessments if a.actual_performance < 0.5]

    def run_cycle(self) -> EvaluationResult:
        self.cycle_count += 1
        result = EvaluationResult()

        capabilities = [
            "reasoning", "memory", "planning", "creativity",
            "collaboration", "tool_use", "world_modeling", "self_awareness"
        ]
        for cap in capabilities:
            actual = random.uniform(0.3, 0.95)
            predicted = actual + random.uniform(-0.2, 0.2)
            predicted = max(0.0, min(1.0, predicted))
            self.assess_capability(capability_name=cap, actual_score=actual,
                                  predicted_score=predicted)
            result.capabilities_assessed += 1

        weaknesses = self.detect_weaknesses()
        result.weaknesses_detected = len(weaknesses)
        result.strengths_identified = result.capabilities_assessed - result.weaknesses_detected

        recent = self.assessments[-len(capabilities):]
        calibration_errors = [a.calibration_error for a in recent]
        if calibration_errors:
            result.calibration_score = 1.0 - (sum(calibration_errors) / len(calibration_errors))
            result.calibration_score = max(0.0, min(1.0, result.calibration_score))

        if recent:
            result.overall_confidence = sum(a.self_assessed_score for a in recent) / len(recent)

        for w in weaknesses:
            result.improvement_suggestions.append(
                f"Improve {w.capability_name} (current: {w.actual_performance:.2f})")
        return result
