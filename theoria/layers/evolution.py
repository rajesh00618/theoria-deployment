"""
Phase 4: Knowledge Evolution Engine (P4.10).

Tracks theory lifetimes, paradigm shifts, scientific revolutions.
Inspired by Thomas Kuhn, Lakatos, and Popper.
THEORIA starts modeling science itself.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import TheoryEpoch, Theory, ParadigmEvent


class KnowledgeEvolution:
    """
    Tracks the evolution of scientific knowledge over time.
    Measures theory lifetimes, detects paradigm shifts and revolutions.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.epochs: Dict[str, TheoryEpoch] = {}
        self.paradigm_shifts: List[Dict[str, Any]] = []
        self.domain_eras: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def register_theory(self, theory: Theory, paradigm: str = "normal") -> TheoryEpoch:
        epoch = TheoryEpoch(
            theory_id=theory.id,
            theory_name=theory.name,
            domain=theory.domain.conditions[0] if theory.domain.conditions else "general",
            proposed_at=time.time(),
            paradigm=paradigm,
            influence_score=float(theory.posterior),
        )
        self.epochs[theory.id] = epoch
        return epoch

    def falsify_theory(self, theory_id: str, descendants: Optional[List[str]] = None) -> Optional[TheoryEpoch]:
        epoch = self.epochs.get(theory_id)
        if not epoch:
            return None
        epoch.falsified_at = time.time()
        lifetime = epoch.falsified_at - epoch.proposed_at
        epoch.lifetime_cycles = int(lifetime / 10) + 1
        if descendants:
            epoch.descendant_ids.extend(descendants)
        self._check_paradigm_shift(epoch)
        return epoch

    def _check_paradigm_shift(self, epoch: TheoryEpoch) -> Optional[Dict[str, Any]]:
        target_domain = epoch.domain
        recent = [e for e in self.epochs.values()
                  if e.domain == target_domain and e.falsified_at is not None]
        if len(recent) < 5:
            return None
        falsification_rate = len(recent) / max(time.time() - min(e.proposed_at for e in recent), 1)
        threshold = self.config.shift_threshold if self.config else 0.6
        if falsification_rate > threshold:
            shift = {
                "domain": target_domain,
                "type": "paradigm_shift",
                "timestamp": time.time(),
                "trigger": f"High falsification rate ({falsification_rate:.2f})",
                "falsified_count": len(recent),
                "severity": min(1.0, falsification_rate),
            }
            self.paradigm_shifts.append(shift)
            self.domain_eras[target_domain].append(shift)
            return shift
        return None

    def detect_revolution(self, domain: str) -> Optional[Dict[str, Any]]:
        shifts = self.domain_eras.get(domain, [])
        if len(shifts) >= 3:
            recent = shifts[-3:]
            times = [s["timestamp"] for s in recent]
            if max(times) - min(times) < 1000:
                revolution = {
                    "domain": domain,
                    "type": "scientific_revolution",
                    "timestamp": time.time(),
                    "triggered_by": len(shifts),
                    "description": f"Multiple paradigm shifts in {domain} indicate a revolution",
                    "severity": min(1.0, len(shifts) * 0.25),
                }
                self.paradigm_shifts.append(revolution)
                return revolution
        return None

    def average_theory_lifetime(self, domain: Optional[str] = None) -> float:
        falsified = [e for e in self.epochs.values()
                     if e.falsified_at is not None and
                     (domain is None or e.domain == domain)]
        if not falsified:
            return 0.0
        lifetimes = [(e.falsified_at - e.proposed_at) for e in falsified]
        return float(np.mean(lifetimes)) if lifetimes else 0.0

    def get_summary(self) -> Dict[str, Any]:
        active = sum(1 for e in self.epochs.values() if e.falsified_at is None)
        falsified = sum(1 for e in self.epochs.values() if e.falsified_at is not None)
        return {
            "total_theories_tracked": len(self.epochs),
            "active_theories": active,
            "falsified_theories": falsified,
            "paradigm_shifts": len(self.paradigm_shifts),
            "revolutions": sum(1 for s in self.paradigm_shifts if s["type"] == "scientific_revolution"),
            "avg_lifetime_seconds": self.average_theory_lifetime(),
        }
