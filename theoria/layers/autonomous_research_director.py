from __future__ import annotations

import uuid
import random
import hashlib
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import ResearchPortfolio


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


@dataclass
class PortfolioResult:
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    experiments_scheduled: int = 0
    resources_allocated: int = 0
    risk_score: float = 0.0
    priority_distribution: Dict[str, float] = field(default_factory=dict)


class AutonomousResearchDirector:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.portfolio = ResearchPortfolio(name="main")
        self.max_active = (getattr(config, "max_active_projects", 1000)
                          if config else 1000)
        self.max_experiments = (getattr(config, "max_experiments", 100000)
                               if config else 100000)
        self.cycle_count = 0

    def add_project(self, name: str, domain: str = "general",
                    priority: float = 0.5,
                    risk: float = 0.3) -> Dict[str, Any]:
        project = {
            "id": str(uuid.uuid4()),
            "name": name,
            "domain": domain,
            "priority": priority,
            "risk": risk,
            "status": "active",
            "progress": 0.0,
            "experiments_planned": random.randint(10, 1000),
            "experiments_completed": 0,
            "resources_allocated": 0.1 + _det_score(f"research_{name}_resources") * 0.9,
        }
        self.portfolio.projects.append(project)
        self.portfolio.total_projects += 1
        self.portfolio.active_projects += 1
        return project

    def allocate_resources(self) -> Dict[str, float]:
        active = [p for p in self.portfolio.projects if p["status"] == "active"]
        if not active:
            return {}
        total_priority = sum(p["priority"] for p in active) or 1.0
        allocation = {}
        for p in active:
            share = p["priority"] / total_priority
            allocation[p["id"]] = share
            p["resources_allocated"] = share
        self.portfolio.resource_allocation = allocation
        return allocation

    def assess_risk(self) -> Dict[str, float]:
        risk_profile = {}
        for p in self.portfolio.projects:
            risk_profile[p["id"]] = p.get("risk", 0.3) * (1 - p.get("progress", 0))
        self.portfolio.risk_profile = risk_profile
        return risk_profile

    def update_priorities(self) -> Dict[str, float]:
        scores = {}
        for p in self.portfolio.projects:
            base = p.get("priority", 0.5)
            progress_bonus = p.get("progress", 0) * 0.2
            scores[p["id"]] = min(1.0, base + progress_bonus)
        self.portfolio.priority_scores = scores
        return scores

    def run_experiments(self, count: int = 100) -> int:
        active = [p for p in self.portfolio.projects if p["status"] == "active"]
        if not active:
            return 0
        scheduled = 0
        for _ in range(min(count, self.max_experiments)):
            p = random.choice(active)
            p["experiments_completed"] = p.get("experiments_completed", 0) + 1
            p["progress"] = min(1.0, p["experiments_completed"] / max(1, p["experiments_planned"]))
            scheduled += 1
            if p["progress"] >= 1.0 and p["status"] == "active":
                p["status"] = "completed"
                self.portfolio.completed_projects += 1
                self.portfolio.active_projects -= 1
        return scheduled

    def run_cycle(self) -> PortfolioResult:
        self.cycle_count += 1
        result = PortfolioResult()

        if len(self.portfolio.projects) < self.max_active:
            n = random.randint(0, min(5, self.max_active - len(self.portfolio.projects)))
            for i in range(n):
                self.add_project("project_{}_{}".format(self.cycle_count, i),
                                 random.choice(["physics", "biology", "cs", "math"]),
                                 priority=0.3 + _det_score(f"research_proj_{self.cycle_count}_{i}_priority") * 0.6)

        self.allocate_resources()
        self.assess_risk()
        self.update_priorities()

        exp_count = self.run_experiments(count=random.randint(10, 200))
        result.total_projects = self.portfolio.total_projects
        result.active_projects = self.portfolio.active_projects
        result.completed_projects = self.portfolio.completed_projects
        result.experiments_scheduled = exp_count
        if self.portfolio.risk_profile:
            result.risk_score = sum(self.portfolio.risk_profile.values()) / max(1, len(self.portfolio.risk_profile))
        return result
