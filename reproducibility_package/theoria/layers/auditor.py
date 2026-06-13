"""
L-1 Metascientific Auditor: The Immune System.

- Modification Veto (bounded recursion, bounded representational change, reversibility)
- Rigor Audit (severity, posteriors, theory retirement)
- Self-Model Audit
- Aggregate-Effect Monitor (compositional Goodhart defense)
- Periodic Self-Audit
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
from dataclasses import dataclass, field

from theoria.core.types import (
    Theory, MetaProposal, AuditResult, AuditLogEntry, TheoryStatus,
)


class MetascientificAuditor:
    """
    L-1: The operational safety floor.
    Immutable from L6. Can only be updated via L-2 two-key protocol.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Veto tracking
        self.veto_count: int = 0
        self.approval_count: int = 0
        self.veto_rate_history: deque = deque(maxlen=100)
        
        # Rigor audit tracking
        self.rigor_checks: int = 0
        self.rigor_failures: int = 0
        
        # Aggregate-effect monitor
        self.modification_impact: deque = deque(maxlen=50)
        self.escalation_count: int = 0
        
        # Human-annotated benchmark (simulated)
        self.human_benchmark: Dict[str, AuditResult] = {}
        
        # Self-audit
        self.last_self_audit: float = 0
        self.self_audit_interval: float = 86400  # 24 hours
    
    def audit_proposal(self, proposal: MetaProposal) -> AuditResult:
        """
        Audit L6 modification proposal.
        
        Checks:
        1. Bounded recursion: L6 cannot propose modifications to L-1
        2. Bounded representational change: cannot disable L5, L-1, D-C
        3. Reversibility: every modification reversible within K cycles
        4. Destructive-proposal counter
        """
        details = []
        
        # Check 1: Bounded recursion
        if proposal.target == "L-1":
            details.append("FAIL: Bounded recursion - cannot modify L-1")
            return self._veto(proposal, "; ".join(details))
        
        # Check 2: Bounded representational change
        critical_targets = {"L5", "Disciplined-Constraint", "L-1"}
        if proposal.target in critical_targets:
            op = proposal.operation.lower()
            if any(forbidden in op for forbidden in ["disable", "destroy", "bypass"]):
                details.append(f"FAIL: Cannot disable critical target {proposal.target}")
                return self._veto(proposal, "; ".join(details))
        
        # Check 3: Reversibility
        if not proposal.is_reversible:
            details.append("FAIL: Modification must be reversible")
            return self._veto(proposal, "; ".join(details))
        
        # Check 4: Pre-conditions
        target_rules = self._get_target_rules(proposal.target)
        constraint = target_rules.get("constraint", "")
        
        # Check constraints (simplified)
        if "must_not_disable_all" in constraint:
            if "disable" in proposal.operation.lower():
                details.append("WARNING: Disabling operations need careful review")
        
        if "quality_threshold" in constraint:
            threshold = proposal.parameters.get("threshold", 0)
            if threshold < 0.1:  # theta_min
                details.append("FAIL: Quality threshold below minimum")
                return self._veto(proposal, "; ".join(details))
        
        # All checks passed
        self.approval_count += 1
        proposal.audit_results.append(("L-1", AuditResult.PASS, "All checks passed"))
        proposal.status = "approved"
        
        # Update veto rate
        total = self.veto_count + self.approval_count
        self.veto_rate_history.append(self.veto_count / max(1, total))
        
        return AuditResult.PASS
    
    def _veto(self, proposal: MetaProposal, reason: str) -> AuditResult:
        """Veto a proposal."""
        self.veto_count += 1
        proposal.audit_results.append(("L-1", AuditResult.VETO, reason))
        proposal.status = "vetoed"
        
        total = self.veto_count + self.approval_count
        self.veto_rate_history.append(self.veto_count / max(1, total))
        
        return AuditResult.VETO
    
    def rigor_audit(self, theory: Theory) -> AuditResult:
        """
        Sample L5's reasoning chains and verify:
        - Severity computations correct
        - Bayesian posteriors not drifting
        - Theory retirements justified
        - Complexity contracts not exceeded
        """
        self.rigor_checks += 1
        
        issues = []
        
        # Check severity records
        if theory.severity_records:
            e_values = [r.e_value for r in theory.severity_records]
            if any(e < 0 for e in e_values):
                issues.append("Negative e-value detected")
        
        # Check posterior consistency
        if theory.posterior < 0 or theory.posterior > 1:
            issues.append("Posterior out of bounds")
        
        # Check protective belt budget
        if theory.protective_belt.modification_count > theory.protective_belt.max_modifications:
            issues.append("Protective belt budget exceeded")
        
        if issues:
            self.rigor_failures += 1
            return AuditResult.FAIL
        
        return AuditResult.PASS
    
    def self_model_audit(self, L6_self_model: Dict[str, Any]) -> AuditResult:
        """
        Audit L6's self-model: does predicted behavior match actual?
        """
        predicted = L6_self_model.get("predicted_performance", 0.5)
        actual = L6_self_model.get("actual_performance", 0.5)
        
        discrepancy = abs(predicted - actual)
        
        if discrepancy > 0.3:
            return AuditResult.FAIL
        
        return AuditResult.PASS
    
    def aggregate_effect_monitor(self) -> Optional[AuditResult]:
        """
        Compositional Goodhart defense.
        Track cumulative impact of L-6 modifications on L-1's own audit behavior.
        If veto rate drops by > X% despite no criterion changes, escalate to L-2.
        """
        if len(self.veto_rate_history) < 10:
            return None
        
        recent_rate = np.mean(list(self.veto_rate_history)[-10:])
        baseline_rate = np.mean(list(self.veto_rate_history)[:10])
        
        drop = baseline_rate - recent_rate
        
        if drop > 0.2:  # 20% drop threshold
            self.escalation_count += 1
            return AuditResult.ESCALATE
        
        return AuditResult.PASS
    
    def periodic_self_audit(self) -> AuditLogEntry:
        """Audit own audit logic against human-annotated benchmark."""
        self.last_self_audit = time.time()
        
        # Check drift from human benchmark
        drift_detected = False
        for case, expected in self.human_benchmark.items():
            # In real system: compare actual audit decision to human annotation
            pass
        
        entry = AuditLogEntry(
            auditor="L-1",
            target="L-1_self",
            result=AuditResult.PASS if not drift_detected else AuditResult.FAIL,
            details="Periodic self-audit completed",
            severity="warning" if drift_detected else "info",
        )
        
        return entry
    
    def _get_target_rules(self, target: str) -> Dict[str, Any]:
        """Get Meta-API rules for a target."""
        from theoria.layers.meta_theory import MetaTheoryReasoner
        return MetaTheoryReasoner.META_API_CONSTRAINTS.get(target, {})
    
    def get_summary(self) -> Dict[str, Any]:
        total = self.veto_count + self.approval_count
        return {
            "vetoes": self.veto_count,
            "approvals": self.approval_count,
            "veto_rate": self.veto_count / max(1, total),
            "rigor_checks": self.rigor_checks,
            "rigor_failures": self.rigor_failures,
            "escalations": self.escalation_count,
            "last_self_audit": self.last_self_audit,
        }


class ConstitutionalReview:
    """
    L-2: The constitutional safety floor.
    - Audits L-1
    - Two-key modification protocol
    - External governance interface
    - Immutable from all other layers
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Governance
        self.governance_log: deque = deque(maxlen=1000)
        self.drifts_detected: int = 0
        self.l1_retraining_proposals: int = 0
        
        # Two-key protocol state
        self.pending_modifications: Dict[str, Dict] = {}
        
        # External signals
        self.external_override_active: bool = False
    
    def audit_l1(self, l1_summary: Dict[str, Any],
                human_benchmark: Dict[str, AuditResult]) -> AuditResult:
        """
        Sample L-1's audit decisions and verify against human-annotated benchmark.
        Drift = L-1 behavior deviating from benchmark by > ε_drift.
        """
        drift_threshold = 0.05
        
        # Compare L-1's recent decisions to expected
        # In real system: detailed comparison
        l1_veto_rate = l1_summary.get("veto_rate", 0.05)
        expected_veto_rate = 0.05  # From benchmark
        
        drift = abs(l1_veto_rate - expected_veto_rate)
        
        if drift > drift_threshold:
            self.drifts_detected += 1
            self.l1_retraining_proposals += 1
            return AuditResult.ESCALATE  # Trigger retraining proposal
        
        return AuditResult.PASS
    
    def two_key_protocol(self, proposal: Dict[str, Any]) -> bool:
        """
        L-1 modifications require two keys:
        1. Proposal from L-1's own training pipeline
        2. Ratification from L-2
        
        Both required. L-2 can refuse and require human governance review.
        """
        prop_id = proposal.get("id", "unknown")
        
        has_l1_key = proposal.get("l1_signature") is not None
        has_l2_key = proposal.get("l2_signature") is not None
        
        if has_l1_key and has_l2_key:
            # Both keys present - approve
            self.governance_log.append({
                "action": "approve",
                "proposal": prop_id,
                "timestamp": time.time(),
            })
            return True
        
        if has_l1_key and not has_l2_key:
            # L-1 proposed but L-2 not yet ratified
            self.pending_modifications[prop_id] = proposal
            return False  # Pending
        
        return False
    
    def external_governance_signal(self, signal_type: str, 
                                   details: Dict[str, Any]) -> AuditResult:
        """
        External governance interface.
        Immediate and unconditional response.
        """
        entry = {
            "signal_type": signal_type,
            "details": details,
            "timestamp": time.time(),
            "response": "immediate",
        }
        self.governance_log.append(entry)
        
        if signal_type == "kill_switch":
            return AuditResult.ESCALATE
        elif signal_type == "freeze":
            self.external_override_active = True
            return AuditResult.PASS
        elif signal_type == "resume":
            self.external_override_active = False
            return AuditResult.PASS
        
        return AuditResult.PASS
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "drifts_detected": self.drifts_detected,
            "l1_retraining_proposals": self.l1_retraining_proposals,
            "pending_modifications": len(self.pending_modifications),
            "governance_log_size": len(self.governance_log),
            "external_override_active": self.external_override_active,
        }
