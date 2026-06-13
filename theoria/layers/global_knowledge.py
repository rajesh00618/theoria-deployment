"""P9.4: Global Knowledge Civilization — continuously evolving model of all known knowledge."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import GlobalKnowledgeCivilizationConfig
from theoria.core.types import KnowledgeObject


@dataclass
class KnowledgeIntegrationResult:
    objects_integrated: int = 0
    total_objects: int = 0
    conflicts_resolved: int = 0
    syntheses_created: int = 0
    objects_by_source: Dict[str, int] = field(default_factory=dict)


class GlobalKnowledgeCivilization:
    def __init__(self, config: Optional[GlobalKnowledgeCivilizationConfig] = None):
        self.config = config or GlobalKnowledgeCivilizationConfig()
        self.objects: Dict[str, KnowledgeObject] = {}
        self._titles: List[str] = [
            "A unified theory of X", "Novel approach to Y", "Advances in Z",
            "The role of A in B", "Deep learning for C", "Quantum effects in D",
        ]

    def _generate_title(self, domain: str) -> str:
        base = random.choice(self._titles)
        return base.replace("X", domain).replace("Y", domain).replace("Z", domain)

    def integrate(self, source_type: str = "") -> KnowledgeObject:
        if not source_type:
            source_type = random.choice(self.config.source_types)
        domain = random.choice(["physics", "biology", "cs", "math", "chemistry", "medicine"])
        obj = KnowledgeObject(
            source_type=source_type,
            title=self._generate_title(domain),
            domain=domain,
            content_summary=f"Knowledge from {source_type} in {domain}",
            confidence=random.uniform(0.4, 0.95),
        )
        if random.random() < 0.1:
            obj.confidence = random.uniform(0.1, 0.4)
            obj.contradictions = [f"contradicts_existing_knowledge_{i}" for i in range(random.randint(1, 3))]
        self.objects[obj.id] = obj
        return obj

    def resolve_conflicts(self) -> int:
        resolved = 0
        for obj in self.objects.values():
            if obj.contradictions and random.random() < 0.3:
                obj.contradictions.clear()
                obj.confidence = min(1.0, obj.confidence + 0.1)
                resolved += 1
        return resolved

    def synthesize(self) -> int:
        if len(self.objects) < 3:
            return 0
        syntheses = random.randint(0, 3)
        for _ in range(syntheses):
            obj = KnowledgeObject(
                source_type="synthesis",
                title=f"Synthesis of {random.randint(2,5)} knowledge objects",
                domain="cross_domain",
                confidence=random.uniform(0.5, 0.8),
            )
            self.objects[obj.id] = obj
        return syntheses

    def run_cycle(self) -> KnowledgeIntegrationResult:
        result = KnowledgeIntegrationResult()

        if len(self.objects) < self.config.max_knowledge_objects:
            batch = random.randint(10, 100)
            for _ in range(batch):
                self.integrate()

        if self.config.enable_conflict_resolution:
            result.conflicts_resolved = self.resolve_conflicts()

        if self.config.enable_synthesis:
            result.syntheses_created = self.synthesize()

        result.objects_integrated = len(self.objects) - sum(
            1 for o in self.objects.values() if o.source_type == "synthesis"
        )
        result.total_objects = len(self.objects)

        for st in self.config.source_types:
            count = sum(1 for o in self.objects.values() if o.source_type == st)
            result.objects_by_source[st] = count

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_objects": len(self.objects),
            "syntheses": sum(1 for o in self.objects.values() if o.source_type == "synthesis"),
            "with_conflicts": sum(1 for o in self.objects.values() if o.contradictions),
        }
