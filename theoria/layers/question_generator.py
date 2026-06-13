"""
Phase 2: Research Question Generator.

Generates meaningful scientific questions from detected knowledge gaps.
Question types: why, how, mechanism, comparison, prediction, what_if.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict

from theoria.core.types import (
    ResearchGap, ResearchQuestion, KGNode, KGNodeType,
)
from collections import Counter


class QuestionGenerator:
    """
    Generates research questions from knowledge gaps.
    Uses templates and novelty/importance scoring.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.questions: List[ResearchQuestion] = []
        self.generation_count: int = 0

        self.question_templates: Dict[str, List[str]] = {
            "why": [
                "Why does {concept_a} exhibit {property} in context of {concept_b}?",
                "Why is {concept_a} related to {concept_b} through {mechanism}?",
                "Why does {concept_a} vary with {concept_b} under {condition}?",
            ],
            "how": [
                "How does {concept_a} influence {concept_b}?",
                "How can {concept_a} be modeled in terms of {concept_b}?",
                "How does the relationship between {concept_a} and {concept_b} depend on {context}?",
            ],
            "mechanism": [
                "What mechanism links {concept_a} and {concept_b}?",
                "What is the causal pathway from {concept_a} to {concept_b}?",
                "What mediates the effect of {concept_a} on {concept_b}?",
            ],
            "comparison": [
                "Which theory best explains {phenomenon}: {theory_a} or {theory_b}?",
                "How does {concept_a} in {domain_a} compare to {concept_b} in {domain_b}?",
                "What are the relative strengths of {theory_a} vs {theory_b} for {phenomenon}?",
            ],
            "prediction": [
                "Can {theory_a} predict {phenomenon} under novel conditions?",
                "What does {theory_a} predict for {concept_b} at extreme values?",
                "If {concept_a} changes, how will {concept_b} respond?",
            ],
            "what_if": [
                "What if {concept_a} and {concept_b} are fundamentally the same phenomenon?",
                "What if the relationship between {concept_a} and {concept_b} is not causal but confounded?",
                "What if {concept_a} is actually a consequence of {concept_b}, not the cause?",
            ],
        }

    def generate_from_gaps(self, gaps: List[ResearchGap],
                           kg_nodes: Optional[Dict[str, KGNode]] = None,
                           max_questions: int = 20) -> List[ResearchQuestion]:
        """Generate research questions from knowledge gaps."""
        self.questions = []
        self.generation_count += 1

        config = self.config
        max_per_gap = config.max_questions_per_gap if config else 5
        templates_to_use = config.question_templates if config else list(self.question_templates.keys())

        for gap in gaps:
            gap_questions = self._generate_for_gap(gap, kg_nodes, templates_to_use)
            self.questions.extend(gap_questions[:max_per_gap])

        min_score = config.min_question_score if config else 0.3
        self.questions = [q for q in self.questions if q.overall_score >= min_score]
        self.questions.sort(key=lambda q: q.overall_score, reverse=True)

        return self.questions[:max_questions]

    def _generate_for_gap(self, gap: ResearchGap,
                           kg_nodes: Optional[Dict[str, KGNode]] = None,
                           template_types: Optional[List[str]] = None) -> List[ResearchQuestion]:
        """Generate questions for a specific gap."""
        questions = []

        if template_types is None:
            template_types = list(self.question_templates.keys())

        node_info = self._get_gap_context(gap, kg_nodes)

        for q_type in template_types:
            templates = self.question_templates.get(q_type, [])
            for template in templates[:2]:
                try:
                    question_text = template.format(**node_info)
                except KeyError:
                    continue

                novelty = self._score_novelty(question_text, gap)
                importance = self._score_importance(question_text, gap, q_type)
                answerability = self._score_answerability(question_text, gap)

                question = ResearchQuestion(
                    id=f"q_{self.generation_count}_{len(questions)}_{int(time.time())}",
                    question_text=question_text,
                    question_type=q_type,
                    source_gap_ids=[gap.id],
                    template_used=template,
                    novelty=novelty,
                    importance=importance,
                    answerability=answerability,
                )
                question.overall_score = (
                    0.35 * question.importance
                    + 0.25 * question.novelty
                    + 0.40 * question.answerability
                )
                questions.append(question)

                if len(questions) >= 5:
                    return questions

        return questions

    def _get_gap_context(self, gap: ResearchGap,
                          kg_nodes: Optional[Dict[str, KGNode]] = None) -> Dict[str, str]:
        """Get template context from gap and nodes."""
        context = {
            "concept_a": "X",
            "concept_b": "Y",
            "property": "its properties",
            "mechanism": "some mechanism",
            "condition": "certain conditions",
            "context": "the given context",
            "phenomenon": "the observed phenomenon",
            "theory_a": "Theory A",
            "theory_b": "Theory B",
            "domain_a": "Domain A",
            "domain_b": "Domain B",
        }

        if kg_nodes and gap.involved_nodes:
            names = []
            for nid in gap.involved_nodes[:3]:
                node = kg_nodes.get(nid)
                if node:
                    names.append(node.name)
            if len(names) >= 1:
                context["concept_a"] = names[0]
            if len(names) >= 2:
                context["concept_b"] = names[1]
            if len(names) >= 3:
                context["context"] = names[2]

            if len(names) >= 2:
                context["phenomenon"] = f"{names[0]}-{names[1]} relationship"

            domain_set = set()
            for nid in gap.involved_nodes[:2]:
                node = kg_nodes.get(nid)
                if node and "domain" in node.properties:
                    domain_set.add(node.properties["domain"])
            domains = list(domain_set)
            if len(domains) >= 1:
                context["domain_a"] = domains[0]
            if len(domains) >= 2:
                context["domain_b"] = domains[1]

        return context

    def _score_novelty(self, question: str, gap: ResearchGap) -> float:
        """Score question novelty based on gap type and question structure."""
        base = gap.novelty * 0.6

        unique_words = len(set(question.lower().split()))
        complexity_bonus = min(unique_words / 20.0, 0.2)

        template_indicators = {
            "what if": 0.15,
            "fundamentally": 0.1,
            "emerge": 0.1,
            "unified": 0.1,
            "beyond": 0.05,
        }
        indicator_bonus = sum(
            bonus for word, bonus in template_indicators.items()
            if word in question.lower()
        )

        return min(base + complexity_bonus + indicator_bonus, 1.0)

    def _score_importance(self, question: str, gap: ResearchGap,
                           q_type: str) -> float:
        """Score question importance."""
        base = gap.importance * 0.7

        type_weights = {
            "why": 0.8,
            "how": 0.7,
            "mechanism": 0.9,
            "comparison": 0.6,
            "prediction": 0.7,
            "what_if": 0.5,
        }
        type_bonus = type_weights.get(q_type, 0.5) * 0.3

        return min(base + type_bonus, 1.0)

    def _score_answerability(self, question: str, gap: ResearchGap) -> float:
        """Score how answerable a question is."""
        base = gap.tractability * 0.6

        short = len(question) < 150
        has_measurable = any(
            term in question.lower()
            for term in ["predict", "measure", "compare", "test", "vary", "depend", "model"]
        )
        is_specific = "?" in question

        if short:
            base += 0.1
        if has_measurable:
            base += 0.15
        if is_specific:
            base += 0.05

        return min(base, 1.0)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_questions": len(self.questions),
            "generation_count": self.generation_count,
            "question_types": dict(
                Counter(q.question_type for q in self.questions)
            ),
            "top_questions": [
                {
                    "id": q.id,
                    "text": q.question_text[:120],
                    "score": q.overall_score,
                    "type": q.question_type,
                }
                for q in sorted(self.questions, key=lambda x: x.overall_score, reverse=True)[:5]
            ],
        }
