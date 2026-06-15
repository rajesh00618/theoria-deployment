"""
Knowledge Gap Detector
======================

Identifies contradictions, missing explanations, and weak evidence areas.

Input: Papers, Theories, Knowledge Graph
Output: Contradictions, Missing explanations, Weak evidence areas
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeGap:
    """A detected gap in knowledge."""
    id: str
    gap_type: str  # "contradiction", "missing_explanation", "weak_evidence", "untested_prediction"
    domain: str
    description: str
    severity: float  # 0-1, how critical is this gap
    affected_theories: List[str] = field(default_factory=list)
    suggested_research: List[str] = field(default_factory=list)
    evidence_quality: float = 0.0  # 0-1, quality of existing evidence


@dataclass
class GapDetectionResult:
    """Result of gap detection."""
    gaps: List[KnowledgeGap]
    contradictions: int
    missing_explanations: int
    weak_evidence: int
    untested_predictions: int
    overall_knowledge_quality: float
    timestamp: float = field(default_factory=time.time)


class KnowledgeGapDetector:
    """
    Detects gaps in scientific knowledge.
    
    Identifies:
    - Contradictions between theories
    - Phenomena without explanations
    - Theories with weak evidence
    - Predictions that haven't been tested
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.detected_gaps: List[KnowledgeGap] = []
        self.cycle_count = 0
    
    def detect_gaps(self, theories: List[Dict], papers: List[Dict],
                    knowledge_graph: Optional[Dict] = None) -> GapDetectionResult:
        """
        Detect gaps in knowledge.
        
        Args:
            theories: List of theory dictionaries
            papers: List of paper/literature dictionaries
            knowledge_graph: Optional knowledge graph
        
        Returns:
            GapDetectionResult with all detected gaps
        """
        self.cycle_count += 1
        all_gaps = []
        
        # Detect contradictions
        contradictions = self._detect_contradictions(theories)
        all_gaps.extend(contradictions)
        
        # Detect missing explanations
        missing = self._detect_missing_explanations(theories, knowledge_graph)
        all_gaps.extend(missing)
        
        # Detect weak evidence
        weak = self._detect_weak_evidence(theories, papers)
        all_gaps.extend(weak)
        
        # Detect untested predictions
        untested = self._detect_untested_predictions(theories)
        all_gaps.extend(untested)
        
        self.detected_gaps = all_gaps
        
        # Calculate overall knowledge quality
        if all_gaps:
            avg_severity = sum(g.severity for g in all_gaps) / len(all_gaps)
            quality = max(0.0, 1.0 - avg_severity)
        else:
            quality = 1.0
        
        return GapDetectionResult(
            gaps=all_gaps,
            contradictions=len(contradictions),
            missing_explanations=len(missing),
            weak_evidence=len(weak),
            untested_predictions=len(untested),
            overall_knowledge_quality=quality,
        )
    
    def _detect_contradictions(self, theories: List[Dict]) -> List[KnowledgeGap]:
        """Detect contradictions between theories."""
        gaps = []
        
        for i, t1 in enumerate(theories):
            for t2 in theories[i+1:]:
                if self._theories_contradict(t1, t2):
                    gap = KnowledgeGap(
                        id=f"contradiction_{len(gaps)}",
                        gap_type="contradiction",
                        domain=t1.get("domain", "unknown"),
                        description=f"Theory '{t1.get('name', 'T1')}' contradicts '{t2.get('name', 'T2')}'",
                        severity=0.8,
                        affected_theories=[t1.get("name", ""), t2.get("name", "")],
                        suggested_research=[
                            f"Design experiment to test {t1.get('name', 'T1')} vs {t2.get('name', 'T2')}",
                            "Identify which predictions differ",
                        ],
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _detect_missing_explanations(self, theories: List[Dict],
                                     knowledge_graph: Optional[Dict]) -> List[KnowledgeGap]:
        """Detect phenomena without adequate explanation."""
        gaps = []
        
        if knowledge_graph:
            phenomena = knowledge_graph.get("phenomena", [])
            for p in phenomena:
                explained = any(
                    p.get("name", "") in t.get("explains", [])
                    for t in theories
                )
                if not explained:
                    gap = KnowledgeGap(
                        id=f"missing_{len(gaps)}",
                        gap_type="missing_explanation",
                        domain=p.get("domain", "unknown"),
                        description=f"No theory explains: {p.get('name', 'phenomenon')}",
                        severity=0.7,
                        suggested_research=[
                            f"Develop theory to explain {p.get('name', 'this phenomenon')}",
                            "Review existing attempts",
                        ],
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _detect_weak_evidence(self, theories: List[Dict],
                              papers: List[Dict]) -> List[KnowledgeGap]:
        """Detect theories with weak evidence."""
        gaps = []
        
        for t in theories:
            evidence_count = t.get("evidence_count", 0)
            if evidence_count < 3:
                gap = KnowledgeGap(
                    id=f"weak_{len(gaps)}",
                    gap_type="weak_evidence",
                    domain=t.get("domain", "unknown"),
                    description=f"Theory '{t.get('name', 'T')}' has only {evidence_count} supporting papers",
                    severity=max(0.0, 1.0 - evidence_count / 5.0),
                    affected_theories=[t.get("name", "")],
                    suggested_research=[
                        f"Collect more evidence for {t.get('name', 'T')}",
                        "Design experiments to test key predictions",
                    ],
                )
                gaps.append(gap)
        
        return gaps
    
    def _detect_untested_predictions(self, theories: List[Dict]) -> List[KnowledgeGap]:
        """Detect predictions that haven't been tested."""
        gaps = []
        
        for t in theories:
            predictions = t.get("predictions", [])
            tested = t.get("tested_predictions", [])
            
            for p in predictions:
                if p not in tested:
                    gap = KnowledgeGap(
                        id=f"untested_{len(gaps)}",
                        gap_type="untested_prediction",
                        domain=t.get("domain", "unknown"),
                        description=f"Untested prediction: {p}",
                        severity=0.6,
                        affected_theories=[t.get("name", "")],
                        suggested_research=[
                            f"Design experiment to test: {p}",
                            "Collect data to verify prediction",
                        ],
                    )
                    gaps.append(gap)
        
        return gaps
    
    def _theories_contradict(self, t1: Dict, t2: Dict) -> bool:
        """Check if two theories contradict."""
        p1 = set(t1.get("predictions", []))
        p2 = set(t2.get("predictions", []))
        return bool(p1 & p2) and t1.get("mechanism") != t2.get("mechanism")
    
    def prioritize_gaps(self, gaps: List[KnowledgeGap]) -> List[KnowledgeGap]:
        """Prioritize gaps by severity and feasibility."""
        return sorted(gaps, key=lambda g: g.severity, reverse=True)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of detected gaps."""
        return {
            "cycle_count": self.cycle_count,
            "total_gaps": len(self.detected_gaps),
            "by_type": {
                "contradiction": sum(1 for g in self.detected_gaps if g.gap_type == "contradiction"),
                "missing_explanation": sum(1 for g in self.detected_gaps if g.gap_type == "missing_explanation"),
                "weak_evidence": sum(1 for g in self.detected_gaps if g.gap_type == "weak_evidence"),
                "untested_prediction": sum(1 for g in self.detected_gaps if g.gap_type == "untested_prediction"),
            },
            "avg_severity": sum(g.severity for g in self.detected_gaps) / max(len(self.detected_gaps), 1),
        }
