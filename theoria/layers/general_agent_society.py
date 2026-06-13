from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import GeneralAgent


@dataclass
class AgentSocietyResult:
    active_agents: int = 0
    avg_productivity: float = 0.0
    collaboration_events: int = 0
    collective_intelligence: float = 0.0
    findings: List[str] = field(default_factory=list)
    role_distribution: Dict[str, int] = field(default_factory=dict)


class GeneralAgentSociety:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.agents: Dict[str, GeneralAgent] = {}
        self.roles = (getattr(config, "agent_roles", []) if config else [
            "scientist", "engineer", "mathematician", "doctor", "economist",
            "teacher", "programmer", "strategist", "policy_analyst",
        ])
        self.target_count = (getattr(config, "target_agent_count", 500)
                            if config else 500)
        self.cycle_count = 0
        self.collaboration_graph: Dict[str, List[str]] = {}

        self._initialize_agents()

    def _initialize_agents(self, count: Optional[int] = None) -> None:
        n = count or min(50, self.target_count)
        for i in range(n):
            role = random.choice(self.roles)
            agent = GeneralAgent(
                name="Agent_{}_{}".format(role, i),
                role=role,
                domain="general",
                productivity=random.uniform(0.3, 0.9),
                is_active=True,
            )
            self.agents[agent.id] = agent

    def add_agents(self, count: int) -> List[GeneralAgent]:
        added = []
        base = len(self.agents)
        for i in range(count):
            role = random.choice(self.roles)
            agent = GeneralAgent(
                name="Agent_{}_{}".format(role, base + i),
                role=role,
                domain="general",
                productivity=random.uniform(0.3, 0.9),
                is_active=True,
            )
            self.agents[agent.id] = agent
            added.append(agent)
        return added

    def scale_to_target(self) -> int:
        needed = self.target_count - len(self.agents)
        if needed > 0:
            batch = min(needed, 100)
            self.add_agents(batch)
            return batch
        return 0

    def run_collaboration(self) -> List[str]:
        events = []
        active_ids = [aid for aid, a in self.agents.items() if a.is_active]
        if len(active_ids) < 2:
            return events

        pairs = min(len(active_ids) // 2, 10)
        for _ in range(pairs):
            a1 = random.choice(active_ids)
            a2 = random.choice(active_ids)
            if a1 != a2:
                if a1 not in self.collaboration_graph:
                    self.collaboration_graph[a1] = []
                if a2 not in self.collaboration_graph:
                    self.collaboration_graph[a2] = []
                self.collaboration_graph[a1].append(a2)
                self.collaboration_graph[a2].append(a1)
                events.append("{} collaborated with {}".format(
                    self.agents[a1].name, self.agents[a2].name))
        return events

    def update_productivity(self) -> float:
        total = 0.0
        for agent in self.agents.values():
            if agent.is_active:
                noise = random.uniform(-0.05, 0.05)
                agent.productivity = max(0.1, min(1.0, agent.productivity + noise))
                total += agent.productivity
        return total / max(1, len([a for a in self.agents.values() if a.is_active]))

    def run_cycle(self) -> AgentSocietyResult:
        self.cycle_count += 1
        result = AgentSocietyResult()

        self.scale_to_target()

        collab_events = self.run_collaboration()
        avg_prod = self.update_productivity()

        active_count = len([a for a in self.agents.values() if a.is_active])
        result.active_agents = active_count
        result.avg_productivity = avg_prod
        result.collaboration_events = len(collab_events)
        result.collective_intelligence = min(1.0, avg_prod * (
            1 + math.log(active_count + 1) * 0.1))

        for role in self.roles:
            count = len([a for a in self.agents.values()
                        if a.role == role and a.is_active])
            result.role_distribution[role] = count

        if self.cycle_count % 5 == 0 and self.cycle_count > 0:
            result.findings.append(
                "Agent society reached {} active agents across {} roles".format(
                    active_count, len([r for r, c in result.role_distribution.items() if c > 0])))

        return result

    def get_agents_by_role(self, role: str) -> List[GeneralAgent]:
        return [a for a in self.agents.values() if a.role == role and a.is_active]
