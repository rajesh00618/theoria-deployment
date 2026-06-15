"""
Discovery Prioritization Engine
===============================

Ranks research opportunities by promise.

Input: List of research opportunities
Output: Ranked list with scores
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PrioritizedDiscovery:
    """A ranked research opportunity."""
    opportunity_id: str
    domain: str
    topic: str
    priority_score: float  # 0-1, overall priority
    novelty_score: float
    importance_score: float
    feasibility_score: float
    impact_potential: float
    reasoning: str


@dataclass
class PrioritizationResult:
    """Result of prioritization."""
    ranked_discoveries: List[PrioritizedDiscovery]
    top_recommendation: PrioritizedDiscovery
    total_evaluated: int
    timestamp: float = field(default_factory=time.time)


class DiscoveryPrioritizationEngine:
    """
    Ranks research opportunities by promise.
    
    Considers:
    - Novelty: How new is this?
    - Importance: How significant?
    - Feasibility: How achievable?
    - Impact potential: What's the potential impact?
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.prioritization_history: List[PrioritizationResult] = []
        self.cycle_count = 0
    
    def prioritize(self, opportunities: List[Dict]) -> PrioritizationResult:
        """
        Rank research opportunities by promise.
        
        Args:
            opportunities: List of opportunity dictionaries
        
        Returns:
            PrioritizationResult with ranked discoveries
        """
        self.cycle_count += 1
        
        ranked = []
        for opp in opportunities:
            priority = self._compute_priority(opp)
            ranked.append(PrioritizedDiscovery(
                opportunity_id=opp.get("id", ""),
                domain=opp.get("domain", ""),
                topic=opp.get("topic", ""),
                priority_score=priority,
                novelty_score=opp.get("novelty_score", 0.5),
                importance_score=opp.get("importance_score", 0.5),
                feasibility_score=opp.get("feasibility_score", 0.5),
                impact_potential=self._estimate_impact(opp),
                reasoning=self._generate_reasoning(opp, priority),
            ))
        
        # Sort by priority
        ranked.sort(key=lambda d: d.priority_score, reverse=True)
        
        result = PrioritizationResult(
            ranked_discoveries=ranked,
            top_recommendation=ranked[0] if ranked else None,
            total_evaluated=len(ranked),
        )
        
        self.prioritization_history.append(result)
        return result
    
    def _compute_priority(self, opportunity: Dict) -> float:
        """Compute priority score."""
        novelty = opportunity.get("novelty_score", 0.5)
        importance = opportunity.get("importance_score", 0.5)
        feasibility = opportunity.get("feasibility_score", 0.5)
        
        # Weighted combination
        priority = (
            novelty * 0.35 +
            importance * 0.35 +
            feasibility * 0.20 +
            self._estimate_impact(opportunity) * 0.10
        )
        
        return min(1.0, max(0.0, priority))
    
    def _estimate_impact(self, opportunity: Dict) -> float:
        """Estimate potential impact."""
        importance = opportunity.get("importance_score", 0.5)
        novelty = opportunity.get("novelty_score", 0.5)
        
        # Higher novelty + importance = higher potential impact
        impact = (importance + novelty) / 2
        return min(1.0, impact)
    
    def _generate_reasoning(self, opportunity: Dict, priority: float) -> str:
        """Generate reasoning for priority score."""
        if priority > 0.7:
            return "High priority: novel, important, and feasible"
        elif priority > 0.5:
            return "Medium priority: worth investigating"
        else:
            return "Lower priority: consider after higher-priority items"
    
    def select_top(self, ranked: List[PrioritizedDiscovery],
                   n: int = 3) -> List[PrioritizedDiscovery]:
        """Select top N discoveries."""
        return ranked[:n]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of prioritization activity."""
        return {
            "cycle_count": self.cycle_count,
            "total_prioritized": sum(r.total_evaluated for r in self.prioritization_history),
            "last_top_recommendation": (
                self.prioritization_history[-1].top_recommendation.topic
                if self.prioritization_history else None
            ),
        }
