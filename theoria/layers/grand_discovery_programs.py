"""P9.8: Grand Discovery Programs — civilization-scale research agendas."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _det_score(label: str) -> float:
    return int(hashlib.sha256(label.encode()).hexdigest(), 16) % 10000 / 10000.0

from theoria.core.config import GrandDiscoveryProgramsConfig
from theoria.core.types import DiscoveryProgram


@dataclass
class DiscoveryProgramResult:
    programs_active: int = 0
    experiments_total: int = 0
    theories_total: int = 0
    overall_progress: float = 0.0
    program_progress: Dict[str, float] = field(default_factory=dict)
    total_programs: int = 0


class GrandDiscoveryPrograms:
    def __init__(self, config: Optional[GrandDiscoveryProgramsConfig] = None):
        self.config = config or GrandDiscoveryProgramsConfig()
        self.programs: Dict[str, DiscoveryProgram] = {}

        for name in self.config.programs:
            program = DiscoveryProgram(name=name)
            self.programs[program.id] = program

    def run_cycle(self) -> DiscoveryProgramResult:
        result = DiscoveryProgramResult()

        for prog in self.programs.values():
            if prog.status != "active":
                continue

            exp_batch = random.randint(100, self.config.experiments_per_program // 10)
            prog.experiments_planned += exp_batch
            completed = int(exp_batch * (0.3 + _det_score(f"completion_{prog.id}") * 0.5))
            prog.experiments_completed += completed

            theories = random.randint(5, 20)
            prog.theories_generated += theories
            validated = int(theories * (0.2 + _det_score(f"validation_{prog.id}") * 0.4))
            prog.theories_validated += validated

            progress_increment = 0.001 + _det_score(f"progress_{prog.id}") * 0.009
            prog.progress = min(1.0, prog.progress + progress_increment)

            if prog.progress >= 1.0:
                prog.status = "completed"

        total_experiments = sum(p.experiments_completed for p in self.programs.values())
        total_theories = sum(p.theories_validated for p in self.programs.values())
        overall = sum(p.progress for p in self.programs.values()) / max(1, len(self.programs))

        result.programs_active = sum(1 for p in self.programs.values() if p.status == "active")
        result.total_programs = len(self.programs)
        result.experiments_total = total_experiments
        result.theories_total = total_theories
        result.overall_progress = overall
        result.program_progress = {p.name: p.progress for p in self.programs.values()}

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "programs": {p.name: {"progress": p.progress, "status": p.status}
                         for p in self.programs.values()},
            "overall_progress": sum(p.progress for p in self.programs.values()) / max(1, len(self.programs)),
        }
