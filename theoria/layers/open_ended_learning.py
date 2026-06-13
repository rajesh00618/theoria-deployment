from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import OpenEndedGoal


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
        gain = random.uniform(0.05, 0.3)
        goal.progress += gain
        if goal.progress >= 1.0:
            goal.status = "completed"
            self.completed_goals.append(goal)
        return goal.progress

    def generate_new_goals(self) -> List[OpenEndedGoal]:
        new_goals = []
        max_goals = getattr(self.config, "max_goals_per_cycle", 5) if self.config else 5
        domains = ["science", "math", "engineering", "software", "general"]
        for _ in range(random.randint(1, max_goals)):
            domain = random.choice(domains)
            difficulty = random.uniform(0.2, 0.9)
            description = "Explore {} in {} (cycle {})".format(
                random.choice(["patterns", "structures", "phenomena", "relationships"]),
                domain, self.cycle_count)
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
                info_gain = g.difficulty * random.uniform(0.3, 0.8)
                result.information_gained += info_gain

        result.curiosity_level = min(1.0, self.curiosity_bonus * (
            1 + random.uniform(-0.2, 0.2)))
        result.competence_level = min(1.0, len(self.completed_goals) / max(
            1, len(self.goals) + len(self.completed_goals)))
        result.active_goals = [g for g in self.goals if g.status == "active"]
        return result
