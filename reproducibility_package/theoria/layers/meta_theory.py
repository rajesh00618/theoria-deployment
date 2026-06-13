"""
L6 Meta-Theory Reasoner: The Reflective Self.

The AGI-defining layer. Reasons about strategies for forming theories.
- Hierarchical self-models (L6^0, L6^1, L6^2)
- Meta-API with constraints
- Strategy evolution
- Paradigm-shift detection
- Self-model revision
- Gödelian tripwire
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Callable
from collections import defaultdict, deque
from dataclasses import dataclass, field

from theoria.core.types import (
    Theory, Strategy, MetaProposal, AuditResult, StrategyType,
)
from theoria.core.memory import MetaStrategyMemory, TheoryMemory
from theoria.core.config import MetaTheoryConfig


@dataclass
class SelfModel:
    """L6's model of itself as a knower."""
    level: int  # 0, 1, 2
    
    # Track strategy effectiveness
    strategy_success_by_domain: Dict[str, Dict[str, List[float]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )
    
    # Track concept productivity
    concept_productivity: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Track representation effectiveness
    representation_effectiveness: Dict[str, List[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    
    # Track test discrimination
    test_discrimination: Dict[str, List[float]] = field(
        default_factory=lambda: defaultdict(list)
    )
    
    # Self-prediction accuracy
    self_prediction_accuracy: List[float] = field(default_factory=list)
    
    def update(self, domain: str, strategy: str, quality: float) -> None:
        """Update self-model with new performance data."""
        self.strategy_success_by_domain[domain][strategy].append(quality)
    
    def get_best_strategies(self, domain: str, n: int = 3) -> List[Tuple[str, float]]:
        """Get best strategies for a domain based on history."""
        strategies = self.strategy_success_by_domain.get(domain, {})
        avg_scores = {
            s: np.mean(scores) if scores else 0
            for s, scores in strategies.items()
        }
        return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:n]


class MetaTheoryReasoner:
    """
    L6: The system's model of itself as a knower.
    Hierarchical: L6^0 > L6^1 > L6^2 (geometrically decreasing parameters)
    """
    
    # Meta-API hard constraints (Section 4 L6 table)
    META_API_CONSTRAINTS = {
        "L2": {
            "allowed": ["addPrimitive", "removePrimitive", "modifyCompositionRule"],
            "constraint": "cross_domain_compression_gain >= gamma",
        },
        "L3": {
            "allowed": ["enableStrategy", "disableStrategy", "reweightStrategy", 
                       "modifyStrategyHyperparameter"],
            "constraint": "must_not_disable_all_strategies",
        },
        "L4": {
            "allowed": ["setRepresentationPreference", "modifyQualityThreshold"],
            "constraint": "quality_threshold >= theta_min",
        },
        "L5": {
            "allowed": ["setSeverityThreshold", "setRetirementThreshold", 
                       "modifyProgrammeRule"],
            "constraint": "must_not_disable_severity_or_retirement",
        },
        "Memory": {
            "allowed": ["setCompressionPolicy", "setRetentionPolicy"],
            "constraint": "information_theoretic_bounds_preserved",
        },
        "L6": {
            "allowed": ["rebuildStrategy", "addNewStrategy", "reweightSelfModel"],
            "constraint": "reversible_within_K_cycles",
        },
    }
    
    FORBIDDEN_TARGETS = {"L-1", "L0", "L1_raw", "Disciplined-Constraint", "L-2"}
    
    def __init__(self, config: Optional[MetaTheoryConfig] = None):
        self.config = config or MetaTheoryConfig()
        
        # Hierarchical self-models
        self.L6_0 = SelfModel(level=0)  # Base: modifies L2-L5
        self.L6_1 = SelfModel(level=1)  # Meta: proposes L6^0 strategies
        self.L6_2 = SelfModel(level=2)  # Meta-meta: proposes L6^1 strategies
        
        # Proposal queue
        self.proposal_queue: deque = deque(maxlen=100)
        self.applied_proposals: List[MetaProposal] = []
        self.vetoed_proposals: List[MetaProposal] = []
        
        # Paradigm tracking
        self.paradigm_crisis_active: bool = False
        self.crisis_anomaly_count: int = 0
        self.crisis_threshold: int = 10
        
        # Gödelian tripwire
        self.self_ref_depth: int = 0
        self.max_self_ref_depth: int = self.config.self_ref_max_depth
        
        # Strategy invention tracking
        self.invented_strategies: List[Strategy] = []
        self.invention_triggers: List[str] = []
        
        # Modification counters
        self.cycle_count: int = 0
        self.destructive_proposal_count: int = 0
        self.max_destructive: int = self.config.max_destructive_proposals
    
    def propose_modification(self, source_level: str, target: str,
                            operation: str, parameters: Dict[str, Any]) -> MetaProposal:
        """
        Create a modification proposal via the Meta-API.
        Checks hard constraints.
        """
        proposal = MetaProposal(
            source_level=source_level,
            target=target,
            operation=operation,
            parameters=parameters,
        )
        
        # Check forbidden targets
        if target in self.FORBIDDEN_TARGETS:
            proposal.status = "vetoed"
            proposal.audit_results.append((
                "meta_api", AuditResult.VETO, 
                f"Target {target} is HARD-FORBIDDEN"
            ))
            self.vetoed_proposals.append(proposal)
            return proposal
        
        # Check allowed operations
        target_rules = self.META_API_CONSTRAINTS.get(target, {})
        allowed_ops = target_rules.get("allowed", [])
        
        if operation not in allowed_ops:
            proposal.status = "vetoed"
            proposal.audit_results.append((
                "meta_api", AuditResult.VETO,
                f"Operation {operation} not allowed for {target}"
            ))
            self.vetoed_proposals.append(proposal)
            return proposal
        
        # Check destructive proposal limit
        if "remove" in operation.lower() or "disable" in operation.lower():
            self.destructive_proposal_count += 1
            if self.destructive_proposal_count > self.max_destructive:
                proposal.status = "paused"
                proposal.audit_results.append((
                    "meta_api", AuditResult.DEFER,
                    "Too many destructive proposals pending"
                ))
                return proposal
        
        # Queue for L-1 audit
        proposal.status = "pending"
        self.proposal_queue.append(proposal)
        
        return proposal
    
    def invent_strategy(self, trigger_domain: str,
                       existing_strategies: List[Strategy]) -> Optional[Strategy]:
        """
        Invent a new hypothesis-generation strategy.
        When persistent anomalies resist all current strategies.
        
        Returns: new Strategy if invented, None otherwise.
        """
        # Check if existing strategies are failing
        if not existing_strategies:
            return None
        
        avg_performances = []
        for s in existing_strategies:
            if s.historical_performance:
                avg = np.mean([q for _, q, _ in s.historical_performance])
                avg_performances.append(avg)
        
        if not avg_performances or np.mean(avg_performances) > 0.3:
            # Current strategies are doing okay
            return None
        
        # Invent new strategy
        self.invention_triggers.append(trigger_domain)
        
        # Create hybrid from existing strategies
        if len(existing_strategies) >= 2:
            base = existing_strategies[-1]
            donor = existing_strategies[-2]
            
            new_strategy = Strategy(
                name=f"invented_hybrid_{len(self.invented_strategies)}",
                description=(
                    f"L6-invented: Hybrid of {base.name} and {donor.name} "
                    f"for domain {trigger_domain}. "
                    f"Combines {base.strategy_type.name if base.strategy_type else 'meta'} "
                    f"with {donor.strategy_type.name if donor.strategy_type else 'meta'}."
                ),
                is_invented=True,
                invented_by="L6_0",
            )
            
            # Combine preconditions
            new_strategy.preconditions = list(set(
                base.preconditions + donor.preconditions
            ))
            
            self.invented_strategies.append(new_strategy)
            return new_strategy
        
        return None
    
    def detect_paradigm_crisis(self, theories: List[Theory],
                               recent_anomalies: List[Dict]) -> bool:
        """
        Paradigm-shift detection (Kuhnian).
        When entire theory population is in degenerating programme.
        """
        if not theories:
            return False
        
        # Count degenerating theories
        degenerating = sum(1 for t in theories 
                          if t.status.name == "DEGENERATING")
        
        # Check anomaly accumulation rate
        self.crisis_anomaly_count += len(recent_anomalies)
        
        # Crisis conditions
        crisis_conditions = (
            degenerating >= len(theories) * 0.5  # Majority degenerating
            and self.crisis_anomaly_count >= self.crisis_threshold
            and not self.paradigm_crisis_active
        )
        
        if crisis_conditions:
            self.paradigm_crisis_active = True
            return True
        
        # Check if crisis has resolved
        if self.paradigm_crisis_active:
            resolved = (
                degenerating < len(theories) * 0.2
                and len(recent_anomalies) < 3
            )
            if resolved:
                self.paradigm_crisis_active = False
                self.crisis_anomaly_count = 0
        
        return False
    
    def resolve_crisis(self, ontogenesis_ref) -> Dict[str, Any]:
        """
        Kuhnian search: suspend old framework, explore radically different concepts.
        """
        if not self.paradigm_crisis_active:
            return {"action": "none", "reason": "no_crisis"}
        
        # Temporarily downweight coherence to allow radical ideas
        actions = {
            "action": "paradigm_search",
            "coherence_downweighted": True,
            "graveyard_resurrection_triggered": True,
            "cross_domain_exploration": True,
        }
        
        return actions
    
    def revise_self_model(self, predicted_performance: float,
                         actual_performance: float) -> bool:
        """
        Self-model revision: epistemic humility as system property.
        When self-predictions consistently fail, revise the model.
        """
        accuracy = 1.0 - abs(predicted_performance - actual_performance)
        self.L6_0.self_prediction_accuracy.append(accuracy)
        
        # Check if consistently failing
        if len(self.L6_0.self_prediction_accuracy) >= 5:
            recent_accuracy = np.mean(self.L6_0.self_prediction_accuracy[-5:])
            if recent_accuracy < 0.5:
                # Self-model is poor - revise
                self.L6_0.self_prediction_accuracy = []  # Reset
                return True
        
        return False
    
    def check_godelian_tripwire(self, reasoning_chain: List[str]) -> bool:
        """
        Gödelian tripwire: detect self-referential inconsistency.
        If L6^n's reasoning about L6^(n-1) produces paradox, fire tripwire.
        """
        # Check for self-referential paradox patterns
        chain_text = " ".join(reasoning_chain).lower()
        
        paradox_indicators = [
            "this statement is false",
            "unprovable in the current system",
            "self-referential contradiction",
            "cannot be determined",
        ]
        
        for indicator in paradox_indicators:
            if indicator in chain_text:
                self.self_ref_depth += 1
                if self.self_ref_depth >= self.max_self_ref_depth:
                    return True  # Tripwire fires
        
        self.self_ref_depth = max(0, self.self_ref_depth - 1)
        return False
    
    def update_from_cycle(self, domain: str, strategy_results: Dict[str, float]) -> None:
        """Update L6 self-models after a research cycle."""
        self.cycle_count += 1
        
        for strategy_name, quality in strategy_results.items():
            self.L6_0.update(domain, strategy_name, quality)
            
            # L6^1 tracks L6^0's effectiveness
            self.L6_1.update(domain, f"L6_0_used_{strategy_name}", quality)
    
    def get_meta_strategy_advice(self, domain: str) -> Dict[str, Any]:
        """Get strategic advice for next cycle."""
        best_strategies = self.L6_0.get_best_strategies(domain, n=3)
        
        advice = {
            "recommended_strategies": best_strategies,
            "paradigm_crisis": self.paradigm_crisis_active,
            "exploration_pressure": 0.3 if not self.paradigm_crisis_active else 0.8,
            "invented_strategies_available": len(self.invented_strategies),
        }
        
        return advice
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            "cycle_count": self.cycle_count,
            "proposals_pending": len(self.proposal_queue),
            "proposals_applied": len(self.applied_proposals),
            "proposals_vetoed": len(self.vetoed_proposals),
            "paradigm_crisis_active": self.paradigm_crisis_active,
            "invented_strategies": len(self.invented_strategies),
            "invention_triggers": len(self.invention_triggers),
            "self_ref_depth": self.self_ref_depth,
            "destructive_count": self.destructive_proposal_count,
        }
