"""
Phase 3: Intervention Engine (P3.2).

Generates interventions, simulates counterfactuals, evaluates experiment designs.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import defaultdict

from theoria.core.types import (
    Theory, Intervention, DisciplineMode, CounterfactualOutcome,
    ExperimentDesign, ExperimentResult, Concept,
)


class InterventionGenerator:
    """
    Generates concrete intervention plans for testing theories.
    Input: Theory / Hypothesis
    Output: Intervention designs with target variables, manipulation, cost.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.interventions: Dict[str, Intervention] = {}
        self.history: List[Dict[str, Any]] = []

    def generate_from_theory(self, theory: Theory) -> Intervention:
        target_vars = [v for v in theory.reference_class
                       if len(v) > 1][:3]
        if theory.intervention:
            target_vars = theory.intervention.target_variables or target_vars

        manipulation = {}
        for var in target_vars:
            manipulation[var] = {"operation": "modulate", "range": [0.0, 1.0]}

        expected = {}
        for claim in theory.core_claims:
            expected[claim.statement[:50]] = 0.7

        intervention = Intervention(
            name=f"Intervention: {theory.name}",
            description=f"Test {theory.name} via {'/'.join(target_vars)} manipulation",
            target_variables=target_vars,
            manipulation=manipulation,
            expected_outcomes=expected,
            realizability=self._estimate_realizability(theory),
            cost_estimate=self._estimate_cost(theory, target_vars),
            severity_potential=self._estimate_severity(theory),
            mode=DisciplineMode.EMPIRICAL_INTERVENTION,
        )

        self.interventions[intervention.id] = intervention
        self.history.append({
            "intervention_id": intervention.id,
            "theory_id": theory.id,
            "timestamp": time.time(),
        })
        return intervention

    def _estimate_realizability(self, theory: Theory) -> float:
        score = 0.6
        if theory.intervention:
            score += 0.2
        if theory.reference_class:
            score += 0.1
        if theory.domain.parameter_ranges:
            score += 0.1
        return min(1.0, max(0.1, score))

    def _estimate_cost(self, theory: Theory, vars: List[str]) -> float:
        base = 100.0
        var_cost = len(vars) * 50.0
        return base + var_cost

    def _estimate_severity(self, theory: Theory) -> float:
        if theory.posterior > 0.8:
            return 0.8
        elif theory.posterior > 0.5:
            return 0.5
        else:
            return 0.3

    def optimize_intervention(self, intervention: Intervention,
                              budget: float = 1000.0) -> Intervention:
        n_vars = len(intervention.target_variables)
        cost_per_var = intervention.cost_estimate / max(n_vars, 1)

        if intervention.cost_estimate > budget:
            n_keep = max(1, int(budget / max(cost_per_var, 1)))
            intervention.target_variables = intervention.target_variables[:n_keep]
            intervention.manipulation = {
                k: v for k, v in intervention.manipulation.items()
                if k in intervention.target_variables
            }
            intervention.cost_estimate = n_keep * cost_per_var
            intervention.realizability *= 1.2

        return intervention

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_interventions": len(self.interventions),
            "avg_realizability": (
                np.mean([i.realizability for i in self.interventions.values()])
                if self.interventions else 0
            ),
            "avg_cost": (
                np.mean([i.cost_estimate for i in self.interventions.values()])
                if self.interventions else 0
            ),
        }


class CounterfactualSimulator:
    """
    Simulates counterfactual outcomes given a theory and intervention.
    "What would happen if we changed X?"
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.counterfactuals: List[CounterfactualOutcome] = []

    def simulate(self, theory: Theory, intervention: Intervention,
                 scenario: str, n_samples: int = 100) -> CounterfactualOutcome:
        predicted = {}
        for var in intervention.target_variables:
            base = np.random.normal(0.5, 0.2)
            effect = theory.posterior * 0.3
            predicted[var] = float(base + effect)

        outcome = CounterfactualOutcome(
            scenario=scenario,
            condition=f"Intervene on {', '.join(intervention.target_variables)}",
            predicted_outcome=predicted,
            confidence=theory.posterior * intervention.realizability,
            mechanism_description=self._describe_mechanism(theory, intervention),
        )

        self.counterfactuals.append(outcome)
        return outcome

    def _describe_mechanism(self, theory: Theory, intervention: Intervention) -> str:
        parts = []
        for claim in theory.core_claims[:2]:
            parts.append(claim.statement[:80])
        parts.append(f"via {', '.join(intervention.target_variables[:3])} manipulation")
        return "; ".join(parts)

    def multi_scenario(self, theory: Theory, intervention: Intervention,
                       scenarios: List[str]) -> List[CounterfactualOutcome]:
        return [self.simulate(theory, intervention, s) for s in scenarios]

    def compare_outcomes(self, outcomes: List[CounterfactualOutcome]) -> Dict[str, Any]:
        if not outcomes:
            return {}
        all_vars = set()
        for o in outcomes:
            all_vars.update(o.predicted_outcome.keys())

        comparisons = {}
        for var in all_vars:
            vals = [o.predicted_outcome.get(var, 0) for o in outcomes]
            comparisons[var] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "range": (float(np.min(vals)), float(np.max(vals))),
            }
        return comparisons

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_counterfactuals": len(self.counterfactuals),
        }


class ExperimentEvaluator:
    """
    Evaluates experiment results against theoretical predictions.
    Determines whether evidence supports or contradicts the hypothesis.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.evaluations: List[Dict[str, Any]] = []

    def evaluate(self, design: ExperimentDesign, result: ExperimentResult) -> Dict[str, Any]:
        evaluation = {
            "design_id": design.id,
            "result_id": result.id,
            "hypothesis_id": design.hypothesis_id,
            "supports_hypothesis": result.supports_hypothesis,
            "contradicts_hypothesis": result.contradicts_hypothesis,
            "inconclusive": result.inconclusive,
            "effect_size": result.effect_size,
            "p_value": result.p_value,
            "bayes_factor": result.bayes_factor,
            "power_achieved": result.effect_size > 0.3,
            "quality_score": 0.0,
            "issues": [],
            "recommendation": "",
            "timestamp": time.time(),
        }

        quality = 0.5
        issues = []

        if result.p_value < 0.05:
            quality += 0.2
        if result.effect_size > 0.5:
            quality += 0.15
        if result.bayes_factor > 3:
            quality += 0.15
        if len(result.trials) < 5:
            issues.append("Low number of trials")
            quality -= 0.1
        if result.inconclusive:
            issues.append("Inconclusive result - may need more power")
            quality -= 0.1

        evaluation["quality_score"] = float(min(1.0, max(0.0, quality)))
        evaluation["issues"] = issues

        if result.supports_hypothesis and quality > 0.5:
            evaluation["recommendation"] = "Hypothesis supported - consider replication with different methods"
        elif result.contradicts_hypothesis and quality > 0.5:
            evaluation["recommendation"] = "Hypothesis contradicted - consider modification or alternative"
        else:
            evaluation["recommendation"] = "Insufficient evidence - increase sample size or refine design"

        self.evaluations.append(evaluation)
        return evaluation

    def compare_theories(self, results: List[ExperimentResult],
                         theories: List[Theory]) -> Dict[str, Any]:
        theory_scores = {}
        for t in theories:
            relevant = [r for r in results if r.hypothesis_id == t.id]
            if relevant:
                support = sum(1 for r in relevant if r.supports_hypothesis)
                contradict = sum(1 for r in relevant if r.contradicts_hypothesis)
                theory_scores[t.id] = {
                    "theory_name": t.name,
                    "support_count": support,
                    "contradict_count": contradict,
                    "total_tests": len(relevant),
                    "net_support": support - contradict,
                }
        return {"comparisons": theory_scores}

    def get_summary(self) -> Dict[str, Any]:
        if not self.evaluations:
            return {"total_evaluations": 0}
        supported = sum(1 for e in self.evaluations if e["supports_hypothesis"])
        contradicted = sum(1 for e in self.evaluations if e["contradicts_hypothesis"])
        inconclusive = sum(1 for e in self.evaluations if e["inconclusive"])
        return {
            "total_evaluations": len(self.evaluations),
            "supported": supported,
            "contradicted": contradicted,
            "inconclusive": inconclusive,
            "avg_quality": float(np.mean([e["quality_score"] for e in self.evaluations])),
        }
