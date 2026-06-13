from __future__ import annotations

import uuid
import random
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import CivilizationForecast


@dataclass
class SimulatorResult:
    models_active: int = 0
    forecasts_generated: int = 0
    policies_evaluated: int = 0
    scenarios_created: int = 0
    avg_accuracy: float = 0.0


class CivilizationSimulator:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.forecasts: List[CivilizationForecast] = []
        self.models: Dict[str, Dict[str, Any]] = {}
        self.model_types = ["economy", "government", "science", "technology"]
        self.cycle_count = 0

    def build_model(self, model_type: str) -> Dict[str, Any]:
        model = {
            "type": model_type, "accuracy": random.uniform(0.5, 0.95),
            "parameters": {"complexity": random.uniform(0.3, 0.9)},
            "status": "active",
        }
        self.models[model_type] = model
        return model

    def forecast(self, model_type: str, scenario: str,
                 horizon: int = 365) -> CivilizationForecast:
        model = self.models.get(model_type)
        if not model:
            model = self.build_model(model_type)
        n_outcomes = random.randint(3, 6)
        forecast = CivilizationForecast(
            model_type=model_type, scenario=scenario,
            forecast_horizon_days=horizon,
            predicted_outcomes=[
                {"step": i, "value": random.uniform(0, 1)}
                for i in range(n_outcomes)
            ],
            confidence_intervals=[random.uniform(0.6, 0.95) for _ in range(n_outcomes)],
            accuracy=model["accuracy"],
        )
        self.forecasts.append(forecast)
        return forecast

    def evaluate_policy(self, policy: str, model_type: str) -> Dict[str, Any]:
        model = self.models.get(model_type)
        if not model:
            model = self.build_model(model_type)
        return {
            "policy": policy, "model_type": model_type,
            "expected_impact": random.uniform(-0.5, 0.5),
            "confidence": model["accuracy"],
        }

    def create_scenario(self, base: str, variations: int = 3) -> List[Dict[str, Any]]:
        scenarios = []
        for i in range(variations):
            scenarios.append({
                "name": f"{base}_variant_{i}",
                "probability": random.uniform(0.1, 0.5),
                "description": f"Scenario {i} based on {base}",
            })
        total = sum(s["probability"] for s in scenarios)
        for s in scenarios:
            s["probability"] /= total
        return scenarios

    def run_cycle(self) -> SimulatorResult:
        self.cycle_count += 1
        result = SimulatorResult()

        for mt in self.model_types:
            if mt not in self.models:
                self.build_model(mt)

        result.models_active = len(self.models)

        if random.random() < 0.5:
            mt = random.choice(self.model_types)
            f = self.forecast(mt, f"scenario_{self.cycle_count}", horizon=random.randint(30, 365))
            result.forecasts_generated += 1

        if random.random() < 0.3:
            self.evaluate_policy(f"policy_{self.cycle_count}", random.choice(self.model_types))
            result.policies_evaluated += 1

        if random.random() < 0.3:
            self.create_scenario(f"base_{self.cycle_count}")
            result.scenarios_created += 1

        if self.forecasts:
            result.avg_accuracy = sum(f.accuracy for f in self.forecasts[-3:]) / min(3, len(self.forecasts))
        return result
