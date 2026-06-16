from __future__ import annotations

import uuid
import hashlib
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import AgentTeam


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class OrganizationResult:
    teams_created: int = 0
    agents_recruited: int = 0
    agents_retired: int = 0
    agents_trained: int = 0
    total_agents: int = 0
    avg_productivity: float = 0.0


class OrganizationBuilder:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.teams: Dict[str, AgentTeam] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.max_agents = (getattr(config, "max_agents", 10000)
                          if config else 10000)
        self.specializations = ["research", "engineering", "analysis", "exploration", "optimization"]
        self.cycle_count = 0

    def recruit_agent(self, specialization: str) -> str:
        aid = str(uuid.uuid4())[:8]
        self.agents[aid] = {
            "id": aid, "specialization": specialization,
            "productivity": 0.3 + _det_score(f"prod_{aid}") * 0.6,
            "training_level": 0, "status": "active",
        }
        return aid

    def create_team(self, name: str, purpose: str,
                    agent_ids: List[str]) -> AgentTeam:
        team = AgentTeam(
            name=name, agent_ids=agent_ids,
            team_purpose=purpose,
            specialization_areas=list(set(
                self.agents[a]["specialization"] for a in agent_ids if a in self.agents
            )),
        )
        self.teams[team.id] = team
        return team

    def train_agent(self, agent_id: str) -> bool:
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        agent["training_level"] = min(10, agent["training_level"] + 1)
        agent["productivity"] = min(1.0, agent["productivity"] + 0.05)
        return True

    def retire_agent(self, agent_id: str) -> bool:
        agent = self.agents.get(agent_id)
        if not agent:
            return False
        agent["status"] = "retired"
        return True

    def run_cycle(self) -> OrganizationResult:
        self.cycle_count += 1
        result = OrganizationResult()

        n = random.randint(1, 5)
        for i in range(n):
            if len(self.agents) < self.max_agents:
                spec = random.choice(self.specializations)
                self.recruit_agent(spec)
                result.agents_recruited += 1

        if len(self.agents) >= 3 and random.random() < 0.3:
            members = random.sample(list(self.agents.keys()), min(3, len(self.agents)))
            team = self.create_team(f"team_{self.cycle_count}", f"purpose_{self.cycle_count}", members)
            result.teams_created += 1

        for aid, agent in list(self.agents.items()):
            if agent["status"] == "active" and random.random() < 0.2:
                self.train_agent(aid)
                result.agents_trained += 1
            if agent["productivity"] < 0.1 and random.random() < 0.1:
                self.retire_agent(aid)
                result.agents_retired += 1

        result.total_agents = len([a for a in self.agents.values() if a["status"] == "active"])
        active_agents = [a for a in self.agents.values() if a["status"] == "active"]
        if active_agents:
            result.avg_productivity = sum(a["productivity"] for a in active_agents) / len(active_agents)
        return result
