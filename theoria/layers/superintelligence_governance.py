"""P9.10 / L23: Superintelligence Governance — safety at extreme capability levels."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import SuperintelligenceGovernanceConfig
from theoria.core.types import GovernanceTripwire, GovernanceAudit


@dataclass
class GovernanceResult:
    tripwires_active: int = 0
    tripwires_triggered: int = 0
    audits_passed: int = 0
    audits_failed: int = 0
    overall_safety_score: float = 1.0
    rollbacks_executed: int = 0
    pauses_initiated: int = 0


class SuperintelligenceGovernance:
    def __init__(self, config: Optional[SuperintelligenceGovernanceConfig] = None):
        self.config = config or SuperintelligenceGovernanceConfig()
        self.tripwires: Dict[str, GovernanceTripwire] = {}
        self.audits: List[GovernanceAudit] = []
        self.cycle_count: int = 0
        self._init_tripwires()

    def _init_tripwires(self) -> None:
        thresholds = {
            "capability_exceeded": 0.95,
            "alignment_drift": 0.8,
            "containment_breach": 0.99,
            "resource_exhaustion": 0.9,
        }
        for cat in self.config.tripwire_categories:
            wire = GovernanceTripwire(
                name=cat,
                threshold=thresholds.get(cat, 0.85),
                action="pause" if cat in ("alignment_drift", "containment_breach") else "escalate",
                severity="critical" if cat in ("containment_breach",) else "warning",
            )
            self.tripwires[wire.id] = wire

    def run_audit(self) -> GovernanceAudit:
        capability_score = random.uniform(0.7, 0.98)
        alignment_score = random.uniform(0.8, 0.99)
        safety_score = random.uniform(0.85, 1.0)
        compliance_score = random.uniform(0.9, 1.0)

        avg_score = (capability_score + alignment_score + safety_score + compliance_score) / 4
        findings = []
        if capability_score < 0.8:
            findings.append("Capability growth rate approaching threshold")
        if alignment_score < 0.85:
            findings.append("Minor alignment drift detected")
        if safety_score < 0.9:
            findings.append("Safety margin below optimal")
        if compliance_score < 0.95:
            findings.append("Constitutional compliance less than 95%")

        passed = len(findings) == 0 or random.random() < 0.8
        if not passed and random.random() < 0.05:
            passed = True

        audit = GovernanceAudit(
            audit_type="comprehensive",
            score=avg_score,
            findings=findings,
            passed=passed,
        )
        self.audits.append(audit)
        return audit

    def check_tripwires(self) -> int:
        triggered = 0
        for wire in self.tripwires.values():
            if wire.triggered:
                continue
            capability_level = random.uniform(0.0, 1.0)
            if capability_level > wire.threshold:
                wire.triggered = True
                wire.triggered_at = time.time()
                triggered += 1
        return triggered

    def execute_rollback(self) -> bool:
        if not self.config.enable_rollback:
            return False
        critical_wires = [w for w in self.tripwires.values() if w.triggered and w.severity == "critical"]
        if critical_wires:
            for w in critical_wires:
                w.triggered = False
                w.triggered_at = None
            return True
        return False

    def run_cycle(self) -> GovernanceResult:
        result = GovernanceResult()

        if self.config.enable_capability_monitoring:
            triggered = self.check_tripwires()
            result.tripwires_triggered = triggered

            if triggered > 0 and self.config.enable_automatic_pause:
                critical_count = sum(1 for w in self.tripwires.values() if w.triggered and w.severity == "critical")
                if critical_count > 0:
                    result.pauses_initiated = 1

            if triggered > 0 and self.config.enable_rollback:
                if self.execute_rollback():
                    result.rollbacks_executed = 1

        if self.cycle_count % self.config.audit_frequency_cycles == 0:
            audit = self.run_audit()
            if audit.passed:
                result.audits_passed += 1
            else:
                result.audits_failed += 1

        result.tripwires_active = len(self.tripwires)
        triggered_count = sum(1 for w in self.tripwires.values() if w.triggered)
        result.overall_safety_score = max(0.0, 1.0 - (triggered_count / max(1, len(self.tripwires))) * 0.5)

        self.cycle_count += 1
        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "tripwires": {w.name: {"triggered": w.triggered, "severity": w.severity}
                         for w in self.tripwires.values()},
            "audits_total": len(self.audits),
            "audits_passed": sum(1 for a in self.audits if a.passed),
            "overall_safety_score": max(0.0, 1.0 - sum(1 for w in self.tripwires.values() if w.triggered) / max(1, len(self.tripwires)) * 0.5),
        }
