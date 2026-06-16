"""P10.1 / L24: Knowledge Evolution Layer — knowledge evolves itself."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import KnowledgeEvolutionConfig, DiscoveryEcologyConfig
from theoria.core.types import KnowledgeEvolutionRecord, DiscoveryEcology


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class KnowledgeEvolutionResult:
    records_created: int = 0
    total_records: int = 0
    active_ecologies: int = 0
    ecologies: List[str] = field(default_factory=list)
    evolution_rate: float = 0.0


class KnowledgeEvolutionLayer:
    def __init__(self, config: Optional[KnowledgeEvolutionConfig] = None):
        self.config = config or KnowledgeEvolutionConfig()
        self.records: Dict[str, KnowledgeEvolutionRecord] = {}
        self.ecologies: Dict[str, DiscoveryEcology] = {}
        self._knowledge_pool: List[str] = []
        self._init_ecologies()

    def _init_ecologies(self) -> None:
        approaches = {
            "conservative": "Incremental refinement of established theories",
            "radical": "High-risk, high-reward paradigm-breaking approaches",
            "exploratory": "Broad undirected exploration of novel domains",
            "verification": "Rigorous replication and validation-focused research",
        }
        for name, approach in approaches.items():
            eco = DiscoveryEcology(
                name=name,
                approach=approach,
                agents=[f"agent_{i}" for i in range(int(10 + _det_score(f"agents_{name}") * 90))],
                theories_active=int(5 + _det_score(f"theories_{name}") * 45),
                productivity_score=0.2 + _det_score(f"prod_{name}") * 0.4,
                stability_score=0.5 + _det_score(f"stab_{name}") * 0.4,
            )
            self.ecologies[eco.id] = eco

    def _mutate_knowledge(self, parent_id: str = "") -> KnowledgeEvolutionRecord:
        evo_type = random.choice(self.config.evolution_types)
        parent = f"knowledge_{random.randint(0, 9999)}"
        kid = f"knowledge_{len(self._knowledge_pool)}"
        record = KnowledgeEvolutionRecord(
            knowledge_id=kid,
            parent_knowledge_id=parent_id or parent,
            evolution_type=evo_type,
            mutation_description=f"{evo_type.capitalize()} of {parent}",
            fitness_score=0.3 + _det_score(f"fitness_{kid}") * 0.65,
        )
        self.records[record.id] = record
        self._knowledge_pool.append(record.knowledge_id)
        return record

    def evolve_ecologies(self) -> int:
        active = 0
        for eco in self.ecologies.values():
            if random.random() < 0.3:
                eco.discoveries_made += random.randint(0, 3)
                eco.theories_active += max(0, eco.theories_active + random.randint(-1, 3))
                eco.productivity_score = max(0.0, min(1.0, eco.productivity_score + _det_score(f"prodelta_{eco.name}_{self.cycle_count if hasattr(self, 'cycle_count') else 0}") * 0.15 - 0.03))
                eco.stability_score = max(0.0, min(1.0, eco.stability_score + _det_score(f"stabdelta_{eco.name}_{self.cycle_count if hasattr(self, 'cycle_count') else 0}") * 0.1 - 0.02))
            if eco.productivity_score > 0.1:
                active += 1
        return active

    def run_cycle(self) -> KnowledgeEvolutionResult:
        result = KnowledgeEvolutionResult()

        mutations = random.randint(5, 20)
        for _ in range(mutations):
            parent = random.choice(self._knowledge_pool) if self._knowledge_pool else ""
            self._mutate_knowledge(parent)

        active = self.evolve_ecologies()

        result.records_created = len(self.records)
        result.total_records = len(self.records)
        result.active_ecologies = active
        result.ecologies = [e.name for e in self.ecologies.values()]
        result.evolution_rate = mutations / max(1, len(self.records))

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_records": len(self.records),
            "ecologies": {e.name: {"discoveries": e.discoveries_made, "productivity": e.productivity_score}
                         for e in self.ecologies.values()},
            "knowledge_pool_size": len(self._knowledge_pool),
        }
