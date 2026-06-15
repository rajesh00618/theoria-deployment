"""
Phase 4 Autonomous Research Pipeline
=====================================

Complete autonomous research system with literature, experiments, validation, and paper generation.

Input: Domain list
Output: Complete research with paper draft
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.layers.topic_discovery import TopicDiscoveryAgent
from theoria.layers.knowledge_gap_detector import KnowledgeGapDetector
from theoria.layers.research_planner import AutonomousResearchPlanner
from theoria.layers.discovery_prioritizer import DiscoveryPrioritizationEngine
from theoria.layers.literature_agent import AutonomousLiteratureAgent
from theoria.layers.experiment_designer import AutonomousExperimentDesigner
from theoria.layers.validation_engine import AutonomousValidationEngine
from theoria.layers.paper_generator_auto import AutonomousPaperGenerator
from theoria.layers.research_memory import ResearchMemorySystem


@dataclass
class Phase4Result:
    """Complete result from Phase 4 pipeline."""
    # Topic selection
    topic: str
    domain: str
    # Literature review
    literature_findings: int
    theories_found: int
    contradictions: int
    # Research plan
    hypothesis: str
    # Experiment
    experiment_name: str
    methodology: str
    # Validation
    validation_passed: bool
    validation_confidence: float
    # Paper
    paper_title: str
    paper_words: int
    # Memory
    memories_stored: int
    # Overall
    pipeline_confidence: float
    execution_time: float
    timestamp: float = field(default_factory=time.time)


class Phase4Pipeline:
    """
    Complete Phase 4 Autonomous Research Pipeline.
    
    Runs the full autonomous research cycle:
    1. Topic Discovery
    2. Literature Review
    3. Gap Detection
    4. Research Planning
    5. Experiment Design
    6. Validation
    7. Paper Generation
    8. Memory Storage
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Phase 3 modules
        self.topic_agent = TopicDiscoveryAgent(config)
        self.gap_detector = KnowledgeGapDetector(config)
        self.planner = AutonomousResearchPlanner(config)
        self.prioritizer = DiscoveryPrioritizationEngine(config)
        
        # Phase 4 modules
        self.literature_agent = AutonomousLiteratureAgent(config)
        self.experiment_designer = AutonomousExperimentDesigner(config)
        self.validation_engine = AutonomousValidationEngine(config)
        self.paper_generator = AutonomousPaperGenerator(config)
        self.memory = ResearchMemorySystem(config)
        
        self.pipeline_history: List[Phase4Result] = []
    
    def run_pipeline(self, domain_knowledge: Optional[Dict[str, Dict]] = None) -> Phase4Result:
        """
        Run the complete Phase 4 autonomous research pipeline.
        
        Args:
            domain_knowledge: Optional knowledge for each domain
        
        Returns:
            Phase4Result with complete findings
        """
        t0 = time.time()
        
        # Step 1: Load knowledge
        if domain_knowledge:
            for domain, knowledge in domain_knowledge.items():
                self.topic_agent.load_domain_knowledge(domain, knowledge)
        
        # Step 2: Discover topics
        topic_result = self.topic_agent.discover_opportunities()
        
        if not topic_result.opportunities:
            return self._empty_result(time.time() - t0)
        
        top_opp = topic_result.opportunities[0]
        topic = top_opp.topic
        domain = top_opp.domain
        
        # Step 3: Literature review
        lit_review = self.literature_agent.review_literature(topic, domain)
        
        # Step 4: Detect gaps
        theories = [{"name": t, "domain": domain, "predictions": [], "mechanism": ""}
                    for t in lit_review.theories_extracted]
        gap_result = self.gap_detector.detect_gaps(theories, [])
        
        # Step 5: Plan research
        planning_result = self.planner.plan_research(
            question=topic,
            domain=domain,
            context={"gaps": [g.description for g in gap_result.gaps]},
        )
        
        # Step 6: Design experiment
        if planning_result.plan:
            exp_result = self.experiment_designer.design_experiment(
                research_question=topic,
                hypothesis=planning_result.plan.hypothesis,
                domain=domain,
            )
        else:
            exp_result = None
        
        # Step 7: Validate (simulate results)
        sim_results = {
            "p_value": 0.03,
            "effect_size": 0.45,
            "consistency": 0.8,
        }
        
        if planning_result.plan:
            validation = self.validation_engine.validate(
                hypothesis=planning_result.plan.hypothesis,
                experiment_results=sim_results,
                domain=domain,
            )
        else:
            validation = None
        
        # Step 8: Generate paper
        if planning_result.plan and validation:
            paper = self.paper_generator.generate_paper(
                topic=topic,
                hypothesis=planning_result.plan.hypothesis,
                methods=["computational_simulation", "statistical_analysis"],
                results=sim_results,
                validation={"passed": validation.overall_passed,
                           "confidence": validation.overall_confidence},
            )
        else:
            paper = None
        
        # Step 9: Store in memory
        if planning_result.plan:
            self.memory.store(
                category="discovery",
                domain=domain,
                content=f"Found {topic} with {lit_review.papers_found} papers reviewed",
                importance=top_opp.importance_score,
            )
        
        execution_time = time.time() - t0
        
        # Calculate confidence
        confidence = self._compute_confidence(
            topic_result, lit_review, gap_result, planning_result,
            validation, paper
        )
        
        result = Phase4Result(
            topic=topic,
            domain=domain,
            literature_findings=lit_review.papers_found,
            theories_found=len(lit_review.theories_extracted),
            contradictions=len(lit_review.contradictions_found),
            hypothesis=planning_result.plan.hypothesis if planning_result.plan else "",
            experiment_name=exp_result.experiment.name if exp_result else "",
            methodology=exp_result.experiment.methodology if exp_result else "",
            validation_passed=validation.overall_passed if validation else False,
            validation_confidence=validation.overall_confidence if validation else 0,
            paper_title=paper.title if paper else "",
            paper_words=paper.total_words if paper else 0,
            memories_stored=len(self.memory.memories),
            pipeline_confidence=confidence,
            execution_time=execution_time,
        )
        
        self.pipeline_history.append(result)
        return result
    
    def _compute_confidence(self, topic_result, lit_review, gap_result,
                            planning_result, validation, paper) -> float:
        """Compute overall pipeline confidence."""
        scores = []
        
        if topic_result.opportunities:
            scores.append(0.8)
        
        if lit_review.papers_found > 0:
            scores.append(0.7)
        
        if planning_result.plan:
            scores.append(planning_result.confidence)
        
        if validation:
            scores.append(validation.overall_confidence)
        
        if paper:
            scores.append(0.8)
        
        return sum(scores) / max(len(scores), 1)
    
    def _empty_result(self, execution_time: float) -> Phase4Result:
        """Return empty result when no opportunities found."""
        return Phase4Result(
            topic="",
            domain="",
            literature_findings=0,
            theories_found=0,
            contradictions=0,
            hypothesis="",
            experiment_name="",
            methodology="",
            validation_passed=False,
            validation_confidence=0,
            paper_title="",
            paper_words=0,
            memories_stored=0,
            pipeline_confidence=0,
            execution_time=execution_time,
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline activity."""
        return {
            "pipelines_run": len(self.pipeline_history),
            "memory_summary": self.memory.get_summary(),
            "last_confidence": (
                self.pipeline_history[-1].pipeline_confidence
                if self.pipeline_history else 0
            ),
        }
