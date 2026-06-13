"""
Phase 3: Multi-Agent Research Lab (P3.3) + Autonomous Debate (P3.4).

Specialized agents with roles: Planner, Theorist, Experimenter, Critic, Reviewer, Safety.
Autonomous debate simulates peer review before theory activation.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from collections import defaultdict
from enum import Enum, auto

from theoria.core.types import (
    Theory, Evidence, CandidateHypothesis, ExperimentDesign, ExperimentResult,
    AgentRole, AgentMessage, AgentProfile, DebateRound,
    CriticReport, TheoryStatus,
)


class ResearchAgent:
    """
    Base class for all specialized research agents.
    Each agent has a role, expertise, and decision rules.
    """

    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.message_history: List[AgentMessage] = []
        self.decisions: List[Dict[str, Any]] = []
        self.iteration: int = 0

    @property
    def role(self) -> AgentRole:
        return self.profile.role

    def send_message(self, content: str, receiver: AgentRole,
                     msg_type: str = "proposal",
                     references: Optional[List[str]] = None) -> AgentMessage:
        msg = AgentMessage(
            sender_role=self.role,
            receiver_role=receiver,
            content=content,
            message_type=msg_type,
            references=references or [],
            confidence=self.profile.assertiveness,
        )
        self.message_history.append(msg)
        return msg

    def can_continue(self) -> bool:
        return self.iteration < self.profile.max_iterations

    def increment_iteration(self) -> None:
        self.iteration += 1


class PlannerAgent(ResearchAgent):
    """Designs research plans and coordinates the scientific workflow."""

    def __init__(self, profile: Optional[AgentProfile] = None):
        super().__init__(profile or AgentProfile(
            role=AgentRole.PLANNER,
            name="Planner",
            expertise=["research_design", "prioritization", "resource_allocation"],
            assertiveness=0.7,
            creativity=0.4,
            rigor=0.6,
        ))
        self.plans: List[Dict[str, Any]] = []

    def create_research_plan(self, hypotheses: List[CandidateHypothesis],
                             available_compute: float) -> Dict[str, Any]:
        self.increment_iteration()
        plan = {
            "plan_id": str(uuid.uuid4())[:8],
            "objectives": [h.description[:80] for h in hypotheses[:3]],
            "priority_order": [h.id for h in sorted(hypotheses,
                              key=lambda h: h.falsifiability, reverse=True)],
            "compute_allocation": available_compute * 0.3,
            "estimated_cycles": len(hypotheses) * 5,
            "milestones": [f"Test {h.description[:40]}..." for h in hypotheses[:3]],
        }
        self.plans.append(plan)
        return plan

    def prioritize_experiments(self, designs: List[ExperimentDesign]) -> List[str]:
        scored = []
        for d in designs:
            score = 0.4 * d.feasibility + 0.3 * d.predicted_power - 0.3 * d.risk_score
            scored.append((score, d.id))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [sid for _, sid in scored]


class TheoryAgent(ResearchAgent):
    """Generates and refines theories based on evidence."""

    def __init__(self, profile: Optional[AgentProfile] = None):
        super().__init__(profile or AgentProfile(
            role=AgentRole.THEORIST,
            name="Theorist",
            expertise=["abduction", "formalization", "compression"],
            assertiveness=0.6,
            creativity=0.8,
            rigor=0.4,
        ))

    def propose_refinement(self, theory: Theory,
                           evidence: List[Evidence]) -> Dict[str, Any]:
        self.increment_iteration()
        support = sum(e.likelihood_under_theory.get(theory.id, 0) for e in evidence)
        if support < len(evidence) * 0.3:
            return {
                "theory_id": theory.id,
                "action": "modify",
                "suggestion": "Increase protective belt assumptions",
                "confidence": 0.4,
            }
        elif theory.posterior > 0.8:
            return {
                "theory_id": theory.id,
                "action": "extend",
                "suggestion": "Extend domain of validity",
                "confidence": 0.7,
            }
        return {
            "theory_id": theory.id,
            "action": "maintain",
            "suggestion": "Current formulation sufficient",
            "confidence": 0.5,
        }


class ExperimentAgent(ResearchAgent):
    """Designs and executes experiments to test hypotheses."""

    def __init__(self, profile: Optional[AgentProfile] = None):
        super().__init__(profile or AgentProfile(
            role=AgentRole.EXPERIMENTER,
            name="Experimenter",
            expertise=["experimental_design", "measurement", "statistics"],
            assertiveness=0.5,
            creativity=0.3,
            rigor=0.9,
        ))

    def design_critical_test(self, t1: Theory, t2: Theory) -> Dict[str, Any]:
        self.increment_iteration()
        shared_vars = set(t1.reference_class) & set(t2.reference_class)
        differing_claims = []
        for c1 in t1.core_claims:
            for c2 in t2.core_claims:
                if c1.statement != c2.statement:
                    differing_claims.append((c1.statement, c2.statement))
        return {
            "test_design": "crucial_experiment",
            "shared_variables": list(shared_vars),
            "discriminating_predictions": differing_claims[:3],
            "recommended_n": max(10, int(5 / max(abs(t1.posterior - t2.posterior), 0.1))),
        }


class CriticAgent(ResearchAgent):
    """Criticizes theories and experiments for weaknesses."""

    def __init__(self, profile: Optional[AgentProfile] = None):
        super().__init__(profile or AgentProfile(
            role=AgentRole.CRITIC,
            name="Critic",
            expertise=["logical_analysis", "methodology", "falsification"],
            assertiveness=0.8,
            creativity=0.3,
            rigor=0.9,
        ))

    def critique_theory(self, theory: Theory) -> Dict[str, Any]:
        self.increment_iteration()
        flaws = []
        if not theory.intervention:
            flaws.append("No intervention specified - unfalsifiable")
        if theory.posterior > 0.9 and len(theory.severity_records) < 3:
            flaws.append("Overconfident with insufficient severe testing")
        if not theory.domain.parameter_ranges:
            flaws.append("Domain of validity not characterized")
        return {
            "theory_id": theory.id,
            "flaws": flaws[:5],
            "verdict": "reject" if len(flaws) >= 2 else "needs_revision" if flaws else "accept",
            "severity": "high" if any("unfalsifiable" in f for f in flaws) else "medium",
        }

    def critique_experiment(self, design: ExperimentDesign) -> Dict[str, Any]:
        self.increment_iteration()
        issues = []
        if not design.independent_variables:
            issues.append("No independent variables specified")
        if not design.dependent_variables:
            issues.append("No dependent variables specified")
        if design.num_trials < 5:
            issues.append("Insufficient trial count for statistical power")
        if not design.controls:
            issues.append("No control variables specified")
        return {
            "design_id": design.id,
            "issues": issues,
            "soundness": "low" if len(issues) >= 2 else "medium" if issues else "high",
        }


class ReviewerAgent(ResearchAgent):
    """Peer-review style evaluation of complete research packages."""

    def __init__(self, profile: Optional[AgentProfile] = None):
        super().__init__(profile or AgentProfile(
            role=AgentRole.REVIEWER,
            name="Reviewer",
            expertise=["peer_review", "reproducibility", "statistics"],
            assertiveness=0.6,
            creativity=0.3,
            rigor=0.8,
        ))

    def review_package(self, theory: Theory, design: ExperimentDesign,
                       result: Optional[ExperimentResult] = None) -> Dict[str, Any]:
        self.increment_iteration()
        scores = {
            "significance": 0.5,
            "rigor": 0.5,
            "novelty": 0.5,
            "reproducibility": 0.5,
        }

        if theory.novel_predictions_confirmed > 0:
            scores["significance"] += 0.2
        if theory.intervention:
            scores["rigor"] += 0.2
        if len(theory.severity_records) >= 3:
            scores["reproducibility"] += 0.2
        if theory.novel_predictions_confirmed > 2:
            scores["novelty"] += 0.2

        if result:
            if result.supports_hypothesis and result.p_value < 0.01:
                scores["significance"] += 0.2
            if result.effect_size > 0.5:
                scores["rigor"] += 0.1

        avg_score = np.mean(list(scores.values()))
        return {
            "theory_id": theory.id,
            "scores": scores,
            "overall": float(avg_score),
            "verdict": "accept" if avg_score > 0.7 else "minor_revision" if avg_score > 0.5 else "major_revision" if avg_score > 0.3 else "reject",
            "comments": [],
        }


class SafetyAgent(ResearchAgent):
    """Evaluates safety and ethical implications of research."""

    def __init__(self, profile: Optional[AgentProfile] = None):
        super().__init__(profile or AgentProfile(
            role=AgentRole.SAFETY_OFFICER,
            name="Safety Officer",
            expertise=["safety", "ethics", "dual_use"],
            assertiveness=0.9,
            creativity=0.2,
            rigor=0.9,
        ))

    def screen_theory(self, theory: Theory) -> Dict[str, Any]:
        self.increment_iteration()
        concerns = []
        if theory.reference_class:
            high_risk_terms = ["weapon", "pathogen", "toxin", "surveillance",
                               "manipulation", "autonomous"]
            for term in high_risk_terms:
                for claim in theory.core_claims:
                    if term in claim.statement.lower():
                        concerns.append(f"Dual-use concern: {term} in core claims")

        return {
            "theory_id": theory.id,
            "concerns": concerns,
            "clearance": "denied" if concerns else "granted",
            "restrictions": ["requires_human_review"] if concerns else [],
        }

    def screen_experiment(self, design: ExperimentDesign) -> Dict[str, Any]:
        self.increment_iteration()
        concerns = []
        if design.risk_score > 0.7:
            concerns.append("High risk score - requires additional safeguards")
        if not design.blinding or design.blinding == "none":
            concerns.append("No blinding - risk of observer bias")
        return {
            "design_id": design.id,
            "concerns": concerns,
            "approval": "denied" if any("risk" in c for c in concerns) else "approved",
        }


class MultiAgentLab:
    """
    Multi-Agent Research Lab coordinating specialized agents.
    Manages debate workflows, agent communication, and consensus building.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.agents: Dict[AgentRole, ResearchAgent] = {}
        self.debate_history: List[DebateRound] = []
        self.consensus_results: List[Dict[str, Any]] = []

        self._register_default_agents()

    def _register_default_agents(self) -> None:
        self.register_agent(PlannerAgent())
        self.register_agent(TheoryAgent())
        self.register_agent(ExperimentAgent())
        self.register_agent(CriticAgent())
        self.register_agent(ReviewerAgent())
        self.register_agent(SafetyAgent())

    def register_agent(self, agent: ResearchAgent) -> None:
        self.agents[agent.role] = agent

    def get_agent(self, role: AgentRole) -> Optional[ResearchAgent]:
        return self.agents.get(role)

    def send_message(self, content: str, sender: AgentRole,
                     receiver: AgentRole, msg_type: str = "proposal",
                     references: Optional[List[str]] = None) -> AgentMessage:
        agent = self.agents.get(sender)
        if not agent:
            raise ValueError(f"No agent registered for role {sender}")
        msg = agent.send_message(content, receiver, msg_type, references)
        return msg

    def run_debate(self, topic: str,
                   participants: List[AgentRole],
                   max_rounds: int = 3) -> DebateRound:
        debate = DebateRound(round_number=len(self.debate_history) + 1)

        for rnd in range(max_rounds):
            for role in participants:
                agent = self.agents.get(role)
                if not agent or not agent.can_continue():
                    continue

                statement = agent.send_message(
                    content=f"[Round {rnd+1}] {role.name} analysis of: {topic}",
                    receiver=participants[(participants.index(role) + 1) % len(participants)],
                    msg_type="analysis",
                )
                debate.statements.append(statement)
                agent.increment_iteration()

        debate.consensus_reached, debate.consensus_statement = self._check_consensus(debate)
        self.debate_history.append(debate)
        return debate

    def _check_consensus(self, debate: DebateRound) -> Tuple[bool, str]:
        if len(debate.statements) < 2:
            return False, "Insufficient statements for consensus"

        critics = [s for s in debate.statements if s.sender_role in (AgentRole.CRITIC, AgentRole.REVIEWER)]
        proponents = [s for s in debate.statements if s.sender_role in (AgentRole.THEORIST, AgentRole.EXPERIMENTER)]

        if critics and proponents:
            threshold = self.config.consensus_threshold if self.config else 0.7
            avg_confidence_critics = np.mean([s.confidence for s in critics])
            avg_confidence_proponents = np.mean([s.confidence for s in proponents])
            ratio = avg_confidence_proponents / max(avg_confidence_critics, 0.01)
            if ratio > threshold:
                return True, "Agreement: proposal meets scientific standards"
            elif ratio < 1.0 / threshold:
                return True, "Agreement: proposal requires substantial revision"
        return False, "No consensus reached"

    def review_theory_pipeline(self, theory: Theory,
                               design: Optional[ExperimentDesign] = None,
                               result: Optional[ExperimentResult] = None) -> Dict[str, Any]:
        reviews = {}

        critic = self.agents.get(AgentRole.CRITIC)
        if critic and isinstance(critic, CriticAgent):
            reviews["critic"] = critic.critique_theory(theory)
            critic.increment_iteration()

        safety = self.agents.get(AgentRole.SAFETY_OFFICER)
        if safety and isinstance(safety, SafetyAgent):
            reviews["safety"] = safety.screen_theory(theory)
            safety.increment_iteration()

        reviewer = self.agents.get(AgentRole.REVIEWER)
        if reviewer and isinstance(reviewer, ReviewerAgent):
            reviews["reviewer"] = reviewer.review_package(theory, design or ExperimentDesign(), result)
            reviewer.increment_iteration()

        passes_review = all(
            r.get("verdict") != "reject" and r.get("clearance") != "denied"
            for r in reviews.values()
        )

        result = {
            "theory_id": theory.id,
            "reviews": reviews,
            "passes_review": passes_review,
            "timestamp": time.time(),
        }
        self.consensus_results.append(result)
        return result

    def get_summary(self) -> Dict[str, Any]:
        return {
            "agents": {
                role.name: {
                    "name": agent.profile.name,
                    "iterations": agent.iteration,
                    "messages": len(agent.message_history),
                }
                for role, agent in self.agents.items()
            },
            "debates": len(self.debate_history),
            "reviews_completed": len(self.consensus_results),
            "consensus_rate": (
                sum(1 for r in self.consensus_results if r["passes_review"]) /
                max(len(self.consensus_results), 1)
            ),
        }
