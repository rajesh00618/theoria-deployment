from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import CreativeArtifact


@dataclass
class CreativityResult:
    artifacts_created: int = 0
    avg_novelty: float = 0.0
    avg_utility: float = 0.0
    avg_impact: float = 0.0
    domain_distribution: Dict[str, int] = field(default_factory=dict)


class CreativityEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.artifacts: List[CreativeArtifact] = []
        self.domains = ["science", "math", "engineering", "software", "strategy"]
        self.cycle_count = 0

    def create(self, domain: str, prompt: str,
               novelty: float = 0.5,
               utility: float = 0.5,
               impact: float = 0.3) -> CreativeArtifact:
        artifact = CreativeArtifact(
            domain=domain,
            title=prompt,
            description=f"A creative artifact in {domain} inspired by {prompt}",
            novelty_score=novelty,
            utility_score=utility,
            impact_score=impact,
            artifact_type="scientific_idea",
        )
        self.artifacts.append(artifact)
        return artifact

    def generate_hypothesis(self, domain: str) -> CreativeArtifact:
        novelty = random.uniform(0.3, 0.95)
        utility = random.uniform(0.2, 0.8)
        impact = random.uniform(0.1, 0.9)
        return self.create(domain, f"novel_hypothesis_{self.cycle_count}",
                          novelty=novelty, utility=utility, impact=impact)

    def generate_theory(self, domain: str) -> CreativeArtifact:
        novelty = random.uniform(0.4, 0.9)
        utility = random.uniform(0.3, 0.85)
        impact = random.uniform(0.3, 0.95)
        return self.create(domain, f"novel_theory_{self.cycle_count}",
                          novelty=novelty, utility=utility, impact=impact)

    def generate_design(self, domain: str) -> CreativeArtifact:
        novelty = random.uniform(0.3, 0.85)
        utility = random.uniform(0.5, 0.95)
        impact = random.uniform(0.2, 0.8)
        return self.create(domain, f"novel_design_{self.cycle_count}",
                          novelty=novelty, utility=utility, impact=impact)

    def run_cycle(self) -> CreativityResult:
        self.cycle_count += 1
        result = CreativityResult()

        for domain in self.domains:
            choice = random.random()
            if choice < 0.33:
                self.generate_hypothesis(domain)
            elif choice < 0.66:
                self.generate_theory(domain)
            else:
                self.generate_design(domain)
            result.artifacts_created += 1

        if self.artifacts:
            recent = self.artifacts[-len(self.domains):]
            result.avg_novelty = sum(a.novelty_score for a in recent) / len(recent)
            result.avg_utility = sum(a.utility_score for a in recent) / len(recent)
            result.avg_impact = sum(a.impact_score for a in recent) / len(recent)

        for domain in self.domains:
            count = sum(1 for a in self.artifacts if a.domain == domain)
            if count > 0:
                result.domain_distribution[domain] = count
        return result
