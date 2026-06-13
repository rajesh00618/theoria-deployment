"""
Phase 3: Cross-Domain Transfer (P3.7).

Applies structural insights from one domain to another.
Examples: Evolution → Economics, Neural Networks → Biology.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set
from collections import defaultdict

from theoria.core.types import (
    Theory, Concept, CrossDomainMapping, CandidateHypothesis, StrategyType,
)


class CrossDomainTransfer:
    """
    Identifies structural isomorphisms between domains and transfers insights.
    Enables novel insights through analogical reasoning across fields.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.mappings: Dict[str, CrossDomainMapping] = {}
        self.transfer_history: List[Dict[str, Any]] = []
        self.domain_graph: Dict[str, Set[str]] = defaultdict(set)

    def find_mappings(self, source_domain: str, target_domain: str,
                      source_concepts: List[Concept],
                      target_concepts: List[Concept]) -> List[CrossDomainMapping]:
        mappings = []
        for sc in source_concepts:
            for tc in target_concepts:
                score = self._compute_isomorphism(sc, tc)
                if score >= (self.config.min_isomorphism_score if self.config else 0.3):
                    mapping = CrossDomainMapping(
                        source_domain=source_domain,
                        target_domain=target_domain,
                        source_concept=sc.name,
                        target_concept=tc.name,
                        description=f"{sc.name} in {source_domain} maps to {tc.name} in {target_domain}",
                        strength=score,
                        verified=False,
                    )
                    mappings.append(mapping)
                    self.mappings[mapping.id] = mapping

        self.domain_graph[source_domain].add(target_domain)
        self.domain_graph[target_domain].add(source_domain)

        return mappings

    def _compute_isomorphism(self, sc: Concept, tc: Concept) -> float:
        score = 0.0

        if sc.kind == tc.kind:
            score += 0.3

        if sc.role and tc.role and sc.role == tc.role:
            score += 0.3

        mutual_domains = sc.domains_where_useful & tc.domains_where_useful
        if mutual_domains:
            score += 0.2

        name_overlap = len(set(sc.name.lower()) & set(tc.name.lower())) / max(
            max(len(sc.name), len(tc.name)), 1
        )
        score += name_overlap * 0.2

        return float(min(1.0, score))

    def _generate_transfer_predictions(self, sc: Concept, tc: Concept) -> List[str]:
        predictions = []
        predictions.append(f"If {sc.name} has property P in source domain, then {tc.name} may have analogous property P' in target domain")
        predictions.append(f"Relationships involving {sc.name} may have isomorphic counterparts for {tc.name}")
        return predictions

    def apply_mapping(self, mapping: CrossDomainMapping,
                      source_theory: Theory) -> CandidateHypothesis:
        transferred_claims = []
        for claim in source_theory.core_claims:
            transferred = claim.statement.replace(
                mapping.source_concept, mapping.target_concept
            )
            transferred_claims.append(transferred)

        description = "; ".join(transferred_claims[:3])
        hypothesis = CandidateHypothesis(
            id=str(uuid.uuid4())[:8],
            description=f"Cross-domain transfer: {mapping.source_domain} → {mapping.target_domain}: {description}",
            strategy_origin=StrategyType.CROSS_DOMAIN,
            concepts_used=[mapping.source_concept, mapping.target_concept],
            explanatory_power=mapping.strength * 0.7,
            novelty=mapping.strength * 0.9,
            falsifiability=mapping.strength * 0.5,
        )

        self.transfer_history.append({
            "mapping_id": mapping.id,
            "source_theory_id": source_theory.id,
            "generated_hypothesis_id": hypothesis.id,
            "timestamp": time.time(),
        })

        return hypothesis

    def get_domain_proximity(self, d1: str, d2: str) -> float:
        if d1 == d2:
            return 1.0
        shared = self.domain_graph.get(d1, set()) & self.domain_graph.get(d2, set())
        if shared:
            return 0.5
        return 0.1

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_mappings": len(self.mappings),
            "total_transfers": len(self.transfer_history),
            "domain_pairs_mapped": len(self.domain_graph),
            "domains": list(self.domain_graph.keys()),
            "avg_isomorphism": (
                float(np.mean([m.strength for m in self.mappings.values()]))
                if self.mappings else 0
            ),
        }
