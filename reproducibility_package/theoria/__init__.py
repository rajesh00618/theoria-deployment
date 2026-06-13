"""
THEORIA: A Cognitive Architecture for Autonomous Scientific Theory Creation
An Audited, Bounded, Governed, and Self-Improving Framework for Theory-Creating AGI

Author: rajesh gurugubelli (June 2026)
Prototype Implementation
"""

__version__ = "0.1.0"
__author__ = "rajesh gurugubelli"

from theoria.core.types import (
    Theory,
    Evidence,
    Concept,
    Strategy,
    Intervention,
    TheoryStatus,
    DisciplineMode,
)

from theoria.core.memory import (
    EpisodicMemory,
    SemanticMemory,
    TheoryMemory,
    Graveyard,
    MetaStrategyMemory,
    MemoryArchitecture,
)

from theoria.core.config import TheoriaConfig

__all__ = [
    "Theory",
    "Evidence",
    "Concept",
    "Strategy",
    "Intervention",
    "TheoryStatus",
    "DisciplineMode",
    "EpisodicMemory",
    "SemanticMemory",
    "TheoryMemory",
    "Graveyard",
    "MetaStrategyMemory",
    "MemoryArchitecture",
    "TheoriaConfig",
]
