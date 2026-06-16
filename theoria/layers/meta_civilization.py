from __future__ import annotations

import uuid
import hashlib
import random
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import (
    MetaScienceFinding, CivilizationMetrics, ResearchAgenda,
)


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).digest()
    return (h[0] + h[1]) / 510.0


@dataclass
class MetaScienceResult:
    findings: List[MetaScienceFinding] = field(default_factory=list)
    findings_generated: int = 0
    best_evidence_strength: float = 0.0


@dataclass
class AnalyticsResult:
    metrics: CivilizationMetrics = field(default_factory=CivilizationMetrics)
    health_trend: str = "stable"
    innovation_trend: str = "stable"


@dataclass
class GoalGenerationResult:
    agendas: List[ResearchAgenda] = field(default_factory=list)
    agendas_generated: int = 0
    best_score: float = 0.0


class MetaScienceEngine:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.findings: List[MetaScienceFinding] = []
        self.cycle_count = 0

    def analyze_method_effectiveness(self, method_stats: Dict[str, float]) -> List[MetaScienceFinding]:
        findings = []
        for method, effectiveness in method_stats.items():
            if effectiveness > 0.6:
                finding = MetaScienceFinding(
                    title=f"Method effectiveness: {method}",
                    description=f"{method} shows {effectiveness:.1%} effectiveness",
                    finding_type="method_effectiveness",
                    domain="meta",
                    evidence_strength=effectiveness,
                    confidence=min(1.0, effectiveness + 0.1),
                    supporting_data={"method": method, "effectiveness": effectiveness},
                    implication=f"Prioritize {method} for research",
                )
                findings.append(finding)
                self.findings.append(finding)
        return findings

    def analyze_theory_longevity(self, theory_lifetimes: Dict[str, int]) -> List[MetaScienceFinding]:
        findings = []
        for theory_name, lifetime in theory_lifetimes.items():
            if lifetime > 10:
                finding = MetaScienceFinding(
                    title=f"Theory longevity: {theory_name}",
                    description=f"{theory_name} survived {lifetime} cycles",
                    finding_type="theory_longevity",
                    domain="meta",
                    evidence_strength=min(1.0, lifetime / 50),
                    confidence=min(1.0, lifetime / 30),
                    supporting_data={"theory": theory_name, "lifetime_cycles": lifetime},
                    implication="Robust theoretical framework identified",
                )
                findings.append(finding)
                self.findings.append(finding)
        return findings

    def analyze_experiment_informativeness(self, experiment_results: List[Dict[str, Any]]) -> List[MetaScienceFinding]:
        findings = []
        for exp in experiment_results[:10]:
            info_gain = exp.get("information_gain", 0)
            if info_gain > 0.3:
                finding = MetaScienceFinding(
                    title=f"Informative experiment: {exp.get('name', 'unknown')}",
                    description=f"Experiment yielded {info_gain:.1%} information gain",
                    finding_type="experiment_informativeness",
                    domain=exp.get("domain", "general"),
                    evidence_strength=info_gain,
                    confidence=min(1.0, info_gain + 0.2),
                    supporting_data=exp,
                    implication="High-yield experimental design identified",
                )
                findings.append(finding)
                self.findings.append(finding)
        return findings

    def run_cycle(self, method_stats: Dict[str, float],
                  theory_lifetimes: Dict[str, int],
                  experiment_results: List[Dict[str, Any]]) -> MetaScienceResult:
        findings = []
        if self.config and getattr(self.config, 'track_method_effectiveness', True):
            findings.extend(self.analyze_method_effectiveness(method_stats))
        if self.config and getattr(self.config, 'track_theory_longevity', True):
            findings.extend(self.analyze_theory_longevity(theory_lifetimes))
        if self.config and getattr(self.config, 'track_experiment_informativeness', True):
            findings.extend(self.analyze_experiment_informativeness(experiment_results))

        self.cycle_count += 1
        best_strength = max((f.evidence_strength for f in findings), default=0)
        return MetaScienceResult(
            findings=findings,
            findings_generated=len(findings),
            best_evidence_strength=best_strength,
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_findings": len(self.findings),
            "by_type": dict((ft, sum(1 for f in self.findings if f.finding_type == ft))
                           for ft in ["method_effectiveness", "experiment_informativeness", "theory_longevity"]),
            "avg_confidence": np.mean([f.confidence for f in self.findings]) if self.findings else 0,
        }


class CivilizationAnalytics:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.history: List[CivilizationMetrics] = []
        self.cycle_count = 0

    def compute_metrics(self, agent_data: Dict[str, Any],
                        theory_data: Dict[str, Any],
                        experiment_data: Dict[str, Any],
                        society_data: Dict[str, Any]) -> CivilizationMetrics:
        agent_productivity = agent_data.get("avg_productivity", 0.5)
        theory_quality = theory_data.get("avg_quality", 0.5)
        active_theories = theory_data.get("active_count", 0)
        total_experiments = experiment_data.get("total", 0)
        total_papers = society_data.get("total_papers", 0)
        collaborations = society_data.get("collaborations", 0)
        agents = society_data.get("agent_count", 100)
        collaboration_density = collaborations / max(agents, 1)

        discovery_rate = experiment_data.get("discoveries_per_cycle", 0)
        paradigm_shifts = theory_data.get("paradigm_shifts", 0)
        paradigm_shift_rate = paradigm_shifts / max(self.cycle_count, 1)

        resource_efficiency = experiment_data.get("resource_efficiency", 0.5)

        health_score = (
            0.25 * agent_productivity +
            0.25 * theory_quality +
            0.20 * collaboration_density +
            0.15 * resource_efficiency +
            0.15 * min(1.0, active_theories / 20)
        )

        innovation_score = (
            0.30 * discovery_rate +
            0.30 * theory_data.get("novelty_rate", 0.5) +
            0.20 * paradigm_shift_rate +
            0.20 * experiment_data.get("breakthrough_rate", 0.1)
        )

        civilization_score = 0.5 * health_score + 0.5 * innovation_score

        metrics = CivilizationMetrics(
            health_score=health_score,
            civilization_score=civilization_score,
            innovation_score=innovation_score,
            agent_productivity=agent_productivity,
            theory_quality=theory_quality,
            paradigm_shift_rate=paradigm_shift_rate,
            discovery_rate=discovery_rate,
            total_experiments=total_experiments,
            active_theories=active_theories,
            total_papers=total_papers,
            collaboration_density=collaboration_density,
            resource_efficiency=resource_efficiency,
        )

        self.history.append(metrics)
        self.cycle_count += 1
        return metrics

    def get_health_trend(self) -> str:
        if len(self.history) < 3:
            return "stable"
        recent = [m.health_score for m in self.history[-5:]]
        if len(recent) >= 2 and recent[-1] > recent[0] * 1.05:
            return "improving"
        elif len(recent) >= 2 and recent[-1] < recent[0] * 0.95:
            return "declining"
        return "stable"

    def get_innovation_trend(self) -> str:
        if len(self.history) < 3:
            return "stable"
        recent = [m.innovation_score for m in self.history[-5:]]
        if len(recent) >= 2 and recent[-1] > recent[0] * 1.05:
            return "accelerating"
        elif len(recent) >= 2 and recent[-1] < recent[0] * 0.95:
            return "decelerating"
        return "stable"

    def get_summary(self) -> Dict[str, Any]:
        return {
            "cycles_tracked": len(self.history),
            "latest_health": self.history[-1].health_score if self.history else 0,
            "latest_civilization": self.history[-1].civilization_score if self.history else 0,
            "latest_innovation": self.history[-1].innovation_score if self.history else 0,
            "health_trend": self.get_health_trend(),
            "innovation_trend": self.get_innovation_trend(),
        }


class GoalGeneration:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.agendas: List[ResearchAgenda] = []
        self.cycle_count = 0

    def generate_agenda(self, domain: str, gaps: List[str],
                        existing_theories: int) -> ResearchAgenda:
        agenda_types = ["ten_year_program", "new_field", "new_civilization"]
        agenda_type = random.choice(agenda_types)

        objectives = [
            f"Characterize fundamental {domain} phenomena",
            f"Develop predictive models for {domain} systems",
            f"Create experimental frameworks for {domain}",
            f"Establish theoretical foundations for {domain}",
            f"Bridge {domain} with adjacent domains",
            f"Invent new mathematical tools for {domain}",
        ]

        milestones = [
            {"cycle": 10, "description": f"Initial {domain} survey complete", "status": "pending"},
            {"cycle": 50, "description": f"First {domain} theory established", "status": "pending"},
            {"cycle": 100, "description": f"{domain} predictive models validated", "status": "pending"},
            {"cycle": 200, "description": f"{domain} paradigm consolidation", "status": "pending"},
        ]

        agenda = ResearchAgenda(
            title=f"{domain.upper()}: {agenda_type.replace('_', ' ').title()}",
            description=f"A {agenda_type} to advance {domain} research over {getattr(self.config, 'horizon_years', 10)} years",
            agenda_type=agenda_type,
            domain=domain,
            objectives=objectives[:3 + len(gaps) % 3],
            milestones=milestones,
            expected_outcomes=[
                f"New theories of {domain}",
                "Published research program",
                f"Cross-domain applications of {domain} insights",
            ],
            resource_estimate=0.3 + _det_score(f"resource_{domain}_{self.cycle_count}") * 0.7,
            novelty_score=0.4 + _det_score(f"novelty_{domain}_{self.cycle_count}") * 0.5,
            feasibility_score=0.3 + _det_score(f"feasibility_{domain}_{self.cycle_count}") * 0.5,
            impact_score=0.5 + _det_score(f"impact_{domain}_{self.cycle_count}") * 0.45,
        )

        self.agendas.append(agenda)
        self.cycle_count += 1
        return agenda

    def execute_agenda(self, agenda_id: str, progress_increment: float = 0.01) -> Optional[ResearchAgenda]:
        for a in self.agendas:
            if a.id == agenda_id:
                a.progress = min(1.0, a.progress + progress_increment)
                if a.progress >= 1.0:
                    a.status = "completed"
                return a
        return None

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_agendas": len(self.agendas),
            "active": sum(1 for a in self.agendas if a.status == "proposed"),
            "completed": sum(1 for a in self.agendas if a.status == "completed"),
            "avg_impact": np.mean([a.impact_score for a in self.agendas]) if self.agendas else 0,
        }


class MetaCivilizationLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.meta_science = MetaScienceEngine(config.meta_science if config else None)
        self.analytics = CivilizationAnalytics(config.civilization_analytics if config else None)
        self.goal_generation = GoalGeneration(config.goal_generation if config else None)

    def run_cycle(self, method_stats: Dict[str, float],
                  theory_lifetimes: Dict[str, int],
                  experiment_results: List[Dict[str, Any]],
                  agent_data: Dict[str, Any],
                  theory_data: Dict[str, Any],
                  experiment_data: Dict[str, Any],
                  society_data: Dict[str, Any],
                  gaps: List[str],
                  existing_theories: int) -> Dict[str, Any]:
        result = {}

        meta_result = self.meta_science.run_cycle(method_stats, theory_lifetimes, experiment_results)
        result["meta_findings"] = meta_result.findings_generated
        result["meta_best_evidence"] = meta_result.best_evidence_strength

        metrics = self.analytics.compute_metrics(agent_data, theory_data, experiment_data, society_data)
        result["health_score"] = metrics.health_score
        result["civilization_score"] = metrics.civilization_score
        result["innovation_score"] = metrics.innovation_score
        result["health_trend"] = self.analytics.get_health_trend()
        result["innovation_trend"] = self.analytics.get_innovation_trend()

        if gaps and random.random() < 0.3:
            domain = gaps[0] if isinstance(gaps[0], str) else "general"
            agenda = self.goal_generation.generate_agenda(
                domain, gaps[:3], existing_theories
            )
            result["agenda_generated"] = agenda.id

        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "meta_science": self.meta_science.get_summary(),
            "analytics": self.analytics.get_summary(),
            "goal_generation": self.goal_generation.get_summary(),
        }
