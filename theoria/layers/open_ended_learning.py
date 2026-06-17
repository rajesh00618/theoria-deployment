from __future__ import annotations

import uuid
import hashlib
import random
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import OpenEndedGoal


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class OpenEndedLearningResult:
    goals_set: int = 0
    goals_completed: int = 0
    information_gained: float = 0.0
    curiosity_level: float = 0.0
    competence_level: float = 0.0
    new_skills: List[str] = field(default_factory=list)
    active_goals: List[OpenEndedGoal] = field(default_factory=list)


class OpenEndedLearning:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.goals: List[OpenEndedGoal] = []
        self.completed_goals: List[OpenEndedGoal] = []
        self.curiosity_bonus = (getattr(config, "exploration_bonus", 0.3)
                               if config else 0.3)
        self.cycle_count = 0
        self._rng = random.Random(42)

    def set_goal(self, description: str,
                 domain: str = "general",
                 difficulty: float = 0.5) -> OpenEndedGoal:
        goal = OpenEndedGoal(
            description=description,
            domain=domain,
            difficulty=difficulty,
            status="active",
        )
        self.goals.append(goal)
        return goal

    def pursue_goal(self, goal: OpenEndedGoal) -> float:
        gain = 0.05 + _det_score(f"gain_{goal.id}_{self.cycle_count}") * 0.25
        goal.progress += gain
        if goal.progress >= 1.0:
            goal.status = "completed"
            self.completed_goals.append(goal)
        return goal.progress

    def generate_new_goals(self) -> List[OpenEndedGoal]:
        new_goals = []
        max_goals = getattr(self.config, "max_goals_per_cycle", 5) if self.config else 5
        domains = ["science", "math", "engineering", "software", "general"]
        topics = ["patterns", "structures", "phenomena", "relationships"]
        n_goals = max(1, int(_det_score(f"ngoals_{self.cycle_count}") * max_goals))
        for i in range(n_goals):
            domain = domains[int(_det_score(f"dom_{self.cycle_count}_{i}") * len(domains)) % len(domains)]
            difficulty = 0.2 + _det_score(f"diff_{self.cycle_count}_{i}") * 0.7
            topic = topics[int(_det_score(f"topic_{self.cycle_count}_{i}") * len(topics)) % len(topics)]
            description = "Explore {} in {} (cycle {})".format(
                topic, domain, self.cycle_count)
            goal = self.set_goal(description, domain, difficulty)
            new_goals.append(goal)
        return new_goals

    def run_cycle(self) -> OpenEndedLearningResult:
        self.cycle_count += 1
        result = OpenEndedLearningResult()

        new_goals = self.generate_new_goals()
        result.goals_set = len(new_goals)

        active = [g for g in self.goals if g.status == "active"]
        for g in active[:5]:
            progress = self.pursue_goal(g)
            if g.progress >= 1.0:
                result.goals_completed += 1
                info_gain = g.difficulty * (0.3 + _det_score(f"info_{g.id}") * 0.5)
                result.information_gained += info_gain

        curiosity_delta = _det_score(f"curiosity_{self.cycle_count}") * 0.4 - 0.2
        result.curiosity_level = min(1.0, max(0.0, self.curiosity_bonus * (1 + curiosity_delta)))
        result.competence_level = min(1.0, len(self.completed_goals) / max(
            1, len(self.goals) + len(self.completed_goals)))
        result.active_goals = [g for g in self.goals if g.status == "active"]
        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "cycle_count": self.cycle_count,
            "total_goals": len(self.goals),
            "completed_goals": len(self.completed_goals),
            "active_goals": len([g for g in self.goals if g.status == "active"]),
        }
