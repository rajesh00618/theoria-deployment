"""
Phase 6 Autonomous Research Lab Pipeline
=========================================

Multi-agent research lab with specialized agents.

Input: Domains
Output: Coordinated research across domains
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.layers.research_lab import ResearchLabOrchestrator
from theoria.layers.knowledge_gap_detector import KnowledgeGapDetector
from theoria.layers.discovery_scorer import DiscoveryScoringEngine
from theoria.layers.discovery_tournament import DiscoveryTournament
from theoria.layers.verification_loop import RealWorldVerificationLoop
from theoria.layers.research_memory import ResearchMemorySystem


@dataclass
class Phase6Result:
    """Result from Phase 6 Research Lab."""
    agents_active: int
    research_cycles: int
    discoveries_shared: int
    cross_domain_connections: int
    theories_competed: int
    winner_theory: str
    verification_passed: bool
    discoveries_stored: int
    pipeline_confidence: float
    execution_time: float
    timestamp: float = field(default_factory=time.time)


class Phase6Pipeline:
    """
    Phase 6 Autonomous Research Lab Pipeline.
    
    Multi-agent system with:
    - Physics Agent
    - Biology Agent
    - Math Agent
    - Economics Agent
    - Research Manager
    
    Working together and sharing discoveries.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Lab components
        self.lab = ResearchLabOrchestrator(config)
        self.gap_detector = KnowledgeGapDetector(config)
        self.scorer = DiscoveryScoringEngine(config)
        self.tournament = DiscoveryTournament(config)
        self.verifier = RealWorldVerificationLoop(config)
        self.memory = ResearchMemorySystem(config)
        
        self.pipeline_history: List[Phase6Result] = []
    
    def run_pipeline(self, domains: Optional[List[str]] = None,
                     n_cycles: int = 3,
                     domain_knowledge: Optional[Dict[str, Dict]] = None) -> Phase6Result:
        """
        Run the Phase 6 multi-agent research pipeline.
        
        Args:
            domains: List of domains to research
            n_cycles: Number of research cycles
            domain_knowledge: Optional knowledge for each domain
        
        Returns:
            Phase6Result with coordinated research
        """
        t0 = time.time()
        domain_knowledge = domain_knowledge or {}
        
        # Setup lab
        self.lab.setup_lab(domains)
        
        # Load knowledge into agents
        for agent_id, agent in self.lab.agents.items():
            if agent.domain in domain_knowledge:
                agent.knowledge = domain_knowledge[agent.domain]
        
        # Run multiple research cycles
        for _ in range(n_cycles):
            self.lab.run_cycle()
        
        # Get agent states
        agent_states = self.lab.get_agent_states()
        
        # Collect discoveries from all agents
        all_theories = []
        for agent_id, agent in self.lab.agents.items():
            for discovery in agent.knowledge.keys():
                all_theories.append({
                    "id": f"{agent_id}_{discovery[:20]}",
                    "name": discovery,
                    "domain": agent.domain,
                    "claims": [discovery],
                    "predictions": [],
                })
        
        # Run tournament on collected theories
        if all_theories:
            tournament_result = self.tournament.run_tournament(all_theories[:10])
            winner = tournament_result.winner
        else:
            tournament_result = None
            winner = None
        
        # Verify winner
        if winner:
            verification = self.verifier.verify(winner, [])
        else:
            verification = None
        
        # Store discoveries
        for agent_id, agent in self.lab.agents.items():
            for discovery in agent.knowledge.keys():
                self.memory.store(
                    category="discovery",
                    domain=agent.domain,
                    content=f"{agent_id}: {discovery}",
                    importance=0.6,
                )
        
        execution_time = time.time() - t0
        
        # Calculate confidence
        confidence = self._compute_confidence(
            agent_states, tournament_result, verification
        )
        
        result = Phase6Result(
            agents_active=len(self.lab.agents),
            research_cycles=self.lab.cycle_count,
            discoveries_shared=self.lab.manager.discoveries_shared if self.lab.manager else 0,
            cross_domain_connections=self.lab._count_cross_domain_connections(),
            theories_competed=tournament_result.total_entries if tournament_result else 0,
            winner_theory=winner.get("name", "") if winner else "",
            verification_passed=verification.overall_passed if verification else False,
            discoveries_stored=len(self.memory.memories),
            pipeline_confidence=confidence,
            execution_time=execution_time,
        )
        
        self.pipeline_history.append(result)
        return result
    
    def _compute_confidence(self, agent_states, tournament_result, verification) -> float:
        """Compute overall pipeline confidence."""
        scores = []
        
        if agent_states:
            scores.append(min(1.0, len(agent_states) / 4))
        
        if tournament_result and tournament_result.winner:
            scores.append(tournament_result.winner_score)
        
        if verification:
            scores.append(verification.overall_confidence)
        
        return sum(scores) / max(len(scores), 1)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline activity."""
        return {
            "pipelines_run": len(self.pipeline_history),
            "lab_summary": self.lab.get_summary(),
            "memory_summary": self.memory.get_summary(),
        }
