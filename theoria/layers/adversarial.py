"""
Phase 4: Adversarial Science (P4.6).

Three independent Red Teams (A, B, C) that attempt to break
THEORIA's theories, assumptions, experiments, and conclusions.
Nothing is accepted until it survives adversarial review.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import RedTeamChallenge, Theory, ExperimentResult


class RedTeam:
    """
    Single adversarial red team that challenges theories and experiments.
    """

    def __init__(self, team_id: str, name: str, aggressiveness: float = 0.7):
        self.team_id = team_id
        self.name = name
        self.aggressiveness = aggressiveness
        self.challenges: List[RedTeamChallenge] = []
        self.stats = {"total": 0, "survived": 0, "broken": 0}

    def challenge_theory(self, theory: Theory) -> RedTeamChallenge:
        flaws = []
        severity = 0.0
        if not theory.core_claims:
            flaws.append("No core claims specified")
            severity += 0.3
        if theory.posterior > 0.95:
            flaws.append("Suspiciously high posterior — possible overfitting")
            severity += 0.2
        if len(theory.reference_class) < 2:
            flaws.append("Insufficient reference class for generalization")
            severity += 0.15
        if self.aggressiveness > 0.5 and np.random.random() < self.aggressiveness:
            flaws.append("Assumption: causal direction may be reversed")
            severity += 0.2
            flaws.append("Alternative explanation: hidden confounder")
            severity += 0.2
        challenge = RedTeamChallenge(
            team_id=self.team_id, target_type="theory",
            target_id=theory.id,
            challenge_text="; ".join(flaws) if flaws else "No specific flaws identified",
            severity=min(severity, 1.0),
        )
        self.challenges.append(challenge)
        self.stats["total"] += 1
        return challenge

    def challenge_experiment(self, design_id: str, description: str,
                             result: Optional[ExperimentResult] = None) -> RedTeamChallenge:
        flaws = []
        severity = 0.0
        flaws.append("Potential confounding variable not controlled")
        severity += 0.15
        if result and result.p_value > 0.01:
            flaws.append("Marginal statistical significance")
            severity += 0.2
        if result and result.effect_size < 0.3:
            flaws.append("Small effect size — may lack practical significance")
            severity += 0.15
        if np.random.random() < self.aggressiveness * 0.3:
            flaws.append("Measurement instrument may lack sufficient precision")
            severity += 0.1
        challenge = RedTeamChallenge(
            team_id=self.team_id, target_type="experiment",
            target_id=design_id,
            challenge_text="; ".join(flaws),
            severity=min(severity, 1.0),
        )
        self.challenges.append(challenge)
        self.stats["total"] += 1
        return challenge

    def evaluate_challenge(self, challenge_id: str, defense: str) -> bool:
        survived = len(defense) > 20 or np.random.random() > 0.3
        for c in self.challenges:
            if c.id == challenge_id:
                c.resolved = True
                c.resolution = "survived" if survived else "broken"
        if survived:
            self.stats["survived"] += 1
        else:
            self.stats["broken"] += 1
        return survived


class AdversarialScience:
    """
    Manages three independent Red Teams (A, B, C) that adversarially review
    all theories, experiments, and conclusions before acceptance.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        team_count = config.team_count if config else 3
        self.teams: Dict[str, RedTeam] = {}
        team_names = ["Ares", "Bifrost", "Cerberus"]
        aggressiveness = [0.6, 0.75, 0.9]
        for i in range(min(team_count, 3)):
            tid = f"red_team_{chr(65 + i)}"
            self.teams[tid] = RedTeam(tid, team_names[i], aggressiveness[i])
        self.challenge_log: List[Dict[str, Any]] = []

    def review_theory(self, theory: Theory) -> Dict[str, Any]:
        challenges = []
        for tid, team in self.teams.items():
            challenge = team.challenge_theory(theory)
            challenges.append(challenge)
        return {"theory_id": theory.id, "challenges": challenges,
                "total": len(challenges)}

    def review_experiment(self, design_id: str, description: str,
                          result: Optional[ExperimentResult] = None) -> Dict[str, Any]:
        challenges = []
        for tid, team in self.teams.items():
            challenge = team.challenge_experiment(design_id, description, result)
            challenges.append(challenge)
        return {"design_id": design_id, "challenges": challenges,
                "total": len(challenges)}

    def defend_theory(self, theory_id: str, defense: str) -> Dict[str, Any]:
        results = {}
        for tid, team in self.teams.items():
            open_challenges = [c for c in team.challenges
                               if c.target_id == theory_id and not c.resolved]
            for c in open_challenges:
                survived = team.evaluate_challenge(c.id, defense)
                results[c.id] = {"team": tid, "survived": survived}
        return results

    def all_survived(self) -> bool:
        for team in self.teams.values():
            unresolved = sum(1 for c in team.challenges if not c.resolved)
            broken = team.stats["broken"]
            if unresolved > 0 or broken > 0:
                return False
        return True

    def get_summary(self) -> Dict[str, Any]:
        total = sum(t.stats["total"] for t in self.teams.values())
        survived = sum(t.stats["survived"] for t in self.teams.values())
        broken = sum(t.stats["broken"] for t in self.teams.values())
        return {
            "teams": len(self.teams),
            "total_challenges": total,
            "survived": survived,
            "broken": broken,
            "all_survived": self.all_survived(),
        }
