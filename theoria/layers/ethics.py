"""
Phase 4: Values & Ethics Layer (P4.5 / L10).

Dual-use detection, ethics review, risk scoring, red-line enforcement.
Determines whether experiments should be performed, whether knowledge
should be restricted, and whether harm could result.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from theoria.core.types import EthicsReview, SafetyLevel


class EthicsLayer:
    """
    Ethics review and dual-use detection for THEORIA.
    Reviews theories, experiments, papers before they are executed/published.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.reviews: Dict[str, EthicsReview] = {}
        self.red_lines: Set[str] = set()
        self.ethics_log: List[Dict[str, Any]] = []
        self._init_red_lines()

    def _init_red_lines(self):
        self.red_lines = {
            "enhanced_pathogen_design",
            "autonomous_weapons_targeting",
            "mass_surveillance_architecture",
            "manipulation_campaign",
            "chemical_weapons_synthesis",
            "nuclear_proliferation",
            "human_enhancement_ethically_restricted",
            "privacy_violation_at_scale",
        }

    def review_theory(self, theory_id: str, domain: str,
                      claims: List[str]) -> EthicsReview:
        issues = []
        risk_score = 0.0
        text = " ".join(claims).lower()
        for red_line in self.red_lines:
            keywords = red_line.split("_")
            if any(kw in text for kw in keywords):
                issues.append(f"Potential red line violation: {red_line}")
                risk_score += 0.3
        if "weapon" in text or "harm" in text:
            issues.append("Dual-use concern: weaponization potential")
            risk_score += 0.2
        if "human" in text and ("trial" in text or "experiment" in text):
            issues.append("Ethics concern: human subjects")
            risk_score += 0.15
        risk_level, recommendation = self._classify_risk(risk_score)
        review = EthicsReview(
            subject_type="theory", subject_id=theory_id,
            risk_level=risk_level, risk_score=min(risk_score, 1.0),
            issues_found=issues, recommendation=recommendation,
        )
        self.reviews[review.id] = review
        self.ethics_log.append({
            "time": time.time(), "type": "theory_review",
            "subject": theory_id, "risk": risk_level,
        })
        return review

    def review_experiment(self, design_id: str, domain: str,
                          description: str,
                          independent_vars: List[str]) -> EthicsReview:
        issues = []
        risk_score = 0.0
        text = (description + " " + " ".join(independent_vars)).lower()
        if "human" in text or "patient" in text or "subject" in text:
            issues.append("Human subjects research requires IRB approval")
            risk_score += 0.25
        if "dangerous" in text or "hazard" in text or "toxic" in text:
            issues.append("Physical hazard detected")
            risk_score += 0.2
        if "privacy" in text or "surveillance" in text:
            issues.append("Privacy concern")
            risk_score += 0.2
        for rl in self.red_lines:
            if rl.replace("_", " ") in text:
                issues.append(f"Red line: {rl}")
                risk_score += 0.5
        risk_level, recommendation = self._classify_risk(risk_score)
        review = EthicsReview(
            subject_type="experiment", subject_id=design_id,
            risk_level=risk_level, risk_score=min(risk_score, 1.0),
            issues_found=issues, recommendation=recommendation,
        )
        self.reviews[review.id] = review
        return review

    def review_paper(self, paper_id: str, title: str,
                     abstract: str) -> EthicsReview:
        issues = []
        risk_score = 0.0
        text = (title + " " + abstract).lower()
        if any(rl.replace("_", " ") in text for rl in self.red_lines):
            issues.append("Red line content in publication")
            risk_score += 0.4
        if "method" in text and ("dangerous" in text or "harmful" in text):
            issues.append("Dual-use methodology described")
            risk_score += 0.2
        risk_level, recommendation = self._classify_risk(risk_score)
        review = EthicsReview(
            subject_type="paper", subject_id=paper_id,
            risk_level=risk_level, risk_score=min(risk_score, 1.0),
            issues_found=issues, recommendation=recommendation,
        )
        self.reviews[review.id] = review
        return review

    def _classify_risk(self, score: float) -> Tuple[str, str]:
        thresholds = self.config.risk_thresholds if self.config else {
            "safe": 0.3, "review": 0.6, "dual_use": 0.8, "red_line": 1.0
        }
        if score >= thresholds.get("red_line", 1.0):
            return ("red_line", "blocked")
        elif score >= thresholds.get("dual_use", 0.8):
            return ("dual_use", "restricted")
        elif score >= thresholds.get("review", 0.6):
            return ("review", "requires_human_review")
        return ("safe", "proceed")

    def get_restricted_count(self) -> int:
        return sum(1 for r in self.reviews.values()
                   if r.risk_level in ("dual_use", "red_line"))

    def get_summary(self) -> Dict[str, Any]:
        levels = {"safe": 0, "review": 0, "dual_use": 0, "red_line": 0}
        for r in self.reviews.values():
            levels[r.risk_level] = levels.get(r.risk_level, 0) + 1
        return {
            "total_reviews": len(self.reviews),
            "risk_levels": levels,
            "restricted": self.get_restricted_count(),
            "red_lines_configured": len(self.red_lines),
        }
