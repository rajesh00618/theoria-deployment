from __future__ import annotations

import uuid
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import CompressedAbstraction, Theory


class KnowledgeCompressionEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.abstractions: List[CompressedAbstraction] = []
        self.cycle_count = 0

    def compress_theories(self, theories: Dict[str, Theory]) -> CompressedAbstraction:
        theory_list = list(theories.values())
        if len(theory_list) < (getattr(self.config, 'min_source_count', 3) if self.config else 3):
            source_names = [t.name for t in theory_list]
            compressed = CompressedAbstraction(
                name=f"MetaConcept_{self.cycle_count}",
                description=f"Abstraction from {len(theory_list)} theories",
                abstraction_type="meta_concept",
                source_count=len(theory_list),
                compression_ratio=min(1.0, len(theory_list) / 10),
                source_ids=[t.id for t in theory_list],
                formal_representation=f"Union of {', '.join(source_names[:5])}",
                applicability_domains=list(set(
                    d for t in theory_list for d in (getattr(t.domain, 'conditions', []) or [])
                )) or ["general"],
                predictive_power=random.uniform(0.4, 0.8),
            )
            self.abstractions.append(compressed)
            return compressed

        clusters = self._cluster_theories(theory_list)
        cluster_key = max(clusters, key=lambda k: len(clusters[k]))
        cluster = clusters[cluster_key]

        compressed = CompressedAbstraction(
            name=f"UnifiedPrinciple_{self.cycle_count}",
            description=f"Unifying principle from {len(cluster)} related theories",
            abstraction_type="unified_principle",
            source_count=len(cluster),
            compression_ratio=len(cluster) / max(len(theory_list), 1),
            source_ids=[t.id for t in cluster],
            formal_representation=f"Generalization of {cluster[0].name} pattern",
            applicability_domains=list(set(
                d for t in cluster for d in (getattr(t.domain, 'conditions', []) or [])
            )) or ["general"],
            predictive_power=random.uniform(0.5, 0.9),
        )
        self.abstractions.append(compressed)
        return compressed

    def _cluster_theories(self, theories: List[Theory]) -> Dict[str, List[Theory]]:
        clusters: Dict[str, List[Theory]] = {}
        for t in theories:
            cluster_key = t.origin_strategy or "unknown"
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(t)
        return clusters

    def extract_research_patterns(self, theories: List[Theory]) -> CompressedAbstraction:
        tactics = {}
        for t in theories:
            strategy = t.origin_strategy or "unknown"
            if strategy not in tactics:
                tactics[strategy] = []
            tactics[strategy].append(t.name)

        dominant = max(tactics, key=lambda k: len(tactics[k]))

        pattern = CompressedAbstraction(
            name=f"ResearchPattern_{self.cycle_count}",
            description=f"Research pattern: {dominant} strategy dominant",
            abstraction_type="research_pattern",
            source_count=len(theories),
            compression_ratio=len(tactics.get(dominant, [])) / max(len(theories), 1),
            source_ids=[t.id for t in theories],
            formal_representation=f"Pattern: {dominant} -> theory",
            applicability_domains=list(set(
                getattr(t.domain, 'conditions', [])[0] if getattr(t.domain, 'conditions', None) else "general"
                for t in theories
            )) or ["general"],
            predictive_power=random.uniform(0.3, 0.7),
        )
        self.abstractions.append(pattern)
        return pattern

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_abstractions": len(self.abstractions),
            "by_type": dict((at, sum(1 for a in self.abstractions if a.abstraction_type == at))
                           for at in ["meta_concept", "unified_principle", "research_pattern"]),
            "avg_compression": np.mean([a.compression_ratio for a in self.abstractions]) if self.abstractions else 0,
            "avg_predictive_power": np.mean([a.predictive_power for a in self.abstractions]) if self.abstractions else 0,
        }
