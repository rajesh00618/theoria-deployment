"""P9.5: Autonomous Research Institutions — simulated scientific ecosystems."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import AutonomousInstitutionsConfig
from theoria.core.types import ResearchInstitution


@dataclass
class InstitutionCycleResult:
    institutions_active: int = 0
    proposals_reviewed: int = 0
    resources_allocated: float = 0.0
    publications_produced: int = 0
    total_institutions: int = 0


class AutonomousResearchInstitutions:
    def __init__(self, config: Optional[AutonomousInstitutionsConfig] = None):
        self.config = config or AutonomousInstitutionsConfig()
        self.institutions: Dict[str, ResearchInstitution] = {}
        self._lab_names = [
            "Institute for Advanced Study", "Center for Discovery Science",
            "Frontier Research Laboratory", "Innovation Hub",
            "Quantum Research Center", "Bioengineering Institute",
            "Computational Science Lab", "Theoretical Physics Center",
        ]

    def create_institution(self, inst_type: str = "") -> ResearchInstitution:
        if not inst_type:
            inst_type = random.choice(self.config.institution_types)
        domain = random.choice(["physics", "biology", "cs", "math", "chemistry", "medicine"])
        name = random.choice(self._lab_names) + f" ({inst_type})"

        institution = ResearchInstitution(
            name=name,
            institution_type=inst_type,
            domain=domain,
            members=[f"agent_{random.randint(0, 9999)}" for _ in range(random.randint(5, 50))],
        )
        self.institutions[institution.id] = institution
        return institution

    def run_cycle(self) -> InstitutionCycleResult:
        result = InstitutionCycleResult()

        if len(self.institutions) < self.config.max_institutions:
            growth = random.randint(0, 5)
            for _ in range(growth):
                self.create_institution()

        proposals = 0
        publications = 0
        resources = 0.0

        for inst in self.institutions.values():
            if inst.status != "active":
                continue
            if self.config.enable_proposal_review:
                reviewed = random.randint(0, 10)
                inst.proposals_reviewed += reviewed
                proposals += reviewed
            if self.config.enable_resource_allocation:
                allocated = random.uniform(0, 100)
                inst.resources_allocated += allocated
                resources += allocated
            pubs = random.randint(0, 5)
            inst.publications += pubs
            publications += pubs
            if random.random() < 0.005:
                inst.status = "inactive"

        result.institutions_active = sum(1 for i in self.institutions.values() if i.status == "active")
        result.total_institutions = len(self.institutions)
        result.proposals_reviewed = proposals
        result.resources_allocated = resources
        result.publications_produced = publications

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_institutions": len(self.institutions),
            "active": sum(1 for i in self.institutions.values() if i.status == "active"),
            "by_type": {
                t: sum(1 for i in self.institutions.values() if i.institution_type == t)
                for t in self.config.institution_types
            },
        }
