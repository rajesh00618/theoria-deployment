from __future__ import annotations

import uuid
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import SimulationWorld


@dataclass
class WorldExperimentResult:
    world_id: str = ""
    experiment_id: str = ""
    domain: str = ""
    hypothesis: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    confirmed: bool = False
    information_gain: float = 0.0


class SimulationWorldManager:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.worlds: Dict[str, SimulationWorld] = {}
        self.experiment_results: List[WorldExperimentResult] = []
        self.cycle_count = 0

    def create_world(self, domain: str, name: Optional[str] = None,
                     parameters: Optional[Dict[str, Any]] = None) -> SimulationWorld:
        world_templates = {
            "physics": {
                "description": "Physics simulation with mechanics, thermodynamics, and electromagnetism",
                "rules": ["newtonian_mechanics", "thermodynamics", "electromagnetism"],
                "parameters": {"dimensions": 3, "precision": "double", "dt": 0.001},
            },
            "biology": {
                "description": "Ecosystem simulation with populations, selection, and mutation",
                "rules": ["natural_selection", "genetic_drift", "population_dynamics"],
                "parameters": {"population_size": 10000, "mutation_rate": 0.01, "generations": 1000},
            },
            "economics": {
                "description": "Market simulation with agents, goods, and exchange",
                "rules": ["supply_demand", "rational_choice", "market_equilibrium"],
                "parameters": {"agents": 1000, "goods": 10, "rounds": 1000},
            },
            "artificial": {
                "description": "Abstract computational world with programmable rules",
                "rules": ["cellular_automaton", "information_theory", "computational_irreducibility"],
                "parameters": {"grid_size": 256, "rule_set": "arbitrary", "steps": 10000},
            },
        }

        template = world_templates.get(domain, world_templates["artificial"])
        if parameters:
            template["parameters"].update(parameters)

        world = SimulationWorld(
            name=name or f"{domain.title()}World_{len(self.worlds)}",
            description=template["description"],
            domain=domain,
            world_parameters=template["parameters"],
            rules=template["rules"],
            max_experiments=getattr(self.config, 'experiments_per_world', 100000) if self.config else 100000,
        )
        self.worlds[world.id] = world
        return world

    def initialize_worlds(self, domains: Optional[List[str]] = None) -> List[SimulationWorld]:
        if domains is None:
            domains = ["physics", "biology", "economics", "artificial"]
        worlds = []
        for domain in domains:
            for i in range(10):
                world = self.create_world(
                    domain,
                    name=f"{domain.title()}World_{i}",
                )
                worlds.append(world)
        return worlds

    def run_experiment(self, world_id: str, hypothesis: str) -> WorldExperimentResult:
        world = self.worlds.get(world_id)
        if not world:
            return WorldExperimentResult()

        if world.experiment_count >= world.max_experiments:
            return WorldExperimentResult(world_id=world_id)

        confirmed = random.random() < 0.6
        info_gain = random.uniform(0.1, 0.9)

        result = WorldExperimentResult(
            world_id=world_id,
            experiment_id=str(uuid.uuid4())[:8],
            domain=world.domain,
            hypothesis=hypothesis,
            result={
                "outcome": "confirmed" if confirmed else "refuted",
                "effect_size": random.uniform(0.1, 2.0),
                "significance": random.uniform(0.001, 0.1),
                "data_points": random.randint(10, 1000),
            },
            confirmed=confirmed,
            information_gain=info_gain,
        )

        world.experiment_count += 1
        if confirmed:
            world.discovery_count += 1

        self.experiment_results.append(result)
        return result

    def run_batch_experiments(self, n: int = 100) -> List[WorldExperimentResult]:
        if not self.worlds:
            self.initialize_worlds()

        results = []
        hypotheses = [
            "increasing X increases Y",
            "A and B are correlated",
            "C causes D under condition E",
            "F and G interact synergistically",
            "H follows power law distribution",
        ]

        for _ in range(n):
            world_id = random.choice(list(self.worlds.keys()))
            hypothesis = random.choice(hypotheses)
            result = self.run_experiment(world_id, hypothesis)
            results.append(result)

        return results

    def get_world_stats(self) -> Dict[str, Any]:
        return {
            "total_worlds": len(self.worlds),
            "total_experiments": sum(w.experiment_count for w in self.worlds.values()),
            "total_discoveries": sum(w.discovery_count for w in self.worlds.values()),
            "by_domain": dict((d, sum(1 for w in self.worlds.values() if w.domain == d))
                             for d in ["physics", "biology", "economics", "artificial"]),
        }

    def get_summary(self) -> Dict[str, Any]:
        stats = self.get_world_stats()
        stats["experiments_this_cycle"] = len(self.experiment_results)
        stats["confirmation_rate"] = (
            sum(1 for r in self.experiment_results if r.confirmed) / max(len(self.experiment_results), 1)
        )
        return stats
