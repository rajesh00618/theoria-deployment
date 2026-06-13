from __future__ import annotations

import uuid
import random
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


class IntelligenceEvaluator:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.evaluations: List[IntelligenceEvaluation] = []
        self.metrics = ["adaptability", "learning_speed", "problem_solving", "creativity", "autonomy", "robustness"]
        self.prev_scores: Dict[str, float] = {}
        self.cycle_count = 0

    def evaluate(self, metric: str) -> IntelligenceEvaluation:
        score = random.uniform(0.3, 0.95)
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

    def get_overall_score(self) -> float:
        recent = {}
        for e in self.evaluations:
            recent[e.evaluation_type] = e.score
        if not recent:
            return 0.0
        return sum(recent.values()) / len(recent)

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
