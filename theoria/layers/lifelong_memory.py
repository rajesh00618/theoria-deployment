from __future__ import annotations

import uuid
import random
import time
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import LifeEpisode


@dataclass
class MemoryConsolidationResult:
    episodes_consolidated: int = 0
    episodes_archived: int = 0
    episodes_forgotten: int = 0
    total_episodes: int = 0
    memory_strength_avg: float = 0.0


class LifelongMemoryLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.episodes: Dict[str, LifeEpisode] = {}
        self.working_memory: Dict[str, LifeEpisode] = {}
        self.consolidated_memory: Dict[str, LifeEpisode] = {}
        self.archived_memory: Dict[str, LifeEpisode] = {}
        self.cycle_count = 0
        self.max_episodes = (getattr(config, "max_episodes", 1000000)
                            if config else 1000000)
        self.consolidation_interval = (getattr(config, "consolidation_interval_cycles", 100)
                                       if config else 100)

    def record_episode(self, episode_type: str, description: str,
                       importance: float = 0.5,
                       insights: Optional[List[str]] = None,
                       links: Optional[List[str]] = None) -> LifeEpisode:
        episode = LifeEpisode(
            episode_type=episode_type,
            description=description,
            importance=importance,
            consolidation_state="working",
            memory_strength=importance,
            linked_episodes=links or [],
            key_insights=insights or [],
        )
        self.episodes[episode.id] = episode
        self.working_memory[episode.id] = episode
        return episode

    def replay_experience(self, batch_size: int = 64) -> List[LifeEpisode]:
        candidates = list(self.consolidated_memory.values())
        if len(candidates) < batch_size:
            candidates.extend(self.working_memory.values())
        return random.sample(candidates, min(batch_size, len(candidates)))

    def consolidate(self) -> MemoryConsolidationResult:
        result = MemoryConsolidationResult()
        for ep_id, ep in list(self.working_memory.items()):
            if ep.memory_strength > 0.5 or self.cycle_count % self.consolidation_interval == 0:
                ep.consolidation_state = "consolidated"
                self.consolidated_memory[ep_id] = ep
                del self.working_memory[ep_id]
                result.episodes_consolidated += 1

        for ep_id, ep in list(self.consolidated_memory.items()):
            if ep.importance < 0.2 and ep.memory_strength < 0.3:
                ep.consolidation_state = "archived"
                self.archived_memory[ep_id] = ep
                del self.consolidated_memory[ep_id]
                result.episodes_archived += 1

        if len(self.episodes) > self.max_episodes:
            candidates = [(eid, e) for eid, e in self.archived_memory.items()]
            candidates.sort(key=lambda x: x[1].memory_strength)
            to_remove = candidates[:len(self.episodes) - self.max_episodes]
            for eid, _ in to_remove:
                del self.episodes[eid]
                del self.archived_memory[eid]
                result.episodes_forgotten += 1

        result.total_episodes = len(self.episodes)
        all_eps = list(self.episodes.values())
        if all_eps:
            result.memory_strength_avg = sum(e.memory_strength for e in all_eps) / len(all_eps)
        return result

    def query(self, query: str, top_k: int = 10) -> List[LifeEpisode]:
        results = []
        query_lower = query.lower()
        for ep in self.episodes.values():
            if query_lower in ep.description.lower():
                results.append(ep)
            elif any(query_lower in i.lower() for i in ep.key_insights):
                results.append(ep)
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:top_k]

    def get_life_history(self) -> Dict[str, Any]:
        return {
            "total_episodes": len(self.episodes),
            "working": len(self.working_memory),
            "consolidated": len(self.consolidated_memory),
            "archived": len(self.archived_memory),
            "avg_importance": sum(e.importance for e in self.episodes.values()) / max(1, len(self.episodes)),
        }

    def run_cycle(self) -> MemoryConsolidationResult:
        self.cycle_count += 1
        result = self.consolidate()
        for ep in self.working_memory.values():
            ep.memory_strength *= random.uniform(0.99, 1.0)
        for ep in self.consolidated_memory.values():
            ep.memory_strength *= random.uniform(0.998, 1.0)
        return result
