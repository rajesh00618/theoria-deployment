"""P9.2: Autonomous Scientific Field Creation — invent entirely new disciplines."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _det_score(label: str) -> float:
    return int(hashlib.sha256(label.encode()).hexdigest(), 16) % 10000 / 10000.0

from theoria.core.config import AutonomousFieldCreationConfig
from theoria.core.types import ScientificField


@dataclass
class FieldCreationResult:
    fields_created: int = 0
    total_fields: int = 0
    fields_matured: int = 0
    current_fields: List[str] = field(default_factory=list)


class AutonomousFieldCreator:
    def __init__(self, config: Optional[AutonomousFieldCreationConfig] = None):
        self.config = config or AutonomousFieldCreationConfig()
        self.fields: Dict[str, ScientificField] = {}
        self._field_prefixes = [
            "Quantum", "Computational", "Synthetic", "Information", "Network",
            "Emergent", "Adaptive", "Cognitive", "Evolutionary", "Thermodynamic",
        ]
        self._field_suffixes = [
            "Dynamics", "Informatics", "Thermodynamics", "Mechanics", "Ecology",
            "Genomics", "Synthesis", "Engineering", "Analytics", "Theory",
        ]

    def _generate_field_name(self) -> str:
        prefix = random.choice(self._field_prefixes)
        suffix = random.choice(self._field_suffixes)
        return f"{prefix} {suffix}"

    def create_field(self, parent: str = "") -> ScientificField:
        name = self._generate_field_name()
        while name in [f.name for f in self.fields.values()]:
            name = self._generate_field_name()

        parents = self.config.parent_disciplines.copy()
        if parent and parent not in parents:
            parents.append(parent)

        num_concepts = random.randint(3, 6)
        num_methods = random.randint(3, 5)
        num_questions = random.randint(4, 8)

        field = ScientificField(
            name=name,
            parent_disciplines=random.sample(parents, min(len(parents), random.randint(1, 3))),
            core_concepts=[f"{name.lower().replace(' ', '_')}_concept_{i}" for i in range(num_concepts)],
            methods=[f"{name.lower().replace(' ', '_')}_method_{i}" for i in range(num_methods)],
            open_questions=[f"How does {name.lower()} apply to domain X?" for _ in range(num_questions)],
            maturity=0.1,
        )
        self.fields[field.id] = field
        return field

    def mature_fields(self) -> int:
        matured = 0
        for f in self.fields.values():
            if f.maturity < 1.0:
                f.maturity = min(1.0, f.maturity + 0.05 + _det_score(f"maturity_{f.id}") * 0.1)
                if f.maturity >= self.config.min_maturity_for_completion:
                    matured += 1
        return matured

    def run_cycle(self) -> FieldCreationResult:
        result = FieldCreationResult()

        if random.random() < 0.3 or len(self.fields) < 3:
            parent = random.choice(self.config.parent_disciplines) if self.config.parent_disciplines else ""
            self.create_field(parent)

        matured = self.mature_fields()
        result.fields_created = len(self.fields)
        result.total_fields = len(self.fields)
        result.fields_matured = sum(
            1 for f in self.fields.values()
            if f.maturity >= self.config.min_maturity_for_completion
        )
        result.current_fields = [f.name for f in list(self.fields.values())[-5:]]

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_fields": len(self.fields),
            "field_names": [f.name for f in self.fields.values()],
            "matured": sum(1 for f in self.fields.values() if f.maturity >= 0.8),
        }
