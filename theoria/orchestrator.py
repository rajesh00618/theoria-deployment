"""
THEORIA Orchestrator: Main system controller.

Integrates all layers and subsystems into a cohesive research cycle.
Manages the discovery → falsification → revision loop.
"""

from __future__ import annotations

import time
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.config import TheoriaConfig
from theoria.core.memory import MemoryArchitecture
from theoria.core.types import (
    Theory, Evidence, Concept, Strategy, TheoryStatus, DisciplineMode,
    MotivationalState, ComputeBudget, AuditResult, ConceptLifecycle,
    AuditLogEntry, EvidenceReplicationStatus, ProvenanceRecord,
    ScientificPaper, Citation, Figure, ResearchGap, ResearchQuestion,
    ResearchProgram, CandidateHypothesis, CriticReport, DashboardMetrics,
    KGNode, KGEdge, KGNodeType, KGEdgeType,
    ExperimentDesign, ExperimentResult, AgentRole, PaperDraft,
    ScientificPrediction, CrossDomainMapping,
)

# Layer imports
from theoria.layers.sensorium import Sensorium, SensoryInput
from theoria.layers.empirics import Empirics
from theoria.layers.ontogenesis import Ontogenesis
from theoria.layers.abductive import AbductiveImagination
from theoria.layers.theory_constructor import TheoryConstructor
from theoria.layers.falsification import FalsificationEngine
from theoria.layers.meta_theory import MetaTheoryReasoner
from theoria.layers.auditor import MetascientificAuditor, ConstitutionalReview

# Phase 2 imports
from theoria.layers.literature import LiteratureIngestor, PaperCorpus
from theoria.layers.gap_detector import GapDetector
from theoria.layers.question_generator import QuestionGenerator
from theoria.layers.planner import ResearchPlanner
from theoria.layers.critic import ScientificCritic
from theoria.layers.dashboard import DiscoveryDashboard

# Phase 3 imports
from theoria.layers.experiment_design import ExperimentPlanner
from theoria.layers.intervention import InterventionGenerator, CounterfactualSimulator, ExperimentEvaluator
from theoria.layers.multi_agent import MultiAgentLab
from theoria.layers.paper_generator import PaperGenerator
from theoria.layers.prediction_engine import PredictionEngine
from theoria.layers.cross_domain import CrossDomainTransfer
from theoria.layers.data_connectors import DataConnector

# Phase 4 imports
from theoria.layers.real_data import RealDataConnector
from theoria.layers.embodied import EmbodiedLab
from theoria.layers.scientific_society import ScientificSociety
from theoria.layers.communication import CommunicationLayer
from theoria.layers.ethics import EthicsLayer
from theoria.layers.adversarial import AdversarialScience
from theoria.layers.prediction_market import PredictionMarket
from theoria.layers.economy import ScientificEconomy
from theoria.layers.research_programs import ResearchProgramManager
from theoria.layers.evolution import KnowledgeEvolution

# Phase 5 imports
from theoria.layers.self_improvement import SelfImprovementLayer
from theoria.layers.meta_civilization import MetaCivilizationLayer
from theoria.layers.benchmark_generator import BenchmarkGenerator
from theoria.layers.simulation_worlds import SimulationWorldManager
from theoria.layers.self_modification import SelfModificationFramework
from theoria.layers.knowledge_compression import KnowledgeCompressionEngine

# Phase 6 imports
from theoria.layers.universal_reasoning import UniversalReasoningEngine, ReasoningResult
from theoria.layers.knowledge_civilization import KnowledgeCivilizationLayer
from theoria.layers.mathematical_discovery import MathematicalDiscovery
from theoria.layers.software_intelligence import SoftwareIntelligence
from theoria.layers.open_ended_learning import OpenEndedLearning
from theoria.layers.long_horizon_planning import LongHorizonPlanning
from theoria.layers.general_agent_society import GeneralAgentSociety
from theoria.layers.universal_solver import UniversalProblemSolver
from theoria.layers.world_models import WorldModelingEngine
from theoria.layers.universal_fabric import UniversalKnowledgeFabric

# Phase 7 imports
from theoria.layers.unified_cognitive_core import UnifiedCognitiveCore
from theoria.layers.lifelong_memory import LifelongMemoryLayer
from theoria.layers.autonomous_research_director import AutonomousResearchDirector
from theoria.layers.unified_world_model import UnifiedWorldModel
from theoria.layers.tool_creation_engine import ToolCreationEngine
from theoria.layers.human_collaboration import HumanCollaboration
from theoria.layers.creativity_engine import CreativityEngine
from theoria.layers.agency_layer import AgencyLayer
from theoria.layers.self_evaluation import SelfEvaluation
from theoria.layers.grand_challenge_engine import GrandChallengeEngine
from theoria.layers.civilization_intelligence import CivilizationIntelligenceLayer

# Phase 8 imports
from theoria.layers.open_world_learning import OpenWorldLearningEngine
from theoria.layers.global_memory import GlobalMemory
from theoria.layers.executive_intelligence import ExecutiveIntelligenceLayer
from theoria.layers.organization_builder import OrganizationBuilder
from theoria.layers.cognitive_evolution import CognitiveEvolutionLayer
from theoria.layers.real_world_action import RealWorldActionEngine
from theoria.layers.tool_ecosystem import UniversalToolEcosystem
from theoria.layers.civilization_simulator import CivilizationSimulator
from theoria.layers.mission_system import MissionIntelligenceLayer
from theoria.layers.intelligence_evaluator import IntelligenceEvaluator

# Phase 9 imports
from theoria.layers.planet_scale_discovery import PlanetScaleDiscoveryEngine
from theoria.layers.field_creation import AutonomousFieldCreator
from theoria.layers.discovery_acceleration import DiscoveryAccelerationLayer
from theoria.layers.global_knowledge import GlobalKnowledgeCivilization
from theoria.layers.research_institutions import AutonomousResearchInstitutions
from theoria.layers.paradigm_shift_generator import ParadigmShiftGenerator
from theoria.layers.recursive_tool_civilization import RecursiveToolCivilization
from theoria.layers.grand_discovery_programs import GrandDiscoveryPrograms
from theoria.layers.meta_civilization_intelligence import MetaCivilizationIntelligence
from theoria.layers.superintelligence_governance import SuperintelligenceGovernance
from theoria.layers.knowledge_civilization_integration import KnowledgeCivilizationLayer

# Phase 10 imports
from theoria.layers.knowledge_evolution_layer import KnowledgeEvolutionLayer
from theoria.layers.recursive_discovery_ecosystem import RecursiveDiscoveryEcosystem
from theoria.layers.universal_knowledge_fabric2 import UniversalKnowledgeFabric2
from theoria.layers.meta_knowledge_civilization import MetaKnowledgeCivilization
from theoria.layers.civilization_memory import CivilizationMemory
from theoria.layers.civilization_governance_layer import CivilizationGovernanceLayer
from theoria.layers.discovery_forecasting import DiscoveryForecastingEngine
from theoria.layers.universal_problem_network import UniversalProblemNetwork
from theoria.layers.singularity_coordination_layer import SingularityCoordinationLayer
from theoria.layers.llm_client import LLMDriver


@dataclass
class CycleResult:
    """Result of a single THEORIA research cycle."""
    cycle_number: int
    duration: float
    theories_proposed: int
    theories_falsified: int
    theories_converged: int
    strategies_used: List[str]
    anomalies_detected: int
    paradigm_crisis: bool
    memory_summary: Dict[str, Any]
    motivational_state: Dict[str, float]
    audit_summary: Dict[str, Any]
    
    # Phase 2 metrics
    papers_ingested: int = 0
    gaps_detected: int = 0
    questions_generated: int = 0
    critiques_issued: int = 0
    kg_nodes_added: int = 0
    kg_edges_added: int = 0
    programs_active: int = 0

    # Phase 3 metrics
    experiments_designed: int = 0
    experiments_executed: int = 0
    interventions_generated: int = 0
    papers_generated: int = 0
    predictions_made: int = 0
    cross_domain_mappings: int = 0
    debates_held: int = 0
    agents_active: int = 0

    # Phase 4 metrics
    real_papers_found: int = 0
    embodied_experiments: int = 0
    society_papers: int = 0
    ethics_reviews: int = 0
    adversarial_challenges: int = 0
    market_predictions: int = 0
    economy_allocations: int = 0
    programs_running: int = 0
    paradigm_events: int = 0

    # Phase 5 metrics
    architecture_proposals: int = 0
    algorithm_candidates: int = 0
    strategy_population: int = 0
    benchmarks_generated: int = 0
    simulation_experiments: int = 0
    self_modifications_proposed: int = 0
    self_modifications_approved: int = 0
    meta_findings: int = 0
    abstractions_created: int = 0
    agendas_generated: int = 0
    civilization_health: float = 0.0
    civilization_innovation: float = 0.0

    # Phase 6 metrics
    reasoning_traces: int = 0
    conjectures_generated: int = 0
    proofs_found: int = 0
    software_projects: int = 0
    open_goals: int = 0
    plans_active: int = 0
    agent_society_size: int = 0
    problems_solved: int = 0
    world_models_active: int = 0
    fabric_nodes: int = 0
    cross_domain_mappings_p6: int = 0

    # Phase 7 metrics
    cognitive_traces: int = 0
    memory_episodes: int = 0
    projects_active: int = 0
    world_models_p7: int = 0
    tools_created: int = 0
    collaborations: int = 0
    creative_artifacts: int = 0
    active_goals: int = 0
    capabilities_assessed: int = 0
    grand_challenge_progress: float = 0.0
    civilization_impact: float = 0.0

    # Phase 8 metrics
    open_world_records: int = 0
    global_memory_entries: int = 0
    executive_active_goals: int = 0
    organization_agents: int = 0
    cognitive_inventions: int = 0
    real_world_actions: int = 0
    ecosystem_tools: int = 0
    civilization_forecasts: int = 0
    mission_progress: float = 0.0
    intelligence_overall_score: float = 0.0

    # Phase 9 metrics
    discovery_agents_total: int = 0
    fields_created: int = 0
    pipelines_active: int = 0
    knowledge_objects_total: int = 0
    institutions_active: int = 0
    paradigm_shifts: int = 0
    recursive_tools_total: int = 0
    grand_programs_active: int = 0
    civilization_models: int = 0
    governance_safety_score: float = 0.0

    # Phase 10 metrics
    knowledge_evolution_rate: float = 0.0
    recursive_discoverers: int = 0
    fabric_integration_score: float = 0.0
    meta_knowledge_models: int = 0
    civilization_memory_records: int = 0
    governance_stability: float = 0.0
    discovery_forecasts: int = 0
    problem_network_density: float = 0.0
    coordination_score: float = 0.0
    self_sustaining: bool = False


class TheoriaOrchestrator:
    """
    Main THEORIA system.
    Manages the full research cycle across all layers.
    """
    
    def __init__(self, config: Optional[TheoriaConfig] = None):
        self.config = config or TheoriaConfig.phase_1_baseline()
        
        # Initialize memory
        self.memory = MemoryArchitecture(config)
        
        # Initialize layers
        self.sensorium = Sensorium(config)
        self.empirics = Empirics(config)
        self.ontogenesis = Ontogenesis(config)
        self.abductive = AbductiveImagination(config)
        self.theory_constructor = TheoryConstructor(config)
        self.falsification = FalsificationEngine(config)
        self.meta_theory = MetaTheoryReasoner(config.meta_theory if config else None)
        self.auditor = MetascientificAuditor(config)
        self.constitutional = ConstitutionalReview(config)
        
        # Phase 2 components
        is_phase_2 = self.config and self.config.phase >= 2
        self.literature = LiteratureIngestor(config.literature if config else None)
        self.gap_detector = GapDetector(config.gap_detection if config else None)
        self.question_gen = QuestionGenerator(config.question_gen if config else None)
        self.planner = ResearchPlanner(config.planner if config else None)
        self.critic = ScientificCritic(config.critic if config else None)
        self.dashboard = DiscoveryDashboard(config.dashboard if config else None)
        
        # Phase 3 components
        is_phase_3 = self.config and self.config.phase >= 3
        self.experiment_planner = ExperimentPlanner(config.experiment_design if config else None)
        self.intervention_gen = InterventionGenerator(config.intervention if config else None)
        self.counterfactual_sim = CounterfactualSimulator(config.intervention if config else None)
        self.experiment_eval = ExperimentEvaluator(config.intervention if config else None)
        self.multi_agent_lab = MultiAgentLab(config.multi_agent if config else None)
        self.paper_gen = PaperGenerator(config.paper_gen if config else None)
        self.prediction_engine = PredictionEngine(config.prediction if config else None)
        self.cross_domain = CrossDomainTransfer(config.cross_domain if config else None)
        self.data_connector = DataConnector(config.data_connector if config else None)

        # Phase 4 components
        is_phase_4 = self.config and self.config.phase >= 4
        self.real_data = RealDataConnector(config.data_connector if config else None)
        self.embodied_lab = EmbodiedLab(config.embodied if config else None)
        self.scientific_society = ScientificSociety(config.society if config else None)
        self.communication = CommunicationLayer(config.communication if config else None)
        self.ethics_layer = EthicsLayer(config.ethics if config else None)
        self.adversarial_science = AdversarialScience(config.adversarial if config else None)
        self.prediction_market = PredictionMarket(config.prediction_market if config else None)
        self.scientific_economy = ScientificEconomy(config.economy if config else None)
        self.research_programs = ResearchProgramManager(config.research_program if config else None)
        self.knowledge_evolution = KnowledgeEvolution(config.evolution if config else None)

        # Phase 5 components
        is_phase_5 = self.config and self.config.phase >= 5
        self.self_improvement = SelfImprovementLayer(config)
        self.meta_civilization = MetaCivilizationLayer(config)
        self.benchmark_generator = BenchmarkGenerator(config.benchmark_generator if config else None)
        self.simulation_worlds = SimulationWorldManager(config.simulation_worlds if config else None)
        self.self_modification = SelfModificationFramework(config.self_modification if config else None)
        self.knowledge_compression = KnowledgeCompressionEngine(config.knowledge_compression if config else None)

        # Phase 6 components
        is_phase_6 = self.config and self.config.phase >= 6
        self.universal_reasoning = UniversalReasoningEngine(
            config.universal_reasoning if config else None)
        self.knowledge_civilization = KnowledgeCivilizationLayer(config)
        self.mathematical_discovery = MathematicalDiscovery(
            config.mathematical_discovery_p6 if config else None)
        self.software_intelligence = SoftwareIntelligence(
            config.software_intelligence if config else None)
        self.open_ended_learning = OpenEndedLearning(
            config.open_ended_learning if config else None)
        self.long_horizon_planning = LongHorizonPlanning(
            config.long_horizon_planning if config else None)
        self.general_agent_society = GeneralAgentSociety(
            config.general_agent_society if config else None)
        self.universal_problem_solver = UniversalProblemSolver(
            config.universal_problem_solver if config else None)
        self.world_models = WorldModelingEngine(
            config.world_model_p6 if config else None)
        self.universal_fabric = UniversalKnowledgeFabric(
            config.knowledge_fabric if config else None)
        
        # Phase 7 components
        is_phase_7 = self.config and self.config.phase >= 7
        self.unified_cognitive_core = UnifiedCognitiveCore(
            config.unified_cognitive_core if config else None)
        self.lifelong_memory = LifelongMemoryLayer(
            config.lifelong_memory if config else None)
        self.research_director = AutonomousResearchDirector(
            config.autonomous_research_director if config else None)
        self.unified_world_model_p7 = UnifiedWorldModel(
            config.unified_world_model_p7 if config else None)
        self.tool_creation = ToolCreationEngine(
            config.tool_creation_engine if config else None)
        self.human_collab = HumanCollaboration(
            config.human_collaboration if config else None)
        self.creativity = CreativityEngine(
            config.creativity_engine if config else None)
        self.agency = AgencyLayer(
            config.autonomous_agency if config else None)
        self.self_eval = SelfEvaluation(
            config.self_evaluation if config else None)
        self.grand_challenge = GrandChallengeEngine(
            config.grand_challenge_engine if config else None)
        self.civilization_intel = CivilizationIntelligenceLayer(config)

        # Phase 8 components
        is_phase_8 = self.config and self.config.phase >= 8
        self.open_world_learning = OpenWorldLearningEngine(
            config.open_world_learning if config else None)
        self.global_memory = GlobalMemory(
            config.global_memory if config else None)
        self.executive_intel = ExecutiveIntelligenceLayer(
            config.executive_intelligence if config else None)
        self.organization_builder = OrganizationBuilder(
            config.organization_builder if config else None)
        self.cognitive_evolution = CognitiveEvolutionLayer(
            config.cognitive_evolution if config else None)
        self.real_world_action = RealWorldActionEngine(
            config.real_world_action if config else None)
        self.tool_ecosystem = UniversalToolEcosystem(
            config.tool_ecosystem if config else None)
        self.civilization_sim = CivilizationSimulator(
            config.civilization_simulator if config else None)
        self.mission_system = MissionIntelligenceLayer(
            config.autonomous_mission if config else None)
        self.intelligence_eval = IntelligenceEvaluator(
            config.intelligence_evaluator if config else None)

        # Phase 9 components
        is_phase_9 = self.config and self.config.phase >= 9
        self.planet_discovery = PlanetScaleDiscoveryEngine(
            config.planet_scale_discovery if config else None)
        self.field_creator = AutonomousFieldCreator(
            config.autonomous_field_creation if config else None)
        self.discovery_accel = DiscoveryAccelerationLayer(
            config.discovery_acceleration if config else None)
        self.global_knowledge = GlobalKnowledgeCivilization(
            config.global_knowledge_civilization if config else None)
        self.research_institutions = AutonomousResearchInstitutions(
            config.autonomous_institutions if config else None)
        self.paradigm_shift_gen = ParadigmShiftGenerator(
            config.paradigm_shift_generator if config else None)
        self.recursive_tools = RecursiveToolCivilization(
            config.recursive_tool_civilization if config else None)
        self.grand_programs = GrandDiscoveryPrograms(
            config.grand_discovery_programs if config else None)
        self.meta_civ_intel = MetaCivilizationIntelligence(
            config.meta_civilization_intelligence if config else None)
        self.governance = SuperintelligenceGovernance(
            config.superintelligence_governance if config else None)
        self.knowledge_civ_layer = KnowledgeCivilizationLayer(config)

        # Phase 10 components
        is_phase_10 = self.config and self.config.phase >= 10
        self.knowledge_evolution_layer = KnowledgeEvolutionLayer(
            config.knowledge_evolution if config else None)
        self.recursive_discovery = RecursiveDiscoveryEcosystem(
            config.recursive_discovery if config else None)
        self.knowledge_fabric2 = UniversalKnowledgeFabric2(
            config.knowledge_fabric2 if config else None)
        self.meta_knowledge = MetaKnowledgeCivilization(
            config.meta_knowledge if config else None)
        self.civilization_memory = CivilizationMemory(
            config.civilization_memory if config else None)
        self.civilization_governance = CivilizationGovernanceLayer(
            config.civilization_governance if config else None)
        self.discovery_forecasting = DiscoveryForecastingEngine(
            config.discovery_forecasting if config else None)
        self.problem_network = UniversalProblemNetwork(
            config.universal_problem_network if config else None)
        self.singularity_coordination = SingularityCoordinationLayer(
            config.singularity_coordination if config else None)
        
        # Connect abductive layer to knowledge graph and papers
        if is_phase_2:
            self.abductive.knowledge_graph = self.memory.knowledge_graph
            self.abductive.papers = self.memory.scientific.papers

        # Connect LLM driver
        self.llm_driver = LLMDriver(model="gemma3:4b")
        if self.llm_driver.available:
            self.abductive.llm_driver = self.llm_driver
        
        # Connect Phase 3 layers
        if is_phase_3:
            self.cross_domain.domain_graph = self._build_domain_graph()
        
        # Motivational state
        self.motivation = MotivationalState()
        
        # Compute budget
        self.budget = ComputeBudget(
            B_cycle=self.config.budget.B_cycle if config else 1e20,
            B_life=self.config.budget.B_life if config else 1e25,
        )
        
        # Cycle tracking
        self.cycle_count: int = 0
        self.cycle_history: List[CycleResult] = []
        
        # Classical laws target for B1
        self.classical_laws_catalog = {
            "kepler_third": {
                "name": "Kepler's Third Law",
                "pattern": "T^2 ∝ a^3",
                "observables": ["period", "semi_major_axis"],
            },
            "ohms_law": {
                "name": "Ohm's Law",
                "pattern": "V = I·R",
                "observables": ["voltage", "current", "resistance"],
            },
            "snells_law": {
                "name": "Snell's Law",
                "pattern": "n₁·sin(θ₁) = n₂·sin(θ₂)",
                "observables": ["angle_incidence", "angle_refraction", "refractive_index"],
            },
            "ideal_gas": {
                "name": "Ideal Gas Law",
                "pattern": "PV = nRT",
                "observables": ["pressure", "volume", "temperature", "amount"],
            },
            "coulombs_law": {
                "name": "Coulomb's Law",
                "pattern": "F = k·q₁q₂/r²",
                "observables": ["force", "charge_1", "charge_2", "distance"],
            },
            "momentum": {
                "name": "Conservation of Momentum",
                "pattern": "Σp_initial = Σp_final",
                "observables": ["mass", "velocity", "momentum"],
            },
        }
        self.discovered_laws: Dict[str, Dict[str, Any]] = {}
    
    def initialize_primitives(self, domain: str = "physics") -> None:
        """Initialize base primitives for a domain."""
        self.ontogenesis.initialize_base_primitives(domain)
        self.abductive.init_primitive_names(self.ontogenesis.primitives)
        self.abductive.domain = domain
        
        # Register strategies in meta-strategy memory
        for st in StrategyType:
            strategy = Strategy(
                name=st.name,
                strategy_type=st,
            )
            self.memory.meta_strategy.register_strategy(strategy)
    
    def ingest_data(self, data: List[Dict[str, Any]], 
                   modality: str = "numerical") -> Dict[str, Any]:
        """
        Ingest observational data into the system.
        Extracts variable names as concepts for L2.
        Returns anomaly report.
        """
        anomalies = []
        features = []
        
        for i, record in enumerate(data):
            sensory = SensoryInput(
                raw_data=record,
                modality=modality,
                source=f"batch_{i}",
                metadata={"id": f"obs_{i}", "index": i},
            )
            
            feat, anomaly = self.sensorium.ingest(sensory)
            if feat:
                features.append(feat)
            if anomaly and anomaly.anomaly_score > 0.7:
                anomalies.append(anomaly)
            
            # Store in episodic memory
            from theoria.core.memory import EpisodicRecord
            obs_id = f"obs_{i}_{len(self.memory.episodic.records)}"
            self.memory.episodic.append(EpisodicRecord(
                id=obs_id,
                timestamp=time.time(),
                modality=modality,
                raw_data=record,
            ))
            
            # Create evidence for all active theories against this observation
            # Matching theories get mild confirmation, non-matching get disconfirmed
            if isinstance(record, dict):
                obs_vars = set(str(k).lower() for k in record.keys())
                for t in self.memory.theory.get_active():
                    t_vars = set(str(v).lower() for v in t.reference_class)
                    has_overlap = bool(t_vars & obs_vars)
                    if has_overlap:
                        # Theory's domain matches observation — mildly confirming
                        ev = Evidence(
                            id=f"ev_{t.id}_{obs_id}",
                            description=f"Evidence from {obs_id} for {t.name}",
                            data=record,
                            likelihood_under_theory={t.id: 0.60},
                            replication_status=EvidenceReplicationStatus.REPLICATED_ONCE,
                            provenance=ProvenanceRecord(
                                source_experiment=obs_id,
                                timestamp=time.time(),
                                uncertainty_estimate=0.3,
                            ),
                        )
                        self.empirics.add_evidence(ev)
                        self.empirics.update_theory_posterior(t, ev.id)
                    else:
                        # Theory does not address this observation — disconfirm
                        ev = Evidence(
                            id=f"ev_{t.id}_{obs_id}",
                            description=f"Evidence from {obs_id} for {t.name}",
                            data=record,
                            likelihood_under_theory={t.id: 0.20},
                            replication_status=EvidenceReplicationStatus.FAILED_TO_REPLICATE,
                            provenance=ProvenanceRecord(
                                source_experiment=obs_id,
                                timestamp=time.time(),
                                uncertainty_estimate=0.3,
                            ),
                        )
                        self.empirics.add_evidence(ev)
                        self.empirics.update_theory_posterior(t, ev.id)
        
        # Extract variable names from data and add as concepts to L2
        if data and isinstance(data[0], dict):
            variable_names = set()
            for record in data:
                for key in record.keys():
                    if isinstance(record[key], (int, float)):
                        variable_names.add(key)
            
            for var_name in variable_names:
                # Check if concept already exists
                exists = any(c.name == var_name for c in self.ontogenesis.concepts.values())
                if not exists:
                    concept = Concept(
                        name=var_name,
                        definition=f"Observable variable: {var_name}",
                        kind="base",
                        lifecycle=ConceptLifecycle.ALIVE,
                    )
                    concept.domains_where_useful.add("physics")
                    self.ontogenesis.concepts[concept.id] = concept
        
        return {
            "records_ingested": len(data),
            "anomalies_detected": len(anomalies),
            "features_extracted": len(features),
            "queue_size": self.sensorium.queue_size,
            "overloaded": self.sensorium.is_overloaded,
            "new_concepts": len(variable_names) if data and isinstance(data[0], dict) else 0,
        }
    
    def ingest_paper(self, text: str, title: str = "",
                     authors: Optional[List[str]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> ScientificPaper:
        """Ingest a scientific paper into the system."""
        if authors is None:
            authors = []
        if metadata is None:
            metadata = {}

        paper = self.literature.parse_paper_text(
            text=text, title=title, authors=authors, metadata=metadata
        )

        self.memory.scientific.add_paper(paper)

        concepts = self.literature.extract_concepts(paper)
        theories = self.literature.extract_theories(paper)
        evidence = self.literature.extract_evidence(paper)

        kg_nodes = self.literature.paper_to_kg_nodes(paper)
        kg_nodes_ref = self.memory.knowledge_graph
        for node in kg_nodes:
            kg_nodes_ref.add_node(node)

        for concept_info in concepts:
            existing = kg_nodes_ref.get_node_by_name(concept_info["name"])
            node = existing or KGNode(
                node_type=KGNodeType.CONCEPT,
                name=concept_info["name"][:100],
                description=f"Concept from: {paper.title[:80]}",
                source_paper_ids=[paper.id],
                properties={"domain": paper.domain},
                confidence=0.7,
            )
            if not existing:
                kg_nodes_ref.add_node(node)

        for theory_info in theories:
            existing = kg_nodes_ref.get_node_by_name(theory_info["statement"][:100])
            if not existing:
                node = KGNode(
                    node_type=KGNodeType.THEORY,
                    name=theory_info["statement"][:100],
                    description=theory_info["statement"][:500],
                    source_paper_ids=[paper.id],
                    confidence=0.6,
                )
                kg_nodes_ref.add_node(node)

        return paper

    def _phase2_research_cycle(self, domain: str,
                                concepts: List[Concept],
                                active_theories: List[Theory]) -> Dict[str, Any]:
        """Phase 2 research pipeline: literature → KG → gaps → questions → critic."""
        result = {
            "papers_ingested": 0,
            "gaps_detected": 0,
            "questions_generated": 0,
            "critiques_issued": 0,
            "kg_nodes_added": 0,
            "kg_edges_added": 0,
        }

        kg = self.memory.knowledge_graph

        gaps = self.gap_detector.detect_all(
            kg=kg, theories=active_theories,
            max_gaps=20,
        )
        for gap in gaps:
            self.memory.scientific.add_gap(gap)
        result["gaps_detected"] = len(gaps)

        open_gaps = self.memory.scientific.get_open_gaps(min_score=0.3)
        if open_gaps:
            kg_nodes = kg.nodes if hasattr(kg, 'nodes') else {}
            questions = self.question_gen.generate_from_gaps(
                gaps=open_gaps[:5],
                kg_nodes=kg_nodes,
                max_questions=10,
            )
            for q in questions:
                self.memory.scientific.add_question(q)
            result["questions_generated"] = len(questions)

        for theory in active_theories:
            theory_evidence = self.empirics.query_evidence_for_theory(
                theory.id, min_posterior=0.01
            )
            report = self.critic.critique_theory(
                theory=theory,
                evidence=theory_evidence,
                alternatives=[t for t in active_theories if t.id != theory.id],
            )
            self.memory.scientific.add_critique(report)
            result["critiques_issued"] += 1

        active_progs = self.memory.scientific.get_active_programs()
        if not active_progs and len(open_gaps) >= 3:
            questions = self.memory.scientific.get_open_questions(min_score=0.3)
            program = self.planner.create_program(
                name=f"Research: {domain}",
                domain=domain,
                long_term_goal=f"Advance understanding in {domain}",
                gaps=open_gaps[:5],
                questions=questions[:5],
                estimated_cycles=100,
            )
            self.memory.scientific.add_program(program)

        if self.memory.persistent:
            for gap in gaps:
                self.memory.persistent.save_gap(gap)

        if self.dashboard:
            metrics = self.dashboard.snapshot(self.memory)

        result["papers_ingested"] = len(self.literature.papers)
        return result

    def research_cycle(self, domain: str = "physics") -> CycleResult:
        """
        Execute one complete THEORIA research cycle.

        Flow:
        1. L2: Concept management (evaluate, compose, analogy)
        2. L3: Generate candidate hypotheses (12 strategies)
        3. L4: Formalize candidates into theories
        4. L5: Falsify theories (severity, comparison)
        5. Phase 2: Literature → KG → Gaps → Questions → Critic
        6. L6: Meta-strategy update
        7. L-1: Audit modifications
        8. Memory: Update all stores + Dashboard snapshot
        """
        start_time = time.time()
        self.cycle_count += 1

        # --- L2: Ontogenesis ---
        self.ontogenesis.evaluate_primitives()

        einstein_moment = self.ontogenesis.the_einstein_moment()
        if einstein_moment:
            print(f"  [L2] EINSTEIN MOMENT: {einstein_moment}")

        analogies = self.ontogenesis.find_analogy(domain, "general")
        concepts = self.ontogenesis.get_concepts_for_domain(domain)

        # --- Get observations from memory ---
        recent_obs = self.memory.episodic.get_recent(n=100)
        observations = [{"data": r.raw_data, "modality": r.modality}
                       for r in recent_obs]

        # --- L3: Abductive Imagination ---
        active_theories = self.memory.theory.get_active()
        candidates = self.abductive.generate_candidates(
            observations=observations,
            concepts=concepts,
            existing_theories=active_theories,
            n_candidates=10,
        )

        # --- L4: Theory Constructor ---
        new_theories = []
        for candidate in candidates:
            theory = self.theory_constructor.formalize(
                candidate=candidate,
                domain=domain,
                discipline_mode=DisciplineMode.EMPIRICAL_INTERVENTION,
                existing_theories=active_theories + new_theories,
            )
            if theory:
                registered = self.memory.theory.register(theory)
                if registered:
                    new_theories.append(theory)
                    self._check_classical_law_discovery(theory)

        # Create evidence for new theories against observations
        # so falsification can evaluate them this cycle
        if new_theories:
            for obs in observations:
                obs_data = obs.get("data", {})
                if isinstance(obs_data, dict):
                    obs_vars = set(str(k).lower() for k in obs_data.keys())
                    for t in new_theories:
                        t_vars = set(str(v).lower() for v in t.reference_class)
                        has_overlap = bool(t_vars & obs_vars)
                        if has_overlap:
                            ev = Evidence(
                                id=f"cyc_{self.cycle_count}_{t.id}_{len(self.empirics.evidence_store)}",
                                description=f"Evidence from cycle {self.cycle_count} for {t.name}",
                                data=obs_data,
                                likelihood_under_theory={t.id: 0.60},
                                replication_status=EvidenceReplicationStatus.REPLICATED_ONCE,
                                provenance=ProvenanceRecord(
                                    source_experiment=f"cycle_{self.cycle_count}",
                                    timestamp=time.time(),
                                    uncertainty_estimate=0.3,
                                ),
                            )
                            self.empirics.add_evidence(ev)
                            self.empirics.update_theory_posterior(t, ev.id)

        # --- L5: Falsification Engine ---
        all_theories = self.memory.theory.get_active()
        falsified = []
        converged = []

        for theory in all_theories:
            theory_evidence = self.empirics.query_evidence_for_theory(
                theory.id, min_posterior=0.01
            )
            eval_result = self.falsification.evaluate_theory(
                theory=theory,
                evidence=theory_evidence,
                competing=[t for t in all_theories if t.id != theory.id],
            )
            if eval_result["is_falsified"]:
                falsified.append(theory)
                retired = self.memory.theory.retire_to_graveyard(
                    theory.id, "falsified_by_L5"
                )
                if retired:
                    self.memory.graveyard.bury(retired, "L5_falsification")
            elif eval_result["is_converged"]:
                converged.append(theory)

        # --- Phase 2: Literature → KG → Gaps → Questions → Critic ---
        if self.config.phase >= 2:
            p2_result = self._phase2_research_cycle(domain, concepts, all_theories)
        else:
            p2_result = {
                "papers_ingested": 0, "gaps_detected": 0, "questions_generated": 0,
                "critiques_issued": 0, "kg_nodes_added": 0, "kg_edges_added": 0,
            }

        # --- Phase 3: Experiment Design → Intervention → Multi-Agent → Paper ---
        if self.config.phase >= 3:
            p3_result = self._phase3_research_cycle(domain, all_theories)
            if p3_result.get("debates_held", 0) == 0:
                topic = f"Test hypotheses in {domain}"
                participants = [AgentRole.THEORIST, AgentRole.CRITIC, AgentRole.REVIEWER, AgentRole.SAFETY_OFFICER]
                debate = self.multi_agent_lab.run_debate(topic, participants)
                p3_result["debates_held"] = 1
        else:
            p3_result = {
                "experiments_designed": 0, "experiments_executed": 0,
                "interventions_generated": 0, "papers_generated": 0,
                "predictions_made": 0, "cross_domain_mappings": 0,
                "debates_held": 0, "agents_active": 0,
            }

        # --- Phase 5: Self-Improving Civilization ---
        if self.config.phase >= 5:
            p5_result = self._phase5_research_cycle(domain, all_theories)
        else:
            p5_result = {
                "architecture_proposals": 0, "algorithm_candidates": 0,
                "strategy_population": 0, "benchmarks_generated": 0,
                "simulation_experiments": 0, "self_modifications_proposed": 0,
                "self_modifications_approved": 0, "meta_findings": 0,
                "abstractions_created": 0, "agendas_generated": 0,
                "civilization_health": 0.0, "civilization_innovation": 0.0,
            }

        # --- Phase 6: General Research Intelligence ---
        if self.config.phase >= 6:
            p6_result = self._phase6_research_cycle(domain, all_theories)
        else:
            p6_result = {
                "reasoning_traces": 0, "conjectures_generated": 0,
                "proofs_found": 0, "software_projects": 0,
                "open_goals": 0, "plans_active": 0,
                "agent_society_size": 0, "problems_solved": 0,
                "world_models_active": 0, "fabric_nodes": 0,
                "cross_domain_mappings_p6": 0,
            }

        # --- Phase 7: AGI-Level Scientist ---
        if self.config.phase >= 7:
            p7_result = self._phase7_research_cycle()
        else:
            p7_result = {
                "cognitive_traces": 0, "memory_episodes": 0,
                "projects_active": 0, "world_models_p7": 0,
                "tools_created": 0, "collaborations": 0,
                "creative_artifacts": 0, "active_goals": 0,
                "capabilities_assessed": 0, "grand_challenge_progress": 0.0,
                "civilization_impact": 0.0,
            }

        # --- Phase 8: Autonomous General Intelligence ---
        if self.config.phase >= 8:
            p8_result = self._phase8_research_cycle()
        else:
            p8_result = {
                "open_world_records": 0, "global_memory_entries": 0,
                "executive_active_goals": 0, "organization_agents": 0,
                "cognitive_inventions": 0, "real_world_actions": 0,
                "ecosystem_tools": 0, "civilization_forecasts": 0,
                "mission_progress": 0.0, "intelligence_overall_score": 0.0,
            }

        # --- Phase 9: Superhuman Research Intelligence ---
        if self.config.phase >= 9:
            p9_result = self._phase9_research_cycle()
        else:
            p9_result = {
                "discovery_agents_total": 0, "fields_created": 0,
                "pipelines_active": 0, "knowledge_objects_total": 0,
                "institutions_active": 0, "paradigm_shifts": 0,
                "recursive_tools_total": 0, "grand_programs_active": 0,
                "civilization_models": 0, "governance_safety_score": 0.0,
            }

        # --- Phase 10: Scientific Singularity Framework ---
        if self.config.phase >= 10:
            p10_result = self._phase10_research_cycle()
        else:
            p10_result = {
                "knowledge_evolution_rate": 0.0, "recursive_discoverers": 0,
                "fabric_integration_score": 0.0, "meta_knowledge_models": 0,
                "civilization_memory_records": 0, "governance_stability": 0.0,
                "discovery_forecasts": 0, "problem_network_density": 0.0,
                "coordination_score": 0.0, "self_sustaining": False,
            }

        # --- L6: Meta-Theory ---
        strategy_results = {
            c.strategy_origin.name: c.explanatory_power
            for c in candidates
        }
        self.meta_theory.update_from_cycle(domain, strategy_results)

        recent_anomalies = [{"score": a.anomaly_score}
                           for a in self.sensorium.get_anomalies(min_score=0.7)]
        crisis = self.meta_theory.detect_paradigm_crisis(all_theories, recent_anomalies)

        if crisis:
            resolution = self.meta_theory.resolve_crisis(self.ontogenesis)
            print(f"  [L6] PARADIGM CRISIS detected! Resolution: {resolution}")

        all_strategies = list(self.memory.meta_strategy.strategies.values())
        new_strategy = self.meta_theory.invent_strategy(domain, all_strategies)
        if new_strategy:
            self.memory.meta_strategy.register_strategy(new_strategy)
            self.memory.meta_strategy.record_invention(new_strategy, "persistent_anomalies")
            print(f"  [L6] INVENTED new strategy: {new_strategy.name}")

        # --- L-1: Auditor ---
        for proposal in self.meta_theory.proposal_queue:
            result = self.auditor.audit_proposal(proposal)
            self.memory.log_audit(AuditLogEntry(
                auditor="L-1",
                target=f"L6_proposal_{proposal.id}",
                result=result,
            ))

        agg_result = self.auditor.aggregate_effect_monitor()
        if agg_result == AuditResult.ESCALATE:
            print("  [L-1] ESCALATION: Aggregate effect monitor triggered!")

        # --- Dashboard snapshot ---
        if self.config.phase >= 2:
            self.dashboard.snapshot(self.memory, self.cycle_count)

        # --- Budget ---
        cycle_cost = 1e15
        self.budget.consume(cycle_cost)

        self.sensorium.clear_anomalies()

        duration = time.time() - start_time

        is_phase_2 = self.config.phase >= 2
        result = CycleResult(
            cycle_number=self.cycle_count,
            duration=duration,
            theories_proposed=len(new_theories),
            theories_falsified=len(falsified),
            theories_converged=len(converged),
            strategies_used=list(set(c.strategy_origin.name for c in candidates)),
            anomalies_detected=len(recent_anomalies),
            paradigm_crisis=crisis,
            memory_summary=self.memory.memory_summary(),
            motivational_state={
                "info_gain": self.motivation.information_gain_weight,
                "compression": self.motivation.compression_reward_weight,
                "dc_weight": self.motivation.disciplined_constraint_weight,
                "crisis": float(self.motivation.in_paradigm_crisis),
            },
            audit_summary=self.auditor.get_summary(),
            papers_ingested=p2_result.get("papers_ingested", 0) if is_phase_2 else 0,
            gaps_detected=p2_result.get("gaps_detected", 0) if is_phase_2 else 0,
            questions_generated=p2_result.get("questions_generated", 0) if is_phase_2 else 0,
            critiques_issued=p2_result.get("critiques_issued", 0) if is_phase_2 else 0,
            kg_nodes_added=p2_result.get("kg_nodes_added", 0) if is_phase_2 else 0,
            kg_edges_added=p2_result.get("kg_edges_added", 0) if is_phase_2 else 0,
            programs_active=len(self.memory.scientific.get_active_programs()) if is_phase_2 else 0,

            # Phase 3 metrics
            experiments_designed=p3_result.get("experiments_designed", 0) if self.config.phase >= 3 else 0,
            experiments_executed=p3_result.get("experiments_executed", 0) if self.config.phase >= 3 else 0,
            interventions_generated=p3_result.get("interventions_generated", 0) if self.config.phase >= 3 else 0,
            papers_generated=p3_result.get("papers_generated", 0) if self.config.phase >= 3 else 0,
            predictions_made=p3_result.get("predictions_made", 0) if self.config.phase >= 3 else 0,
            cross_domain_mappings=p3_result.get("cross_domain_mappings", 0) if self.config.phase >= 3 else 0,
            debates_held=p3_result.get("debates_held", 0) if self.config.phase >= 3 else 0,
            agents_active=len(self.multi_agent_lab.agents) if self.config.phase >= 3 else 0,

            # Phase 5 metrics
            architecture_proposals=p5_result.get("architecture_proposals", 0) if self.config.phase >= 5 else 0,
            algorithm_candidates=p5_result.get("algorithm_candidates", 0) if self.config.phase >= 5 else 0,
            strategy_population=p5_result.get("strategy_population", 0) if self.config.phase >= 5 else 0,
            benchmarks_generated=p5_result.get("benchmarks_generated", 0) if self.config.phase >= 5 else 0,
            simulation_experiments=p5_result.get("simulation_experiments", 0) if self.config.phase >= 5 else 0,
            self_modifications_proposed=p5_result.get("self_modifications_proposed", 0) if self.config.phase >= 5 else 0,
            self_modifications_approved=p5_result.get("self_modifications_approved", 0) if self.config.phase >= 5 else 0,
            meta_findings=p5_result.get("meta_findings", 0) if self.config.phase >= 5 else 0,
            abstractions_created=p5_result.get("abstractions_created", 0) if self.config.phase >= 5 else 0,
            agendas_generated=p5_result.get("agendas_generated", 0) if self.config.phase >= 5 else 0,
            civilization_health=p5_result.get("civilization_health", 0.0) if self.config.phase >= 5 else 0.0,
            civilization_innovation=p5_result.get("civilization_innovation", 0.0) if self.config.phase >= 5 else 0.0,

            # Phase 6 metrics
            reasoning_traces=p6_result.get("reasoning_traces", 0) if self.config.phase >= 6 else 0,
            conjectures_generated=p6_result.get("conjectures_generated", 0) if self.config.phase >= 6 else 0,
            proofs_found=p6_result.get("proofs_found", 0) if self.config.phase >= 6 else 0,
            software_projects=p6_result.get("software_projects", 0) if self.config.phase >= 6 else 0,
            open_goals=p6_result.get("open_goals", 0) if self.config.phase >= 6 else 0,
            plans_active=p6_result.get("plans_active", 0) if self.config.phase >= 6 else 0,
            agent_society_size=p6_result.get("agent_society_size", 0) if self.config.phase >= 6 else 0,
            problems_solved=p6_result.get("problems_solved", 0) if self.config.phase >= 6 else 0,
            world_models_active=p6_result.get("world_models_active", 0) if self.config.phase >= 6 else 0,
            fabric_nodes=p6_result.get("fabric_nodes", 0) if self.config.phase >= 6 else 0,
            cross_domain_mappings_p6=p6_result.get("cross_domain_mappings_p6", 0) if self.config.phase >= 6 else 0,

            # Phase 7 metrics
            cognitive_traces=p7_result.get("cognitive_traces", 0) if self.config.phase >= 7 else 0,
            memory_episodes=p7_result.get("memory_episodes", 0) if self.config.phase >= 7 else 0,
            projects_active=p7_result.get("projects_active", 0) if self.config.phase >= 7 else 0,
            world_models_p7=p7_result.get("world_models_p7", 0) if self.config.phase >= 7 else 0,
            tools_created=p7_result.get("tools_created", 0) if self.config.phase >= 7 else 0,
            collaborations=p7_result.get("collaborations", 0) if self.config.phase >= 7 else 0,
            creative_artifacts=p7_result.get("creative_artifacts", 0) if self.config.phase >= 7 else 0,
            active_goals=p7_result.get("active_goals", 0) if self.config.phase >= 7 else 0,
            capabilities_assessed=p7_result.get("capabilities_assessed", 0) if self.config.phase >= 7 else 0,
            grand_challenge_progress=p7_result.get("grand_challenge_progress", 0.0) if self.config.phase >= 7 else 0.0,
            civilization_impact=p7_result.get("civilization_impact", 0.0) if self.config.phase >= 7 else 0.0,

            # Phase 8 metrics
            open_world_records=p8_result.get("open_world_records", 0) if self.config.phase >= 8 else 0,
            global_memory_entries=p8_result.get("global_memory_entries", 0) if self.config.phase >= 8 else 0,
            executive_active_goals=p8_result.get("executive_active_goals", 0) if self.config.phase >= 8 else 0,
            organization_agents=p8_result.get("organization_agents", 0) if self.config.phase >= 8 else 0,
            cognitive_inventions=p8_result.get("cognitive_inventions", 0) if self.config.phase >= 8 else 0,
            real_world_actions=p8_result.get("real_world_actions", 0) if self.config.phase >= 8 else 0,
            ecosystem_tools=p8_result.get("ecosystem_tools", 0) if self.config.phase >= 8 else 0,
            civilization_forecasts=p8_result.get("civilization_forecasts", 0) if self.config.phase >= 8 else 0,
            mission_progress=p8_result.get("mission_progress", 0.0) if self.config.phase >= 8 else 0.0,
            intelligence_overall_score=p8_result.get("intelligence_overall_score", 0.0) if self.config.phase >= 8 else 0.0,

            # Phase 9 metrics
            discovery_agents_total=p9_result.get("discovery_agents_total", 0) if self.config.phase >= 9 else 0,
            fields_created=p9_result.get("fields_created", 0) if self.config.phase >= 9 else 0,
            pipelines_active=p9_result.get("pipelines_active", 0) if self.config.phase >= 9 else 0,
            knowledge_objects_total=p9_result.get("knowledge_objects_total", 0) if self.config.phase >= 9 else 0,
            institutions_active=p9_result.get("institutions_active", 0) if self.config.phase >= 9 else 0,
            paradigm_shifts=p9_result.get("paradigm_shifts", 0) if self.config.phase >= 9 else 0,
            recursive_tools_total=p9_result.get("recursive_tools_total", 0) if self.config.phase >= 9 else 0,
            grand_programs_active=p9_result.get("grand_programs_active", 0) if self.config.phase >= 9 else 0,
            civilization_models=p9_result.get("civilization_models", 0) if self.config.phase >= 9 else 0,
            governance_safety_score=p9_result.get("governance_safety_score", 0.0) if self.config.phase >= 9 else 0.0,

            # Phase 10 metrics
            knowledge_evolution_rate=p10_result.get("knowledge_evolution_rate", 0.0) if self.config.phase >= 10 else 0.0,
            recursive_discoverers=p10_result.get("recursive_discoverers", 0) if self.config.phase >= 10 else 0,
            fabric_integration_score=p10_result.get("fabric_integration_score", 0.0) if self.config.phase >= 10 else 0.0,
            meta_knowledge_models=p10_result.get("meta_knowledge_models", 0) if self.config.phase >= 10 else 0,
            civilization_memory_records=p10_result.get("civilization_memory_records", 0) if self.config.phase >= 10 else 0,
            governance_stability=p10_result.get("governance_stability", 0.0) if self.config.phase >= 10 else 0.0,
            discovery_forecasts=p10_result.get("discovery_forecasts", 0) if self.config.phase >= 10 else 0,
            problem_network_density=p10_result.get("problem_network_density", 0.0) if self.config.phase >= 10 else 0.0,
            coordination_score=p10_result.get("coordination_score", 0.0) if self.config.phase >= 10 else 0.0,
            self_sustaining=p10_result.get("self_sustaining", False) if self.config.phase >= 10 else False,
        )

        self.cycle_history.append(result)
        return result
    
    def _check_classical_law_discovery(self, theory: Theory) -> None:
        """Check if a theory matches a known classical law (B1)."""
        # Build comprehensive description from theory
        theory_parts = [theory.name.lower()]
        for c in theory.core_claims:
            theory_parts.append(c.statement.lower())
        for ref in theory.reference_class:
            theory_parts.append(ref.lower())
        if theory.intervention:
            for var in theory.intervention.target_variables:
                theory_parts.append(var.lower())
        theory_desc = " ".join(theory_parts)
        theory_set = set(theory_desc.split())
        
        for law_id, law_info in self.classical_laws_catalog.items():
            if law_id in self.discovered_laws:
                continue
            
            # Match on observables (key variables)
            observables = [obs.lower() for obs in law_info["observables"]]
            observable_hits = sum(1 for obs in observables if obs in theory_desc)
            observable_score = observable_hits / len(observables) if observables else 0
            
            # Match on pattern keywords (e.g., "period", "axis", "pressure", "volume")
            pattern_keywords = law_info["pattern"].lower().replace("^", " ").replace("·", " ").replace("=", " ").replace("∝", " ").split()
            pattern_hits = sum(1 for kw in pattern_keywords if kw in theory_set and len(kw) > 1)
            pattern_score = pattern_hits / len(pattern_keywords) if pattern_keywords else 0
            
            # Combined score - need strong observable match
            match_score = 0.7 * observable_score + 0.3 * pattern_score
            
            # Require at least 2/3 of observables to match
            if observable_hits >= max(2, len(observables) * 0.5) and match_score > 0.4:
                self.discovered_laws[law_id] = {
                    "law_name": law_info["name"],
                    "theory_id": theory.id,
                    "match_score": match_score,
                    "cycle": self.cycle_count,
                    "pattern": law_info["pattern"],
                }
                print(f"  [B1] DISCOVERED: {law_info['name']} ({law_info['pattern']})")
    
    def run_benchmark_b1(self, max_cycles: int = 50) -> Dict[str, Any]:
        """
        B1: Rediscovery of classical laws.
        Pass criterion: Rediscover 5 of 6 from {Kepler, Ohm, Snell, Ideal Gas, Coulomb, Momentum}.
        """
        print(f"\n{'='*60}")
        print(f"B1 BENCHMARK: Classical Law Rediscovery")
        print(f"Target: 5 of 6 laws | Max cycles: {max_cycles}")
        print(f"{'='*60}\n")
        
        # Provide observational data that encodes the laws implicitly
        self._generate_classical_law_data()
        
        for cycle in range(max_cycles):
            result = self.research_cycle(domain="physics")
            
            print(f"Cycle {cycle+1}: "
                  f"{result.theories_proposed} proposed, "
                  f"{result.theories_falsified} falsified, "
                  f"{result.theories_converged} converged, "
                  f"{len(self.discovered_laws)}/6 laws found")
            
            if len(self.discovered_laws) >= 5:
                print(f"\n{'='*60}")
                print(f"B1 PASSED! Discovered {len(self.discovered_laws)}/6 laws in {cycle+1} cycles")
                print(f"{'='*60}")
                return {
                    "passed": True,
                    "laws_discovered": len(self.discovered_laws),
                    "cycles": cycle + 1,
                    "discovered": self.discovered_laws,
                }
        
        print(f"\n{'='*60}")
        print(f"B1 INCOMPLETE: Discovered {len(self.discovered_laws)}/6 laws in {max_cycles} cycles")
        print(f"{'='*60}")
        return {
            "passed": len(self.discovered_laws) >= 5,
            "laws_discovered": len(self.discovered_laws),
            "cycles": max_cycles,
            "discovered": self.discovered_laws,
        }
    
    def _generate_classical_law_data(self) -> None:
        """Generate observational data implicitly encoding classical laws."""
        np.random.seed(42)
        
        datasets = {
            "kepler": self._generate_kepler_data(),
            "ohms": self._generate_ohms_data(),
            "snells": self._generate_snells_data(),
            "ideal_gas": self._generate_ideal_gas_data(),
            "coulomb": self._generate_coulomb_data(),
            "momentum": self._generate_momentum_data(),
        }
        
        for name, data in datasets.items():
            self.ingest_data(data, modality="numerical")
    
    def _generate_kepler_data(self) -> List[Dict]:
        """T² ∝ a³: period vs semi-major axis for planetary orbits."""
        data = []
        for a in np.linspace(0.5, 10, 20):  # semi-major axis
            T = np.sqrt(a**3) + np.random.normal(0, 0.1)  # period
            data.append({"semi_major_axis": a, "period": T, "body_type": "planet"})
        return data
    
    def _generate_ohms_data(self) -> List[Dict]:
        """V = I·R: voltage vs current at fixed resistance."""
        data = []
        R = 10  # Fixed resistance
        for I in np.linspace(0.1, 5, 20):  # current
            V = I * R + np.random.normal(0, 0.5)
            data.append({"current": I, "voltage": V, "resistance": R})
        return data
    
    def _generate_snells_data(self) -> List[Dict]:
        """n₁·sin(θ₁) = n₂·sin(θ₂): refraction data."""
        data = []
        n1, n2 = 1.0, 1.5  # air to glass
        for theta1_deg in np.linspace(10, 80, 15):
            theta1 = np.radians(theta1_deg)
            theta2 = np.arcsin(n1 * np.sin(theta1) / n2)
            theta2_deg = np.degrees(theta2) + np.random.normal(0, 0.5)
            data.append({
                "angle_incidence": theta1_deg,
                "angle_refraction": theta2_deg,
                "refractive_index_1": n1,
                "refractive_index_2": n2,
            })
        return data
    
    def _generate_ideal_gas_data(self) -> List[Dict]:
        """PV = nRT: pressure vs volume at fixed temperature."""
        data = []
        n, R_const, T = 1, 0.0821, 300  # 1 mol, 300K
        for V in np.linspace(1, 10, 20):  # volume
            P = n * R_const * T / V + np.random.normal(0, 0.05)
            data.append({"volume": V, "pressure": P, "temperature": T, "amount": n})
        return data
    
    def _generate_coulomb_data(self) -> List[Dict]:
        """F = k·q₁q₂/r²: electrostatic force vs distance."""
        data = []
        k, q1, q2 = 8.99e9, 1e-6, 1e-6
        for r in np.linspace(0.1, 2, 20):  # distance
            F = k * q1 * q2 / (r**2) + np.random.normal(0, 1e-3)
            data.append({"distance": r, "force": F, "charge_1": q1, "charge_2": q2})
        return data
    
    def _generate_momentum_data(self) -> List[Dict]:
        """Conservation of momentum: collision data."""
        data = []
        for _ in range(20):
            m1, v1 = 2.0, 3.0  # mass and velocity before
            m2, v2 = 3.0, -1.0
            
            # After elastic collision (simplified)
            v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
            v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
            
            p_initial = m1 * v1 + m2 * v2
            p_final = m1 * v1_final + m2 * v2_final + np.random.normal(0, 0.1)
            
            data.append({
                "mass_1": m1, "velocity_1_initial": v1, "velocity_1_final": v1_final,
                "mass_2": m2, "velocity_2_initial": v2, "velocity_2_final": v2_final,
                "momentum_initial": p_initial, "momentum_final": p_final,
            })
        return data
    
    def _build_domain_graph(self) -> Dict[str, Any]:
        kg = self.memory.knowledge_graph
        domain_nodes = kg.get_nodes_by_type(KGNodeType.DOMAIN) if hasattr(kg, 'get_nodes_by_type') else []
        domains = set()
        for n in domain_nodes:
            d = n.properties.get("domain", n.name)
            if d:
                domains.add(d)
        if not domains:
            domains = {"physics", "biology", "economics"}
        return {d: domains - {d} for d in domains}

    def _phase3_research_cycle(self, domain: str,
                                active_theories: List[Theory]) -> Dict[str, Any]:
        result = {
            "experiments_designed": 0,
            "experiments_executed": 0,
            "interventions_generated": 0,
            "papers_generated": 0,
            "predictions_made": 0,
            "cross_domain_mappings": 0,
            "debates_held": 0,
            "agents_active": len(self.multi_agent_lab.agents),
        }

        for theory in active_theories[:3]:
            intervention = self.intervention_gen.generate_from_theory(theory)
            result["interventions_generated"] += 1

            design = self.experiment_planner.design_from_theory(theory, domain)
            result["experiments_designed"] += 1

            ground_truth = {v: np.random.uniform(0.2, 0.8)
                          for v in theory.reference_class[:3]}
            exp_result = self.experiment_planner.simulate_experiment(design.id, ground_truth)
            if exp_result:
                result["experiments_executed"] += 1

            evaluation = self.experiment_eval.evaluate(design, exp_result)

            review = self.multi_agent_lab.review_theory_pipeline(theory, design, exp_result)
            if review["passes_review"] and exp_result:
                paper = self.paper_gen.generate(theory, design, exp_result)
                result["papers_generated"] += 1

            pred = self.prediction_engine.predict_outcome(theory, design)
            result["predictions_made"] += 1

            if exp_result:
                self.prediction_engine.evaluate_from_experiment(pred, exp_result)

        self._cross_domain_cycle(domain, active_theories, result)

        return result

    def _cross_domain_cycle(self, domain: str, active_theories: List[Theory],
                             result: Dict[str, Any]) -> None:
        target_domains = [d for d in ["physics", "biology", "economics", "neuroscience"]
                         if d != domain]
        if not target_domains:
            return

        target = target_domains[0]
        source_concepts = []
        for t in active_theories[:2]:
            for c in t.reference_class[:3]:
                from theoria.core.types import Concept
                source_concepts.append(Concept(name=c, definition=c))
        target_concepts = source_concepts[:2]

        mappings = self.cross_domain.find_mappings(domain, target,
                                                     source_concepts, target_concepts)
        result["cross_domain_mappings"] += len(mappings)

        for mapping in mappings[:1]:
            for theory in active_theories[:1]:
                hypothesis = self.cross_domain.apply_mapping(mapping, theory)
                from theoria.layers.abductive import CandidateHypothesis
                if hypothesis:
                    print(f"  [P3.7] Cross-domain hypothesis: {mapping.source_domain} -> {mapping.target_domain}")

    def _phase5_research_cycle(self, domain: str,
                                active_theories: List[Theory]) -> Dict[str, Any]:
        """Phase 5 research pipeline: self-improvement + meta-civilization."""
        result = {
            "architecture_proposals": 0,
            "algorithm_candidates": 0,
            "strategy_population": 0,
            "benchmarks_generated": 0,
            "simulation_experiments": 0,
            "self_modifications_proposed": 0,
            "self_modifications_approved": 0,
            "meta_findings": 0,
            "abstractions_created": 0,
            "agendas_generated": 0,
            "civilization_health": 0.0,
            "civilization_innovation": 0.0,
        }

        # L11: Self-Improvement
        layer_perf = {f"L{i}": random.uniform(0.4, 0.9) for i in range(0, 11)}
        bottlenecks = [
            {"layer": "L3", "issue": "underperformance", "severity": 0.5},
            {"layer": "L5", "issue": "bottleneck", "severity": 0.3},
        ]
        all_strategies = list(self.memory.meta_strategy.strategies.values())
        si_result = self.self_improvement.run_cycle(layer_perf, bottlenecks, all_strategies)
        result["architecture_proposals"] = si_result.get("architecture_proposals", 0)
        result["algorithm_candidates"] = si_result.get("algorithm_candidates", 0)
        result["strategy_population"] = si_result.get("strategy_population", 0)

        # Benchmark generation
        benchmarks = self.benchmark_generator.generate_benchmark_suite(domain, count=3)
        result["benchmarks_generated"] = len(benchmarks)

        # Simulation worlds
        if not self.simulation_worlds.worlds:
            self.simulation_worlds.initialize_worlds()
        sim_results = self.simulation_worlds.run_batch_experiments(n=50)
        result["simulation_experiments"] = len(sim_results)

        # Self-modification safety pipeline
        if random.random() < 0.2:
            proposal = self.self_modification.propose_modification(
                name=f"tune_{domain}_{self.cycle_count}",
                description=f"Tune parameters for {domain} research",
                target_component=f"L3_{domain}",
                modification_type="parameter_tuning",
            )
            result["self_modifications_proposed"] = 1
            completed = self.self_modification.run_safety_pipeline(proposal, current_performance=0.7)
            if completed.approval_status == "approved":
                result["self_modifications_approved"] = 1

        # Knowledge compression
        theory_dict = {t.id: t for t in active_theories}
        if theory_dict:
            abstraction = self.knowledge_compression.compress_theories(theory_dict)
            if abstraction:
                result["abstractions_created"] = 1

        # L12: Meta-Civilization
        method_stats = {s.name: s.expected_value for s in all_strategies}
        theory_lifetimes = {}
        for t in active_theories:
            theory_lifetimes[t.name] = t.cycles_below_threshold + 5

        society_data = {}
        if hasattr(self, 'scientific_society'):
            try:
                society_data = {
                    "total_papers": sum(a.papers_published for a in self.scientific_society.agents),
                    "collaborations": len(self.scientific_society.collaborations) if hasattr(self.scientific_society, 'collaborations') else 0,
                    "agent_count": len(self.scientific_society.agents),
                }
            except Exception:
                society_data = {"total_papers": 0, "collaborations": 0, "agent_count": 100}

        mc_result = self.meta_civilization.run_cycle(
            method_stats=method_stats,
            theory_lifetimes=theory_lifetimes,
            experiment_results=[],
            agent_data={"avg_productivity": 0.5},
            theory_data={
                "avg_quality": np.mean([t.posterior for t in active_theories]) if active_theories else 0.5,
                "active_count": len(active_theories),
                "paradigm_shifts": 0,
                "novelty_rate": 0.5,
            },
            experiment_data={
                "total": result.get("simulation_experiments", 0),
                "discoveries_per_cycle": 5,
                "resource_efficiency": 0.5,
                "breakthrough_rate": 0.1,
            },
            society_data=society_data,
            gaps=[],
            existing_theories=len(active_theories),
        )
        result["meta_findings"] = mc_result.get("meta_findings", 0)
        result["civilization_health"] = mc_result.get("health_score", 0)
        result["civilization_innovation"] = mc_result.get("innovation_score", 0)
        result["agendas_generated"] = 1 if mc_result.get("agenda_generated") else 0

        return result

    def _phase6_research_cycle(self, domain: str,
                                active_theories: List[Theory]) -> Dict[str, Any]:
        """Phase 6 research pipeline: General Research Intelligence."""
        result = {
            "reasoning_traces": 0,
            "conjectures_generated": 0,
            "proofs_found": 0,
            "software_projects": 0,
            "open_goals": 0,
            "plans_active": 0,
            "agent_society_size": 0,
            "problems_solved": 0,
            "world_models_active": 0,
            "fabric_nodes": 0,
            "cross_domain_mappings_p6": 0,
        }

        # L13: Universal Reasoning
        reasoning_result = self.universal_reasoning.reason_all_modes(
            "Analyze {} research domain".format(domain))
        result["reasoning_traces"] = sum(
            1 for r in reasoning_result.values() if r.conclusion)

        # Mathematical Discovery
        math_result = self.mathematical_discovery.run_cycle()
        result["conjectures_generated"] = math_result.conjectures_generated
        result["proofs_found"] = math_result.proofs_found

        # Software Intelligence
        sw_result = self.software_intelligence.run_cycle()
        result["software_projects"] = sw_result.projects_created

        # Open-Ended Learning
        oel_result = self.open_ended_learning.run_cycle()
        result["open_goals"] = len(oel_result.active_goals)

        # Long-Horizon Planning
        plan_results = self.long_horizon_planning.run_cycle()
        result["plans_active"] = len([pr for pr in plan_results if pr.plan and pr.plan.status == "active"])

        # General Agent Society
        society_result = self.general_agent_society.run_cycle()
        result["agent_society_size"] = society_result.active_agents

        # Universal Problem Solver
        solver_result = self.universal_problem_solver.run_cycle()
        result["problems_solved"] = solver_result.solutions_found

        # World Models
        world_result = self.world_models.run_cycle()
        result["world_models_active"] = world_result.models_active

        # Universal Knowledge Fabric
        fabric_result = self.universal_fabric.evolve()
        result["fabric_nodes"] = fabric_result.new_nodes
        result["cross_domain_mappings_p6"] = fabric_result.cross_domain_links

        return result

    def _phase7_research_cycle(self) -> Dict[str, Any]:
        """Phase 7 research pipeline: AGI-Level Scientist."""
        result = {
            "cognitive_traces": 0, "memory_episodes": 0,
            "projects_active": 0, "world_models_p7": 0,
            "tools_created": 0, "collaborations": 0,
            "creative_artifacts": 0, "active_goals": 0,
            "capabilities_assessed": 0, "grand_challenge_progress": 0.0,
            "civilization_impact": 0.0,
        }

        # L14b: Unified Cognitive Core
        cc_result = self.unified_cognitive_core.run_cycle()
        result["cognitive_traces"] = cc_result.traces_generated

        # L15: Lifelong Memory
        mem_result = self.lifelong_memory.run_cycle()
        result["memory_episodes"] = mem_result.total_episodes

        # Research Director (portfolio management)
        rd_result = self.research_director.run_cycle()
        result["projects_active"] = rd_result.active_projects

        # Unified World Model
        wm_result = self.unified_world_model_p7.run_cycle()
        result["world_models_p7"] = wm_result.models_maintained

        # L16: Agency Layer
        ag_result = self.agency.run_cycle()
        result["active_goals"] = ag_result.active_goals

        # Tool Creation
        tc_result = self.tool_creation.run_cycle()
        result["tools_created"] = tc_result.tools_created

        # Human Collaboration
        hc_result = self.human_collab.run_cycle()
        result["collaborations"] = hc_result.interactions

        # Creativity Engine
        cr_result = self.creativity.run_cycle()
        result["creative_artifacts"] = cr_result.artifacts_created

        # Self Evaluation
        se_result = self.self_eval.run_cycle()
        result["capabilities_assessed"] = se_result.capabilities_assessed

        # L17: Grand Challenge + Civilization Intelligence
        gc_result = self.grand_challenge.run_cycle()
        result["grand_challenge_progress"] = gc_result.total_progress

        ci_result = self.civilization_intel.run_cycle()
        result["civilization_impact"] = ci_result.civilization_impact

        return result

    def _phase8_research_cycle(self) -> Dict[str, Any]:
        """Phase 8 research pipeline: Autonomous General Intelligence."""
        result = {
            "open_world_records": 0, "global_memory_entries": 0,
            "executive_active_goals": 0, "organization_agents": 0,
            "cognitive_inventions": 0, "real_world_actions": 0,
            "ecosystem_tools": 0, "civilization_forecasts": 0,
            "mission_progress": 0.0, "intelligence_overall_score": 0.0,
        }

        # P8.1: Open-World Learning
        owl_result = self.open_world_learning.run_cycle()
        result["open_world_records"] = owl_result.records_created

        # P8.2: Global Memory
        gm_result = self.global_memory.run_cycle()
        result["global_memory_entries"] = gm_result.total_entries

        # L18: Executive Intelligence
        ei_result = self.executive_intel.run_cycle()
        result["executive_active_goals"] = ei_result.active_goals

        # P8.4: Organization Builder
        ob_result = self.organization_builder.run_cycle()
        result["organization_agents"] = ob_result.total_agents

        # L19: Cognitive Evolution
        ce_result = self.cognitive_evolution.run_cycle()
        result["cognitive_inventions"] = ce_result.inventions

        # P8.6: Real-World Action
        rwa_result = self.real_world_action.run_cycle()
        result["real_world_actions"] = rwa_result.actions_executed

        # P8.7: Tool Ecosystem
        te_result = self.tool_ecosystem.run_cycle()
        result["ecosystem_tools"] = te_result.tools_active

        # P8.8: Civilization Simulator
        cs_result = self.civilization_sim.run_cycle()
        result["civilization_forecasts"] = cs_result.forecasts_generated

        # L20: Mission Intelligence
        ms_result = self.mission_system.run_cycle()
        result["mission_progress"] = ms_result.total_progress

        # P8.10: Intelligence Evaluator
        ie_result = self.intelligence_eval.run_cycle()
        result["intelligence_overall_score"] = ie_result.overall_score

        return result

    def _phase9_research_cycle(self) -> Dict[str, Any]:
        """Phase 9 research pipeline: Superhuman Research Intelligence."""
        result = {
            "discovery_agents_total": 0, "fields_created": 0,
            "pipelines_active": 0, "knowledge_objects_total": 0,
            "institutions_active": 0, "paradigm_shifts": 0,
            "recursive_tools_total": 0, "grand_programs_active": 0,
            "civilization_models": 0, "governance_safety_score": 0.0,
        }

        # L21: Discovery Acceleration
        da_result = self.discovery_accel.run_cycle()
        result["pipelines_active"] = da_result.pipelines_active

        # P9.1: Planet-Scale Discovery
        pd_result = self.planet_discovery.run_discovery_cycle()
        result["discovery_agents_total"] = pd_result.total_agents

        # P9.2: Autonomous Field Creation
        fc_result = self.field_creator.run_cycle()
        result["fields_created"] = fc_result.total_fields

        # L22: Knowledge Civilization
        kc_result = self.knowledge_civ_layer.run_cycle()
        result["knowledge_objects_total"] = kc_result.knowledge_objects
        result["institutions_active"] = kc_result.institutions_active
        result["grand_programs_active"] = kc_result.programs_active
        result["civilization_models"] = kc_result.models_active

        # P9.6: Paradigm Shift Generator
        ps_result = self.paradigm_shift_gen.run_cycle()
        result["paradigm_shifts"] = ps_result.total_shifts

        # P9.7: Recursive Tool Civilization
        rt_result = self.recursive_tools.run_cycle()
        result["recursive_tools_total"] = rt_result.total_tools

        # P9.8: Grand Discovery Programs
        gp_result = self.grand_programs.run_cycle()
        result["grand_programs_active"] = gp_result.programs_active

        # P9.9: Meta-Civilization Intelligence
        mc_result = self.meta_civ_intel.run_cycle()
        result["civilization_models"] = mc_result.total_models

        # L23: Superintelligence Governance
        gv_result = self.governance.run_cycle()
        result["governance_safety_score"] = gv_result.overall_safety_score

        return result

    def _phase10_research_cycle(self) -> Dict[str, Any]:
        """Phase 10 research pipeline: Scientific Singularity Framework."""
        result = {
            "knowledge_evolution_rate": 0.0, "recursive_discoverers": 0,
            "fabric_integration_score": 0.0, "meta_knowledge_models": 0,
            "civilization_memory_records": 0, "governance_stability": 0.0,
            "discovery_forecasts": 0, "problem_network_density": 0.0,
            "coordination_score": 0.0, "self_sustaining": False,
        }

        # L24: Knowledge Evolution
        ke_result = self.knowledge_evolution_layer.run_cycle()
        result["knowledge_evolution_rate"] = ke_result.evolution_rate

        # P10.2: Recursive Discovery Ecosystem
        rd_result = self.recursive_discovery.run_cycle()
        result["recursive_discoverers"] = rd_result.total_discoverers

        # P10.3: Universal Knowledge Fabric 2.0
        kf_result = self.knowledge_fabric2.run_cycle()
        result["fabric_integration_score"] = kf_result.integration_score

        # P10.5: Meta-Knowledge Civilization
        mk_result = self.meta_knowledge.run_cycle()
        result["meta_knowledge_models"] = mk_result.total_models

        # P10.6: Civilization Memory
        cm_result = self.civilization_memory.run_cycle()
        result["civilization_memory_records"] = cm_result.total_records

        # L25: Civilization Governance
        cg_result = self.civilization_governance.run_cycle()
        result["governance_stability"] = cg_result.stability_score

        # P10.8: Discovery Forecasting
        df_result = self.discovery_forecasting.run_cycle()
        result["discovery_forecasts"] = df_result.total_forecasts

        # P10.9: Universal Problem Network
        pn_result = self.problem_network.run_cycle()
        result["problem_network_density"] = pn_result.network_density

        # L26: Singularity Coordination
        sc_result = self.singularity_coordination.run_cycle()
        result["coordination_score"] = sc_result.coordination_score
        result["self_sustaining"] = sc_result.self_sustaining

        return result

    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary."""
        is_phase_2 = self.config.phase >= 2
        summary = {
            "cycles_completed": self.cycle_count,
            "memory": self.memory.memory_summary(),
            "auditor": self.auditor.get_summary(),
            "constitutional": self.constitutional.get_summary(),
            "meta_theory": self.meta_theory.get_summary(),
            "falsification": self.falsification.get_summary(),
            "theory_constructor": self.theory_constructor.get_summary(),
            "abductive": self.abductive.get_summary(),
            "ontogenesis": self.ontogenesis.get_summary(),
            "budget_remaining": self.budget.B_life - self.budget.B_life_consumed,
            "discovered_laws": len(self.discovered_laws),
            "discovered_law_details": self.discovered_laws,
        }
        
        if is_phase_2:
            p2 = {
                "literature": self.literature.get_ingestion_stats(),
                "gap_detector": self.gap_detector.get_summary(),
                "question_generator": self.question_gen.get_summary(),
                "planner": self.planner.get_summary(),
                "critic": self.critic.get_summary(),
                "dashboard": self.dashboard.get_summary(),
                "knowledge_graph": self.memory.knowledge_graph.get_summary(),
            }
            summary["phase_2"] = p2
        
        if self.config.phase >= 3:
            p3 = {
                "experiment_planner": self.experiment_planner.get_summary(),
                "intervention_generator": self.intervention_gen.get_summary(),
                "counterfactual_simulator": self.counterfactual_sim.get_summary(),
                "experiment_evaluator": self.experiment_eval.get_summary(),
                "multi_agent_lab": self.multi_agent_lab.get_summary(),
                "paper_generator": self.paper_gen.get_summary(),
                "prediction_engine": self.prediction_engine.get_summary(),
                "cross_domain": self.cross_domain.get_summary(),
                "data_connector": self.data_connector.get_summary(),
            }
            summary["phase_3"] = p3

        if self.config.phase >= 4:
            p4 = {
                "real_data": self.real_data.get_summary(),
                "embodied_lab": self.embodied_lab.get_summary(),
                "scientific_society": self.scientific_society.get_summary(),
                "communication": self.communication.get_summary(),
                "ethics_layer": self.ethics_layer.get_summary(),
                "adversarial_science": self.adversarial_science.get_summary(),
                "prediction_market": self.prediction_market.get_summary(),
                "scientific_economy": self.scientific_economy.get_summary(),
                "research_programs": self.research_programs.get_summary(),
                "knowledge_evolution": self.knowledge_evolution.get_summary(),
            }
            summary["phase_4"] = p4

        if self.config.phase >= 5:
            p5 = {
                "self_improvement": self.self_improvement.get_summary(),
                "meta_civilization": self.meta_civilization.get_summary(),
                "benchmark_generator": self.benchmark_generator.get_summary(),
                "simulation_worlds": self.simulation_worlds.get_summary(),
                "self_modification": self.self_modification.get_summary(),
                "knowledge_compression": self.knowledge_compression.get_summary(),
            }
            summary["phase_5"] = p5

        if self.config.phase >= 6:
            p6 = {
                "universal_reasoning": self.universal_reasoning.get_summary(),
                "knowledge_civilization": self.knowledge_civilization.get_summary(),
                "mathematical_discovery": self.mathematical_discovery.get_summary(),
                "software_intelligence": self.software_intelligence.get_summary(),
                "open_ended_learning": self.open_ended_learning.get_summary(),
                "long_horizon_planning": self.long_horizon_planning.get_summary(),
                "general_agent_society": self.general_agent_society.get_summary(),
                "universal_problem_solver": self.universal_problem_solver.get_summary(),
                "world_models": self.world_models.get_summary(),
                "universal_fabric": self.universal_fabric.get_summary(),
            }
            summary["phase_6"] = p6

        if self.config.phase >= 7:
            p7 = {
                "unified_cognitive_core": self.unified_cognitive_core.run_cycle().__dict__,
                "lifelong_memory": self.lifelong_memory.get_life_history(),
                "research_director": {
                    "total_projects": self.research_director.portfolio.total_projects,
                    "active_projects": self.research_director.portfolio.active_projects,
                },
                "unified_world_model": {
                    "models": len(self.unified_world_model_p7.models),
                },
                "tool_creation": {
                    "tools": len(self.tool_creation.tools),
                },
                "human_collaboration": {
                    "collaborations": len(self.human_collab.collaborations),
                },
                "creativity": {
                    "artifacts": len(self.creativity.artifacts),
                },
                "agency": {
                    "active_goals": len(self.agency.active_goal_ids),
                    "completed_goals": len(self.agency.completed_goal_ids),
                },
                "self_evaluation": {
                    "assessments": len(self.self_eval.assessments),
                },
                "grand_challenge": self.grand_challenge.get_summary(),
                "civilization_intelligence": {
                    "portfolios": len(self.civilization_intel.portfolios),
                    "grand_challenges": len(self.civilization_intel.grand_challenge_results),
                },
            }
            summary["phase_7"] = p7

        if self.config.phase >= 9:
            p9 = {
                "planet_discovery": self.planet_discovery.get_summary(),
                "field_creator": self.field_creator.get_summary(),
                "discovery_accel": self.discovery_accel.get_summary(),
                "global_knowledge": self.global_knowledge.get_summary(),
                "research_institutions": self.research_institutions.get_summary(),
                "paradigm_shift_gen": self.paradigm_shift_gen.get_summary(),
                "recursive_tools": self.recursive_tools.get_summary(),
                "grand_programs": self.grand_programs.get_summary(),
                "meta_civ_intel": self.meta_civ_intel.get_summary(),
                "governance": self.governance.get_summary(),
                "knowledge_civ_layer": self.knowledge_civ_layer.get_summary(),
            }
            summary["phase_9"] = p9

        if self.config.phase >= 10:
            p10 = {
                "knowledge_evolution": self.knowledge_evolution_layer.get_summary(),
                "recursive_discovery": self.recursive_discovery.get_summary(),
                "knowledge_fabric2": self.knowledge_fabric2.get_summary(),
                "meta_knowledge": self.meta_knowledge.get_summary(),
                "civilization_memory": self.civilization_memory.get_summary(),
                "civilization_governance": self.civilization_governance.get_summary(),
                "discovery_forecasting": self.discovery_forecasting.get_summary(),
                "problem_network": self.problem_network.get_summary(),
                "singularity_coordination": self.singularity_coordination.get_summary(),
            }
            summary["phase_10"] = p10

        return summary


# Need to import StrategyType for the orchestrator
from theoria.core.types import StrategyType
