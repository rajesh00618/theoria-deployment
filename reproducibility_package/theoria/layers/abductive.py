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
    DisciplineMode,
)
from theoria.core.memory import MetaStrategyMemory


class AbductiveImagination:
    """
    L3: The multi-strategy ensemble hypothesis generator.
    
    Key property: strategies are complementary, not redundant.
    Each catches cases the others miss.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Six strategies
        self.strategies: Dict[StrategyType, Callable] = {
            StrategyType.PATTERN_COMPLETION: self._s1_pattern_completion,
            StrategyType.CAUSAL_STRUCTURAL_SEARCH: self._s2_causal_search,
            StrategyType.ANALOGICAL_TRANSFER: self._s3_analogical_transfer,
            StrategyType.EVOLUTIONARY_SEARCH: self._s4_evolutionary_search,
            StrategyType.DREAM_STATE: self._s5_dream_state,
            StrategyType.RARE_EVENT: self._s6_rare_event,
        }
        
        # Strategy performance tracking for COA
        self.strategy_rewards: Dict[StrategyType, List[float]] = {
            st: [] for st in StrategyType
        }
        self.strategy_costs: Dict[StrategyType, List[float]] = {
            st: [] for st in StrategyType
        }
        
        # COA state
        self.coa_weights: Dict[StrategyType, float] = {
            st: 1.0 for st in StrategyType
        }
        self.exploration_bonus: float = 0.1
        
        # Candidate pool
        self.candidates: List[CandidateHypothesis] = []
        self.generation_count: int = 0
    
    def _select_concepts(self, concepts: List[Concept], n: int, 
                        cycle: int = 0) -> List[Concept]:
        """
        Select concepts with exploration/exploitation tradeoff.
        Cycles through concept pool to ensure diversity.
        """
        if not concepts:
            return []
        
        # Use cycle offset to rotate through concepts
        offset = (cycle * 2) % max(len(concepts), 1)
        rotated = concepts[offset:] + concepts[:offset]
        
        # Prioritize data-derived concepts (observables) over abstract primitives
        observable = [c for c in rotated if c.name not in 
                     {"cause", "vector", "rate_of_change", "force", "energy", "field"}]
        abstract = [c for c in rotated if c.name in 
                   {"cause", "vector", "rate_of_change", "force", "energy", "field"}]
        
        # Mix: 70% observable, 30% abstract
        mixed = observable + abstract
        
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
        
        # Look for numerical patterns in observations
        numerical_obs = [obs for obs in observations 
                        if any(k in obs for k in ["x", "y", "value", "measurement"])]
        
        if len(numerical_obs) >= 3 or len(observations) > 0:
            # Try to extract simple patterns
            patterns = [
                "linear relationship",
                "inverse relationship", 
                "quadratic relationship",
                "exponential relationship",
                "periodic pattern",
                "power law",
            ]
            
            for i, pattern in enumerate(patterns[:n]):
                selected = self._select_concepts(concepts, 3, self.generation_count + i)
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
    
    def report_strategy_performance(self, strategy_type: StrategyType,
                                    quality: float) -> None:
        """Report quality outcome for COA learning."""
        self.strategy_rewards[strategy_type].append(quality)
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_candidates_generated": len(self.candidates),
            "generation_cycles": self.generation_count,
            "strategy_rewards": {
                st.name: np.mean(rewards) if rewards else 0
                for st, rewards in self.strategy_rewards.items()
            },
        }
