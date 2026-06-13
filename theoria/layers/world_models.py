from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import WorldModel


@dataclass
class Prediction:
    model_id: str = ""
    variable: str = ""
    predicted_value: float = 0.0
    confidence: float = 0.0
    actual_value: Optional[float] = None


@dataclass
class InterventionPlan:
    plan_id: str = ""
    target_variable: str = ""
    intervention: str = ""
    expected_outcome: float = 0.0
    risk: float = 0.0


@dataclass
class WorldModelResult:
    models_active: int = 0
    predictions_made: int = 0
    interventions_planned: int = 0
    avg_accuracy: float = 0.0
    model_diversity: int = 0
    findings: List[str] = field(default_factory=list)


class WorldModelingEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.models: Dict[str, WorldModel] = {}
        self.model_types = (getattr(config, "model_types", []) if config else [
            "scientific", "economic", "social", "technological", "political",
        ])
        self.max_models = getattr(config, "max_models", 25) if config else 25
        self.predictions: List[Prediction] = []
        self.interventions: List[InterventionPlan] = []
        self.cycle_count = 0

        self._initialize_models()

    def _initialize_models(self) -> None:
        for mt in self.model_types:
            model = WorldModel(
                name=mt + "_model",
                model_type=mt,
                domain=mt,
                accuracy=0.5,
                state_variables=[],
                parameters={},
            )
            self.models[model.id] = model

    def add_model(self, domain: str, model_type: str = "scientific") -> Optional[WorldModel]:
        if len(self.models) >= self.max_models:
            return None
        model = WorldModel(
            name=domain + "_model",
            model_type=model_type,
            domain=domain,
            accuracy=0.5,
            state_variables=[],
            parameters={},
        )
        self.models[model.id] = model
        return model

    def predict(self, model_id: str, variable: str) -> Prediction:
        model = self.models.get(model_id)
        if not model:
            return Prediction(confidence=0.0)
        pred = Prediction(
            model_id=model_id,
            variable=variable,
            predicted_value=random.uniform(-1, 1),
            confidence=model.accuracy * random.uniform(0.5, 1.0),
        )
        self.predictions.append(pred)
        return pred

    def plan_intervention(self, model_id: str, target: str) -> InterventionPlan:
        plan = InterventionPlan(
            plan_id=str(uuid.uuid4()),
            target_variable=target,
            intervention="Adjust {}".format(target),
            expected_outcome=random.uniform(-0.5, 0.5),
            risk=random.uniform(0.1, 0.7),
        )
        self.interventions.append(plan)
        return plan

    def update_model(self, model_id: str) -> None:
        model = self.models.get(model_id)
        if model:
            model.accuracy = min(1.0, model.accuracy + random.uniform(-0.05, 0.1))

    def run_cycle(self) -> WorldModelResult:
        self.cycle_count += 1
        result = WorldModelResult()

        for model_id in list(self.models.keys()):
            self.update_model(model_id)
            var = "variable_{}".format(random.randint(0, 5))
            self.predict(model_id, var)
            result.predictions_made += 1

            if random.random() < 0.3:
                self.plan_intervention(model_id, var)
                result.interventions_planned += 1

        accuracies = [m.accuracy for m in self.models.values()]
        result.avg_accuracy = sum(accuracies) / max(1, len(accuracies))
        result.models_active = len(self.models)
        result.model_diversity = len(set(m.model_type for m in self.models.values()))

        if result.avg_accuracy > 0.8:
            result.findings.append(
                "World models reached {:.1%} accuracy".format(result.avg_accuracy))

        return result
