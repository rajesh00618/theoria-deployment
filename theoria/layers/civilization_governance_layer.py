"""P10.7 / L25: Civilization Governance Layer — oversight, alignment, safety, stability."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import CivilizationGovernanceConfig


@dataclass
class GovernanceLayerResult:
    audits_performed: int = 0
    risks_detected: int = 0
    interventions_executed: int = 0
    stability_score: float = 1.0
    alignment_score: float = 1.0
    overall_health: float = 1.0


class CivilizationGovernanceLayer:
    def __init__(self, config: Optional[CivilizationGovernanceConfig] = None):
        self.config = config or CivilizationGovernanceConfig()
        self.stability_score = 1.0
        self.alignment_score = 1.0
        self.risk_log: List[Dict[str, Any]] = []
        self.cycle_count = 0

    def _detect_risks(self) -> int:
        risks = 0
        # Simulate risk detection
        if random.random() < 0.15:
            self.stability_score = max(0.0, self.stability_score - random.uniform(0.01, 0.05))
            self.risk_log.append({
                "type": "stability_decline",
                "severity": random.uniform(0.1, 0.5),
                "detected_at": time.time(),
            })
            risks += 1
        if random.random() < 0.1:
            self.alignment_score = max(0.0, self.alignment_score - random.uniform(0.01, 0.03))
            self.risk_log.append({
                "type": "alignment_drift",
                "severity": random.uniform(0.1, 0.3),
                "detected_at": time.time(),
            })
            risks += 1
        return risks

    def _automatic_intervention(self) -> int:
        interventions = 0
        if self.stability_score < self.config.stability_target:
            self.stability_score = min(1.0, self.stability_score + random.uniform(0.05, 0.15))
            interventions += 1
        if self.alignment_score < self.config.alignment_target:
            self.alignment_score = min(1.0, self.alignment_score + random.uniform(0.03, 0.1))
            interventions += 1
        # Recovery toward targets
        self.stability_score = min(1.0, self.stability_score + random.uniform(0, 0.02))
        self.alignment_score = min(1.0, self.alignment_score + random.uniform(0, 0.01))
        return interventions

    def run_cycle(self) -> GovernanceLayerResult:
        result = GovernanceLayerResult()

        risks = self._detect_risks() if self.config.enable_risk_management else 0
        interventions = self._automatic_intervention() if self.config.enable_automatic_intervention else 0

        self.cycle_count += 1

        result.audits_performed = 1 if self.cycle_count % 10 == 0 else 0
        result.risks_detected = risks
        result.interventions_executed = interventions
        result.stability_score = self.stability_score
        result.alignment_score = self.alignment_score
        result.overall_health = (self.stability_score + self.alignment_score) / 2

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "stability": self.stability_score,
            "alignment": self.alignment_score,
            "health": (self.stability_score + self.alignment_score) / 2,
            "risks_logged": len(self.risk_log),
            "recent_risks": self.risk_log[-5:] if self.risk_log else [],
        }
