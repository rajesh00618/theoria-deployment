"""
Memory Architecture: Five interconnected stores + two-tier forgetting.

From Section 5.1:
- Episodic: Raw observations
- Semantic: Established facts
- Theory: Living theories with version history
- Graveyard: Rejected hypotheses (with resurrection)
- Meta-strategy: How the system learns
"""

from __future__ import annotations

import time
import numpy as np
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field

from theoria.core.types import (
    Theory, Evidence, Concept, Strategy, AuditLogEntry, TripwireEvent,
    TheoryStatus, ConceptLifecycle, StrategyType,
)


# ============================================================================
# Episodic Memory: Raw observations
# ============================================================================

@dataclass
class EpisodicRecord:
    """A raw observation with timestamp and context."""
    id: str
    timestamp: float
    modality: str  # text, numerical, image, sensor, etc.
    raw_data: Any
    context: Dict[str, Any] = field(default_factory=dict)
    compressed: bool = False
    compression_error: float = 0.0


class EpisodicMemory:
    """
    Tier 1: Append-only, lossless (or bounded-error compression).
    Periodically decompressed and re-verified.
    """
    
    def __init__(self, max_size: int = 100000, compression_epsilon: float = 0.01):
        self.records: deque = deque(maxlen=max_size)
        self.compressed_indices: Set[int] = set()
        self.compression_epsilon = compression_epsilon
        self.modality_stats: Dict[str, int] = defaultdict(int)
        
    def append(self, record: EpisodicRecord) -> None:
        """Append-only insert."""
        self.records.append(record)
        self.modality_stats[record.modality] += 1
        
    def query_time_range(self, t_start: float, t_end: float) -> List[EpisodicRecord]:
        """Query observations in time range."""
        return [r for r in self.records if t_start <= r.timestamp <= t_end]
    
    def query_modality(self, modality: str) -> List[EpisodicRecord]:
        """Query by modality."""
        return [r for r in self.records if r.modality == modality]
    
    def get_recent(self, n: int = 100) -> List[EpisodicRecord]:
        """Get n most recent observations."""
        records_list = list(self.records)
        return records_list[-n:] if len(records_list) >= n else records_list
    
    def compress_older_than(self, age_threshold: float) -> int:
        """
        Tier-2 forgetting: Compress old records with provable bounds.
        Information-theoretic compression preserving sufficient statistics.
        """
        current_time = time.time()
        compressed = 0
        for i, record in enumerate(self.records):
            if i in self.compressed_indices:
                continue
            if current_time - record.timestamp > age_threshold:
                # Simulate compression (in real system: autoencoder/PCA)
                record.compressed = True
                record.compression_error = self.compression_epsilon
                self.compressed_indices.add(i)
                compressed += 1
        return compressed
    
    def decompress_and_verify(self, n_samples: int = 100) -> List[int]:
        """
        Periodically decompress and re-verify against new evidence.
        If reconstruction disagrees, compression is undone.
        """
        if not self.compressed_indices:
            return []
        
        indices = list(self.compressed_indices)
        sample = np.random.choice(
            indices, 
            size=min(n_samples, len(indices)), 
            replace=False
        )
        restored = []
        for idx in sample:
            record = self.records[idx]
            record.compressed = False
            record.compression_error = 0.0
            self.compressed_indices.discard(idx)
            restored.append(idx)
        return restored
    
    @property
    def size(self) -> int:
        return len(self.records)
    
    @property
    def compression_ratio(self) -> float:
        if not self.records:
            return 0.0
        return len(self.compressed_indices) / len(self.records)


# ============================================================================
# Semantic Memory: Established facts
# ============================================================================

class SemanticMemory:
    """
    Tier 1: Established facts updated on sufficient Bayesian evidence.
    Each fact has a posterior over its truth value.
    """
    
    def __init__(self):
        self.facts: Dict[str, Dict[str, Any]] = {}  # fact_id -> fact data
        self.fact_posteriors: Dict[str, float] = {}
        self.claim_to_evidence: Dict[str, List[str]] = defaultdict(list)
        
    def add_fact(self, fact_id: str, statement: str, 
                 initial_posterior: float = 0.5,
                 evidence_ids: Optional[List[str]] = None) -> None:
        """Add or update a fact."""
        self.facts[fact_id] = {
            "statement": statement,
            "added": time.time(),
            "last_updated": time.time(),
            "version": 1,
        }
        self.fact_posteriors[fact_id] = initial_posterior
        if evidence_ids:
            self.claim_to_evidence[fact_id].extend(evidence_ids)
    
    def update_posterior(self, fact_id: str, new_posterior: float) -> None:
        """Update fact posterior with new evidence."""
        if fact_id in self.facts:
            self.fact_posteriors[fact_id] = new_posterior
            self.facts[fact_id]["last_updated"] = time.time()
            self.facts[fact_id]["version"] += 1
    
    def query(self, min_posterior: float = 0.7) -> List[Tuple[str, str, float]]:
        """Query facts above posterior threshold."""
        results = []
        for fid, fact in self.facts.items():
            post = self.fact_posteriors.get(fid, 0.0)
            if post >= min_posterior:
                results.append((fid, fact["statement"], post))
        return sorted(results, key=lambda x: x[2], reverse=True)
    
    def get(self, fact_id: str) -> Optional[Tuple[str, float]]:
        """Get fact statement and posterior."""
        if fact_id not in self.facts:
            return None
        return (self.facts[fact_id]["statement"], 
                self.fact_posteriors.get(fact_id, 0.0))
    
    @property
    def size(self) -> int:
        return len(self.facts)


# ============================================================================
# Theory Memory: Living theories
# ============================================================================

class TheoryMemory:
    """
    Tier 1: Living theories with version history, domains of validity, evidence.
    Theories are never deleted, only versioned or retired to Graveyard.
    """
    
    def __init__(self):
        self.theories: Dict[str, Theory] = {}  # theory_id -> Theory
        self.name_to_id: Dict[str, str] = {}  # theory name -> latest id
        self.version_history: Dict[str, List[str]] = defaultdict(list)
        self.programme_theories: Dict[str, List[str]] = defaultdict(list)
        
    def register(self, theory: Theory) -> bool:
        """
        Register a theory if it satisfies registration conditions (Appendix D).
        Returns True if registered successfully.
        """
        if not theory.is_registered:
            theory.status = TheoryStatus.PROPOSED
            return False
        
        theory.status = TheoryStatus.ACTIVE
        theory.status_history.append((time.time(), TheoryStatus.ACTIVE))
        
        self.theories[theory.id] = theory
        self.name_to_id[theory.name] = theory.id
        self.version_history[theory.name].append(theory.id)
        
        if theory.programme_id:
            self.programme_theories[theory.programme_id].append(theory.id)
        
        return True
    
    def get(self, theory_id: str) -> Optional[Theory]:
        """Get theory by ID."""
        return self.theories.get(theory_id)
    
    def get_by_name(self, name: str) -> Optional[Theory]:
        """Get latest version of theory by name."""
        tid = self.name_to_id.get(name)
        return self.theories.get(tid) if tid else None
    
    def update_status(self, theory_id: str, new_status: TheoryStatus) -> None:
        """Update theory status."""
        if theory_id in self.theories:
            t = self.theories[theory_id]
            t.status = new_status
            t.status_history.append((time.time(), new_status))
    
    def retire_to_graveyard(self, theory_id: str, reason: str) -> Optional[Theory]:
        """
        Retire a theory. Returns the theory for transfer to Graveyard.
        """
        if theory_id not in self.theories:
            return None
        theory = self.theories[theory_id]
        theory.status = TheoryStatus.RETIRED
        theory.status_history.append((time.time(), TheoryStatus.RETIRED))
        
        # Remove from active but keep ID mapping
        del self.theories[theory_id]
        
        return theory
    
    def get_active(self) -> List[Theory]:
        """Get all active theories."""
        return [t for t in self.theories.values() 
                if t.status in (TheoryStatus.ACTIVE, TheoryStatus.UNDER_TEST,
                               TheoryStatus.CONVERGED)]
    
    def get_by_programme(self, programme_id: str) -> List[Theory]:
        """Get all theories in a research programme."""
        tids = self.programme_theories.get(programme_id, [])
        return [self.theories[tid] for tid in tids if tid in self.theories]
    
    def get_pareto_front(self, 
                         objectives: Optional[List[str]] = None) -> List[Theory]:
        """
        Get Pareto-optimal theories across multiple objectives.
        Default: posterior, parsimony (inverse parameter count), novelty.
        """
        if objectives is None:
            objectives = ["posterior", "parsimony", "novelty"]
        
        active = self.get_active()
        if not active:
            return []
        
        # Simple Pareto front computation
        pareto = []
        for t in active:
            dominated = False
            for other in active:
                if other.id == t.id:
                    continue
                # Check if other dominates t
                better_in_all = True
                better_in_some = False
                for obj in objectives:
                    t_val = getattr(t, obj, 0.5)
                    o_val = getattr(other, obj, 0.5)
                    if o_val < t_val:
                        better_in_all = False
                        break
                    if o_val > t_val:
                        better_in_some = True
                if better_in_all and better_in_some:
                    dominated = True
                    break
            if not dominated:
                pareto.append(t)
        return pareto
    
    @property
    def size(self) -> int:
        return len(self.theories)


# ============================================================================
# Graveyard: Rejected hypotheses
# ============================================================================

class Graveyard:
    """
    Tier 1: Rejected hypotheses with reasons for rejection.
    Used to seed L3 with anti-priors and for concept archaeology.
    
    Three purposes:
    1. Avoidance: avoid re-proposing in same context
    2. Counterfactual reasoning: "what would have to be different?"
    3. Concept archaeology: study failure to illuminate new domains
    """
    
    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}  # theory_id -> entry
        self.rejection_reasons: Dict[str, int] = defaultdict(int)
        self.concept_failures: Dict[str, List[str]] = defaultdict(list)
        self.resurrection_signals: deque = deque(maxlen=1000)
        
    def bury(self, theory: Theory, reason: str, 
             context: Optional[Dict[str, Any]] = None) -> None:
        """Add a failed theory to the graveyard."""
        entry = {
            "theory": theory,
            "reason": reason,
            "context": context or {},
            "buried_at": time.time(),
            "resurrection_count": 0,
            "mode_of_failure": self._classify_failure(reason),
        }
        self.entries[theory.id] = entry
        self.rejection_reasons[reason] += 1
        
        # Track concept failures for archaeology
        for claim in theory.core_claims:
            self.concept_failures[claim.statement].append(theory.id)
    
    def _classify_failure(self, reason: str) -> str:
        """Classify mode of failure for counterfactual reasoning."""
        reason_lower = reason.lower()
        if "falsified" in reason_lower:
            return "empirical_falsification"
        elif "degenerate" in reason_lower:
            return "programme_degeneration"
        elif "protective belt" in reason_lower:
            return "belt_exhaustion"
        elif "compression" in reason_lower:
            return "compression_only"
        elif "red line" in reason_lower or "safety" in reason_lower:
            return "safety_violation"
        else:
            return "general_failure"
    
    def query(self, reason_filter: Optional[str] = None,
              concept_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query graveyard entries with optional filters."""
        results = []
        for entry in self.entries.values():
            if reason_filter and not entry["reason"].startswith(reason_filter):
                continue
            if concept_filter and concept_filter not in str(entry["theory"].core_claims):
                continue
            results.append(entry)
        return results
    
    def signal_resurrection(self, theory_id: str, trigger: str) -> bool:
        """
        Signal that a graveyard entry should be re-evaluated.
        Triggers: paradigm crisis, context change, concept archaeology.
        """
        if theory_id not in self.entries:
            return False
        
        entry = self.entries[theory_id]
        entry["resurrection_count"] += 1
        self.resurrection_signals.append({
            "theory_id": theory_id,
            "trigger": trigger,
            "time": time.time(),
        })
        return True
    
    def get_resurrection_candidates(self, 
                                     current_context: Dict[str, Any]) -> List[str]:
        """
        Get candidates for concept archaeology.
        Concepts that failed in their original domain but might succeed in new context.
        """
        candidates = []
        for tid, entry in self.entries.items():
            # Check if context has changed significantly
            old_context = entry.get("context", {})
            if self._context_differs(old_context, current_context):
                candidates.append(tid)
        return candidates
    
    def _context_differs(self, old: Dict[str, Any], new: Dict[str, Any]) -> bool:
        """Check if context has changed enough to warrant re-evaluation."""
        # Simple heuristic: different domain or different data characteristics
        old_domain = old.get("domain", "")
        new_domain = new.get("domain", "")
        return old_domain != new_domain
    
    def get_anti_prior_boost(self, theory_signature: str) -> float:
        """
        Return penalty for theories similar to graveyard entries.
        Used by L3 to avoid re-proposing failed ideas.
        """
        penalty = 0.0
        for entry in self.entries.values():
            t = entry["theory"]
            sig = f"{t.name}:{[c.statement for c in t.core_claims]}"
            if theory_signature == sig:
                penalty += 0.5 * (1 + entry.get("resurrection_count", 0))
        return min(penalty, 5.0)  # Cap penalty
    
    @property
    def size(self) -> int:
        return len(self.entries)


# ============================================================================
# Meta-Strategy Memory: How the system learns
# ============================================================================

class MetaStrategyMemory:
    """
    Tier 1: Which reasoning strategies worked in which domains.
    Updated by L6 after each research cycle.
    Makes THEORIA a learning scientist.
    """
    
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}  # strategy_id -> Strategy
        self.domain_performance: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )  # domain -> strategy_id -> quality scores
        self.strategy_inventions: List[Dict[str, Any]] = []
        self.cross_domain_transfers: List[Dict[str, Any]] = []
        
    def register_strategy(self, strategy: Strategy) -> None:
        """Register a strategy (built-in or L6-invented)."""
        self.strategies[strategy.id] = strategy
    
    def record_performance(self, strategy_id: str, domain: str, 
                          quality: float, compute: float) -> None:
        """Record strategy performance in a domain."""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].historical_performance.append(
                (domain, quality, compute)
            )
        self.domain_performance[domain][strategy_id].append(quality)
    
    def get_best_for_domain(self, domain: str, 
                            top_k: int = 3) -> List[Tuple[str, float]]:
        """Get best strategies for a domain."""
        scores = []
        for sid, qualities in self.domain_performance[domain].items():
            avg_quality = np.mean(qualities) if qualities else 0.0
            scores.append((sid, avg_quality))
        return sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
    
    def record_invention(self, strategy: Strategy, 
                        triggered_by: str) -> None:
        """Record that L6 invented a new strategy."""
        self.strategy_inventions.append({
            "strategy_id": strategy.id,
            "name": strategy.name,
            "invented_by": strategy.invented_by,
            "triggered_by": triggered_by,
            "timestamp": time.time(),
        })
    
    def record_transfer(self, strategy_id: str, 
                       from_domain: str, to_domain: str,
                       quality_in_new: float) -> None:
        """Record a cross-domain strategy transfer."""
        self.cross_domain_transfers.append({
            "strategy_id": strategy_id,
            "from": from_domain,
            "to": to_domain,
            "quality": quality_in_new,
            "timestamp": time.time(),
        })
    
    def get_strategy_library(self) -> Dict[str, Dict[str, Any]]:
        """Get queryable strategy library."""
        library = {}
        for sid, strat in self.strategies.items():
            library[sid] = {
                "name": strat.name,
                "type": strat.strategy_type.name if strat.strategy_type else "meta",
                "is_invented": strat.is_invented,
                "expected_value": strat.expected_value,
                "average_cost": strat.average_cost,
                "preconditions": strat.preconditions,
                "performance_count": len(strat.historical_performance),
            }
        return library
    
    @property
    def size(self) -> int:
        return len(self.strategies)


# ============================================================================
# Unified Memory Architecture
# ============================================================================

class MemoryArchitecture:
    """
    The five interconnected stores with two-tier forgetting.
    Central coordinator for all memory operations.
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.theory = TheoryMemory()
        self.graveyard = Graveyard()
        self.meta_strategy = MetaStrategyMemory()
        
        # Audit log (public registry)
        self.audit_log: deque = deque(maxlen=10000)
        self.tripwire_log: deque = deque(maxlen=1000)
        
        # Replication-aware field credibility
        self.field_credibility: Dict[str, float] = defaultdict(lambda: 1.0)
        self.field_replication_rates: Dict[str, List[bool]] = defaultdict(list)
        
    def log_audit(self, entry: AuditLogEntry) -> None:
        """Log an audit event to the public registry."""
        self.audit_log.append(entry)
    
    def log_tripwire(self, event: TripwireEvent) -> None:
        """Log a tripwire activation."""
        self.tripwire_log.append(event)
    
    def update_field_replication(self, field: str, replicated: bool) -> None:
        """Update replication tracking for a field."""
        self.field_replication_rates[field].append(replicated)
        
        # Compute field credibility discount epsilon_field
        history = self.field_replication_rates[field]
        if len(history) >= 10:
            rate = sum(history[-50:]) / len(history[-50:])
            # Low replication rate -> high discount
            self.field_credibility[field] = max(0.1, rate)
    
    def get_field_credibility(self, field: str) -> float:
        """Get epsilon_field for a field."""
        return self.field_credibility[field]
    
    def memory_summary(self) -> Dict[str, Any]:
        """Summary statistics for all memory stores."""
        return {
            "episodic": {
                "size": self.episodic.size,
                "compression_ratio": self.episodic.compression_ratio,
                "modalities": dict(self.episodic.modality_stats),
            },
            "semantic": {"size": self.semantic.size},
            "theory": {
                "active": len(self.theory.get_active()),
                "total_registered": self.theory.size,
            },
            "graveyard": {
                "size": self.graveyard.size,
                "rejection_reasons": dict(self.graveyard.rejection_reasons),
                "resurrection_signals": len(self.graveyard.resurrection_signals),
            },
            "meta_strategy": {
                "strategies": self.meta_strategy.size,
                "inventions": len(self.meta_strategy.strategy_inventions),
                "transfers": len(self.meta_strategy.cross_domain_transfers),
            },
            "audit_log": len(self.audit_log),
            "tripwire_log": len(self.tripwire_log),
            "fields_tracked": len(self.field_credibility),
        }
