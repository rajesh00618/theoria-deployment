"""
Prediction Generator
====================

Generates testable predictions for theories.

Input: Theory, Domain
Output: Predictions with timestamps and test criteria
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Prediction:
    """A testable prediction."""
    id: str
    theory_id: str
    statement: str
    testable: bool
    falsifiable: bool
    test_method: str
    expected_outcome: str
    deadline: str
    confidence: float  # 0-1


@dataclass
class PredictionSet:
    """Set of predictions for a theory."""
    theory_id: str
    predictions: List[Prediction]
    total_predictions: int
    testable_count: int
    falsifiable_count: int
    timestamp: float = field(default_factory=time.time)


class PredictionGenerator:
    """
    Generates testable predictions for theories.
    
    Every theory must produce predictions with:
    - Clear statement
    - Test method
    - Expected outcome
    - Deadline
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.generated_predictions: List[Prediction] = []
        self.cycle_count = 0
    
    def generate_predictions(self, theory: Dict[str, Any],
                             domain: str) -> PredictionSet:
        """
        Generate predictions for a theory.
        
        Args:
            theory: Theory dictionary
            domain: Scientific domain
        
        Returns:
            PredictionSet with all predictions
        """
        self.cycle_count += 1
        
        predictions = []
        
        # Generate predictions from theory claims
        claims = theory.get("claims", [])
        for i, claim in enumerate(claims):
            pred = self._generate_from_claim(claim, theory, domain, i)
            predictions.append(pred)
        
        # Generate predictions from mechanisms
        mechanisms = theory.get("mechanisms", [])
        for i, mech in enumerate(mechanisms):
            pred = self._generate_from_mechanism(mech, theory, domain, i + len(claims))
            predictions.append(pred)
        
        # Generate predictions from patterns
        patterns = theory.get("patterns", [])
        for i, pat in enumerate(patterns):
            pred = self._generate_from_pattern(pat, theory, domain, i + len(claims) + len(mechanisms))
            predictions.append(pred)
        
        self.generated_predictions.extend(predictions)
        
        return PredictionSet(
            theory_id=theory.get("id", "unknown"),
            predictions=predictions,
            total_predictions=len(predictions),
            testable_count=sum(1 for p in predictions if p.testable),
            falsifiable_count=sum(1 for p in predictions if p.falsifiable),
        )
    
    def _generate_from_claim(self, claim: str, theory: Dict,
                             domain: str, index: int) -> Prediction:
        """Generate prediction from a claim."""
        return Prediction(
            id=f"pred_{theory.get('id', 'unk')}_{index}",
            theory_id=theory.get("id", "unknown"),
            statement=f"If {claim}, then measurable effect X should occur",
            testable=True,
            falsifiable=True,
            test_method="controlled_experiment",
            expected_outcome="statistically significant effect",
            deadline="6 months",
            confidence=0.7,
        )
    
    def _generate_from_mechanism(self, mechanism: str, theory: Dict,
                                 domain: str, index: int) -> Prediction:
        """Generate prediction from a mechanism."""
        return Prediction(
            id=f"pred_{theory.get('id', 'unk')}_{index}",
            theory_id=theory.get("id", "unknown"),
            statement=f"The mechanism {mechanism} should produce observable pattern Y",
            testable=True,
            falsifiable=True,
            test_method="observational_study",
            expected_outcome="pattern Y observed in data",
            deadline="12 months",
            confidence=0.6,
        )
    
    def _generate_from_pattern(self, pattern: str, theory: Dict,
                               domain: str, index: int) -> Prediction:
        """Generate prediction from a pattern."""
        return Prediction(
            id=f"pred_{theory.get('id', 'unk')}_{index}",
            theory_id=theory.get("id", "unknown"),
            statement=f"The pattern {pattern} should hold across conditions",
            testable=True,
            falsifiable=True,
            test_method="cross_validation",
            expected_outcome="pattern consistent across conditions",
            deadline="3 months",
            confidence=0.8,
        )
    
    def verify_prediction(self, prediction_id: str,
                          actual_outcome: str) -> bool:
        """Verify if a prediction was confirmed."""
        for pred in self.generated_predictions:
            if pred.id == prediction_id:
                # Simple matching
                return "confirmed" in actual_outcome.lower()
        return False
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of prediction generation."""
        return {
            "cycle_count": self.cycle_count,
            "predictions_generated": len(self.generated_predictions),
            "testable": sum(1 for p in self.generated_predictions if p.testable),
            "falsifiable": sum(1 for p in self.generated_predictions if p.falsifiable),
        }
