from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import UniversalToolSpec


@dataclass
class ToolEcosystemResult:
    tools_active: int = 0
    tools_created: int = 0
    tools_retired: int = 0
    tools_evaluated: int = 0
    avg_capability: float = 0.0
    avg_reliability: float = 0.0


class UniversalToolEcosystem:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.tools: Dict[str, UniversalToolSpec] = {}
        self.tool_types = ["analyzer", "compiler", "simulator", "designer", "researcher", "optimizer"]
        self.cycle_count = 0

    def create_tool(self, tool_type: str, name: str) -> UniversalToolSpec:
        tool = UniversalToolSpec(
            tool_type=tool_type, name=name,
            description=f"{tool_type} tool created at cycle {self.cycle_count}",
            capability_score=random.uniform(0.3, 0.9),
            reliability=random.uniform(0.3, 0.9),
            usage_count=0, status="active",
        )
        self.tools[tool.name] = tool
        return tool

    def evaluate_tool(self, tool_name: str) -> float:
        tool = self.tools.get(tool_name)
        if not tool:
            return 0.0
        tool.capability_score = min(1.0, tool.capability_score + random.uniform(-0.1, 0.1))
        tool.reliability = min(1.0, tool.reliability + random.uniform(-0.05, 0.05))
        tool.usage_count += 1
        return (tool.capability_score + tool.reliability) / 2

    def retire_tool(self, tool_name: str) -> bool:
        tool = self.tools.get(tool_name)
        if not tool:
            return False
        tool.status = "retired"
        return True

    def get_active_tools(self) -> List[UniversalToolSpec]:
        return [t for t in self.tools.values() if t.status == "active"]

    def run_cycle(self) -> ToolEcosystemResult:
        self.cycle_count += 1
        result = ToolEcosystemResult()

        n = random.randint(0, 3)
        for i in range(n):
            tt = random.choice(self.tool_types)
            self.create_tool(tt, f"{tt}_v{self.cycle_count}_{i}")
            result.tools_created += 1

        for tname, tool in list(self.tools.items()):
            if tool.status == "active" and random.random() < 0.3:
                self.evaluate_tool(tname)
                result.tools_evaluated += 1
            if tool.reliability < 0.2 and random.random() < 0.3:
                self.retire_tool(tname)
                result.tools_retired += 1

        active = self.get_active_tools()
        result.tools_active = len(active)
        if active:
            result.avg_capability = sum(t.capability_score for t in active) / len(active)
            result.avg_reliability = sum(t.reliability for t in active) / len(active)
        return result
