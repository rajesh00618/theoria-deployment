from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import IntelligenceEvaluation


@dataclass
class EvaluationResult:
    evaluations_completed: int = 0
    adaptability_score: float = 0.0
    learning_speed_score: float = 0.0
    problem_solving_score: float = 0.0
    creativity_score: float = 0.0
    autonomy_score: float = 0.0
    robustness_score: float = 0.0
    overall_score: float = 0.0
    improvement: float = 0.0


METRIC_WEIGHTS = {
    "adaptability": 0.20,
    "learning_speed": 0.18,
    "problem_solving": 0.22,
    "creativity": 0.15,
    "autonomy": 0.12,
    "robustness": 0.13,
}


class IntelligenceEvaluator:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.evaluations: List[IntelligenceEvaluation] = []
        self.metrics = ["adaptability", "learning_speed", "problem_solving", "creativity", "autonomy", "robustness"]
        self.prev_scores: Dict[str, float] = {}
        self.cycle_count = 0
        self._system_context: Dict[str, Any] = {}

    def set_system_context(self, context: Dict[str, Any]) -> None:
        """Provide actual system state for evaluation."""
        self._system_context.update(context)

    def evaluate(self, metric: str) -> IntelligenceEvaluation:
        score = self._compute_metric_score(metric)
        prev = self.prev_scores.get(metric, 0.0)
        evaluation = IntelligenceEvaluation(
            evaluation_type=metric, score=score,
            benchmark_reference=f"B7{self.metrics.index(metric) + 1}",
            details={"raw_score": score, "normalized": score},
            improvement_since_last=score - prev,
        )
        self.evaluations.append(evaluation)
        self.prev_scores[metric] = score
        return evaluation

    def _compute_metric_score(self, metric: str) -> float:
        if metric == "adaptability":
            return self._score_adaptability()
        elif metric == "learning_speed":
            return self._score_learning_speed()
        elif metric == "problem_solving":
            return self._score_problem_solving()
        elif metric == "creativity":
            return self._score_creativity()
        elif metric == "autonomy":
            return self._score_autonomy()
        elif metric == "robustness":
            return self._score_robustness()
        return 0.0

    def _score_adaptability(self) -> float:
        theories_revised = self._system_context.get("theories_revised", 0)
        strategies_tried = self._system_context.get("strategies_used", 0)
        base = min(0.95, 0.3 + theories_revised * 0.05 + strategies_tried * 0.03)
        return max(0.1, min(0.95, base))

    def _score_learning_speed(self) -> float:
        cycles = self._system_context.get("cycle_count", self.cycle_count)
        discoveries = self._system_context.get("discoveries", 0)
        base = min(0.95, 0.2 + discoveries * 0.1 + cycles * 0.01)
        return max(0.1, min(0.95, base))

    def _score_problem_solving(self) -> float:
        puzzles_solved = self._system_context.get("puzzles_solved", 0)
        total_puzzles = max(1, self._system_context.get("total_puzzles", 1))
        accuracy = puzzles_solved / total_puzzles
        base = 0.3 + accuracy * 0.6
        return max(0.1, min(0.95, base))

    def _score_creativity(self) -> float:
        novel_theories = self._system_context.get("novel_theories", 0)
        total_theories = max(1, self._system_context.get("total_theories", 1))
        novelty_ratio = novel_theories / total_theories
        base = 0.2 + novelty_ratio * 0.7
        return max(0.1, min(0.95, base))

    def _score_autonomy(self) -> float:
        human_interventions = self._system_context.get("human_interventions", 0)
        cycles = max(1, self._system_context.get("cycle_count", 1))
        autonomy_ratio = 1.0 - min(1.0, human_interventions / cycles)
        base = 0.2 + autonomy_ratio * 0.7
        return max(0.1, min(0.95, base))

    def _score_robustness(self) -> float:
        adversarial_survived = self._system_context.get("adversarial_survived", 0)
        adversarial_total = max(1, self._system_context.get("adversarial_total", 1))
        survival_rate = adversarial_survived / adversarial_total
        base = 0.3 + survival_rate * 0.6
        return max(0.1, min(0.95, base))

    def get_overall_score(self) -> float:
        recent = {}
        for e in self.evaluations:
            recent[e.evaluation_type] = e.score
        if not recent:
            return 0.0
        weighted = sum(recent.get(m, 0) * w for m, w in METRIC_WEIGHTS.items())
        return weighted

    def get_improvement(self) -> float:
        if len(self.evaluations) < len(self.metrics) * 2:
            return 0.0
        half = len(self.evaluations) // 2
        first_half = [e.score for e in self.evaluations[:half]]
        second_half = [e.score for e in self.evaluations[half:]]
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        return avg_second - avg_first

    def run_cycle(self) -> EvaluationResult:
        self.cycle_count += 1
        self._system_context["cycle_count"] = self.cycle_count
        result = EvaluationResult()

        for metric in self.metrics:
            self.evaluate(metric)
            result.evaluations_completed += 1

        recent = {}
        for e in self.evaluations[-len(self.metrics):]:
            recent[e.evaluation_type] = e.score

        result.adaptability_score = recent.get("adaptability", 0.0)
        result.learning_speed_score = recent.get("learning_speed", 0.0)
        result.problem_solving_score = recent.get("problem_solving", 0.0)
        result.creativity_score = recent.get("creativity", 0.0)
        result.autonomy_score = recent.get("autonomy", 0.0)
        result.robustness_score = recent.get("robustness", 0.0)
        result.overall_score = self.get_overall_score()
        result.improvement = self.get_improvement()
        return result
