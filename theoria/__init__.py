"""
THEORIA: A Cognitive Architecture for Autonomous Scientific Theory Creation
An Audited, Bounded, Governed, and Self-Improving Framework for Theory-Creating AGI

Author: rajesh gurugubelli (June 2026)
Prototype Implementation
"""

__version__ = "0.6.0"
__author__ = "rajesh gurugubelli"

from theoria.core.types import (
    Theory,
    Evidence,
    Concept,
    Strategy,
    Intervention,
    TheoryStatus,
    DisciplineMode,
    # Phase 2 types
    ScientificPaper,
    Citation,
    Figure,
    KGNode,
    KGEdge,
    KGNodeType,
    KGEdgeType,
    ResearchGap,
    ResearchQuestion,
    ResearchProgram,
    CriticReport,
    QualityMetrics,
    DashboardMetrics,
)

from theoria.core.memory import (
    EpisodicMemory,
    SemanticMemory,
    TheoryMemory,
    Graveyard,
    MetaStrategyMemory,
    MemoryArchitecture,
    ScientificMemory,
)

from theoria.core.config import TheoriaConfig

from theoria.core.knowledge_graph import KnowledgeGraph

from theoria.layers.literature import LiteratureIngestor, PaperCorpus
from theoria.layers.gap_detector import GapDetector
from theoria.layers.question_generator import QuestionGenerator
from theoria.layers.planner import ResearchPlanner
from theoria.layers.critic import ScientificCritic
from theoria.layers.dashboard import DiscoveryDashboard

from theoria.layers.experiment_design import ExperimentPlanner
from theoria.layers.intervention import InterventionGenerator, CounterfactualSimulator, ExperimentEvaluator
from theoria.layers.multi_agent import MultiAgentLab, PlannerAgent, TheoryAgent, ExperimentAgent, CriticAgent, ReviewerAgent, SafetyAgent
from theoria.layers.paper_generator import PaperGenerator
from theoria.layers.prediction_engine import PredictionEngine
from theoria.layers.cross_domain import CrossDomainTransfer
from theoria.layers.data_connectors import DataConnector, Dataset

from theoria.layers.real_data import RealDataConnector
from theoria.layers.embodied import EmbodiedLab
from theoria.layers.scientific_society import ScientificSociety
from theoria.layers.communication import CommunicationLayer
from theoria.layers.ethics import EthicsLayer
from theoria.layers.adversarial import AdversarialScience, RedTeam
from theoria.layers.prediction_market import PredictionMarket
from theoria.layers.economy import ScientificEconomy
from theoria.layers.research_programs import ResearchProgramManager
from theoria.layers.evolution import KnowledgeEvolution

from theoria.layers.self_improvement import SelfImprovementLayer, ArchitectureSearch, AlgorithmDiscovery, StrategyEvolution
from theoria.layers.meta_civilization import MetaCivilizationLayer, MetaScienceEngine, CivilizationAnalytics, GoalGeneration
from theoria.layers.benchmark_generator import BenchmarkGenerator
from theoria.layers.simulation_worlds import SimulationWorldManager
from theoria.layers.self_modification import SelfModificationFramework
from theoria.layers.knowledge_compression import KnowledgeCompressionEngine

from theoria.core.types import (
    ArchitectureProposal, AlgorithmCandidate, StrategyVariant,
    BenchmarkSpec, MetaScienceFinding, SimulationWorld,
    SelfModificationProposal, CompressedAbstraction, ResearchAgenda,
    CivilizationMetrics,
    # Phase 6 types
    KnowledgeNode, KnowledgeEdge, ReasoningTrace, MathematicalConjecture,
    SoftwareProject, CrossDomainMapping, OpenEndedGoal, LongHorizonPlan,
    GeneralAgent, UniversalProblem, WorldModel,
)

from theoria.layers.universal_reasoning import UniversalReasoningEngine
from theoria.layers.knowledge_civilization import KnowledgeCivilizationLayer
from theoria.layers.mathematical_discovery import MathematicalDiscovery
from theoria.layers.software_intelligence import SoftwareIntelligence
from theoria.layers.open_ended_learning import OpenEndedLearning
from theoria.layers.long_horizon_planning import LongHorizonPlanning
from theoria.layers.general_agent_society import GeneralAgentSociety
from theoria.layers.universal_solver import UniversalProblemSolver
from theoria.layers.world_models import WorldModelingEngine
from theoria.layers.universal_fabric import UniversalKnowledgeFabric

__all__ = [
    # Phase 1
    "Theory",
    "Evidence",
    "Concept",
    "Strategy",
    "Intervention",
    "TheoryStatus",
    "DisciplineMode",
    "EpisodicMemory",
    "SemanticMemory",
    "TheoryMemory",
    "Graveyard",
    "MetaStrategyMemory",
    "MemoryArchitecture",
    "TheoriaConfig",
    # Phase 2
    "ScientificPaper",
    "Citation",
    "Figure",
    "KGNode",
    "KGEdge",
    "KGNodeType",
    "KGEdgeType",
    "ResearchGap",
    "ResearchQuestion",
    "ResearchProgram",
    "CriticReport",
    "QualityMetrics",
    "DashboardMetrics",
    "ScientificMemory",
    "KnowledgeGraph",
    "LiteratureIngestor",
    "PaperCorpus",
    "GapDetector",
    "QuestionGenerator",
    "ResearchPlanner",
    "ScientificCritic",
    "DiscoveryDashboard",
    # Phase 3
    "ExperimentPlanner",
    "InterventionGenerator",
    "CounterfactualSimulator",
    "ExperimentEvaluator",
    "MultiAgentLab",
    "PlannerAgent",
    "TheoryAgent",
    "ExperimentAgent",
    "CriticAgent",
    "ReviewerAgent",
    "SafetyAgent",
    "PaperGenerator",
    "PredictionEngine",
    "CrossDomainTransfer",
    "DataConnector",
    "Dataset",
    "ExperimentDesign",
    "ExperimentResult",
    "PaperDraft",
    "ScientificPrediction",
    "AgentRole",
    "AgentMessage",
    "DebateRound",
    "CrossDomainMapping",
    # Phase 4
    "RealDataConnector",
    "EmbodiedLab",
    "ScientificSociety",
    "CommunicationLayer",
    "EthicsLayer",
    "AdversarialScience",
    "RedTeam",
    "PredictionMarket",
    "ScientificEconomy",
    "ResearchProgramManager",
    "KnowledgeEvolution",
    "ResearchProgram",
    "Presentation",
    "GrantProposal",
    "EthicsReview",
    "MarketPrediction",
    "ResearchProgram",
    "TheoryEpoch",
    "ParadigmEvent",
    "LabDevice",
    "EmbodiedExperiment",
    "APISearchResult",
    # Phase 5
    "SelfImprovementLayer",
    "ArchitectureSearch",
    "AlgorithmDiscovery",
    "StrategyEvolution",
    "MetaCivilizationLayer",
    "MetaScienceEngine",
    "CivilizationAnalytics",
    "GoalGeneration",
    "BenchmarkGenerator",
    "SimulationWorldManager",
    "SelfModificationFramework",
    "KnowledgeCompressionEngine",
    "ArchitectureProposal",
    "AlgorithmCandidate",
    "StrategyVariant",
    "BenchmarkSpec",
    "MetaScienceFinding",
    "SimulationWorld",
    "SelfModificationProposal",
    "CompressedAbstraction",
    "ResearchAgenda",
    "CivilizationMetrics",
    # Phase 6
    "UniversalReasoningEngine",
    "KnowledgeCivilizationLayer",
    "MathematicalDiscovery",
    "SoftwareIntelligence",
    "OpenEndedLearning",
    "LongHorizonPlanning",
    "GeneralAgentSociety",
    "UniversalProblemSolver",
    "WorldModelingEngine",
    "UniversalKnowledgeFabric",
    "KnowledgeNode",
    "KnowledgeEdge",
    "ReasoningTrace",
    "MathematicalConjecture",
    "SoftwareProject",
    "CrossDomainMapping",
    "OpenEndedGoal",
    "LongHorizonPlan",
    "GeneralAgent",
    "UniversalProblem",
    "WorldModel",
]
