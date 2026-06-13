from __future__ import annotations

import uuid
import random
import math
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from theoria.core.types import ResearchPortfolio, GrandChallenge


@dataclass
class CivilizationIntelligenceResult:
    portfolios_managed: int = 0
    grand_challenges_coordinated: int = 0
    synergy_score: float = 0.0
    optimization_cycles: int = 0
    cross_portfolio_transfers: int = 0
    civilization_impact: float = 0.0


class CivilizationIntelligenceLayer:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.portfolios: Dict[str, ResearchPortfolio] = {}
        self.grand_challenge_results: Dict[str, Any] = {}
        self.cycle_count = 0

    def register_portfolio(self, name: str) -> ResearchPortfolio:
        portfolio = ResearchPortfolio(name=name)
        self.portfolios[name] = portfolio
        return portfolio

    def optimize_across_portfolios(self) -> Dict[str, Any]:
        if not self.portfolios:
            return {"optimization": "none"}
        transfers = []
        names = list(self.portfolios.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                synergy = random.uniform(0.1, 0.9)
                if synergy > 0.6:
                    transfers.append({
                        "from": names[i], "to": names[j],
                        "synergy": synergy,
                        "resource_transferred": random.uniform(0.01, 0.1),
                    })
        return {"optimization": "cross_portfolio", "transfers": transfers}

    def coordinate_challenge(self, challenge_name: str,
                             portfolio_names: List[str]) -> Dict[str, Any]:
        if challenge_name not in self.grand_challenge_results:
            self.grand_challenge_results[challenge_name] = {
                "name": challenge_name,
                "coordinated_cycles": 0,
                "total_progress": 0.0,
                "portfolios_involved": [],
            }
        record = self.grand_challenge_results[challenge_name]
        record["coordinated_cycles"] += 1
        record["total_progress"] = min(1.0, record["total_progress"] + random.uniform(0.005, 0.02))
        record["portfolios_involved"] = list(set(record["portfolios_involved"] + portfolio_names))
        return record

    def assess_civilization_impact(self) -> Dict[str, float]:
        scores = {}
        for name, record in self.grand_challenge_results.items():
            progress = record.get("total_progress", 0)
            portfolios = len(record.get("portfolios_involved", []))
            cycles = record.get("coordinated_cycles", 1)
            scores[name] = progress * math.log(1 + portfolios) * math.sqrt(cycles)
        normalization = max(scores.values()) if scores else 1.0
        for k in scores:
            scores[k] /= normalization
        return scores

    def run_cycle(self) -> CivilizationIntelligenceResult:
        self.cycle_count += 1
        result = CivilizationIntelligenceResult()

        result.portfolios_managed = len(self.portfolios)
        result.grand_challenges_coordinated = len(self.grand_challenge_results)

        opt_result = self.optimize_across_portfolios()
        if "transfers" in opt_result:
            result.cross_portfolio_transfers = len(opt_result["transfers"])
        result.optimization_cycles += 1

        for challenge in list(self.grand_challenge_results.keys()):
            portfolio_names = list(self.portfolios.keys())
            self.coordinate_challenge(challenge, portfolio_names)

        scores = self.assess_civilization_impact()
        if scores:
            result.civilization_impact = sum(scores.values()) / len(scores)
            result.synergy_score = random.uniform(0.4, 0.9)
        return result
