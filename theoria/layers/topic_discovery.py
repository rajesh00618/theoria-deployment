"""
Topic Discovery Agent
=====================

Automatically identifies research opportunities across domains.

Input: All available domains
Output: Top 10 research opportunities ranked by novelty and importance
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ResearchOpportunity:
    """A discovered research opportunity."""
    id: str
    domain: str
    topic: str
    description: str
    novelty_score: float  # 0-1, how new is this
    importance_score: float  # 0-1, how significant
    feasibility_score: float  # 0-1, how achievable
    evidence_gaps: List[str] = field(default_factory=list)
    related_theories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)


@dataclass
class TopicDiscoveryResult:
    """Result of topic discovery."""
    opportunities: List[ResearchOpportunity]
    domains_scanned: int
    total_opportunities: int
    timestamp: float = field(default_factory=time.time)


class TopicDiscoveryAgent:
    """
    Discovers research opportunities across domains.
    
    Uses heuristics to identify:
    - Under-studied areas
    - Contradictions in existing theories
    - Novel combinations of concepts
    - Predictions that haven't been tested
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.domains = [
            "physics", "biology", "neuroscience", "psychology",
            "economics", "sociology", "computer_science", "mathematics",
            "philosophy", "chemistry", "ecology", "medicine",
        ]
        self.domain_knowledge: Dict[str, Dict[str, Any]] = {}
        self.discovered_opportunities: List[ResearchOpportunity] = []
        self.cycle_count = 0
    
    def load_domain_knowledge(self, domain: str, knowledge: Dict[str, Any]) -> None:
        """Load existing knowledge for a domain."""
        self.domain_knowledge[domain] = knowledge
    
    def discover_opportunities(self, max_per_domain: int = 3) -> TopicDiscoveryResult:
        """
        Discover research opportunities across all domains.
        
        Returns top opportunities ranked by combined score.
        """
        self.cycle_count += 1
        all_opportunities = []
        
        for domain in self.domains:
            domain_opps = self._discover_for_domain(domain, max_per_domain)
            all_opportunities.extend(domain_opps)
        
        # Rank by combined score
        all_opportunities.sort(
            key=lambda o: o.novelty_score * 0.4 + o.importance_score * 0.4 + o.feasibility_score * 0.2,
            reverse=True
        )
        
        self.discovered_opportunities = all_opportunities
        
        return TopicDiscoveryResult(
            opportunities=all_opportunities[:10],
            domains_scanned=len(self.domains),
            total_opportunities=len(all_opportunities),
        )
    
    def _discover_for_domain(self, domain: str, max_opps: int) -> List[ResearchOpportunity]:
        """Discover opportunities for a single domain."""
        opportunities = []
        knowledge = self.domain_knowledge.get(domain, {})
        
        # Strategy 1: Contradictions
        contradictions = self._find_contradictions(domain, knowledge)
        opportunities.extend(contradictions[:1])
        
        # Strategy 2: Missing explanations
        gaps = self._find_explanation_gaps(domain, knowledge)
        opportunities.extend(gaps[:1])
        
        # Strategy 3: Novel combinations
        novel = self._find_novel_combinations(domain, knowledge)
        opportunities.extend(novel[:1])
        
        return opportunities[:max_opps]
    
    def _find_contradictions(self, domain: str, knowledge: Dict) -> List[ResearchOpportunity]:
        """Find contradictions in existing theories."""
        theories = knowledge.get("theories", [])
        contradictions = []
        
        for i, t1 in enumerate(theories):
            for t2 in theories[i+1:]:
                if self._theories_contradict(t1, t2):
                    opp = ResearchOpportunity(
                        id=f"{domain}_contradiction_{len(contradictions)}",
                        domain=domain,
                        topic=f"Contradiction between {t1.get('name', 'T1')} and {t2.get('name', 'T2')}",
                        description=f"Two theories in {domain} make contradictory predictions",
                        novelty_score=0.7,
                        importance_score=0.8,
                        feasibility_score=0.6,
                        evidence_gaps=["Which theory is correct?", "What evidence would resolve?"],
                        related_theories=[t1.get('name', ''), t2.get('name', '')],
                    )
                    contradictions.append(opp)
        
        return contradictions
    
    def _find_explanation_gaps(self, domain: str, knowledge: Dict) -> List[ResearchOpportunity]:
        """Find phenomena without adequate explanation."""
        phenomena = knowledge.get("phenomena", [])
        theories = knowledge.get("theories", [])
        
        gaps = []
        for p in phenomena:
            explained = any(
                self._theory_explains(t, p) for t in theories
            )
            if not explained:
                opp = ResearchOpportunity(
                    id=f"{domain}_gap_{len(gaps)}",
                    domain=domain,
                    topic=f"Unexplained: {p.get('name', 'phenomenon')}",
                    description=f"No adequate theory explains {p.get('name', 'this phenomenon')}",
                    novelty_score=0.8,
                    importance_score=0.7,
                    feasibility_score=0.5,
                    evidence_gaps=[f"What mechanism causes {p.get('name', 'this')}?"],
                )
                gaps.append(opp)
        
        return gaps
    
    def _find_novel_combinations(self, domain: str, knowledge: Dict) -> List[ResearchOpportunity]:
        """Find novel combinations of existing concepts."""
        concepts = knowledge.get("concepts", [])
        combinations = []
        
        if len(concepts) >= 2:
            for i, c1 in enumerate(concepts[:5]):
                for c2 in concepts[i+1:i+3]:
                    if not self._concepts_already_combined(c1, c2, knowledge):
                        opp = ResearchOpportunity(
                            id=f"{domain}_novel_{len(combinations)}",
                            domain=domain,
                            topic=f"Novel combination: {c1.get('name', '')} + {c2.get('name', '')}",
                            description=f"Combining {c1.get('name', '')} with {c2.get('name', '')} may yield new insights",
                            novelty_score=0.9,
                            importance_score=0.5,
                            feasibility_score=0.7,
                            keywords=[c1.get('name', ''), c2.get('name', '')],
                        )
                        combinations.append(opp)
        
        return combinations
    
    def _theories_contradict(self, t1: Dict, t2: Dict) -> bool:
        """Check if two theories contradict each other."""
        p1 = set(t1.get("predictions", []))
        p2 = set(t2.get("predictions", []))
        return bool(p1 & p2) and t1.get("mechanism") != t2.get("mechanism")
    
    def _theory_explains(self, theory: Dict, phenomenon: Dict) -> bool:
        """Check if a theory explains a phenomenon."""
        explained = phenomenon.get("name", "") in theory.get("explains", [])
        return explained
    
    def _concepts_already_combined(self, c1: Dict, c2: Dict, knowledge: Dict) -> bool:
        """Check if two concepts have already been combined."""
        existing = knowledge.get("existing_combinations", [])
        pair = {c1.get("name", ""), c2.get("name", "")}
        return any(set(combo) == pair for combo in existing)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of discoveries."""
        return {
            "cycle_count": self.cycle_count,
            "domains_scanned": len(self.domains),
            "total_opportunities": len(self.discovered_opportunities),
            "top_3": [
                {"topic": o.topic, "score": o.novelty_score * 0.4 + o.importance_score * 0.4 + o.feasibility_score * 0.2}
                for o in self.discovered_opportunities[:3]
            ],
        }
