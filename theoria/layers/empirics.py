"""
L1 Empirics: The World-Data Substrate.

Persists phenomenal data with provenance, uncertainty, and counterfactual scaffolding.
- Bayesian evidence store
- Intervention-grounded Structural Causal Model (SCM)
- Provenance versioning
- Replication-aware updating
- Theory-Age prior
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

from theoria.core.types import (
    Evidence, Theory, ProvenanceRecord, EvidenceReplicationStatus,
    Intervention, DomainOfValidity, DisciplineMode,
)


@dataclass
class CausalVariable:
    """A variable in the Structural Causal Model."""
    name: str
    parents: List[str] = field(default_factory=list)
    functional_form: Optional[str] = None  # e.g., "linear", "nonlinear"
    noise_distribution: str = "gaussian"


@dataclass  
class StructuralCausalModel:
    """
    Intervention-grounded SCM (not theory-derived).
    Built from controlled experiments and instrumental variables.
    """
    variables: Dict[str, CausalVariable] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)  # (cause, effect)
    
    def add_variable(self, var: CausalVariable) -> None:
        self.variables[var.name] = var
        for parent in var.parents:
            self.edges.append((parent, var.name))
    
    def get_parents(self, var_name: str) -> List[str]:
        return self.variables.get(var_name, CausalVariable("")).parents
    
    def counterfactual(self, target: str, intervention: Dict[str, Any],
                      evidence: Dict[str, Any]) -> float:
        """
        Simple counterfactual prediction.
        P(Y | do(X=x), evidence)
        """
        # Simplified: linear propagation
        if target not in self.variables:
            return 0.0
        
        var = self.variables[target]
        result = 0.0
        for parent in var.parents:
            if parent in intervention:
                result += intervention[parent]
            elif parent in evidence:
                result += evidence[parent]
        return result


class Empirics:
    """
    L1: The epistemic memory of the world, distinct from theoretical interpretation.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Bayesian evidence store
        self.evidence_store: Dict[str, Evidence] = {}
        self.claim_posteriors: Dict[str, float] = defaultdict(float)
        
        # Structural Causal Model (intervention-grounded)
        self.scm = StructuralCausalModel()
        
        # Provenance versioning
        self.provenance_history: Dict[str, List[ProvenanceRecord]] = defaultdict(list)
        
        # Replication tracking
        self.replication_registry: Dict[str, List[Dict]] = defaultdict(list)
        self.field_replication_rates: Dict[str, List[bool]] = defaultdict(list)
        
        # Heterogeneity handlers
        self.missing_data_strategy = "multiple_imputation"
        self.noisy_data_filter = "probabilistic_kalman"
        
        # Theory-Age prior
        self.theory_age_cycles: Dict[str, int] = defaultdict(int)
        self.age_decay_rate: float = 0.01  # Configurable per domain
    
    def add_evidence(self, evidence: Evidence) -> str:
        """
        Add evidence with full provenance.
        Returns evidence ID.
        """
        self.evidence_store[evidence.id] = evidence
        
        # Store provenance
        if evidence.provenance:
            self.provenance_history[evidence.id].append(evidence.provenance)
        
        # Weight by replication status
        weighted_posterior = self._replication_weighted_update(evidence)
        
        return evidence.id
    
    def _replication_weighted_update(self, evidence: Evidence) -> float:
        """
        Replication-aware updating (Section 5.9).
        Failed-to-replicate entries actively decrease credibility.
        """
        status = evidence.replication_status
        base_weight = 1.0
        
        if status == EvidenceReplicationStatus.REPLICATED_MULTIPLE:
            base_weight = 2.0
        elif status == EvidenceReplicationStatus.REPLICATED_ONCE:
            base_weight = 1.0
        elif status == EvidenceReplicationStatus.FAILED_TO_REPLICATE:
            base_weight = -1.5  # Actively decreases credibility
        elif status == EvidenceReplicationStatus.IN_DISPUTE:
            base_weight = 0.0  # No update until resolved
        
        return base_weight
    
    def update_theory_posterior(self, theory: Theory, 
                                evidence_id: str) -> float:
        """
        Bayesian update: P(T|D) ∝ P(D|T) * P(T)
        With theory-age prior and replication weighting.
        """
        if evidence_id not in self.evidence_store:
            return theory.posterior
        
        evidence = self.evidence_store[evidence_id]
        
        # Get likelihood P(D|T)
        likelihood = evidence.likelihood_under_theory.get(theory.id, 0.5)
        
        # Replication weight
        rep_weight = self._replication_weighted_update(evidence)
        
        # Theory-age prior (gentle pressure to keep population fresh)
        age_cycles = self.theory_age_cycles.get(theory.id, 0)
        age_penalty = np.exp(-self.age_decay_rate * age_cycles)
        
        # Bayesian update
        prior = theory.prior
        if rep_weight > 0:
            # Confirming evidence
            posterior = (likelihood * prior * rep_weight * age_penalty) / \
                       (likelihood * prior + 0.5 * (1 - prior) + 1e-10)
        elif rep_weight < 0:
            # Disconfirming evidence
            posterior = prior * (1 + rep_weight * (1 - likelihood))  # Decrease
            posterior = max(0.01, posterior)  # Floor
        else:
            posterior = theory.posterior  # No update
        
        # Clamp
        posterior = np.clip(posterior, 0.01, 0.99)
        
        theory.update_posterior(posterior)
        return posterior
    
    def update_with_intervention_result(self, theory: Theory,
                                        intervention: Intervention,
                                        observed_outcome: Any) -> Dict[str, Any]:
        """
        Update theory posterior based on intervention outcome.
        This is the key Disciplined-Constraint pathway.
        """
        # Compare predicted vs observed
        predicted = intervention.expected_outcomes
        
        # Simple matching for numerical outcomes
        match_score = 0.0
        for var, pred_val in predicted.items():
            if var in observed_outcome:
                obs_val = observed_outcome[var]
                if isinstance(pred_val, (int, float)) and isinstance(obs_val, (int, float)):
                    error = abs(obs_val - pred_val) / (abs(pred_val) + 1e-10)
                    match_score += max(0, 1 - error)
                else:
                    match_score += 1.0 if obs_val == pred_val else 0.0
        
        match_score /= len(predicted) if predicted else 1
        
        # Convert to likelihood
        likelihood = max(0.01, min(0.99, match_score))
        
        # Update
        prior = theory.posterior
        posterior = (likelihood * prior) / (likelihood * prior + 0.5 * (1 - prior) + 1e-10)
        posterior = np.clip(posterior, 0.01, 0.99)
        
        theory.update_posterior(posterior)
        
        return {
            "predicted": predicted,
            "observed": observed_outcome,
            "match_score": match_score,
            "likelihood": likelihood,
            "posterior_before": prior,
            "posterior_after": posterior,
        }
    
    def build_scm_from_interventions(self, variables: List[str],
                                     intervention_results: List[Dict]) -> StructuralCausalModel:
        """
        Build intervention-grounded SCM.
        Uses controlled experiments, not theory-derived.
        """
        scm = StructuralCausalModel()
        
        for var_name in variables:
            scm.add_variable(CausalVariable(name=var_name))
        
        # Infer edges from intervention results
        for result in intervention_results:
            intervened = result.get("intervened_var", "")
            affected = result.get("affected_vars", [])
            for aff in affected:
                if intervened in scm.variables and aff in scm.variables:
                    scm.variables[aff].parents.append(intervened)
                    scm.edges.append((intervened, aff))
        
        self.scm = scm
        return scm
    
    def get_counterfactual(self, target: str, 
                          intervention: Dict[str, Any],
                          evidence: Dict[str, Any]) -> float:
        """Query the counterfactual simulator."""
        return self.scm.counterfactual(target, intervention, evidence)
    
    def record_failed_replication(self, field: str, 
                                  original_evidence_id: str) -> None:
        """
        Handle replication failure.
        Updates field credibility (epsilon_field).
        """
        if original_evidence_id in self.evidence_store:
            ev = self.evidence_store[original_evidence_id]
            ev.replication_status = EvidenceReplicationStatus.FAILED_TO_REPLICATE
            ev.replication_attempts += 1
        
        self.field_replication_rates[field].append(False)
    
    def get_field_credibility_discount(self, field: str) -> float:
        """
        Compute epsilon_field: credibility discount for a field.
        Low replication rate → high discount.
        """
        history = self.field_replication_rates.get(field, [])
        if len(history) < 5:
            return 1.0  # Not enough data
        
        recent_rate = sum(history[-20:]) / len(history[-20:])
        # Map [0, 1] to [0.1, 1.0]
        discount = 0.1 + 0.9 * recent_rate
        return discount
    
    def increment_theory_age(self, theory_id: str) -> None:
        """Increment theory age for theory-age prior."""
        self.theory_age_cycles[theory_id] += 1
    
    def query_evidence_for_theory(self, theory_id: str,
                                   min_posterior: float = 0.5) -> List[Evidence]:
        """Get all evidence relevant to a theory."""
        results = []
        for ev in self.evidence_store.values():
            if theory_id in ev.likelihood_under_theory:
                results.append(ev)
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "evidence_count": len(self.evidence_store),
            "scm_variables": len(self.scm.variables),
            "scm_edges": len(self.scm.edges),
            "fields_tracked": len(self.field_replication_rates),
            "theories_aged": len(self.theory_age_cycles),
        }
