"""
Discovery Tournament
====================

Competes multiple theories and keeps the best.

Input: Multiple theories
Output: Winner theory with competition results
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TournamentEntry:
    """A theory entered in the tournament."""
    theory: Dict[str, Any]
    score: float
    round_scores: List[float] = field(default_factory=list)
    eliminated: bool = False
    elimination_round: int = -1


@dataclass
class TournamentResult:
    """Result of a tournament."""
    winner: Dict[str, Any]
    winner_score: float
    total_entries: int
    rounds: int
    elimination_history: List[Dict[str, Any]]
    timestamp: float = field(default_factory=time.time)


class DiscoveryTournament:
    """
    Competes multiple theories and keeps the best.
    
    Process:
    1. Generate N theories
    2. Score each theory
    3. Eliminate bottom half each round
    4. Keep winner
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.tournament_history: List[TournamentResult] = []
        self.cycle_count = 0
    
    def run_tournament(self, theories: List[Dict[str, Any]],
                       n_rounds: int = 3) -> TournamentResult:
        """
        Run a tournament between theories.
        
        Args:
            theories: List of theory dictionaries
            n_rounds: Number of elimination rounds
        
        Returns:
            TournamentResult with winner
        """
        self.cycle_count += 1
        
        # Create entries
        entries = [
            TournamentEntry(theory=t, score=self._score_theory(t))
            for t in theories
        ]
        
        elimination_history = []
        
        # Run elimination rounds
        for round_num in range(n_rounds):
            if len(entries) <= 1:
                break
            
            # Sort by score
            entries.sort(key=lambda e: e.score, reverse=True)
            
            # Eliminate bottom half
            n_eliminate = max(1, len(entries) // 2)
            eliminated = entries[-n_eliminate:]
            
            for entry in eliminated:
                entry.eliminated = True
                entry.elimination_round = round_num
            
            elimination_history.append({
                "round": round_num + 1,
                "eliminated": len(eliminated),
                "remaining": len(entries) - len(eliminated),
                "top_score": entries[0].score if entries else 0,
            })
            
            # Keep top half
            entries = entries[:-n_eliminate] if n_eliminate < len(entries) else entries[:1]
        
        # Winner
        entries.sort(key=lambda e: e.score, reverse=True)
        winner = entries[0] if entries else None
        
        result = TournamentResult(
            winner=winner.theory if winner else {},
            winner_score=winner.score if winner else 0,
            total_entries=len(theories),
            rounds=min(n_rounds, len(theories) - 1),
            elimination_history=elimination_history,
        )
        
        self.tournament_history.append(result)
        return result
    
    def _score_theory(self, theory: Dict) -> float:
        """Score a theory for tournament."""
        claims = theory.get("claims", [])
        predictions = theory.get("predictions", [])
        mechanisms = theory.get("mechanisms", [])
        
        score = 0.3
        if claims:
            score += min(0.3, len(claims) * 0.1)
        if predictions:
            score += min(0.2, len(predictions) * 0.05)
        if mechanisms:
            score += min(0.2, len(mechanisms) * 0.1)
        
        return min(1.0, score)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of tournament activity."""
        return {
            "cycle_count": self.cycle_count,
            "tournaments_run": len(self.tournament_history),
            "avg_winner_score": sum(t.winner_score for t in self.tournament_history) / max(len(self.tournament_history), 1),
        }
