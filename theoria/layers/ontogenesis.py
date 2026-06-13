"""
L2 Ontogenesis: The Concept-Forge.

Forms genuinely new concepts, not merely retrieves existing ones.
- Evolving primitive set with lifecycle
- Composition rules (relational, functional, limit/duality)
- Cross-domain analogy engine (Gentner's structure-mapping)
- Concept archaeology (graveyard mining)
- Hierarchical concepts (base, composite, meta)
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

from theoria.core.types import Concept, ConceptLifecycle, Theory
from theoria.core.memory import Graveyard


class Ontogenesis:
    """
    L2: The Concept-Forge.
    Concepts are reified — once formed, they become first-class citizens.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Primitive set with lifecycle
        self.concepts: Dict[str, Concept] = {}
        self.primitives: Set[str] = set()  # Base concept IDs
        self.composite_concepts: Set[str] = set()
        self.meta_concepts: Set[str] = set()
        
        # Composition rules
        self.composition_rules: Dict[str, callable] = {
            "relational": self._compose_relational,
            "functional": self._compose_functional,
            "limit": self._compose_limit,
            "duality": self._compose_duality,
        }
        
        # Cross-domain analogy tracking
        self.domain_structures: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.analogy_mappings: List[Dict[str, Any]] = []
        
        # Evaluation tracking
        self.evaluation_cycles: int = 0
        self.cross_domain_threshold: float = 0.1  # gamma
    
    def initialize_base_primitives(self, domain: str = "physics") -> None:
        """Initialize primitive concepts for a domain."""
        base_primitives = {
            "physics": ["cause", "vector", "rate_of_change", "force", 
                       "mass", "distance", "time", "energy", "field"],
            "biology": ["population", "variation", "selection", "inheritance",
                       "competition", "reproduction", "speciation", "adaptation"],
            "general": ["entity", "relation", "change", "similarity",
                       "pattern", "structure", "process", "state"],
        }
        
        for name in base_primitives.get(domain, base_primitives["general"]):
            concept = Concept(
                name=name,
                definition=f"Primitive concept: {name}",
                kind="base",
                lifecycle=ConceptLifecycle.ALIVE,
            )
            concept.domains_where_useful.add(domain)
            self.concepts[concept.id] = concept
            self.primitives.add(concept.id)
    
    def compose_concept(self, primitive_ids: List[str], 
                       rule: str,
                       name: str,
                       definition: str = "") -> Optional[Concept]:
        """
        Compose new concept from primitives using a composition rule.
        Example: "force" = compose(["cause", "vector", "rate_of_change"], "functional")
        """
        # Verify primitives exist
        valid_primitives = [pid for pid in primitive_ids if pid in self.concepts]
        if len(valid_primitives) < 2:
            return None
        
        # Apply composition rule
        composer = self.composition_rules.get(rule)
        if composer is None:
            return None
        
        composed = composer(valid_primitives, name, definition)
        if composed:
            composed.primitives = valid_primitives
            composed.composition_rule = rule
            composed.kind = "composite"
            composed.lifecycle = ConceptLifecycle.PROPOSED
            self.concepts[composed.id] = composed
            self.composite_concepts.add(composed.id)
        
        return composed
    
    def _compose_relational(self, primitive_ids: List[str], 
                           name: str, definition: str) -> Concept:
        """Relational composition: A relates_to B."""
        primitive_names = [self.concepts[pid].name for pid in primitive_ids]
        auto_def = definition or f"Relational composition of {', '.join(primitive_names)}"
        return Concept(name=name, definition=auto_def, role="relation")
    
    def _compose_functional(self, primitive_ids: List[str],
                           name: str, definition: str) -> Concept:
        """Functional composition: f(g(x))."""
        primitive_names = [self.concepts[pid].name for pid in primitive_ids]
        auto_def = definition or f"Functional composition of {', '.join(primitive_names)}"
        return Concept(name=name, definition=auto_def, role="function")
    
    def _compose_limit(self, primitive_ids: List[str],
                      name: str, definition: str) -> Concept:
        """Limit composition: limit as X approaches Y."""
        return Concept(name=name, 
                      definition=definition or f"Limit concept: {name}",
                      role="limit")
    
    def _compose_duality(self, primitive_ids: List[str],
                        name: str, definition: str) -> Concept:
        """Duality composition: A and its dual."""
        return Concept(name=name,
                      definition=definition or f"Dual of {name}",
                      role="dual")
    
    def find_analogy(self, source_domain: str, 
                    target_domain: str) -> List[Dict[str, Any]]:
        """
        Cross-domain analogy engine (Gentner's structure-mapping).
        Finds structural isomorphisms between domains.
        
        Example: falling elevator ↔ orbiting spaceship (Einstein's equivalence)
        """
        source_concepts = [c for c in self.concepts.values() 
                          if source_domain in c.domains_where_useful]
        target_concepts = [c for c in self.concepts.values()
                          if target_domain in c.domains_where_useful]
        
        analogies = []
        
        for sc in source_concepts:
            for tc in target_concepts:
                # Structure-preserving similarity check
                if sc.role == tc.role and sc.kind == tc.kind:
                    # Check if relational structure matches
                    similarity = self._structural_similarity(sc, tc)
                    if similarity > 0.6:  # Threshold for analogy
                        analogies.append({
                            "source": sc.name,
                            "target": tc.name,
                            "similarity": similarity,
                            "type": "structural",
                            "source_domain": source_domain,
                            "target_domain": target_domain,
                        })
        
        self.analogy_mappings.extend(analogies)
        return analogies
    
    def _structural_similarity(self, c1: Concept, c2: Concept) -> float:
        """
        Compute structure-preserving similarity.
        Based on role, kind, and shared relational patterns.
        """
        score = 0.0
        
        # Role match
        if c1.role == c2.role:
            score += 0.3
        
        # Kind match
        if c1.kind == c2.kind:
            score += 0.2
        
        # Shared domains
        shared_domains = c1.domains_where_useful & c2.domains_where_useful
        if shared_domains:
            score += 0.2 * len(shared_domains) / max(len(c1.domains_where_useful),
                                                       len(c2.domains_where_useful))
        
        # Composition similarity
        if c1.composition_rule == c2.composition_rule:
            score += 0.3
        
        return min(1.0, score)
    
    def concept_archaeology(self, graveyard: Graveyard,
                           current_domain: str) -> List[Concept]:
        """
        Mine Graveyard for concepts that failed in their original domain
        but might succeed in a new one.
        
        Example: Pasteur's germ theory concept failed for centuries,
        then succeeded in medicine.
        """
        candidates = graveyard.get_resurrection_candidates(
            {"domain": current_domain}
        )
        
        resurrected = []
        for tid in candidates:
            entry = graveyard.entries[tid]
            theory = entry["theory"]
            
            # Extract concepts from failed theory
            for claim in theory.core_claims:
                # Check if concept could apply to new domain
                concept = Concept(
                    name=f"archaeo_{claim.statement[:30]}",
                    definition=f"Resurrected from {theory.name}: {claim.statement}",
                    kind="composite",
                    lifecycle=ConceptLifecycle.PROPOSED,
                )
                concept.domains_where_useful.add(current_domain)
                resurrected.append(concept)
        
        return resurrected
    
    def evaluate_primitives(self) -> None:
        """
        Lifecycle management: evaluate primitives for cross-domain compression.
        Transition: ALIVE → DEPRECATED → DEAD or PROPOSED → ALIVE.
        """
        self.evaluation_cycles += 1
        
        for cid, concept in self.concepts.items():
            if concept.kind != "base":
                continue
            
            if concept.lifecycle == ConceptLifecycle.PROPOSED:
                # Check if useful across domains
                if len(concept.domains_where_useful) >= 2:
                    concept.transition(ConceptLifecycle.ALIVE)
            
            elif concept.lifecycle == ConceptLifecycle.ALIVE:
                # Check if compression benefit has diminished
                if concept.cross_domain_score < -0.05:
                    concept.transition(ConceptLifecycle.DEPRECATED)
            
            elif concept.lifecycle == ConceptLifecycle.DEPRECATED:
                # Remove if no longer useful
                if concept.cross_domain_score < -0.1:
                    concept.transition(ConceptLifecycle.DEAD)
    
    def create_meta_concept(self, name: str, 
                           target_concepts: List[str],
                           definition: str = "") -> Optional[Concept]:
        """
        Create a meta-concept (concept about concepts).
        Examples: "symmetry", "conservation", "invariance"
        """
        valid_targets = [cid for cid in target_concepts if cid in self.concepts]
        if not valid_targets:
            return None
        
        concept = Concept(
            name=name,
            definition=definition or f"Meta-concept over {len(valid_targets)} concepts",
            kind="meta",
            role="meta",
            primitives=valid_targets,
            lifecycle=ConceptLifecycle.PROPOSED,
        )
        
        self.concepts[concept.id] = concept
        self.meta_concepts.add(concept.id)
        
        return concept
    
    def get_concepts_for_domain(self, domain: str,
                                 min_lifecycle: ConceptLifecycle = ConceptLifecycle.ALIVE
                                ) -> List[Concept]:
        """Get concepts relevant to a domain."""
        results = []
        for concept in self.concepts.values():
            if domain in concept.domains_where_useful:
                if concept.lifecycle.value >= min_lifecycle.value:
                    results.append(concept)
        return results
    
    def the_einstein_moment(self) -> Optional[Dict[str, Any]]:
        """
        Detect when two phenomena are the same under structure-preserving map.
        falling elevator == orbiting spaceship (equivalence principle)
        """
        # Find pairs of concepts from different domains with high structural similarity
        best_analogy = None
        best_score = 0.0
        
        concepts_list = list(self.concepts.values())
        for i, c1 in enumerate(concepts_list):
            for c2 in concepts_list[i+1:]:
                sim = self._structural_similarity(c1, c2)
                # Check if from different domains
                domains1 = c1.domains_where_useful
                domains2 = c2.domains_where_useful
                if not (domains1 & domains2) and sim > best_score:
                    best_score = sim
                    best_analogy = {
                        "concept1": c1.name,
                        "concept2": c2.name,
                        "similarity": sim,
                        "domains1": list(domains1),
                        "domains2": list(domains2),
                        "type": "equivalence_principle_candidate",
                    }
        
        return best_analogy if best_score > 0.7 else None
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_concepts": len(self.concepts),
            "primitives": len(self.primitives),
            "composite": len(self.composite_concepts),
            "meta": len(self.meta_concepts),
            "alive": sum(1 for c in self.concepts.values() if c.is_alive),
            "analogies_found": len(self.analogy_mappings),
            "evaluation_cycles": self.evaluation_cycles,
        }
