from __future__ import annotations

import uuid
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import (
    ArchitectureProposal, AlgorithmCandidate, StrategyVariant,
    Strategy, StrategyType,
)


@dataclass
class ArchitectureSearchResult:
    proposals_generated: int = 0
    proposals_benchmarked: int = 0
    best_improvement: float = 0.0
    proposals: List[ArchitectureProposal] = field(default_factory=list)


@dataclass
class AlgorithmDiscoveryResult:
    candidates_generated: int = 0
    candidates_benchmarked: int = 0
    best_improvement: float = 0.0
    candidates: List[AlgorithmCandidate] = field(default_factory=list)


@dataclass
class StrategyEvolutionResult:
    variants_generated: int = 0
    variants_benchmarked: int = 0
    variants_retained: int = 0
    best_performance: float = 0.0
    total_population: int = 0
    variants: List[StrategyVariant] = field(default_factory=list)


class ArchitectureSearch:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.proposals: List[ArchitectureProposal] = []
        self.cycle_count = 0

    def generate_proposals(self, layer_performance: Dict[str, float],
                           bottlenecks: List[Dict[str, Any]],
                           n_proposals: int = 5) -> List[ArchitectureProposal]:
        proposals = []
        templates = [
            ("reweight_layer", "Adjust allocation weights for layer {layer}"),
            ("add_module", "Add new module to {layer} for enhanced capability"),
            ("modify_parameter", "Tune {param} in {layer} from {old} to {new}"),
            ("remove_module", "Remove redundant module from {layer}"),
            ("rewire_connection", "Rewire {source} to {target} for better information flow"),
        ]

        if not bottlenecks:
            bottlenecks = [{"layer": "L3", "issue": "underperformance", "severity": 0.5}]

        for b in bottlenecks[:n_proposals]:
            layer = b.get("layer", "L3")
            template = random.choice(templates)
            name = template[0]
            desc = template[1].format(layer=layer, param=b.get("param", "weight"),
                                      old=b.get("old", 0.5), new=b.get("new", 0.8),
                                      source=b.get("source", "L3"), target=b.get("target", "L4"))
            expected_improvement = random.uniform(0.05, 0.3)
            proposal = ArchitectureProposal(
                name=f"arch_{name}_{layer}_{self.cycle_count}",
                description=desc,
                target_layer=layer,
                modification_type=name,
                proposed_changes={"layer": layer, "bottleneck": b.get("issue", "")},
                expected_improvement=expected_improvement,
                resource_cost=random.uniform(0.1, 0.8),
                risk_score=random.uniform(0.05, 0.4),
            )
            proposals.append(proposal)
            self.proposals.append(proposal)

        self.cycle_count += 1
        return proposals

    def benchmark_proposal(self, proposal: ArchitectureProposal,
                           current_performance: float) -> ArchitectureProposal:
        simulated_performance = current_performance * (1 + proposal.expected_improvement * random.uniform(0.5, 1.5))
        proposal.performance_impact = simulated_performance - current_performance
        proposal.benchmark_results.append({
            "cycle": self.cycle_count,
            "current_performance": current_performance,
            "simulated_performance": simulated_performance,
            "improvement": proposal.performance_impact,
        })
        proposal.status = "benchmarked"
        return proposal

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_proposals": len(self.proposals),
            "approved": sum(1 for p in self.proposals if p.status == "approved"),
            "deployed": sum(1 for p in self.proposals if p.status == "deployed"),
            "avg_improvement": np.mean([p.expected_improvement for p in self.proposals]) if self.proposals else 0,
        }


class AlgorithmDiscovery:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.population: List[AlgorithmCandidate] = []
        self.generation = 0
        self.target_domains = ["optimization", "search", "reasoning", "planning", "memory", "kg_traversal"]

    def evolve_population(self, n_candidates: int = 10) -> List[AlgorithmCandidate]:
        if not self.population:
            self.population = self._seed_initial_population(n_candidates)
            return self.population

        new_population = []
        elite_size = max(1, n_candidates // 5)

        sorted_pop = sorted(self.population, key=lambda c: c.measured_performance, reverse=True)
        new_population.extend(sorted_pop[:elite_size])

        while len(new_population) < n_candidates:
            if random.random() < 0.5 and len(sorted_pop) >= 2:
                parent1 = random.choice(sorted_pop[:len(sorted_pop)//2])
                parent2 = random.choice(sorted_pop[:len(sorted_pop)//2])
                child = self._crossover(parent1, parent2)
            else:
                parent = random.choice(sorted_pop[:max(1, len(sorted_pop)//3)])
                child = self._mutate(parent)

            if child:
                new_population.append(child)

        self.population = new_population[:n_candidates]
        self.generation += 1
        return self.population

    def _seed_initial_population(self, n: int) -> List[AlgorithmCandidate]:
        templates = {
            "optimization": ["gradient_descent_variant", "evolutionary_strategy", "simulated_annealing_adaptive"],
            "search": ["beam_search_variant", "monte_carlo_tree_search", "bidirectional_search"],
            "reasoning": ["chain_of_thought_variant", "tree_of_thought", "abductive_reasoning"],
            "planning": ["hierarchical_planner", "iterative_deepening", "means_ends_analysis"],
            "memory": ["sparse_retrieval", "hierarchical_memory", "associative_recall"],
            "kg_traversal": ["graph_attention_walk", "metapath_search", "neighborhood_aggregation"],
        }
        population = []
        for domain in self.target_domains:
            templates_for_domain = templates.get(domain, ["generic_variant"])
            for t in templates_for_domain[:max(1, n // len(self.target_domains))]:
                candidate = AlgorithmCandidate(
                    name=f"{t}_{self.generation}",
                    description=f"Algorithm variant for {domain}: {t}",
                    target_domain=domain,
                    pseudocode=f"def {t}(input): pass  # evolved variant",
                    complexity_estimate=f"O(n log n)",
                    baseline_name="current_best",
                    baseline_performance=0.5,
                    measured_performance=random.uniform(0.3, 0.8),
                    improvement_factor=random.uniform(-0.1, 0.3),
                )
                population.append(candidate)
        return population

    def _crossover(self, parent1: AlgorithmCandidate, parent2: AlgorithmCandidate) -> Optional[AlgorithmCandidate]:
        if parent1.target_domain != parent2.target_domain:
            return None
        child = AlgorithmCandidate(
            name=f"cross_{parent1.name}_{parent2.name}_{self.generation}",
            description=f"Crossover: {parent1.description} + {parent2.description}",
            target_domain=parent1.target_domain,
            pseudocode=f"# Crossover of {parent1.name} and {parent2.name}",
            complexity_estimate=parent1.complexity_estimate,
            baseline_name=parent1.baseline_name if parent1.measured_performance > parent2.measured_performance else parent2.baseline_name,
            baseline_performance=max(parent1.measured_performance, parent2.measured_performance),
            measured_performance=(parent1.measured_performance + parent2.measured_performance) / 2 * random.uniform(0.9, 1.1),
            improvement_factor=0.0,
        )
        return child

    def _mutate(self, parent: AlgorithmCandidate) -> AlgorithmCandidate:
        mutation_strength = random.uniform(-0.2, 0.3)
        child = AlgorithmCandidate(
            name=f"mut_{parent.name}_{self.generation}",
            description=f"Mutation of {parent.description}",
            target_domain=parent.target_domain,
            pseudocode=f"# Mutated from {parent.name}",
            complexity_estimate=parent.complexity_estimate,
            baseline_name=parent.baseline_name,
            baseline_performance=parent.baseline_performance,
            measured_performance=parent.measured_performance * (1 + mutation_strength),
            improvement_factor=parent.measured_performance * (1 + mutation_strength) - parent.baseline_performance,
        )
        return child

    def benchmark_candidate(self, candidate: AlgorithmCandidate,
                            test_results: Dict[str, float]) -> AlgorithmCandidate:
        avg_perf = np.mean(list(test_results.values())) if test_results else 0
        candidate.measured_performance = avg_perf
        candidate.improvement_factor = avg_perf - candidate.baseline_performance
        candidate.benchmark_results.append(test_results)
        candidate.status = "benchmarked"
        return candidate

    def get_best_candidate(self, domain: Optional[str] = None) -> Optional[AlgorithmCandidate]:
        candidates = self.population if not domain else [c for c in self.population if c.target_domain == domain]
        if not candidates:
            return None
        return max(candidates, key=lambda c: c.measured_performance)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_performance": max((c.measured_performance for c in self.population), default=0),
            "target_domains": self.target_domains,
        }


class StrategyEvolution:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.population: List[StrategyVariant] = []
        self.generation = 0

    def initialize_from_strategies(self, existing_strategies: List[Strategy]) -> None:
        for s in existing_strategies:
            variant = StrategyVariant(
                name=s.name,
                description=s.description,
                parent_strategies=[s.name],
                mutation_type="baseline",
                parameters={},
                performance_score=s.expected_value,
                generation=0,
            )
            self.population.append(variant)

        while len(self.population) < 10:
            self._seed_variant()

    def _seed_variant(self) -> StrategyVariant:
        mutation_types = ["search_focus", "exploration_bias", "composition", "parallelism", "sequential_depth"]
        mt = random.choice(mutation_types)
        variant = StrategyVariant(
            name=f"seed_strat_{len(self.population)}",
            description=f"Seeded strategy with {mt} mutation",
            mutation_type=mt,
            parameters={"focus": random.uniform(0, 1), "bias": random.uniform(0, 0.5)},
            performance_score=random.uniform(0.3, 0.7),
            generation=0,
        )
        self.population.append(variant)
        return variant

    def evolve(self, target_population: int = 1000) -> StrategyEvolutionResult:
        if not self.population:
            self.initialize_from_strategies([])

        while len(self.population) < target_population:
            if random.random() < 0.4:
                self._mutate_variant()
            elif random.random() < 0.7:
                self._combine_variants()
            else:
                self._novel_variant()

        self.population = self.population[:target_population]
        self.generation += 1

        retained = [v for v in self.population if v.performance_score > 0.4]
        best = max([v.performance_score for v in self.population], default=0)

        updated = []
        for v in self.population[:max(1, len(self.population)//10)]:
            v.benchmark_results.append({"cycle": self.generation, "score": v.performance_score})
            updated.append(v)

        return StrategyEvolutionResult(
            variants_generated=len(self.population),
            variants_benchmarked=len(updated),
            variants_retained=len(retained),
            best_performance=best,
            total_population=len(self.population),
            variants=self.population[:50],
        )

    def _mutate_variant(self) -> Optional[StrategyVariant]:
        if not self.population:
            return None
        parent = random.choice(self.population)
        child = StrategyVariant(
            name=f"mut_{parent.name}_{self.generation}",
            description=f"Mutation of {parent.name}",
            parent_strategies=[parent.name],
            mutation_type="mutate",
            parameters={k: v * random.uniform(0.8, 1.2) for k, v in parent.parameters.items()},
            performance_score=parent.performance_score * random.uniform(0.9, 1.15),
            generation=self.generation,
        )
        self.population.append(child)
        return child

    def _combine_variants(self) -> Optional[StrategyVariant]:
        if len(self.population) < 2:
            return None
        p1, p2 = random.sample(self.population, 2)
        child = StrategyVariant(
            name=f"comb_{p1.name}_{p2.name}_{self.generation}",
            description=f"Combination of {p1.name} and {p2.name}",
            parent_strategies=[p1.name, p2.name],
            mutation_type="combine",
            parameters={**p1.parameters, **p2.parameters},
            performance_score=(p1.performance_score + p2.performance_score) / 2 * random.uniform(0.95, 1.1),
            generation=self.generation,
        )
        self.population.append(child)
        return child

    def _novel_variant(self) -> StrategyVariant:
        novel_params = {
            "temperature": random.uniform(0.1, 2.0),
            "exploration_rate": random.uniform(0.01, 0.5),
            "depth": random.randint(1, 10),
            "breadth": random.randint(1, 5),
        }
        variant = StrategyVariant(
            name=f"novel_{len(self.population)}_{self.generation}",
            description="Novel strategy variant",
            mutation_type="novel",
            parameters=novel_params,
            performance_score=random.uniform(0.3, 0.9),
            generation=self.generation,
        )
        self.population.append(variant)
        return variant

    def get_top_strategies(self, n: int = 10) -> List[StrategyVariant]:
        sorted_variants = sorted(self.population, key=lambda v: v.performance_score, reverse=True)
        return sorted_variants[:n]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "generation": self.generation,
            "population_size": len(self.population),
            "best_performance": max((v.performance_score for v in self.population), default=0),
            "avg_performance": np.mean([v.performance_score for v in self.population]) if self.population else 0,
            "mutation_types": dict((mt, sum(1 for v in self.population if v.mutation_type == mt)) for mt in ["mutate", "combine", "novel", "baseline"]),
        }


class SelfImprovementLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.architecture_search = ArchitectureSearch(config.self_improvement if config else None)
        self.algorithm_discovery = AlgorithmDiscovery(config.algorithm_discovery if config else None)
        self.strategy_evolution = StrategyEvolution(config.strategy_evolution if config else None)
        self.cycle_count = 0

    def run_cycle(self, layer_performance: Dict[str, float],
                  bottlenecks: List[Dict[str, Any]],
                  existing_strategies: List[Strategy]) -> Dict[str, Any]:
        result = {}

        if self.config and getattr(self.config, 'enable_architecture_search', True):
            arch_proposals = self.architecture_search.generate_proposals(
                layer_performance, bottlenecks,
                n_proposals=getattr(self.config, 'max_architecture_proposals_per_cycle', 5),
            )
            for p in arch_proposals:
                self.architecture_search.benchmark_proposal(p, layer_performance.get(p.target_layer, 0.5))
            result["architecture_proposals"] = len(arch_proposals)
            result["architecture_proposals_list"] = arch_proposals

        if self.config and getattr(self.config, 'enable_algorithm_discovery', True):
            algo_candidates = self.algorithm_discovery.evolve_population(
                n_candidates=getattr(self.config, 'algorithm_population_size', 50)
            )
            result["algorithm_candidates"] = len(algo_candidates)
            result["algorithm_generation"] = self.algorithm_discovery.generation

        if self.config and getattr(self.config, 'enable_strategy_evolution', True):
            if not self.strategy_evolution.population:
                self.strategy_evolution.initialize_from_strategies(existing_strategies)
            strat_result = self.strategy_evolution.evolve(
                target_population=getattr(self.config, 'strategy_population_size', 1000)
            )
            result["strategy_population"] = strat_result.total_population
            result["strategy_best_performance"] = strat_result.best_performance

        self.cycle_count += 1
        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "architecture": self.architecture_search.get_summary(),
            "algorithm": self.algorithm_discovery.get_summary(),
            "strategy": self.strategy_evolution.get_summary(),
        }
