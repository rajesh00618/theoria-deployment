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
    """The L3 abductive strategies (S1-S12)."""
    PATTERN_COMPLETION = auto()         # S1
    CAUSAL_STRUCTURAL_SEARCH = auto()   # S2
    ANALOGICAL_TRANSFER = auto()        # S3
    EVOLUTIONARY_SEARCH = auto()        # S4
    DREAM_STATE = auto()                # S5
    RARE_EVENT = auto()                 # S6
    LITERATURE_INFORMED = auto()        # S7: Phase 2
    CROSS_DOMAIN = auto()               # S8: Phase 2
    CAUSAL_REASONING = auto()           # S9: Phase 2
    COUNTERFACTUAL = auto()             # S10: Phase 2
    CONCEPT_BLENDING = auto()           # S11: Phase 2
    MECHANISTIC = auto()                # S12: Phase 2
    LLM_DRIVEN = auto()                # S13: Local LLM hypothesis generation


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
    name: str = ""
    description: str = ""
    target_variables: List[str] = field(default_factory=list)
    manipulation: Dict[str, Any] = field(default_factory=dict)
    expected_outcomes: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
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


# ============================================================================
# Phase 3 Intervention Types
# ============================================================================

@dataclass
class CounterfactualOutcome:
    """Result of a counterfactual simulation."""
    scenario: str = ""
    condition: str = ""
    predicted_outcome: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    mechanism_description: str = ""


# ============================================================================
# Knowledge Graph Types
# ============================================================================

class KGNodeType(Enum):
    """Types of nodes in the knowledge graph."""
    THEORY = auto()
    CONCEPT = auto()
    EXPERIMENT = auto()
    EVIDENCE = auto()
    PAPER = auto()
    HYPOTHESIS = auto()
    DOMAIN = auto()
    METHOD = auto()
    VARIABLE = auto()


class KGEdgeType(Enum):
    """Types of edges in the knowledge graph."""
    RELATED_TO = auto()
    DERIVES_FROM = auto()
    CONTRADICTS = auto()
    SUPPORTS = auto()
    PART_OF = auto()
    CAUSES = auto()
    PREDICTS = auto()
    INSTANCE_OF = auto()
    CITES = auto()
    EVIDENCE_FOR = auto()
    LEADS_TO = auto()
    ENABLES = auto()


@dataclass
class KGNode:
    """A node in the knowledge graph."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    node_type: KGNodeType = KGNodeType.CONCEPT
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    last_accessed: float = field(default_factory=time.time)
    confidence: float = 1.0
    degree: int = 0
    source_paper_ids: List[str] = field(default_factory=list)


@dataclass
class KGEdge:
    """An edge in the knowledge graph."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    edge_type: KGEdgeType = KGEdgeType.RELATED_TO
    weight: float = 1.0
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)


# ============================================================================
# Phase 2 Types
# ============================================================================

@dataclass
class ResearchGap:
    """A gap in scientific knowledge."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    domain: str = ""
    detection_method: str = ""
    detection_source: str = ""
    involved_nodes: List[str] = field(default_factory=list)
    involved_edges: List[str] = field(default_factory=list)
    evidence_gap: bool = False
    theoretical_gap: bool = False
    methodological_gap: bool = False
    overall_score: float = 0.0
    importance: float = 0.5
    tractability: float = 0.5
    novelty: float = 0.5
    status: str = "open"


@dataclass
class ResearchQuestion:
    """A specific research question derived from a gap."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    question_text: str = ""
    domain: str = ""
    gap_id: str = ""
    question_type: str = ""
    source_gap_ids: List[str] = field(default_factory=list)
    template_used: str = ""
    importance: float = 0.5
    novelty: float = 0.5
    answerability: float = 0.5
    overall_score: float = 0.5
    status: str = "open"


@dataclass
class ResearchProgram:
    """
    Multi-year research program (Phase 2 planner + Phase 4 autonomous).
    Supports both legacy (name/description) and Phase 4 (title/objective) fields.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    domain: str = ""
    # Phase 2 fields
    long_term_goal: str = ""
    gap_ids: List[str] = field(default_factory=list)
    question_ids: List[str] = field(default_factory=list)
    estimated_cycles: int = 100
    compute_allocated: float = 0.0
    short_term_goals: List[str] = field(default_factory=list)
    medium_term_goals: List[str] = field(default_factory=list)
    next_milestone: str = ""
    cycles_completed: int = 0
    compute_spent: float = 0.0
    # Phase 4 fields
    questions: List[str] = field(default_factory=list)
    experiment_ids: List[str] = field(default_factory=list)
    theory_ids: List[str] = field(default_factory=list)
    total_questions: int = 0
    total_experiments: int = 0
    total_theories: int = 0
    # Shared
    status: str = "proposed"
    progress: float = 0.0


@dataclass
class CriticReport:
    """Peer-review style evaluation report."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    target_id: str = ""
    target_type: str = "theory"  # theory, experiment, paper
    verdict: str = "pending"  # accept, minor_revision, major_revision, reject
    scores: Dict[str, float] = field(default_factory=dict)
    comments: List[str] = field(default_factory=list)
    reviewer: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class QualityMetrics:
    """Quality metrics for research outputs."""
    severe_tests_passed: int = 0
    severe_tests_failed: int = 0
    replication_attempts: int = 0
    replication_successes: int = 0
    mdl_complexity: float = 0.0
    prediction_accuracy: float = 0.0
    novelty: float = 0.0
    rigor: float = 0.0
    significance: float = 0.0
    reproducibility: float = 0.0
    overall: float = 0.0


@dataclass
class DashboardMetrics:
    """Aggregated metrics for the discovery dashboard."""
    total_theories: int = 0
    active_theories: int = 0
    total_experiments: int = 0
    total_concepts: int = 0
    total_publications: int = 0
    avg_theory_quality: float = 0.0
    research_progress: float = 0.0
    top_theories: List[str] = field(default_factory=list)
    recent_discoveries: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    kg_nodes: int = 0
    kg_edges: int = 0
    kg_domains: int = 0
    kg_clusters: int = 0
    papers_ingested: int = 0
    open_gaps: int = 0
    open_questions: int = 0
    active_programs: int = 0
    critiques_issued: int = 0
    cycles_completed: int = 0
    uptime_hours: float = 0.0
    topic_status: str = ""
    total_simulations: int = 0
    novel_concepts: int = 0
    experiments_run: int = 0
    predictions_made: int = 0
    papers_generated: int = 0


@dataclass
class ScientificPaper:
    """A scientific paper with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    content: str = ""
    full_text: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    domain: str = ""
    citations: List[str] = field(default_factory=list)
    published_at: float = field(default_factory=time.time)


@dataclass
class Citation:
    """A citation record."""
    paper_id: str = ""
    cited_paper_id: str = ""
    context: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class Figure:
    """A figure in a scientific paper."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    caption: str = ""
    figure_type: str = "graph"  # graph, diagram, schematic, photo
    data_refs: List[str] = field(default_factory=list)


# ============================================================================
# Phase 3 Types
# ============================================================================

@dataclass
class VariableSpec:
    """Specification for a variable in an experiment design."""
    name: str = ""
    type: str = "continuous"  # continuous, categorical, ordinal
    range: Tuple[float, float] = (0.0, 1.0)
    levels: List[Any] = field(default_factory=list)
    manipulation: str = ""


@dataclass
class ControlSpec:
    """Specification for a control variable."""
    variable: str = ""
    value: float = 0.0
    rationale: str = ""


@dataclass
class ExperimentDesign:
    """A complete experimental design."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    hypothesis_id: str = ""
    hypothesis_text: str = ""
    independent_variables: List[VariableSpec] = field(default_factory=list)
    dependent_variables: List[str] = field(default_factory=list)
    controls: List[ControlSpec] = field(default_factory=list)
    intervention_description: str = ""
    expected_outcomes: List[str] = field(default_factory=list)
    measurement_plan: str = ""
    protocol: List[str] = field(default_factory=list)
    num_trials: int = 30
    randomize: bool = True
    blinding: str = "double_blind"
    feasibility: float = 0.7
    predicted_power: float = 0.5
    risk_score: float = 0.1
    status: str = "designed"


@dataclass
class TrialResult:
    """Single trial result."""
    trial_number: int = 0
    independent_vars: Dict[str, float] = field(default_factory=dict)
    dependent_vars: Dict[str, float] = field(default_factory=dict)
    controls: Dict[str, float] = field(default_factory=dict)
    anomalies: List[str] = field(default_factory=list)


@dataclass
class ExperimentResult:
    """Results from an experiment."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    experiment_id: str = ""
    hypothesis_id: str = ""
    trials: List[TrialResult] = field(default_factory=list)
    effect_size: float = 0.0
    p_value: float = 0.5
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    mean_raw: float = 0.0
    bayes_factor: float = 1.0
    supports_hypothesis: bool = False
    contradicts_hypothesis: bool = False
    inconclusive: bool = True
    timestamp: float = field(default_factory=time.time)


@dataclass
class PaperSection:
    """A section of a scientific paper."""
    heading: str = ""
    content: str = ""


@dataclass
class PaperDraft:
    """Draft of a scientific paper."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    hypothesis_id: str = ""
    experiment_id: str = ""
    result_id: str = ""
    abstract: str = ""
    methods: Optional[PaperSection] = None
    results: Optional[PaperSection] = None
    discussion: Optional[PaperSection] = None
    references: List[str] = field(default_factory=list)
    sections: List[PaperSection] = field(default_factory=list)
    word_count: int = 0
    quality_score: float = 0.0
    status: str = "draft"
    created_at: float = field(default_factory=time.time)


@dataclass
class ScientificPrediction:
    """A falsifiable prediction extracted from a theory."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    target_variable: str = ""
    predicted_value: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    prediction_interval: Tuple[float, float] = (0.0, 0.0)
    theory_id: str = ""
    domain: str = ""
    time_horizon: str = ""
    actual_value: Optional[float] = None
    error: Optional[float] = None
    verified: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class CrossDomainMapping:
    """A structural mapping between two domains."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_domain: str = ""
    target_domain: str = ""
    source_concept: str = ""
    target_concept: str = ""
    mapping_description: str = ""
    isomorphism_score: float = 0.0
    predictions_generated: List[str] = field(default_factory=list)
    confidence: float = 0.0


class AgentRole(Enum):
    """Roles for multi-agent research lab."""
    PLANNER = auto()
    THEORIST = auto()
    EXPERIMENTER = auto()
    CRITIC = auto()
    REVIEWER = auto()
    SAFETY_OFFICER = auto()


@dataclass
class AgentProfile:
    """Profile for a research agent."""
    role: AgentRole = AgentRole.PLANNER
    name: str = ""
    expertise: List[str] = field(default_factory=list)
    assertiveness: float = 0.5
    creativity: float = 0.5
    rigor: float = 0.5
    max_iterations: int = 10


@dataclass
class AgentMessage:
    """Message sent between research agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    sender_role: AgentRole = AgentRole.PLANNER
    receiver_role: AgentRole = AgentRole.PLANNER
    content: str = ""
    message_type: str = "proposal"
    references: List[str] = field(default_factory=list)
    confidence: float = 0.5
    timestamp: float = field(default_factory=time.time)


@dataclass
class DebateRound:
    """A round of autonomous scientific debate."""
    round_number: int = 0
    statements: List[AgentMessage] = field(default_factory=list)
    consensus_reached: bool = False
    consensus_statement: str = ""


# ============================================================================
# Phase 4 Types
# ============================================================================

@dataclass
class APISourceConfig:
    """Configuration for a real data API source."""
    name: str = ""
    base_url: str = ""
    domains: str = ""
    rate_limit_per_min: int = 60
    enabled: bool = True


@dataclass
class APISearchResult:
    """Result from a real data API search."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source: str = ""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    abstract: str = ""
    url: str = ""
    year: int = 0
    citation_count: int = 0
    doi: str = ""
    relevance_score: float = 0.0
    fetched_at: float = field(default_factory=time.time)


@dataclass
class LabDevice:
    """A laboratory device for embodied experimentation."""
    id: str = ""
    name: str = ""
    device_type: str = ""
    domain: str = ""
    capabilities: List[str] = field(default_factory=list)
    connected: bool = True
    precision: float = 0.01
    calibrated: bool = True
    last_maintenance: float = field(default_factory=time.time)


@dataclass
class MeasurementResult:
    """A single measurement from a lab device."""
    device_id: str = ""
    measurement_type: str = ""
    value: float = 0.0
    unit: str = ""
    precision: float = 0.01
    timestamp: float = field(default_factory=time.time)


@dataclass
class EmbodiedExperiment:
    """An experiment executed on real/simulated lab devices."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    devices_used: List[str] = field(default_factory=list)
    protocol: List[str] = field(default_factory=list)
    measurements: List[MeasurementResult] = field(default_factory=list)
    status: str = "planned"
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class SocietyAgent:
    """An agent in the scientific society."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    role: str = "researcher"
    domain: str = ""
    expertise: List[str] = field(default_factory=list)
    productivity: float = 0.5
    reputation: float = 0.5
    is_active: bool = True
    papers_published: int = 0
    collaboration_count: int = 0


@dataclass
class Collaboration:
    """A collaboration between society agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_ids: List[str] = field(default_factory=list)
    domain: str = ""
    topic: str = ""
    output_count: int = 0
    consensus_reached: bool = False
    formed_at: float = field(default_factory=time.time)


@dataclass
class ParadigmEvent:
    """A paradigm-level event in the scientific society."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: str = ""
    description: str = ""
    domain: str = ""
    involved_theories: List[str] = field(default_factory=list)
    severity: float = 0.5
    timestamp: float = field(default_factory=time.time)


@dataclass
class Presentation:
    """A scientific presentation or talk."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    event_type: str = "conference"
    duration_minutes: int = 20
    slides: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class GrantProposal:
    """A research grant proposal."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    summary: str = ""
    objectives: List[str] = field(default_factory=list)
    methodology: str = ""
    expected_outcomes: List[str] = field(default_factory=list)
    budget_requested: float = 0.0
    score: float = 0.0
    status: str = "draft"
    created_at: float = field(default_factory=time.time)


@dataclass
class EthicsReview:
    """An ethics review record."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    subject_type: str = "theory"
    subject_id: str = ""
    risk_level: str = "low"
    risk_score: float = 0.0
    issues_found: List[str] = field(default_factory=list)
    recommendation: str = "approved"
    reviewer: str = ""
    reviewed_at: float = field(default_factory=time.time)


@dataclass
class RedTeamChallenge:
    """An adversarial challenge from a red team."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    team_id: str = ""
    target_id: str = ""
    target_type: str = "theory"
    challenge_text: str = ""
    severity: float = 0.0
    survived: bool = False
    timestamp: float = field(default_factory=time.time)


@dataclass
class MarketPrediction:
    """A prediction tracked by the prediction market."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    theory_id: str = ""
    description: str = ""
    predicted_value: float = 0.0
    confidence: float = 0.5
    actual_value: Optional[float] = None
    error: Optional[float] = None
    verified: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class ResourceAllocation:
    """Allocation of resources to a project or experiment."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = ""
    compute_budget: float = 0.0
    time_budget_hours: float = 0.0
    monetary_budget: float = 0.0
    experiment_slots: int = 0
    priority: str = "medium"
    allocated_at: float = field(default_factory=time.time)


@dataclass
class TheoryEpoch:
    """An epoch in the lifecycle of a theory in knowledge evolution."""
    theory_id: str = ""
    theory_name: str = ""
    domain: str = ""
    proposed_at: float = 0.0
    falsified_at: Optional[float] = None
    lifetime_cycles: int = 0
    paradigm: str = "normal"  # normal, crisis, revolutionary
    influence_score: float = 0.0
    descendant_ids: List[str] = field(default_factory=list)


@dataclass
class EmbodiedExperiment:
    """An experiment executed on real/simulated lab devices."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    design_id: str = ""
    device_ids: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "planned"
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    results: List[Any] = field(default_factory=list)


@dataclass
class MeasurementResult:
    """A single measurement result from a lab experiment."""
    device_id: str = ""
    measurements: Dict[str, float] = field(default_factory=dict)
    uncertainty: Dict[str, float] = field(default_factory=dict)
    trial_number: int = 0
    timestamp: float = field(default_factory=time.time)


# ============================================================================
# Phase 5 Types: Self-Improving Scientific Civilization
# ============================================================================

@dataclass
class ArchitectureProposal:
    """A proposal to modify THEORIA's own architecture."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    target_layer: str = ""
    modification_type: str = ""  # add_module, remove_module, modify_parameter, rewire_connection
    proposed_changes: Dict[str, Any] = field(default_factory=dict)
    expected_improvement: float = 0.0
    performance_impact: float = 0.0
    resource_cost: float = 0.0
    risk_score: float = 0.0
    status: str = "proposed"  # proposed, simulated, benchmarked, approved, rejected, deployed
    benchmark_results: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class AlgorithmCandidate:
    """A candidate algorithm discovered by P5.2."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    target_domain: str = ""  # optimization, search, reasoning, planning, memory, kg_traversal
    pseudocode: str = ""
    complexity_estimate: str = ""
    baseline_name: str = ""
    baseline_performance: float = 0.0
    measured_performance: float = 0.0
    improvement_factor: float = 0.0
    benchmark_results: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "candidate"  # candidate, benchmarked, adopted, rejected
    created_at: float = field(default_factory=time.time)


@dataclass
class StrategyVariant:
    """A variant of a research strategy (P5.3)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    parent_strategies: List[str] = field(default_factory=list)
    mutation_type: str = ""  # mutate, combine, novel
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_score: float = 0.0
    benchmark_results: List[Dict[str, Any]] = field(default_factory=list)
    generation: int = 0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class BenchmarkSpec:
    """A benchmark specification generated by P5.4."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    benchmark_type: str = ""  # stress_test, adversarial, novel
    domain: str = ""
    difficulty: float = 0.5
    scoring_criteria: List[str] = field(default_factory=list)
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    ground_truth: Dict[str, Any] = field(default_factory=dict)
    status: str = "generated"  # generated, validated, active, retired
    validation_score: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class MetaScienceFinding:
    """A finding from meta-science (P5.5)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    finding_type: str = ""  # method_effectiveness, experiment_informativeness, theory_longevity
    domain: str = ""
    evidence_strength: float = 0.0
    confidence: float = 0.0
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    implication: str = ""
    status: str = "discovered"
    created_at: float = field(default_factory=time.time)


@dataclass
class SimulationWorld:
    """A virtual simulation world for massive experimentation (P5.6)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    domain: str = ""  # physics, biology, economics, artificial
    world_parameters: Dict[str, Any] = field(default_factory=dict)
    rules: List[str] = field(default_factory=list)
    experiment_count: int = 0
    max_experiments: int = 100000
    discovery_count: int = 0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class SelfModificationProposal:
    """A self-modification proposal with safety checks (P5.7)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    target_component: str = ""
    modification_type: str = ""  # parameter_tuning, module_addition, module_removal, behavior_change
    proposed_diff: Dict[str, Any] = field(default_factory=dict)
    expected_impact: str = ""
    risk_assessment: str = ""
    l2_constitutional_verdict: str = "pending"
    l1_auditor_verdict: str = "pending"
    simulation_result: str = "pending"
    benchmark_result: str = "pending"
    approval_status: str = "pending"
    rollback_plan: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class CompressedAbstraction:
    """A compressed knowledge abstraction (P5.8)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    abstraction_type: str = ""  # meta_concept, unified_principle, research_pattern
    source_count: int = 0
    compression_ratio: float = 0.0
    source_ids: List[str] = field(default_factory=list)
    formal_representation: str = ""
    applicability_domains: List[str] = field(default_factory=list)
    predictive_power: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class ResearchAgenda:
    """An autonomous research agenda (P5.10)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    agenda_type: str = ""  # ten_year_program, new_field, new_civilization
    domain: str = ""
    objectives: List[str] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    resource_estimate: float = 0.0
    novelty_score: float = 0.0
    feasibility_score: float = 0.0
    impact_score: float = 0.0
    status: str = "proposed"
    progress: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class CivilizationMetrics:
    """Civilization-level analytics (P5.9)."""
    health_score: float = 0.0
    civilization_score: float = 0.0
    innovation_score: float = 0.0
    agent_productivity: float = 0.0
    theory_quality: float = 0.0
    paradigm_shift_rate: float = 0.0
    discovery_rate: float = 0.0
    total_experiments: int = 0
    active_theories: int = 0
    total_papers: int = 0
    collaboration_density: float = 0.0
    resource_efficiency: float = 0.0
    timestamp: float = field(default_factory=time.time)


# ============================================================================
# Phase 6 Types: General Research Intelligence
# ============================================================================

@dataclass
class KnowledgeNode:
    """A single node in the Universal Knowledge Fabric (P6.1)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    node_type: str = ""  # concept, theory, process, system, organization, technology, person, tool, method
    domain: str = ""
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    embeddings: List[float] = field(default_factory=list)
    confidence: float = 1.0
    source_ids: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class KnowledgeEdge:
    """An edge in the Universal Knowledge Fabric (P6.1)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    relation_type: str = ""  # is_a, part_of, causes, similar_to, contradicts, specializes, depends_on, leads_to, produces, requires
    weight: float = 1.0
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)


@dataclass
class ReasoningTrace:
    """A reasoning trace from the Universal Reasoning Engine (P6.2)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    reasoning_mode: str = ""  # deduction, induction, abduction, causal, counterfactual, analogical, game_theoretic, strategic, legal, economic
    premises: List[str] = field(default_factory=list)
    conclusion: str = ""
    confidence: float = 0.0
    steps: List[Dict[str, Any]] = field(default_factory=list)
    domain: str = ""
    valid: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class MathematicalConjecture:
    """A mathematical conjecture generated by P6.3."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    statement: str = ""
    domain: str = ""  # number_theory, algebra, geometry, topology, analysis, logic, combinatorics, probability
    conjecture_type: str = ""  # conjecture, theorem, lemma, corollary, hypothesis
    proof_attempted: bool = False
    proof_found: bool = False
    proof_steps: List[str] = field(default_factory=list)
    formal_verification: bool = False
    counterexamples: List[str] = field(default_factory=list)
    novelty_score: float = 0.0
    depth_score: float = 0.0
    status: str = "proposed"  # proposed, proven, disproven, open
    created_at: float = field(default_factory=time.time)


@dataclass
class SoftwareProject:
    """A software project designed by P6.4."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    architecture: Dict[str, Any] = field(default_factory=dict)
    modules: List[Dict[str, Any]] = field(default_factory=list)
    algorithms: List[str] = field(default_factory=list)
    code_generated: bool = False
    tests_passed: bool = False
    performance_score: float = 0.0
    quality_score: float = 0.0
    status: str = "designed"  # designed, implemented, tested, deployed
    created_at: float = field(default_factory=time.time)


@dataclass
class CrossDomainMapping:
    """A cross-domain mapping between unrelated fields (P6.5)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_domain: str = ""
    target_domain: str = ""
    source_concept: str = ""
    target_concept: str = ""
    mapping_type: str = ""  # analogy, isomorphism, metaphor, transfer, generalization
    description: str = ""
    strength: float = 0.0
    novelty: float = 0.0
    utility: float = 0.0
    verified: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class OpenEndedGoal:
    """A curiosity-driven learning goal (P6.6)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    domain: str = ""
    goal_type: str = ""  # exploration, understanding, discovery, mastery, synthesis
    curiosity_score: float = 0.0
    expected_information_gain: float = 0.0
    difficulty: float = 0.0
    prerequisites: List[str] = field(default_factory=list)
    progress: float = 0.0
    status: str = "active"  # active, completed, abandoned
    created_at: float = field(default_factory=time.time)


@dataclass
class LongHorizonPlan:
    """A long-horizon plan (P6.7)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    domain: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    steps: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    estimated_duration_cycles: int = 0
    current_phase: int = 0
    status: str = "planned"  # planned, in_progress, completed, failed
    created_at: float = field(default_factory=time.time)


@dataclass
class GeneralAgent:
    """A general-purpose agent for the General Agent Society (P6.8)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    role: str = ""  # scientist, engineer, mathematician, doctor, economist, teacher, programmer, strategist, policy_analyst
    domain: str = ""
    capabilities: List[str] = field(default_factory=list)
    knowledge_areas: List[str] = field(default_factory=list)
    productivity: float = 0.5
    specialization_depth: float = 0.0
    collaboration_history: List[str] = field(default_factory=list)
    projects_completed: int = 0
    performance_score: float = 0.0
    is_active: bool = True
    created_at: float = field(default_factory=time.time)


@dataclass
class UniversalProblem:
    """A problem for the Universal Problem Solver (P6.9)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    domain: str = ""  # research, engineering, business, education, technology, policy
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    solution_attempted: bool = False
    solution_found: bool = False
    solution_summary: str = ""
    approach: str = ""  # analytical, empirical, creative, hybrid
    difficulty: float = 0.0
    quality_score: float = 0.0
    execution_plan: List[str] = field(default_factory=list)
    status: str = "unsolved"  # unsolved, in_progress, solved, failed
    created_at: float = field(default_factory=time.time)


@dataclass
class WorldModel:
    """A world model for understanding complex systems (P6.10)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    model_type: str = ""  # scientific, economic, social, technological, political
    domain: str = ""
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    state_variables: List[str] = field(default_factory=list)
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    simulation_results: List[Dict[str, Any]] = field(default_factory=list)
    accuracy: float = 0.0
    complexity: float = 0.0
    last_updated: float = field(default_factory=time.time)
    status: str = "active"


# ============================================================================
# Phase 7 Types — AGI-Level Scientist (P7.1–P7.10)
# ============================================================================


@dataclass
class CognitiveTrace:
    """A unified cognitive trace from the Unified Cognitive Core (P7.1)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    attention_focus: str = ""
    reasoning_modes_used: List[str] = field(default_factory=list)
    input_domains: List[str] = field(default_factory=list)
    active_goals: List[str] = field(default_factory=list)
    shared_memory_keys: List[str] = field(default_factory=list)
    inference_steps: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class LifeEpisode:
    """An episode in lifelong memory (P7.2)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    episode_type: str = ""  # research, learning, collaboration, tool_creation, etc.
    description: str = ""
    timestamp: float = field(default_factory=time.time)
    importance: float = 0.5
    consolidation_state: str = "working"  # working → consolidated → archived
    memory_strength: float = 1.0
    linked_episodes: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    emotional_valence: float = 0.0


@dataclass
class ResearchPortfolio:
    """A research portfolio for the Autonomous Research Director (P7.3)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    projects: List[Dict[str, Any]] = field(default_factory=list)
    total_projects: int = 0
    active_projects: int = 0
    completed_projects: int = 0
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    risk_profile: Dict[str, float] = field(default_factory=dict)
    priority_scores: Dict[str, float] = field(default_factory=dict)
    performance_history: List[float] = field(default_factory=list)


@dataclass
class UnifiedModel:
    """A unified world model across all domains (P7.4)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    domains: List[str] = field(default_factory=list)
    cross_domain_connections: List[Dict[str, Any]] = field(default_factory=list)
    prediction_accuracy: Dict[str, float] = field(default_factory=dict)
    simulation_depth: int = 0
    parameters: Dict[str, Any] = field(default_factory=dict)
    last_calibrated: float = field(default_factory=time.time)
    consistency_score: float = 1.0


@dataclass
class ToolSpec:
    """A tool specification for the Tool Creation Engine (P7.5)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    tool_type: str = ""  # simulator, algorithm, analyzer, compiler, research_system
    description: str = ""
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    implementation: str = ""
    test_results: Dict[str, Any] = field(default_factory=dict)
    novelty_score: float = 0.0
    utility_score: float = 0.0
    status: str = "specified"  # specified, implemented, tested, deployed


@dataclass
class CollaborationRecord:
    """A human collaboration record (P7.6)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    partner_type: str = ""  # human, agent
    interaction_type: str = ""  # teaching, debating, explaining, mentoring, teamwork
    topic: str = ""
    duration_minutes: float = 0.0
    feedback_score: float = 0.0
    collaboration_quality: float = 0.0
    outcomes: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class CreativeArtifact:
    """A creative artifact from the Creativity Engine (P7.7)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    artifact_type: str = ""  # scientific_idea, mathematical_proof, engineering_design, software_architecture, strategic_plan
    domain: str = ""
    description: str = ""
    novelty_score: float = 0.0
    utility_score: float = 0.0
    impact_score: float = 0.0
    predecessors: List[str] = field(default_factory=list)
    evaluation_notes: str = ""


@dataclass
class AgencyGoal:
    """A self-generated goal for Autonomous Agency (P7.8)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    source: str = ""  # self_generated, external, derived
    priority: float = 0.5
    complexity: float = 0.5
    estimated_effort: float = 1.0
    dependencies: List[str] = field(default_factory=list)
    subgoals: List[str] = field(default_factory=list)
    progress: float = 0.0
    status: str = "proposed"  # proposed, active, completed, failed
    outcome_summary: str = ""


@dataclass
class CapabilityAssessment:
    """A self-evaluation capability assessment (P7.9)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    capability_name: str = ""
    self_assessed_score: float = 0.0
    actual_performance: float = 0.0
    calibration_error: float = 0.0
    improvement_rate: float = 0.0
    weaknesses: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    assessment_date: float = field(default_factory=time.time)


@dataclass
class GrandChallenge:
    """A grand challenge program (P7.10)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""  # cancer, climate, fusion, materials, ai_safety, longevity
    description: str = ""
    decade_plan: List[Dict[str, Any]] = field(default_factory=list)
    total_experiments: int = 0
    completed_experiments: int = 0
    collaborators: List[str] = field(default_factory=list)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    progress: float = 0.0
    resources_allocated: float = 0.0
    status: str = "planned"


# ============================================================================
# Phase 8: Autonomous General Intelligence
# ============================================================================

@dataclass
class OpenWorldLearningRecord:
    """A record of open-world learning from arbitrary sources (P8.1)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_type: str = ""  # internet, document, human, sensor, experiment, software, organization
    source_description: str = ""
    fact_discovered: str = ""
    contradiction_with: List[str] = field(default_factory=list)
    confidence: float = 0.0
    learned_at: float = field(default_factory=time.time)
    verified: bool = False


@dataclass
class GlobalMemoryEntry:
    """An entry in the global multi-year memory architecture (P8.2)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memory_type: str = ""  # personal, research, world, goal, decision
    content: str = ""
    abstraction_level: int = 0  # 0=raw, 10=highly abstracted
    compression_ratio: float = 1.0
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    linked_entries: List[str] = field(default_factory=list)


@dataclass
class ExecutiveDecision:
    """A decision made by the Executive Intelligence layer (P8.3 / L18)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    decision_type: str = ""  # goal_selection, priority, resource, risk
    context: str = ""
    options_considered: List[str] = field(default_factory=list)
    chosen_option: str = ""
    confidence: float = 0.0
    expected_outcome: str = ""
    actual_outcome: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class AgentTeam:
    """An autonomous team of agents (P8.4)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    agent_ids: List[str] = field(default_factory=list)
    team_purpose: str = ""
    formation_time: float = field(default_factory=time.time)
    productivity_score: float = 0.0
    specialization_areas: List[str] = field(default_factory=list)
    status: str = "active"


@dataclass
class CognitiveInvention:
    """A novel cognitive architecture or reasoning strategy (P8.5 / L19)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    invention_type: str = ""  # architecture, reasoning_strategy, learning_algorithm
    name: str = ""
    description: str = ""
    parent_architectures: List[str] = field(default_factory=list)
    performance_gain: float = 0.0
    complexity: float = 0.0
    verified: bool = False
    created_at: float = field(default_factory=time.time)


@dataclass
class RealWorldAction:
    """An action executed in a real external environment (P8.6)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    environment_type: str = ""  # software, research, business, robotics, digital
    action_description: str = ""
    status: str = "planned"  # planned, executing, completed, failed, recovered
    result_summary: str = ""
    error_count: int = 0
    recovery_attempts: int = 0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class UniversalToolSpec:
    """A tool in the universal tool ecosystem (P8.7)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tool_type: str = ""  # analyzer, compiler, simulator, designer, researcher, optimizer
    name: str = ""
    description: str = ""
    capability_score: float = 0.0
    reliability: float = 0.0
    usage_count: int = 0
    status: str = "active"  # active, retired
    depends_on: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class CivilizationForecast:
    """A forecast generated by the civilization simulator (P8.8)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    model_type: str = ""  # economy, government, science, technology
    scenario: str = ""
    forecast_horizon_days: int = 0
    predicted_outcomes: List[Dict[str, Any]] = field(default_factory=list)
    confidence_intervals: List[float] = field(default_factory=list)
    accuracy: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class AutonomousMission:
    """An autonomous mission in the mission system (P8.9 / L20)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    mission_name: str = ""
    mission_type: str = ""  # energy, healthcare, science, climate, exploration
    description: str = ""
    programs: List[Dict[str, Any]] = field(default_factory=list)
    total_progress: float = 0.0
    status: str = "active"  # active, completed, failed
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    deadline: Optional[float] = None


@dataclass
class IntelligenceEvaluation:
    """An evaluation of general intelligence (P8.10)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    evaluation_type: str = ""  # adaptability, learning_speed, problem_solving, creativity, autonomy, robustness
    score: float = 0.0
    benchmark_reference: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    evaluated_at: float = field(default_factory=time.time)
    improvement_since_last: float = 0.0


# ═══════════════════════════════════════════════════════════════
# Phase 9: Superhuman Research Intelligence (SRI)
# ═══════════════════════════════════════════════════════════════

@dataclass
class DiscoveryAgent:
    """A single agent in the planet-scale discovery engine (P9.1)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    domain: str = ""  # science, engineering, medicine, economics, mathematics, technology
    specialization: str = ""
    hypotheses_generated: int = 0
    experiments_run: int = 0
    discoveries_made: int = 0
    status: str = "active"  # active, idle, retired
    created_at: float = field(default_factory=time.time)


@dataclass
class ScientificField:
    """A scientific field created autonomously (P9.2)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    parent_disciplines: List[str] = field(default_factory=list)
    core_concepts: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)
    maturity: float = 0.0  # 0.0 = nascent, 1.0 = established
    created_at: float = field(default_factory=time.time)


@dataclass
class DiscoveryPipeline:
    """A discovery acceleration pipeline (P9.3 / L21)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    question: str = ""
    hypotheses_queued: int = 0
    experiments_queued: int = 0
    validations_completed: int = 0
    knowledge_integrated: int = 0
    speedup_factor: float = 1.0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class KnowledgeObject:
    """A knowledge object in the global knowledge civilization (P9.4)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_type: str = ""  # paper, patent, book, dataset, experiment, simulation
    title: str = ""
    domain: str = ""
    content_summary: str = ""
    confidence: float = 0.0
    contradictions: List[str] = field(default_factory=list)
    integrated_at: float = field(default_factory=time.time)


@dataclass
class ResearchInstitution:
    """A simulated research institution (P9.5)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    institution_type: str = ""  # university, lab, review_board, funding_agency, journal
    domain: str = ""
    members: List[str] = field(default_factory=list)
    proposals_reviewed: int = 0
    resources_allocated: float = 0.0
    publications: int = 0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class ParadigmShift:
    """A paradigm shift event (P9.6)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    old_paradigm_name: str = ""
    new_paradigm_name: str = ""
    detected_limitations: List[str] = field(default_factory=list)
    generated_alternatives: List[str] = field(default_factory=list)
    evidence_for_shift: List[str] = field(default_factory=list)
    adopted: bool = False
    shift_date: float = field(default_factory=time.time)


@dataclass
class RecursiveTool:
    """A tool in the recursive tool civilization (P9.7)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    recursion_level: int = 0  # 0 = tool, 1 = tool generator, 2 = tool generator generator
    tools_produced: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    performance_score: float = 0.0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class DiscoveryProgram:
    """A grand discovery program (P9.8)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""  # cancer, fusion, climate, longevity, quantum_computing, ai_safety, materials
    experiments_planned: int = 0
    experiments_completed: int = 0
    theories_generated: int = 0
    theories_validated: int = 0
    progress: float = 0.0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class CivilizationModel:
    """A model of scientific civilization progress (P9.9)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    model_type: str = ""  # efficiency, friction, evolution
    description: str = ""
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    accuracy: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class GovernanceTripwire:
    """A safety tripwire for superintelligence governance (P9.10 / L23)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    threshold: float = 0.0
    triggered: bool = False
    triggered_at: Optional[float] = None
    action: str = ""  # pause, rollback, escalate, terminate
    severity: str = "info"  # info, warning, critical


@dataclass
class GovernanceAudit:
    """An audit record for superintelligence governance (P9.10)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    audit_type: str = ""  # capability, alignment, safety, compliance
    score: float = 0.0
    findings: List[str] = field(default_factory=list)
    passed: bool = True
    audited_at: float = field(default_factory=time.time)


# ═══════════════════════════════════════════════════════════════
# Phase 10: Scientific Singularity Framework (SSF)
# ═══════════════════════════════════════════════════════════════

@dataclass
class KnowledgeEvolutionRecord:
    """A record of knowledge evolution (P10.1 / L24)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    knowledge_id: str = ""
    parent_knowledge_id: str = ""
    evolution_type: str = ""  # refinement, combination, abstraction, specialization
    mutation_description: str = ""
    fitness_score: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class DiscoveryEcology:
    """A research ecology in the discovery ecosystem (P10.4)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""  # conservative, radical, exploratory, verification
    approach: str = ""
    agents: List[str] = field(default_factory=list)
    theories_active: int = 0
    discoveries_made: int = 0
    productivity_score: float = 0.0
    stability_score: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class RecursiveDiscoverer:
    """An agent that creates other discoverers (P10.2)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    recursion_depth: int = 0
    discoverers_created: List[str] = field(default_factory=list)
    discoveries_generated: int = 0
    performance: float = 0.0
    status: str = "active"
    created_at: float = field(default_factory=time.time)


@dataclass
class KnowledgeFabricNode:
    """A node in the Universal Knowledge Fabric 2.0 (P10.3)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    domain: str = ""  # science, math, engineering, technology, economics, medicine, governance, education
    content: str = ""
    connections: List[str] = field(default_factory=list)
    integration_score: float = 0.0
    last_updated: float = field(default_factory=time.time)


@dataclass
class MetaKnowledgeModel:
    """A model of knowledge itself (P10.5)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    question: str = ""  # What is knowledge? How does knowledge evolve? How do discoveries emerge?
    hypothesis: str = ""
    findings: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class CivilizationMemoryRecord:
    """A record in civilization memory (P10.6)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    record_type: str = ""  # theory, experiment, discovery, failure, paradigm_shift, institution
    title: str = ""
    summary: str = ""
    importance: float = 0.0
    references: List[str] = field(default_factory=list)
    archived_at: float = field(default_factory=time.time)


@dataclass
class DiscoveryForecast:
    """A forecast of future discoveries (P10.8)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    forecast_type: str = ""  # discovery, technology, bottleneck, paradigm_shift
    target_domain: str = ""
    prediction: str = ""
    probability: float = 0.0
    time_horizon_days: int = 0
    accuracy: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class ProblemNode:
    """A node in the Universal Problem Network (P10.9)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""  # energy, climate, materials, economics, policy, society
    description: str = ""
    connected_problems: List[str] = field(default_factory=list)
    solutions_proposed: int = 0
    solutions_implemented: int = 0
    criticality: float = 0.0
    created_at: float = field(default_factory=time.time)


@dataclass
class SingularityMetric:
    """A metric tracking the self-sustaining civilization (P10.10 / L26)."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    metric_name: str = ""  # discovery_rate, knowledge_growth, governance_stability, coordination_efficiency
    value: float = 0.0
    target: float = 0.0
    trend: str = "stable"  # improving, stable, declining
    recorded_at: float = field(default_factory=time.time)
