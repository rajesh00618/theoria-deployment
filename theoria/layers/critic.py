"""
Phase 2: Scientific Critic.

Acts as an internal peer reviewer:
- Attack weak theories
- Detect logical flaws and unsupported claims
- Evaluate evidence quality
- Generate critique reports with confidence scores
"""

from __future__ import annotations

import re
import time
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

from theoria.core.types import (
    Theory, Evidence, CandidateHypothesis, CriticReport, QualityMetrics,
    TheoryStatus,
)


class ScientificCritic:
    """
    Internal peer reviewer that evaluates theories and hypotheses.
    Generates structured critique reports with dimension scores.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.critiques: List[CriticReport] = []
        self.quality_tracker: Dict[str, List[QualityMetrics]] = defaultdict(list)

    def critique_theory(self, theory: Theory,
                        evidence: Optional[List[Evidence]] = None,
                        alternatives: Optional[List[Theory]] = None) -> CriticReport:
        """Generate a comprehensive critique of a theory."""
        report = CriticReport(
            target_id=theory.id,
            target_type="theory",
        )

        report.logical_coherence = self._evaluate_logical_coherence(theory)
        report.evidence_quality = self._evaluate_evidence_quality(theory, evidence or [])
        report.explanatory_power = self._evaluate_explanatory_power(theory)
        report.parsimony = self._evaluate_parsimony(theory)
        report.falsifiability = self._evaluate_falsifiability(theory)
        report.novelty = self._evaluate_novelty(theory, alternatives or [])
        report.methodological_rigor = self._evaluate_methodological_rigor(theory)

        report.logical_flaws = self._detect_logical_flaws(theory)
        report.unsupported_claims = self._detect_unsupported_claims(theory, evidence or [])
        report.weak_evidence = self._find_weak_evidence(theory, evidence or [])
        report.missing_controls = self._find_missing_controls(theory)
        report.alternative_explanations = self._find_alternatives(theory, alternatives or [])

        report.required_fixes = self._generate_fixes(report)
        report.suggested_experiments = self._suggest_experiments(theory, report)
        report.overall_score = self._compute_overall(report)
        report.verdict = self._determine_verdict(report)

        self.critiques.append(report)

        qm = self._compute_quality_metrics(theory, evidence or [])
        self.quality_tracker[theory.id].append(qm)

        return report

    def critique_hypothesis(self, hypothesis: CandidateHypothesis) -> CriticReport:
        """Critique a candidate hypothesis before formalization."""
        report = CriticReport(
            target_id=hypothesis.id,
            target_type="hypothesis",
        )

        has_structure = any(t in hypothesis.description.lower()
                           for t in ["=", "proportional", "function", "model"])
        has_prediction = any(t in hypothesis.description.lower()
                            for t in ["predicts", "implies", "if", "then"])
        has_mechanism = any(t in hypothesis.description.lower()
                           for t in ["because", "via", "through", "mechanism"])

        report.logical_coherence = 0.6 if has_structure else 0.3
        report.falsifiability = 0.7 if has_prediction else 0.3
        report.explanatory_power = hypothesis.explanatory_power
        report.parsimony = hypothesis.parsimony
        report.novelty = hypothesis.novelty

        if not has_structure:
            report.logical_flaws.append({
                "type": "missing_formalization",
                "severity": "high",
                "description": "Hypothesis lacks formal structure for testing",
            })
            report.required_fixes.append("Add formal/mathematical structure")

        if not has_prediction:
            report.logical_flaws.append({
                "type": "no_testable_prediction",
                "severity": "high",
                "description": "Hypothesis makes no testable prediction",
            })
            report.required_fixes.append("Formulate a testable prediction")

        report.overall_score = self._compute_overall(report)
        report.verdict = self._determine_verdict(report)

        self.critiques.append(report)
        return report

    def _evaluate_logical_coherence(self, theory: Theory) -> float:
        """Evaluate internal logical consistency."""
        score = 0.7

        claims = [c.statement.lower() for c in theory.core_claims]
        contradictions = []
        for i, c1 in enumerate(claims):
            for j, c2 in enumerate(claims):
                if i < j:
                    c1_neg = any(term in c1 for term in ["not", "never", "no"])
                    c2_neg = any(term in c2 for term in ["not", "never", "no"])
                    if c1_neg and c2_neg:
                        contradictions.append((i, j))

        score -= len(contradictions) * 0.15

        if theory.language and theory.language.semantics:
            score += 0.1
        if theory.is_registered:
            score += 0.1
        if theory.domain.conditions:
            score += 0.05

        return max(0.1, min(1.0, score))

    def _evaluate_evidence_quality(self, theory: Theory,
                                     evidence: List[Evidence]) -> float:
        """Evaluate quality of supporting evidence."""
        if not evidence:
            return 0.2

        relevant = [e for e in evidence
                    if theory.id in e.likelihood_under_theory]
        if not relevant:
            return 0.3

        likelihoods = [e.likelihood_under_theory.get(theory.id, 0)
                       for e in relevant]
        avg_likelihood = np.mean(likelihoods) if likelihoods else 0

        replicated_count = sum(
            1 for e in relevant
            if e.replication_successes > 0
        )
        replication_ratio = replicated_count / max(len(relevant), 1)

        recent_count = sum(
            1 for e in relevant
            if e.cycles_since_tested < 10
        )
        freshness_ratio = recent_count / max(len(relevant), 1)

        score = (
            0.4 * avg_likelihood
            + 0.4 * replication_ratio
            + 0.2 * freshness_ratio
        )

        return max(0.1, min(1.0, score))

    def _evaluate_explanatory_power(self, theory: Theory) -> float:
        """Evaluate explanatory scope and power."""
        score = 0.5

        if theory.posterior > 0.7:
            score += 0.2
        if len(theory.core_claims) >= 2:
            score += 0.1
        if len(theory.domain.conditions) >= 2:
            score += 0.1
        if theory.novel_predictions_confirmed > 0:
            score += 0.15

        return min(1.0, score)

    def _evaluate_parsimony(self, theory: Theory) -> float:
        """Evaluate simplicity/Occam's razor."""
        n_params = len(theory.parameters)
        n_claims = len(theory.core_claims)

        if n_params == 0 and n_claims == 0:
            return 0.5

        complexity_penalty = (n_params * 0.1 + n_claims * 0.05)
        return max(0.1, min(1.0, 0.8 - complexity_penalty))

    def _evaluate_falsifiability(self, theory: Theory) -> float:
        """Evaluate how testable/falsifiable the theory is."""
        score = 0.3

        if theory.intervention:
            score += 0.3
            if theory.intervention.severity_potential > 0.5:
                score += 0.15
            if theory.intervention.realizability > 0.5:
                score += 0.1

        if len(theory.severity_records) > 0:
            score += 0.1

        if theory.domain.parameter_ranges:
            score += 0.1

        return min(1.0, score)

    def _evaluate_novelty(self, theory: Theory,
                           alternatives: List[Theory]) -> float:
        """Evaluate novelty against existing theories."""
        if not alternatives:
            return 0.7

        claim_sets = [
            set(c.statement.lower() for c in t.core_claims)
            for t in alternatives
        ]
        theory_claims = set(c.statement.lower() for c in theory.core_claims)

        max_overlap = max(
            len(theory_claims & cs) / max(len(theory_claims | cs), 1)
            for cs in claim_sets
        ) if claim_sets else 0

        return 1.0 - max_overlap

    def _evaluate_methodological_rigor(self, theory: Theory) -> float:
        """Evaluate methodological soundness."""
        score = 0.4

        if theory.intervention and theory.intervention.mode:
            score += 0.2
        if hasattr(theory, 'provenance') and theory.provenance:
            score += 0.1
        if len(theory.severity_records) >= 3:
            score += 0.15
        if theory.reference_class:
            score += 0.1
        if theory.domain.parameter_ranges:
            score += 0.1

        return min(1.0, score)

    def _detect_logical_flaws(self, theory: Theory) -> List[Dict[str, Any]]:
        """Detect logical flaws in the theory."""
        flaws = []
        claims = [c.statement.lower() for c in theory.core_claims]

        for i, claim in enumerate(claims):
            if "all" in claim and "some" not in claim:
                flaws.append({
                    "type": "overgeneralization",
                    "severity": "medium",
                    "description": f"Claim {i} uses universal quantifier without exception handling",
                    "location": f"core_claim[{i}]",
                })

        if theory.intervention:
            if theory.intervention.target_variables:
                for var in theory.intervention.target_variables:
                    if var not in theory.reference_class:
                        flaws.append({
                            "type": "intervention_mismatch",
                            "severity": "high",
                            "description": f"Intervention targets '{var}' not in reference class",
                            "location": "intervention",
                        })

        if theory.posterior > 0.9 and len(theory.severity_records) < 3:
            flaws.append({
                "type": "overconfidence",
                "severity": "medium",
                "description": "High posterior with insufficient severe testing",
                "location": "posterior",
            })

        return flaws

    def _detect_unsupported_claims(self, theory: Theory,
                                     evidence: List[Evidence]) -> List[str]:
        """Detect claims without supporting evidence."""
        unsupported = []
        relevant_evidence = [
            e for e in evidence
            if theory.id in e.likelihood_under_theory
        ]

        for claim in theory.core_claims:
            supporting = [
                e for e in relevant_evidence
                if e.likelihood_under_theory.get(theory.id, 0) > 0.5
            ]
            if not supporting:
                unsupported.append(claim.statement[:100])

        return unsupported

    def _find_weak_evidence(self, theory: Theory,
                              evidence: List[Evidence]) -> List[str]:
        """Find weak or unreliable evidence."""
        weak = []
        for e in evidence:
            reasons = []
            if e.replication_status.value in ("UNTESTED", "FAILED_TO_REPLICATE"):
                reasons.append("unreplicated")
            if e.cycles_since_tested > 20:
                reasons.append("stale")
            if e.provenance and e.provenance.uncertainty_estimate > 0.5:
                reasons.append("high_uncertainty")
            if reasons:
                weak.append(f"{e.description[:80]} ({', '.join(reasons)})")
        return weak[:5]

    def _find_missing_controls(self, theory: Theory) -> List[str]:
        """Identify missing experimental controls."""
        missing = []
        if theory.intervention:
            if not theory.intervention.expected_outcomes:
                missing.append("No expected outcomes specified")
            if not theory.domain.parameter_ranges:
                missing.append("No parameter range boundaries")
            if len(theory.reference_class) < 2:
                missing.append("Limited reference class (need comparison)")
        return missing

    def _find_alternatives(self, theory: Theory,
                            alternatives: List[Theory]) -> List[str]:
        """Generate alternative explanations."""
        alts = []
        for alt in alternatives[:3]:
            if alt.id != theory.id:
                posterior_diff = abs(theory.posterior - alt.posterior)
                if posterior_diff < 0.15:
                    alts.append(
                        f"{alt.name} has comparable posterior ({alt.posterior:.2f})"
                    )
        return alts

    def _generate_fixes(self, report: CriticReport) -> List[str]:
        """Generate required fixes based on critique."""
        fixes = []
        if report.logical_coherence < 0.5:
            fixes.append("Resolve internal logical contradictions")
        if report.evidence_quality < 0.4:
            fixes.append("Gather stronger supporting evidence")
        if report.falsifiability < 0.4:
            fixes.append("Design explicit testable predictions")
        if report.parsimony < 0.3:
            fixes.append("Simplify model (reduce parameters)")
        if report.methodological_rigor < 0.4:
            fixes.append("Improve methodological controls")
        return fixes

    def _suggest_experiments(self, theory: Theory,
                               report: CriticReport) -> List[str]:
        """Suggest experiments to address weaknesses."""
        experiments = []
        if report.falsifiability < 0.5:
            experiments.append(
                "Design intervention testing a core prediction under novel conditions"
            )
        if report.evidence_quality < 0.5:
            experiments.append(
                "Replicate key findings with independent methodology"
            )
        if report.logical_flaws:
            experiments.append(
                "Test edge cases where logical contradictions might manifest"
            )
        if not theory.domain.parameter_ranges:
            experiments.append(
                "Map parameter space to establish domain of validity"
            )
        return experiments[:3]

    def _compute_overall(self, report: CriticReport) -> float:
        """Compute overall quality score."""
        return (
            0.2 * report.logical_coherence
            + 0.2 * report.evidence_quality
            + 0.15 * report.explanatory_power
            + 0.1 * report.parsimony
            + 0.15 * report.falsifiability
            + 0.1 * report.novelty
            + 0.1 * report.methodological_rigor
        )

    def _determine_verdict(self, report: CriticReport) -> str:
        """Determine overall verdict based on scores."""
        flaws_high = sum(
            1 for f in report.logical_flaws
            if f.get("severity") == "high"
        )
        flaws_medium = sum(
            1 for f in report.logical_flaws
            if f.get("severity") == "medium"
        )

        if report.overall_score >= 0.8 and flaws_high == 0:
            return "accept"
        elif report.overall_score >= 0.6 and flaws_high <= 1:
            return "minor_revision"
        elif report.overall_score >= 0.3:
            return "major_revision"
        else:
            return "reject"

    def _compute_quality_metrics(self, theory: Theory,
                                   evidence: List[Evidence]) -> QualityMetrics:
        """Compute detailed quality metrics."""
        relevant = [e for e in evidence if theory.id in e.likelihood_under_theory]

        return QualityMetrics(
            severe_tests_passed=sum(1 for r in theory.severity_records
                                     if r.outcome == "passed"),
            severe_tests_failed=sum(1 for r in theory.severity_records
                                     if r.outcome == "failed"),
            replication_attempts=sum(e.replication_attempts for e in relevant),
            replication_successes=sum(e.replication_successes for e in relevant),
            mdl_complexity=len(theory.parameters) + 0.5 * len(theory.core_claims),
            prediction_accuracy=(
                theory.novel_predictions_confirmed /
                max(theory.novel_predictions_confirmed + theory.modifications_in_period, 1)
            ),
        )

    def get_summary(self) -> Dict[str, Any]:
        verdicts = defaultdict(int)
        for c in self.critiques:
            verdicts[c.verdict] += 1
        return {
            "total_critiques": len(self.critiques),
            "verdicts": dict(verdicts),
            "avg_overall_score": (
                np.mean([c.overall_score for c in self.critiques])
                if self.critiques else 0
            ),
        }
