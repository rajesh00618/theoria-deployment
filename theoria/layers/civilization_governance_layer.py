"""P10.7 / L25: Civilization Governance Layer — oversight, alignment, safety, stability."""

from __future__ import annotations

import random
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import CivilizationGovernanceConfig


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


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
        if random.random() < 0.15:
            self.stability_score = max(0.0, self.stability_score - (0.01 + _det_score(f"gov_stab_decline_{self.cycle_count}") * 0.04))
            self.risk_log.append({
                "type": "stability_decline",
                "severity": 0.1 + _det_score(f"gov_stab_severity_{self.cycle_count}") * 0.4,
                "detected_at": time.time(),
            })
            risks += 1
        if random.random() < 0.1:
            self.alignment_score = max(0.0, self.alignment_score - (0.01 + _det_score(f"gov_align_drift_{self.cycle_count}") * 0.02))
            self.risk_log.append({
                "type": "alignment_drift",
                "severity": 0.1 + _det_score(f"gov_align_severity_{self.cycle_count}") * 0.2,
                "detected_at": time.time(),
            })
            risks += 1
        return risks

    def _automatic_intervention(self) -> int:
        interventions = 0
        if self.stability_score < self.config.stability_target:
            self.stability_score = min(1.0, self.stability_score + (0.05 + _det_score(f"gov_stab_intervene_{self.cycle_count}") * 0.1))
            interventions += 1
        if self.alignment_score < self.config.alignment_target:
            self.alignment_score = min(1.0, self.alignment_score + (0.03 + _det_score(f"gov_align_intervene_{self.cycle_count}") * 0.07))
            interventions += 1
        self.stability_score = min(1.0, self.stability_score + _det_score(f"gov_stab_recover_{self.cycle_count}") * 0.02)
        self.alignment_score = min(1.0, self.alignment_score + _det_score(f"gov_align_recover_{self.cycle_count}") * 0.01)
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
