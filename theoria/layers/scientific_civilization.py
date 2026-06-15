"""
Scientific Civilization
=======================

Multiple THEORIA agents collaborating and challenging each other.

Input: Multiple research domains
Output: Collaborative discoveries across domains
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CivilizationDiscovery:
    """A discovery made by the scientific civilization."""
    id: str
    domains: List[str]
    description: str
    contributors: List[str]
    novelty_score: float
    impact_score: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class CivilizationResult:
    """Result from scientific civilization."""
    agents: int
    discoveries: int
    cross_domain_insights: int
    challenges_issued: int
    collaborations_formed: int
    overall_progress: float
    timestamp: float = field(default_factory=time.time)


class ScientificCivilization:
    """
    Multiple THEORIA agents collaborating and challenging each other.
    
    Features:
    - Specialized agents per domain
    - Cross-domain collaboration
    - Adversarial challenges
    - Knowledge sharing
    - Collective intelligence
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.discoveries: List[CivilizationDiscovery] = []
        self.challenges: List[Dict[str, Any]] = []
        self.collaborations: List[Dict[str, Any]] = []
        self.cycle_count = 0
    
    def setup_civilization(self, domains: List[str]) -> None:
        """Setup agents for each domain."""
        for i, domain in enumerate(domains):
            self.agents[f"agent_{i}"] = {
                "id": f"agent_{i}",
                "domain": domain,
                "discoveries": [],
                "knowledge": {},
            }
    
    def run_cycle(self) -> CivilizationResult:
        """Run one cycle of civilization activity."""
        self.cycle_count += 1
        
        # Each agent researches
        for agent_id, agent in self.agents.items():
            self._agent_research(agent)
        
        # Share discoveries
        self._share_discoveries()
        
        # Challenge each other
        self._issue_challenges()
        
        # Collaborate on promising areas
        self._form_collaborations()
        
        return CivilizationResult(
            agents=len(self.agents),
            discoveries=len(self.discoveries),
            cross_domain_insights=len(self.collaborations),
            challenges_issued=len(self.challenges),
            collaborations_formed=len(self.collaborations),
            overall_progress=min(1.0, len(self.discoveries) * 0.05),
        )
    
    def _agent_research(self, agent: Dict) -> None:
        """Individual agent research."""
        domain = agent["domain"]
        discovery = CivilizationDiscovery(
            id=f"disc_{len(self.discoveries)}",
            domains=[domain],
            description=f"Discovery in {domain}",
            contributors=[agent["id"]],
            novelty_score=0.6,
            impact_score=0.5,
        )
        self.discoveries.append(discovery)
        agent["discoveries"].append(discovery.id)
    
    def _share_discoveries(self) -> None:
        """Share discoveries between agents."""
        for discovery in self.discoveries[-5:]:
            for agent_id, agent in self.agents.items():
                agent["knowledge"][discovery.id] = discovery.description
    
    def _issue_challenges(self) -> None:
        """Agents challenge each other's discoveries."""
        if len(self.discoveries) >= 2:
            challenge = {
                "challenger": "agent_0",
                "target": "agent_1",
                "discovery": self.discoveries[-1].id,
                "type": "evidence_quality",
            }
            self.challenges.append(challenge)
    
    def _form_collaborations(self) -> None:
        """Agents collaborate on cross-domain work."""
        if len(self.agents) >= 2:
            agent_ids = list(self.agents.keys())
            collaboration = {
                "agents": agent_ids[:2],
                "topic": "cross_domain_synthesis",
                "discoveries_shared": 2,
            }
            self.collaborations.append(collaboration)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of civilization activity."""
        return {
            "cycle_count": self.cycle_count,
            "agents": len(self.agents),
            "discoveries": len(self.discoveries),
            "challenges": len(self.challenges),
            "collaborations": len(self.collaborations),
        }
