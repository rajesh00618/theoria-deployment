from __future__ import annotations

import uuid
import hashlib
import random
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from theoria.core.types import CognitiveTrace


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class CognitiveCoreResult:
    traces_generated: int = 0
    attention_shifts: int = 0
    goals_processed: int = 0
    modes_used: Set[str] = field(default_factory=set)
    merged_traces: int = 0
    coherence: float = 0.0


class UnifiedCognitiveCore:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.traces: List[CognitiveTrace] = []
        self.attention_focus: str = "general"
        self.active_goals: List[str] = []
        self.reasoning_modes = [
            "deduction", "induction", "abduction", "causal", "counterfactual",
            "analogical", "game_theoretic", "strategic", "legal", "economic"
        ]
        self.cycle_count = 0

    def process(self, input_data: str, domains: Optional[List[str]] = None,
                goals: Optional[List[str]] = None) -> CognitiveTrace:
        domains = domains or ["general"]
        goals = goals or []
        modes_used = random.sample(self.reasoning_modes,
                                    k=random.randint(1, min(5, len(self.reasoning_modes))))

        confidence = 0.3 + _det_score(f"conf_{input_data}_{self.cycle_count}") * 0.65
        trace = CognitiveTrace(
            attention_focus=input_data,
            reasoning_modes_used=modes_used,
            input_domains=domains,
            active_goals=goals,
            inference_steps=[{"step": i, "mode": m} for i, m in enumerate(modes_used)],
            confidence=confidence,
        )
        self.traces.append(trace)
        self.attention_focus = input_data
        return trace

    def merge_traces(self, trace_ids: List[str]) -> Optional[CognitiveTrace]:
        matching = [t for t in self.traces if t.id in trace_ids]
        if not matching:
            return None
        merged_modes = set()
        merged_domains = set()
        merged_goals = set()
        for t in matching:
            merged_modes.update(t.reasoning_modes_used)
            merged_domains.update(t.input_domains)
            merged_goals.update(t.active_goals)
        merged = CognitiveTrace(
            attention_focus="merged",
            reasoning_modes_used=list(merged_modes),
            input_domains=list(merged_domains),
            active_goals=list(merged_goals),
            confidence=sum(t.confidence for t in matching) / len(matching),
        )
        self.traces.append(merged)
        return merged

    def shift_attention(self, new_focus: str) -> None:
        self.attention_focus = new_focus

    def get_active_goals(self) -> List[str]:
        return self.active_goals

    def run_cycle(self) -> CognitiveCoreResult:
        self.cycle_count += 1
        result = CognitiveCoreResult()

        trace = self.process("cycle_{}_input".format(self.cycle_count))
        result.traces_generated += 1
        result.modes_used.update(trace.reasoning_modes_used)

        if random.random() < 0.3:
            self.shift_attention("new_focus_{}".format(self.cycle_count))
            result.attention_shifts += 1

        if len(self.traces) >= 3 and random.random() < 0.5:
            ids = [t.id for t in self.traces[-3:]]
            merged = self.merge_traces(ids)
            if merged:
                result.merged_traces += 1

        recent = self.traces[-10:]
        if recent and self.reasoning_modes:
            result.coherence = min(1.0, len(set(
                t.reasoning_modes_used[0] if t.reasoning_modes_used else ""
                for t in recent
            )) / len(self.reasoning_modes))
        return result
