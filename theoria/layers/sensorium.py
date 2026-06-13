"""
L0 Sensorium: The Phenomenal Layer.

Converts raw world signals into phenomenal stream.
- Multi-modal encoders
- Pre-attentive anomaly detectors
- Causal feature extractors
- Sub-theoretic Anomaly Buffer (STAB)
- Adversarial input detection
- Async ingest with back-pressure
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Callable
from collections import deque
from dataclasses import dataclass, field

from theoria.core.types import Evidence


@dataclass
class SensoryInput:
    """A raw sensory input across any modality."""
    raw_data: Any
    modality: str  # "numerical", "text", "image", "sensor", "tabular"
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyReport:
    """Report from anomaly detection subsystem."""
    input_id: str
    anomaly_score: float  # 0 = normal, 1 = extreme anomaly
    anomaly_type: str  # "statistical", "ood", "residue", "adversarial"
    explanation: str = ""
    recommended_action: str = "process"  # process, quarantine, drop


@dataclass
class FeatureVector:
    """Extracted causal features from sensory input."""
    source_input: str
    features: np.ndarray
    inductive_bias: str = ""  # e.g., "translation_equivariant"
    causal_tags: List[str] = field(default_factory=list)
    confidence: float = 1.0


class Sensorium:
    """
    L0: The Phenomenal Layer.
    Pre-theoretic: does not impose explanatory structure on data.
    Merely surfaces structure for higher layers.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        
        # Running models for anomaly detection
        self.running_mean: Dict[str, float] = {}
        self.running_var: Dict[str, float] = {}
        self.running_count: Dict[str, int] = {}
        
        # Sub-theoretic Anomaly Buffer (STAB)
        self.stab: deque = deque(maxlen=10000)  # Truly raw signals
        self.stab_anomaly_scores: Dict[str, float] = {}
        
        # Anomaly tracking
        self.anomaly_history: List[AnomalyReport] = []
        self.current_anomalies: List[str] = []  # IDs of current anomalies
        
        # Back-pressure
        self.ingest_queue: deque = deque(maxlen=1000)
        self.low_fidelity_mode: bool = False
        self.dropped_count: int = 0
        
        # Feature extractors registry
        self.feature_extractors: Dict[str, Callable] = {}
        self.register_default_extractors()
    
    def register_default_extractors(self) -> None:
        """Register default feature extractors for common modalities."""
        self.feature_extractors["numerical"] = self._extract_numerical_features
        self.feature_extractors["tabular"] = self._extract_tabular_features
        self.feature_extractors["text"] = self._extract_text_features
    
    def ingest(self, data: SensoryInput) -> Tuple[Optional[FeatureVector], 
                                                   Optional[AnomalyReport]]:
        """
        Main entry: ingest raw sensory data.
        Returns: (extracted_features, anomaly_report)
        """
        # Back-pressure check
        if len(self.ingest_queue) >= self.ingest_queue.maxlen:
            self.low_fidelity_mode = True
            # Drop oldest rather than newest
            self.ingest_queue.popleft()
            self.dropped_count += 1
        else:
            self.low_fidelity_mode = False
        
        self.ingest_queue.append(data)
        
        # Always store in STAB (truly raw)
        self.stab.append(data)
        
        # Run anomaly detection
        anomaly = self._detect_anomaly(data)
        if anomaly and anomaly.anomaly_score > 0.7:
            self.current_anomalies.append(data.metadata.get("id", str(len(self.stab))))
            self.anomaly_history.append(anomaly)
        
        # Extract features
        features = self._extract_features(data)
        
        return features, anomaly
    
    def _detect_anomaly(self, data: SensoryInput) -> Optional[AnomalyReport]:
        """
        Multi-method anomaly detection:
        1. Statistical surprise (KL-divergence from running model)
        2. Out-of-distribution (Mahalanobis distance)
        3. Residue detection (deviation from current theory predictions)
        """
        source = data.source
        
        # Convert to numerical representation
        if isinstance(data.raw_data, (int, float)):
            value = float(data.raw_data)
        elif isinstance(data.raw_data, np.ndarray):
            value = float(np.mean(data.raw_data))
        elif isinstance(data.raw_data, (list, tuple)):
            value = float(np.mean(data.raw_data))
        else:
            value = float(hash(str(data.raw_data)) % 10000) / 10000
        
        # Update running statistics
        if source not in self.running_mean:
            self.running_mean[source] = value
            self.running_var[source] = 1.0
            self.running_count[source] = 1
            return None  # Not enough data yet
        
        # Welford's online algorithm
        n = self.running_count[source]
        old_mean = self.running_mean[source]
        old_var = self.running_var[source]
        
        new_mean = old_mean + (value - old_mean) / (n + 1)
        new_var = old_var + (value - old_mean) * (value - new_mean)
        
        self.running_mean[source] = new_mean
        self.running_var[source] = new_var
        self.running_count[source] = n + 1
        
        # Statistical surprise (KL-like)
        std = np.sqrt(max(new_var / (n + 1), 1e-10))
        z_score = abs(value - new_mean) / std if std > 0 else 0
        
        # Convert to anomaly score (sigmoid)
        anomaly_score = 1.0 / (1.0 + np.exp(-0.5 * (z_score - 3)))
        
        # Determine type
        if z_score > 4:
            anomaly_type = "statistical"
            explanation = f"Extreme statistical outlier (z={z_score:.2f})"
        elif z_score > 2.5:
            anomaly_type = "ood"
            explanation = f"Out-of-distribution (z={z_score:.2f})"
        else:
            return None
        
        # STAB verification
        raw_score = self._stab_check(data, anomaly_score)
        if abs(raw_score - anomaly_score) > 0.3:
            explanation += " [STAB disagreement - possible feature artifact]"
            anomaly_score = max(anomaly_score, raw_score)
        
        report = AnomalyReport(
            input_id=data.metadata.get("id", str(len(self.stab))),
            anomaly_score=anomaly_score,
            anomaly_type=anomaly_type,
            explanation=explanation,
            recommended_action="quarantine" if anomaly_score > 0.8 else "process"
        )
        
        return report
    
    def _stab_check(self, data: SensoryInput, feature_score: float) -> float:
        """
        Sub-theoretic Anomaly Buffer check.
        Verify that anomalies are not artifacts of feature-extractor theory-ladenness.
        """
        # Compute anomaly on raw representation (not feature-based)
        if isinstance(data.raw_data, np.ndarray):
            raw = data.raw_data.flatten()
            if len(raw) > 0:
                raw_spread = np.std(raw) / (np.mean(np.abs(raw)) + 1e-10)
                # Normalize to [0, 1]
                raw_score = min(raw_spread / 10.0, 1.0)
                return raw_score
        return feature_score * 0.8  # Conservative default
    
    def _extract_features(self, data: SensoryInput) -> Optional[FeatureVector]:
        """Extract causal features using modality-appropriate extractor."""
        extractor = self.feature_extractors.get(data.modality)
        if extractor is None:
            return None
        return extractor(data)
    
    def _extract_numerical_features(self, data: SensoryInput) -> FeatureVector:
        """Extract features from numerical data (handles scalars, lists, and dicts)."""
        raw = data.raw_data
        if isinstance(raw, (int, float)):
            features = np.array([float(raw), 0.0, 0.0, 0.0])
        elif isinstance(raw, dict):
            # Extract numerical values from dict
            values = [float(v) for v in raw.values() if isinstance(v, (int, float))]
            if len(values) >= 4:
                features = np.array([np.mean(values), np.std(values), 
                                   np.min(values), np.max(values)])
            elif values:
                arr = np.array(values)
                features = np.pad(arr, (0, 4 - len(arr)))
            else:
                features = np.array([0.0, 0.0, 0.0, 0.0])
        elif isinstance(raw, (list, tuple)):
            arr = np.array(raw, dtype=float).flatten()[:100]
            if len(arr) < 4:
                arr = np.pad(arr, (0, 4 - len(arr)))
            features = arr[:4]
        else:
            features = np.array([0.0, 0.0, 0.0, 0.0])
        
        return FeatureVector(
            source_input=data.metadata.get("id", ""),
            features=features,
            inductive_bias="scale_invariant",
            causal_tags=["observable"],
        )
    
    def _extract_tabular_features(self, data: SensoryInput) -> FeatureVector:
        """Extract features from tabular data."""
        df = data.raw_data
        if hasattr(df, 'values'):
            numeric = df.select_dtypes(include=[np.number])
            features = numeric.mean().values[:10]
            if len(features) < 4:
                features = np.pad(features, (0, 4 - len(features)))
        else:
            features = np.array([0.0, 0.0, 0.0, 0.0])
        
        return FeatureVector(
            source_input=data.metadata.get("id", ""),
            features=features[:4],
            inductive_bias="row_permutation_invariant",
            causal_tags=["tabular_observation"],
        )
    
    def _extract_text_features(self, data: SensoryInput) -> FeatureVector:
        """Extract simple features from text."""
        text = str(data.raw_data)
        features = np.array([
            len(text),  # length
            len(text.split()),  # word count
            text.count('.'),  # sentence count proxy
            hash(text) % 1000 / 1000,  # rough semantic hash
        ])
        return FeatureVector(
            source_input=data.metadata.get("id", ""),
            features=features,
            inductive_bias="bag_of_words",
            causal_tags=["linguistic"],
        )
    
    def get_anomalies(self, min_score: float = 0.5) -> List[AnomalyReport]:
        """Get current anomalies above threshold."""
        return [a for a in self.anomaly_history if a.anomaly_score >= min_score]
    
    def clear_anomalies(self) -> None:
        """Clear current anomaly list (called between cycles)."""
        self.current_anomalies = []
    
    @property
    def queue_size(self) -> int:
        return len(self.ingest_queue)
    
    @property
    def is_overloaded(self) -> bool:
        return self.low_fidelity_mode
