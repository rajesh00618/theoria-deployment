"""P10.5: Meta-Knowledge Civilization — THEORIA studies discovery itself."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import MetaKnowledgeConfig
from theoria.core.types import MetaKnowledgeModel


@dataclass
class MetaKnowledgeResult:
    models_created: int = 0
    total_models: int = 0
    hypotheses_tested: int = 0
    findings_generated: int = 0
    avg_confidence: float = 0.0


class MetaKnowledgeCivilization:
    def __init__(self, config: Optional[MetaKnowledgeConfig] = None):
        self.config = config or MetaKnowledgeConfig()
        self.models: Dict[str, MetaKnowledgeModel] = {}

    def _generate_hypothesis(self, question: str) -> str:
        templates = [
            f"Knowledge evolves through {random.choice(['selection', 'combination', 'abstraction', 'specialization'])}",
            f"Discoveries emerge from {random.choice(['anomaly detection', 'cross-domain transfer', 'paradigm shifts', 'tool innovation'])}",
            f"The structure of knowledge is fundamentally {random.choice(['networked', 'hierarchical', 'fractal', 'relational'])}",
        ]
        return random.choice(templates)

    def _generate_findings(self, hypothesis: str) -> List[str]:
        num = random.randint(2, 4)
        findings = []
        for i in range(num):
            finding = f"Evidence {i+1}: {hypothesis.split(' through ')[0] if ' through ' in hypothesis else hypothesis} correlates with {random.choice(['discovery rate', 'paradigm stability', 'knowledge diversity', 'innovation velocity'])}"
            findings.append(finding)
        return findings

    def create_model(self) -> MetaKnowledgeModel:
        question = random.choice(self.config.questions)
        hypothesis = self._generate_hypothesis(question)
        findings = self._generate_findings(hypothesis)

        model = MetaKnowledgeModel(
            question=question,
            hypothesis=hypothesis,
            findings=findings,
            confidence=random.uniform(0.3, 0.8),
        )
        self.models[model.id] = model
        return model

    def test_hypotheses(self) -> int:
        tested = 0
        for model in self.models.values():
            if model.confidence < 0.9 and random.random() < 0.3:
                # Test and update confidence
                delta = random.uniform(-0.1, 0.2)
                model.confidence = min(1.0, max(0.0, model.confidence + delta))
                if delta > 0:
                    model.findings.append(f"New evidence supports hypothesis (confidence delta: {delta:.2f})")
                tested += 1
        return tested

    def run_cycle(self) -> MetaKnowledgeResult:
        result = MetaKnowledgeResult()

        if random.random() < 0.4 or len(self.models) < 3:
            self.create_model()

        tested = self.test_hypotheses() if self.config.enable_hypothesis_testing else 0

        findings = sum(len(m.findings) for m in self.models.values())
        avg_conf = sum(m.confidence for m in self.models.values()) / max(1, len(self.models))

        result.models_created = len(self.models)
        result.total_models = len(self.models)
        result.hypotheses_tested = tested
        result.findings_generated = findings
        result.avg_confidence = avg_conf

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_models": len(self.models),
            "avg_confidence": sum(m.confidence for m in self.models.values()) / max(1, len(self.models)),
            "questions": list(set(m.question for m in self.models.values())),
        }
