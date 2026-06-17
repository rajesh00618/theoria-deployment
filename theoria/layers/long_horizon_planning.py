from __future__ import annotations

import uuid
import hashlib
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import LongHorizonPlan


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class Milestone:
    milestone_id: str = ""
    description: str = ""
    step: int = 0
    status: str = "pending"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class PlanExecutionResult:
    plan: Optional[LongHorizonPlan] = None
    milestones_completed: int = 0
    milestones_total: int = 0
    risk_level: float = 0.0
    progress: float = 0.0
    issues: List[str] = field(default_factory=list)
    repairs_applied: int = 0


class LongHorizonPlanning:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.plans: List[LongHorizonPlan] = []
        self.milestones: Dict[str, List[Milestone]] = {}
        self.cycle_count = 0
        self.max_steps = (getattr(config, "max_plan_steps", 1000)
                         if config else 1000)

    def create_plan(self, objective: str,
                    domain: str = "general",
                    steps: int = 100) -> LongHorizonPlan:
        plan = LongHorizonPlan(
            name=objective,
            description="Plan for: " + objective,
            domain=domain,
            total_steps=min(steps, self.max_steps),
            status="in_progress",
        )
        self.plans.append(plan)
        plan_milestones = []
        interval = getattr(self.config, "milestone_interval", 100) if self.config else 100
        for s in range(interval, plan.total_steps + 1, interval):
            m = Milestone(
                milestone_id=str(uuid.uuid4()),
                description="Milestone at step {} for {}".format(s, objective),
                step=s,
                status="pending",
            )
            plan_milestones.append(m)
            plan.milestones.append({"id": m.milestone_id, "description": m.description, "step": m.step})
        self.milestones[plan.id] = plan_milestones
        return plan

    def execute_plan(self, plan: LongHorizonPlan) -> PlanExecutionResult:
        result = PlanExecutionResult(plan=plan)
        plan_milestones = self.milestones.get(plan.id, [])

        progress_gain = 0.05 + _det_score(f"progress_{plan.id}_{self.cycle_count}") * 0.1
        plan.completed_steps = min(plan.total_steps, plan.completed_steps + int(plan.total_steps * progress_gain))
        progress = plan.completed_steps / max(1, plan.total_steps)

        for m in plan_milestones:
            if m.status == "pending" and plan.completed_steps >= m.step:
                if random.random() < 0.8:
                    m.status = "completed"
                    result.milestones_completed += 1
                else:
                    result.issues.append("Milestone {} delayed".format(m.milestone_id))

        if result.issues and random.random() < 0.5:
            result.repairs_applied = len(result.issues)
            result.issues = []

        result.milestones_total = len(plan_milestones)
        result.progress = progress
        result.risk_level = max(0.0, 0.3 - progress * 0.2)

        if plan.completed_steps >= plan.total_steps:
            plan.status = "completed"

        return result

    def run_cycle(self) -> List[PlanExecutionResult]:
        self.cycle_count += 1
        results = []
        active = [p for p in self.plans if p.status == "in_progress"]
        if not active:
            active.append(self.create_plan(
                "Cycle {} exploration".format(self.cycle_count),
                steps=random.randint(50, 200)))
        for p in active[:3]:
            result = self.execute_plan(p)
            results.append(result)
        return results

    def get_summary(self) -> Dict[str, Any]:
        return {
            "cycle_count": self.cycle_count,
            "total_plans": len(self.plans),
            "active_plans": len([p for p in self.plans if p.status == "in_progress"]),
            "completed_plans": len([p for p in self.plans if p.status == "completed"]),
        }
