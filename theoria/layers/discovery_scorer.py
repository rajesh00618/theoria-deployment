"""
Discovery Scoring Engine
========================

Estimates novelty, importance, testability, and falsifiability for theories.

Input: Theory
Output: Discovery Score with components
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DiscoveryScore:
    """Score for a discovered theory."""
    theory_id: str
    novelty_score: float  # 0-1, how new is this
    importance_score: float  # 0-1, how significant
    testability_score: float  # 0-1, how testable
    falsifiability_score: float  # 0-1, how falsifiable
    overall_score: float  # 0-1, combined score
    reasoning: str
    timestamp: float = field(default_factory=time.time)


class DiscoveryScoringEngine:
    """
    Scores discoveries on multiple dimensions.
    
    Dimensions:
    - Novelty: Is this genuinely new?
    - Importance: How significant is this?
    - Testability: Can this be tested?
    - Falsifiability: Can this be proven wrong?
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.scored_theories: List[DiscoveryScore] = []
        self.cycle_count = 0
    
    def score_theory(self, theory: Dict[str, Any],
                     existing_knowledge: Optional[Dict] = None) -> DiscoveryScore:
        """
        Score a theory on all dimensions.
        
        Args:
            theory: Theory dictionary with claims, predictions, etc.
            existing_knowledge: Optional existing knowledge base
        
        Returns:
            DiscoveryScore with all dimension scores
        """
        self.cycle_count += 1
        existing_knowledge = existing_knowledge or {}
        
        # Score novelty
        novelty = self._score_novelty(theory, existing_knowledge)
        
        # Score importance
        importance = self._score_importance(theory)
        
        # Score testability
        testability = self._score_testability(theory)
        
        # Score falsifiability
        falsifiability = self._score_falsifiability(theory)
        
        # Combined score
        overall = (
            novelty * 0.30 +
            importance * 0.30 +
            testability * 0.20 +
            falsifiability * 0.20
        )
        
        reasoning = self._generate_reasoning(novelty, importance, testability, falsifiability)
        
        score = DiscoveryScore(
            theory_id=theory.get("id", "unknown"),
            novelty_score=novelty,
            importance_score=importance,
            testability_score=testability,
            falsifiability_score=falsifiability,
            overall_score=overall,
            reasoning=reasoning,
        )
        
        self.scored_theories.append(score)
        return score
    
    def _score_novelty(self, theory: Dict, knowledge: Dict) -> float:
        """Score how novel a theory is."""
        claims = theory.get("claims", [])
        existing_claims = knowledge.get("existing_claims", [])
        
        if not claims:
            return 0.3
        
        # Check how many claims are new
        new_claims = 0
        for claim in claims:
            if not any(self._claims_similar(claim, ec) for ec in existing_claims):
                new_claims += 1
        
        novelty = new_claims / len(claims)
        return min(1.0, max(0.0, novelty))
    
    def _score_importance(self, theory: Dict) -> float:
        """Score how important a theory is."""
        domain = theory.get("domain", "unknown")
        
        # Domain importance weights
        importance_weights = {
            "physics": 0.9,
            "medicine": 0.9,
            "neuroscience": 0.8,
            "biology": 0.8,
            "computer_science": 0.7,
            "psychology": 0.7,
            "economics": 0.6,
            "sociology": 0.5,
        }
        
        base_importance = importance_weights.get(domain, 0.5)
        
        # Adjust by predictions count
        predictions = theory.get("predictions", [])
        prediction_bonus = min(0.2, len(predictions) * 0.05)
        
        return min(1.0, base_importance + prediction_bonus)
    
    def _score_testability(self, theory: Dict) -> float:
        """Score how testable a theory is."""
        predictions = theory.get("predictions", [])
        has_experiment = theory.get("experiment_design") is not None
        has_metrics = len(theory.get("metrics", [])) > 0
        
        testability = 0.3
        if predictions:
            testability += 0.3
        if has_experiment:
            testability += 0.2
        if has_metrics:
            testability += 0.2
        
        return min(1.0, testability)
    
    def _score_falsifiability(self, theory: Dict) -> float:
        """Score how falsifiable a theory is."""
        predictions = theory.get("predictions", [])
        falsification_tests = theory.get("falsification_tests", [])
        
        falsifiability = 0.3
        if predictions:
            falsifiability += 0.3
        if falsification_tests:
            falsifiability += 0.4
        
        return min(1.0, falsifiability)
    
    def _claims_similar(self, c1: str, c2: str) -> bool:
        """Check if two claims are similar."""
        words1 = set(c1.lower().split())
        words2 = set(c2.lower().split())
        overlap = len(words1 & words2)
        return overlap > len(words1) * 0.5
    
    def _generate_reasoning(self, novelty: float, importance: float,
                           testability: float, falsifiability: float) -> str:
        """Generate reasoning for score."""
        strengths = []
        weaknesses = []
        
        if novelty > 0.7:
            strengths.append("highly novel")
        elif novelty < 0.3:
            weaknesses.append("low novelty")
        
        if importance > 0.7:
            strengths.append("important")
        elif importance < 0.3:
            weaknesses.append("low importance")
        
        if testability > 0.7:
            strengths.append("testable")
        elif testability < 0.3:
            weaknesses.append("hard to test")
        
        if falsifiability > 0.7:
            strengths.append("falsifiable")
        elif falsifiability < 0.3:
            weaknesses.append("hard to falsify")
        
        parts = []
        if strengths:
            parts.append(f"Strengths: {', '.join(strengths)}")
        if weaknesses:
            parts.append(f"Weaknesses: {', '.join(weaknesses)}")
        
        return "; ".join(parts) if parts else "Mixed profile"
    
    def rank_theories(self, theories: List[Dict]) -> List[DiscoveryScore]:
        """Rank multiple theories."""
        scores = []
        for theory in theories:
            score = self.score_theory(theory)
            scores.append(score)
        
        scores.sort(key=lambda s: s.overall_score, reverse=True)
        return scores
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of scoring activity."""
        return {
            "cycle_count": self.cycle_count,
            "theories_scored": len(self.scored_theories),
            "avg_overall": sum(s.overall_score for s in self.scored_theories) / max(len(self.scored_theories), 1),
        }
