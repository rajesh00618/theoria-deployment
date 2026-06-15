from __future__ import annotations

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
        self._system_context: Dict[str, Any] = {}

    def set_system_context(self, context: Dict[str, Any]) -> None:
        """Provide actual system state for self-assessment."""
        self._system_context.update(context)

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
            actual = self._compute_actual_score(cap)
            predicted = self._compute_predicted_score(cap, actual)
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

    def _compute_actual_score(self, capability: str) -> float:
        if capability == "reasoning":
            theories = self._system_context.get("theories_proposed", 0)
            falsified = self._system_context.get("theories_falsified", 0)
            if theories == 0:
                return 0.3
            survival_rate = 1.0 - (falsified / max(1, theories))
            return max(0.1, min(0.95, 0.3 + survival_rate * 0.6))

        elif capability == "memory":
            stored = self._system_context.get("memory_entries", 0)
            recalled = self._system_context.get("memory_recalls", 0)
            if stored == 0:
                return 0.3
            recall_rate = recalled / max(1, stored)
            return max(0.1, min(0.95, 0.3 + recall_rate * 0.6))

        elif capability == "planning":
            plans = self._system_context.get("plans_executed", 0)
            completed = self._system_context.get("plans_completed", 0)
            if plans == 0:
                return 0.3
            completion_rate = completed / plans
            return max(0.1, min(0.95, 0.3 + completion_rate * 0.6))

        elif capability == "creativity":
            novel = self._system_context.get("novel_hypotheses", 0)
            total = max(1, self._system_context.get("total_hypotheses", 1))
            novelty_ratio = novel / total
            return max(0.1, min(0.95, 0.2 + novelty_ratio * 0.7))

        elif capability == "collaboration":
            interactions = self._system_context.get("agent_interactions", 0)
            successful = self._system_context.get("successful_interactions", 0)
            if interactions == 0:
                return 0.3
            success_rate = successful / interactions
            return max(0.1, min(0.95, 0.3 + success_rate * 0.6))

        elif capability == "tool_use":
            tools_used = self._system_context.get("tools_used", 0)
            tools_available = max(1, self._system_context.get("tools_available", 1))
            utilization = tools_used / tools_available
            return max(0.1, min(0.95, 0.3 + utilization * 0.6))

        elif capability == "world_modeling":
            accuracy = self._system_context.get("world_model_accuracy", 0.5)
            return max(0.1, min(0.95, accuracy))

        elif capability == "self_awareness":
            calibration = self._system_context.get("self_calibration_error", 0.3)
            return max(0.1, min(0.95, 1.0 - calibration))

        return 0.5

    def _compute_predicted_score(self, capability: str, actual: float) -> float:
        error_margin = self._system_context.get("prediction_error_margin", 0.1)
        predicted = actual + error_margin
        return max(0.0, min(1.0, predicted))
