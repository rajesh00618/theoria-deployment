from __future__ import annotations

import uuid
import hashlib
import random
import math
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from theoria.core.types import KnowledgeNode, KnowledgeEdge


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class FabricEvolveResult:
    new_nodes: int = 0
    new_edges: int = 0
    coherence: float = 0.0
    growth_rate: float = 0.0
    cross_domain_links: float = 0.0
    findings: List[str] = field(default_factory=list)


class UniversalKnowledgeFabric:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: List[KnowledgeEdge] = []
        self.cycle_count = 0
        self.node_types = [
            "concept", "theory", "process", "system", "organization",
            "technology", "person", "tool", "method",
        ]

    def add_node(self, name: str, node_type: str = "concept",
                 domain: str = "general",
                 description: str = "",
                 properties: Optional[Dict[str, Any]] = None) -> KnowledgeNode:
        node = KnowledgeNode(
            name=name,
            node_type=node_type,
            domain=domain,
            description=description,
            properties=properties or {},
        )
        self.nodes[node.id] = node
        return node

    def add_edge(self, source_id: str, target_id: str,
                 relation_type: str = "related_to",
                 weight: float = 1.0) -> KnowledgeEdge:
        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
        )
        self.edges.append(edge)
        return edge

    def query(self, query: str, domain: Optional[str] = None,
              top_k: int = 10) -> List[KnowledgeNode]:
        results = []
        for node in self.nodes.values():
            if domain and node.domain != domain:
                continue
            if query.lower() in node.name.lower():
                results.append(node)
        return results[:top_k]

    def get_neighbors(self, node_id: str,
                      max_depth: int = 1) -> List[KnowledgeNode]:
        visited = {node_id}
        frontier = {node_id}
        for _ in range(max_depth):
            next_frontier = set()
            for edge in self.edges:
                if edge.source_id in frontier and edge.target_id not in visited:
                    next_frontier.add(edge.target_id)
                if edge.target_id in frontier and edge.source_id not in visited:
                    next_frontier.add(edge.source_id)
            visited.update(next_frontier)
            frontier = next_frontier
        return [self.nodes[nid] for nid in visited if nid != node_id and nid in self.nodes]

    def evolve(self) -> FabricEvolveResult:
        self.cycle_count += 1
        result = FabricEvolveResult()

        new_count = random.randint(0, 3)
        for _ in range(new_count):
            node_type = random.choice(self.node_types)
            name = "{}_{}_{}".format(node_type, self.cycle_count, random.randint(0, 999))
            node = self.add_node(name, node_type)
            result.new_nodes += 1

            if len(self.nodes) > 1:
                target = random.choice(list(self.nodes.keys()))
                self.add_edge(node.id, target)
                result.new_edges += 1

        if result.new_nodes > 0:
            cross_count = random.randint(0, min(3, result.new_nodes))
            result.cross_domain_links = cross_count
            for _ in range(cross_count):
                n1 = random.choice(list(self.nodes.keys()))
                n2 = random.choice(list(self.nodes.keys()))
                if n1 != n2:
                    self.add_edge(n1, n2, "cross_domain", _det_score(f"edge_{n1}_{n2}_{self.cycle_count}"))

        total_possible = len(self.nodes) * (len(self.nodes) - 1) / 2.0
        actual_edges = len(self.edges)
        result.coherence = min(1.0, actual_edges / max(1, total_possible * 0.1))
        result.growth_rate = result.new_nodes / max(1, self.cycle_count)
        return result

    def get_domain_nodes(self, domain: str) -> List[KnowledgeNode]:
        return [n for n in self.nodes.values() if n.domain == domain]
