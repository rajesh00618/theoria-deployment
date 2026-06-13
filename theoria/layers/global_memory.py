from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import GlobalMemoryEntry


@dataclass
class GlobalMemoryResult:
    total_entries: int = 0
    compressed_count: int = 0
    abstractions_created: int = 0
    memory_types: Dict[str, int] = field(default_factory=dict)
    compression_ratio_avg: float = 1.0


class GlobalMemory:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.entries: Dict[str, GlobalMemoryEntry] = {}
        self.memory_types = ["personal", "research", "world", "goal", "decision"]
        self.cycle_count = 0

    def store(self, memory_type: str, content: str,
              importance: float = 0.5) -> GlobalMemoryEntry:
        entry = GlobalMemoryEntry(
            memory_type=memory_type, content=content,
            importance=importance, abstraction_level=0,
        )
        self.entries[entry.id] = entry
        return entry

    def compress(self) -> int:
        compressed = 0
        for entry in self.entries.values():
            if entry.abstraction_level < 5 and len(entry.content) > 100:
                entry.content = entry.content[:len(entry.content) // 2]
                entry.compression_ratio = 0.5
                entry.abstraction_level += 1
                compressed += 1
        return compressed

    def abstract(self) -> int:
        abstracted = 0
        for entry in self.entries.values():
            if entry.abstraction_level < 10 and random.random() < 0.2:
                if len(entry.content) > 50:
                    entry.content = f"Abstract({entry.content[:30]}...)"
                    entry.abstraction_level += 1
                    abstracted += 1
        return abstracted

    def query(self, memory_type: str, top_k: int = 10) -> List[GlobalMemoryEntry]:
        matching = [e for e in self.entries.values() if e.memory_type == memory_type]
        matching.sort(key=lambda x: x.importance, reverse=True)
        return matching[:top_k]

    def run_cycle(self) -> GlobalMemoryResult:
        self.cycle_count += 1
        result = GlobalMemoryResult()

        for mt in self.memory_types:
            if random.random() < 0.3:
                self.store(mt, f"{mt}_content_at_cycle_{self.cycle_count}",
                          importance=random.uniform(0.3, 0.9))

        result.compressed_count = self.compress()
        result.abstractions_created = self.abstract()
        result.total_entries = len(self.entries)

        for mt in self.memory_types:
            count = sum(1 for e in self.entries.values() if e.memory_type == mt)
            if count > 0:
                result.memory_types[mt] = count

        if self.entries:
            result.compression_ratio_avg = sum(e.compression_ratio for e in self.entries.values()) / len(self.entries)
        return result
