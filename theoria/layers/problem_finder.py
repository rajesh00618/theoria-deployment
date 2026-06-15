"""
Unknown Problem Finder
======================

Actively hunts for gaps and unknown problems.

Input: Domains, Existing Knowledge
Output: Ranked list of unknown problems
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class UnknownProblem:
    """An unknown problem to investigate."""
    id: str
    domain: str
    problem: str
    description: str
    urgency: float  # 0-1, how urgent is this
    feasibility: float  # 0-1, how feasible to solve
    impact: float  # 0-1, potential impact
    evidence_count: int  # how much evidence exists
    related_work: List[str] = field(default_factory=list)


@dataclass
class ProblemSearchResult:
    """Result of problem search."""
    problems: List[UnknownProblem]
    domains_searched: int
    total_problems: int
    timestamp: float = field(default_factory=time.time)


class UnknownProblemFinder:
    """
    Actively hunts for unknown problems.
    
    Asks:
    - What important phenomena lack strong explanations?
    - What contradictions exist in current theories?
    - What predictions haven't been tested?
    - What domains are understudied?
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.problems_found: List[UnknownProblem] = []
        self.cycle_count = 0
    
    def find_problems(self, domains: List[str],
                      knowledge_bases: Optional[Dict[str, Dict]] = None) -> ProblemSearchResult:
        """
        Search for unknown problems across domains.
        
        Args:
            domains: List of domains to search
            knowledge_bases: Optional knowledge for each domain
        
        Returns:
            ProblemSearchResult with found problems
        """
        self.cycle_count += 1
        knowledge_bases = knowledge_bases or {}
        
        all_problems = []
        
        for domain in domains:
            kb = knowledge_bases.get(domain, {})
            domain_problems = self._find_for_domain(domain, kb)
            all_problems.extend(domain_problems)
        
        # Rank by urgency * impact * feasibility
        all_problems.sort(
            key=lambda p: p.urgency * p.impact * p.feasibility,
            reverse=True
        )
        
        self.problems_found.extend(all_problems)
        
        return ProblemSearchResult(
            problems=all_problems[:10],
            domains_searched=len(domains),
            total_problems=len(all_problems),
        )
    
    def _find_for_domain(self, domain: str, knowledge: Dict) -> List[UnknownProblem]:
        """Find unknown problems for a domain."""
        problems = []
        
        # Strategy 1: Find phenomena without explanations
        phenomena = knowledge.get("phenomena", [])
        theories = knowledge.get("theories", [])
        
        for p in phenomena:
            explained = any(
                p.get("name", "") in t.get("explains", [])
                for t in theories
            )
            if not explained:
                problems.append(UnknownProblem(
                    id=f"{domain}_unexplained_{len(problems)}",
                    domain=domain,
                    problem=f"Unexplained: {p.get('name', 'phenomenon')}",
                    description=f"No adequate theory explains {p.get('name', 'this')}",
                    urgency=0.8,
                    feasibility=0.6,
                    impact=0.7,
                    evidence_count=p.get("evidence_count", 0),
                ))
        
        # Strategy 2: Find contradictions
        for i, t1 in enumerate(theories):
            for t2 in theories[i+1:]:
                if self._theories_contradict(t1, t2):
                    problems.append(UnknownProblem(
                        id=f"{domain}_contradiction_{len(problems)}",
                        domain=domain,
                        problem=f"Contradiction: {t1.get('name', 'T1')} vs {t2.get('name', 'T2')}",
                        description=f"Two theories make contradictory predictions",
                        urgency=0.9,
                        feasibility=0.5,
                        impact=0.8,
                        evidence_count=0,
                        related_work=[t1.get("name", ""), t2.get("name", "")],
                    ))
        
        # Strategy 3: Find understudied areas
        if len(theories) < 3:
            problems.append(UnknownProblem(
                id=f"{domain}_understudied_{len(problems)}",
                domain=domain,
                problem=f"Understudied: {domain}",
                description=f"Only {len(theories)} theories exist for {domain}",
                urgency=0.6,
                feasibility=0.7,
                impact=0.6,
                evidence_count=len(theories),
            ))
        
        return problems
    
    def _theories_contradict(self, t1: Dict, t2: Dict) -> bool:
        """Check if theories contradict."""
        p1 = set(t1.get("predictions", []))
        p2 = set(t2.get("predictions", []))
        return bool(p1 & p2) and t1.get("mechanism") != t2.get("mechanism")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of problem finding activity."""
        return {
            "cycle_count": self.cycle_count,
            "total_problems_found": len(self.problems_found),
            "by_domain": {
                dom: sum(1 for p in self.problems_found if p.domain == dom)
                for dom in set(p.domain for p in self.problems_found)
            },
        }
