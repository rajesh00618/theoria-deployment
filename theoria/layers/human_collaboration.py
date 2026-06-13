from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import CollaborationRecord


@dataclass
class CollaborationResult:
    interactions: int = 0
    teaching_sessions: int = 0
    debates: int = 0
    explanations: int = 0
    mentoring_sessions: int = 0
    team_projects: int = 0
    avg_quality: float = 0.0


class HumanCollaboration:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.collaborations: List[CollaborationRecord] = []
        self.cycle_count = 0

    def interact(self, partner: str, mode: str, topic: str,
                 success: bool = True) -> CollaborationRecord:
        record = CollaborationRecord(
            partner_type=partner,
            interaction_type=mode,
            topic=topic,
            feedback_score=random.uniform(0.4, 0.95),
            collaboration_quality=random.uniform(0.4, 0.95),
            outcomes=[f"{mode}_on_{topic[:30]}"],
        )
        self.collaborations.append(record)
        return record

    def teach(self, topic: str, student: str = "human") -> CollaborationRecord:
        return self.interact(partner=student, mode="teaching", topic=topic)

    def debate(self, topic: str, opponent: str = "human") -> CollaborationRecord:
        return self.interact(partner=opponent, mode="debate", topic=topic)

    def explain(self, concept: str, audience: str = "human") -> CollaborationRecord:
        return self.interact(partner=audience, mode="explaining", topic=concept)

    def mentor(self, mentee: str, skill: str) -> CollaborationRecord:
        return self.interact(partner=mentee, mode="mentoring", topic=skill)

    def team_up(self, project: str, members: List[str]) -> List[CollaborationRecord]:
        records = []
        for member in members:
            record = self.interact(partner=member, mode="teamwork", topic=project)
            records.append(record)
        return records

    def run_cycle(self) -> CollaborationResult:
        self.cycle_count += 1
        result = CollaborationResult()

        if random.random() < 0.6:
            self.teach(f"concept_{self.cycle_count}")
            result.teaching_sessions += 1
        if random.random() < 0.4:
            self.debate(f"topic_{self.cycle_count}")
            result.debates += 1
        if random.random() < 0.7:
            self.explain(f"concept_{self.cycle_count}")
            result.explanations += 1
        if random.random() < 0.3:
            self.mentor("student", f"skill_{self.cycle_count}")
            result.mentoring_sessions += 1
        if random.random() < 0.3:
            self.team_up(f"project_{self.cycle_count}", ["alice", "bob", "carol"])
            result.team_projects += 1

        result.interactions = len(self.collaborations)
        quality_values = [c.collaboration_quality for c in self.collaborations[-20:]]
        if quality_values:
            result.avg_quality = sum(quality_values) / len(quality_values)
        return result
