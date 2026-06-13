"""P10.10 / L26: Singularity Coordination Layer — civilization-wide coordination, resource optimization, system synchronization."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import SingularityCoordinationConfig
from theoria.core.types import SingularityMetric


@dataclass
class CoordinationResult:
    metrics_tracked: int = 0
    metrics_on_target: int = 0
    coordination_score: float = 0.0
    discovery_rate: float = 0.0
    knowledge_growth: float = 0.0
    self_sustaining: bool = False


class SingularityCoordinationLayer:
    def __init__(self, config: Optional[SingularityCoordinationConfig] = None):
        self.config = config or SingularityCoordinationConfig()
        self.metrics: Dict[str, SingularityMetric] = {}
        self._init_metrics()
        self.cycle_count = 0

    def _init_metrics(self) -> None:
        for name, target in self.config.metric_targets.items():
            metric = SingularityMetric(
                metric_name=name,
                value=random.uniform(target * 0.5, target * 0.9),
                target=target,
            )
            self.metrics[metric.id] = metric

    def _update_metrics(self) -> int:
        on_target = 0
        for m in self.metrics.values():
            # Simulate organic growth toward targets
            delta = random.uniform(-0.05, 0.08) * m.target
            m.value = max(0.0, m.value + delta)

            if m.value >= m.target * 0.9:
                m.trend = "improving"
                on_target += 1
            elif m.value >= m.target * 0.7:
                m.trend = "stable"
            else:
                m.trend = "declining"

        if self.config.enable_continuous_improvement and on_target < len(self.metrics):
            # Boost lagging metrics
            for m in self.metrics.values():
                if m.trend == "declining":
                    m.value = min(m.target, m.value + 0.05 * m.target)
        return on_target

    def run_cycle(self) -> CoordinationResult:
        result = CoordinationResult()

        on_target = self._update_metrics()
        self.cycle_count += 1

        discovery_metric = next((m for m in self.metrics.values() if m.metric_name == "discovery_rate"), None)
        knowledge_metric = next((m for m in self.metrics.values() if m.metric_name == "knowledge_growth"), None)

        result.metrics_tracked = len(self.metrics)
        result.metrics_on_target = on_target

        result.coordination_score = sum(
            m.value / m.target for m in self.metrics.values()
        ) / max(1, len(self.metrics))

        result.discovery_rate = discovery_metric.value if discovery_metric else 0.0
        result.knowledge_growth = knowledge_metric.value if knowledge_metric else 0.0

        result.self_sustaining = all(
            m.trend != "declining" for m in self.metrics.values()
        ) if self.config.enable_self_sustaining else False

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "metrics": {m.metric_name: {"value": m.value, "target": m.target, "trend": m.trend}
                       for m in self.metrics.values()},
            "coordination_score": sum(m.value / m.target for m in self.metrics.values()) / max(1, len(self.metrics)),
        }
