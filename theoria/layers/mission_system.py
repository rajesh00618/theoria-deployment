from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import AutonomousMission


@dataclass
class MissionResult:
    missions_active: int = 0
    missions_completed: int = 0
    programs_created: int = 0
    projects_created: int = 0
    tasks_executed: int = 0
    total_progress: float = 0.0


class MissionIntelligenceLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.missions: Dict[str, AutonomousMission] = {}
        self.mission_types = ["energy", "healthcare", "science", "climate", "exploration"]
        self.cycle_count = 0

    def create_mission(self, name: str, mission_type: str,
                       description: str = "") -> AutonomousMission:
        mission = AutonomousMission(
            mission_name=name, mission_type=mission_type,
            description=description or f"Mission: {name}",
            programs=[],
        )
        self.missions[mission.id] = mission
        return mission

    def add_program(self, mission_id: str, program_name: str) -> Dict[str, Any]:
        mission = self.missions.get(mission_id)
        if not mission:
            return {"error": "mission_not_found"}
        program = {
            "id": str(uuid.uuid4()), "name": program_name,
            "projects": [], "progress": 0.0, "status": "active",
        }
        mission.programs.append(program)
        return program

    def add_project(self, program: Dict[str, Any], project_name: str) -> Dict[str, Any]:
        project = {
            "id": str(uuid.uuid4()), "name": project_name,
            "tasks": [], "progress": 0.0, "status": "active",
        }
        program["projects"].append(project)
        return project

    def execute_task(self, project: Dict[str, Any], task_name: str) -> bool:
        task = {
            "id": str(uuid.uuid4()), "name": task_name,
            "status": "completed", "result": f"Result of {task_name}",
        }
        project["tasks"].append(task)
        project["progress"] = min(1.0, project["progress"] + 0.2)
        return True

    def run_cycle(self) -> MissionResult:
        self.cycle_count += 1
        result = MissionResult()

        if random.random() < 0.3:
            mt = random.choice(self.mission_types)
            self.create_mission(f"mission_{self.cycle_count}", mt)
            result.missions_active += 1

        for mid, mission in self.missions.items():
            if mission.status != "active":
                continue
            if random.random() < 0.4:
                program = self.add_program(mid, f"program_{self.cycle_count}")
                result.programs_created += 1
                if random.random() < 0.6:
                    project = self.add_project(program, f"project_{self.cycle_count}")
                    result.projects_created += 1
                    for _ in range(random.randint(1, 3)):
                        self.execute_task(project, f"task_{self.cycle_count}_{_}")
                        result.tasks_executed += 1
                    program["progress"] = sum(p["progress"] for p in program["projects"]) / max(1, len(program["projects"]))

            program_progresses = [p["progress"] for p in mission.programs]
            mission.total_progress = sum(program_progresses) / max(1, len(program_progresses)) if program_progresses else 0.0
            if mission.total_progress >= 1.0:
                mission.status = "completed"
                result.missions_completed += 1

        result.missions_active = len([m for m in self.missions.values() if m.status == "active"])
        active_missions = [m for m in self.missions.values() if m.status == "active"]
        if active_missions:
            result.total_progress = sum(m.total_progress for m in active_missions) / len(active_missions)
        return result
