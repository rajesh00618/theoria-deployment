"""
Phase 3: Paper Generation (P3.5).

Auto-generates scientific papers from experiments:
Abstract, Methods, Results, Discussion, References.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import (
    Theory, Evidence, ExperimentDesign, ExperimentResult,
    PaperDraft, PaperSection, CandidateHypothesis,
)


class PaperGenerator:
    """
    Generates structured scientific papers from theories and experimental results.
    Produces Abstract, Methods, Results, Discussion, References.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.papers: Dict[str, PaperDraft] = {}
        self.publication_history: List[Dict[str, Any]] = []

    def generate(self, theory: Theory, design: ExperimentDesign,
                 result: ExperimentResult,
                 title: Optional[str] = None) -> PaperDraft:
        paper = PaperDraft(
            title=title or f"Experimental Test of {theory.name}",
            hypothesis_id=theory.id,
            experiment_id=design.id,
            result_id=result.id,
        )

        paper.abstract = self._generate_abstract(theory, design, result)
        paper.methods = self._generate_methods(design)
        paper.results = self._generate_results(result)
        paper.discussion = self._generate_discussion(theory, result)
        paper.references = self._generate_references(theory)

        sections = [
            PaperSection(heading="Introduction", content=self._generate_introduction(theory)),
            PaperSection(heading="Methods", content=paper.methods.content),
            PaperSection(heading="Results", content=paper.results.content),
            PaperSection(heading="Discussion", content=paper.discussion.content),
            PaperSection(heading="Conclusion", content=self._generate_conclusion(theory, result)),
        ]
        paper.sections = sections
        paper.word_count = sum(len(s.content.split()) for s in sections)
        paper.quality_score = self._score_quality(paper, result)

        self.papers[paper.id] = paper
        self.publication_history.append({
            "paper_id": paper.id,
            "title": paper.title,
            "timestamp": time.time(),
        })
        return paper

    def _generate_abstract(self, theory: Theory, design: ExperimentDesign,
                           result: ExperimentResult) -> str:
        parts = [
            f"We present an experimental test of {theory.name}.",
        ]

        if theory.core_claims:
            parts.append(f"The theory posits: {'; '.join(c.statement for c in theory.core_claims[:2])}.")

        parts.append(f"We designed a controlled experiment with {len(design.independent_variables)} "
                     f"independent variables and {design.num_trials} trials.")

        if not result.inconclusive:
            if result.supports_hypothesis:
                parts.append(f"The results support the theoretical prediction "
                             f"(effect size={result.effect_size:.2f}, p={result.p_value:.3f}).")
            else:
                parts.append(f"The results contradict the theoretical prediction "
                             f"(effect size={result.effect_size:.2f}, p={result.p_value:.3f}).")
        else:
            parts.append("The results were inconclusive, suggesting the need for refined measurements.")

        return " ".join(parts)

    def _generate_introduction(self, theory: Theory) -> str:
        parts = [
            f"The relationship between {', '.join(theory.reference_class[:3])} "
            f"has been a subject of scientific inquiry.",
        ]
        for claim in theory.core_claims[:2]:
            parts.append(f"Previous work suggests that {claim.statement}.")
        parts.append(f"In this work, we experimentally test these theoretical predictions.")
        return " ".join(parts)

    def _generate_methods(self, design: ExperimentDesign) -> PaperSection:
        content_parts = [
            f"Experimental Design.",
            f"We designed a controlled experiment with {len(design.independent_variables)} "
            f"independent variables and {len(design.dependent_variables)} dependent variables."
        ]

        if design.independent_variables:
            iv_desc = "; ".join(f"{v.name} ({v.range[0]}-{v.range[1]})"
                               for v in design.independent_variables)
            content_parts.append(f"Independent variables: {iv_desc}.")

        if design.dependent_variables:
            content_parts.append(f"Dependent variables: {', '.join(design.dependent_variables)}.")

        if design.controls:
            c_desc = "; ".join(f"{c.variable}={c.value}" for c in design.controls)
            content_parts.append(f"Controls: {c_desc}.")

        content_parts.append(f"Intervention: {design.intervention_description}.")
        content_parts.append(f"A total of {design.num_trials} trials were conducted "
                             f"with {'randomized' if design.randomize else 'fixed'} assignment.")
        content_parts.append(f"Blinding: {design.blinding}.")

        return PaperSection(
            heading="Methods",
            content="\n".join(content_parts),
        )

    def _generate_results(self, result: ExperimentResult) -> PaperSection:
        content_parts = ["Results."]

        if result.trials:
            dv_vals = defaultdict(list)
            for t in result.trials:
                for dv, val in t.dependent_vars.items():
                    dv_vals[dv].append(val)

            for dv, vals in dv_vals.items():
                content_parts.append(
                    f"{dv}: mean={np.mean(vals):.2f}, std={np.std(vals):.2f}, "
                    f"n={len(vals)}."
                )

        content_parts.append(
            f"Statistical analysis revealed: effect size={result.effect_size:.2f}, "
            f"p-value={result.p_value:.3f}, Bayes factor={result.bayes_factor:.2f}."
        )

        if result.supports_hypothesis:
            content_parts.append("The data support the theoretical prediction.")
        elif result.contradicts_hypothesis:
            content_parts.append("The data contradict the theoretical prediction.")
        else:
            content_parts.append("The data are inconclusive with respect to the prediction.")

        return PaperSection(
            heading="Results",
            content="\n".join(content_parts),
        )

    def _generate_discussion(self, theory: Theory, result: ExperimentResult) -> PaperSection:
        content_parts = ["Discussion."]

        if result.supports_hypothesis:
            content_parts.append(
                f"Our results provide empirical support for {theory.name}. "
                f"The observed effect size of {result.effect_size:.2f} is consistent "
                f"with the theoretical framework."
            )
        elif result.contradicts_hypothesis:
            content_parts.append(
                f"Our results challenge {theory.name}. "
                f"The discrepancy between predicted and observed outcomes suggests "
                f"that the theory may require modification."
            )
        else:
            content_parts.append(
                "The inconclusive results highlight the need for more "
                "powerful experimental designs or refined theoretical predictions."
            )

        content_parts.append(
            f"A limitation of this study is the sample size of {len(result.trials)} trials, "
            f"which may limit statistical power."
        )
        content_parts.append(
            "Future work should replicate these findings with independent "
            "methodologies and explore broader parameter ranges."
        )

        return PaperSection(
            heading="Discussion",
            content="\n".join(content_parts),
        )

    def _generate_conclusion(self, theory: Theory, result: ExperimentResult) -> str:
        if result.supports_hypothesis:
            return (f"We conclude that the experimental evidence supports {theory.name}. "
                    f"This contributes to our understanding of {'/'.join(theory.reference_class[:3])}.")
        elif result.contradicts_hypothesis:
            return (f"We conclude that the experimental evidence contradicts {theory.name}. "
                    f"Revision of the theoretical framework is warranted.")
        return ("Further investigation is needed to resolve the experimental outcomes "
                "with theoretical predictions.")

    def _generate_references(self, theory: Theory) -> List[str]:
        refs = []
        refs.append(f"{theory.name} (THEORIA internal theory, {time.strftime('%Y')})")
        for i, claim in enumerate(theory.core_claims[:3]):
            refs.append(f"Core claim {i+1}: {claim.statement[:80]}")
        return refs

    def _score_quality(self, paper: PaperDraft, result: ExperimentResult) -> float:
        score = 0.5
        if len(paper.abstract) >= 100:
            score += 0.1
        if len(paper.sections) >= 4:
            score += 0.1
        if result.effect_size > 0.3:
            score += 0.1
        if result.p_value < 0.05:
            score += 0.1
        if result.bayes_factor > 3:
            score += 0.1
        return float(min(1.0, max(0.0, score)))

    def get_paper(self, paper_id: str) -> Optional[PaperDraft]:
        return self.papers.get(paper_id)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_papers": len(self.papers),
            "avg_quality": (
                float(np.mean([p.quality_score for p in self.papers.values()]))
                if self.papers else 0
            ),
            "papers": [
                {"id": pid, "title": p.title, "quality": p.quality_score, "words": p.word_count}
                for pid, p in self.papers.items()
            ],
        }
