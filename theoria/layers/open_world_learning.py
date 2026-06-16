from __future__ import annotations

import uuid
import hashlib
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import OpenWorldLearningRecord


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class OpenWorldLearningResult:
    records_created: int = 0
    sources_used: int = 0
    contradictions_detected: int = 0
    beliefs_revised: int = 0
    avg_confidence: float = 0.0


class OpenWorldLearningEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.records: List[OpenWorldLearningRecord] = []
        self.sources = ["internet", "documents", "humans", "sensors", "experiments", "software_systems", "organizations"]
        self.beliefs: Dict[str, float] = {}
        self.cycle_count = 0

    def learn_from_source(self, source_type: str, fact: str) -> OpenWorldLearningRecord:
        confidence = 0.3 + _det_score(f"conf_{source_type}_{fact}_{self.cycle_count}") * 0.65
        record = OpenWorldLearningRecord(
            source_type=source_type,
            source_description=f"learned from {source_type} at cycle {self.cycle_count}",
            fact_discovered=fact,
            confidence=confidence,
            verified=confidence > 0.6,
        )
        self.records.append(record)
        self.beliefs[fact] = confidence
        return record

    def detect_contradictions(self) -> List[OpenWorldLearningRecord]:
        contradictions = []
        for i, r1 in enumerate(self.records):
            for r2 in self.records[i + 1:]:
                if r1.confidence > 0.5 and r2.confidence > 0.5:
                    if random.random() < 0.1:
                        r1.contradiction_with.append(r2.id)
                        r2.contradiction_with.append(r1.id)
                        contradictions.append(r1)
                        contradictions.append(r2)
        seen = set()
        unique = []
        for c in contradictions:
            if c.id not in seen:
                seen.add(c.id)
                unique.append(c)
        return unique

    def revise_beliefs(self, contradictions: List[OpenWorldLearningRecord]) -> int:
        revised = 0
        for record in contradictions:
            if record in self.records and record.confidence < 0.5:
                self.beliefs[record.fact_discovered] = record.confidence * 0.5
                revised += 1
        return revised

    def run_cycle(self) -> OpenWorldLearningResult:
        self.cycle_count += 1
        result = OpenWorldLearningResult()

        n = random.randint(0, 5)
        for i in range(n):
            source = random.choice(self.sources)
            self.learn_from_source(source, f"fact_{self.cycle_count}_{i}")
            result.records_created += 1
        result.sources_used = len(set(r.source_type for r in self.records))

        contradictions = self.detect_contradictions()
        result.contradictions_detected = len(contradictions)

        revised = self.revise_beliefs(contradictions)
        result.beliefs_revised = revised

        if self.records:
            n = 3
            subset = self.records[-n:] if n <= len(self.records) else self.records
            result.avg_confidence = sum(r.confidence for r in subset) / max(1, len(subset))
        return result
