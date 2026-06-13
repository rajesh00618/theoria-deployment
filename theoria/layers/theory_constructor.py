"""
L4 Theory Constructor: The Formalizer.

Converts candidate hypotheses into formal theories.
- Multi-representation (logic, causal graphs, probabilistic programs, geometric)
- Bayesian model merging
- Complexity contract
- Theory registration standard (Appendix D)
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import (
    Theory, FormalLanguage, CoreClaim,
    ProtectiveBelt, DomainOfValidity, Intervention, DisciplineMode,
    TheoryStatus,
)
from theoria.layers.abductive import CandidateHypothesis


class TheoryConstructor:
    """
    L4: Converts candidates into formal theories.
    T = (L, C, P, R, I, D, θ, π)
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.formalization_count: int = 0
        self.abandoned_count: int = 0
        
        # Supported formal languages
        self.languages: Dict[str, FormalLanguage] = {
            "algebraic": FormalLanguage(
                name="algebraic",
                syntax="equations",
                semantics="mathematical",
            ),
            "causal_graph": FormalLanguage(
                name="causal_graph",
                syntax="dag",
                semantics="structural_causal_model",
            ),
            "probabilistic": FormalLanguage(
                name="probabilistic",
                syntax="probabilistic_program",
                semantics="generative_model",
            ),
        }
    
    def formalize(self, candidate: CandidateHypothesis,
                  domain: str = "general",
                  discipline_mode: DisciplineMode = DisciplineMode.EMPIRICAL_INTERVENTION,
                  existing_theories: Optional[List[Theory]] = None
                 ) -> Optional[Theory]:
        """
        Compile a candidate hypothesis into a formal theory.
        
        Pipeline:
        1. Parse into formal primitives
        2. Type/well-formedness checks
        3. Consistency with existing theories
        4. Fit to data
        5. Occam-prior (MDL)
        6. Register in Theory Memory
        """
        # Duplicate check: skip if an identical theory already exists
        if existing_theories:
            candidate_sig = self._candidate_signature(candidate)
            for t in existing_theories:
                existing_sig = self._theory_signature(t)
                if candidate_sig == existing_sig:
                    self.abandoned_count += 1
                    return None
        
        self.formalization_count += 1
        
        # Select representation
        language = self._select_representation(candidate)
        
        # Extract core claims
        core_claims = self._extract_claims(candidate, language)
        if not core_claims:
            self.abandoned_count += 1
            return None
        
        # Build protective belt
        belt = self._build_protective_belt(candidate)
        
        # Define domain
        dom = self._infer_domain(candidate, domain)
        
        # Create intervention
        intervention = self._design_intervention(candidate, discipline_mode)
        
        # Compute Occam prior (MDL)
        complexity = len(core_claims) + len(candidate.concepts_used) * 0.5
        occam_prior = np.exp(-0.1 * complexity)  # Simpler theories get higher prior
        
        # Build theory
        theory = Theory(
            name=f"theory_{candidate.strategy_origin.name}_{self.formalization_count}",
            language=language,
            core_claims=core_claims,
            protective_belt=belt,
            reference_class=candidate.concepts_used + [domain],
            intervention=intervention,
            domain=dom,
            prior=occam_prior,
            posterior=occam_prior,
            origin_strategy=candidate.strategy_origin.name,
            discipline_mode=discipline_mode,
        )
        
        # Parse and check well-formedness
        if not self._well_formedness_check(theory):
            self.abandoned_count += 1
            return None
        
        return theory
    
    def _select_representation(self, 
                               candidate: CandidateHypothesis) -> FormalLanguage:
        """
        Select representation via meta-controller.
        Tries in order of predicted fit.
        """
        desc = candidate.description.lower()
        
        # Simple heuristic selection
        if any(w in desc for w in ["causal", "causes", "→", "leads to"]):
            return self.languages["causal_graph"]
        elif any(w in desc for w in ["probability", "distribution", "stochastic"]):
            return self.languages["probabilistic"]
        else:
            return self.languages["algebraic"]
    
    def _extract_claims(self, candidate: CandidateHypothesis,
                       language: FormalLanguage) -> List[CoreClaim]:
        """Extract core claims from candidate description."""
        claims = []
        
        desc = candidate.description
        
        # Parse key assertions
        # Look for patterns like "X is Y", "X → Y", "X proportional to Y"
        if "relationship" in desc or "proportional" in desc:
            claims.append(CoreClaim(
                statement=desc,
                formalization=f"f({', '.join(candidate.concepts_used)}) = ...",
                evidence_support=candidate.confidence,
            ))
        elif "causal" in desc:
            claims.append(CoreClaim(
                statement=desc,
                formalization=f"{' → '.join(candidate.concepts_used)}",
                evidence_support=candidate.confidence,
            ))
        elif "what if" in desc:
            # Postulate
            claims.append(CoreClaim(
                statement=desc,
                formalization=f"POSTULATE: {desc.replace('What if ', '')}",
                evidence_support=candidate.confidence * 0.8,  # Lower support for postulates
            ))
        else:
            # Generic claim
            claims.append(CoreClaim(
                statement=desc,
                evidence_support=candidate.confidence,
            ))
        
        return claims
    
    def _build_protective_belt(self, 
                               candidate: CandidateHypothesis) -> ProtectiveBelt:
        """Build initial protective belt with auxiliary hypotheses."""
        belt = ProtectiveBelt(max_modifications=3)
        
        # Add assumptions as auxiliary hypotheses
        for concept in candidate.concepts_used:
            belt.claims.append(CoreClaim(
                statement=f"Assumption: {concept} is well-defined in this domain",
                evidence_support=0.7,
            ))
        
        return belt
    
    def _infer_domain(self, candidate: CandidateHypothesis,
                     domain_hint: str) -> DomainOfValidity:
        """Infer domain of validity from candidate."""
        conditions = []
        
        if candidate.strategy_origin.name == "PATTERN_COMPLETION":
            conditions.append("Requires sufficient data density")
        elif candidate.strategy_origin.name == "CAUSAL_STRUCTURAL_SEARCH":
            conditions.append("Requires identifiable causal structure")
        elif candidate.strategy_origin.name == "DREAM_STATE":
            conditions.append("Requires testing of postulated invariants")
        
        return DomainOfValidity(
            conditions=conditions + [f"domain: {domain_hint}"],
        )
    
    def _design_intervention(self, candidate: CandidateHypothesis,
                            mode: DisciplineMode) -> Optional[Intervention]:
        """
        Design an intervention for the theory.
        This is the key Disciplined-Constraint anchor.
        """
        concepts = candidate.concepts_used
        if not concepts:
            return None
        
        if mode == DisciplineMode.EMPIRICAL_INTERVENTION:
            # Design physical intervention
            return Intervention(
                name=f"test_{'_'.join(concepts[:2])}",
                description=f"Vary {concepts[0]} and measure effect on {concepts[1]}",
                target_variables=concepts[:2],
                manipulation={concepts[0]: "systematic_variation"},
                expected_outcomes={concepts[1]: "correlated_response"},
                realizability=0.8,
                severity_potential=0.7,
            )
        
        elif mode == DisciplineMode.FORMAL_DEMONSTRATION:
            # Design proof obligation
            return Intervention(
                name=f"prove_{'_'.join(concepts[:2])}",
                description=f"Construct formal proof of relationship between {concepts[0]} and {concepts[1]}",
                target_variables=concepts[:2],
                manipulation={"proof_strategy": "derive_from_axioms"},
                expected_outcomes={"theorem": "proved_or_refuted"},
                realizability=0.9,
                severity_potential=0.9,
                mode=DisciplineMode.FORMAL_DEMONSTRATION,
            )
        
        elif mode == DisciplineMode.HISTORICAL_CONSILIENCE:
            # Design consilience check
            return Intervention(
                name=f"consilience_{'_'.join(concepts[:2])}",
                description=f"Converge evidence from independent streams about {concepts[0]} and {concepts[1]}",
                target_variables=concepts[:2],
                manipulation={"evidence_streams": "independent_measurement"},
                expected_outcomes={"convergence": "multi_source_agreement"},
                realizability=0.7,
                severity_potential=0.6,
                mode=DisciplineMode.HISTORICAL_CONSILIENCE,
            )
        
        return None
    
    def _candidate_signature(self, candidate: CandidateHypothesis) -> str:
        """Compute a signature for a candidate to detect duplicates."""
        claims = candidate.description.strip().lower()
        concepts = sorted(candidate.concepts_used)
        return f"{claims}|{concepts}"

    def _theory_signature(self, theory: Theory) -> str:
        """Compute a signature for a theory to compare with candidates."""
        claims = " ".join(c.statement.strip().lower() for c in theory.core_claims)
        # Exclude domain-name entries from reference_class for candidate comparison
        domain_keywords = {"physics", "biology", "chemistry", "mathematics", "general"}
        concepts = sorted(c for c in theory.reference_class if c.lower() not in domain_keywords)
        return f"{claims}|{concepts}"

    def _well_formedness_check(self, theory: Theory) -> bool:
        """Check theory well-formedness."""
        if not theory.core_claims:
            return False
        if not theory.reference_class:
            return False
        if not theory.intervention:
            return False
        return True
    
    def try_merge_theories(self, t1: Theory, t2: Theory,
                          kl_threshold: float = 0.1) -> Optional[Theory]:
        """
        Bayesian model merging.
        If posterior predictive KL < δ, merge with weighted average.
        """
        # Simplified KL estimate
        kl = abs(t1.posterior - t2.posterior)
        
        if kl < kl_threshold:
            # Merge
            merged = Theory(
                name=f"merged_{t1.name}_{t2.name}",
                language=t1.language,
                core_claims=t1.core_claims + t2.core_claims,
                protective_belt=t1.protective_belt,
                reference_class=list(set(t1.reference_class + t2.reference_class)),
                intervention=t1.intervention or t2.intervention,
                domain=t1.domain,
                prior=(t1.prior + t2.prior) / 2,
                posterior=(t1.posterior + t2.posterior) / 2,
            )
            return merged
        
        return None  # Keep separate
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "formalizations": self.formalization_count,
            "abandoned": self.abandoned_count,
            "success_rate": (self.formalization_count - self.abandoned_count) / max(1, self.formalization_count),
        }
