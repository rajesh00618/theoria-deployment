from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import ToolSpec


@dataclass
class ToolCreationResult:
    tools_created: int = 0
    tools_tested: int = 0
    tools_deployed: int = 0
    tools_available: int = 0
    avg_novelty: float = 0.0
    avg_utility: float = 0.0
    types_distribution: Dict[str, int] = field(default_factory=dict)


class ToolCreationEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.tools: Dict[str, ToolSpec] = {}
        self.tool_types = ["simulator", "algorithm", "analyzer", "compiler", "research_system"]
        self.max_per_cycle = (getattr(config, "max_tools_per_cycle", 3)
                             if config else 3)
        self.cycle_count = 0

    def create_tool(self, tool_type: str, purpose: str) -> ToolSpec:
        tool = ToolSpec(
            name=f"{tool_type}_{purpose[:20]}_{self.cycle_count}",
            tool_type=tool_type,
            description=purpose,
            novelty_score=random.uniform(0.3, 0.9),
            utility_score=random.uniform(0.3, 0.9),
            status="specified",
        )
        self.tools[tool.name] = tool
        return tool

    def test_tool(self, tool_name: str) -> bool:
        tool = self.tools.get(tool_name)
        if not tool:
            return False
        passes = random.random() < max(tool.novelty_score, tool.utility_score)
        if passes:
            tool.status = "deployed"
        else:
            tool.status = "specified"
        return passes

    def deploy_tool(self, tool_name: str) -> bool:
        tool = self.tools.get(tool_name)
        if not tool:
            return False
        tool.status = "deployed"
        return True

    def get_available_tools(self) -> List[ToolSpec]:
        return [t for t in self.tools.values() if t.status == "deployed"]

    def run_cycle(self) -> ToolCreationResult:
        self.cycle_count += 1
        result = ToolCreationResult()

        n = random.randint(0, self.max_per_cycle)
        for i in range(n):
            tool_type = random.choice(self.tool_types)
            purpose = f"task_{self.cycle_count}_{i}"
            tool = self.create_tool(tool_type, purpose)
            result.tools_created += 1
            if self.test_tool(tool.name):
                result.tools_tested += 1
            if random.random() < 0.7:
                self.deploy_tool(tool.name)
                result.tools_deployed += 1

        result.tools_available = len(self.get_available_tools())
        all_tools = list(self.tools.values())
        if all_tools:
            result.avg_novelty = sum(t.novelty_score for t in all_tools) / len(all_tools)
            result.avg_utility = sum(t.utility_score for t in all_tools) / len(all_tools)
        for t in self.tool_types:
            count = sum(1 for tool in self.tools.values() if tool.tool_type == t)
            if count > 0:
                result.types_distribution[t] = count
        return result
