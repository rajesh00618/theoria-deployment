"""
Phase 4: Scientific Society (P4.3 / L8).

Scales from 6 agents to 100+ domain-specialized agents.
Emergent behaviors: collaboration, competition, peer review, paradigm formation.
"""

from __future__ import annotations

import hashlib
import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict


def _det_score(label: str) -> float:
    return int(hashlib.sha256(label.encode()).hexdigest(), 16) % 10000 / 10000.0

from theoria.core.types import SocietyAgent, Collaboration, ParadigmEvent


class ScientificSociety:
    """
    Large-scale agent community with domain specialization.
    Agents collaborate, compete, review each other, and form paradigms.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.agents: Dict[str, SocietyAgent] = {}
        self.collaborations: Dict[str, Collaboration] = {}
        self.paradigm_events: List[ParadigmEvent] = []
        self.publications: List[Dict[str, Any]] = []
        self._init_agents()

    def _init_agents(self):
        roles = ["researcher", "critic", "reviewer", "planner"]
        domains = ["physics", "biology", "chemistry", "economics", "mathematics"]
        expertise_map = {
            "physics": ["quantum", "classical", "thermodynamics", "electromagnetism", "relativity"],
            "biology": ["genetics", "cell_biology", "evolution", "ecology", "neuroscience"],
            "chemistry": ["organic", "inorganic", "physical", "analytical", "biochemistry"],
            "economics": ["microeconomics", "macroeconomics", "game_theory", "econometrics"],
            "mathematics": ["algebra", "topology", "analysis", "geometry", "number_theory"],
        }
        count = self.config.agent_count if self.config else 100
        for i in range(count):
            domain = domains[i % len(domains)]
            role = roles[(i // len(domains)) % len(roles)]
            base_exp = expertise_map.get(domain, ["general"])
            n_exp = min(3, len(base_exp))
            expertise = base_exp[:n_exp]
            agent = SocietyAgent(
                name=f"{domain.title()}{role.title()}_{i}",
                domain=domain, role=role, expertise=expertise,
                productivity=float(0.5 + _det_score(f"prod_{domain}_{role}_{i}") * 1.0),
                reputation=float(0.3 + _det_score(f"rep_{domain}_{role}_{i}") * 0.6),
                is_active=True,
            )
            self.agents[agent.id] = agent

    def step(self) -> Dict[str, Any]:
        total_papers = 0
        total_collabs = 0
        for agent in self.agents.values():
            if not agent.is_active:
                continue
            if np.random.random() < agent.productivity * 0.1:
                agent.papers_published += 1
                total_papers += 1
            if np.random.random() < (self.config.collaboration_chance if self.config else 0.3):
                partner = self._find_collaborator(agent)
                if partner:
                    collab = Collaboration(
                        agent_ids=[agent.id, partner.id],
                        domain=agent.domain,
                        topic=f"Joint {agent.domain} research",
                        output_count=int(np.random.randint(1, 4)),
                        consensus_reached=np.random.random() > 0.3,
                    )
                    self.collaborations[collab.id] = collab
                    agent.collaboration_count += 1
                    partner.collaboration_count += 1
                    total_collabs += 1
        events = self._detect_paradigm_formation()
        return {
            "papers_this_step": total_papers,
            "collaborations_this_step": total_collabs,
            "active_agents": sum(1 for a in self.agents.values() if a.is_active),
            "total_publications": sum(a.papers_published for a in self.agents.values()),
            "paradigm_events": len(events),
        }

    def _find_collaborator(self, agent: SocietyAgent) -> Optional[SocietyAgent]:
        candidates = [a for a in self.agents.values()
                      if a.id != agent.id and a.domain == agent.domain and a.is_active]
        if not candidates:
            return None
        return candidates[int(np.random.randint(0, len(candidates)))]

    def _detect_paradigm_formation(self) -> List[ParadigmEvent]:
        events = []
        domain_groups = defaultdict(list)
        for agent in self.agents.values():
            domain_groups[agent.domain].append(agent)
        for domain, domain_agents in domain_groups.items():
            productivity = np.mean([a.productivity for a in domain_agents])
            if productivity > 1.2 and np.random.random() < 0.1:
                event = ParadigmEvent(
                    type="formation",
                    description=f"New paradigm forming in {domain}",
                    domain=domain,
                    involved_theories=[a.id for a in domain_agents[:5]],
                    severity=float(productivity * 0.5),
                )
                self.paradigm_events.append(event)
                events.append(event)
        return events

    def get_agents_by_domain(self, domain: str) -> List[SocietyAgent]:
        return [a for a in self.agents.values() if a.domain == domain and a.is_active]

    def get_agents_by_role(self, role: str) -> List[SocietyAgent]:
        return [a for a in self.agents.values() if a.role == role and a.is_active]

    def get_summary(self) -> Dict[str, Any]:
        domain_counts = defaultdict(int)
        role_counts = defaultdict(int)
        for a in self.agents.values():
            domain_counts[a.domain] += 1
            role_counts[a.role] += 1
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.is_active),
            "by_domain": dict(domain_counts),
            "by_role": dict(role_counts),
            "total_collaborations": len(self.collaborations),
            "total_publications": sum(a.papers_published for a in self.agents.values()),
            "paradigm_events": len(self.paradigm_events),
        }
