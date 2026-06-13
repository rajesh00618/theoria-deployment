"""
Phase 4: Autonomous Research Programs (P4.9).

Instead of single questions, creates multi-year research programs.
Example: Understanding Aging — 100 Questions, 500 Experiments, 50 Theories.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import ResearchProgram


class ResearchProgramManager:
    """
    Manages multi-year autonomous research programs.
    Each program has questions, experiments, and theories linked together.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.programs: Dict[str, ResearchProgram] = {}
        self._init_default_programs()

    def _init_default_programs(self):
        programs_data = [
            ("Understanding Aging", "biology",
             "Understand the molecular mechanisms of aging and develop interventions",
             ["What causes cellular senescence?", "How does telomere length affect lifespan?",
              "Can epigenetic changes be reversed?", "What role do mitochondria play?",
              "How does caloric restriction extend lifespan?"]),
            ("Quantum Gravity", "physics",
             "Unify quantum mechanics and general relativity",
             ["What is the quantum nature of spacetime?", "Can gravity be quantized?",
              "What happens at Planck scale?", "Do gravitons exist?",
              "How does entanglement affect spacetime?"]),
            ("Climate Modeling", "physics",
             "Build predictive climate models with uncertainty quantification",
             ["How do cloud feedbacks amplify warming?", "What is the role of ocean circulation?",
              "Can we predict tipping points?", "How do aerosols affect precipitation?"]),
            ("Neuroplasticity", "biology",
             "Understand how the brain rewires itself throughout life",
             ["What triggers synaptic pruning?", "How do new neurons integrate?",
              "What is the role of sleep in plasticity?",
              "Can learning be optimized through targeted stimulation?"]),
            ("Economic Forecasting", "economics",
             "Develop robust economic forecasting using causal inference",
             ["What causes recessions?", "How do interest rates affect employment?",
              "Can we predict market bubbles?", "What is the role of inequality in growth?"]),
        ]
        for title, domain, objective, questions in programs_data:
            prog = ResearchProgram(
                name=title, domain=domain, description=objective,
                questions=questions, total_questions=100,
                total_experiments=500, total_theories=50,
                status="active",
            )
            self.programs[prog.id] = prog

    def create_program(self, title: str, domain: str, objective: str,
                       questions: List[str]) -> ResearchProgram:
        prog = ResearchProgram(
            name=title, domain=domain, description=objective,
            questions=questions, total_questions=len(questions),
            status="active",
        )
        self.programs[prog.id] = prog
        return prog

    def add_experiment(self, program_id: str, experiment_id: str) -> bool:
        prog = self.programs.get(program_id)
        if not prog:
            return False
        if experiment_id not in prog.experiment_ids:
            prog.experiment_ids.append(experiment_id)
        prog.total_experiments = len(prog.experiment_ids)
        self._update_progress(prog)
        return True

    def add_theory(self, program_id: str, theory_id: str) -> bool:
        prog = self.programs.get(program_id)
        if not prog:
            return False
        if theory_id not in prog.theory_ids:
            prog.theory_ids.append(theory_id)
        prog.total_theories = len(prog.theory_ids)
        self._update_progress(prog)
        return True

    def _update_progress(self, prog: ResearchProgram):
        weights = {"questions": 0.2, "experiments": 0.5, "theories": 0.3}
        q_prog = min(len(prog.questions) / max(prog.total_questions, 1), 1.0)
        e_prog = min(len(prog.experiment_ids) / max(prog.total_experiments, 1), 1.0)
        t_prog = min(len(prog.theory_ids) / max(prog.total_theories, 1), 1.0)
        prog.progress = (weights["questions"] * q_prog +
                         weights["experiments"] * e_prog +
                         weights["theories"] * t_prog)
        if prog.progress >= 0.95:
            prog.status = "completed"

    def get_active_programs(self) -> List[ResearchProgram]:
        return [p for p in self.programs.values() if p.status == "active"]

    def get_summary(self) -> Dict[str, Any]:
        active = self.get_active_programs()
        return {
            "total_programs": len(self.programs),
            "active": len(active),
            "completed": sum(1 for p in self.programs.values() if p.status == "completed"),
            "total_experiments": sum(len(p.experiment_ids) for p in self.programs.values()),
            "total_theories": sum(len(p.theory_ids) for p in self.programs.values()),
        }
