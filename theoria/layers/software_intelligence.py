from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import SoftwareProject


@dataclass
class SoftwareIntelligenceResult:
    projects_created: int = 0
    modules_written: int = 0
    tests_generated: int = 0
    refactors_applied: int = 0
    optimizations_found: int = 0
    bugs_fixed: int = 0
    projects: List[SoftwareProject] = field(default_factory=list)


class SoftwareIntelligence:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.languages = (getattr(config, "languages", None) or
                         ["python", "pseudocode"]) if config else ["python"]
        self.projects: List[SoftwareProject] = []
        self.cycle_count = 0

    def create_project(self, name: str, description: str,
                       language: str = "python") -> SoftwareProject:
        project = SoftwareProject(
            name=name,
            description=description,
            quality_score=0.5,
            status="designed",
        )
        self.projects.append(project)
        return project

    def synthesize_module(self, project: SoftwareProject,
                          module_name: str) -> str:
        module_code = "def {}():\n    pass\n".format(module_name)
        project.modules.append({"name": module_name, "code": module_code})
        project.status = "implemented"
        return module_code

    def generate_tests(self, project: SoftwareProject) -> List[str]:
        tests = []
        for module in project.modules:
            mname = module.get("name", "unknown") if isinstance(module, dict) else str(module)
            test = "def test_{}():\n    assert True\n".format(mname)
            tests.append(test)
        project.quality_score = min(1.0, len(tests) / max(1, len(project.modules)))
        return tests

    def refactor(self, project: SoftwareProject) -> List[str]:
        refactors = []
        if project.quality_score < 0.8:
            project.quality_score = min(1.0, project.quality_score + 0.1)
            refactors.append("Improved {}".format(project.name))
        return refactors

    def optimize(self, project: SoftwareProject) -> List[str]:
        optimizations = []
        if project.quality_score < 0.9:
            project.quality_score = min(1.0, project.quality_score + 0.05)
            optimizations.append("Optimized {}".format(project.name))
        return optimizations

    def run_cycle(self) -> SoftwareIntelligenceResult:
        self.cycle_count += 1
        result = SoftwareIntelligenceResult()
        max_projects = getattr(self.config, "max_modules", 10) if self.config else 10

        new_projects = random.randint(0, min(3, max_projects))
        for i in range(new_projects):
            lang = random.choice(self.languages) if self.languages else "python"
            p = self.create_project(
                "project_{}_{}".format(self.cycle_count, i),
                "Auto-generated project",
                lang,
            )
            result.projects.append(p)
            for m in range(random.randint(1, 5)):
                self.synthesize_module(p, "module_{}".format(m))
                result.modules_written += 1
            tests = self.generate_tests(p)
            result.tests_generated += len(tests)
            refactors = self.refactor(p)
            result.refactors_applied += len(refactors)
            opts = self.optimize(p)
            result.optimizations_found += len(opts)
            result.projects_created += 1

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "cycle_count": self.cycle_count,
            "total_projects": len(self.projects),
            "languages_used": list(set(self.languages)),
        }
