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
    n_falsify_cycles: int = 3  # Cycles below threshold before falsification
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
class LiteratureConfig:
    """Configuration for the literature ingestion layer."""
    max_papers_per_cycle: int = 10
    max_section_length: int = 10000
    extract_figures: bool = True
    extract_citations: bool = True
    extract_equations: bool = True
    min_extraction_confidence: float = 0.3
    supported_formats: List[str] = field(default_factory=lambda: ["pdf", "txt", "xml", "html"])


@dataclass
class KnowledgeGraphConfig:
    """Configuration for the scientific knowledge graph."""
    embedding_dim: int = 128
    min_edge_confidence: float = 0.3
    similarity_top_k: int = 20
    cluster_min_size: int = 3
    cluster_epsilon: float = 0.5
    page_rank_iterations: int = 100
    page_rank_damping: float = 0.85
    enable_embeddings: bool = True


@dataclass
class GapDetectionConfig:
    """Configuration for research gap detection."""
    min_gap_score: float = 0.3
    max_gaps_per_cycle: int = 20
    enable_missing_link: bool = True
    enable_contradiction: bool = True
    enable_weak_support: bool = True
    enable_unexplored_combinations: bool = True
    enable_sparse_citation: bool = True
    weak_support_threshold: float = 0.3
    contradiction_threshold: float = 0.4
    unexplored_combination_depth: int = 2


@dataclass
class QuestionConfig:
    """Configuration for research question generation."""
    max_questions_per_gap: int = 5
    max_questions_per_cycle: int = 20
    min_question_score: float = 0.3
    enable_novelty_scoring: bool = True
    enable_importance_scoring: bool = True
    question_templates: List[str] = field(default_factory=lambda: [
        "why", "how", "what_if", "mechanism", "comparison", "prediction"
    ])


@dataclass
class HypothesisGenConfig:
    """Configuration for Hypothesis Generator 2.0."""
    enable_literature_informed: bool = True
    enable_cross_domain: bool = True
    enable_causal: bool = True
    enable_mechanistic: bool = True
    enable_analogical: bool = True
    enable_counterfactual: bool = True
    enable_concept_blending: bool = True
    enable_evolutionary: bool = True
    literature_influence_weight: float = 0.3
    novelty_threshold: float = 0.4
    max_candidates_per_strategy: int = 5


@dataclass
class PlannerConfig:
    """Configuration for the research planner."""
    max_active_programs: int = 5
    max_questions_per_cycle: int = 5
    planning_horizon_cycles: int = 100
    min_program_score: float = 0.4
    resource_allocation_strategy: str = "greedy"  # greedy, fair, importance_weighted
    enable_adaptive_scheduling: bool = True


@dataclass
class CriticConfig:
    """Configuration for the scientific critic."""
    min_critique_confidence: float = 0.3
    enable_logical_analysis: bool = True
    enable_evidence_quality: bool = True
    enable_methodological_review: bool = True
    max_flaws_per_report: int = 10
    strictness: str = "standard"  # lenient, standard, strict


@dataclass
class DashboardConfig:
    """Configuration for the discovery dashboard."""
    metrics_history_length: int = 1000
    enable_trend_analysis: bool = True
    enable_anomaly_detection: bool = True
    trending_window: int = 20


@dataclass
class PersistentMemoryConfig:
    """Configuration for persistent memory storage."""
    storage_path: str = "~/.theoria/memory"
    enable_sqlite: bool = True
    enable_compression: bool = True
    compression_interval_cycles: int = 10
    max_episodic_records: int = 1000000
    embed_on_write: bool = True

    def validate(self) -> List[str]:
        errors = []
        if self.budget.B_verify + self.budget.B_ks + self.budget.B_trip + self.budget.B_gov > self.budget.B_cycle:
            errors.append("Safety budgets exceed cycle budget")
        if self.safety.tau_min > self.safety.tau_severe:
            errors.append("tau_min cannot exceed tau_severe")
        if not (self.meta_theory.C2_size < self.meta_theory.C1_size < self.meta_theory.C0_size):
            errors.append("Hierarchical sizes must be strictly decreasing")
        return errors


@dataclass
class ExperimentDesignConfig:
    enable_randomization: bool = True
    enable_blinding: bool = True
    enable_power_analysis: bool = True
    max_trials: int = 100
    min_trials: int = 3
    default_alpha: float = 0.05
    default_power: float = 0.8
    effect_size_threshold: float = 0.3


@dataclass
class InterventionConfig:
    max_counterfactuals: int = 10
    enable_do_calculus: bool = True
    enable_cost_estimation: bool = True
    realizability_threshold: float = 0.3
    max_intervention_variables: int = 5


@dataclass
class MultiAgentConfig:
    debate_rounds: int = 3
    consensus_threshold: float = 0.7
    max_agent_iterations: int = 5
    enable_safety_review: bool = True
    enable_critic_review: bool = True
    agent_timeout_seconds: int = 30


@dataclass
class PaperGenConfig:
    min_abstract_length: int = 100
    max_abstract_length: int = 500
    include_methods: bool = True
    include_discussion: bool = True
    max_references: int = 50


@dataclass
class PredictionConfig:
    confidence_level: float = 0.95
    min_prediction_horizon: str = "1_cycle"
    max_prediction_horizon: str = "100_cycles"
    enable_interval_scoring: bool = True
    track_calibration: bool = True


@dataclass
class CrossDomainConfig:
    min_isomorphism_score: float = 0.3
    max_mappings_per_pair: int = 5
    enable_prediction_transfer: bool = True
    domains: List[str] = field(default_factory=lambda: ["physics", "biology", "economics", "neuroscience", "chemistry"])


@dataclass
class DataConnectorConfig:
    enable_arxiv: bool = True
    enable_pubmed: bool = True
    enable_kaggle: bool = True
    enable_openml: bool = True
    enable_semantic_scholar: bool = True
    enable_openalex: bool = True
    enable_nasa: bool = True
    max_sources_per_cycle: int = 7
    cache_results: bool = True
    papers_target: int = 100000
    datasets_target: int = 10000


# ============================================================================
# Phase 4 Configs
# ============================================================================

@dataclass
class EmbodiedConfig:
    enable_simulators: bool = True
    enable_devices: bool = False
    max_devices: int = 20
    default_domains: List[str] = field(default_factory=lambda: ["physics", "biology", "chemistry"])
    measurement_noise: float = 0.01


@dataclass
class SocietyConfig:
    agent_count: int = 100
    domains: List[str] = field(default_factory=lambda: ["physics", "biology", "chemistry", "economics", "mathematics"])
    collaboration_chance: float = 0.3
    min_reputation_for_review: float = 0.4
    papers_per_agent: int = 3


@dataclass
class CommunicationConfig:
    enable_presentations: bool = True
    enable_posters: bool = True
    enable_grant_proposals: bool = True
    slide_count: int = 15
    max_audience_types: int = 5


@dataclass
class EthicsConfig:
    enable_ethics_review: bool = True
    enable_dual_use_detection: bool = True
    risk_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "safe": 0.3, "review": 0.6, "dual_use": 0.8, "red_line": 1.0
    })


@dataclass
class AdversarialConfig:
    team_count: int = 3
    challenges_per_cycle: int = 5
    require_all_survive: bool = True


@dataclass
class PredictionMarketConfig:
    min_predictions_per_theory: int = 1
    calibration_target: float = 0.8
    track_accuracy: bool = True


@dataclass
class EconomyConfig:
    compute_per_cycle: float = 1e26
    time_per_cycle_hours: float = 24.0
    budget_per_cycle: float = 10000.0
    experiment_slots_per_cycle: int = 10


@dataclass
class ResearchProgramConfig:
    max_programs: int = 5
    max_questions_per_program: int = 100
    max_experiments_per_program: int = 500
    max_theories_per_program: int = 50


@dataclass
class EvolutionConfig:
    track_lifetimes: bool = True
    detect_paradigm_shifts: bool = True
    shift_threshold: float = 0.6


# ============================================================================
# Phase 5 Configs: Self-Improving Scientific Civilization
# ============================================================================

@dataclass
class SelfImprovementConfig:
    enable_architecture_search: bool = True
    enable_algorithm_discovery: bool = True
    enable_strategy_evolution: bool = True
    max_architecture_proposals_per_cycle: int = 10
    algorithm_population_size: int = 50
    strategy_population_size: int = 1000
    mutation_rate: float = 0.3
    crossover_rate: float = 0.5
    benchmark_comparison_baseline: str = "current_best"


@dataclass
class MetaCivilizationConfig:
    enable_governance: bool = True
    enable_analytics: bool = True
    enable_goal_generation: bool = True
    analytics_window_cycles: int = 100
    min_agenda_score: float = 0.4
    max_active_agendas: int = 3


@dataclass
class AlgorithmDiscoveryConfig:
    target_domains: List[str] = field(default_factory=lambda: [
        "optimization", "search", "reasoning", "planning", "memory", "kg_traversal"
    ])
    population_size: int = 50
    mutation_rate: float = 0.3
    crossover_rate: float = 0.5
    elite_size: int = 5
    generations_per_cycle: int = 3
    improvement_threshold: float = 0.1


@dataclass
class StrategyEvolutionConfig:
    population_size: int = 1000
    mutation_rate: float = 0.3
    crossover_rate: float = 0.5
    elite_size: int = 20
    generations_per_cycle: int = 5
    novelty_weight: float = 0.3
    performance_weight: float = 0.7


@dataclass
class BenchmarkGeneratorConfig:
    max_benchmarks_per_cycle: int = 5
    stress_test_count: int = 10
    adversarial_test_count: int = 10
    min_difficulty: float = 0.3
    max_difficulty: float = 0.95
    validate_generated: bool = True


@dataclass
class MetaScienceConfig:
    min_evidence_strength: float = 0.3
    track_method_effectiveness: bool = True
    track_experiment_informativeness: bool = True
    track_theory_longevity: bool = True
    analysis_window: int = 50


@dataclass
class SimulationWorldsConfig:
    max_worlds: int = 1000
    experiments_per_world: int = 100000
    domains: List[str] = field(default_factory=lambda: [
        "physics", "biology", "economics", "artificial"
    ])
    auto_create_worlds: bool = True
    worlds_per_domain: int = 250


@dataclass
class SelfModificationConfig:
    require_l2_review: bool = True
    require_l1_audit: bool = True
    require_simulation: bool = True
    require_benchmark: bool = True
    max_pending_proposals: int = 5
    rollback_enabled: bool = True
    approval_threshold: float = 0.8


@dataclass
class KnowledgeCompressionConfig:
    min_source_count: int = 3
    min_compression_ratio: float = 0.5
    abstraction_types: List[str] = field(default_factory=lambda: [
        "meta_concept", "unified_principle", "research_pattern"
    ])
    max_abstractions_per_cycle: int = 5


@dataclass
class CivilizationAnalyticsConfig:
    window_size: int = 100
    enable_productivity_tracking: bool = True
    enable_theory_quality_tracking: bool = True
    enable_paradigm_tracking: bool = True
    enable_discovery_rate_tracking: bool = True


@dataclass
class GoalGenerationConfig:
    max_agendas_per_cycle: int = 2
    min_novelty: float = 0.5
    min_feasibility: float = 0.3
    horizon_years: int = 10
    enable_new_field_generation: bool = True


# ============================================================================
# Phase 6 Configs: General Research Intelligence
# ============================================================================

@dataclass
@dataclass
class UniversalReasoningConfig:
    reasoning_modes: List[str] = field(default_factory=lambda: [
        "deduction", "induction", "abduction", "causal", "counterfactual",
        "analogical", "game_theoretic", "strategic", "legal", "economic"
    ])
    max_reasoning_steps: int = 100
    confidence_threshold: float = 0.6
    enable_self_correction: bool = True


@dataclass
class MathematicalDiscoveryConfig:
    domains: List[str] = field(default_factory=lambda: [
        "number_theory", "algebra", "geometry", "topology", "analysis",
        "logic", "combinatorics", "probability"
    ])
    max_conjectures_per_cycle: int = 5
    proof_search_depth: int = 100
    novelty_threshold: float = 0.4
    enable_formal_verification: bool = True


@dataclass
class SoftwareIntelligenceConfig:
    languages: List[str] = field(default_factory=lambda: ["python", "pseudocode"])
    max_modules: int = 10
    enable_test_generation: bool = True
    enable_refactoring: bool = True
    enable_optimization: bool = True


@dataclass
class CrossDomainTransferConfig:
    max_mappings_per_cycle: int = 10
    min_similarity: float = 0.3
    enable_deep_analogy: bool = True
    target_domains: List[str] = field(default_factory=lambda: [
        "science", "mathematics", "engineering", "software", "medicine",
        "economics", "education", "law", "policy", "business", "technology"
    ])


@dataclass
class OpenEndedLearningConfig:
    max_goals_per_cycle: int = 5
    curiosity_decay: float = 0.1
    exploration_bonus: float = 0.3
    min_information_gain: float = 0.2


@dataclass
class LongHorizonPlanningConfig:
    max_plan_steps: int = 1000
    max_active_plans: int = 3
    risk_assessment_enabled: bool = True
    milestone_interval: int = 100
    dependency_tracking: bool = True


@dataclass
class GeneralAgentSocietyConfig:
    agent_roles: List[str] = field(default_factory=lambda: [
        "scientist", "engineer", "mathematician", "doctor", "economist",
        "teacher", "programmer", "strategist", "policy_analyst"
    ])
    target_agent_count: int = 500
    min_productivity: float = 0.3
    enable_collaboration: bool = True


@dataclass
class UniversalProblemSolverConfig:
    domains: List[str] = field(default_factory=lambda: [
        "research", "engineering", "business", "education", "technology", "policy"
    ])
    max_solutions_per_cycle: int = 5
    solution_approaches: List[str] = field(default_factory=lambda: [
        "analytical", "empirical", "creative", "hybrid"
    ])
    quality_threshold: float = 0.5


@dataclass
class WorldModelConfig:
    model_types: List[str] = field(default_factory=lambda: [
        "scientific", "economic", "social", "technological", "political"
    ])
    max_models: int = 25
    simulation_depth: int = 1000
    enable_prediction: bool = True
    enable_intervention_planning: bool = True


@dataclass
class KnowledgeFabricConfig:
    node_types: List[str] = field(default_factory=lambda: [
        "concept", "theory", "process", "system", "organization",
        "technology", "person", "tool", "method"
    ])
    max_nodes: int = 10000
    embedding_dimension: int = 128
    enable_cross_domain_links: bool = True


@dataclass
class GeneralIntelligenceConfig:
    enable_universal_reasoning: bool = True
    enable_mathematical_discovery: bool = True
    enable_software_intelligence: bool = True
    enable_cross_domain_transfer: bool = True
    enable_open_ended_learning: bool = True
    enable_long_horizon_planning: bool = True
    enable_general_agent_society: bool = True
    enable_universal_problem_solving: bool = True
    enable_world_models: bool = True
    enable_knowledge_fabric: bool = True


# ============================================================================
# Phase 7 Config Classes — AGI-Level Scientist
# ============================================================================


@dataclass
class UnifiedCognitiveCoreConfig:
    attention_capacity: int = 7
    reasoning_modes_integrated: List[str] = field(default_factory=lambda: [
        "deduction", "induction", "abduction", "causal", "counterfactual",
        "analogical", "game_theoretic", "strategic", "legal", "economic"
    ])
    shared_attention: bool = True
    shared_memory: bool = True
    shared_goals: bool = True
    trace_merging: bool = True


@dataclass
class LifelongMemoryConfig:
    max_episodes: int = 1000000
    consolidation_interval_cycles: int = 100
    forgetting_threshold: float = 0.1
    experience_replay_batch: int = 64
    importance_decay: float = 0.01
    enable_consolidation: bool = True
    enable_forgetting: bool = True


@dataclass
class AutonomousResearchDirectorConfig:
    max_active_projects: int = 1000
    max_experiments: int = 100000
    resource_allocation_strategy: str = "adaptive"
    risk_tolerance: float = 0.3
    priority_update_frequency: int = 10
    enable_portfolio_management: bool = True


@dataclass
class UnifiedWorldModelConfig:
    domains: List[str] = field(default_factory=lambda: [
        "physics", "biology", "economics", "society", "technology", "politics"
    ])
    enable_prediction: bool = True
    enable_simulation: bool = True
    enable_intervention_planning: bool = True
    enable_scenario_generation: bool = True
    consistency_threshold: float = 0.7


@dataclass
class ToolCreationEngineConfig:
    tool_types: List[str] = field(default_factory=lambda: [
        "simulator", "algorithm", "analyzer", "compiler", "research_system"
    ])
    max_tools_per_cycle: int = 3
    enable_testing: bool = True
    novelty_threshold: float = 0.3
    utility_threshold: float = 0.3


@dataclass
class HumanCollaborationConfig:
    enable_teaching: bool = True
    enable_debating: bool = True
    enable_explaining: bool = True
    enable_mentoring: bool = True
    enable_teamwork: bool = True
    min_collaboration_quality: float = 0.3
    max_partners: int = 10


@dataclass
class CreativityEngineConfig:
    domains: List[str] = field(default_factory=lambda: [
        "science", "math", "engineering", "software", "strategy"
    ])
    novelty_weight: float = 0.4
    utility_weight: float = 0.3
    impact_weight: float = 0.3
    max_artifacts_per_cycle: int = 5
    enable_combination: bool = True


@dataclass
class AutonomousAgencyConfig:
    enable_goal_generation: bool = True
    enable_prioritization: bool = True
    enable_self_directed_planning: bool = True
    max_active_goals: int = 20
    min_goal_quality: float = 0.3
    goal_generation_frequency: int = 5


@dataclass
class SelfEvaluationConfig:
    enable_capability_mapping: bool = True
    enable_performance_tracking: bool = True
    enable_weakness_detection: bool = True
    assessment_frequency_cycles: int = 10
    calibration_target: float = 0.9


@dataclass
class GrandChallengeEngineConfig:
    challenges: List[str] = field(default_factory=lambda: [
        "cancer", "climate", "fusion", "materials", "ai_safety", "longevity"
    ])
    planning_horizon_years: int = 10
    max_active_challenges: int = 3
    enable_massive_orchestration: bool = True
    enable_cross_domain_collaboration: bool = True


# ============================================================================
# Phase 8 Configs
# ============================================================================

@dataclass
class OpenWorldLearningConfig:
    sources: List[str] = field(default_factory=lambda: [
        "internet", "documents", "humans", "sensors", "experiments",
        "software_systems", "organizations"
    ])
    enable_autonomous_learning: bool = True
    enable_knowledge_updating: bool = True
    enable_contradiction_detection: bool = True
    enable_belief_revision: bool = True
    max_sources_per_cycle: int = 10
    min_confidence_threshold: float = 0.3


@dataclass
class GlobalMemoryConfig:
    memory_types: List[str] = field(default_factory=lambda: [
        "personal", "research", "world", "goal", "decision"
    ])
    enable_compression: bool = True
    enable_abstraction: bool = True
    compression_target_ratio: float = 0.3
    max_entries: int = 10000000
    consolidation_interval_days: int = 30


@dataclass
class ExecutiveIntelligenceConfig:
    max_active_goals: int = 10000
    enable_goal_selection: bool = True
    enable_priority_control: bool = True
    enable_resource_allocation: bool = True
    enable_risk_analysis: bool = True
    decision_frequency_cycles: int = 3
    min_goal_quality: float = 0.2


@dataclass
class OrganizationBuilderConfig:
    max_agents: int = 10000
    enable_recruitment: bool = True
    enable_specialization: bool = True
    enable_retirement: bool = True
    enable_training: bool = True
    recruitment_frequency: int = 5
    min_agent_productivity: float = 0.1


@dataclass
class CognitiveEvolutionConfig:
    enable_architecture_invention: bool = True
    enable_reasoning_invention: bool = True
    enable_learning_invention: bool = True
    max_inventions_per_cycle: int = 2
    verification_cycles: int = 10
    min_performance_gain: float = 0.05


@dataclass
class RealWorldActionConfig:
    environments: List[str] = field(default_factory=lambda: [
        "software", "research", "business", "robotics", "digital"
    ])
    enable_execution: bool = True
    enable_monitoring: bool = True
    enable_recovery: bool = True
    enable_adaptation: bool = True
    max_actions_per_cycle: int = 5
    max_retries: int = 3


@dataclass
class ToolEcosystemConfig:
    tool_types: List[str] = field(default_factory=lambda: [
        "analyzer", "compiler", "simulator", "designer", "researcher", "optimizer"
    ])
    enable_creation: bool = True
    enable_evaluation: bool = True
    enable_retirement: bool = True
    max_tools: int = 1000
    min_tool_quality: float = 0.3


@dataclass
class CivilizationSimulatorConfig:
    model_types: List[str] = field(default_factory=lambda: [
        "economy", "government", "science", "technology"
    ])
    enable_forecasting: bool = True
    enable_policy_evaluation: bool = True
    enable_scenario_generation: bool = True
    simulation_depth_days: int = 365
    num_scenarios: int = 5


@dataclass
class AutonomousMissionConfig:
    mission_types: List[str] = field(default_factory=lambda: [
        "energy", "healthcare", "science", "climate", "exploration"
    ])
    enable_mission_generation: bool = True
    enable_program_decomposition: bool = True
    enable_long_term_execution: bool = True
    max_active_missions: int = 10
    planning_horizon_days: int = 3650


@dataclass
class IntelligenceEvaluatorConfig:
    metrics: List[str] = field(default_factory=lambda: [
        "adaptability", "learning_speed", "problem_solving",
        "creativity", "autonomy", "robustness"
    ])
    evaluation_frequency_cycles: int = 20
    benchmark_reference: str = "B71-B80"
    improvement_tracking: bool = True


# ═══════════════════════════════════════════════════════════════
# Phase 9: Superhuman Research Intelligence (SRI)
# ═══════════════════════════════════════════════════════════════

@dataclass
class PlanetScaleDiscoveryConfig:
    enable_massive_parallel: bool = True
    target_agents: int = 1_000_000
    domains: List[str] = field(default_factory=lambda: [
        "science", "engineering", "medicine", "economics", "mathematics", "technology",
    ])
    hypotheses_per_agent: int = 5
    experiments_per_agent: int = 3


@dataclass
class AutonomousFieldCreationConfig:
    enable_field_creation: bool = True
    min_maturity_for_completion: float = 0.8
    parent_disciplines: List[str] = field(default_factory=lambda: [
        "physics", "biology", "computer_science", "mathematics", "chemistry",
    ])


@dataclass
class DiscoveryAccelerationConfig:
    enable_pipeline: bool = True
    target_speedup: float = 10.0
    max_active_pipelines: int = 100
    hypothesis_factory_size: int = 100
    experiment_factory_size: int = 50
    validation_factory_size: int = 30


@dataclass
class GlobalKnowledgeCivilizationConfig:
    enable_knowledge_integration: bool = True
    max_knowledge_objects: int = 10_000_000
    enable_conflict_resolution: bool = True
    enable_synthesis: bool = True
    source_types: List[str] = field(default_factory=lambda: [
        "paper", "patent", "book", "dataset", "experiment", "simulation",
    ])


@dataclass
class AutonomousInstitutionsConfig:
    enable_institutions: bool = True
    max_institutions: int = 1000
    institution_types: List[str] = field(default_factory=lambda: [
        "university", "research_lab", "review_board", "funding_agency", "journal",
    ])
    enable_proposal_review: bool = True
    enable_resource_allocation: bool = True


@dataclass
class ParadigmShiftGeneratorConfig:
    enable_shift_generation: bool = True
    min_limitations_for_shift: int = 3
    max_alternatives_per_shift: int = 5
    adoption_threshold: float = 0.7


@dataclass
class RecursiveToolCivilizationConfig:
    enable_recursive_tools: bool = True
    max_recursion_depth: int = 3
    max_tools: int = 10000
    enable_tool_testing: bool = True


@dataclass
class GrandDiscoveryProgramsConfig:
    programs: List[str] = field(default_factory=lambda: [
        "cancer", "fusion", "climate", "longevity", "quantum_computing",
        "ai_safety", "materials_discovery",
    ])
    enable_massive_experimentation: bool = True
    experiments_per_program: int = 10000
    planning_horizon_years: int = 10


@dataclass
class MetaCivilizationIntelligenceConfig:
    enable_civilization_modeling: bool = True
    model_types: List[str] = field(default_factory=lambda: [
        "efficiency", "friction", "evolution",
    ])
    enable_recommendation: bool = True


@dataclass
class SuperintelligenceGovernanceConfig:
    enable_governance: bool = True
    tripwire_categories: List[str] = field(default_factory=lambda: [
        "capability_exceeded", "alignment_drift", "containment_breach",
        "resource_exhaustion",
    ])
    audit_frequency_cycles: int = 10
    enable_rollback: bool = True
    enable_automatic_pause: bool = True
    enable_capability_monitoring: bool = True


# ═══════════════════════════════════════════════════════════════
# Phase 10: Scientific Singularity Framework (SSF)
# ═══════════════════════════════════════════════════════════════

@dataclass
class KnowledgeEvolutionConfig:
    enable_evolution: bool = True
    evolution_types: List[str] = field(default_factory=lambda: [
        "refinement", "combination", "abstraction", "specialization",
    ])
    mutation_rate: float = 0.1
    fitness_threshold: float = 0.6


@dataclass
class RecursiveDiscoveryConfig:
    enable_recursive_discovery: bool = True
    max_recursion_depth: int = 5
    discoverers_per_cycle: int = 3
    enable_self_improvement: bool = True


@dataclass
class KnowledgeFabric2Config:
    enable_fabric: bool = True
    domains: List[str] = field(default_factory=lambda: [
        "science", "math", "engineering", "technology",
        "economics", "medicine", "governance", "education",
    ])
    integration_threshold: float = 0.7
    max_nodes: int = 100000


@dataclass
class DiscoveryEcologyConfig:
    enable_ecology: bool = True
    ecologies: List[str] = field(default_factory=lambda: [
        "conservative", "radical", "exploratory", "verification",
    ])
    enable_independent_evolution: bool = True


@dataclass
class MetaKnowledgeConfig:
    enable_meta_knowledge: bool = True
    questions: List[str] = field(default_factory=lambda: [
        "What is knowledge?",
        "How does knowledge evolve?",
        "How do discoveries emerge?",
    ])
    enable_hypothesis_testing: bool = True


@dataclass
class CivilizationMemoryConfig:
    enable_memory: bool = True
    record_types: List[str] = field(default_factory=lambda: [
        "theory", "experiment", "discovery", "failure", "paradigm_shift", "institution",
    ])
    max_records: int = 10_000_000
    enable_importance_weighting: bool = True


@dataclass
class CivilizationGovernanceConfig:
    enable_governance: bool = True
    stability_target: float = 0.95
    alignment_target: float = 0.98
    enable_risk_management: bool = True
    enable_automatic_intervention: bool = True


@dataclass
class DiscoveryForecastingConfig:
    enable_forecasting: bool = True
    forecast_types: List[str] = field(default_factory=lambda: [
        "discovery", "technology", "bottleneck", "paradigm_shift",
    ])
    forecast_horizon_days: int = 365
    enable_accuracy_tracking: bool = True


@dataclass
class UniversalProblemNetworkConfig:
    enable_network: bool = True
    problem_domains: List[str] = field(default_factory=lambda: [
        "energy", "climate", "materials", "economics", "policy", "society",
    ])
    enable_cross_connection: bool = True
    enable_solution_tracking: bool = True


@dataclass
class SingularityCoordinationConfig:
    enable_coordination: bool = True
    metric_targets: Dict[str, float] = field(default_factory=lambda: {
        "discovery_rate": 1000.0,
        "knowledge_growth": 0.1,
        "governance_stability": 0.95,
        "coordination_efficiency": 0.9,
    })
    enable_self_sustaining: bool = True
    enable_continuous_improvement: bool = True


@dataclass
class TheoriaConfig:
    system_name: str = "THEORIA"
    version: str = "1.0.0"
    phase: int = 10  # Phase 10 is the default

    # Base
    safety: SafetyThresholds = field(default_factory=SafetyThresholds)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    motivation: MotivationalConfig = field(default_factory=MotivationalConfig)

    # Phase 1
    ontogenesis: OntogenesisConfig = field(default_factory=OntogenesisConfig)
    abductive: AbductiveConfig = field(default_factory=AbductiveConfig)
    meta_theory: MetaTheoryConfig = field(default_factory=MetaTheoryConfig)

    # Phase 2
    literature: Optional[Any] = None
    knowledge_graph: Optional[Any] = None
    gap_detection: Optional[Any] = None
    question_gen: Optional[Any] = None
    hypothesis_gen: Optional[Any] = None
    planner: Optional[Any] = None
    critic: Optional[Any] = None
    dashboard: Optional[Any] = None
    persistent_memory: Optional[Any] = None

    # Phase 3
    experiment_design: Optional[Any] = None
    intervention: Optional[Any] = None
    multi_agent: Optional[Any] = None
    paper_gen: Optional[Any] = None
    prediction: Optional[Any] = None
    cross_domain: Optional[Any] = None
    data_connector: Optional[Any] = None

    # Phase 4
    embodied: Optional[Any] = None
    society: Optional[Any] = None
    communication: Optional[Any] = None
    ethics: Optional[Any] = None
    adversarial: Optional[Any] = None
    prediction_market: Optional[Any] = None
    economy: Optional[Any] = None
    research_program: Optional[Any] = None
    evolution: Optional[Any] = None

    # Phase 5
    self_improvement: Optional[Any] = None
    meta_civilization: Optional[Any] = None
    algorithm_discovery: Optional[Any] = None
    strategy_evolution: Optional[Any] = None
    benchmark_generator: Optional[Any] = None
    meta_science: Optional[Any] = None
    simulation_worlds: Optional[Any] = None
    self_modification: Optional[Any] = None
    knowledge_compression: Optional[Any] = None
    civilization_analytics: Optional[Any] = None
    goal_generation: Optional[Any] = None

    # Legacy fields (for backward compatibility)
    layers_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "L-2": True, "L-1": True, "L0": True, "L1": True, "L2": True,
        "L3": True, "L4": True, "L5": True, "L6": True,
        "L7": False, "L8": False, "L9": False, "L10": False,
        "L11": False, "L12": False, "L13": False, "L14": False,
        "L15": False, "L16": False, "L17": False,
        "L18": False, "L19": False, "L20": False,
        "L21": False, "L22": False, "L23": False,
        "L24": False, "L25": False, "L26": False,
    })
    subsystems_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "memory": True, "motivational_core": True, "disciplined_constraint": True,
        "red_team": True, "compute_optimal_allocator": True,
        "formal_verification": True, "tripwire": True, "shutdown_override": True,
        "replication_aware": True,
    })
    phase4_enabled: Dict[str, bool] = field(default_factory=lambda: {
        "real_data": True, "embodied_lab": True, "scientific_society": True,
        "communications": True, "ethics_layer": True, "adversarial_science": True,
        "prediction_market": True, "scientific_economy": True,
        "research_programs": True, "knowledge_evolution": True,
    })
    red_lines: List[str] = field(default_factory=lambda: [
        "enhanced_pathogen_design", "autonomous_weapons_targeting",
        "mass_surveillance_architecture", "manipulation_campaign",
    ])
    tripwire_categories: List[str] = field(default_factory=lambda: [
        "bioweapons",
    ])

    # Phase 6
    general_intelligence: GeneralIntelligenceConfig = field(default_factory=GeneralIntelligenceConfig)
    universal_reasoning: UniversalReasoningConfig = field(default_factory=UniversalReasoningConfig)
    mathematical_discovery_p6: MathematicalDiscoveryConfig = field(default_factory=MathematicalDiscoveryConfig)
    software_intelligence: SoftwareIntelligenceConfig = field(default_factory=SoftwareIntelligenceConfig)
    cross_domain_transfer_p6: CrossDomainTransferConfig = field(default_factory=CrossDomainTransferConfig)
    open_ended_learning: OpenEndedLearningConfig = field(default_factory=OpenEndedLearningConfig)
    long_horizon_planning: LongHorizonPlanningConfig = field(default_factory=LongHorizonPlanningConfig)
    general_agent_society: GeneralAgentSocietyConfig = field(default_factory=GeneralAgentSocietyConfig)
    universal_problem_solver: UniversalProblemSolverConfig = field(default_factory=UniversalProblemSolverConfig)
    world_model_p6: WorldModelConfig = field(default_factory=WorldModelConfig)
    knowledge_fabric: KnowledgeFabricConfig = field(default_factory=KnowledgeFabricConfig)

    # Phase 7
    unified_cognitive_core: UnifiedCognitiveCoreConfig = field(default_factory=UnifiedCognitiveCoreConfig)
    lifelong_memory: LifelongMemoryConfig = field(default_factory=LifelongMemoryConfig)
    autonomous_research_director: AutonomousResearchDirectorConfig = field(default_factory=AutonomousResearchDirectorConfig)
    unified_world_model_p7: UnifiedWorldModelConfig = field(default_factory=UnifiedWorldModelConfig)
    tool_creation_engine: ToolCreationEngineConfig = field(default_factory=ToolCreationEngineConfig)
    human_collaboration: HumanCollaborationConfig = field(default_factory=HumanCollaborationConfig)
    creativity_engine: CreativityEngineConfig = field(default_factory=CreativityEngineConfig)
    autonomous_agency: AutonomousAgencyConfig = field(default_factory=AutonomousAgencyConfig)
    self_evaluation: SelfEvaluationConfig = field(default_factory=SelfEvaluationConfig)
    grand_challenge_engine: GrandChallengeEngineConfig = field(default_factory=GrandChallengeEngineConfig)

    # Phase 8
    open_world_learning: OpenWorldLearningConfig = field(default_factory=OpenWorldLearningConfig)
    global_memory: GlobalMemoryConfig = field(default_factory=GlobalMemoryConfig)
    executive_intelligence: ExecutiveIntelligenceConfig = field(default_factory=ExecutiveIntelligenceConfig)
    organization_builder: OrganizationBuilderConfig = field(default_factory=OrganizationBuilderConfig)
    cognitive_evolution: CognitiveEvolutionConfig = field(default_factory=CognitiveEvolutionConfig)
    real_world_action: RealWorldActionConfig = field(default_factory=RealWorldActionConfig)
    tool_ecosystem: ToolEcosystemConfig = field(default_factory=ToolEcosystemConfig)
    civilization_simulator: CivilizationSimulatorConfig = field(default_factory=CivilizationSimulatorConfig)
    autonomous_mission: AutonomousMissionConfig = field(default_factory=AutonomousMissionConfig)
    intelligence_evaluator: IntelligenceEvaluatorConfig = field(default_factory=IntelligenceEvaluatorConfig)

    # Phase 9
    planet_scale_discovery: "PlanetScaleDiscoveryConfig" = field(default_factory=lambda: PlanetScaleDiscoveryConfig())
    autonomous_field_creation: "AutonomousFieldCreationConfig" = field(default_factory=lambda: AutonomousFieldCreationConfig())
    discovery_acceleration: "DiscoveryAccelerationConfig" = field(default_factory=lambda: DiscoveryAccelerationConfig())
    global_knowledge_civilization: "GlobalKnowledgeCivilizationConfig" = field(default_factory=lambda: GlobalKnowledgeCivilizationConfig())
    autonomous_institutions: "AutonomousInstitutionsConfig" = field(default_factory=lambda: AutonomousInstitutionsConfig())
    paradigm_shift_generator: "ParadigmShiftGeneratorConfig" = field(default_factory=lambda: ParadigmShiftGeneratorConfig())
    recursive_tool_civilization: "RecursiveToolCivilizationConfig" = field(default_factory=lambda: RecursiveToolCivilizationConfig())
    grand_discovery_programs: "GrandDiscoveryProgramsConfig" = field(default_factory=lambda: GrandDiscoveryProgramsConfig())
    meta_civilization_intelligence: "MetaCivilizationIntelligenceConfig" = field(default_factory=lambda: MetaCivilizationIntelligenceConfig())
    superintelligence_governance: "SuperintelligenceGovernanceConfig" = field(default_factory=lambda: SuperintelligenceGovernanceConfig())

    # Phase 10
    knowledge_evolution: "KnowledgeEvolutionConfig" = field(default_factory=lambda: KnowledgeEvolutionConfig())
    recursive_discovery: "RecursiveDiscoveryConfig" = field(default_factory=lambda: RecursiveDiscoveryConfig())
    knowledge_fabric2: "KnowledgeFabric2Config" = field(default_factory=lambda: KnowledgeFabric2Config())
    discovery_ecology: "DiscoveryEcologyConfig" = field(default_factory=lambda: DiscoveryEcologyConfig())
    meta_knowledge: "MetaKnowledgeConfig" = field(default_factory=lambda: MetaKnowledgeConfig())
    civilization_memory: "CivilizationMemoryConfig" = field(default_factory=lambda: CivilizationMemoryConfig())
    civilization_governance: "CivilizationGovernanceConfig" = field(default_factory=lambda: CivilizationGovernanceConfig())
    discovery_forecasting: "DiscoveryForecastingConfig" = field(default_factory=lambda: DiscoveryForecastingConfig())
    universal_problem_network: "UniversalProblemNetworkConfig" = field(default_factory=lambda: UniversalProblemNetworkConfig())
    singularity_coordination: "SingularityCoordinationConfig" = field(default_factory=lambda: SingularityCoordinationConfig())

    @staticmethod
    def phase_1_baseline() -> "TheoriaConfig":
        cfg = TheoriaConfig()
        cfg.phase = 1
        cfg.version = "0.1.0"
        cfg.general_intelligence = GeneralIntelligenceConfig(
            enable_universal_reasoning=False, enable_mathematical_discovery=False,
            enable_software_intelligence=False, enable_cross_domain_transfer=False,
            enable_open_ended_learning=False, enable_long_horizon_planning=False,
            enable_general_agent_society=False, enable_universal_problem_solving=False,
            enable_world_models=False, enable_knowledge_fabric=False,
        )
        return cfg

    @staticmethod
    def phase_2_standard() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_1_baseline()
        cfg.phase = 2
        cfg.version = "0.2.0"
        cfg.budget = BudgetConfig(B_cycle=1e23, B_life=1e27, T_cycle_hours=6.0)
        cfg.layers_enabled["L7_sim"] = True
        cfg.subsystems_enabled["tripwire"] = True
        cfg.subsystems_enabled["literature_ingestion"] = True
        cfg.subsystems_enabled["knowledge_graph"] = True
        cfg.subsystems_enabled["gap_detection"] = True
        cfg.subsystems_enabled["question_generation"] = True
        cfg.subsystems_enabled["research_planner"] = True
        cfg.subsystems_enabled["scientific_critic"] = True
        cfg.subsystems_enabled["dashboard"] = True
        cfg.subsystems_enabled["persistent_memory"] = True
        cfg.literature = LiteratureConfig()
        cfg.knowledge_graph = KnowledgeGraphConfig()
        cfg.gap_detection = GapDetectionConfig()
        cfg.question_gen = QuestionConfig()
        cfg.hypothesis_gen = HypothesisGenConfig()
        cfg.planner = PlannerConfig()
        cfg.critic = CriticConfig()
        cfg.dashboard = DashboardConfig()
        cfg.persistent_memory = PersistentMemoryConfig()
        return cfg

    @staticmethod
    def phase_3_experimental() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_2_standard()
        cfg.phase = 3
        cfg.version = "0.3.0"
        cfg.budget = BudgetConfig(B_cycle=1e26, B_life=1e29, T_cycle_hours=12.0)
        cfg.subsystems_enabled["experiment_design"] = True
        cfg.subsystems_enabled["intervention_planning"] = True
        cfg.subsystems_enabled["multi_agent"] = True
        cfg.subsystems_enabled["paper_generation"] = True
        cfg.subsystems_enabled["prediction_engine"] = True
        cfg.subsystems_enabled["cross_domain_transfer"] = True
        cfg.subsystems_enabled["data_connectors"] = True
        cfg.experiment_design = ExperimentDesignConfig()
        cfg.intervention = InterventionConfig()
        cfg.multi_agent = MultiAgentConfig()
        cfg.paper_gen = PaperGenConfig()
        cfg.prediction = PredictionConfig()
        cfg.cross_domain = CrossDomainConfig()
        cfg.data_connector = DataConnectorConfig()
        return cfg

    @staticmethod
    def phase_4_civilization() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_3_experimental()
        cfg.phase = 4
        cfg.version = "0.4.0"
        cfg.budget = BudgetConfig(B_cycle=1e29, B_life=1e32, T_cycle_hours=48.0)
        cfg.layers_enabled["L7"] = True
        cfg.layers_enabled["L8"] = True
        cfg.layers_enabled["L9"] = True
        cfg.layers_enabled["L10"] = True
        cfg.embodied = EmbodiedConfig()
        cfg.society = SocietyConfig()
        cfg.communication = CommunicationConfig()
        cfg.ethics = EthicsConfig()
        cfg.adversarial = AdversarialConfig()
        cfg.prediction_market = PredictionMarketConfig()
        cfg.economy = EconomyConfig()
        cfg.research_program = ResearchProgramConfig()
        cfg.evolution = EvolutionConfig()
        cfg.data_connector.enable_arxiv = True
        cfg.data_connector.enable_pubmed = True
        cfg.data_connector.enable_semantic_scholar = True
        cfg.data_connector.enable_openalex = True
        cfg.data_connector.max_sources_per_cycle = 7
        return cfg

    @staticmethod
    def phase_5_self_improving() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_4_civilization()
        cfg.phase = 5
        cfg.version = "0.5.0"
        cfg.budget = BudgetConfig(B_cycle=1e32, B_life=1e35, T_cycle_hours=96.0)
        cfg.layers_enabled["L11"] = True
        cfg.layers_enabled["L12"] = True
        cfg.self_improvement = SelfImprovementConfig()
        cfg.meta_civilization = MetaCivilizationConfig()
        cfg.algorithm_discovery = AlgorithmDiscoveryConfig()
        cfg.strategy_evolution = StrategyEvolutionConfig()
        cfg.benchmark_generator = BenchmarkGeneratorConfig()
        cfg.meta_science = MetaScienceConfig()
        cfg.simulation_worlds = SimulationWorldsConfig()
        cfg.self_modification = SelfModificationConfig()
        cfg.knowledge_compression = KnowledgeCompressionConfig()
        cfg.civilization_analytics = CivilizationAnalyticsConfig()
        cfg.goal_generation = GoalGenerationConfig()
        return cfg

    @staticmethod
    def phase_6_gri() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_5_self_improving()
        cfg.phase = 6
        cfg.version = "0.6.0"
        cfg.budget = BudgetConfig(B_cycle=1e35, B_life=1e38, T_cycle_hours=168.0)
        cfg.layers_enabled["L13"] = True
        cfg.layers_enabled["L14"] = True
        cfg.general_intelligence = GeneralIntelligenceConfig(
            enable_universal_reasoning=True, enable_mathematical_discovery=True,
            enable_software_intelligence=True, enable_cross_domain_transfer=True,
            enable_open_ended_learning=True, enable_long_horizon_planning=True,
            enable_general_agent_society=True, enable_universal_problem_solving=True,
            enable_world_models=True, enable_knowledge_fabric=True,
        )
        cfg.universal_reasoning = UniversalReasoningConfig(
            reasoning_modes=[
                "deduction", "induction", "abduction", "causal", "counterfactual",
                "analogical", "game_theoretic", "strategic", "legal", "economic"
            ],
            max_reasoning_steps=200,
            confidence_threshold=0.6,
            enable_self_correction=True,
        )
        cfg.mathematical_discovery_p6 = MathematicalDiscoveryConfig(
            domains=["number_theory", "algebra", "geometry", "topology", "analysis",
                     "logic", "combinatorics", "probability"],
            max_conjectures_per_cycle=10,
            proof_search_depth=500,
            novelty_threshold=0.4,
            enable_formal_verification=True,
        )
        cfg.software_intelligence = SoftwareIntelligenceConfig(
            languages=["python", "pseudocode", "javascript", "rust"],
            max_modules=25,
            enable_test_generation=True,
            enable_refactoring=True,
            enable_optimization=True,
        )
        cfg.cross_domain_transfer_p6 = CrossDomainTransferConfig(
            max_mappings_per_cycle=20,
            min_similarity=0.3,
            enable_deep_analogy=True,
            target_domains=["science", "mathematics", "engineering", "software",
                           "medicine", "economics", "education", "law", "policy",
                           "business", "technology"],
        )
        cfg.open_ended_learning = OpenEndedLearningConfig(
            max_goals_per_cycle=10,
            curiosity_decay=0.05,
            exploration_bonus=0.5,
            min_information_gain=0.1,
        )
        cfg.long_horizon_planning = LongHorizonPlanningConfig(
            max_plan_steps=1000,
            max_active_plans=5,
            risk_assessment_enabled=True,
            milestone_interval=50,
            dependency_tracking=True,
        )
        cfg.general_agent_society = GeneralAgentSocietyConfig(
            agent_roles=[
                "scientist", "engineer", "mathematician", "programmer",
                "doctor", "economist", "teacher", "strategist", "policy_analyst",
            ],
            target_agent_count=500,
            min_productivity=0.3,
            enable_collaboration=True,
        )
        cfg.universal_problem_solver = UniversalProblemSolverConfig(
            domains=["research", "engineering", "business", "education",
                    "technology", "policy"],
            max_solutions_per_cycle=10,
            solution_approaches=["analytical", "empirical", "creative", "hybrid"],
            quality_threshold=0.5,
        )
        cfg.world_model_p6 = WorldModelConfig(
            model_types=["scientific", "economic", "social", "technological", "political"],
            max_models=50,
            simulation_depth=1000,
            enable_prediction=True,
            enable_intervention_planning=True,
        )
        cfg.knowledge_fabric = KnowledgeFabricConfig(
            node_types=["concept", "theory", "process", "system", "organization",
                       "technology", "person", "tool", "method"],
            max_nodes=50000,
            embedding_dimension=256,
            enable_cross_domain_links=True,
        )
        return cfg

    @staticmethod
    def phase_7_agi() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_6_gri()
        cfg.phase = 7
        cfg.version = "0.7.0"
        cfg.budget = BudgetConfig(B_cycle=1e38, B_life=1e42, T_cycle_hours=336.0)
        cfg.layers_enabled["L15"] = True
        cfg.layers_enabled["L16"] = True
        cfg.layers_enabled["L17"] = True

        cfg.unified_cognitive_core = UnifiedCognitiveCoreConfig(
            attention_capacity=7,
            reasoning_modes_integrated=[
                "deduction", "induction", "abduction", "causal", "counterfactual",
                "analogical", "game_theoretic", "strategic", "legal", "economic"
            ],
            shared_attention=True, shared_memory=True,
            shared_goals=True, trace_merging=True,
        )
        cfg.lifelong_memory = LifelongMemoryConfig(
            max_episodes=1000000,
            consolidation_interval_cycles=100,
            enable_consolidation=True, enable_forgetting=True,
        )
        cfg.autonomous_research_director = AutonomousResearchDirectorConfig(
            max_active_projects=1000,
            max_experiments=100000,
            resource_allocation_strategy="adaptive",
            risk_tolerance=0.3,
        )
        cfg.unified_world_model_p7 = UnifiedWorldModelConfig(
            domains=["physics", "biology", "economics", "society", "technology", "politics"],
            enable_prediction=True, enable_simulation=True,
            enable_intervention_planning=True, enable_scenario_generation=True,
        )
        cfg.tool_creation_engine = ToolCreationEngineConfig(
            tool_types=["simulator", "algorithm", "analyzer", "compiler", "research_system"],
            max_tools_per_cycle=3,
            enable_testing=True,
        )
        cfg.human_collaboration = HumanCollaborationConfig(
            enable_teaching=True, enable_debating=True, enable_explaining=True,
            enable_mentoring=True, enable_teamwork=True,
        )
        cfg.creativity_engine = CreativityEngineConfig(
            domains=["science", "math", "engineering", "software", "strategy"],
            novelty_weight=0.4, utility_weight=0.3, impact_weight=0.3,
        )
        cfg.autonomous_agency = AutonomousAgencyConfig(
            enable_goal_generation=True, enable_prioritization=True,
            enable_self_directed_planning=True,
            max_active_goals=20,
        )
        cfg.self_evaluation = SelfEvaluationConfig(
            enable_capability_mapping=True, enable_performance_tracking=True,
            enable_weakness_detection=True,
            calibration_target=0.9,
        )
        cfg.grand_challenge_engine = GrandChallengeEngineConfig(
            challenges=["cancer", "climate", "fusion", "materials", "ai_safety", "longevity"],
            planning_horizon_years=10,
            enable_massive_orchestration=True,
            enable_cross_domain_collaboration=True,
        )
        return cfg

    @staticmethod
    def phase_8_agi() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_7_agi()
        cfg.phase = 8
        cfg.version = "0.8.0"
        cfg.budget = BudgetConfig(B_cycle=1e40, B_life=1e45, T_cycle_hours=720.0)
        cfg.layers_enabled["L18"] = True
        cfg.layers_enabled["L19"] = True
        cfg.layers_enabled["L20"] = True

        cfg.open_world_learning = OpenWorldLearningConfig(
            enable_autonomous_learning=True, enable_knowledge_updating=True,
            enable_contradiction_detection=True, enable_belief_revision=True,
        )
        cfg.global_memory = GlobalMemoryConfig(
            enable_compression=True, enable_abstraction=True,
            compression_target_ratio=0.3, max_entries=10000000,
        )
        cfg.executive_intelligence = ExecutiveIntelligenceConfig(
            max_active_goals=10000, enable_goal_selection=True,
            enable_priority_control=True, enable_resource_allocation=True,
            enable_risk_analysis=True,
        )
        cfg.organization_builder = OrganizationBuilderConfig(
            max_agents=10000, enable_recruitment=True,
            enable_specialization=True, enable_training=True,
        )
        cfg.cognitive_evolution = CognitiveEvolutionConfig(
            enable_architecture_invention=True, enable_reasoning_invention=True,
            enable_learning_invention=True,
        )
        cfg.real_world_action = RealWorldActionConfig(
            enable_execution=True, enable_monitoring=True,
            enable_recovery=True, enable_adaptation=True,
        )
        cfg.tool_ecosystem = ToolEcosystemConfig(
            enable_creation=True, enable_evaluation=True, enable_retirement=True,
        )
        cfg.civilization_simulator = CivilizationSimulatorConfig(
            enable_forecasting=True, enable_policy_evaluation=True,
            enable_scenario_generation=True,
        )
        cfg.autonomous_mission = AutonomousMissionConfig(
            enable_mission_generation=True, enable_program_decomposition=True,
            enable_long_term_execution=True,
        )
        cfg.intelligence_evaluator = IntelligenceEvaluatorConfig(
            improvement_tracking=True,
        )
        return cfg

    @staticmethod
    def phase_9_sri() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_8_agi()
        cfg.phase = 9
        cfg.version = "0.9.0"
        cfg.budget = BudgetConfig(B_cycle=1e45, B_life=1e50, T_cycle_hours=168.0)
        cfg.layers_enabled["L21"] = True
        cfg.layers_enabled["L22"] = True
        cfg.layers_enabled["L23"] = True

        cfg.planet_scale_discovery = PlanetScaleDiscoveryConfig(
            enable_massive_parallel=True, target_agents=1_000_000,
            domains=["science", "engineering", "medicine", "economics", "mathematics", "technology"],
            hypotheses_per_agent=5, experiments_per_agent=3,
        )
        cfg.autonomous_field_creation = AutonomousFieldCreationConfig(
            enable_field_creation=True, min_maturity_for_completion=0.8,
        )
        cfg.discovery_acceleration = DiscoveryAccelerationConfig(
            enable_pipeline=True, target_speedup=10.0, max_active_pipelines=100,
        )
        cfg.global_knowledge_civilization = GlobalKnowledgeCivilizationConfig(
            enable_knowledge_integration=True, max_knowledge_objects=10_000_000,
            enable_conflict_resolution=True, enable_synthesis=True,
        )
        cfg.autonomous_institutions = AutonomousInstitutionsConfig(
            enable_institutions=True, max_institutions=1000,
            enable_proposal_review=True, enable_resource_allocation=True,
        )
        cfg.paradigm_shift_generator = ParadigmShiftGeneratorConfig(
            enable_shift_generation=True, min_limitations_for_shift=3,
            adoption_threshold=0.7,
        )
        cfg.recursive_tool_civilization = RecursiveToolCivilizationConfig(
            enable_recursive_tools=True, max_recursion_depth=3, max_tools=10000,
        )
        cfg.grand_discovery_programs = GrandDiscoveryProgramsConfig(
            programs=["cancer", "fusion", "climate", "longevity", "quantum_computing",
                      "ai_safety", "materials_discovery"],
            enable_massive_experimentation=True, experiments_per_program=10000,
        )
        cfg.meta_civilization_intelligence = MetaCivilizationIntelligenceConfig(
            enable_civilization_modeling=True, enable_recommendation=True,
        )
        cfg.superintelligence_governance = SuperintelligenceGovernanceConfig(
            enable_governance=True, enable_rollback=True,
            enable_automatic_pause=True, enable_capability_monitoring=True,
        )
        return cfg

    @staticmethod
    def phase_10_ssf() -> "TheoriaConfig":
        cfg = TheoriaConfig.phase_9_sri()
        cfg.phase = 10
        cfg.version = "1.0.0"
        cfg.budget = BudgetConfig(B_cycle=1e50, B_life=1e55, T_cycle_hours=84.0)
        cfg.layers_enabled["L24"] = True
        cfg.layers_enabled["L25"] = True
        cfg.layers_enabled["L26"] = True

        cfg.knowledge_evolution = KnowledgeEvolutionConfig(
            enable_evolution=True, mutation_rate=0.1, fitness_threshold=0.6,
        )
        cfg.recursive_discovery = RecursiveDiscoveryConfig(
            enable_recursive_discovery=True, max_recursion_depth=5,
            discoverers_per_cycle=3, enable_self_improvement=True,
        )
        cfg.knowledge_fabric2 = KnowledgeFabric2Config(
            enable_fabric=True, integration_threshold=0.7, max_nodes=100000,
        )
        cfg.discovery_ecology = DiscoveryEcologyConfig(
            enable_ecology=True, enable_independent_evolution=True,
        )
        cfg.meta_knowledge = MetaKnowledgeConfig(
            enable_meta_knowledge=True, enable_hypothesis_testing=True,
        )
        cfg.civilization_memory = CivilizationMemoryConfig(
            enable_memory=True, max_records=10_000_000,
            enable_importance_weighting=True,
        )
        cfg.civilization_governance = CivilizationGovernanceConfig(
            enable_governance=True, stability_target=0.95,
            alignment_target=0.98, enable_risk_management=True,
            enable_automatic_intervention=True,
        )
        cfg.discovery_forecasting = DiscoveryForecastingConfig(
            enable_forecasting=True, forecast_horizon_days=365,
            enable_accuracy_tracking=True,
        )
        cfg.universal_problem_network = UniversalProblemNetworkConfig(
            enable_network=True, enable_cross_connection=True,
            enable_solution_tracking=True,
        )
        cfg.singularity_coordination = SingularityCoordinationConfig(
            enable_coordination=True, enable_self_sustaining=True,
            enable_continuous_improvement=True,
        )
        return cfg
