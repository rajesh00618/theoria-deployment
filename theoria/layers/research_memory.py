"""
Research Memory System
======================

Remembers past discoveries, failed hypotheses, and successful strategies.

Input: Research Activity
Output: Updated Memory, Insights
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """A memory entry."""
    id: str
    category: str  # "discovery", "failure", "strategy", "insight"
    domain: str
    content: str
    importance: float  # 0-1
    timestamp: float = field(default_factory=time.time)
    references: List[str] = field(default_factory=list)


@dataclass
class MemoryQuery:
    """Query for memory retrieval."""
    keywords: List[str]
    domain: Optional[str] = None
    category: Optional[str] = None
    max_results: int = 10


@dataclass
class MemoryResult:
    """Result of memory query."""
    entries: List[MemoryEntry]
    total_matches: int
    query_time: float


class ResearchMemorySystem:
    """
    Stores and retrieves research memory.
    
    Remembers:
    - Past discoveries
    - Failed hypotheses
    - Successful strategies
    - Key insights
    """
    
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.memories: List[MemoryEntry] = []
        self.cycle_count = 0
    
    def store(self, category: str, domain: str, content: str,
              importance: float = 0.5, references: Optional[List[str]] = None) -> MemoryEntry:
        """
        Store a memory entry.
        
        Args:
            category: Type of memory
            domain: Scientific domain
            content: Memory content
            importance: Importance score (0-1)
            references: Related references
        
        Returns:
            Stored MemoryEntry
        """
        self.cycle_count += 1
        
        entry = MemoryEntry(
            id=f"mem_{self.cycle_count}",
            category=category,
            domain=domain,
            content=content,
            importance=importance,
            references=references or [],
        )
        
        self.memories.append(entry)
        return entry
    
    def query(self, query: MemoryQuery) -> MemoryResult:
        """
        Query memory for relevant entries.
        
        Args:
            query: MemoryQuery with search criteria
        
        Returns:
            MemoryResult with matching entries
        """
        t0 = time.time()
        
        matches = []
        for entry in self.memories:
            if self._matches_query(entry, query):
                matches.append(entry)
        
        # Sort by importance
        matches.sort(key=lambda e: e.importance, reverse=True)
        
        query_time = time.time() - t0
        
        return MemoryResult(
            entries=matches[:query.max_results],
            total_matches=len(matches),
            query_time=query_time,
        )
    
    def _matches_query(self, entry: MemoryEntry, query: MemoryQuery) -> bool:
        """Check if entry matches query."""
        # Check domain
        if query.domain and entry.domain != query.domain:
            return False
        
        # Check category
        if query.category and entry.category != query.category:
            return False
        
        # Check keywords
        if query.keywords:
            entry_text = entry.content.lower()
            if not any(kw.lower() in entry_text for kw in query.keywords):
                return False
        
        return True
    
    def get_discoveries(self, domain: Optional[str] = None) -> List[MemoryEntry]:
        """Get all discoveries."""
        query = MemoryQuery(keywords=[], domain=domain, category="discovery")
        result = self.query(query)
        return result.entries
    
    def get_failures(self, domain: Optional[str] = None) -> List[MemoryEntry]:
        """Get all failures."""
        query = MemoryQuery(keywords=[], domain=domain, category="failure")
        result = self.query(query)
        return result.entries
    
    def get_strategies(self, domain: Optional[str] = None) -> List[MemoryEntry]:
        """Get all strategies."""
        query = MemoryQuery(keywords=[], domain=domain, category="strategy")
        result = self.query(query)
        return result.entries
    
    def get_insights(self, domain: Optional[str] = None) -> List[MemoryEntry]:
        """Get all insights."""
        query = MemoryQuery(keywords=[], domain=domain, category="insight")
        result = self.query(query)
        return result.entries
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of memory state."""
        return {
            "cycle_count": self.cycle_count,
            "total_memories": len(self.memories),
            "by_category": {
                cat: sum(1 for m in self.memories if m.category == cat)
                for cat in ["discovery", "failure", "strategy", "insight"]
            },
            "by_domain": {
                dom: sum(1 for m in self.memories if m.domain == dom)
                for dom in set(m.domain for m in self.memories)
            },
        }
