"""P10.3: Universal Knowledge Fabric 2.0 — integrates all domains into a single evolving structure."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import KnowledgeFabric2Config
from theoria.core.types import KnowledgeFabricNode


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class Fabric2Result:
    nodes_created: int = 0
    total_nodes: int = 0
    connections_formed: int = 0
    integration_score: float = 0.0
    nodes_by_domain: Dict[str, int] = field(default_factory=dict)


class UniversalKnowledgeFabric2:
    def __init__(self, config: Optional[KnowledgeFabric2Config] = None):
        self.config = config or KnowledgeFabric2Config()
        self.nodes: Dict[str, KnowledgeFabricNode] = {}

    def create_node(self, domain: str) -> KnowledgeFabricNode:
        content_templates = {
            "science": "Scientific finding in {}",
            "math": "Mathematical theorem in {}",
            "engineering": "Engineering principle for {}",
            "technology": "Technology breakthrough in {}",
            "economics": "Economic model of {}",
            "medicine": "Medical discovery about {}",
            "governance": "Governance framework for {}",
            "education": "Educational method for {}",
        }
        template = content_templates.get(domain, "Knowledge about {}")
        content = template.format(domain)

        node = KnowledgeFabricNode(
            domain=domain,
            content=content,
            integration_score=0.3 + _det_score(f"integ_{domain}_{len(self.nodes)}") * 0.5,
        )

        # Connect to existing nodes in other domains
        for existing in self.nodes.values():
            if existing.domain != domain and random.random() < 0.3:
                node.connections.append(existing.id)
                existing.connections.append(node.id)

        self.nodes[node.id] = node
        return node

    def integrate_domains(self) -> int:
        connections = 0
        # Create cross-domain connections
        domains_list = list(self.config.domains)
        for i, d1 in enumerate(domains_list):
            for d2 in domains_list[i+1:]:
                nodes_d1 = [n for n in self.nodes.values() if n.domain == d1]
                nodes_d2 = [n for n in self.nodes.values() if n.domain == d2]
                if nodes_d1 and nodes_d2 and random.random() < 0.2:
                    n1 = random.choice(nodes_d1)
                    n2 = random.choice(nodes_d2)
                    if n2.id not in n1.connections:
                        n1.connections.append(n2.id)
                        n2.connections.append(n1.id)
                        connections += 1
                        n1.integration_score = min(1.0, n1.integration_score + 0.05)
                        n2.integration_score = min(1.0, n2.integration_score + 0.05)
        return connections

    def run_cycle(self) -> Fabric2Result:
        result = Fabric2Result()

        if len(self.nodes) < self.config.max_nodes:
            batch = random.randint(10, 50)
            for _ in range(batch):
                domain = random.choice(self.config.domains)
                self.create_node(domain)

        connections = self.integrate_domains()

        result.nodes_created = len(self.nodes)
        result.total_nodes = len(self.nodes)
        result.connections_formed = connections
        result.integration_score = sum(n.integration_score for n in self.nodes.values()) / max(1, len(self.nodes))

        for d in self.config.domains:
            count = sum(1 for n in self.nodes.values() if n.domain == d)
            result.nodes_by_domain[d] = count

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "domains": {d: sum(1 for n in self.nodes.values() if n.domain == d) for d in self.config.domains},
            "avg_integration": sum(n.integration_score for n in self.nodes.values()) / max(1, len(self.nodes)),
            "total_connections": sum(len(n.connections) for n in self.nodes.values()),
        }
