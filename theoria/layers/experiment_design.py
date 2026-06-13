"""
Phase 3: Experiment Design Engine (P3.1).

Transforms hypotheses into testable experiment designs:
- Variables, Controls, Interventions, Expected Outcomes, Measurements
"""

from __future__ import annotations

import math
import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import (
    Theory, CandidateHypothesis, ExperimentDesign, VariableSpec,
    ControlSpec, ExperimentResult, TrialResult,
)


class ExperimentPlanner:
    """
    Designs experiments from hypotheses.
    Input: Hypothesis / Theory
    Output: Full experiment design with variables, controls, protocol.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.designs: Dict[str, ExperimentDesign] = {}
        self.results: Dict[str, ExperimentResult] = {}
        self.design_history: List[Dict[str, Any]] = []

    def design_from_hypothesis(self, hypothesis: CandidateHypothesis,
                               domain: str = "physics") -> ExperimentDesign:
        design = ExperimentDesign(
            name=f"Exp: {hypothesis.description[:60]}",
            hypothesis_id=hypothesis.id,
            hypothesis_text=hypothesis.description,
        )

        design.independent_variables = self._extract_independent_vars(hypothesis)
        design.dependent_variables = self._extract_dependent_vars(hypothesis)
        design.controls = self._design_controls(hypothesis, domain)
        design.intervention_description = self._build_intervention(hypothesis)
        design.expected_outcomes = self._generate_expected_outcomes(hypothesis)
        design.measurement_plan = self._build_measurement_plan(design)
        design.protocol = self._build_protocol(design)

        design.feasibility = self._estimate_feasibility(design, domain)
        design.predicted_power = self._estimate_power(design)

        self.designs[design.id] = design
        self.design_history.append({
            "design_id": design.id,
            "hypothesis_id": hypothesis.id,
            "timestamp": time.time(),
        })
        return design

    def design_from_theory(self, theory: Theory, domain: str = "physics") -> ExperimentDesign:
        hypothesis_like = CandidateHypothesis(
            id=theory.id,
            description=f"{theory.name}: {'; '.join(c.statement for c in theory.core_claims)}",
            strategy_origin=None,
            concepts_used=theory.reference_class,
            explanatory_power=theory.posterior,
        )
        return self.design_from_hypothesis(hypothesis_like, domain)

    def _extract_independent_vars(self, hypothesis: CandidateHypothesis) -> List[VariableSpec]:
        # Extract manipulable variables from hypothesis text
        vars_found = []
        text_lower = hypothesis.description.lower()

        cause_keywords = ["causes", "increases", "decreases", "affects", "depends on",
                          "determined by", "function of", "proportional to",
                          "a -> b", "a causes b", "if a then b"]
        for kw in cause_keywords:
            if kw in text_lower:
                parts = text_lower.split(kw)
                if len(parts) >= 2:
                    for concept in hypothesis.concepts_used:
                        if concept.lower() in parts[0]:
                            vars_found.append(VariableSpec(
                                name=concept,
                                type="continuous",
                                manipulation=f"Vary {concept} systematically",
                            ))

        if not vars_found:
            for concept in hypothesis.concepts_used[:2]:
                vars_found.append(VariableSpec(
                    name=concept,
                    type="continuous",
                    manipulation=f"Manipulate {concept}",
                ))

        return vars_found[:3]

    def _extract_dependent_vars(self, hypothesis: CandidateHypothesis) -> List[str]:
        text_lower = hypothesis.description.lower()
        outcome_keywords = ["leads to", "results in", "produces", "causes",
                            "increases", "decreases", "measured by"]
        for kw in outcome_keywords:
            if kw in text_lower:
                parts = text_lower.split(kw)
                if len(parts) >= 2:
                    after = parts[1]
                    matched = [c for c in hypothesis.concepts_used if c.lower() in after]
                    if matched:
                        return matched[:3]
                    words = after.strip().split()
                    return [w for w in words if len(w) > 3][:3]
        return [f"outcome_{c}" for c in hypothesis.concepts_used[:2]]

    def _design_controls(self, hypothesis: CandidateHypothesis,
                         domain: str) -> List[ControlSpec]:
        controls = []
        if domain == "physics":
            controls.append(ControlSpec(variable="temperature", value=298.0,
                                        rationale="Thermal effects on measurement"))
            controls.append(ControlSpec(variable="pressure", value=1.0,
                                        rationale="Standard atmospheric conditions"))
        elif domain == "biology":
            controls.append(ControlSpec(variable="temperature", value=310.0,
                                        rationale="Physiological temperature"))
            controls.append(ControlSpec(variable="ph", value=7.4,
                                        rationale="Physiological pH"))
        else:
            controls.append(ControlSpec(variable="baseline", value=0.0,
                                        rationale="Baseline measurement"))
        return controls

    def _build_intervention(self, hypothesis: CandidateHypothesis) -> str:
        iv_names = [v.name for v in self._extract_independent_vars(hypothesis)]
        dv_names = self._extract_dependent_vars(hypothesis)
        if iv_names and dv_names:
            return f"Systematically manipulate {', '.join(iv_names)} and measure {', '.join(dv_names)}"
        return f"Controlled experiment testing: {hypothesis.description[:100]}"

    def _generate_expected_outcomes(self, hypothesis: CandidateHypothesis) -> List[str]:
        text = hypothesis.description.lower()
        outcomes = []
        if "increases" in text or "positive" in text:
            outcomes.append("Positive correlation between independent and dependent variables")
        if "decreases" in text or "negative" in text:
            outcomes.append("Negative correlation between independent and dependent variables")
        if "proportional" in text:
            outcomes.append("Linear relationship with constant of proportionality")
        if "causes" in text:
            outcomes.append("Significant difference between control and experimental conditions")
        if not outcomes:
            outcomes.append("Statistically significant effect (p < 0.05)")
            outcomes.append("Effect size exceeds minimum detectable threshold")
        return outcomes

    def _build_measurement_plan(self, design: ExperimentDesign) -> str:
        n_iv = len(design.independent_variables)
        n_dv = len(design.dependent_variables)
        return (f"Collect {design.num_trials} trials across {n_iv} independent variables, "
                f"measuring {n_dv} dependent variables with repeated measures. "
                f"Use {'randomized' if design.randomize else 'fixed'} order. "
                f"Blinding: {design.blinding}.")

    def _build_protocol(self, design: ExperimentDesign) -> List[str]:
        protocol = []
        protocol.append(f"1. Setup: Configure {len(design.independent_variables)} independent variables")
        protocol.append(f"2. Calibrate {len(design.controls)} control variables")

        steps = [
            "3. Run pre-experiment baseline measurements",
            "4. Apply intervention systematically",
            "5. Record all dependent variable measurements",
            "6. Repeat for each trial condition",
            "7. Document anomalies and deviations",
            "8. Verify data integrity",
        ]
        protocol.extend(steps)
        protocol.append(f"9. Complete {design.num_trials} total trials")
        return protocol

    def _estimate_feasibility(self, design: ExperimentDesign, domain: str) -> float:
        score = 0.7
        if len(design.independent_variables) > 3:
            score -= 0.2
        if len(design.controls) > 5:
            score -= 0.1
        if design.num_trials > 50:
            score -= 0.1
        if domain in ("physics", "chemistry"):
            score += 0.1
        return max(0.1, min(1.0, score))

    def _estimate_power(self, design: ExperimentDesign) -> float:
        n = design.num_trials
        n_iv = len(design.independent_variables)
        power = 0.5 * (1 - np.exp(-n / (10 + 5 * n_iv)))
        return float(max(0.1, min(1.0, power)))

    def simulate_experiment(self, design_id: str,
                            ground_truth: Optional[Dict[str, Any]] = None) -> Optional[ExperimentResult]:
        design = self.designs.get(design_id)
        if not design:
            return None

        result = ExperimentResult(
            experiment_id=design_id,
            hypothesis_id=design.hypothesis_id,
        )

        for t in range(design.num_trials):
            iv_vals = {}
            for iv in design.independent_variables:
                if design.randomize:
                    val = np.random.uniform(iv.range[0], iv.range[1])
                else:
                    val = iv.range[0] + (iv.range[1] - iv.range[0]) * t / max(design.num_trials, 1)
                iv_vals[iv.name] = float(val)

            dv_vals = {}
            for dv in design.dependent_variables:
                base = np.random.normal(0, 0.1)
                if ground_truth:
                    for iv_name, iv_val in iv_vals.items():
                        effect = ground_truth.get(iv_name, 0)
                        base += effect * iv_val
                else:
                    for iv in design.independent_variables:
                        base += 0.3 * iv_vals[iv.name] / (1 + abs(iv_vals[iv.name]))
                dv_vals[dv] = float(base)

            control_vals = {c.variable: c.value for c in design.controls}

            result.trials.append(TrialResult(
                trial_number=t + 1,
                independent_vars=iv_vals,
                dependent_vars=dv_vals,
                controls=control_vals,
            ))

        self._compute_statistics(result, design)
        self.results[result.id] = result
        return result

    def _compute_statistics(self, result: ExperimentResult,
                            design: ExperimentDesign) -> None:
        if len(result.trials) < 2:
            return

        dv_values = {}
        for dv in design.dependent_variables:
            vals = [t.dependent_vars.get(dv, 0) for t in result.trials]
            dv_values[dv] = vals

        all_vals = []
        for vals in dv_values.values():
            all_vals.extend(vals)

        if all_vals:
            mean = np.mean(all_vals)
            std = np.std(all_vals)
            n = len(all_vals)
            se = std / max(np.sqrt(n), 1)
            t_stat = mean / max(se, 1e-10)
            df = n - 1
            p_value = 2 * (1 - self._t_cdf(abs(t_stat), df))
            effect = abs(mean) / max(std, 1e-10)

            result.effect_size = float(effect)
            result.p_value = float(min(p_value, 1.0))
            result.confidence_interval = (float(mean - 1.96 * se), float(mean + 1.96 * se))
            result.mean_raw = float(mean)
            result.bayes_factor = float(np.exp(-0.5 * t_stat**2 / n))

            result.supports_hypothesis = p_value < 0.05 and effect > 0.3
            result.contradicts_hypothesis = p_value < 0.05 and effect < -0.3
            result.inconclusive = not (result.supports_hypothesis or result.contradicts_hypothesis)

    def _t_cdf(self, x: float, df: int) -> float:
        return float(self._t_distribution_cdf(x, df))

    def _betainc(self, a: float, b: float, x: float,
                  max_iter: int = 200, epsilon: float = 1e-12) -> float:
        if x < 0 or x > 1:
            return 0.0
        if x == 0 or x == 1:
            return x
        if x > (a + 1) / (a + b + 2):
            return 1.0 - self._betainc(b, a, 1.0 - x)
        lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
        front = math.exp(math.log(x) * a + math.log1p(-x) * b - lbeta - math.log(a))
        f = 1.0
        C = 1.0
        D = 1.0 - (a + b) * x / (a + 1.0)
        if abs(D) < 1e-30:
            D = 1e-30
        D = 1.0 / D
        f = D
        for m in range(1, max_iter + 1):
            nu_even = float(m) * (b - float(m)) * x
            de_even = (a + 2.0 * float(m) - 1.0) * (a + 2.0 * float(m))
            if abs(de_even) > 1e-30:
                d = nu_even / de_even
                D = 1.0 + d * D
                if abs(D) < 1e-30:
                    D = 1e-30
                C = 1.0 + d / C
                if abs(C) < 1e-30:
                    C = 1e-30
                D = 1.0 / D
                delta = C * D
                f *= delta
                if abs(delta - 1.0) < epsilon:
                    break
            nu_odd = -(a + float(m)) * (a + b + float(m)) * x
            de_odd = (a + 2.0 * float(m)) * (a + 2.0 * float(m) + 1.0)
            if abs(de_odd) > 1e-30:
                d = nu_odd / de_odd
                D = 1.0 + d * D
                if abs(D) < 1e-30:
                    D = 1e-30
                C = 1.0 + d / C
                if abs(C) < 1e-30:
                    C = 1e-30
                D = 1.0 / D
                delta = C * D
                f *= delta
                if abs(delta - 1.0) < epsilon:
                    break
        return float(front * f)

    def _t_distribution_cdf(self, x: float, df: int) -> float:
        x = float(x)
        df = float(df)
        if df <= 0:
            return 0.5
        if df > 200:
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
        a = df / 2.0
        b = 0.5
        xx = float(df) / (float(df) + x * x)
        if x >= 0:
            return 1.0 - 0.5 * self._betainc(a, b, xx)
        else:
            return 0.5 * self._betainc(a, b, xx)

    def get_design(self, design_id: str) -> Optional[ExperimentDesign]:
        return self.designs.get(design_id)

    def get_result(self, result_id: str) -> Optional[ExperimentResult]:
        return self.results.get(result_id)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_designs": len(self.designs),
            "total_results": len(self.results),
            "designs": [
                {"id": did, "name": d.name, "status": d.status,
                 "feasibility": d.feasibility}
                for did, d in self.designs.items()
            ],
        }
