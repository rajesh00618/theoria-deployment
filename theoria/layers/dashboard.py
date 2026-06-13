"""
Phase 2: Autonomous Discovery Dashboard.

Monitors ongoing research:
- Concepts discovered, theories generated/falsified
- Knowledge gaps found, hypotheses proposed
- Research programs active
- Analytics engine with trend detection
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field

from theoria.core.types import (
    DashboardMetrics, Theory, Concept, ResearchGap, ResearchQuestion,
    ResearchProgram, CandidateHypothesis, CriticReport,
    TheoryStatus, ConceptLifecycle,
)
from theoria.core.memory import MemoryArchitecture
from theoria.core.knowledge_graph import KnowledgeGraph


class DiscoveryDashboard:
    """
    Monitoring dashboard for autonomous scientific discovery.
    Tracks metrics, detects trends, and provides system health status.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.metrics_history: List[DashboardMetrics] = []
        self.alerts: deque = deque(maxlen=100)
        self.trends: Dict[str, List[float]] = defaultdict(list)

    def snapshot(self, memory: MemoryArchitecture,
                 cycle_count: int = 0) -> DashboardMetrics:
        """Take a metrics snapshot of the current system state."""
        m = DashboardMetrics()

        concepts = memory.semantic.facts
        if hasattr(memory, 'scientific') and memory.scientific:
            kg = memory.knowledge_graph
            m.kg_nodes = kg.nodes.__len__() if hasattr(kg, 'nodes') else 0
            m.kg_edges = kg.edges.__len__() if hasattr(kg, 'edges') else 0
            m.kg_domains = len(set(
                n.properties.get("domain", "unknown")
                for n in kg.nodes.values()
                if "domain" in n.properties
            ))
            m.kg_clusters = len(kg.clusters) if hasattr(kg, 'clusters') else 0

            sci = memory.scientific
            m.papers_ingested = sci.paper_count
            m.open_gaps = len(sci.get_open_gaps())
            m.open_questions = len(sci.get_open_questions())
            m.active_programs = len(sci.get_active_programs())
            m.critiques_issued = sci.critique_count

        active = memory.theory.get_active()
        m.active_theories = len(active)
        m.total_theories = memory.theory.size

        m.cycles_completed = cycle_count
        m.uptime_hours = self._compute_uptime()

        self.metrics_history.append(m)
        self._update_trends(m)

        if memory.persistent:
            memory.persistent.save_metrics_snapshot(m)

        return m

    def _update_trends(self, metrics: DashboardMetrics) -> None:
        """Update trend data from metrics."""
        self.trends["active_theories"].append(metrics.active_theories)
        self.trends["papers_ingested"].append(metrics.papers_ingested)
        self.trends["open_gaps"].append(metrics.open_gaps)
        self.trends["open_questions"].append(metrics.open_questions)
        self.trends["kg_nodes"].append(metrics.kg_nodes)
        self.trends["kg_edges"].append(metrics.kg_edges)

    def _compute_uptime(self) -> float:
        """Compute system uptime in hours."""
        if not self.metrics_history:
            return 0.0
        first = self.metrics_history[0]
        last = self.metrics_history[-1]
        return (last.timestamp - first.timestamp) / 3600

    def get_latest_metrics(self) -> Optional[DashboardMetrics]:
        """Get the most recent metrics snapshot."""
        return self.metrics_history[-1] if self.metrics_history else None

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in metrics."""
        anomalies = []
        if len(self.metrics_history) < 5:
            return anomalies

        window = self.config.trending_window if self.config else 20
        recent = self.metrics_history[-window:]

        for metric_name in ["active_theories", "open_gaps", "kg_nodes"]:
            values = [getattr(m, metric_name, 0) for m in recent]
            if len(values) >= 5:
                mean = np.mean(values[:-3])
                recent_vals = values[-3:]
                for v in recent_vals:
                    if abs(v - mean) > 2 * np.std(values) + 0.1:
                        anomalies.append({
                            "metric": metric_name,
                            "value": v,
                            "expected": mean,
                            "severity": "warning" if abs(v - mean) > np.std(values) else "info",
                            "timestamp": time.time(),
                        })

        return anomalies

    def get_trend(self, metric_name: str, window: int = 20) -> Dict[str, Any]:
        """Analyze trend for a specific metric."""
        values = self.trends.get(metric_name, [])
        if len(values) < 3:
            return {"stable": True, "direction": "unknown"}

        recent = values[-window:]
        first_half = np.mean(recent[:len(recent)//2])
        second_half = np.mean(recent[len(recent)//2:])

        direction = "increasing" if second_half > first_half * 1.1 else \
                    "decreasing" if second_half < first_half * 0.9 else \
                    "stable"

        return {
            "metric": metric_name,
            "direction": direction,
            "current": recent[-1] if recent else 0,
            "change": recent[-1] - recent[0] if len(recent) > 1 else 0,
            "stable": direction == "stable",
            "values": recent[-10:],
        }

    def add_alert(self, message: str, severity: str = "info") -> None:
        """Add a system alert."""
        self.alerts.append({
            "message": message,
            "severity": severity,
            "timestamp": time.time(),
        })

    def get_health_score(self) -> float:
        """Compute overall system health score (0-1)."""
        if not self.metrics_history:
            return 0.5

        latest = self.metrics_history[-1]

        discovery_score = min(
            latest.active_theories / 10.0,
            1.0,
        )
        knowledge_score = min(
            (latest.kg_nodes + latest.kg_edges) / 1000.0,
            1.0,
        )
        research_score = min(
            (latest.open_gaps + latest.open_questions) / 20.0,
            1.0,
        )

        return 0.4 * discovery_score + 0.3 * knowledge_score + 0.3 * research_score

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get full dashboard data for display."""
        latest = self.get_latest_metrics()
        trends = {}
        for metric in ["active_theories", "papers_ingested", "open_gaps",
                        "open_questions", "kg_nodes", "kg_edges"]:
            trends[metric] = self.get_trend(metric)

        return {
            "metrics": {
                "concepts": latest.total_concepts if latest else 0,
                "active_theories": latest.active_theories if latest else 0,
                "falsified_theories": latest.falsified_theories if latest else 0,
                "kg_nodes": latest.kg_nodes if latest else 0,
                "kg_edges": latest.kg_edges if latest else 0,
                "papers_ingested": latest.papers_ingested if latest else 0,
                "open_gaps": latest.open_gaps if latest else 0,
                "open_questions": latest.open_questions if latest else 0,
                "active_programs": latest.active_programs if latest else 0,
                "cycles": latest.cycles_completed if latest else 0,
            },
            "trends": trends,
            "health_score": self.get_health_score(),
            "alerts": list(self.alerts)[-10:],
            "anomalies": self.detect_anomalies(),
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "snapshots_taken": len(self.metrics_history),
            "alerts_active": len(self.alerts),
            "trends_tracked": len(self.trends),
            "health_score": self.get_health_score(),
            "latest": (
                {
                    "active_theories": self.metrics_history[-1].active_theories,
                    "kg_nodes": self.metrics_history[-1].kg_nodes,
                    "papers": self.metrics_history[-1].papers_ingested,
                    "gaps": self.metrics_history[-1].open_gaps,
                    "questions": self.metrics_history[-1].open_questions,
                    "programs": self.metrics_history[-1].active_programs,
                }
                if self.metrics_history else {}
            ),
        }
