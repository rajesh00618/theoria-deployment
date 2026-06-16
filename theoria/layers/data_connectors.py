"""
Phase 3: Real Data Connectors (P3.8).

Connects to real scientific data sources:
ArXiv, Semantic Scholar, CrossRef, Wikipedia, GitHub.

All connectors make real HTTP requests. If a source is unavailable,
an explicit error is returned rather than fabricated data.
"""

from __future__ import annotations

import time
import json
import uuid
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

try:
    import urllib.request
    import urllib.parse
    import urllib.error
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False


@dataclass
class DataSource:
    name: str
    source_type: str
    url: str
    records_count: int = 0
    last_access: float = 0.0
    is_connected: bool = False


@dataclass
class Dataset:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    source: str = ""
    domain: str = ""
    description: str = ""
    features: List[str] = field(default_factory=list)
    n_samples: int = 0
    data: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    imported_at: float = field(default_factory=time.time)


class DataConnector:
    """
    Connects to external scientific data sources and imports real datasets.
    Provides a unified interface to diverse data repositories.
    
    All search/import operations make real HTTP requests.
    Returns explicit errors when sources are unavailable.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.sources: Dict[str, DataSource] = {}
        self.datasets: Dict[str, Dataset] = {}
        self.import_history: List[Dict[str, Any]] = []

        self._register_default_sources()

    def _register_default_sources(self) -> None:
        sources = [
            DataSource("ArXiv", "academic", "https://export.arxiv.org/api/query"),
            DataSource("SemanticScholar", "academic", "https://api.semanticscholar.org/graph/v1"),
            DataSource("CrossRef", "academic", "https://api.crossref.org/works"),
            DataSource("Wikipedia", "encyclopedia", "https://en.wikipedia.org/w/api.php"),
            DataSource("GitHub", "code", "https://api.github.com/search/repositories"),
        ]
        for s in sources:
            self.sources[s.name.lower()] = s

    def connect_source(self, source_name: str) -> bool:
        key = source_name.lower()
        if key not in self.sources:
            return False
        self.sources[key].is_connected = True
        self.sources[key].last_access = time.time()
        return True

    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search arXiv via its real API."""
        if not _HAS_URLLIB:
            return [{"error": "urllib not available"}]
        try:
            params = urllib.parse.urlencode({
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            })
            url = f"https://export.arxiv.org/api/query?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "THEORIA/0.6.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")
            return self._parse_arxiv_xml(content, max_results)
        except Exception as e:
            return [{"error": f"arXiv API error: {str(e)}"}]

    def _parse_arxiv_xml(self, xml_content: str, max_results: int) -> List[Dict[str, Any]]:
        """Parse arXiv Atom XML into structured results."""
        import re
        entries = re.findall(r'<entry>(.*?)</entry>', xml_content, re.DOTALL)
        results = []
        for entry in entries[:max_results]:
            title = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
            summary = re.search(r'<summary>(.*?)</summary>', entry, re.DOTALL)
            authors = re.findall(r'<name>(.*?)</name>', entry)
            published = re.search(r'<published>(.*?)</published>', entry)
            link = re.search(r'<id>(.*?)</id>', entry)
            results.append({
                "title": title.group(1).strip() if title else "",
                "abstract": summary.group(1).strip() if summary else "",
                "authors": authors,
                "published": published.group(1) if published else "",
                "url": link.group(1) if link else "",
                "source": "arxiv",
            })
        return results

    def search_semantic_scholar(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search Semantic Scholar via its real API."""
        if not _HAS_URLLIB:
            return [{"error": "urllib not available"}]
        try:
            params = urllib.parse.urlencode({
                "query": query,
                "limit": max_results,
                "fields": "title,abstract,authors,year,citationCount,url",
            })
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "THEORIA/0.6.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            papers = data.get("data", [])
            results = []
            for p in papers:
                results.append({
                    "title": p.get("title", ""),
                    "abstract": p.get("abstract", ""),
                    "authors": [a.get("name", "") for a in p.get("authors", [])],
                    "year": p.get("year"),
                    "citation_count": p.get("citationCount", 0),
                    "url": p.get("url", ""),
                    "source": "semantic_scholar",
                })
            return results
        except Exception as e:
            return [{"error": f"Semantic Scholar API error: {str(e)}"}]

    def search_crossref(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search CrossRef via its real API."""
        if not _HAS_URLLIB:
            return [{"error": "urllib not available"}]
        try:
            params = urllib.parse.urlencode({
                "query": query,
                "rows": max_results,
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
                results.append({
                    "title": item.get("title", [""])[0] if item.get("title") else "",
                    "abstract": item.get("abstract", ""),
                    "authors": [
                        f"{a.get('given', '')} {a.get('family', '')}"
                        for a in item.get("author", [])
                    ],
                    "year": item.get("published-print", {}).get("date-parts", [[None]])[0][0],
                    "doi": item.get("DOI", ""),
                    "citation_count": item.get("is-referenced-by-count", 0),
                    "source": "crossref",
                })
            return results
        except Exception as e:
            return [{"error": f"CrossRef API error: {str(e)}"}]

    def search_wikipedia(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia via its real API."""
        if not _HAS_URLLIB:
            return [{"error": "urllib not available"}]
        try:
            params = urllib.parse.urlencode({
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
            })
            url = f"https://en.wikipedia.org/w/api.php?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "THEORIA/0.6.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            searches = data.get("query", {}).get("search", [])
            results = []
            for s in searches:
                results.append({
                    "title": s.get("title", ""),
                    "abstract": s.get("snippet", ""),
                    "url": f"https://en.wikipedia.org/wiki/{s.get('title', '').replace(' ', '_')}",
                    "word_count": s.get("wordcount", 0),
                    "source": "wikipedia",
                })
            return results
        except Exception as e:
            return [{"error": f"Wikipedia API error: {str(e)}"}]

    def search_github(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search GitHub repositories via its real API."""
        if not _HAS_URLLIB:
            return [{"error": "urllib not available"}]
        try:
            params = urllib.parse.urlencode({
                "q": query,
                "per_page": min(max_results, 30),
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
            for item in items[:max_results]:
                results.append({
                    "title": item.get("full_name", ""),
                    "description": item.get("description", ""),
                    "language": item.get("language", ""),
                    "stars": item.get("stargazers_count", 0),
                    "forks": item.get("forks_count", 0),
                    "url": item.get("html_url", ""),
                    "source": "github",
                })
            return results
        except Exception as e:
            return [{"error": f"GitHub API error: {str(e)}"}]

    def import_dataset(self, source_name: str, query: str,
                       domain: str = "general") -> Dataset:
        """Import data by searching a real source. Returns Dataset or error."""
        key = source_name.lower()
        if key not in self.sources:
            return Dataset(
                name=f"error_{source_name}",
                source=source_name,
                domain=domain,
                description=f"Error: source '{source_name}' not registered",
            )

        source = self.sources[key]
        source.is_connected = True
        source.last_access = time.time()

        results = []
        if key == "arxiv":
            results = self.search_arxiv(query)
        elif key == "semanticscholar":
            results = self.search_semantic_scholar(query)
        elif key == "crossref":
            results = self.search_crossref(query)
        elif key == "wikipedia":
            results = self.search_wikipedia(query)
        elif key == "github":
            results = self.search_github(query)
        else:
            return Dataset(
                name=f"error_{source_name}",
                source=source_name,
                domain=domain,
                description=f"No real connector for '{source_name}'",
            )

        has_error = any("error" in r for r in results)
        if has_error:
            error_msg = next(r.get("error", "Unknown error") for r in results if "error" in r)
            return Dataset(
                name=f"error_{source_name}",
                source=source_name,
                domain=domain,
                description=f"API error: {error_msg}",
                metadata={"error": error_msg},
            )

        dataset = Dataset(
            name=query,
            source=source_name,
            domain=domain,
            description=f"Search results for '{query}' from {source_name}",
            n_samples=len(results),
            data=results,
            metadata={
                "source_url": source.url,
                "import_method": "real_api",
                "result_count": len(results),
            },
        )

        source.records_count += 1
        self.datasets[dataset.id] = dataset
        self.import_history.append({
            "dataset_id": dataset.id,
            "source": source_name,
            "query": query,
            "domain": domain,
            "samples": dataset.n_samples,
            "timestamp": time.time(),
            "method": "real_api",
        })

        return dataset

    def list_datasets(self, domain: Optional[str] = None) -> List[Dataset]:
        if domain:
            return [d for d in self.datasets.values() if d.domain == domain]
        return list(self.datasets.values())

    def search_datasets(self, query: str) -> List[Dataset]:
        query_lower = query.lower()
        results = []
        for d in self.datasets.values():
            if (query_lower in d.name.lower() or
                query_lower in d.description.lower() or
                query_lower in d.domain.lower()):
                results.append(d)
        return results

    def get_source_stats(self, source_name: str) -> Optional[Dict[str, Any]]:
        key = source_name.lower()
        source = self.sources.get(key)
        if not source:
            return None
        ds_from_source = [d for d in self.datasets.values() if d.source.lower() == key]
        return {
            "name": source.name,
            "connected": source.is_connected,
            "datasets_imported": len(ds_from_source),
            "total_records": sum(d.n_samples for d in ds_from_source),
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "sources_registered": len(self.sources),
            "sources_connected": sum(1 for s in self.sources.values() if s.is_connected),
            "datasets_imported": len(self.datasets),
            "total_samples": sum(d.n_samples for d in self.datasets.values()),
            "domains": list(set(d.domain for d in self.datasets.values())),
            "imports_logged": len(self.import_history),
        }
