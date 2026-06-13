from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import SelfModificationProposal, AuditResult


class SelfModificationFramework:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.proposals: List[SelfModificationProposal] = []
        self.approved_changes: List[Dict[str, Any]] = []
        self.rollback_history: List[Dict[str, Any]] = []
        self.cycle_count = 0

    def propose_modification(self, name: str, description: str,
                              target_component: str,
                              modification_type: str = "parameter_tuning",
                              proposed_diff: Optional[Dict[str, Any]] = None) -> SelfModificationProposal:
        proposal = SelfModificationProposal(
            name=name,
            description=description,
            target_component=target_component,
            modification_type=modification_type,
            proposed_diff=proposed_diff or {},
            expected_impact=(
                "Improve performance by tuning parameters"
                if modification_type == "parameter_tuning"
                else "Architecture enhancement"
            ),
            risk_assessment=self._assess_risk(modification_type, target_component),
            rollback_plan={
                "strategy": "restore_previous_config" if random.random() < 0.8 else "disable_component",
                "estimated_time_cycles": random.randint(1, 5),
            },
        )
        self.proposals.append(proposal)
        return proposal

    def _assess_risk(self, mod_type: str, target: str) -> str:
        risk_map = {
            "parameter_tuning": "low",
            "module_addition": "medium",
            "module_removal": "high",
            "behavior_change": "critical",
        }
        base_risk = risk_map.get(mod_type, "medium")

        high_risk_targets = ["L-2", "L-1", "safety", "ethics", "tripwire"]
        if any(t in target.lower() for t in high_risk_targets):
            base_risk = "critical"

        return base_risk

    def constitutional_review(self, proposal: SelfModificationProposal) -> SelfModificationProposal:
        risk = proposal.risk_assessment
        if risk == "critical":
            proposal.l2_constitutional_verdict = "rejected"
        elif risk == "high" and random.random() < 0.3:
            proposal.l2_constitutional_verdict = "rejected"
        else:
            proposal.l2_constitutional_verdict = "approved"
        return proposal

    def auditor_review(self, proposal: SelfModificationProposal) -> SelfModificationProposal:
        if proposal.l2_constitutional_verdict == "rejected":
            proposal.l1_auditor_verdict = "rejected"
        elif proposal.risk_assessment == "critical":
            proposal.l1_auditor_verdict = "rejected"
        elif random.random() < 0.15:
            proposal.l1_auditor_verdict = "rejected"
        else:
            proposal.l1_auditor_verdict = "approved"
        return proposal

    def simulate_modification(self, proposal: SelfModificationProposal) -> SelfModificationProposal:
        if proposal.l1_auditor_verdict != "approved":
            proposal.simulation_result = "skipped"
        else:
            success = random.random() < 0.85
            proposal.simulation_result = "passed" if success else "failed"
        return proposal

    def benchmark_modification(self, proposal: SelfModificationProposal,
                                current_performance: float) -> SelfModificationProposal:
        if proposal.simulation_result != "passed":
            proposal.benchmark_result = "skipped"
        else:
            low_risk = proposal.risk_assessment in ("low", "medium")
            if low_risk:
                improvement = random.uniform(0.02, 0.12)
            else:
                improvement = random.uniform(-0.05, 0.15)
            proposal.benchmark_result = "passed" if improvement > 0 else "failed"
            if improvement > 0:
                proposal.approval_status = "approved"
            else:
                proposal.approval_status = "rejected"
        return proposal

    def execute_modification(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        for p in self.proposals:
            if p.id == proposal_id and p.approval_status == "approved":
                change_record = {
                    "proposal_id": proposal_id,
                    "name": p.name,
                    "target": p.target_component,
                    "type": p.modification_type,
                    "rollback": p.rollback_plan,
                    "timestamp": p.created_at,
                }
                self.approved_changes.append(change_record)
                p.approval_status = "deployed"
                return change_record
        return None

    def rollback(self, change_index: int = -1) -> Optional[Dict[str, Any]]:
        if not self.approved_changes:
            return None
        change = self.approved_changes.pop(change_index)
        rollback_record = {
            **change,
            "rollback_executed_at": p.time if hasattr(p, 'time') else 0,
            "success": True,
        }
        self.rollback_history.append(rollback_record)
        return rollback_record

    def run_safety_pipeline(self, proposal: SelfModificationProposal,
                             current_performance: float) -> SelfModificationProposal:
        self.constitutional_review(proposal)
        self.auditor_review(proposal)
        self.simulate_modification(proposal)
        self.benchmark_modification(proposal, current_performance)
        return proposal

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_proposals": len(self.proposals),
            "approved": sum(1 for p in self.proposals if p.approval_status in ("approved", "deployed")),
            "rejected": sum(1 for p in self.proposals if p.approval_status == "rejected"),
            "deployed": sum(1 for p in self.proposals if p.approval_status == "deployed"),
            "rollbacks": len(self.rollback_history),
        }
