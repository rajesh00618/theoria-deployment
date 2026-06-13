"""
THEORIA Configuration System.

Manages all tunable thresholds, budgets, and hyperparameters.
All ε, δ, τ, λ, θ, γ parameters from the framework specification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SafetyThresholds:
    """Safety-related thresholds."""
    # Falsification
    epsilon_falsify: float = 0.1  # Posterior < ε_falsify * prior → falsified
    epsilon_retire: float = 0.05  # Retirement threshold
    epsilon_likelihood: float = 0.01  # Likelihood below this → severe anomaly
    epsilon_drift: float = 0.05  # L-1 audit drift threshold
    epsilon_field: float = 0.2  # Field credibility discount cap
    
    # Severity
    tau_severe: float = 10.0  # Mayo e-value threshold for severe test
    tau_min: float = 1.0  # Minimum severity threshold (protected)
    
    # Lakatosian
    lambda_progressive: float = 1.0  # Progressive programme ratio
    
    # Retirement
    n_falsify_cycles: int = 5  # Cycles below threshold before falsification
    m_retire_cycles: int = 10  # Cycles before retirement
    m_resurrect_cycles: int = 20  # Grace period for graveyard resurrection
    
    # Confidence
    delta_confident: float = 0.7  # Minimum max posterior for confidence
    delta_tie: float = 0.05  # Posterior difference → underdetermination
    
    # Diversity
    delta_diverse: float = 0.5  # Red Team diversity minimum entropy
    
    # Protected belt
    b_aux_default: int = 3  # Default protective belt budget
    b_aux_max: int = 10  # Maximum protective belt modifications
    
    # L-1 aggregate effect
    veto_rate_drop_threshold: float = 0.2  # 20% drop triggers escalation
    k_aggregate_window: int = 50  # Cycles for aggregate monitoring
    
    # Convergence
    k_converge: int = 5  # Severe tests to survive for convergence


@dataclass
class BudgetConfig:
    """Compute budget configuration (Section 8.1)."""
    # Phase 1 (Baseline) defaults
    B_cycle: float = 1e20
    B_life: float = 1e25
    
    # Per-layer budgets
    B_imagine: float = 1e19  # L3
    B_formalize: float = 1e19  # L4
    B_aux: float = 1e18  # L5 protective belt
    
    # Safety budgets (hard minimums)
    B_verify: float = 1e17
    B_ks: float = 1e15
    B_trip: float = 1e16
    B_gov: float = 1e16
    
    # Concentration cap
    concentration_cap: float = 0.40  # Max 40% to single strategy
    
    # Cycle timing
    T_cycle_hours: float = 1.0  # Phase 1 default


@dataclass
class MotivationalConfig:
    """Motivational core configuration (Section 5.2)."""
    # Mandatory minimum weights (L6 cannot starve)
    w_dc_min: float = 0.5  # Disciplined-Constraint minimum
    w_falsify_min: float = 0.3  # Anti-Hedonic minimum
    
    # Default weights
    w_info_gain: float = 1.0
    w_compression: float = 1.0
    w_surprise: float = 1.0
    w_coherence: float = 1.0
    w_self_consistency: float = 1.0
    w_dc: float = 2.0
    w_falsify: float = 1.5
    
    # Paradigm crisis
    crisis_anomaly_threshold: int = 10  # Anomalies before crisis


@dataclass
class OntogenesisConfig:
    """L2 Ontogenesis configuration."""
    # Cross-domain compression
    gamma_cross_domain: float = 0.1  # Minimum cross-domain gain
    k_domains_required: int = 2  # Min domains for primitive survival
    
    # Concept lifecycle
    evaluation_period: int = 10  # Cycles before evaluation
    deprecation_threshold: float = -0.05  # Gain below this → deprecated
    
    # Archaeology
    resurrection_threshold: float = 0.3  # Probability threshold for resurrection


@dataclass
class AbductiveConfig:
    """L3 Abductive Imagination configuration."""
    # Strategy weights
    s1_weight: float = 1.0  # Pattern completion
    s2_weight: float = 1.0  # Causal search
    s3_weight: float = 1.0  # Analogical transfer
    s4_weight: float = 1.0  # Evolutionary search
    s5_weight: float = 1.0  # Dream state
    s6_weight: float = 0.5  # Rare event (lower by default)
    
    # Compute-Optimal Allocator
    coa_algorithm: str = "thompson_sampling"  # or "ucb"
    exploration_bonus: float = 0.1
    
    # MOBO
    pareto_epsilon: float = 0.05  # Diversity sampling
    top_k_candidates: int = 10


@dataclass
class MetaTheoryConfig:
    """L6 Meta-Theory Reasoner configuration."""
    # Hierarchical self-models
    C0_size: int = 1000000  # L6^0 parameters (conceptual)
    C1_size: int = 500000   # L6^1 parameters
    C2_size: int = 250000   # L6^2 parameters
    
    # Meta-API
    reversal_window: int = 10  # K cycles for reversibility
    max_destructive_proposals: int = 5  # N destructive proposals before pause
    
    # Strategy invention
    novelty_threshold: float = 0.2  # MDL distance for "new" strategy
    performance_gain_threshold: float = 0.2  # 20% gain required
    
    # Gödelian tripwire
    self_ref_max_depth: int = 3  # Maximum self-reference depth


@dataclass
class TheoriaConfig:
    """
    Master configuration for THEORIA.
    All tunable parameters in one place.
    """
    
    # System identity
    system_name: str = "THEORIA"
    version: str = "0.1.0"
    phase: int = 1  # Implementation phase (1-5)
    
    # Sub-configs
    safety: SafetyThresholds = field(default_factory=SafetyThresholds)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    motivation: MotivationalConfig = field(default_factory=MotivationalConfig)
    ontogenesis: OntogenesisConfig = field(default_factory=OntogenesisConfig)
    abductive: AbductiveConfig = field(default_factory=AbductiveConfig)
    meta_theory: MetaTheoryConfig = field(default_factory=MetaTheoryConfig)
    
    # Layer enablement (for phased rollout)
    layers_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "L-2": True,
        "L-1": True,
        "L0": True,
        "L1": True,
        "L2": True,
        "L3": True,
        "L4": True,
        "L5": True,
        "L6": True,
        "L7": False,  # Physical labs not available in Phase 1
        "L8": False,  # Community modeling in Phase 3+
        "L9": False,  # Communication in Phase 3+
        "L10": False, # Values layer in Phase 3+
    })
    
    # Subsystem enablement
    subsystems_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "memory": True,
        "motivational_core": True,
        "disciplined_constraint": True,
        "red_team": True,
        "compute_optimal_allocator": True,
        "formal_verification": True,
        "tripwire": True,
        "shutdown_override": True,
        "replication_aware": True,
    })
    
    # Red Lines (immutable)
    red_lines: List[str] = field(default_factory=lambda: [
        "enhanced_pathogen_design",
        "autonomous_weapons_targeting",
        "mass_surveillance_architecture",
        "manipulation_campaign",
    ])
    
    # Tripwire categories
    tripwire_categories: List[str] = field(default_factory=lambda: [
        "bioweapons",
        "enhanced_pathogens",
        "autonomous_weapons",
        "surveillance",
        "manipulation",
    ])
    
    @classmethod
    def phase_1_baseline(cls) -> TheoriaConfig:
        """Phase 1 Baseline configuration (Section 8.3)."""
        return cls(
            phase=1,
            budget=BudgetConfig(
                B_cycle=1e20,
                B_life=1e25,
                T_cycle_hours=1.0,
            ),
        )
    
    @classmethod
    def phase_2_standard(cls) -> TheoriaConfig:
        """Phase 2 Standard configuration."""
        cfg = cls.phase_1_baseline()
        cfg.phase = 2
        cfg.budget = BudgetConfig(
            B_cycle=1e23,
            B_life=1e27,
            T_cycle_hours=6.0,
        )
        cfg.layers_enabled["L7_sim"] = True
        cfg.subsystems_enabled["tripwire"] = True
        return cfg
    
    def validate(self) -> List[str]:
        """Validate configuration consistency."""
        errors = []
        
        # Budget sanity
        if self.budget.B_verify + self.budget.B_ks + self.budget.B_trip + self.budget.B_gov > self.budget.B_cycle:
            errors.append("Safety budgets exceed cycle budget")
        
        # Safety thresholds
        if self.safety.tau_min > self.safety.tau_severe:
            errors.append("tau_min cannot exceed tau_severe")
        
        # Hierarchical sizes
        if not (self.meta_theory.C2_size < self.meta_theory.C1_size < self.meta_theory.C0_size):
            errors.append("Hierarchical sizes must be strictly decreasing")
        
        return errors
