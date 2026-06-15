"""
Autonomous Research Pipeline
=============================

Ties together all Phase 3 modules into a complete autonomous research system.

Input: Domain list
Output: Complete research plan without human guidance
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.layers.topic_discovery import TopicDiscoveryAgent, TopicDiscoveryResult
from theoria.layers.knowledge_gap_detector import KnowledgeGapDetector, GapDetectionResult
from theoria.layers.research_planner import AutonomousResearchPlanner, PlanningResult
from theoria.layers.discovery_prioritizer import DiscoveryPrioritizationEngine, PrioritizationResult


@dataclass
class AutonomousResearchResult:
    """Complete result from autonomous research pipeline."""
    # Step 1: Topic Discovery
    topic_result: TopicDiscoveryResult
    # Step 2: Gap Detection
    gap_result: GapDetectionResult
    # Step 3: Planning
    planning_result: PlanningResult
    # Step 4: Prioritization
    prioritization_result: PrioritizationResult
    # Overall
    pipeline_confidence: float
    execution_time: float
    timestamp: float = field(default_factory=time.time)


class AutonomousResearchPipeline:
    """
    Complete autonomous research pipeline.
    
    Runs the full cycle:
    1. Discover topics
    2. Detect gaps
    3. Plan research
    4. Prioritize discoveries
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.topic_agent = TopicDiscoveryAgent(config)
        self.gap_detector = KnowledgeGapDetector(config)
        self.research_planner = AutonomousResearchPlanner(config)
        self.prioritizer = DiscoveryPrioritizationEngine(config)
        self.pipeline_history: List[AutonomousResearchResult] = []
    
    def run_pipeline(self, domain_knowledge: Optional[Dict[str, Dict]] = None) -> AutonomousResearchResult:
        """
        Run the complete autonomous research pipeline.
        
        Args:
            domain_knowledge: Optional knowledge for each domain
        
        Returns:
            AutonomousResearchResult with complete findings
        """
        t0 = time.time()
        
        # Step 1: Load knowledge if provided
        if domain_knowledge:
            for domain, knowledge in domain_knowledge.items():
                self.topic_agent.load_domain_knowledge(domain, knowledge)
        
        # Step 2: Discover topics
        topic_result = self.topic_agent.discover_opportunities()
        
        # Step 3: Detect gaps using discovered topics
        theories = []
        for opp in topic_result.opportunities:
            theories.append({
                "name": opp.topic,
                "domain": opp.domain,
                "predictions": [],
                "mechanism": opp.description,
            })
        gap_result = self.gap_detector.detect_gaps(theories, [])
        
        # Step 4: Plan research for top opportunity
        if topic_result.opportunities:
            top_opp = topic_result.opportunities[0]
            planning_result = self.research_planner.plan_research(
                question=top_opp.topic,
                domain=top_opp.domain,
                context={"gaps": [g.description for g in gap_result.gaps]},
            )
        else:
            planning_result = PlanningResult(
                plan=None,
                confidence=0.0,
                alternatives_count=0,
            )
        
        # Step 5: Prioritize all opportunities
        opp_dicts = [
            {
                "id": o.id,
                "domain": o.domain,
                "topic": o.topic,
                "novelty_score": o.novelty_score,
                "importance_score": o.importance_score,
                "feasibility_score": o.feasibility_score,
            }
            for o in topic_result.opportunities
        ]
        prioritization_result = self.prioritizer.prioritize(opp_dicts)
        
        execution_time = time.time() - t0
        
        # Calculate overall confidence
        pipeline_confidence = self._compute_confidence(
            topic_result, gap_result, planning_result, prioritization_result
        )
        
        result = AutonomousResearchResult(
            topic_result=topic_result,
            gap_result=gap_result,
            planning_result=planning_result,
            prioritization_result=prioritization_result,
            pipeline_confidence=pipeline_confidence,
            execution_time=execution_time,
        )
        
        self.pipeline_history.append(result)
        return result
    
    def _compute_confidence(self, topic_result, gap_result,
                            planning_result, prioritization_result) -> float:
        """Compute overall pipeline confidence."""
        scores = []
        
        if topic_result.opportunities:
            scores.append(min(1.0, len(topic_result.opportunities) / 10))
        
        if gap_result.gaps:
            scores.append(gap_result.overall_knowledge_quality)
        
        if planning_result.plan:
            scores.append(planning_result.confidence)
        
        if prioritization_result.ranked_discoveries:
            scores.append(0.8)
        
        return sum(scores) / max(len(scores), 1)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of pipeline activity."""
        return {
            "pipelines_run": len(self.pipeline_history),
            "topic_agent": self.topic_agent.get_summary(),
            "gap_detector": self.gap_detector.get_summary(),
            "research_planner": self.research_planner.get_summary(),
            "prioritizer": self.prioritizer.get_summary(),
            "last_confidence": (
                self.pipeline_history[-1].pipeline_confidence
                if self.pipeline_history else 0
            ),
        }
