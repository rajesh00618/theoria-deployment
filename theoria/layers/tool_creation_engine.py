from __future__ import annotations

import uuid
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
            novelty_score=self._compute_novelty(tool_type),
            utility_score=self._compute_utility(tool_type),
            status="specified",
        )
        self.tools[tool.name] = tool
        return tool

    def _compute_novelty(self, tool_type: str) -> float:
        existing_count = sum(1 for t in self.tools.values() if t.tool_type == tool_type)
        novelty = max(0.3, min(0.9, 0.9 - existing_count * 0.1))
        return novelty

    def _compute_utility(self, tool_type: str) -> float:
        type_utility = {
            "simulator": 0.7,
            "algorithm": 0.8,
            "analyzer": 0.6,
            "compiler": 0.5,
            "research_system": 0.9,
        }
        return type_utility.get(tool_type, 0.5)

    def test_tool(self, tool_name: str) -> bool:
        tool = self.tools.get(tool_name)
        if not tool:
            return False
        novelty = tool.novelty_score
        utility = tool.utility_score
        score = 0.4 * novelty + 0.6 * utility
        passes = score > 0.5
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

        n = min(self.max_per_cycle, max(1, self.cycle_count % (self.max_per_cycle + 1)))
        for i in range(n):
            tool_type = self.tool_types[i % len(self.tool_types)]
            purpose = f"task_{self.cycle_count}_{i}"
            tool = self.create_tool(tool_type, purpose)
            result.tools_created += 1
            if self.test_tool(tool.name):
                result.tools_tested += 1
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
