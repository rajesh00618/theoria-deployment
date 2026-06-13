from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import AgencyGoal


@dataclass
class AgencyResult:
    active_goals: int = 0
    goals_completed: int = 0
    goals_generated: int = 0
    decisions_made: int = 0
    actions_executed: int = 0
    goal_completion_rate: float = 0.0
    decision_quality: float = 0.0


class AgencyLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.goals: Dict[str, AgencyGoal] = {}
        self.active_goal_ids: List[str] = []
        self.completed_goal_ids: List[str] = []
        self.max_active = (getattr(config, "max_active_goals", 20)
                          if config else 20)
        self.cycle_count = 0

    def generate_goal(self, description: str, priority: float = 0.5,
                      source: str = "self_generated") -> AgencyGoal:
        goal = AgencyGoal(
            description=description,
            source=source,
            priority=priority,
            complexity=random.uniform(0.3, 0.9),
            estimated_effort=random.uniform(1.0, 10.0),
            status="active",
            subgoals=[],
            progress=0.0,
        )
        self.goals[goal.id] = goal
        self.active_goal_ids.append(goal.id)
        return goal

    def decide(self, context: str, options: List[str]) -> Tuple[str, float]:
        weights = []
        for opt in options:
            relevance = random.uniform(0.3, 0.9)
            confidence = random.uniform(0.4, 0.95)
            weights.append(relevance * confidence)
        total = sum(weights) or 1.0
        probs = [w / total for w in weights]
        choice = random.choices(options, weights=probs, k=1)[0]
        confidence = probs[options.index(choice)]
        return choice, confidence

    def execute_action(self, action: str, target_goal_id: str) -> bool:
        goal = self.goals.get(target_goal_id)
        if not goal:
            return False
        progress_gain = random.uniform(0.01, 0.1)
        goal.progress = min(1.0, goal.progress + progress_gain)
        if goal.progress >= 1.0 and goal.status == "active":
            goal.status = "completed"
            self.active_goal_ids.remove(target_goal_id)
            self.completed_goal_ids.append(target_goal_id)
        return True

    def prioritize_goals(self) -> List[AgencyGoal]:
        active = [self.goals[gid] for gid in self.active_goal_ids if gid in self.goals]
        active.sort(key=lambda g: g.priority, reverse=True)
        return active

    def run_cycle(self) -> AgencyResult:
        self.cycle_count += 1
        result = AgencyResult()

        if len(self.active_goal_ids) < self.max_active and random.random() < 0.5:
            n = random.randint(0, min(3, self.max_active - len(self.active_goal_ids)))
            for i in range(n):
                self.generate_goal(
                    f"goal_{self.cycle_count}_{i}",
                    priority=random.uniform(0.3, 0.9),
                )
                result.goals_generated += 1

        active = self.prioritize_goals()
        for goal in active[:5]:
            options = [f"approach_{i}" for i in range(random.randint(2, 5))]
            choice, conf = self.decide(goal.description, options)
            result.decisions_made += 1
            success = self.execute_action(choice, goal.id)
            if success:
                result.actions_executed += 1

        result.active_goals = len(self.active_goal_ids)
        result.goals_completed = len(self.completed_goal_ids)
        completed = len(self.completed_goal_ids)
        total = completed + len(self.active_goal_ids)
        result.goal_completion_rate = completed / max(1, total)
        result.decision_quality = random.uniform(0.5, 0.9)
        return result
