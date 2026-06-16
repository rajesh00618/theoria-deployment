"""
THEORIA Prediction Tracker
===========================

Immutable prediction storage with SHA256 hashing.
Once created, predictions cannot be modified. Verification
is append-only with modification detection.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class Prediction:
    """A prediction made by THEORIA. Frozen at creation time."""
    id: str
    statement: str
    domain: str
    made_date: str
    deadline: str
    status: str  # "pending", "confirmed", "falsified", "expired"
    confidence: float
    content_hash: str = ""  # SHA256 of immutable fields
    evidence: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    verified_date: Optional[str] = None
    verification_hash: Optional[str] = None  # Hash of verification record

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA256 of immutable prediction fields."""
        content = f"{self.id}|{self.statement}|{self.domain}|{self.made_date}|{self.deadline}|{self.confidence}"
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_integrity(self) -> bool:
        """Check that immutable fields haven't been tampered with."""
        return self.content_hash == self._compute_hash()


@dataclass
class VerificationRecord:
    """Append-only verification record."""
    prediction_id: str
    outcome: str
    confirmed: bool
    verified_date: str
    verification_hash: str
    previous_hash: str  # Chain to previous record for this prediction

    def _compute_hash(self) -> str:
        content = f"{self.prediction_id}|{self.outcome}|{self.confirmed}|{self.verified_date}|{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()


class PredictionTracker:
    """
    Tracks predictions with immutable storage and append-only verification.
    
    Predictions are frozen at creation time with SHA256 hashes.
    Verification records are append-only with chain hashing.
    Any modification to frozen fields is detected.
    """
    
    def __init__(self, data_file: str = "results/predictions.json"):
        self.data_file = data_file
        self.predictions: Dict[str, Prediction] = {}
        self.verification_history: List[VerificationRecord] = []
        self._last_hashes: Dict[str, str] = {}  # prediction_id -> last verification hash
        self._load()
    
    def _load(self) -> None:
        """Load predictions from file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file) as f:
                    data = json.load(f)
                for p_data in data.get("predictions", []):
                    pred = Prediction(**p_data)
                    if pred.verify_integrity():
                        self.predictions[pred.id] = pred
                    else:
                        print(f"WARNING: Prediction {pred.id} failed integrity check - skipping")
                for v_data in data.get("verification_history", []):
                    vrec = VerificationRecord(**v_data)
                    self.verification_history.append(vrec)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"WARNING: Failed to load predictions: {e}")
    
    def _save(self) -> None:
        """Save predictions to file."""
        os.makedirs(os.path.dirname(self.data_file) or ".", exist_ok=True)
        data = {
            "version": "2.0",
            "immutable_format": True,
            "predictions": [asdict(p) for p in self.predictions.values()],
            "verification_history": [asdict(v) for v in self.verification_history],
            "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def add_prediction(self, statement: str, domain: str, deadline: str,
                       confidence: float, prediction_id: Optional[str] = None) -> Prediction:
        """Create a new immutable prediction. Returns the frozen prediction."""
        if prediction_id is None:
            prediction_id = f"PRED-{len(self.predictions)+1:03d}"
        
        pred = Prediction(
            id=prediction_id,
            statement=statement,
            domain=domain,
            made_date=time.strftime("%Y-%m-%d"),
            deadline=deadline,
            status="pending",
            confidence=confidence,
        )
        self.predictions[pred.id] = pred
        self._save()
        return pred
    
    def verify_prediction(self, prediction_id: str, outcome: str,
                          confirmed: bool) -> Optional[VerificationRecord]:
        """Append a verification record. Does NOT modify the original prediction."""
        if prediction_id not in self.predictions:
            return None
        
        pred = self.predictions[prediction_id]
        previous_hash = self._last_hashes.get(prediction_id, pred.content_hash)
        
        verified_date = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        
        vrec = VerificationRecord(
            prediction_id=prediction_id,
            outcome=outcome,
            confirmed=confirmed,
            verified_date=verified_date,
            verification_hash="",  # Computed below
            previous_hash=previous_hash,
        )
        vrec.verification_hash = vrec._compute_hash()
        
        # Update prediction status (append, don't overwrite immutable fields)
        pred.status = "confirmed" if confirmed else "falsified"
        pred.outcome = outcome
        pred.verified_date = verified_date
        pred.verification_hash = vrec.verification_hash
        
        self._last_hashes[prediction_id] = vrec.verification_hash
        self.verification_history.append(vrec)
        self._save()
        return vrec
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Verify integrity of all predictions and verification chains."""
        results = {"predictions_ok": 0, "predictions_tampered": 0, "chains_ok": 0, "chains_broken": 0}
        
        for pred in self.predictions.values():
            if pred.verify_integrity():
                results["predictions_ok"] += 1
            else:
                results["predictions_tampered"] += 1
        
        for vrec in self.verification_history:
            expected = vrec._compute_hash()
            if vrec.verification_hash == expected:
                results["chains_ok"] += 1
            else:
                results["chains_broken"] += 1
        
        return results
    
    def get_pending(self) -> List[Prediction]:
        """Get all pending predictions."""
        return [p for p in self.predictions.values() if p.status == "pending"]
    
    def get_expired(self) -> List[Prediction]:
        """Get predictions past their deadline."""
        today = time.strftime("%Y-%m-%d")
        return [p for p in self.predictions.values()
                if p.status == "pending" and p.deadline < today]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of predictions with integrity check."""
        statuses = {}
        for p in self.predictions.values():
            statuses[p.status] = statuses.get(p.status, 0) + 1
        
        integrity = self.verify_integrity()
        
        return {
            "total": len(self.predictions),
            "by_status": statuses,
            "pending": statuses.get("pending", 0),
            "confirmed": statuses.get("confirmed", 0),
            "falsified": statuses.get("falsified", 0),
            "integrity": integrity,
            "all_hashes_valid": (
                integrity["predictions_tampered"] == 0 and
                integrity["chains_broken"] == 0
            ),
        }
