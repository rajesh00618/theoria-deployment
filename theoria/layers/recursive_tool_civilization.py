"""P9.7: Recursive Tool Civilization — systems that invent tool-building systems."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import RecursiveToolCivilizationConfig
from theoria.core.types import RecursiveTool


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class RecursiveToolResult:
    tools_created: int = 0
    total_tools: int = 0
    max_recursion_reached: int = 0
    tools_by_level: Dict[int, int] = field(default_factory=dict)
    performance_score: float = 0.0


class RecursiveToolCivilization:
    def __init__(self, config: Optional[RecursiveToolCivilizationConfig] = None):
        self.config = config or RecursiveToolCivilizationConfig()
        self.tools: Dict[str, RecursiveTool] = {}
        self._tool_names = [
            "Hypothesis Generator", "Experiment Runner", "Data Analyzer",
            "Theory Validator", "Paper Writer", "Literature Searcher",
            "Simulation Engine", "Pattern Detector", "Model Optimizer",
        ]

    def _generate_tools(self, count: int, prefix: str = "") -> List[str]:
        return [f"{prefix}{random.choice(self._tool_names)}_{i}" for i in range(count)]

    def create_tool(self, recursion_level: int = 0) -> RecursiveTool:
        name = f"{'Meta-' * recursion_level}{random.choice(self._tool_names)}_{len(self.tools)}"
        capabilities = [
            f"capability_{random.randint(0, 99)}" for _ in range(random.randint(2, 5))
        ]
        produced = self._generate_tools(random.randint(1, 4), prefix="Meta-" * recursion_level)

        tool = RecursiveTool(
            name=name,
            recursion_level=recursion_level,
            tools_produced=produced,
            capabilities=capabilities,
            performance_score=0.5 + _det_score(f"perftool_{name}_{recursion_level}") * 0.5,
        )
        self.tools[tool.id] = tool
        return tool

    def discover_next_recursion(self) -> Optional[RecursiveTool]:
        current_max = max((t.recursion_level for t in self.tools.values()), default=-1)
        next_level = current_max + 1
        if next_level > self.config.max_recursion_depth:
            return None
        # Lower-level tools produce higher-level tools
        return self.create_tool(recursion_level=next_level)

    def run_cycle(self) -> RecursiveToolResult:
        result = RecursiveToolResult()

        if len(self.tools) < self.config.max_tools:
            created = random.randint(5, 20)
            for _ in range(created):
                level = 0
                if random.random() < 0.2 and max((t.recursion_level for t in self.tools.values()), default=0) < self.config.max_recursion_depth:
                    level = 1
                if random.random() < 0.05:
                    max_level = max((t.recursion_level for t in self.tools.values()), default=0)
                    level = min(max_level + 1, self.config.max_recursion_depth)
                self.create_tool(level)

            if random.random() < 0.1:
                self.discover_next_recursion()

        for t in self.tools.values():
            delta = _det_score(f"perfup_{t.id}_{self.cycle_count if hasattr(self, 'cycle_count') else 0}") * 0.15 - 0.05
            t.performance_score = max(0.0, min(1.0, t.performance_score + delta))

        result.tools_created = len(self.tools)
        result.total_tools = len(self.tools)
        result.max_recursion_reached = max((t.recursion_level for t in self.tools.values()), default=0)
        for level in range(self.config.max_recursion_depth + 1):
            count = sum(1 for t in self.tools.values() if t.recursion_level == level)
            result.tools_by_level[level] = count
        result.performance_score = sum(t.performance_score for t in self.tools.values()) / max(1, len(self.tools))

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_tools": len(self.tools),
            "max_recursion": max((t.recursion_level for t in self.tools.values()), default=0),
            "avg_performance": sum(t.performance_score for t in self.tools.values()) / max(1, len(self.tools)),
        }
