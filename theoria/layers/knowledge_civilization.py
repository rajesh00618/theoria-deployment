from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from theoria.core.types import KnowledgeNode, KnowledgeEdge, ReasoningTrace
from theoria.layers.universal_fabric import UniversalKnowledgeFabric
from theoria.layers.general_agent_society import GeneralAgentSociety
from theoria.layers.world_models import WorldModelingEngine


@dataclass
class CivilizationState:
    fabric_coherence: float = 0.0
    agent_productivity: float = 0.0
    model_accuracy: float = 0.0
    knowledge_growth_rate: float = 0.0
    cross_domain_activity: float = 0.0
    active_agents: int = 0
    active_models: int = 0
    total_nodes: int = 0
    total_edges: int = 0


@dataclass
class KnowledgeCivilizationResult:
    state: CivilizationState = field(default_factory=CivilizationState)
    nodes_created: int = 0
    mappings_generated: int = 0
    models_updated: int = 0
    findings: List[str] = field(default_factory=list)


class KnowledgeCivilizationLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.fabric = UniversalKnowledgeFabric(
            getattr(config, "knowledge_fabric", None) if config else None)
        self.agent_society = GeneralAgentSociety(
            getattr(config, "general_agent_society", None) if config else None)
        self.world_models = WorldModelingEngine(
            getattr(config, "world_model_p6", None) if config else None)
        self.cycle_count = 0
        self.state = CivilizationState()

    def run_cycle(self) -> KnowledgeCivilizationResult:
        self.cycle_count += 1
        result = KnowledgeCivilizationResult()

        fabric_result = self.fabric.evolve()
        agent_result = self.agent_society.run_cycle()
        model_result = self.world_models.run_cycle()

        self.state.fabric_coherence = fabric_result.get("coherence", 0.0)
        self.state.agent_productivity = agent_result.get("avg_productivity", 0.0)
        self.state.model_accuracy = model_result.get("avg_accuracy", 0.0)
        self.state.active_agents = agent_result.get("active_agents", 0)
        self.state.active_models = len(self.world_models.models)
        self.state.total_nodes = len(self.fabric.nodes)
        self.state.total_edges = len(self.fabric.edges)
        self.state.knowledge_growth_rate = fabric_result.get("growth_rate", 0.0)
        self.state.cross_domain_activity = fabric_result.get("cross_domain_links", 0.0)

        result.nodes_created = fabric_result.get("new_nodes", 0)
        result.mappings_generated = fabric_result.get("new_edges", 0)
        result.models_updated = len(self.world_models.models)
        result.findings = (
            agent_result.get("findings", []) +
            fabric_result.get("findings", [])
        )
        return result

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            "cycle": self.cycle_count,
            "fabric_coherence": self.state.fabric_coherence,
            "agent_productivity": self.state.agent_productivity,
            "model_accuracy": self.state.model_accuracy,
            "knowledge_growth": self.state.knowledge_growth_rate,
            "active_agents": self.state.active_agents,
            "active_models": self.state.active_models,
            "total_nodes": self.state.total_nodes,
            "total_edges": self.state.total_edges,
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "cycle_count": self.cycle_count,
            "fabric_nodes": len(self.fabric.nodes),
            "fabric_edges": len(self.fabric.edges),
            "agent_count": len(self.agent_society.agents),
            "model_count": len(self.world_models.models),
            "state": self.get_state_summary(),
        }
