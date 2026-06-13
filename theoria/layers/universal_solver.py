from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import UniversalProblem


@dataclass
class Solution:
    solution_id: str = ""
    problem_id: str = ""
    approach: str = ""
    description: str = ""
    quality: float = 0.0
    steps: List[str] = field(default_factory=list)


@dataclass
class SolverResult:
    problems_posed: int = 0
    solutions_found: int = 0
    best_quality: float = 0.0
    approaches_used: Dict[str, int] = field(default_factory=dict)
    solutions: List[Solution] = field(default_factory=list)


class UniversalProblemSolver:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.problems: List[UniversalProblem] = []
        self.solutions: List[Solution] = []
        self.domains = (getattr(config, "domains", []) if config else [
            "research", "engineering", "business", "education",
            "technology", "policy",
        ])
        self.approaches = (getattr(config, "solution_approaches", []) if config else [
            "analytical", "empirical", "creative", "hybrid",
        ])
        self.cycle_count = 0

    def pose_problem(self, description: str, domain: str = "general",
                     difficulty: float = 0.5) -> UniversalProblem:
        problem = UniversalProblem(
            description=description,
            domain=domain,
            difficulty=difficulty,
            status="unsolved",
            constraints=[],
        )
        self.problems.append(problem)
        return problem

    def solve(self, problem: UniversalProblem,
              approach: Optional[str] = None) -> Optional[Solution]:
        approach = approach or random.choice(self.approaches)
        quality_threshold = (getattr(self.config, "quality_threshold", 0.5)
                            if self.config else 0.5)

        quality = random.uniform(0.2, 0.95)
        if quality < quality_threshold:
            return None

        solution = Solution(
            solution_id=str(uuid.uuid4()),
            problem_id=problem.id,
            approach=approach,
            description="Solution using {} approach for '{}'".format(
                approach, problem.description),
            quality=quality,
            steps=["Analyze", "Design", "Implement", "Verify"],
        )
        self.solutions.append(solution)
        problem.solution_found = True
        return solution

    def run_cycle(self) -> SolverResult:
        self.cycle_count += 1
        result = SolverResult()
        max_solutions = (getattr(self.config, "max_solutions_per_cycle", 5)
                        if self.config else 5)

        new_problems = random.randint(0, 3)
        for i in range(new_problems):
            domain = random.choice(self.domains)
            difficulty = random.uniform(0.3, 0.9)
            self.pose_problem(
                "Problem {} in {} (cycle {})".format(i, domain, self.cycle_count),
                domain, difficulty)
            result.problems_posed += 1

        open_problems = [p for p in self.problems if p.status == "unsolved"]
        for p in open_problems[:max_solutions]:
            approach = random.choice(self.approaches)
            solution = self.solve(p, approach)
            if solution:
                result.solutions.append(solution)
                result.solutions_found += 1
                if solution.quality > result.best_quality:
                    result.best_quality = solution.quality
                result.approaches_used[approach] = result.approaches_used.get(approach, 0) + 1

        return result
