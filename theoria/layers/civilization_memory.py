"""P10.6: Civilization Memory — stores all knowledge for indefinite retention."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import CivilizationMemoryConfig
from theoria.core.types import CivilizationMemoryRecord


@dataclass
class MemoryResult:
    records_added: int = 0
    total_records: int = 0
    records_by_type: Dict[str, int] = field(default_factory=dict)
    avg_importance: float = 0.0
    total_discoveries: int = 0


class CivilizationMemory:
    def __init__(self, config: Optional[CivilizationMemoryConfig] = None):
        self.config = config or CivilizationMemoryConfig()
        self.records: Dict[str, CivilizationMemoryRecord] = {}

    def add_record(self, record_type: str = "") -> CivilizationMemoryRecord:
        if not record_type:
            record_type = random.choice(self.config.record_types)
        titles = {
            "theory": "Unified Theory of Everything",
            "experiment": "Large Hadron Collider Run",
            "discovery": "Novel Quantum Effect",
            "failure": "Failed Cold Fusion Attempt",
            "paradigm_shift": "Copernican Revolution",
            "institution": "Institute for Advanced Study",
        }
        title = titles.get(record_type, f"{record_type.capitalize()} Record")
        importance = random.uniform(0.1, 1.0) if self.config.enable_importance_weighting else 0.5

        record = CivilizationMemoryRecord(
            record_type=record_type,
            title=title,
            summary=f"Summary of {title}",
            importance=importance,
            references=[f"ref_{random.randint(0, 999)}" for _ in range(random.randint(0, 5))],
        )
        self.records[record.id] = record
        return record

    def run_cycle(self) -> MemoryResult:
        result = MemoryResult()

        if len(self.records) < self.config.max_records:
            batch = random.randint(10, 50)
            for _ in range(batch):
                self.add_record()

        result.records_added = len(self.records)
        result.total_records = len(self.records)
        for rt in self.config.record_types:
            count = sum(1 for r in self.records.values() if r.record_type == rt)
            result.records_by_type[rt] = count
        result.avg_importance = sum(r.importance for r in self.records.values()) / max(1, len(self.records))
        result.total_discoveries = sum(1 for r in self.records.values() if r.record_type == "discovery")

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_records": len(self.records),
            "by_type": {rt: sum(1 for r in self.records.values() if r.record_type == rt)
                       for rt in self.config.record_types},
            "most_important": max((r.importance for r in self.records.values()), default=0),
        }
