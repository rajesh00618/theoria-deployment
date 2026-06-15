"""
THEORIA Prediction Tracker
===========================

Tracks predictions and their outcomes over time.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class Prediction:
    """A prediction made by THEORIA."""
    id: str
    statement: str
    domain: str
    made_date: str
    deadline: str
    status: str  # "pending", "confirmed", "falsified", "expired"
    confidence: float
    evidence: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    verified_date: Optional[str] = None


class PredictionTracker:
    """
    Tracks predictions and their outcomes.
    
    Predictions are frozen at creation time.
    Outcomes are verified when data becomes available.
    """
    
    def __init__(self, data_file: str = "results/predictions.json"):
        self.data_file = data_file
        self.predictions: Dict[str, Prediction] = {}
        self.load()
    
    def load(self) -> None:
        """Load predictions from file."""
        if os.path.exists(self.data_file):
            with open(self.data_file) as f:
                data = json.load(f)
                for p in data.get("predictions", []):
                    self.predictions[p["id"]] = Prediction(**p)
    
    def save(self) -> None:
        """Save predictions to file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        data = {
            "predictions": [asdict(p) for p in self.predictions.values()],
            "last_updated": time.strftime("%Y-%m-%d"),
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_prediction(self, prediction: Prediction) -> None:
        """Add a new prediction."""
        self.predictions[prediction.id] = prediction
        self.save()
    
    def verify_prediction(self, prediction_id: str, outcome: str,
                          confirmed: bool) -> None:
        """Verify a prediction's outcome."""
        if prediction_id in self.predictions:
            pred = self.predictions[prediction_id]
            pred.status = "confirmed" if confirmed else "falsified"
            pred.outcome = outcome
            pred.verified_date = time.strftime("%Y-%m-%d")
            self.save()
    
    def get_pending(self) -> List[Prediction]:
        """Get all pending predictions."""
        return [p for p in self.predictions.values() if p.status == "pending"]
    
    def get_expired(self) -> List[Prediction]:
        """Get predictions past their deadline."""
        today = time.strftime("%Y-%m-%d")
        return [p for p in self.predictions.values()
                if p.status == "pending" and p.deadline < today]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of predictions."""
        statuses = {}
        for p in self.predictions.values():
            statuses[p.status] = statuses.get(p.status, 0) + 1
        
        return {
            "total": len(self.predictions),
            "by_status": statuses,
            "pending": statuses.get("pending", 0),
            "confirmed": statuses.get("confirmed", 0),
            "falsified": statuses.get("falsified", 0),
        }


def create_initial_predictions() -> None:
    """Create initial predictions for THEORIA."""
    tracker = PredictionTracker()
    
    predictions = [
        Prediction(
            id="PRED-001",
            statement="Reddit communities with >15% persistent dissenters will show higher fragmentation than communities with <10% dissenters",
            domain="social_science",
            made_date="2026-06-15",
            deadline="2026-12-15",
            status="pending",
            confidence=0.7,
        ),
        Prediction(
            id="PRED-002",
            statement="GitHub repositories with >15% persistent issue dissenters will have higher fork rates and lower contributor retention",
            domain="software_engineering",
            made_date="2026-06-15",
            deadline="2026-12-15",
            status="pending",
            confidence=0.6,
        ),
        Prediction(
            id="PRED-003",
            statement="Stack Overflow tags with >20% persistent dissenters will show lower answer acceptance rates",
            domain="online_communities",
            made_date="2026-06-15",
            deadline="2026-12-15",
            status="pending",
            confidence=0.5,
        ),
        Prediction(
            id="PRED-004",
            statement="Wikipedia articles with higher dissent fractions will receive more editorial interventions",
            domain="wikipedia",
            made_date="2026-06-15",
            deadline="2026-09-15",
            status="pending",
            confidence=0.65,
        ),
    ]
    
    for pred in predictions:
        tracker.add_prediction(pred)
    
    print("Created %d predictions" % len(predictions))
    print("Saved to results/predictions.json")


if __name__ == "__main__":
    create_initial_predictions()
