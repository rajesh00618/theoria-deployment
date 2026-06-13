"""
Scientific Knowledge Graph for THEORIA Phase 2.

Node Types: Concept, Theory, Experiment, Dataset, Researcher, Domain, Equation, Observation, Paper
Edge Types: supports, contradicts, derived_from, predicts, explains, tested_by, related_to, cited_by

Features: Graph storage, graph search, similarity search, concept clustering
"""

from __future__ import annotations

import time
import uuid
import json
import math
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from collections import defaultdict, Counter
from dataclasses import dataclass, field

from theoria.core.types import (
    KGNode, KGEdge, KGNodeType, KGEdgeType,
)


class KnowledgeGraph:
    """
    Persistent scientific knowledge graph.
    Stores structured scientific knowledge as a heterogeneous graph.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.nodes: Dict[str, KGNode] = {}
        self.edges: Dict[str, KGEdge] = {}

        self.node_type_index: Dict[KGNodeType, Set[str]] = defaultdict(set)
        self.edge_type_index: Dict[KGEdgeType, Set[str]] = defaultdict(set)
        self.name_to_node: Dict[str, str] = {}

        self.adjacency: Dict[str, Dict[str, float]] = defaultdict(dict)

        self.embeddings: Dict[str, np.ndarray] = {}

        self.page_ranks: Dict[str, float] = {}
        self.clusters: Dict[str, Set[str]] = {}

        self.change_log: List[Dict[str, Any]] = []

    def add_node(self, node: KGNode) -> str:
        """Add a node to the graph."""
        if node.id in self.nodes:
            old = self.nodes[node.id]
            old.properties.update(node.properties)
            if node.embedding is not None:
                old.embedding = node.embedding
            old.last_accessed = time.time()
            old.confidence = max(old.confidence, node.confidence)
            if node.source_paper_ids:
                old.source_paper_ids.extend(
                    pid for pid in node.source_paper_ids
                    if pid not in old.source_paper_ids
                )
            return node.id

        self.nodes[node.id] = node
        self.node_type_index[node.node_type].add(node.id)
        if node.name:
            self.name_to_node[node.name.lower()] = node.id

        if node.embedding is not None:
            self.embeddings[node.id] = node.embedding

        self.change_log.append({
            "type": "add_node",
            "node_id": node.id,
            "node_type": node.node_type.name,
            "timestamp": time.time(),
        })

        return node.id

    def add_edge(self, edge: KGEdge) -> str:
        """Add an edge to the graph."""
        if edge.id in self.edges:
            old = self.edges[edge.id]
            old.weight = max(old.weight, edge.weight)
            old.confidence = max(old.confidence, edge.confidence)
            if edge.evidence:
                old.evidence.extend(
                    e for e in edge.evidence if e not in old.evidence
                )
            return edge.id

        if edge.source_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_id} not found")
        if edge.target_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_id} not found")

        self.edges[edge.id] = edge
        self.edge_type_index[edge.edge_type].add(edge.id)

        self.adjacency[edge.source_id][edge.target_id] = edge.weight
        self.adjacency[edge.target_id][edge.source_id] = edge.weight

        self.nodes[edge.source_id].degree += 1
        self.nodes[edge.target_id].degree += 1

        self.change_log.append({
            "type": "add_edge",
            "edge_id": edge.id,
            "source": edge.source_id,
            "target": edge.target_id,
            "edge_type": edge.edge_type.name,
            "timestamp": time.time(),
        })

        return edge.id

    def get_node(self, node_id: str) -> Optional[KGNode]:
        """Get a node by ID."""
        node = self.nodes.get(node_id)
        if node:
            node.last_accessed = time.time()
        return node

    def get_node_by_name(self, name: str) -> Optional[KGNode]:
        """Get a node by name."""
        nid = self.name_to_node.get(name.lower())
        return self.nodes.get(nid) if nid else None

    def get_edge(self, edge_id: str) -> Optional[KGEdge]:
        """Get an edge by ID."""
        return self.edges.get(edge_id)

    def get_nodes_by_type(self, node_type: KGNodeType) -> List[KGNode]:
        """Get all nodes of a given type."""
        nids = self.node_type_index.get(node_type, set())
        return [self.nodes[nid] for nid in nids if nid in self.nodes]

    def get_edges_by_type(self, edge_type: KGEdgeType) -> List[KGEdge]:
        """Get all edges of a given type."""
        eids = self.edge_type_index.get(edge_type, set())
        return [self.edges[eid] for eid in eids if eid in self.edges]

    def get_neighbors(self, node_id: str,
                      edge_type: Optional[KGEdgeType] = None) -> List[Tuple[str, KGEdge]]:
        """Get neighbors of a node, optionally filtered by edge type."""
        neighbors = []
        for edge in self.edges.values():
            if edge.source_id == node_id or edge.target_id == node_id:
                if edge_type and edge.edge_type != edge_type:
                    continue
                other_id = edge.target_id if edge.source_id == node_id else edge.source_id
                neighbors.append((other_id, edge))
        return neighbors

    def query(self, query_type: Optional[KGNodeType] = None,
              name_contains: Optional[str] = None,
              min_confidence: float = 0.0,
              min_degree: int = 0,
              top_k: int = 100) -> List[KGNode]:
        """Query nodes with filters."""
        results = []
        for node in self.nodes.values():
            if query_type and node.node_type != query_type:
                continue
            if name_contains and name_contains.lower() not in node.name.lower():
                continue
            if node.confidence < min_confidence:
                continue
            if node.degree < min_degree:
                continue
            results.append(node)

        results.sort(key=lambda n: n.page_rank, reverse=True)

        return results[:top_k]

    def similarity_search(self, query_embedding: np.ndarray,
                          top_k: int = 10,
                          node_type: Optional[KGNodeType] = None) -> List[Tuple[str, float]]:
        """Find nodes with similar embeddings."""
        if not self.embeddings:
            return []

        scores = []
        for nid, emb in self.embeddings.items():
            if node_type and self.nodes.get(nid, {}).node_type != node_type:
                continue

            if emb.shape != query_embedding.shape:
                continue
            sim = float(np.dot(emb, query_embedding) /
                       (np.linalg.norm(emb) * np.linalg.norm(query_embedding) + 1e-10))
            scores.append((nid, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def compute_page_rank(self, damping: float = 0.85,
                          max_iter: int = 100,
                          tol: float = 1e-6) -> Dict[str, float]:
        """Compute PageRank scores for all nodes."""
        n_nodes = len(self.nodes)
        if n_nodes == 0:
            return {}

        ranks = {nid: 1.0 / n_nodes for nid in self.nodes}
        for _ in range(max_iter):
            new_ranks = {}
            dangling = sum(ranks[nid] for nid in self.nodes
                          if len(self.adjacency.get(nid, {})) == 0)

            for nid in self.nodes:
                rank = (1.0 - damping) / n_nodes
                rank += damping * dangling / n_nodes

                for source_id, neighbors in self.adjacency.items():
                    if nid in neighbors:
                        degree = max(len(neighbors), 1)
                        rank += damping * ranks[source_id] / degree

                new_ranks[nid] = rank

            diff = sum(abs(new_ranks[nid] - ranks[nid]) for nid in self.nodes)
            ranks = new_ranks
            if diff < tol:
                break

        norm = sum(ranks.values())
        if norm > 0:
            for nid in ranks:
                ranks[nid] /= norm

        for nid, pr in ranks.items():
            if nid in self.nodes:
                self.nodes[nid].page_rank = pr

        self.page_ranks = ranks
        return ranks

    def cluster_concepts(self, epsilon: float = 0.5,
                         min_cluster_size: int = 3) -> Dict[str, Set[str]]:
        """Cluster nodes using embedding similarity."""
        if len(self.embeddings) < min_cluster_size:
            return {}

        nids = list(self.embeddings.keys())
        assigned: Set[str] = set()
        clusters: Dict[str, Set[str]] = {}

        for i, nid in enumerate(nids):
            if nid in assigned:
                continue
            cluster_id = f"cluster_{len(clusters)}"
            cluster = {nid}
            assigned.add(nid)

            for j in range(i + 1, len(nids)):
                other = nids[j]
                if other in assigned:
                    continue
                emb_i = self.embeddings[nid]
                emb_j = self.embeddings[other]
                sim = float(np.dot(emb_i, emb_j) /
                           (np.linalg.norm(emb_i) * np.linalg.norm(emb_j) + 1e-10))
                if sim >= (1.0 - epsilon):
                    cluster.add(other)
                    assigned.add(other)

            if len(cluster) >= min_cluster_size:
                clusters[cluster_id] = cluster
                for cid in cluster:
                    if cid in self.nodes:
                        self.nodes[cid].cluster_id = cluster_id

        self.clusters = clusters
        return clusters

    def find_paths(self, source_id: str, target_id: str,
                   max_depth: int = 4) -> List[List[Tuple[str, str, str]]]:
        """Find paths between two nodes (BFS)."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return []

        visited: Set[str] = {source_id}
        queue: List[Tuple[str, List[Tuple[str, str, str]]]] = [
            (source_id, [])
        ]

        paths = []

        while queue and len(paths) < 10:
            current, path = queue.pop(0)
            if len(path) >= max_depth:
                continue

            for edge in self.edges.values():
                next_id = None
                if edge.source_id == current:
                    next_id = edge.target_id
                elif edge.target_id == current:
                    next_id = edge.source_id

                if next_id and next_id not in visited:
                    new_path = path + [(current, next_id, edge.edge_type.name)]
                    if next_id == target_id:
                        paths.append(new_path)
                    else:
                        visited.add(next_id)
                        queue.append((next_id, new_path))

        return paths

    def get_subgraph(self, node_ids: Set[str],
                     max_depth: int = 1) -> Tuple[Dict[str, KGNode], Dict[str, KGEdge]]:
        """Extract a subgraph around given nodes within depth."""
        included_nodes: Set[str] = set(node_ids)
        included_edges: Dict[str, KGEdge] = {}

        frontier = set(node_ids)
        for _ in range(max_depth):
            new_frontier = set()
            for edge in self.edges.values():
                if edge.source_id in frontier or edge.target_id in frontier:
                    included_edges[edge.id] = edge
                    if edge.source_id not in included_nodes:
                        new_frontier.add(edge.source_id)
                    if edge.target_id not in included_nodes:
                        new_frontier.add(edge.target_id)
            included_nodes.update(new_frontier)
            frontier = new_frontier
            if not frontier:
                break

        return (
            {nid: self.nodes[nid] for nid in included_nodes if nid in self.nodes},
            included_edges,
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": {
                nt.name: len(nids)
                for nt, nids in self.node_type_index.items()
            },
            "edge_types": {
                et.name: len(eids)
                for et, eids in self.edge_type_index.items()
            },
            "clusters": len(self.clusters),
            "embeddings_stored": len(self.embeddings),
            "avg_degree": (
                sum(n.degree for n in self.nodes.values()) / max(len(self.nodes), 1)
            ),
            "changes_logged": len(self.change_log),
        }
