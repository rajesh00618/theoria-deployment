"""L22: Knowledge Civilization Layer — planet-scale knowledge integration and ecosystem management."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from theoria.core.config import TheoriaConfig
from theoria.layers.global_knowledge import GlobalKnowledgeCivilization
from theoria.layers.research_institutions import AutonomousResearchInstitutions
from theoria.layers.grand_discovery_programs import GrandDiscoveryPrograms
from theoria.layers.meta_civilization_intelligence import MetaCivilizationIntelligence


@dataclass
class KnowledgeCivilizationResult:
    knowledge_objects: int = 0
    institutions_active: int = 0
    programs_active: int = 0
    models_active: int = 0
    syntheses_created: int = 0
    overall_progress: float = 0.0


class KnowledgeCivilizationLayer:
    def __init__(self, config: Optional[TheoriaConfig] = None):
        cfg = config or TheoriaConfig.phase_9_sri()
        self.knowledge = GlobalKnowledgeCivilization(cfg.global_knowledge_civilization)
        self.institutions = AutonomousResearchInstitutions(cfg.autonomous_institutions)
        self.programs = GrandDiscoveryPrograms(cfg.grand_discovery_programs)
        self.meta = MetaCivilizationIntelligence(cfg.meta_civilization_intelligence)

    def run_cycle(self) -> KnowledgeCivilizationResult:
        k_result = self.knowledge.run_cycle()
        i_result = self.institutions.run_cycle()
        p_result = self.programs.run_cycle()
        m_result = self.meta.run_cycle()

        return KnowledgeCivilizationResult(
            knowledge_objects=k_result.total_objects,
            institutions_active=i_result.institutions_active,
            programs_active=p_result.programs_active,
            models_active=m_result.total_models,
            syntheses_created=k_result.syntheses_created,
            overall_progress=p_result.overall_progress,
        )

    def get_summary(self) -> Dict[str, Any]:
        return {
            "knowledge": self.knowledge.get_summary(),
            "institutions": self.institutions.get_summary(),
            "programs": self.programs.get_summary(),
            "meta": self.meta.get_summary(),
        }
