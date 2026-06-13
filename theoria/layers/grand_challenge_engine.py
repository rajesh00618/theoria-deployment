from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import GrandChallenge


@dataclass
class GrandChallengeResult:
    challenges_active: int = 0
    total_progress: float = 0.0
    milestones_reached: int = 0
    experiments_run: int = 0
    sub_challenges_created: int = 0
    collaboration_score: float = 0.0


class GrandChallengeEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.challenges: Dict[str, GrandChallenge] = {}
        self.default_challenges = ["cancer", "climate", "fusion", "materials", "ai_safety", "longevity"]
        self.planning_horizon = (getattr(config, "planning_horizon_years", 10)
                                if config else 10)
        self.cycle_count = 0

    def register_challenge(self, name: str, domain: str = "",
                           description: str = "") -> GrandChallenge:
        challenge = GrandChallenge(
            name=name,
            description=description or f"Solve {name}",
            decade_plan=[
                {"year": y, "milestone": f"{name}_milestone_{y}", "status": "planned"}
                for y in range(1, self.planning_horizon + 1)
            ],
            milestones=[
                {"year": i, "description": f"milestone_{i}", "achieved": False}
                for i in range(1, 11)
            ],
            progress=0.0,
            resources_allocated=0.0,
            status="active",
        )
        self.challenges[challenge.name] = challenge
        return challenge

    def run_experiment(self, challenge_name: str) -> Dict[str, Any]:
        challenge = self.challenges.get(challenge_name)
        if not challenge:
            return {"error": "challenge_not_found"}
        progress_gain = random.uniform(0.001, 0.01)
        challenge.progress = min(1.0, challenge.progress + progress_gain)
        challenge.completed_experiments += 1
        return {
            "challenge": challenge_name,
            "progress_gain": progress_gain,
            "total_progress": challenge.progress,
        }

    def create_sub_challenge(self, parent: str, name: str) -> GrandChallenge:
        if parent not in self.challenges:
            self.register_challenge(parent, "general")
        sub = self.register_challenge(
            f"{parent}:{name}", "",
            description=f"Sub-challenge of {parent}: {name}"
        )
        return sub

    def get_summary(self) -> Dict[str, Any]:
        active = [c for c in self.challenges.values() if c.status == "active"]
        total_progress = sum(c.progress for c in active) / max(1, len(active))
        return {
            "total_challenges": len(self.challenges),
            "active": len(active),
            "avg_progress": total_progress,
            "challenges": {name: c.progress for name, c in self.challenges.items()},
        }

    def run_cycle(self) -> GrandChallengeResult:
        self.cycle_count += 1
        result = GrandChallengeResult()

        for name in self.default_challenges:
            if name not in self.challenges:
                self.register_challenge(name, name)

        for _ in range(random.randint(5, 20)):
            challenge = random.choice(list(self.challenges.keys()))
            self.run_experiment(challenge)
            result.experiments_run += 1

        if random.random() < 0.3:
            parent = random.choice(list(self.challenges.keys()))
            self.create_sub_challenge(parent, f"sub_{self.cycle_count}")
            result.sub_challenges_created += 1

        active = [c for c in self.challenges.values() if c.status == "active"]
        result.challenges_active = len(active)
        if active:
            result.total_progress = sum(c.progress for c in active) / len(active)

        result.milestones_reached = sum(
            1 for c in self.challenges.values()
            for m in c.milestones
            if m.get("achieved") or int(c.progress * 10) >= m.get("year", 0)
        )
        result.collaboration_score = random.uniform(0.4, 0.9)
        return result
