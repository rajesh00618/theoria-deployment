"""
L5 Falsification Engine: The Critic.

Stress-test theories with:
- Prediction derivation
- Severity via Mayo e-values
- Bayesian model comparison
- Lakatosian programme tracking
- Quine-Duhem handler
- Bounded protective belt
- Underdetermination resolver
- Explicit ignorance state
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

from theoria.core.types import (
    Theory, Evidence, SeverityRecord, Intervention,
    TheoryStatus, DisciplineMode,
)
from theoria.core.memory import TheoryMemory, Graveyard


class FalsificationEngine:
    """
    L5: Operationalizes Popper's severe tests.
    Theories are actively disproven, not merely confirmed.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Severity threshold
        self.tau_severe: float = 10.0  # Mayo e-value threshold
        self.epsilon_falsify: float = 0.1
        self.epsilon_retire: float = 0.05
        self.n_falsify_cycles: int = 5
        
        # Lakatosian tracking
        self.lambda_threshold: float = 1.0
        self.programme_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Underdetermination
        self.delta_tie: float = 0.05
        self.delta_confident: float = 0.7
        
        # Protective belt
        self.b_aux_default: int = 3
        
        # Test history
        self.tests_conducted: int = 0
        self.theories_falsified: int = 0
        self.theories_retired: int = 0
    
    def derive_predictions(self, theory: Theory,
                          competing_theories: List[Theory] = None) -> List[Dict[str, Any]]:
        """
        Derive novel predictions that differ from competing theories.
        Search for predictions improbable under all current alternatives.
        """
        predictions = []
        
        # Derive predictions from core claims
        for claim in theory.core_claims:
            # Look for quantitative relationships
            if "proportional" in claim.statement.lower():
                predictions.append({
                    "type": "quantitative",
                    "claim": claim.statement,
                    "prediction": "positive_correlation",
                    "severity_potential": 0.8,
                })
            elif "inverse" in claim.statement.lower():
                predictions.append({
                    "type": "quantitative",
                    "claim": claim.statement,
                    "prediction": "negative_correlation",
                    "severity_potential": 0.8,
                })
            elif "constant" in claim.statement.lower() or "invariant" in claim.statement.lower():
                predictions.append({
                    "type": "invariance",
                    "claim": claim.statement,
                    "prediction": "unchanged_under_transformation",
                    "severity_potential": 0.9,
                })
            elif "causal" in claim.statement.lower() or "→" in claim.statement:
                predictions.append({
                    "type": "causal",
                    "claim": claim.statement,
                    "prediction": "intervention_produces_effect",
                    "severity_potential": 0.85,
                })
        
        # Check discriminating power against competitors
        if competing_theories:
            for pred in predictions:
                pred["discriminating"] = self._is_discriminating(pred, theory, competing_theories)
        
        # Sort by severity potential
        predictions.sort(key=lambda p: p.get("severity_potential", 0.5), reverse=True)
        
        return predictions
    
    def _is_discriminating(self, prediction: Dict,
                          theory: Theory,
                          competitors: List[Theory]) -> bool:
        """Check if prediction discriminates theory from competitors."""
        # Simple heuristic: different claims → discriminating
        theory_claims = {c.statement for c in theory.core_claims}
        for comp in competitors:
            comp_claims = {c.statement for c in comp.core_claims}
            if prediction["claim"] not in comp_claims:
                return True
        return False
    
    def design_experiment(self, theory: Theory,
                         prediction: Dict[str, Any]) -> Optional[Intervention]:
        """
        Design experiment to test prediction.
        Active learning: maximize information gain.
        """
        if theory.intervention is None:
            return None
        
        # Build on theory's intervention
        base = theory.intervention
        
        experiment = Intervention(
            name=f"test_{prediction['prediction']}_{theory.id}",
            description=f"Test: {prediction['claim']} → {prediction['prediction']}",
            target_variables=base.target_variables,
            manipulation=base.manipulation,
            expected_outcomes={
                **base.expected_outcomes,
                "prediction_type": prediction["type"],
                "predicted_result": prediction["prediction"],
            },
            realizability=base.realizability,
            severity_potential=prediction.get("severity_potential", 0.5),
        )
        
        return experiment
    
    def compute_severity(self, theory: Theory,
                        experiment_result: Dict[str, Any]) -> SeverityRecord:
        """
        Compute Mayo e-value for severity.
        sev(E, T) = P(T passes E | H₀: T true and severely tested) / P(T passes E | T false)
        
        Simplified: ratio of expected vs actual outcome match.
        """
        predicted = experiment_result.get("predicted_outcome", {})
        observed = experiment_result.get("observed_outcome", {})
        
        # Compute match
        match_score = 0.0
        for var, pred_val in predicted.items():
            if var in observed:
                obs_val = observed[var]
                if isinstance(pred_val, (int, float)) and isinstance(obs_val, (int, float)):
                    error = abs(obs_val - pred_val) / (abs(pred_val) + 1e-10)
                    match_score += max(0, 1 - error)
                else:
                    match_score += 1.0 if obs_val == pred_val else 0.0
        
        n_vars = len(predicted) if predicted else 1
        match_score /= n_vars
        
        # e-value: high if test was severe AND theory passed
        # Severe test = could have easily failed if theory were false
        severity_potential = experiment_result.get("severity_potential", 0.5)
        
        if experiment_result.get("passed", False):
            e_value = (match_score * severity_potential) / 0.5  # Denominator: random would get 0.5
        else:
            e_value = 0.1  # Failed severe test
        
        e_value = max(0.01, e_value)
        
        record = SeverityRecord(
            experiment_id=experiment_result.get("id", "unknown"),
            e_value=e_value,
            outcome="passed" if experiment_result.get("passed") else "failed",
        )
        
        return record
    
    def bayesian_model_comparison(self, theories: List[Theory],
                                  evidence: List[Evidence]) -> Dict[str, float]:
        """
        Compute posterior for each theory given evidence.
        P(T|D) ∝ P(D|T) * P(T)
        """
        posteriors = {}
        
        for theory in theories:
            log_likelihood = 0.0
            for ev in evidence:
                # Get likelihood P(D|T)
                likelihood = ev.likelihood_under_theory.get(theory.id, 0.5)
                log_likelihood += np.log(max(likelihood, 1e-10))
            
            # Posterior ∝ prior * likelihood
            log_posterior = np.log(theory.prior) + log_likelihood
            posteriors[theory.id] = np.exp(log_posterior)
        
        # Normalize
        total = sum(posteriors.values())
        if total > 0:
            posteriors = {k: v/total for k, v in posteriors.items()}
        
        return posteriors
    
    def update_theory_status(self, theory: Theory,
                            severity_records: List[SeverityRecord]) -> TheoryStatus:
        """
        Update theory status based on test outcomes.
        Handles falsification, retirement, convergence.
        """
        self.tests_conducted += 1
        
        # Add severity records (tracks severe_tests_survived for convergence)
        # NOTE: Posterior is updated by empirics.update_theory_posterior per-evidence.
        # This method only adds severity records, does NOT overwrite posterior.
        for record in severity_records:
            theory.add_severity_record(record)
        
        # Check falsification
        if theory.is_falsified(self.epsilon_falsify, self.n_falsify_cycles):
            theory.status = TheoryStatus.FALSIFIED
            self.theories_falsified += 1
            return TheoryStatus.FALSIFIED
        
        # Default: mark as ACTIVE if it's survived evaluation
        if theory.status == TheoryStatus.PROPOSED:
            theory.status = TheoryStatus.ACTIVE
        
        # Check Lakatosian status
        prog_ratio = theory.lakatosian_ratio
        if prog_ratio < self.lambda_threshold / 2 and theory.modifications_in_period > 3:
            theory.status = TheoryStatus.DEGENERATING
        elif prog_ratio > self.lambda_threshold:
            theory.status = TheoryStatus.ACTIVE
        
        # Check convergence
        if theory.is_converged(k=5):
            theory.status = TheoryStatus.CONVERGED
        
        return theory.status
    
    def quine_duhem_handler(self, theory: Theory,
                           falsifying_evidence: Dict[str, Any]) -> List[str]:
        """
        When evidence falsifies theory, identify minimal auxiliary hypotheses
        to modify via causal graph surgery, not central hypothesis.
        """
        # Identify auxiliary claims to modify
        auxiliaries = []
        
        for i, claim in enumerate(theory.protective_belt.claims):
            if theory.protective_belt.modification_count < theory.protective_belt.max_modifications:
                auxiliaries.append(f"auxiliary_{i}: {claim.statement}")
        
        if not auxiliaries:
            # Belt exhausted - central hypothesis must be modified
            auxiliaries.append("CENTRAL_HYPOTHESIS")
        
        return auxiliaries
    
    def resolve_underdetermination(self, theories: List[Theory]) -> Tuple[Optional[Theory], Dict[str, Any]]:
        """
        When two+ theories have posterior difference < δ_tie.
        Multi-criteria tie-breaking.
        """
        if not theories:
            return None, {"state": "no_theories"}
        
        if len(theories) == 1:
            return theories[0], {"state": "single_theory"}
        
        # Check for underdetermination
        posteriors = [t.posterior for t in theories]
        max_post = max(posteriors)
        close_theories = [t for t in theories 
                         if abs(t.posterior - max_post) < self.delta_tie]
        
        if len(close_theories) <= 1:
            # Clear winner
            winner = max(theories, key=lambda t: t.posterior)
            if winner.posterior < self.delta_confident:
                return None, {
                    "state": "acknowledged_uncertainty",
                    "recommendation": "design_new_experiment",
                    "best_posterior": winner.posterior,
                }
            return winner, {"state": "clear_winner", "winner_id": winner.id}
        
        # Underdetermination: multi-criteria tie-breaking
        # 1. Highest unification score
        # 2. Highest fertility score
        # 3. Lowest deployment cost
        
        scored = []
        for t in close_theories:
            unification = len(t.reference_class)  # Broader reference = more unifying
            fertility = t.novel_predictions_confirmed
            cost = t.protective_belt.modification_count
            score = (unification * 0.4 + fertility * 0.4 - cost * 0.2)
            scored.append((t, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        winner = scored[0][0]
        
        return winner, {
            "state": "acknowledged_underdetermination",
            "winner_id": winner.id,
            "tied_theories": [t.id for t in close_theories],
            "unification_scores": {t.id: len(t.reference_class) for t in close_theories},
        }
    
    def evaluate_theory(self, theory: Theory,
                       evidence: List[Evidence],
                       competing: List[Theory] = None) -> Dict[str, Any]:
        """
        Full evaluation pipeline for a theory.
        Returns comprehensive evaluation report.
        """
        # Derive predictions
        predictions = self.derive_predictions(theory, competing)
        
        # Compute severity for available evidence
        severity_records = []
        for ev in evidence:
            if theory.id in ev.likelihood_under_theory:
                result = {
                    "id": ev.id,
                    "predicted_outcome": ev.likelihood_under_theory,
                    "observed_outcome": {theory.id: ev.likelihood_under_theory.get(theory.id, 0.5)},
                    "passed": ev.likelihood_under_theory.get(theory.id, 0.5) > 0.5,
                    "severity_potential": 0.7,
                }
                record = self.compute_severity(theory, result)
                severity_records.append(record)
        
        # Update status (now updates posterior based on severity records)
        new_status = self.update_theory_status(theory, severity_records)
        
        # Check for retirement
        if theory.is_retirable(self.epsilon_retire, 10):
            new_status = TheoryStatus.RETIRED
            self.theories_retired += 1
        
        return {
            "theory_id": theory.id,
            "predictions_derived": len(predictions),
            "severity_records": len(severity_records),
            "mean_e_value": np.mean([r.e_value for r in severity_records]) if severity_records else 0,
            "new_status": new_status.name,
            "posterior": theory.posterior,
            "lakatosian_ratio": theory.lakatosian_ratio,
            "is_falsified": theory.is_falsified(self.epsilon_falsify, self.n_falsify_cycles),
            "is_retirable": theory.is_retirable(),
            "is_converged": theory.is_converged(),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "tests_conducted": self.tests_conducted,
            "theories_falsified": self.theories_falsified,
            "theories_retired": self.theories_retired,
            "severity_threshold": self.tau_severe,
            "lambda_threshold": self.lambda_threshold,
        }
