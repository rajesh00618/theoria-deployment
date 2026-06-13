"""
Phase 2: Scientific Literature Ingestion Layer.

Enables THEORIA to learn from existing human knowledge by parsing
scientific papers, extracting concepts, theories, evidence, and experiments.
"""

from __future__ import annotations

import re
import time
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import (
    ScientificPaper, Citation, Figure, KGNode, KGEdge,
    KGNodeType, KGEdgeType,
)


class LiteratureIngestor:
    """
    Scientific literature ingestion layer.
    Parses papers, extracts metadata, citations, and structured knowledge.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.papers: Dict[str, ScientificPaper] = {}
        self.ingestion_log: List[Dict[str, Any]] = []

        self.section_patterns = {
            "abstract": r"(?i)(?:^|\n)(?:abstract|summary)[:\s]*(.*?)(?=\n\s*(?:introduction|1\.|background|1\s))",
            "introduction": r"(?i)(?:^|\n)(?:introduction|1\.?\s*introduction)[:\s]*(.*?)(?=\n\s*(?:background|related work|2\.|methods|methodology))",
            "methods": r"(?i)(?:^|\n)(?:methods|methodology|materials and methods|experimental)[:\s]*(.*?)(?=\n\s*(?:results|3\.|discussion|conclusion))",
            "results": r"(?i)(?:^|\n)(?:results|results and discussion|findings)[:\s]*(.*?)(?=\n\s*(?:discussion|4\.|conclusion))",
            "discussion": r"(?i)(?:^|\n)(?:discussion|conclusion|5\.\s*discussion)[:\s]*(.*?)(?=\n\s*(?:references|acknowledgments|appendix|$))",
            "conclusion": r"(?i)(?:^|\n)(?:conclusion|summary|conclusions)[:\s]*(.*?)(?=\n\s*(?:references|acknowledgments|appendix|$))",
        }

        self.equation_pattern = re.compile(
            r'(?:\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|\$.*?\$|'
            r'(?:^|\s)[A-Za-z_]\w*\s*=\s*[^;\n]+'
            r'(?:\s*[+\-*/]\s*[^;\n]+)*)',
            re.DOTALL,
        )

        self.citation_patterns = [
            re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\]'),
            re.compile(r'\(([A-Za-z\-]+(?:\s+et\s+al\.?)?,\s*\d{4}[a-z]?)\)'),
            re.compile(r'([A-Za-z\-]+)\s+et\s+al\.?\s*[\[\(](\d{4})'),
        ]

    def parse_paper_text(self, text: str,
                         title: str = "",
                         authors: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> ScientificPaper:
        """Parse a paper from raw text content."""
        if authors is None:
            authors = []
        if metadata is None:
            metadata = {}

        paper = ScientificPaper(
            title=title,
            authors=authors,
            full_text=text,
        )

        if metadata:
            paper.year = metadata.get("year", 0)
            paper.journal = metadata.get("journal", "")
            paper.doi = metadata.get("doi", "")
            paper.arxiv_id = metadata.get("arxiv_id", "")
            paper.domain = metadata.get("domain", "")
            paper.keywords = metadata.get("keywords", [])
            paper.source_url = metadata.get("source_url", "")

        abstract = self._extract_section(text, "abstract")
        if abstract:
            paper.abstract = abstract[:self.config.max_section_length] if self.config else abstract[:10000]

        for section_name in ["introduction", "methods", "results", "discussion", "conclusion"]:
            section_text = self._extract_section(text, section_name)
            if section_text:
                max_len = self.config.max_section_length if self.config else 10000
                paper.sections[section_name] = section_text[:max_len]

        if self.config is None or self.config.extract_equations:
            paper.equations = self._extract_equations(text)

        if self.config is None or self.config.extract_citations:
            paper.citations = self._extract_citations(text)

        paper.ingestion_timestamp = time.time()
        self.papers[paper.id] = paper
        self.ingestion_log.append({
            "paper_id": paper.id,
            "title": title[:80],
            "sections_found": list(paper.sections.keys()),
            "citations_found": len(paper.citations),
            "equations_found": len(paper.equations),
            "timestamp": time.time(),
        })

        return paper

    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract a section from paper text using regex patterns."""
        pattern = self.section_patterns.get(section_name)
        if not pattern:
            return None

        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()

        lines = text.split("\n")
        in_section = False
        section_lines = []
        section_headers = {
            "abstract": ["abstract", "summary"],
            "introduction": ["introduction", "1. introduction", "1 introduction"],
            "methods": ["methods", "methodology", "materials and methods",
                        "2. methods", "3. methods", "experimental"],
            "results": ["results", "results and discussion", "3. results",
                        "4. results", "findings"],
            "discussion": ["discussion", "4. discussion", "5. discussion"],
            "conclusion": ["conclusion", "conclusions", "5. conclusion",
                           "6. conclusion", "summary"],
        }

        next_sections = {
            "abstract": ["introduction", "1.", "background"],
            "introduction": ["methods", "2.", "materials"],
            "methods": ["results", "3.", "findings"],
            "results": ["discussion", "4.", "conclusion"],
            "discussion": ["references", "acknowledgments", "appendix"],
            "conclusion": ["references", "acknowledgments", "appendix"],
        }

        for line in lines:
            stripped = line.strip().lower()
            if any(stripped.startswith(h) or stripped == h
                   for h in section_headers.get(section_name, [])):
                in_section = True
                continue

            if in_section:
                stop_headers = next_sections.get(section_name, [])
                if any(stripped.startswith(h) for h in stop_headers):
                    break
                section_lines.append(line)

        if section_lines:
            return "\n".join(section_lines).strip()
        return None

    def _extract_equations(self, text: str) -> List[str]:
        """Extract mathematical equations from text."""
        equations = []
        matches = self.equation_pattern.findall(text)
        for match in matches:
            eq = match.strip()
            if len(eq) > 3 and eq not in equations:
                equations.append(eq)
        return equations

    def _extract_citations(self, text: str) -> List[Citation]:
        """Extract citations from text."""
        citations = []
        seen = set()

        for pattern in self.citation_patterns:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, tuple):
                    key = str(match)
                else:
                    key = match

                if key not in seen:
                    seen.add(key)
                    citation = Citation(raw_text=key)
                    if "," in key and any(c.isalpha() for c in key):
                        parts = key.split(",")
                        if len(parts) >= 2:
                            citation.authors = [parts[0].strip()]
                            try:
                                citation.year = int(re.search(r'\d{4}', parts[1]).group())
                            except (AttributeError, ValueError):
                                pass
                    citations.append(citation)

        return citations

    def extract_concepts(self, paper: ScientificPaper) -> List[Dict[str, Any]]:
        """Extract scientific concepts from paper content."""
        concepts = []
        text = f"{paper.title}\n{paper.abstract}\n"

        for section_text in paper.sections.values():
            text += f"\n{section_text}"

        if paper.full_text and not paper.sections:
            text += f"\n{paper.full_text}"

        concept_patterns = [
            (r'(?i)(?:the\s+)?([A-Z][a-z]+(?:\s+[a-z]+){0,3})\s+(?:is|are|was|were)\s+(?:defined as|a|the\s+)?',
             "definition"),
            (r'(?i)\b([A-Z][a-z]+(?:\s+(?:of|in|for)\s+[a-z]+)?)\s+(?:theory|law|principle|effect|model|hypothesis|equation|function|parameter)\b',
             "named_entity"),
            (r'(?i)\b([a-z_][a-z0-9_]*)\s*=\s*[A-Za-z]',
             "variable"),
            (r'(?i)\b(principle of [a-z]+|conservation of [a-z]+|law of [a-z]+)\b',
             "scientific_principle"),
            (r'(?i)\b([A-Z][a-z]*\s+transformation|[A-Z][a-z]*\s+equivalent)\b',
             "scientific_concept"),
        ]

        seen = set()
        for pattern, kind in concept_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                name = match.strip().lower()
                if name not in seen and len(name) > 2:
                    seen.add(name)
                    concepts.append({
                        "name": name,
                        "kind": kind,
                        "source": "literature",
                        "paper_id": paper.id,
                    })

        paper.extracted_concepts = [c["name"] for c in concepts]
        return concepts

    def extract_theories(self, paper: ScientificPaper) -> List[Dict[str, Any]]:
        """Extract theories and theoretical claims from paper."""
        theories = []
        text = f"{paper.title}\n{paper.abstract}\n"

        for section_text in paper.sections.values():
            text += f"\n{section_text}"

        if paper.full_text and not paper.sections:
            text += f"\n{paper.full_text}"

        theory_patterns = [
            (r'(?i)(?:we\s+)?(?:propose|present|introduce|suggest|hypothesize|postulate)\s+(?:that\s+)?(.*?)(?:\.|;)',
             "proposed_theory"),
            (r'(?i)our\s+(?:model|theory|framework|approach|results|findings)\s+(?:predicts|suggests|implies|shows|show|indicate|demonstrate)\s+(?:that\s+)?(.*?)(?:\.|;)',
             "theoretical_claim"),
            (r'(?i)according\s+to\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[a-z]+){0,5})\s+(?:theory|model|hypothesis|principle)',
             "named_theory"),
            (r'(?i)we\s+(?:derive|find|show|demonstrate)\s+(?:that\s+)?(.*?)(?:\.|;)',
             "derived_result"),
        ]

        for pattern, kind in theory_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                theories.append({
                    "statement": match.strip(),
                    "kind": kind,
                    "paper_id": paper.id,
                })

        paper.extracted_theories = [t["statement"] for t in theories]
        return theories

    def extract_evidence(self, paper: ScientificPaper) -> List[Dict[str, Any]]:
        """Extract experimental evidence from paper."""
        evidence_list = []
        text = paper.sections.get("results", "") + "\n" + paper.sections.get("discussion", "")

        if not text.strip() and paper.full_text:
            text = paper.full_text

        evidence_patterns = [
            (r'(?i)we\s+(?:found|observed|detected|measured|demonstrated)\s+(?:that\s+)?(.*?)(?:\.|;)',
             "experimental_finding"),
            (r'(?i)our\s+(?:results|data|findings|analysis)\s+(?:show|suggest|indicate|demonstrate|reveal)\s+(?:that\s+)?(.*?)(?:\.|;)',
             "result_claim"),
            (r'(?i)(?:statistically\s+)?significant\s+(?:difference|correlation|effect|increase|decrease)\s+(.*?)(?:\.|;)',
             "significant_result"),
            (r'(?i)(?:p\s*[<≤]\s*0\.0[0-9]|p\s*=\s*0\.\d+)',
             "p_value"),
        ]

        for pattern, kind in evidence_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                evidence_list.append({
                    "description": match.strip() if isinstance(match, str) else str(match),
                    "kind": kind,
                    "paper_id": paper.id,
                })

        paper.extracted_evidence = [e["description"] for e in evidence_list]
        return evidence_list

    def paper_to_kg_nodes(self, paper: ScientificPaper) -> List[KGNode]:
        """Convert extracted paper content to knowledge graph nodes."""
        nodes = []

        base_props = {
            "title": paper.title,
            "year": paper.year if hasattr(paper, 'year') else 0,
            "journal": paper.journal if hasattr(paper, 'journal') else "",
            "doi": paper.doi if hasattr(paper, 'doi') else "",
            "authors": paper.authors,
            "domain": paper.domain,
            "description": paper.abstract[:500] if paper.abstract else paper.title,
        }
        paper_node = KGNode(
            node_type=KGNodeType.PAPER,
            name=paper.title[:100],
            properties=base_props,
            confidence=1.0,
        )
        nodes.append(paper_node)

        for concept_info in paper.extracted_concepts:
            node = KGNode(
                node_type=KGNodeType.CONCEPT,
                name=concept_info[:100],
                properties={
                    "description": f"Concept extracted from: {paper.title[:80]}",
                    "source_paper": paper.title[:200],
                },
                source_paper_ids=[paper.id],
                confidence=0.8,
            )
            nodes.append(node)

        for theory_info in paper.extracted_theories:
            node = KGNode(
                node_type=KGNodeType.THEORY,
                name=theory_info[:100],
                properties={
                    "description": f"Theory extracted from: {paper.title[:80]}",
                    "source_paper": paper.title[:200],
                },
                source_paper_ids=[paper.id],
                confidence=0.7,
            )
            nodes.append(node)

        for evidence_info in paper.extracted_evidence:
            node = KGNode(
                node_type=KGNodeType.EVIDENCE,
                name=evidence_info[:100],
                properties={
                    "description": f"Evidence extracted from: {paper.title[:80]}",
                    "source_paper": paper.title[:200],
                },
                source_paper_ids=[paper.id],
                confidence=0.6,
            )
            nodes.append(node)

        return nodes

    def get_ingestion_stats(self) -> Dict[str, Any]:
        return {
            "total_papers": len(self.papers),
            "recent_ingestions": self.ingestion_log[-10:] if self.ingestion_log else [],
            "domains_covered": list(set(
                p.domain for p in self.papers.values() if p.domain
            )),
        }


class PaperCorpus:
    """
    Manages a collection of papers for batch ingestion and querying.
    """

    def __init__(self, ingestor: LiteratureIngestor):
        self.ingestor = ingestor
        self.papers: Dict[str, ScientificPaper] = {}

    def add_paper(self, paper: ScientificPaper) -> None:
        self.papers[paper.id] = paper

    def search_by_keyword(self, keyword: str) -> List[ScientificPaper]:
        keyword = keyword.lower()
        results = []
        for paper in self.papers.values():
            search_text = f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}".lower()
            if keyword in search_text:
                results.append(paper)
        return results

    def search_by_domain(self, domain: str) -> List[ScientificPaper]:
        return [p for p in self.papers.values() if p.domain.lower() == domain.lower()]

    def get_papers_by_year(self, year: int) -> List[ScientificPaper]:
        return [p for p in self.papers.values() if p.year == year]

    def get_citation_network(self, paper_id: str) -> Dict[str, Any]:
        """Get citation network for a paper."""
        paper = self.papers.get(paper_id)
        if not paper:
            return {"paper": None, "citations": [], "cited_by": []}
        return {
            "paper": paper,
            "citations": [c.raw_text for c in paper.citations],
            "cited_by": [
                p for p in self.papers.values()
                if any(c.raw_text == paper.title for c in p.citations)
            ],
        }

    @property
    def size(self) -> int:
        return len(self.papers)
