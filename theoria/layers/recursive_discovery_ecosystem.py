"""P10.2: Recursive Discovery Ecosystem — agents create discoverers that create better discoverers."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _det_score(label: str) -> float:
    return int(hashlib.sha256(label.encode()).hexdigest(), 16) % 10000 / 10000.0

from theoria.core.config import RecursiveDiscoveryConfig
from theoria.core.types import RecursiveDiscoverer


@dataclass
class RecursiveDiscoveryResult:
    discoverers_created: int = 0
    total_discoverers: int = 0
    max_depth: int = 0
    discoveries_generated: int = 0
    avg_performance: float = 0.0


class RecursiveDiscoveryEcosystem:
    def __init__(self, config: Optional[RecursiveDiscoveryConfig] = None):
        self.config = config or RecursiveDiscoveryConfig()
        self.discoverers: Dict[str, RecursiveDiscoverer] = {}
        # Seed with first-generation discoverer
        seed = RecursiveDiscoverer(
            name=f"Discoverer_Seed",
            recursion_depth=0,
        )
        self.discoverers[seed.id] = seed

    def create_discoverer(self, parent_id: str, depth: int) -> RecursiveDiscoverer:
        parent = self.discoverers.get(parent_id)
        if not parent:
            parent = random.choice(list(self.discoverers.values()))

        if depth > self.config.max_recursion_depth:
            depth = self.config.max_recursion_depth

        discoverer = RecursiveDiscoverer(
            name=f"Discoverer_{len(self.discoverers)}_depth{depth}",
            recursion_depth=depth,
        )
        self.discoverers[discoverer.id] = discoverer
        parent.discoverers_created.append(discoverer.id)
        return discoverer

    def run_discovery(self) -> int:
        total = 0
        for d in self.discoverers.values():
            if d.status != "active":
                continue
            found = random.randint(0, 5)
            d.discoveries_generated += found
            total += found

            # Higher-depth discoverers perform better
            perf_boost = d.recursion_depth * 0.1
            d.performance = min(1.0, d.performance + _det_score(f"perf_{d.id}") * 0.05 + perf_boost * 0.01)

            if d.performance > 0.8 and self.config.enable_self_improvement:
                d.performance = min(1.0, d.performance + _det_score(f"self_{d.id}") * 0.02)

            if random.random() < 0.02 and d.recursion_depth > 0:
                d.status = "retired"

        return total

    def run_cycle(self) -> RecursiveDiscoveryResult:
        result = RecursiveDiscoveryResult()

        # Create new discoverers
        for parent in list(self.discoverers.values()):
            if random.random() < 0.3 and parent.status == "active":
                new_depth = min(parent.recursion_depth + 1, self.config.max_recursion_depth)
                self.create_discoverer(parent.id, new_depth)

        # Run discovery
        discoveries = self.run_discovery()

        result.discoverers_created = len(self.discoverers)
        result.total_discoverers = len(self.discoverers)
        result.max_depth = max((d.recursion_depth for d in self.discoverers.values()), default=0)
        result.discoveries_generated = sum(d.discoveries_generated for d in self.discoverers.values())
        result.avg_performance = sum(d.performance for d in self.discoverers.values()) / max(1, len(self.discoverers))

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_discoverers": len(self.discoverers),
            "max_depth": max((d.recursion_depth for d in self.discoverers.values()), default=0),
            "avg_performance": sum(d.performance for d in self.discoverers.values()) / max(1, len(self.discoverers)),
            "active": sum(1 for d in self.discoverers.values() if d.status == "active"),
        }
