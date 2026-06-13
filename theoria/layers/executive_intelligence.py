from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import ExecutiveDecision


@dataclass
class ExecutiveResult:
    active_goals: int = 0
    decisions_made: int = 0
    resources_allocated: int = 0
    risks_assessed: int = 0
    goals_completed: int = 0
    goal_completion_rate: float = 0.0


class ExecutiveIntelligenceLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.goals: Dict[str, Dict[str, Any]] = {}
        self.decisions: List[ExecutiveDecision] = []
        self.max_active = (getattr(config, "max_active_goals", 10000)
                          if config else 10000)
        self.cycle_count = 0

    def add_goal(self, description: str, priority: float = 0.5,
                 domain: str = "general") -> str:
        gid = str(uuid.uuid4())
        self.goals[gid] = {
            "id": gid, "description": description, "priority": priority,
            "domain": domain, "progress": 0.0, "status": "active",
            "resources_allocated": 0.0, "risk_score": random.uniform(0.1, 0.9),
        }
        return gid

    def make_decision(self, context: str, options: List[str]) -> ExecutiveDecision:
        chosen = random.choice(options)
        decision = ExecutiveDecision(
            decision_type="goal_selection",
            context=context, options_considered=options,
            chosen_option=chosen, confidence=random.uniform(0.5, 0.95),
            expected_outcome=f"Expected: {chosen}",
        )
        self.decisions.append(decision)
        return decision

    def allocate_resources(self) -> Dict[str, float]:
        active = {k: v for k, v in self.goals.items() if v["status"] == "active"}
        if not active:
            return {}
        total_priority = sum(v["priority"] for v in active.values()) or 1.0
        allocation = {}
        for gid, goal in active.items():
            share = goal["priority"] / total_priority
            goal["resources_allocated"] = share
            allocation[gid] = share
        return allocation

    def assess_risks(self) -> Dict[str, float]:
        return {gid: g["risk_score"] for gid, g in self.goals.items()}

    def run_cycle(self) -> ExecutiveResult:
        self.cycle_count += 1
        result = ExecutiveResult()

        if len(self.goals) < self.max_active and random.random() < 0.4:
            n = random.randint(0, min(5, self.max_active - len(self.goals)))
            for i in range(n):
                self.add_goal(f"goal_{self.cycle_count}_{i}", priority=random.uniform(0.2, 0.9))

        if random.random() < 0.5:
            self.make_decision(f"cycle_{self.cycle_count}", [f"option_{i}" for i in range(random.randint(2, 5))])
            result.decisions_made += 1

        self.allocate_resources()
        result.resources_allocated = len([g for g in self.goals.values() if g["resources_allocated"] > 0])

        risks = self.assess_risks()
        result.risks_assessed = len(risks)

        for gid, goal in list(self.goals.items()):
            if goal["status"] == "active":
                goal["progress"] = min(1.0, goal["progress"] + random.uniform(0.01, 0.05))
                if goal["progress"] >= 1.0:
                    goal["status"] = "completed"
                    result.goals_completed += 1

        result.active_goals = len([g for g in self.goals.values() if g["status"] == "active"])
        completed = len([g for g in self.goals.values() if g["status"] == "completed"])
        result.goal_completion_rate = completed / max(1, len(self.goals))
        return result
