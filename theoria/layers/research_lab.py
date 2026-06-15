"""
Research Lab Orchestrator
=========================

Coordinates multiple research agents.

Input: Domains to research
Output: Coordinated research results
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.layers.research_agent import ResearchAgent, AgentMessage
from theoria.layers.specialized_agents import (
    PhysicsAgent, BiologyAgent, MathAgent, EconomicsAgent, ResearchManager
)


@dataclass
class LabResult:
    """Result from the research lab."""
    agents_active: int
    total_research_cycles: int
    discoveries_shared: int
    cross_domain_connections: int
    overall_progress: float
    agent_results: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


class ResearchLabOrchestrator:
    """
    Coordinates multiple research agents.
    
    Agents:
    - Physics Agent
    - Biology Agent
    - Math Agent
    - Economics Agent
    - Research Manager (coordinates)
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.agents: Dict[str, ResearchAgent] = {}
        self.manager: Optional[ResearchManager] = None
        self.lab_history: List[LabResult] = []
        self.cycle_count = 0
    
    def setup_lab(self, domains: Optional[List[str]] = None) -> None:
        """Setup the research lab with agents."""
        if domains is None:
            domains = ["physics", "biology", "mathematics", "economics"]
        
        # Create specialized agents
        agent_map = {
            "physics": PhysicsAgent,
            "biology": BiologyAgent,
            "mathematics": MathAgent,
            "economics": EconomicsAgent,
        }
        
        self.manager = ResearchManager()
        
        for domain in domains:
            if domain in agent_map:
                agent = agent_map[domain](self.config)
                self.agents[agent.agent_id] = agent
                self.manager.register_agent(agent)
    
    def run_cycle(self) -> LabResult:
        """
        Run one cycle of coordinated research.
        
        Returns:
            LabResult with all agent results
        """
        self.cycle_count += 1
        
        if not self.manager:
            self.setup_lab()
        
        # Run coordinated research
        coord_result = self.manager.coordinate_research()
        
        # Process messages
        total_messages = 0
        for agent in self.agents.values():
            responses = agent.process_inbox()
            total_messages += len(responses)
        
        # Count cross-domain connections
        cross_domain = self._count_cross_domain_connections()
        
        # Calculate progress
        progress = self._calculate_progress()
        
        result = LabResult(
            agents_active=len(self.agents),
            total_research_cycles=sum(a.cycle_count for a in self.agents.values()),
            discoveries_shared=self.manager.discoveries_shared,
            cross_domain_connections=cross_domain,
            overall_progress=progress,
            agent_results=coord_result.get("results", {}),
        )
        
        self.lab_history.append(result)
        return result
    
    def _count_cross_domain_connections(self) -> int:
        """Count connections between different domains."""
        connections = 0
        agents = list(self.agents.values())
        for i, a1 in enumerate(agents):
            for a2 in agents[i+1:]:
                if a1.domain != a2.domain:
                    shared = set(a1.knowledge.keys()) & set(a2.knowledge.keys())
                    connections += len(shared)
        return connections
    
    def _calculate_progress(self) -> float:
        """Calculate overall lab progress."""
        if not self.agents:
            return 0.0
        
        total_discoveries = sum(a.state.discoveries for a in self.agents.values())
        total_cycles = sum(a.cycle_count for a in self.agents.values())
        
        progress = min(1.0, (total_discoveries * 0.1 + total_cycles * 0.05))
        return progress
    
    def get_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all agents."""
        return {
            agent_id: {
                "domain": agent.domain,
                "discoveries": agent.state.discoveries,
                "cycles": agent.cycle_count,
                "knowledge_size": len(agent.knowledge),
            }
            for agent_id, agent in self.agents.items()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of lab activity."""
        return {
            "cycle_count": self.cycle_count,
            "agents": len(self.agents),
            "total_cycles": sum(a.cycle_count for a in self.agents.values()),
            "total_discoveries": sum(len(a.knowledge) for a in self.agents.values()),
            "discoveries_shared": self.manager.discoveries_shared if self.manager else 0,
        }
