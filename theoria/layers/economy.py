"""
Phase 4: Scientific Economy (P4.8).

Research resources become limited: compute, time, budget, experiments.
THEORIA must decide what is worth studying and what should be abandoned.
Creates realistic scientific prioritization.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import ResourceAllocation


class ScientificEconomy:
    """
    Resource-constrained scientific economy.
    Allocates compute, time, budget, and experiment slots across projects.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.compute_remaining: float = config.compute_per_cycle if config else 1e26
        self.time_remaining: float = config.time_per_cycle_hours if config else 24.0
        self.budget_remaining: float = config.budget_per_cycle if config else 10000.0
        self.slots_remaining: int = config.experiment_slots_per_cycle if config else 10
        self.expenditure_log: List[Dict[str, Any]] = []
        self.cycle: int = 0

    def reset_cycle(self):
        c = self.config
        self.compute_remaining = c.compute_per_cycle if c else 1e26
        self.time_remaining = c.time_per_cycle_hours if c else 24.0
        self.budget_remaining = c.budget_per_cycle if c else 10000.0
        self.slots_remaining = c.experiment_slots_per_cycle if c else 10
        self.cycle += 1

    def request_allocation(self, project_id: str, compute_needed: float,
                           time_needed: float, budget_needed: float,
                           slots_needed: int, priority: float = 0.5) -> Optional[ResourceAllocation]:
        if (self.compute_remaining < compute_needed or
            self.time_remaining < time_needed or
            self.budget_remaining < budget_needed or
            self.slots_remaining < slots_needed):
            return None
        alloc = ResourceAllocation(
            project_id=project_id,
            compute_budget=compute_needed,
            time_budget_hours=time_needed,
            monetary_budget=budget_needed,
            experiment_slots=slots_needed,
            priority=priority,
        )
        self.compute_remaining -= compute_needed
        self.time_remaining -= time_needed
        self.budget_remaining -= budget_needed
        self.slots_remaining -= slots_needed
        self.allocations[alloc.id] = alloc
        self.expenditure_log.append({
            "cycle": self.cycle,
            "project": project_id,
            "compute": compute_needed,
            "time": time_needed,
            "budget": budget_needed,
            "slots": slots_needed,
            "timestamp": time.time(),
        })
        return alloc

    def should_study(self, expected_value: float, cost: float,
                     risk: float = 0.5) -> bool:
        roi = expected_value / max(cost, 0.01)
        return roi > risk

    def should_abandon(self, progress: float, cost_so_far: float,
                       expected_remaining_value: float) -> bool:
        if progress < 0.1 and cost_so_far > 1000:
            return True
        if expected_remaining_value < cost_so_far * 0.1:
            return True
        return False

    def get_priority_ranking(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for p in projects:
            expected_value = p.get("expected_value", 0)
            cost = p.get("cost", 1)
            risk = p.get("risk", 0.5)
            score = expected_value / (cost * risk + 0.01)
            scored.append((score, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored]

    def get_summary(self) -> Dict[str, Any]:
        return {
            "compute_remaining": self.compute_remaining,
            "time_remaining": self.time_remaining,
            "budget_remaining": self.budget_remaining,
            "slots_remaining": self.slots_remaining,
            "total_allocations": len(self.allocations),
            "cycle": self.cycle,
            "total_compute_spent": sum(e["compute"] for e in self.expenditure_log),
            "total_budget_spent": sum(e["budget"] for e in self.expenditure_log),
        }
