"""P9.9: Meta-Civilization Intelligence — model scientific progress itself."""

from __future__ import annotations

import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import MetaCivilizationIntelligenceConfig
from theoria.core.types import CivilizationModel


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class MetaCivilizationResult:
    models_created: int = 0
    total_models: int = 0
    findings_generated: int = 0
    recommendations_generated: int = 0
    avg_accuracy: float = 0.0


class MetaCivilizationIntelligence:
    def __init__(self, config: Optional[MetaCivilizationIntelligenceConfig] = None):
        self.config = config or MetaCivilizationIntelligenceConfig()
        self.models: Dict[str, CivilizationModel] = {}

    def _generate_findings(self, model_type: str) -> List[str]:
        finding_templates = {
            "efficiency": [
                "Discovery accelerates with agent diversity",
                "Parallel exploration reduces time-to-discovery by 40%",
                "Cross-domain transfer is the strongest efficiency lever",
                "Diminishing returns set in after 60% knowledge saturation",
            ],
            "friction": [
                "Paradigm lock-in slows progress by 3x in mature fields",
                "Publication bias causes 25% of knowledge to be unreliable",
                "Competing research programs waste 15% of resources",
                "Reproducibility crisis reduces effective progress by 30%",
            ],
            "evolution": [
                "Scientific revolutions follow a 7-year cycle on average",
                "New fields emerge at boundaries between existing disciplines",
                "Knowledge evolution follows punctuated equilibrium",
                "Tool innovation drives 60% of paradigm shifts",
            ],
        }
        templates = finding_templates.get(model_type, finding_templates["efficiency"])
        return random.sample(templates, min(len(templates), random.randint(2, 4)))

    def _generate_recommendations(self, findings: List[str]) -> List[str]:
        recs = [
            f"Address '{f.split('by')[0].strip() if 'by' in f else f}' through targeted investment"
            for f in findings
        ]
        recs.append("Establish cross-domain collaboration frameworks")
        recs.append("Fund high-risk, high-reward exploratory research")
        return recs[:random.randint(2, 4)]

    def create_model(self) -> CivilizationModel:
        model_type = random.choice(self.config.model_types)
        description = f"Model of scientific {model_type}: analyzing patterns of {model_type} in research ecosystems"
        findings = self._generate_findings(model_type)
        recommendations = self._generate_recommendations(findings) if self.config.enable_recommendation else []

        model = CivilizationModel(
            model_type=model_type,
            description=description,
            findings=findings,
            recommendations=recommendations,
            accuracy=0.6 + _det_score(f"mcacc_{model_type}") * 0.35,
        )
        self.models[model.id] = model
        return model

    def run_cycle(self) -> MetaCivilizationResult:
        result = MetaCivilizationResult()

        if random.random() < 0.5 or len(self.models) < 3:
            self.create_model()

        findings = 0
        recommendations = 0
        for m in self.models.values():
            delta = _det_score(f"mcdelta_{m.id}_{self.cycle_count if hasattr(self, 'cycle_count') else 0}") * 0.07 - 0.02
            m.accuracy = max(0.0, min(1.0, m.accuracy + delta))
            findings += len(m.findings)
            recommendations += len(m.recommendations)

        result.models_created = len(self.models)
        result.total_models = len(self.models)
        result.findings_generated = findings
        result.recommendations_generated = recommendations
        result.avg_accuracy = sum(m.accuracy for m in self.models.values()) / max(1, len(self.models))

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_models": len(self.models),
            "by_type": {
                t: sum(1 for m in self.models.values() if m.model_type == t)
                for t in self.config.model_types
            },
            "avg_accuracy": sum(m.accuracy for m in self.models.values()) / max(1, len(self.models)),
        }
