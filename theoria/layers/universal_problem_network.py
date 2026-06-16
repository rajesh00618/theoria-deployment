"""P10.9: Universal Problem Network — connects all problems into a single network."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import UniversalProblemNetworkConfig
from theoria.core.types import ProblemNode


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class ProblemNetworkResult:
    nodes_created: int = 0
    total_nodes: int = 0
    connections_formed: int = 0
    solutions_proposed: int = 0
    solutions_implemented: int = 0
    network_density: float = 0.0


class UniversalProblemNetwork:
    def __init__(self, config: Optional[UniversalProblemNetworkConfig] = None):
        self.config = config or UniversalProblemNetworkConfig()
        self.nodes: Dict[str, ProblemNode] = {}
        self._init_problems()

    def _init_problems(self) -> None:
        descriptions = {
            "energy": "Global energy transition from fossil fuels to sustainable sources",
            "climate": "Climate change mitigation and adaptation",
            "materials": "Advanced materials for next-generation technologies",
            "economics": "Sustainable economic growth and resource allocation",
            "policy": "Evidence-based policy and governance frameworks",
            "society": "Social cohesion, equity, and human well-being",
        }
        for domain in self.config.problem_domains:
            node = ProblemNode(
                name=domain,
                description=descriptions.get(domain, f"Problems related to {domain}"),
                criticality=0.5 + _det_score(f"crit_{domain}") * 0.5,
            )
            self.nodes[node.id] = node
        # Connect related problems
        if self.config.enable_cross_connection:
            self._cross_connect()

    def _cross_connect(self) -> int:
        connections = 0
        node_list = list(self.nodes.values())
        for i, n1 in enumerate(node_list):
            for n2 in node_list[i+1:]:
                if random.random() < 0.5:
                    n1.connected_problems.append(n2.id)
                    n2.connected_problems.append(n1.id)
                    connections += 1
        return connections

    def propose_solutions(self) -> int:
        proposed = 0
        for node in self.nodes.values():
            if random.random() < 0.3:
                node.solutions_proposed += random.randint(1, 5)
                proposed += 1
            if random.random() < 0.15 and node.solutions_proposed > 0:
                implemented = random.randint(0, min(3, node.solutions_proposed))
                node.solutions_implemented += implemented
        return proposed

    def run_cycle(self) -> ProblemNetworkResult:
        result = ProblemNetworkResult()

        proposed = self.propose_solutions() if self.config.enable_solution_tracking else 0

        if self.config.enable_cross_connection:
            self._cross_connect()

        total_connections = sum(len(n.connected_problems) for n in self.nodes.values())
        max_possible = len(self.nodes) * (len(self.nodes) - 1) / 2 if len(self.nodes) > 1 else 1

        result.nodes_created = len(self.nodes)
        result.total_nodes = len(self.nodes)
        result.connections_formed = total_connections
        result.solutions_proposed = sum(n.solutions_proposed for n in self.nodes.values())
        result.solutions_implemented = sum(n.solutions_implemented for n in self.nodes.values())
        result.network_density = total_connections / max_possible if max_possible > 0 else 0

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "nodes": {n.name: {
                "solutions_proposed": n.solutions_proposed,
                "solutions_implemented": n.solutions_implemented,
                "connections": len(n.connected_problems),
                "criticality": n.criticality,
            } for n in self.nodes.values()},
            "total_connections": sum(len(n.connected_problems) for n in self.nodes.values()),
        }
