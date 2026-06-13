"""
Phase 2: Research Gap Detection Engine.

Identifies areas where knowledge is incomplete using:
- Missing links in graph
- Contradictory evidence
- Weakly supported theories
- Unexplored concept combinations
- Sparse citation regions
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

from theoria.core.types import (
    ResearchGap, KGNode, KGEdge, KGNodeType, KGEdgeType, Theory, Evidence,
    TheoryStatus,
)
from theoria.core.knowledge_graph import KnowledgeGraph


class GapDetector:
    """
    Detects knowledge gaps in the scientific knowledge graph.
    Uses multiple detection strategies for comprehensive coverage.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.gaps: List[ResearchGap] = []
        self.detection_counts: Dict[str, int] = defaultdict(int)

    def detect_all(self, kg: KnowledgeGraph,
                   theories: Optional[List[Theory]] = None,
                   max_gaps: int = 20) -> List[ResearchGap]:
        """Run all gap detection methods."""
        self.gaps = []
        config = self.config

        if config is None or config.enable_missing_link:
            self._detect_missing_links(kg)
        if config is None or config.enable_contradiction:
            self._detect_contradictions(kg)
        if config is None or config.enable_weak_support:
            self._detect_weak_support(kg, theories or [])
        if config is None or config.enable_unexplored_combinations:
            self._detect_unexplored_combinations(kg)
        if config is None or config.enable_sparse_citation:
            self._detect_sparse_citations(kg)

        min_score = config.min_gap_score if config else 0.3
        self.gaps = [g for g in self.gaps if g.overall_score >= min_score]
        self.gaps.sort(key=lambda g: g.overall_score, reverse=True)

        return self.gaps[:max_gaps]

    def _detect_missing_links(self, kg: KnowledgeGraph) -> None:
        """Detect missing edges between closely related nodes."""
        concept_nodes = kg.get_nodes_by_type(KGNodeType.CONCEPT)
        if len(concept_nodes) < 3:
            return

        for i, node_a in enumerate(concept_nodes):
            for j in range(i + 1, len(concept_nodes)):
                node_b = concept_nodes[j]

                if not kg.adjacency.get(node_a.id, {}).get(node_b.id):
                    shared_papers = set(node_a.source_paper_ids) & set(node_b.source_paper_ids)
                    shared_neighbors = set(
                        nid for nid, _ in kg.get_neighbors(node_a.id)
                    ) & set(
                        nid for nid, _ in kg.get_neighbors(node_b.id)
                    )

                    domain_a = node_a.properties.get("domain", "")
                    domain_b = node_b.properties.get("domain", "")
                    same_domain = domain_a and domain_b and domain_a == domain_b

                    link_score = 0.0
                    if shared_papers:
                        link_score += 0.3 * min(len(shared_papers) / 3.0, 1.0)
                    if shared_neighbors:
                        link_score += 0.2 * min(len(shared_neighbors) / 5.0, 1.0)
                    if same_domain:
                        link_score += 0.15

                    if link_score > 0.1:
                        gap = ResearchGap(
                            id=f"missing_link_{i}_{j}_{int(time.time())}",
                            description=(
                                f"Missing link between '{node_a.name}' and '{node_b.name}': "
                                f"concepts appear together but relationship is unexplored"
                            ),
                            detection_method="missing_link",
                            detection_source="GapDetector",
                            involved_nodes=[node_a.id, node_b.id],
                            importance=min(link_score + 0.3, 1.0),
                            tractability=0.6,
                            novelty=min(link_score + 0.4, 1.0),
                        )
                        gap.overall_score = (
                            0.4 * gap.importance + 0.3 * gap.tractability + 0.3 * gap.novelty
                        )
                        self.gaps.append(gap)
                        self.detection_counts["missing_link"] += 1

    def _detect_contradictions(self, kg: KnowledgeGraph) -> None:
        """Detect contradictory evidence in the graph."""
        contradicts_edges = kg.get_edges_by_type(KGEdgeType.CONTRADICTS)
        for edge in contradicts_edges:
            source_node = kg.get_node(edge.source_id)
            target_node = kg.get_node(edge.target_id)
            if source_node and target_node:
                gap = ResearchGap(
                    id=f"contradiction_{edge.id}_{int(time.time())}",
                    description=(
                        f"Contradictory evidence between '{source_node.name}' "
                        f"and '{target_node.name}': resolution needed"
                    ),
                    detection_method="contradiction",
                    detection_source="GapDetector",
                    involved_nodes=[edge.source_id, edge.target_id],
                    involved_edges=[edge.id],
                    importance=min(edge.weight * 0.8 + 0.3, 1.0),
                    tractability=0.5,
                    novelty=0.6,
                )
                gap.overall_score = (
                    0.4 * gap.importance + 0.3 * gap.tractability + 0.3 * gap.novelty
                )
                self.gaps.append(gap)
                self.detection_counts["contradiction"] += 1

    def _detect_weak_support(self, kg: KnowledgeGraph,
                              theories: List[Theory]) -> None:
        """Detect theories with weak empirical support."""
        for theory in theories:
            weak = False
            reasons = []

            if theory.posterior < 0.4:
                weak = True
                reasons.append(f"low posterior ({theory.posterior:.2f})")

            if len(theory.severity_records) < 2:
                weak = True
                reasons.append("insufficient severe tests")

            if theory.status in (TheoryStatus.PROPOSED, TheoryStatus.FORMALIZING):
                weak = True
                reasons.append("never fully formalized")

            if weak:
                theory_node = kg.get_node_by_name(theory.name)
                involved = [theory_node.id] if theory_node else []

                gap = ResearchGap(
                    id=f"weak_support_{theory.id}_{int(time.time())}",
                    description=(
                        f"Weakly supported theory '{theory.name}': "
                        f"{'; '.join(reasons)}"
                    ),
                    detection_method="weak_support",
                    detection_source="GapDetector",
                    involved_nodes=involved,
                    importance=0.7,
                    tractability=0.7,
                    novelty=0.4,
                )
                gap.overall_score = (
                    0.4 * gap.importance + 0.3 * gap.tractability + 0.3 * gap.novelty
                )
                self.gaps.append(gap)
                self.detection_counts["weak_support"] += 1

    def _detect_unexplored_combinations(self, kg: KnowledgeGraph) -> None:
        """Detect unexplored combinations of concepts from different domains."""
        concept_nodes = kg.get_nodes_by_type(KGNodeType.CONCEPT)
        if len(concept_nodes) < 4:
            return

        domain_nodes: Dict[str, List[KGNode]] = defaultdict(list)
        for node in concept_nodes:
            domain = node.properties.get("domain", "unknown")
            domain_nodes[domain].append(node)

        domains = list(domain_nodes.keys())
        if len(domains) < 2:
            return

        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                d1_nodes = domain_nodes[domains[i]]
                d2_nodes = domain_nodes[domains[j]]

                for a in d1_nodes[:3]:
                    for b in d2_nodes[:3]:
                        if not kg.adjacency.get(a.id, {}).get(b.id):
                            gap = ResearchGap(
                                id=f"unexplored_{a.id}_{b.id}_{int(time.time())}",
                                description=(
                                    f"Unexplored combination: '{a.name}' ({domains[i]}) "
                                    f"x '{b.name}' ({domains[j]}): "
                                    f"potential cross-domain interaction"
                                ),
                                detection_method="unexplored_combinations",
                                detection_source="GapDetector",
                                involved_nodes=[a.id, b.id],
                                importance=0.5,
                                tractability=0.4,
                                novelty=0.8,
                            )
                            gap.overall_score = (
                                0.4 * gap.importance + 0.3 * gap.tractability + 0.3 * gap.novelty
                            )
                            self.gaps.append(gap)
                            self.detection_counts["unexplored_combinations"] += 1

    def _detect_sparse_citations(self, kg: KnowledgeGraph) -> None:
        """Detect research areas with sparse citation networks."""
        paper_nodes = kg.get_nodes_by_type(KGNodeType.PAPER)
        if len(paper_nodes) < 5:
            return

        for node in paper_nodes:
            citation_count = len(node.source_paper_ids)
            neighbors = kg.get_neighbors(node.id)
            connection_count = len(neighbors)

            if citation_count < 3 and connection_count < 3:
                gap = ResearchGap(
                    id=f"sparse_{node.id}_{int(time.time())}",
                    description=(
                        f"Sparse citation region around '{node.name[:80]}': "
                        f"only {citation_count} citations and {connection_count} connections"
                    ),
                    detection_method="sparse_citation",
                    detection_source="GapDetector",
                    involved_nodes=[node.id],
                    importance=0.4,
                    tractability=0.5,
                    novelty=0.5,
                )
                gap.overall_score = (
                    0.4 * gap.importance + 0.3 * gap.tractability + 0.3 * gap.novelty
                )
                self.gaps.append(gap)
                self.detection_counts["sparse_citation"] += 1

    def rank_gaps(self, gaps: List[ResearchGap]) -> List[ResearchGap]:
        """Rank gaps by overall score."""
        return sorted(gaps, key=lambda g: g.overall_score, reverse=True)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_gaps_detected": len(self.gaps),
            "by_method": dict(self.detection_counts),
            "top_gaps": [
                {
                    "id": g.id,
                    "description": g.description[:100],
                    "score": g.overall_score,
                    "method": g.detection_method,
                }
                for g in sorted(self.gaps, key=lambda x: x.overall_score, reverse=True)[:5]
            ],
        }
