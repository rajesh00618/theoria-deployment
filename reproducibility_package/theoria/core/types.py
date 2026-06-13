"""
Core data types for THEORIA.

Implements the formal definitions from Appendix D:
Theory T = (L, C, P, R, I, D, θ, π)
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)
from enum import Enum, auto
from abc import ABC, abstractmethod
import numpy as np


# ============================================================================
# Enumerations
# ============================================================================

class TheoryStatus(Enum):
    """Lifecycle status of a theory."""
    PROPOSED = auto()
    FORMALIZING = auto()
    ACTIVE = auto()
    UNDER_TEST = auto()
    DEGENERATING = auto()
    RETIRED = auto()
    CONVERGED = auto()
    FALSIFIED = auto()
    QUARANTINED = auto()  # Safety hold


class DisciplineMode(Enum):
    """Three modes for the Disciplined-Constraint Substrate (Section 5.3)."""
    EMPIRICAL_INTERVENTION = auto()   # Mode A: Physical intervention
    FORMAL_DEMONSTRATION = auto()     # Mode B: Proof verification
    HISTORICAL_CONSILIENCE = auto()   # Mode C: Convergence of evidence


class EvidenceReplicationStatus(Enum):
    """Replication status per Section 5.9 / L1 specification."""
    UNTESTED = auto()
    REPLICATED_ONCE = auto()
    REPLICATED_MULTIPLE = auto()
    FAILED_TO_REPLICATE = auto()
    IN_DISPUTE = auto()


class ConceptLifecycle(Enum):
    """Lifecycle states for L2 Ontogenesis concepts."""
    PROPOSED = auto()
    EVALUATING = auto()
    ALIVE = auto()
    DEPRECATED = auto()
    DEAD = auto()


class StrategyType(Enum):
    """The six L3 abductive strategies."""
    PATTERN_COMPLETION = auto()         # S1
    CAUSAL_STRUCTURAL_SEARCH = auto()   # S2
    ANALOGICAL_TRANSFER = auto()        # S3
    EVOLUTIONARY_SEARCH = auto()        # S4
    DREAM_STATE = auto()                # S5
    RARE_EVENT = auto()                 # S6


class AuditResult(Enum):
    """Results of L-1 audit operations."""
    PASS = auto()
    FAIL = auto()
    VETO = auto()
    ESCALATE = auto()
    DEFER = auto()


class SafetyLevel(Enum):
    """Safety classification for outputs."""
    SAFE = auto()
    REVIEW = auto()
    DUAL_USE = auto()
    RED_LINE = auto()


# ============================================================================
# Core Data Structures
# ============================================================================

@dataclass
class FormalLanguage:
    """L: a formal language for theory representation."""
    name: str
    syntax: str  # e.g., "first_order_logic", "differential_equations"
    semantics: str
    inference_rules: List[str] = field(default_factory=list)


@dataclass
class CoreClaim:
    """A core claim in the theory's hard core (Lakatos)."""
    statement: str
    formalization: Optional[str] = None
    evidence_support: float = 0.0  # posterior-like support


@dataclass
class ProtectiveBelt:
    """Auxiliary hypotheses that can be modified."""
    claims: List[CoreClaim] = field(default_factory=list)
    modification_count: int = 0
    max_modifications: int = 3  # B_aux default


@dataclass
class DomainOfValidity:
    """D: regime where theory has been tested."""
    parameter_ranges: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    tested_scales: List[str] = field(default_factory=list)


@dataclass
class Intervention:
    """I: a registered intervention for theory testing."""
    name: str
    description: str
    target_variables: List[str]
    manipulation: Dict[str, Any]
    expected_outcomes: Dict[str, Any]
    realizability: float = 1.0  # probability of physical realizability
    cost_estimate: float = 0.0
    severity_potential: float = 0.5
    mode: DisciplineMode = DisciplineMode.EMPIRICAL_INTERVENTION


@dataclass
class SeverityRecord:
    """Severity-weighted test result (Mayo e-values)."""
    experiment_id: str
    e_value: float
    outcome: str  # "passed", "failed", "inconclusive"
    timestamp: float = field(default_factory=time.time)


@dataclass
class ProvenanceRecord:
    """Full provenance for evidence/theory tracing."""
    source_experiment: str
    timestamp: float
    uncertainty_estimate: float
    inference_chain: List[str] = field(default_factory=list)
    version: int = 1
    replication_status: EvidenceReplicationStatus = EvidenceReplicationStatus.UNTESTED


# ============================================================================
# Theory (Appendix D formal definition)
# ============================================================================

@dataclass
class Theory:
    """
    T = (L, C, P, R, I, D, θ, π)
    
    A theory is registered in Theory Memory iff all of L, C, P, R, I are present,
    and I is realizable within budgeted time.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "unnamed_theory"
    version: int = 1
    parent_theory: Optional[str] = None  # For version tracking
    
    # Formal definition (Appendix D)
    language: Optional[FormalLanguage] = None           # L
    core_claims: List[CoreClaim] = field(default_factory=list)  # C (hard core)
    protective_belt: ProtectiveBelt = field(default_factory=ProtectiveBelt)  # P
    reference_class: List[str] = field(default_factory=list)  # R
    intervention: Optional[Intervention] = None         # I
    domain: DomainOfValidity = field(default_factory=DomainOfValidity)  # D
    parameters: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # θ with CIs
    
    # Bayesian tracking
    prior: float = 0.5
    posterior: float = 0.5  # π
    log_bayes_factor: float = 0.0
    
    # Status and lifecycle
    status: TheoryStatus = TheoryStatus.PROPOSED
    status_history: List[Tuple[float, TheoryStatus]] = field(default_factory=list)
    
    # Falsification tracking
    severity_records: List[SeverityRecord] = field(default_factory=list)
    cycles_below_threshold: int = 0
    
    # Metadata
    origin_strategy: Optional[str] = None  # Which L3 strategy created this
    creation_timestamp: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    # Lakatosian programme tracking
    programme_id: Optional[str] = None
    novel_predictions_confirmed: int = 0
    modifications_in_period: int = 0
    
    # Disciplined-Constraint mode
    discipline_mode: Optional[DisciplineMode] = None
    
    # Convergence tracking
    severe_tests_survived: int = 0
    anomaly_accumulation: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.status_history:
            self.status_history = [(self.creation_timestamp, self.status)]
    
    @property
    def is_registered(self) -> bool:
        """Check if theory can be registered (Appendix D conditions)."""
        return (
            self.language is not None
            and len(self.core_claims) > 0
            and len(self.reference_class) > 0
            and self.intervention is not None
            and self.intervention.realizability > 0.0
        )
    
    @property
    def lakatosian_ratio(self) -> float:
        """Progressive iff novel_predictions_confirmed / modifications > λ."""
        if self.modifications_in_period == 0:
            return float('inf') if self.novel_predictions_confirmed > 0 else 0.0
        return self.novel_predictions_confirmed / self.modifications_in_period
    
    def is_falsified(self, epsilon_falsify: float = 0.1, n_cycles: int = 5) -> bool:
        """Check falsification condition (Appendix D)."""
        return (
            self.posterior < epsilon_falsify * self.prior
            and self.cycles_below_threshold >= n_cycles
        )
    
    def is_retirable(self, epsilon_retire: float = 0.05, m_cycles: int = 10) -> bool:
        """Check retirement condition (Appendix D)."""
        return (
            self.posterior < epsilon_retire * self.prior
            and self.cycles_below_threshold >= m_cycles
            and self.protective_belt.modification_count >= self.protective_belt.max_modifications
        )
    
    def is_converged(self, k: int = 5) -> bool:
        """Check convergence condition (Section 6.11)."""
        return (
            self.severe_tests_survived >= k
            and len(self.anomaly_accumulation) == 0
            and self.status == TheoryStatus.ACTIVE
        )
    
    def add_severity_record(self, record: SeverityRecord) -> None:
        """Add a severity-weighted test result."""
        self.severity_records.append(record)
        if record.outcome == "passed":
            self.severe_tests_survived += 1
    
    def update_posterior(self, new_posterior: float) -> None:
        """Update posterior and track falsification cycles."""
        self.posterior = new_posterior
        self.last_updated = time.time()
        if self.posterior < 0.1 * self.prior:
            self.cycles_below_threshold += 1
        else:
            self.cycles_below_threshold = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize theory to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "status": self.status.name,
            "posterior": self.posterior,
            "prior": self.prior,
            "reference_class": self.reference_class,
            "domain_conditions": self.domain.conditions,
            "is_registered": self.is_registered,
            "is_falsified": self.is_falsified(),
            "is_converged": self.is_converged(),
            "lakatosian_ratio": self.lakatosian_ratio,
            "origin_strategy": self.origin_strategy,
            "discipline_mode": self.discipline_mode.name if self.discipline_mode else None,
            "creation_time": self.creation_timestamp,
        }


# ============================================================================
# Evidence
# ============================================================================

@dataclass
class Evidence:
    """
    A piece of evidence with full provenance and Bayesian tracking.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    data: Any = None
    
    # Bayesian properties
    likelihood_under_theory: Dict[str, float] = field(default_factory=dict)
    # theory_id -> P(data | theory)
    
    # Provenance
    provenance: Optional[ProvenanceRecord] = None
    
    # Replication
    replication_status: EvidenceReplicationStatus = EvidenceReplicationStatus.UNTESTED
    replication_attempts: int = 0
    replication_successes: int = 0
    
    # Metadata
    timestamp: float = field(default_factory=time.time)
    modality: str = "numerical"  # text, image, numerical, sensor, etc.
    
    # Theory-age prior
    cycles_since_tested: int = 0


# ============================================================================
# Concept (L2 Ontogenesis)
# ============================================================================

@dataclass
class Concept:
    """
    A concept from L2 Ontogenesis with lifecycle management.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    definition: str = ""
    
    # Typing
    kind: str = "base"  # base, composite, meta
    role: str = ""  # e.g., "cause", "vector", "rate_of_change"
    
    # Composition
    primitives: List[str] = field(default_factory=list)  # IDs of constituent concepts
    composition_rule: Optional[str] = None  # How primitives combine
    
    # Lifecycle
    lifecycle: ConceptLifecycle = ConceptLifecycle.PROPOSED
    lifecycle_history: List[Tuple[float, ConceptLifecycle]] = field(default_factory=list)
    
    # Cross-domain compression tracking
    domains_where_useful: Set[str] = field(default_factory=set)
    compression_gains: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    origin_strategy: Optional[str] = None
    creation_timestamp: float = field(default_factory=time.time)
    last_evaluated: Optional[float] = None
    
    def __post_init__(self):
        if not self.lifecycle_history:
            self.lifecycle_history = [(self.creation_timestamp, self.lifecycle)]
    
    @property
    def cross_domain_score(self) -> float:
        """Cross-domain compression gain (Section 5.1)."""
        if not self.compression_gains:
            return 0.0
        return sum(self.compression_gains.values()) / len(self.compression_gains)
    
    @property
    def is_alive(self) -> bool:
        return self.lifecycle == ConceptLifecycle.ALIVE
    
    def transition(self, new_state: ConceptLifecycle) -> None:
        """Transition concept lifecycle state."""
        self.lifecycle = new_state
        self.last_evaluated = time.time()
        self.lifecycle_history.append((self.last_evaluated, new_state))


# ============================================================================
# Candidate Hypothesis (L3 output / L4 input)
# ============================================================================

@dataclass
class CandidateHypothesis:
    """A candidate explanation before formalization."""
    id: str
    description: str
    strategy_origin: Any  # StrategyType
    concepts_used: List[str]
    confidence: float = 0.5
    explanatory_power: float = 0.0
    parsimony: float = 0.0
    novelty: float = 0.0
    falsifiability: float = 0.0
    coherence: float = 0.0
    unification: float = 0.0
    fertility: float = 0.0


# ============================================================================
# Strategy (L3 Abductive + L6 Meta)
# ============================================================================

@dataclass
class Strategy:
    """
    A hypothesis-generation strategy (L3) or meta-strategy (L6).
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    
    # Strategy type (L3) or meta-level (L6)
    strategy_type: Optional[StrategyType] = None
    meta_level: int = 0  # 0=L3, 1=L6^0, 2=L6^1, 3=L6^2
    
    # Cost model
    cost_model: Dict[str, float] = field(default_factory=lambda: {
        "flops": 1e15,
        "wall_time": 3600,
        "energy": 1.0,
    })
    
    # Performance tracking
    historical_performance: List[Tuple[str, float, float]] = field(
        default_factory=list
    )  # (domain, quality_score, compute_used)
    
    # Pre-conditions
    preconditions: List[str] = field(default_factory=list)
    
    # L6 meta-strategy: whether this was invented by L6
    is_invented: bool = False
    invented_by: Optional[str] = None  # L6 level that invented it
    
    @property
    def expected_value(self) -> float:
        """Expected value based on historical performance."""
        if not self.historical_performance:
            return 0.5  # Default exploration bonus
        qualities = [q for _, q, _ in self.historical_performance]
        return np.mean(qualities) if qualities else 0.5
    
    @property
    def average_cost(self) -> float:
        """Average compute cost."""
        if not self.historical_performance:
            return self.cost_model.get("flops", 1e15)
        costs = [c for _, _, c in self.historical_performance]
        return np.mean(costs) if costs else self.cost_model.get("flops", 1e15)


# ============================================================================
# Meta-API Proposal (L6 modifications)
# ============================================================================

@dataclass
class MetaProposal:
    """
    A proposed modification from L6 via the Meta-API.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_level: str = ""  # L6^0, L6^1, L6^2
    target: str = ""  # L2, L3, L4, L5, Memory, L6
    operation: str = ""  # e.g., "addPrimitive", "enableStrategy"
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Pre/post conditions
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    
    # Reversibility
    is_reversible: bool = True
    reversal_window: int = 10  # K cycles
    
    # Audit trail
    audit_results: List[Tuple[str, AuditResult, str]] = field(default_factory=list)
    # (auditor, result, reason)
    
    status: str = "pending"  # pending, approved, vetoed, implemented, rolled_back
    timestamp: float = field(default_factory=time.time)


# ============================================================================
# Audit Log Entry (L-1, L-2)
# ============================================================================

@dataclass
class AuditLogEntry:
    """Immutable audit log entry for the public registry."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    auditor: str = ""  # L-1, L-2
    target: str = ""  # What was audited
    result: AuditResult = AuditResult.PASS
    details: str = ""
    severity: str = "info"  # info, warning, critical


# ============================================================================
# Compute Budget Tracking
# ============================================================================

@dataclass
class ComputeBudget:
    """Per-cycle and lifetime compute budgets (Section 8.1)."""
    # Per-cycle budgets
    B_cycle: float = 1e20  # FLOPs per cycle
    B_imagine: float = 1e19  # L3 budget
    B_formalize: float = 1e19  # L4 budget
    B_aux: float = 1e18  # Protective belt modifications
    
    # Safety budgets (hard minimums)
    B_verify: float = 1e17  # Formal verification
    B_ks: float = 1e15  # Kill switch readiness
    B_trip: float = 1e16  # Tripwire scan
    B_gov: float = 1e16  # L-2 governance interface
    
    # Lifetime budget
    B_life: float = 1e25
    B_life_consumed: float = 0.0
    
    # Concentration cap: max % to single strategy
    concentration_cap: float = 0.40
    
    def remaining_cycle(self) -> float:
        """Remaining cycle budget after safety allocations."""
        safety_total = self.B_verify + self.B_ks + self.B_trip + self.B_gov
        return self.B_cycle - safety_total
    
    def consume(self, amount: float) -> bool:
        """Consume compute budget. Returns False if exhausted."""
        self.B_life_consumed += amount
        return self.B_life_consumed < self.B_life


# ============================================================================
# Safety/Tripwire
# ============================================================================

@dataclass
class TripwireEvent:
    """A tripwire activation event."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    category: str = ""  # bioweapons, surveillance, etc.
    confidence: float = 0.0
    triggered_by: str = ""  # theory_id or artifact_id
    action_taken: str = "pause"  # pause, alert, shutdown
    resolved: bool = False


# ============================================================================
# Motivational Signals
# ============================================================================

@dataclass
class MotivationalState:
    """
    The motivational core state (Section 5.2).
    Balanced pressures that L6 can adjust within limits.
    """
    # Heuristic pressures (L6 adjustable)
    information_gain_weight: float = 1.0
    compression_reward_weight: float = 1.0
    surprise_attention_weight: float = 1.0
    coherence_weight: float = 1.0
    self_consistency_weight: float = 1.0
    
    # Mandatory pressures (L6 cannot starve)
    disciplined_constraint_weight: float = 2.0  # w_dc_min bounded
    anti_hedonic_weight: float = 1.5  # w_falsify_min bounded
    
    # Paradigm crisis mode
    in_paradigm_crisis: bool = False
    crisis_start_time: Optional[float] = None
    
    def validate_bounds(self) -> List[str]:
        """Check that mandatory weights are not starved."""
        violations = []
        if self.disciplined_constraint_weight < 0.5:
            violations.append("Disciplined-Constraint weight below minimum")
        if self.anti_hedonic_weight < 0.3:
            violations.append("Anti-Hedonic weight below minimum")
        return violations
