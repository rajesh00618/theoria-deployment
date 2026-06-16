"""
Phase 4: Real Data Infrastructure (P4.1).

Real API connectors for arXiv, Semantic Scholar, CrossRef,
Wikipedia, and GitHub. All connectors make real HTTP requests.
Returns explicit errors when sources are unavailable.
"""

from __future__ import annotations

import time
import uuid
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

try:
    import urllib.request
    import urllib.parse
    import urllib.error
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False

from theoria.core.types import APISourceConfig, APISearchResult


class RealDataConnector:
    """
    Multi-source real data connector with live API support.
    Sources: arXiv, Semantic Scholar, CrossRef, Wikipedia, GitHub.
    All queries hit real APIs. No fabricated data.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.sources: Dict[str, APISourceConfig] = {}
        self.indexed_papers: Dict[str, APISearchResult] = {}
        self.search_history: List[Dict[str, Any]] = []
        self._init_sources()

    def _init_sources(self):
        sources_data = [
            ("arxiv", "https://export.arxiv.org/api/query", "physics, math, cs, biology", 60),
            ("semantic_scholar", "https://api.semanticscholar.org/graph/v1", "general", 100),
            ("crossref", "https://api.crossref.org/works", "general academic", 50),
            ("wikipedia", "https://en.wikipedia.org/w/api.php", "general knowledge", 200),
            ("github", "https://api.github.com/search/repositories", "software, code", 30),
        ]
        for name, url, domains, rate in sources_data:
            self.sources[name] = APISourceConfig(
                name=name, base_url=url, enabled=True,
                rate_limit_per_min=rate,
            )

    def search(self, query: str, max_results: int = 100,
               sources: Optional[List[str]] = None) -> List[APISearchResult]:
        results = []
        src_list = sources or list(self.sources.keys())
        per_source = max(1, max_results // max(len(src_list), 1))

        for sname in src_list:
            src = self.sources.get(sname)
            if not src or not src.enabled:
                continue
            found = self._query_source(sname, query, per_source)
            results.extend(found)
            for r in found:
                key = r.doi or r.url
                if key:
                    self.indexed_papers[key] = r

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        self.search_history.append({
            "query": query,
            "results": len(results),
            "timestamp": time.time(),
        })
        return results[:max_results]

    def _query_source(self, source: str, query: str, limit: int) -> List[APISearchResult]:
        """Query a real API source. Returns explicit errors if unavailable."""
        if not _HAS_URLLIB:
            return [APISearchResult(
                source=source,
                title=f"ERROR: urllib not available for {source}",
                url="",
                relevance_score=0.0,
            )]

        try:
            if source == "arxiv":
                return self._query_arxiv(query, limit)
            elif source == "semantic_scholar":
                return self._query_semantic_scholar(query, limit)
            elif source == "crossref":
                return self._query_crossref(query, limit)
            elif source == "wikipedia":
                return self._query_wikipedia(query, limit)
            elif source == "github":
                return self._query_github(query, limit)
            else:
                return [APISearchResult(
                    source=source,
                    title=f"ERROR: No connector for '{source}'",
                    url="",
                    relevance_score=0.0,
                )]
        except Exception as e:
            return [APISearchResult(
                source=source,
                title=f"ERROR: {source} API failed: {str(e)}",
                url="",
                relevance_score=0.0,
            )]

    def _query_arxiv(self, query: str, limit: int) -> List[APISearchResult]:
        import re
        params = urllib.parse.urlencode({
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": limit,
            "sortBy": "relevance",
        })
        url = f"https://export.arxiv.org/api/query?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "THEORIA/0.6.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")

        entries = re.findall(r'<entry>(.*?)</entry>', content, re.DOTALL)
        results = []
        for entry in entries[:limit]:
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            authors = re.findall(r'<name>(.*?)</name>', entry)
            published = re.search(r'<published>(.*?)</published>', entry)
            link = re.search(r'<id>(.*?)</id>', entry)
            results.append(APISearchResult(
                source="arxiv",
                title=title.group(1).strip() if title else "",
                authors=authors,
                abstract=summary.group(1).strip()[:500] if summary else "",
                url=link.group(1) if link else "",
                year=int(published.group(1)[:4]) if published else 0,
                relevance_score=0.8,
            ))
        return results

    def _query_semantic_scholar(self, query: str, limit: int) -> List[APISearchResult]:
        params = urllib.parse.urlencode({
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,year,citationCount,url,externalIds",
        })
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "THEORIA/0.6.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        papers = data.get("data", [])
        results = []
        for p in papers:
            doi = p.get("externalIds", {}).get("DOI", "")
            results.append(APISearchResult(
                source="semantic_scholar",
                title=p.get("title", ""),
                authors=[a.get("name", "") for a in p.get("authors", [])],
                abstract=(p.get("abstract") or "")[:500],
                url=p.get("url", ""),
                year=p.get("year") or 0,
                citation_count=p.get("citationCount", 0),
                doi=doi,
                relevance_score=0.85,
            ))
        return results

    def _query_crossref(self, query: str, limit: int) -> List[APISearchResult]:
        params = urllib.parse.urlencode({
            "query": query,
            "rows": limit,
            "sort": "relevance",
        })
        url = f"https://api.crossref.org/works?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "THEORIA/0.6.0 (mailto:theoria@example.com)",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("message", {}).get("items", [])
        results = []
        for item in items:
            year = None
            if "published-print" in item:
                year = item["published-print"].get("date-parts", [[None]])[0][0]
            elif "published-online" in item:
                year = item["published-online"].get("date-parts", [[None]])[0][0]
            results.append(APISearchResult(
                source="crossref",
                title=item.get("title", [""])[0] if item.get("title") else "",
                authors=[
                    f"{a.get('given', '')} {a.get('family', '')}"
                    for a in item.get("author", [])
                ],
                abstract=(item.get("abstract") or "")[:500],
                url=f"https://doi.org/{item.get('DOI', '')}",
                year=year or 0,
                citation_count=item.get("is-referenced-by-count", 0),
                doi=item.get("DOI", ""),
                relevance_score=0.75,
            ))
        return results

    def _query_wikipedia(self, query: str, limit: int) -> List[APISearchResult]:
        params = urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
        })
        url = f"https://en.wikipedia.org/w/api.php?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "THEORIA/0.6.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        searches = data.get("query", {}).get("search", [])
        results = []
        for s in searches:
            results.append(APISearchResult(
                source="wikipedia",
                title=s.get("title", ""),
                abstract=s.get("snippet", ""),
                url=f"https://en.wikipedia.org/wiki/{s.get('title', '').replace(' ', '_')}",
                relevance_score=0.7,
            ))
        return results

    def _query_github(self, query: str, limit: int) -> List[APISearchResult]:
        params = urllib.parse.urlencode({
            "q": query,
            "per_page": min(limit, 30),
            "sort": "stars",
            "order": "desc",
        })
        url = f"https://api.github.com/search/repositories?{params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "THEORIA/0.6.0",
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        items = data.get("items", [])
        results = []
        for item in items[:limit]:
            results.append(APISearchResult(
                source="github",
                title=item.get("full_name", ""),
                abstract=item.get("description", "") or "",
                url=item.get("html_url", ""),
                year=0,
                relevance_score=min(1.0, item.get("stargazers_count", 0) / 10000),
            ))
        return results

    def monitor_literature(self, domains: List[str],
                           max_per_domain: int = 100) -> Dict[str, List[APISearchResult]]:
        domain_queries = {
            "physics": "quantum gravity dark matter cosmology",
            "biology": "genomics proteomics cell signaling evolution",
            "cs": "machine learning neural networks AI safety",
            "mathematics": "topology number theory algebra",
        }
        result: Dict[str, List[APISearchResult]] = {}
        for domain in domains:
            q = domain_queries.get(domain, domain)
            papers = self.search(q, max_results=max_per_domain,
                                sources=["arxiv", "semantic_scholar"])
            result[domain] = papers
        return result

    def detect_trends(self, domain: str, window_days: int = 30) -> List[Dict[str, Any]]:
        papers = [p for p in self.indexed_papers.values()
                  if domain.lower() in (p.title + " " + p.abstract).lower()]
        if not papers:
            return []
        avg_citations = sum(p.citation_count for p in papers) / max(len(papers), 1)
        recent = [p for p in papers if p.year >= 2025]
        return [{
            "domain": domain,
            "total_papers": len(papers),
            "recent_papers": len(recent),
            "avg_citations": round(avg_citations, 1),
            "window_days": window_days,
        }]

    def index_papers_count(self) -> int:
        return len(self.indexed_papers)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "sources": len(self.sources),
            "sources_connected": sum(1 for s in self.sources.values() if s.enabled),
            "papers_indexed": self.index_papers_count(),
            "total_searches": len(self.search_history),
            "real_api_only": True,
        }
