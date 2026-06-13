"""
L3 Abductive Imagination: The Hypothesizer.

Generates a population of candidate explanations using 6 strategies:
S1: Pattern Completion (inductive)
S2: Causal Structural Search
S3: Analogical Transfer
S4: Evolutionary Search
S5: Dream-State Generation
S6: Rare-Event Hunter

Plus: Compute-Optimal Allocator (COA), MOBO aggregation, Formalizability Filter.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Callable
from collections import defaultdict
from dataclasses import dataclass, field

from theoria.core.types import (
    Theory, Concept, Strategy, StrategyType, CandidateHypothesis,
    FormalLanguage, CoreClaim, ProtectiveBelt, DomainOfValidity,
    DisciplineMode, KGNode, KGEdge, KGNodeType, KGEdgeType,
    ScientificPaper, ResearchGap, ResearchQuestion,
)
from theoria.core.memory import MetaStrategyMemory
from theoria.core.knowledge_graph import KnowledgeGraph
from theoria.layers.llm_client import LLMDriver


class AbductiveImagination:
    """
    L3: The multi-strategy ensemble hypothesis generator.
    
    Key property: strategies are complementary, not redundant.
    Each catches cases the others miss.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config

        self.strategies: Dict[StrategyType, Callable] = {
            StrategyType.PATTERN_COMPLETION: self._s1_pattern_completion,
            StrategyType.CAUSAL_STRUCTURAL_SEARCH: self._s2_causal_search,
            StrategyType.ANALOGICAL_TRANSFER: self._s3_analogical_transfer,
            StrategyType.EVOLUTIONARY_SEARCH: self._s4_evolutionary_search,
            StrategyType.DREAM_STATE: self._s5_dream_state,
            StrategyType.RARE_EVENT: self._s6_rare_event,
            StrategyType.LITERATURE_INFORMED: self._s7_literature_informed,
            StrategyType.CROSS_DOMAIN: self._s8_cross_domain,
            StrategyType.CAUSAL_REASONING: self._s9_causal_reasoning,
            StrategyType.COUNTERFACTUAL: self._s10_counterfactual,
            StrategyType.CONCEPT_BLENDING: self._s11_concept_blending,
            StrategyType.MECHANISTIC: self._s12_mechanistic,
            StrategyType.LLM_DRIVEN: self._s13_llm_driven,
        }

        self.strategy_rewards: Dict[StrategyType, List[float]] = {
            st: [] for st in StrategyType
        }
        self.strategy_costs: Dict[StrategyType, List[float]] = {
            st: [] for st in StrategyType
        }

        self.coa_weights: Dict[StrategyType, float] = {
            st: 1.0 for st in StrategyType
        }
        self.exploration_bonus: float = 0.1

        self.candidates: List[CandidateHypothesis] = []
        self.generation_count: int = 0

        self.knowledge_graph: Optional[KnowledgeGraph] = None
        self.papers: Dict[str, ScientificPaper] = {}
        self.primitive_names: set = set()
        self.llm_driver: Optional[LLMDriver] = None
        self.domain: str = "general"
    
    def init_primitive_names(self, primitives: set) -> None:
        """Register base primitive concept IDs so _select_concepts can deprioritize them."""
        self.primitive_names = primitives

    def _select_concepts(self, concepts: List[Concept], n: int, 
                        cycle: int = 0) -> List[Concept]:
        """
        Select concepts with exploration/exploitation tradeoff.
        Cycles through concept pool to ensure diversity.
        Prioritizes data-derived concepts over initialized primitives.
        """
        if not concepts:
            return []
        
        # Use cycle offset to rotate through concepts
        offset = (cycle * 2) % max(len(concepts), 1)
        rotated = concepts[offset:] + concepts[:offset]
        
        # Dynamically separate data-derived concepts from base primitives
        observable = [c for c in rotated if c.id not in self.primitive_names]
        abstract = [c for c in rotated if c.id in self.primitive_names]
        
        # Mix: 70% observable, 30% abstract (but ensure we always have some)
        if not observable:
            mixed = abstract
        elif not abstract:
            mixed = observable
        else:
            n_obs = min(max(int(0.7 * n), 1), len(observable))
            n_abs = min(n - n_obs, len(abstract))
            mixed = observable[:n_obs] + abstract[:n_abs]
        
        return mixed[:n] if len(mixed) >= n else mixed

    def generate_candidates(self, 
                           observations: List[Dict[str, Any]],
                           concepts: List[Concept],
                           existing_theories: List[Theory],
                           n_candidates: int = 10,
                           budget: Optional[float] = None) -> List[CandidateHypothesis]:
        """
        Main entry: generate candidate hypotheses using the ensemble.
        Uses COA to allocate compute across strategies.
        """
        self.candidates = []
        self.generation_count += 1
        
        # COA allocation
        allocations = self._coa_allocate(n_candidates)
        
        for strategy_type, n_alloc in allocations.items():
            if n_alloc <= 0:
                continue
            
            strategy_fn = self.strategies.get(strategy_type)
            if strategy_fn is None:
                continue
            
            start_time = time.time()
            try:
                new_candidates = strategy_fn(
                    observations, concepts, existing_theories, n_alloc
                )
                self.candidates.extend(new_candidates)
                
                # Track cost
                cost = time.time() - start_time
                self.strategy_costs[strategy_type].append(cost)
                
            except Exception as e:
                # Strategy failure is logged but not fatal
                print(f"Strategy {strategy_type.name} failed: {e}")
        
        # MOBO aggregation: Pareto front selection
        pareto_candidates = self._mobo_aggregate(self.candidates)
        
        # Formalizability filter
        filtered = self._formalizability_filter(pareto_candidates)
        
        return filtered[:n_candidates]
    
    def _coa_allocate(self, n_total: int) -> Dict[StrategyType, int]:
        """
        Compute-Optimal Allocator.
        Bandit-based allocation with exploration bonus.
        """
        allocations = {}
        
        # Compute expected value per strategy
        total_value = 0.0
        strategy_values = {}
        
        for st in StrategyType:
            rewards = self.strategy_rewards.get(st, [])
            avg_reward = np.mean(rewards) if rewards else 0.5
            n_pulls = len(rewards) if rewards else 1
            
            # UCB-like exploration bonus
            exploration = self.exploration_bonus * np.sqrt(
                np.log(self.generation_count + 1) / n_pulls
            )
            
            value = avg_reward + exploration
            strategy_values[st] = value
            total_value += value
        
        # Concentration cap: max 40% to any single strategy
        max_alloc = int(0.4 * n_total)
        
        remaining = n_total
        for st in StrategyType:
            if total_value > 0:
                alloc = int(n_total * strategy_values[st] / total_value)
            else:
                alloc = n_total // len(StrategyType)
            
            alloc = min(alloc, max_alloc)
            alloc = max(alloc, 1)  # Minimum 1 per strategy
            
            allocations[st] = alloc
            remaining -= alloc
        
        # Distribute remainder
        if remaining > 0:
            best_st = max(strategy_values, key=strategy_values.get)
            allocations[best_st] += remaining
        
        return allocations
    
    def _mobo_aggregate(self, 
                        candidates: List[CandidateHypothesis]) -> List[CandidateHypothesis]:
        """
        Multi-Objective Bayesian Optimization aggregation.
        Pareto front selection + epsilon-diverse samples.
        """
        if not candidates:
            return []
        
        # Compute Pareto front on (explanatory_power, parsimony, novelty, falsifiability)
        pareto = []
        for c in candidates:
            dominated = False
            for other in candidates:
                if other.id == c.id:
                    continue
                # Check if other dominates c
                dims = ["explanatory_power", "parsimony", "novelty", "falsifiability"]
                better_all = True
                better_some = False
                for dim in dims:
                    c_val = getattr(c, dim, 0)
                    o_val = getattr(other, dim, 0)
                    if o_val < c_val:
                        better_all = False
                        break
                    if o_val > c_val:
                        better_some = True
                if better_all and better_some:
                    dominated = True
                    break
            if not dominated:
                pareto.append(c)
        
        # Add diverse samples (epsilon-greedy)
        non_pareto = [c for c in candidates if c not in pareto]
        if non_pareto:
            n_diverse = max(1, len(pareto) // 5)
            diverse = sorted(non_pareto, 
                           key=lambda c: c.novelty, 
                           reverse=True)[:n_diverse]
            pareto.extend(diverse)
        
        return sorted(pareto, 
                     key=lambda c: c.explanatory_power + c.falsifiability,
                     reverse=True)
    
    def _formalizability_filter(self,
                                 candidates: List[CandidateHypothesis]
                                ) -> List[CandidateHypothesis]:
        """
        Filter: every hypothesis must be formalizable by L4 and testable by L5.
        Rejected at L3 before consuming L4/L5 resources.
        """
        filtered = []
        for c in candidates:
            # Check if description contains enough structure
            has_math_terms = any(term in c.description.lower() 
                               for term in ["=", "proportional", "function", 
                                          "law", "relation", "model"])
            has_predictive = any(term in c.description.lower()
                               for term in ["predicts", "implies", "if", "then"])
            
            if has_math_terms or has_predictive:
                filtered.append(c)
        
        return filtered
    
    # =====================================================================
    # S1: Pattern Completion
    # =====================================================================
    def _s1_pattern_completion(self, observations, concepts, 
                              existing_theories, n) -> List[CandidateHypothesis]:
        """
        Inductive pattern completion.
        Fit model, extract implicit law.
        Strong on curve fitting, weak on mechanism.
        """
        candidates = []
        
        # Extract numerical variable names from observations
        data_vars = set()
        for obs in observations:
            data = obs.get("data", obs)
            if isinstance(data, dict):
                data_vars.update(k for k, v in data.items() 
                               if isinstance(v, (int, float)))
        
        if data_vars:
            var_list = sorted(data_vars)
            patterns = [
                "linear relationship",
                "inverse relationship", 
                "quadratic relationship",
                "exponential relationship",
                "periodic pattern",
                "power law",
            ]
            
            for i, pattern in enumerate(patterns[:n]):
                # Use data-derived variables first, then fall back to concepts
                from itertools import combinations
                if len(var_list) >= 2:
                    chosen_vars = list(combinations(var_list, 2))[i % len(list(combinations(var_list, 2)))]
                    concept_names = list(chosen_vars)
                else:
                    selected = self._select_concepts(concepts, 2, self.generation_count + i)
                    concept_names = [c.name for c in selected]
                
                desc = f"Pattern: {pattern} between {', '.join(concept_names)}"
                
                candidate = CandidateHypothesis(
                    id=f"S1_{self.generation_count}_{i}",
                    description=desc,
                    strategy_origin=StrategyType.PATTERN_COMPLETION,
                    concepts_used=concept_names,
                    confidence=0.6,
                    explanatory_power=0.7,
                    parsimony=0.8,
                    novelty=0.3,
                    falsifiability=0.6,
                )
                candidates.append(candidate)
        else:
            # Fallback: use concepts directly
            for i in range(min(n, len(concepts))):
                selected = self._select_concepts(concepts, 2, self.generation_count + i)
                concept_names = [c.name for c in selected]
                desc = f"Pattern: relationship between {', '.join(concept_names)}"
                candidate = CandidateHypothesis(
                    id=f"S1_{self.generation_count}_{i}",
                    description=desc,
                    strategy_origin=StrategyType.PATTERN_COMPLETION,
                    concepts_used=concept_names,
                    confidence=0.6, explanatory_power=0.7,
                    parsimony=0.8, novelty=0.3, falsifiability=0.6,
                )
                candidates.append(candidate)
        
        return candidates
    
    # =====================================================================
    # S2: Causal Structural Search
    # =====================================================================
    def _s2_causal_search(self, observations, concepts,
                         existing_theories, n) -> List[CandidateHypothesis]:
        """
        Search space of structural causal models.
        Uses do-calculus reasoning.
        Strong on 'what causes what', weak on creative leaps.
        """
        candidates = []
        
        # Generate causal hypotheses from concept relationships
        selected = self._select_concepts(concepts, n + 3, self.generation_count)
        for i in range(min(n, len(selected) - 1)):
            cause = selected[i]
            for j in range(i + 1, min(i + 3, len(selected))):
                effect = selected[j]
                desc = f"Causal: {cause.name} → {effect.name} via structural mechanism"
                
                candidate = CandidateHypothesis(
                    id=f"S2_{self.generation_count}_{i}",
                    description=desc,
                    strategy_origin=StrategyType.CAUSAL_STRUCTURAL_SEARCH,
                    concepts_used=[cause.name, effect.name],
                    confidence=0.5,
                    explanatory_power=0.6,
                    parsimony=0.6,
                    novelty=0.5,
                    falsifiability=0.7,
                )
                candidates.append(candidate)
        
        return candidates[:n]
    
    # =====================================================================
    # S3: Analogical Transfer
    # =====================================================================
    def _s3_analogical_transfer(self, observations, concepts,
                               existing_theories, n) -> List[CandidateHypothesis]:
        """
        Cross-domain analogical transfer.
        Find isomorphic relational structure, port explanation.
        Strong on cross-domain creativity.
        """
        candidates = []
        
        # Check if any existing theory can be transferred
        for i, theory in enumerate(existing_theories[:n]):
            claims = [c.statement for c in theory.core_claims]
            selected = self._select_concepts(concepts, 4, self.generation_count + i)
            current_concepts = [c.name for c in selected]
            
            desc = (f"Analogical transfer from {theory.name}: "
                   f"Apply structure {'; '.join(claims[:2])} to "
                   f"{', '.join(current_concepts)}")
            
            candidate = CandidateHypothesis(
                id=f"S3_{self.generation_count}_{i}",
                description=desc,
                strategy_origin=StrategyType.ANALOGICAL_TRANSFER,
                concepts_used=current_concepts,
                confidence=0.4,
                explanatory_power=0.7,
                parsimony=0.5,
                novelty=0.8,
                falsifiability=0.5,
            )
            candidates.append(candidate)
        
        # If no existing theories, create from concept combinations
        if not candidates:
            selected = self._select_concepts(concepts, 4, self.generation_count)
            concept_names = [c.name for c in selected]
            desc = f"Analogical transfer: Apply pattern to {', '.join(concept_names)}"
            candidate = CandidateHypothesis(
                id=f"S3_{self.generation_count}_0",
                description=desc,
                strategy_origin=StrategyType.ANALOGICAL_TRANSFER,
                concepts_used=concept_names,
                confidence=0.4,
                explanatory_power=0.6,
                parsimony=0.5,
                novelty=0.7,
                falsifiability=0.5,
            )
            candidates.append(candidate)
        
        return candidates[:n]
    
    # =====================================================================
    # S4: Evolutionary Search
    # =====================================================================
    def _s4_evolutionary_search(self, observations, concepts,
                               existing_theories, n) -> List[CandidateHypothesis]:
        """
        Population-based evolutionary search.
        Mutation + crossover on hypotheses.
        Fitness = explanatory_power + parsimony + falsifiability.
        """
        candidates = []
        
        # Create hybrids from existing theories
        if len(existing_theories) >= 2:
            for i in range(min(n, len(existing_theories))):
                t1 = existing_theories[i]
                t2 = existing_theories[(i+1) % len(existing_theories)]
                
                claims1 = [c.statement for c in t1.core_claims[:2]]
                claims2 = [c.statement for c in t2.core_claims[:2]]
                selected = self._select_concepts(concepts, 3, self.generation_count + i)
                
                desc = (f"Evolutionary hybrid: Combine {'; '.join(claims1)} "
                       f"with {'; '.join(claims2)}. "
                       f"Fitness: explanatory + parsimony + falsifiability")
                
                candidate = CandidateHypothesis(
                    id=f"S4_{self.generation_count}_{i}",
                    description=desc,
                    strategy_origin=StrategyType.EVOLUTIONARY_SEARCH,
                    concepts_used=[c.name for c in selected],
                    confidence=0.5,
                    explanatory_power=0.6,
                    parsimony=0.5,
                    novelty=0.7,
                    falsifiability=0.6,
                )
                candidates.append(candidate)
        
        # If no existing theories, create from scratch
        if not candidates:
            for i in range(n):
                selected = self._select_concepts(concepts, 3, self.generation_count + i)
                concept_subset = [c.name for c in selected]
                desc = f"Evolved hypothesis: {' → '.join(concept_subset)} with optimized parameters"
                candidate = CandidateHypothesis(
                    id=f"S4_{self.generation_count}_{i}",
                    description=desc,
                    strategy_origin=StrategyType.EVOLUTIONARY_SEARCH,
                    concepts_used=concept_subset,
                    confidence=0.4,
                    explanatory_power=0.5,
                    parsimony=0.6,
                    novelty=0.6,
                    falsifiability=0.5,
                )
                candidates.append(candidate)
        
        return candidates
    
    # =====================================================================
    # S5: Dream-State Generation
    # =====================================================================
    def _s5_dream_state(self, observations, concepts,
                       existing_theories, n) -> List[CandidateHypothesis]:
        """
        Generative model produces novel combinations.
        The 'postulate' move: "What if X were true?"
        
        Einstein: "What if speed of light is same in all frames?"
        """
        candidates = []
        
        # Generate 'what if' hypotheses
        selected = self._select_concepts(concepts, 5, self.generation_count)
        concept_names = [c.name for c in selected]
        
        if len(concept_names) >= 3:
            postulates = [
                f"What if {concept_names[0]} and {concept_names[1]} are actually the same phenomenon?",
                f"What if there is a universal constant relating {concept_names[0]}, {concept_names[1]}, and {concept_names[2]}?",
                f"What if the relationship between {concept_names[0]} and {concept_names[1]} is invariant under transformation?",
                f"What if {concept_names[0]} emerges from {concept_names[1]} rather than being fundamental?",
                f"What if there exists an unseen mediator between {concept_names[0]} and {concept_names[1]}?",
            ]
        else:
            postulates = [f"What if {concept_names[0]} has a hidden structure?"]
        
        for i, postulate in enumerate(postulates[:n]):
            used = concept_names[:min(3, len(concept_names))]
            candidate = CandidateHypothesis(
                id=f"S5_{self.generation_count}_{i}",
                description=postulate,
                strategy_origin=StrategyType.DREAM_STATE,
                concepts_used=used,
                confidence=0.3,  # Lower confidence for speculative
                explanatory_power=0.8 if i < 2 else 0.5,  # Some postulates more powerful
                parsimony=0.4,
                novelty=0.9,  # Dream state produces novel ideas
                falsifiability=0.4,  # May be hard to test initially
            )
            candidates.append(candidate)
        
        return candidates
    
    # =====================================================================
    # S6: Rare-Event Hunter
    # =====================================================================
    def _s6_rare_event(self, observations, concepts,
                      existing_theories, n) -> List[CandidateHypothesis]:
        """
        Long-tail strategy: targets bottom decile of data distribution.
        High-impact rare events in particle physics, diseases, astronomy.
        """
        candidates = []
        
        for i in range(n):
            selected = self._select_concepts(concepts, 2, self.generation_count + i)
            concept_names = [c.name for c in selected]
            if len(concept_names) >= 2:
                desc = (f"Rare-event hypothesis: Anomalous {concept_names[0]} under "
                       f"extreme {concept_names[1]} conditions. "
                       f"Targets bottom decile with reweighted loss.")
            elif len(concept_names) == 1:
                desc = f"Rare-event hypothesis: Anomalous {concept_names[0]} in tail distribution"
            else:
                desc = "Rare-event hypothesis: Search for outliers"
            
            candidate = CandidateHypothesis(
                id=f"S6_{self.generation_count}_{i}",
                description=desc,
                strategy_origin=StrategyType.RARE_EVENT,
                concepts_used=concept_names,
                confidence=0.3,
                explanatory_power=0.5,
                parsimony=0.4,
                novelty=0.85,
                falsifiability=0.3,  # Hard to test rare events
            )
            candidates.append(candidate)
        
        return candidates
    
    # =====================================================================
    # S7: Literature-Informed Hypotheses (Phase 2)
    # =====================================================================
    def _s7_literature_informed(self, observations, concepts,
                                existing_theories, n) -> List[CandidateHypothesis]:
        """Generate hypotheses informed by scientific literature."""
        candidates = []
        papers = list(self.papers.values()) if self.papers else []

        if papers:
            for i in range(min(n, len(papers))):
                paper = papers[i % len(papers)]
                concepts_used = paper.extracted_concepts[:3] or [
                    c.name for c in self._select_concepts(concepts, 3, i)
                ]

                desc = (
                    f"Literature-informed: Based on '{paper.title[:60]}', "
                    f"hypothesize relationship between {', '.join(concepts_used[:3])} "
                    f"extending beyond reported findings"
                )
                candidate = CandidateHypothesis(
                    id=f"S7_{self.generation_count}_{i}",
                    description=desc,
                    strategy_origin=StrategyType.LITERATURE_INFORMED,
                    concepts_used=concepts_used,
                    confidence=0.5,
                    explanatory_power=0.6,
                    parsimony=0.5,
                    novelty=0.6,
                    falsifiability=0.5,
                )
                candidates.append(candidate)

        if not candidates:
            selected = self._select_concepts(concepts, 3, self.generation_count)
            names = [c.name for c in selected]
            desc = (
                f"Literature-informed hypothesis: "
                f"Based on extracted patterns between {', '.join(names)}"
            )
            candidate = CandidateHypothesis(
                id=f"S7_{self.generation_count}_0",
                description=desc,
                strategy_origin=StrategyType.LITERATURE_INFORMED,
                concepts_used=names,
                confidence=0.5,
                explanatory_power=0.6,
                parsimony=0.5,
                novelty=0.6,
                falsifiability=0.5,
            )
            candidates.append(candidate)

        return candidates[:n]

    # =====================================================================
    # S8: Cross-Domain Hypotheses (Phase 2)
    # =====================================================================
    def _s8_cross_domain(self, observations, concepts,
                         existing_theories, n) -> List[CandidateHypothesis]:
        """Generate hypotheses that bridge multiple domains."""
        candidates = []
        domain_concepts: Dict[str, List[Concept]] = {}

        for c in concepts:
            for domain in c.domains_where_useful:
                if domain not in domain_concepts:
                    domain_concepts[domain] = []
                domain_concepts[domain].append(c)

        domains = list(domain_concepts.keys())
        if len(domains) >= 2:
            for i in range(min(n, 3)):
                d1 = domains[i % len(domains)]
                d2 = domains[(i + 1) % len(domains)]
                c1_list = domain_concepts[d1]
                c2_list = domain_concepts[d2]
                if c1_list and c2_list:
                    c1 = c1_list[i % len(c1_list)]
                    c2 = c2_list[i % len(c2_list)]
                    desc = (
                        f"Cross-domain hypothesis: "
                        f"Bridge '{c1.name}' ({d1}) and '{c2.name}' ({d2}) "
                        f"using unified formal structure"
                    )
                    candidate = CandidateHypothesis(
                        id=f"S8_{self.generation_count}_{i}",
                        description=desc,
                        strategy_origin=StrategyType.CROSS_DOMAIN,
                        concepts_used=[c1.name, c2.name],
                        confidence=0.4,
                        explanatory_power=0.5,
                        parsimony=0.4,
                        novelty=0.8,
                        falsifiability=0.5,
                    )
                    candidates.append(candidate)

        if not candidates:
            selected = self._select_concepts(concepts, 4, self.generation_count)
            names = [c.name for c in selected]
            desc = (
                f"Cross-domain hypothesis: "
                f"Unify {', '.join(names[:2])} and {', '.join(names[2:])} "
                f"under common framework"
            )
            candidate = CandidateHypothesis(
                id=f"S8_{self.generation_count}_0",
                description=desc,
                strategy_origin=StrategyType.CROSS_DOMAIN,
                concepts_used=names,
                confidence=0.4,
                explanatory_power=0.5,
                parsimony=0.4,
                novelty=0.8,
                falsifiability=0.5,
            )
            candidates.append(candidate)

        return candidates[:n]

    # =====================================================================
    # S9: Causal Reasoning (Phase 2)
    # =====================================================================
    def _s9_causal_reasoning(self, observations, concepts,
                             existing_theories, n) -> List[CandidateHypothesis]:
        """Generate causal hypotheses using do-calculus reasoning."""
        candidates = []
        selected = self._select_concepts(concepts, n + 2, self.generation_count)

        causal_templates = [
            ("causal_chain", "{a} causes {b} which in turn causes {c}"),
            ("common_cause", "{a} and {b} share a common cause {c}"),
            ("direct_effect", "{a} directly modulates {b} via {c}"),
            ("feedback_loop", "{a} and {b} form a feedback loop through {c}"),
            ("mediation", "The effect of {a} on {b} is mediated by {c}"),
            ("moderation", "The relationship between {a} and {b} depends on {c}"),
        ]

        for i in range(min(n, len(selected) - 2)):
            names = [selected[j % len(selected)].name for j in range(i, i + 3)]
            template_name, template = causal_templates[i % len(causal_templates)]
            desc = template.format(a=names[0], b=names[1], c=names[2])

            candidate = CandidateHypothesis(
                id=f"S9_{self.generation_count}_{i}",
                description=desc,
                strategy_origin=StrategyType.CAUSAL_REASONING,
                concepts_used=names,
                confidence=0.5,
                explanatory_power=0.7,
                parsimony=0.5,
                novelty=0.6,
                falsifiability=0.7,
            )
            candidates.append(candidate)

        return candidates[:n]

    # =====================================================================
    # S10: Counterfactual Reasoning (Phase 2)
    # =====================================================================
    def _s10_counterfactual(self, observations, concepts,
                            existing_theories, n) -> List[CandidateHypothesis]:
        """Generate counterfactual 'what if' hypotheses."""
        candidates = []
        selected = self._select_concepts(concepts, 3, self.generation_count)
        names = [c.name for c in selected]

        counterfactuals = [
            f"If {names[0]} were absent, then {names[1]} would not exhibit {names[2]}",
            f"Had {names[0]} been different, the relationship between {names[1]} and {names[2]} would change",
            f"Counterfactual: Reversing {names[0]} would invert the effect on {names[1]}",
            f"Under the counterfactual where {names[0]} is held constant, {names[1]} and {names[2]} would be independent",
            f"If the mechanism linking {names[0]} to {names[1]} were disabled, {names[2]} would be unaffected",
        ]

        for i, cf in enumerate(counterfactuals[:n]):
            candidate = CandidateHypothesis(
                id=f"S10_{self.generation_count}_{i}",
                description=cf,
                strategy_origin=StrategyType.COUNTERFACTUAL,
                concepts_used=names,
                confidence=0.3,
                explanatory_power=0.5,
                parsimony=0.4,
                novelty=0.8,
                falsifiability=0.5,
            )
            candidates.append(candidate)

        return candidates

    # =====================================================================
    # S11: Concept Blending (Phase 2)
    # =====================================================================
    def _s11_concept_blending(self, observations, concepts,
                              existing_theories, n) -> List[CandidateHypothesis]:
        """Generate hypotheses by blending existing concepts."""
        candidates = []
        selected = self._select_concepts(concepts, n * 2, self.generation_count)

        for i in range(min(n, len(selected) // 2)):
            a = selected[i * 2]
            b = selected[i * 2 + 1] if i * 2 + 1 < len(selected) else selected[0]

            blend_name = f"{a.name}_{b.name}"
            desc = (
                f"Concept blend: The '{a.name}' and '{b.name}' concepts "
                f"unify into '{blend_name}', a composite that explains "
                f"phenomena involving both {a.role or 'structure'} and {b.role or 'process'}"
            )

            candidate = CandidateHypothesis(
                id=f"S11_{self.generation_count}_{i}",
                description=desc,
                strategy_origin=StrategyType.CONCEPT_BLENDING,
                concepts_used=[a.name, b.name],
                confidence=0.4,
                explanatory_power=0.6,
                parsimony=0.5,
                novelty=0.7,
                falsifiability=0.5,
            )
            candidates.append(candidate)

        return candidates

    # =====================================================================
    # S12: Mechanistic Hypotheses (Phase 2)
    # =====================================================================
    def _s12_mechanistic(self, observations, concepts,
                         existing_theories, n) -> List[CandidateHypothesis]:
        """Generate detailed mechanistic hypotheses."""
        candidates = []
        selected = self._select_concepts(concepts, n + 2, self.generation_count)

        mechanism_templates = [
            "Molecular mechanism: {a} binds to {b} triggering {c} pathway",
            "Physical mechanism: {a} exerts force on {b} through field {c}",
            "Information mechanism: {a} encodes information about {b} via signal {c}",
            "Statistical mechanism: {a} modulates probability of {b} through latent variable {c}",
            "Network mechanism: {a} and {b} are connected via regulatory node {c}",
            "Dynamic mechanism: {a} drives oscillations in {b} through feedback {c}",
        ]

        for i in range(min(n, len(selected) - 2)):
            names = [selected[(i + j) % len(selected)].name for j in range(3)]
            template = mechanism_templates[i % len(mechanism_templates)]
            desc = template.format(a=names[0], b=names[1], c=names[2])

            candidate = CandidateHypothesis(
                id=f"S12_{self.generation_count}_{i}",
                description=desc,
                strategy_origin=StrategyType.MECHANISTIC,
                concepts_used=names,
                confidence=0.5,
                explanatory_power=0.7,
                parsimony=0.4,
                novelty=0.6,
                falsifiability=0.6,
            )
            candidates.append(candidate)

        return candidates

    # =====================================================================
    # S13: LLM-Driven Hypothesis Generation
    # =====================================================================
    def _s13_llm_driven(self, observations, concepts,
                        existing_theories, n) -> List[CandidateHypothesis]:
        """Generate hypotheses using a local LLM via Ollama."""
        if self.llm_driver is None or not self.llm_driver.available:
            return []

        selected = self._select_concepts(concepts, min(n + 2, 5), self.generation_count)
        concept_names = [c.name for c in selected]
        target_concept = concept_names[0] if concept_names else "unknown"

        existing_knowledge = []
        for t in existing_theories[-8:]:
            existing_knowledge.append(f"{t.name}: {t.core_claim.statement if t.core_claim else t.description[:100]}")
        for c in concepts[:5]:
            existing_knowledge.append(f"Concept: {c.name} — {c.definition[:80] if c.definition else 'no definition'}")

        try:
            raw_hypotheses = self.llm_driver.generate_hypotheses(
                concept=target_concept,
                domain=self.domain,
                existing_knowledge=existing_knowledge,
                n_hypotheses=min(n, 5),
            )
        except Exception as e:
            print(f"S13 LLM failed: {e}")
            return []

        candidates = []
        for i, h in enumerate(raw_hypotheses):
            desc = h.get("description", f"LLM hypothesis about {target_concept}")
            mechanism = h.get("mechanism", "")
            if mechanism:
                desc = f"{desc} [mechanism: {mechanism}]"

            confidence = float(h.get("confidence", 0.5))
            confidence = max(0.1, min(1.0, confidence))

            candidate = CandidateHypothesis(
                id=f"S13_{self.generation_count}_{i}",
                description=desc,
                strategy_origin=StrategyType.LLM_DRIVEN,
                concepts_used=concept_names[:3],
                confidence=confidence,
                explanatory_power=min(confidence + 0.1, 1.0),
                parsimony=0.5,
                novelty=0.8,
                falsifiability=0.7,
            )
            candidates.append(candidate)

        return candidates

    def report_strategy_performance(self, strategy_type: StrategyType,
                                    quality: float) -> None:
        """Report quality outcome for COA learning."""
        self.strategy_rewards[strategy_type].append(quality)
    
    def get_summary(self) -> Dict[str, Any]:
        strategy_counts = {}
        for c in self.candidates:
            name = c.strategy_origin.name if hasattr(c.strategy_origin, 'name') else str(c.strategy_origin)
            strategy_counts[name] = strategy_counts.get(name, 0) + 1
        return {
            "total_candidates_generated": len(self.candidates),
            "generation_cycles": self.generation_count,
            "strategy_counts": strategy_counts,
            "strategy_rewards": {
                st.name: np.mean(rewards) if rewards else 0
                for st, rewards in self.strategy_rewards.items()
            },
        }
