"""
Phase 7 Artificial General Researcher Pipeline
===============================================

THEORIA as a self-improving autonomous research system.

Input: Domains
Output: Research with self-improvement
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.layers.research_lab import ResearchLabOrchestrator
from theoria.layers.self_improvement_engine import SelfImprovementEngine
from theoria.layers.scientific_civilization import ScientificCivilization
from theoria.layers.recursive_discovery import RecursiveDiscoveryEngine
from theoria.layers.discovery_scorer import DiscoveryScoringEngine
from theoria.layers.verification_loop import RealWorldVerificationLoop
from theoria.layers.research_memory import ResearchMemorySystem


@dataclass
class Phase7Result:
    """Result from Phase 7 Artificial General Researcher."""
    # Lab activity
    agents_active: int
    research_cycles: int
    # Civilization
    discoveries: int
    challenges: int
    collaborations: int
    # Self-improvement
    improvements_made: int
    capability_scores: Dict[str, float]
    # Recursive
    generations: int
    capability_change: float
    # Overall
    pipeline_confidence: float
    execution_time: float
    timestamp: float = field(default_factory=time.time)


class Phase7Pipeline:
    """
    Phase 7 Artificial General Researcher Pipeline.
    
    THEORIA as a self-improving autonomous research system:
    - Multi-agent research lab
    - Scientific civilization with collaboration
    - Self-improvement engine
    - Recursive discovery
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Components
        self.lab = ResearchLabOrchestrator(config)
        self.self_improvement = SelfImprovementEngine(config)
        self.civilization = ScientificCivilization(config)
        self.recursive = RecursiveDiscoveryEngine(config)
        self.scorer = DiscoveryScoringEngine(config)
        self.verifier = RealWorldVerificationLoop(config)
        self.memory = ResearchMemorySystem(config)
        
        self.pipeline_history: List[Phase7Result] = []
    
    def run_pipeline(self, domains: Optional[List[str]] = None,
                     n_cycles: int = 3,
                     n_generations: int = 2) -> Phase7Result:
        """
        Run the Phase 7 Artificial General Researcher pipeline.
        
        Args:
            domains: List of domains to research
            n_cycles: Number of research cycles
            n_generations: Number of self-improvement generations
        
        Returns:
            Phase7Result with research and improvements
        """
        t0 = time.time()
        
        # Setup
        if domains is None:
            domains = ["physics", "biology", "mathematics", "economics"]
        
        self.lab.setup_lab(domains)
        self.civilization.setup_civilization(domains)
        
        # Run research cycles
        for _ in range(n_cycles):
            self.lab.run_cycle()
            self.civilization.run_cycle()
        
        # Self-improvement
        research_history = [
            {"success": True, "quality": 0.7, "novel": True}
            for _ in range(10)
        ]
        performance = self.self_improvement.analyze_performance(research_history)
        improvements = self.self_improvement.suggest_improvements(performance)
        for imp in improvements:
            self.self_improvement.apply_improvement(imp)
        
        # Recursive improvement
        for _ in range(n_generations):
            self.recursive.improve()
        
        # Store in memory
        self.memory.store(
            category="discovery",
            domain="meta",
            content=f"Phase 7 run: {len(self.civilization.discoveries)} discoveries",
            importance=0.8,
        )
        
        execution_time = time.time() - t0
        
        # Calculate confidence
        confidence = self._compute_confidence()
        
        result = Phase7Result(
            agents_active=len(self.lab.agents),
            research_cycles=self.lab.cycle_count,
            discoveries=len(self.civilization.discoveries),
            challenges=len(self.civilization.challenges),
            collaborations=len(self.civilization.collaborations),
            improvements_made=len(improvements),
            capability_scores=self.recursive.capabilities.copy(),
            generations=self.recursive.generation_count,
            capability_change=self.recursive.capabilities.get("problem_finding", 0.5) - 0.5,
            pipeline_confidence=confidence,
            execution_time=execution_time,
        )
        
        self.pipeline_history.append(result)
        return result
    
    def _compute_confidence(self) -> float:
        """Compute overall pipeline confidence."""
        scores = []
        
        if self.lab.agents:
            scores.append(min(1.0, len(self.lab.agents) / 4))
        
        if self.civilization.discoveries:
            scores.append(min(1.0, len(self.civilization.discoveries) / 10))
        
        avg_capability = sum(self.recursive.capabilities.values()) / len(self.recursive.capabilities)
        scores.append(avg_capability)
        
        return sum(scores) / max(len(scores), 1)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline activity."""
        return {
            "pipelines_run": len(self.pipeline_history),
            "lab_summary": self.lab.get_summary(),
            "civilization_summary": self.civilization.get_summary(),
            "self_improvement_summary": self.self_improvement.get_summary(),
            "recursive_summary": self.recursive.get_summary(),
        }
