"""
Phase 4: Communication Layer (P4.4 / L9).

Generates research papers, presentations, posters, technical reports,
grant proposals, lecture notes, and visualizations from research data.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import Presentation, GrantProposal
from theoria.core.types import CrossDomainMapping, Theory, ExperimentResult


class CommunicationLayer:
    """
    Generates multiple output formats from THEORIA's research.
    Papers, talks, posters, grants, reports, lecture notes.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.presentations: Dict[str, Presentation] = {}
        self.proposals: Dict[str, GrantProposal] = {}
        self.reports: Dict[str, Dict[str, Any]] = {}

    def generate_presentation(self, title: str, domain: str,
                              findings: List[str], event_type: str = "conference",
                              duration: int = 20) -> Presentation:
        slides = [
            f"Slide 1: Title — {title}",
            f"Slide 2: Motivation — Why {domain} matters",
            f"Slide 3: Background — Prior work in {domain}",
            f"Slide 4: Research Question — Core inquiry",
            f"Slide 5-8: Methods — Experimental approach",
            f"Slide 9-12: Results — Key findings",
            f"Slide 13-14: Discussion — Interpretation",
            f"Slide 15: Conclusions & Future Work",
        ]
        for i, finding in enumerate(findings[:5]):
            idx = 5 + i
            if idx < len(slides):
                slides[idx] += f" | {finding}"
        pres = Presentation(
            title=title, event_type=event_type,
            slides=slides, duration_minutes=duration,
        )
        self.presentations[pres.id] = pres
        return pres

    def generate_grant_proposal(self, title: str, domain: str, summary: str,
                                objectives: List[str], budget: float = 500000.0) -> GrantProposal:
        proposal = GrantProposal(
            title=title, summary=summary,
            objectives=objectives,
            methodology=f"We will investigate {title} using THEORIA's autonomous "
                        f"scientific framework across {domain}.",
            expected_outcomes=[
                f"Novel theories in {domain}",
                f"Experimental validation of predictions",
                f"Publication in peer-reviewed venues",
                f"Open-source tools for the community",
            ],
            budget_requested=budget,
            score=min(1.0, 0.3 + len(objectives) * 0.05 + (budget < 1e6) * 0.2),
        )
        self.proposals[proposal.id] = proposal
        return proposal

    def generate_technical_report(self, title: str, domain: str,
                                  sections: Dict[str, str]) -> Dict[str, Any]:
        report = {
            "id": str(uuid.uuid4())[:8],
            "title": title,
            "domain": domain,
            "generated_at": time.time(),
            "sections": sections,
            "word_count": sum(len(v.split()) for v in sections.values()),
        }
        self.reports[report["id"]] = report
        return report

    def generate_visualization_spec(self, data_type: str, domain: str,
                                    variables: List[str]) -> Dict[str, Any]:
        chart_type = {
            "comparison": "bar_chart",
            "trend": "line_chart",
            "distribution": "histogram",
            "correlation": "scatter_plot",
            "composition": "pie_chart",
            "network": "graph",
        }.get(data_type, "line_chart")
        return {
            "chart_type": chart_type,
            "domain": domain,
            "variables": variables,
            "title": f"{' vs '.join(variables[:2])} in {domain}",
            "recommended_width": 800,
            "recommended_height": 500,
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "presentations": len(self.presentations),
            "grant_proposals": len(self.proposals),
            "technical_reports": len(self.reports),
        }
