"""P9.6: Paradigm Shift Generator — create scientific revolutions."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import ParadigmShiftGeneratorConfig
from theoria.core.types import ParadigmShift


@dataclass
class ParadigmShiftResult:
    shifts_generated: int = 0
    shifts_adopted: int = 0
    total_shifts: int = 0
    active_alternatives: int = 0
    recent_shift: str = ""


class ParadigmShiftGenerator:
    def __init__(self, config: Optional[ParadigmShiftGeneratorConfig] = None):
        self.config = config or ParadigmShiftGeneratorConfig()
        self.shifts: Dict[str, ParadigmShift] = {}
        self._old_paradigms = [
            "Classical Mechanics", "Newtonian Gravity", "Standard Model",
            "Lambda-CDM", "Neural Network", "von Neumann Architecture",
            "Centralized Computing", "Reductionist Biology",
        ]
        self._new_paradigm_prefixes = [
            "Quantum", "Emergent", "Network", "Information", "Relational",
            "Distributed", "Adaptive", "Self-Organizing",
        ]

    def _detect_limitations(self, old_paradigm: str) -> List[str]:
        bases = [
            f"Cannot explain {random.choice(['anomalous observations', 'scale-dependent effects', 'emergent phenomena'])}",
            f"Inconsistent with {random.choice(['quantum effects', 'relativistic corrections', 'thermodynamic constraints'])}",
            f"Computational complexity exceeds {random.choice(['polynomial bounds', 'practical limits', 'available resources'])}",
            f"Fails to predict {random.choice(['long-range correlations', 'non-linear dynamics', 'phase transitions'])}",
            f"Assumes {random.choice(['linearity', 'locality', 'separability', 'equilibrium'])} incorrectly",
        ]
        return random.sample(bases, min(len(bases), random.randint(2, 4)))

    def _generate_alternative(self, new_prefix: str) -> str:
        cores = [
            "Framework", "Paradigm", "Theory", "Model", "Approach",
            "Formalism", "Methodology", "Ontology",
        ]
        return f"{new_prefix} {random.choice(cores)}"

    def generate_shift(self) -> ParadigmShift:
        old = random.choice(self._old_paradigms)
        new_prefix = random.choice(self._new_paradigm_prefixes)
        new_name = self._generate_alternative(new_prefix)

        limitations = self._detect_limitations(old)
        num_alternatives = min(self.config.max_alternatives_per_shift, random.randint(2, 4))
        alternatives = [self._generate_alternative(random.choice(self._new_paradigm_prefixes))
                        for _ in range(num_alternatives)]

        evidence = [
            f"Empirical anomaly #{i} contradicts {old}" for i in range(random.randint(2, 4))
        ]

        shift = ParadigmShift(
            old_paradigm_name=old,
            new_paradigm_name=new_name,
            detected_limitations=limitations,
            generated_alternatives=alternatives,
            evidence_for_shift=evidence,
            adopted=random.random() < 0.3,
        )
        self.shifts[shift.id] = shift
        return shift

    def run_cycle(self) -> ParadigmShiftResult:
        result = ParadigmShiftResult()

        if random.random() < 0.4 or len(self.shifts) < 2:
            self.generate_shift()

        adopted = 0
        for s in self.shifts.values():
            if not s.adopted and random.random() < 0.1:
                s.adopted = True
                adopted += 1

        result.shifts_generated = len(self.shifts)
        result.shifts_adopted = sum(1 for s in self.shifts.values() if s.adopted)
        result.total_shifts = len(self.shifts)
        result.active_alternatives = sum(len(s.generated_alternatives) for s in self.shifts.values())

        recent = list(self.shifts.values())[-1] if self.shifts else None
        if recent:
            result.recent_shift = f"{recent.old_paradigm_name} → {recent.new_paradigm_name}"

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_shifts": len(self.shifts),
            "adopted": sum(1 for s in self.shifts.values() if s.adopted),
            "recent": list(self.shifts.values())[-1].new_paradigm_name if self.shifts else "",
        }
