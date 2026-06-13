"""
Phase 2: Research Planner.

Creates autonomous research agendas:
- Select important questions
- Rank hypotheses
- Schedule experiments
- Allocate compute resources

Outputs: daily goals, weekly plans, long-term research programs.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

from theoria.core.types import (
    ResearchGap, ResearchQuestion, ResearchProgram,
    ResearchQuestion, CandidateHypothesis,
)


class ResearchPlanner:
    """
    Creates and manages autonomous research agendas.
    Prioritizes research directions and allocates resources.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.programs: Dict[str, ResearchProgram] = {}
        self.completion_history: List[Dict[str, Any]] = []

    def create_program(self, name: str, domain: str,
                       long_term_goal: str,
                       gaps: List[ResearchGap],
                       questions: List[ResearchQuestion],
                       estimated_cycles: int = 100) -> ResearchProgram:
        """Create a new research program from gaps and questions."""
        program = ResearchProgram(
            name=name,
            description=long_term_goal,
            domain=domain,
            long_term_goal=long_term_goal,
            gap_ids=[g.id for g in gaps],
            question_ids=[q.id for q in questions],
            estimated_cycles=estimated_cycles,
            compute_allocated=estimated_cycles * 1e19,
        )

        sorted_gaps = sorted(gaps, key=lambda g: g.overall_score, reverse=True)
        sorted_questions = sorted(questions, key=lambda q: q.overall_score, reverse=True)

        if sorted_questions:
            program.short_term_goals = [
                f"Investigate: {sorted_questions[i].question_text[:80]}"
                for i in range(min(3, len(sorted_questions)))
            ]

        if len(sorted_gaps) > 3:
            program.medium_term_goals = [
                f"Address gap: {sorted_gaps[i].description[:80]}"
                for i in range(min(3, len(sorted_gaps)))
            ]

        program.next_milestone = program.short_term_goals[0] if program.short_term_goals else ""

        self.programs[program.id] = program
        return program

    def prioritize_questions(self, questions: List[ResearchQuestion],
                              n_select: int = 5) -> List[ResearchQuestion]:
        """Select the most important questions to work on."""
        scored = []
        for q in questions:
            priority_score = (
                0.4 * q.importance
                + 0.3 * q.novelty
                + 0.3 * q.answerability
            )
            scored.append((priority_score, q))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [q for _, q in scored[:n_select]]

    def rank_hypotheses(self, hypotheses: List[CandidateHypothesis],
                         top_k: int = 5) -> List[CandidateHypothesis]:
        """Rank hypotheses by combined score."""
        scored = []
        for h in hypotheses:
            rank_score = (
                0.3 * h.explanatory_power
                + 0.2 * h.falsifiability
                + 0.2 * h.novelty
                + 0.15 * h.parsimony
                + 0.15 * h.confidence
            )
            scored.append((rank_score, h))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [h for _, h in scored[:top_k]]

    def plan_cycle(self, program_id: str,
                   available_compute: float) -> Dict[str, Any]:
        """Create a plan for one research cycle within a program."""
        program = self.programs.get(program_id)
        if not program:
            return {"error": "Program not found"}

        compute_per_cycle = available_compute * 0.8
        compute_remaining = compute_per_cycle

        tasks = []
        for goal in program.short_term_goals:
            task_compute = min(compute_remaining * 0.4, 1e19)
            tasks.append({
                "type": "investigation",
                "description": goal,
                "compute_allocated": task_compute,
                "priority": "high",
                "estimated_cycles": 5,
            })
            compute_remaining -= task_compute
            if compute_remaining < 1e17:
                break

        for goal in program.medium_term_goals:
            if compute_remaining < 1e17:
                break
            task_compute = min(compute_remaining * 0.3, 5e18)
            tasks.append({
                "type": "exploration",
                "description": goal,
                "compute_allocated": task_compute,
                "priority": "medium",
                "estimated_cycles": 20,
            })
            compute_remaining -= task_compute

        program.cycles_completed += 1
        program.compute_spent += compute_per_cycle - compute_remaining
        program.progress = min(
            program.cycles_completed / max(program.estimated_cycles, 1),
            1.0,
        )

        return {
            "program_id": program_id,
            "program_name": program.name,
            "cycle": program.cycles_completed,
            "progress": program.progress,
            "tasks": tasks,
            "compute_used": compute_per_cycle - compute_remaining,
            "compute_remaining": compute_remaining,
        }

    def allocate_resources(self, programs: List[ResearchProgram],
                           total_compute: float) -> Dict[str, float]:
        """Allocate compute resources across programs."""
        strategy = self.config.resource_allocation_strategy if self.config else "greedy"
        allocations: Dict[str, float] = {}

        if not programs:
            return allocations

        if strategy == "greedy":
            sorted_progs = sorted(
                programs,
                key=lambda p: (1 - p.progress) * len(p.question_ids),
                reverse=True,
            )
            per_program = total_compute / max(len(programs), 1)
            for prog in sorted_progs:
                allocations[prog.id] = per_program

        elif strategy == "fair":
            per_program = total_compute / max(len(programs), 1)
            for prog in programs:
                allocations[prog.id] = per_program

        elif strategy == "importance_weighted":
            total_weight = sum(
                (1 - p.progress) * max(len(p.question_ids), 1)
                for p in programs
            )
            for prog in programs:
                if total_weight > 0:
                    weight = (1 - prog.progress) * max(len(prog.question_ids), 1)
                    allocations[prog.id] = total_compute * weight / total_weight
                else:
                    allocations[prog.id] = total_compute / max(len(programs), 1)

        return allocations

    def get_daily_goals(self, program_id: str) -> List[str]:
        """Get daily research goals for a program."""
        program = self.programs.get(program_id)
        if not program:
            return []
        return program.short_term_goals[:3]

    def get_weekly_plan(self, program_id: str) -> Dict[str, Any]:
        """Get a weekly research plan."""
        program = self.programs.get(program_id)
        if not program:
            return {"error": "Program not found"}

        return {
            "program": program.name,
            "domain": program.domain,
            "weekly_goals": program.short_term_goals,
            "milestones": [program.next_milestone] if program.next_milestone else [],
            "estimated_compute": program.compute_allocated * 0.1,
            "cycles_planned": min(7, program.estimated_cycles - program.cycles_completed),
        }

    def record_completion(self, program_id: str, task_description: str,
                           success: bool, notes: str = "") -> None:
        """Record task completion for learning."""
        self.completion_history.append({
            "program_id": program_id,
            "task": task_description,
            "success": success,
            "notes": notes,
            "timestamp": time.time(),
        })

    def get_summary(self) -> Dict[str, Any]:
        return {
            "active_programs": len([p for p in self.programs.values() if p.status == "active"]),
            "total_programs": len(self.programs),
            "completions_logged": len(self.completion_history),
            "programs": [
                {
                    "id": pid,
                    "name": p.name,
                    "domain": p.domain,
                    "status": p.status,
                    "progress": p.progress,
                    "cycles": p.cycles_completed,
                }
                for pid, p in self.programs.items()
            ],
        }
