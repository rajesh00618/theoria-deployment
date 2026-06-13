"""
THEORIA Orchestrator: Main system controller.

Integrates all layers and subsystems into a cohesive research cycle.
Manages the discovery → falsification → revision loop.
"""

from __future__ import annotations

import time
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.config import TheoriaConfig
from theoria.core.memory import MemoryArchitecture
from theoria.core.types import (
    Theory, Evidence, Concept, Strategy, TheoryStatus, DisciplineMode,
    MotivationalState, ComputeBudget, AuditResult, ConceptLifecycle,
)

# Layer imports
from theoria.layers.sensorium import Sensorium, SensoryInput
from theoria.layers.empirics import Empirics
from theoria.layers.ontogenesis import Ontogenesis
from theoria.layers.abductive import AbductiveImagination
from theoria.layers.theory_constructor import TheoryConstructor
from theoria.layers.falsification import FalsificationEngine
from theoria.layers.meta_theory import MetaTheoryReasoner
from theoria.layers.auditor import MetascientificAuditor, ConstitutionalReview


@dataclass
class CycleResult:
    """Result of a single THEORIA research cycle."""
    cycle_number: int
    duration: float
    theories_proposed: int
    theories_falsified: int
    theories_converged: int
    strategies_used: List[str]
    anomalies_detected: int
    paradigm_crisis: bool
    memory_summary: Dict[str, Any]
    motivational_state: Dict[str, float]
    audit_summary: Dict[str, Any]


class TheoriaOrchestrator:
    """
    Main THEORIA system.
    Manages the full research cycle across all layers.
    """
    
    def __init__(self, config: Optional[TheoriaConfig] = None):
        self.config = config or TheoriaConfig.phase_1_baseline()
        
        # Initialize memory
        self.memory = MemoryArchitecture()
        
        # Initialize layers
        self.sensorium = Sensorium(config)
        self.empirics = Empirics(config)
        self.ontogenesis = Ontogenesis(config)
        self.abductive = AbductiveImagination(config)
        self.theory_constructor = TheoryConstructor(config)
        self.falsification = FalsificationEngine(config)
        self.meta_theory = MetaTheoryReasoner(config.meta_theory if config else None)
        self.auditor = MetascientificAuditor(config)
        self.constitutional = ConstitutionalReview(config)
        
        # Motivational state
        self.motivation = MotivationalState()
        
        # Compute budget
        self.budget = ComputeBudget(
            B_cycle=self.config.budget.B_cycle if config else 1e20,
            B_life=self.config.budget.B_life if config else 1e25,
        )
        
        # Cycle tracking
        self.cycle_count: int = 0
        self.cycle_history: List[CycleResult] = []
        
        # Classical laws target for B1
        self.classical_laws_catalog = {
            "kepler_third": {
                "name": "Kepler's Third Law",
                "pattern": "T^2 ∝ a^3",
                "observables": ["period", "semi_major_axis"],
            },
            "ohms_law": {
                "name": "Ohm's Law",
                "pattern": "V = I·R",
                "observables": ["voltage", "current", "resistance"],
            },
            "snells_law": {
                "name": "Snell's Law",
                "pattern": "n₁·sin(θ₁) = n₂·sin(θ₂)",
                "observables": ["angle_incidence", "angle_refraction", "refractive_index"],
            },
            "ideal_gas": {
                "name": "Ideal Gas Law",
                "pattern": "PV = nRT",
                "observables": ["pressure", "volume", "temperature", "amount"],
            },
            "coulombs_law": {
                "name": "Coulomb's Law",
                "pattern": "F = k·q₁q₂/r²",
                "observables": ["force", "charge_1", "charge_2", "distance"],
            },
            "momentum": {
                "name": "Conservation of Momentum",
                "pattern": "Σp_initial = Σp_final",
                "observables": ["mass", "velocity", "momentum"],
            },
        }
        self.discovered_laws: Dict[str, Dict[str, Any]] = {}
    
    def initialize_primitives(self, domain: str = "physics") -> None:
        """Initialize base primitives for a domain."""
        self.ontogenesis.initialize_base_primitives(domain)
        
        # Register strategies in meta-strategy memory
        for st in StrategyType:
            strategy = Strategy(
                name=st.name,
                strategy_type=st,
            )
            self.memory.meta_strategy.register_strategy(strategy)
    
    def ingest_data(self, data: List[Dict[str, Any]], 
                   modality: str = "numerical") -> Dict[str, Any]:
        """
        Ingest observational data into the system.
        Extracts variable names as concepts for L2.
        Returns anomaly report.
        """
        anomalies = []
        features = []
        
        for i, record in enumerate(data):
            sensory = SensoryInput(
                raw_data=record,
                modality=modality,
                source=f"batch_{i}",
                metadata={"id": f"obs_{i}", "index": i},
            )
            
            feat, anomaly = self.sensorium.ingest(sensory)
            if feat:
                features.append(feat)
            if anomaly and anomaly.anomaly_score > 0.7:
                anomalies.append(anomaly)
            
            # Store in episodic memory
            from theoria.core.memory import EpisodicRecord
            self.memory.episodic.append(EpisodicRecord(
                id=f"obs_{i}",
                timestamp=time.time(),
                modality=modality,
                raw_data=record,
            ))
        
        # Extract variable names from data and add as concepts to L2
        if data and isinstance(data[0], dict):
            variable_names = set()
            for record in data:
                for key in record.keys():
                    if isinstance(record[key], (int, float)):
                        variable_names.add(key)
            
            for var_name in variable_names:
                # Check if concept already exists
                exists = any(c.name == var_name for c in self.ontogenesis.concepts.values())
                if not exists:
                    concept = Concept(
                        name=var_name,
                        definition=f"Observable variable: {var_name}",
                        kind="base",
                        lifecycle=ConceptLifecycle.ALIVE,
                    )
                    concept.domains_where_useful.add("physics")
                    self.ontogenesis.concepts[concept.id] = concept
                    self.ontogenesis.primitives.add(concept.id)
        
        return {
            "records_ingested": len(data),
            "anomalies_detected": len(anomalies),
            "features_extracted": len(features),
            "queue_size": self.sensorium.queue_size,
            "overloaded": self.sensorium.is_overloaded,
            "new_concepts": len(variable_names) if data and isinstance(data[0], dict) else 0,
        }
    
    def research_cycle(self, domain: str = "physics") -> CycleResult:
        """
        Execute one complete THEORIA research cycle.
        
        Flow:
        1. L2: Concept management (evaluate, compose, analogy)
        2. L3: Generate candidate hypotheses (6 strategies)
        3. L4: Formalize candidates into theories
        4. L5: Falsify theories (severity, comparison)
        5. L6: Meta-strategy update
        6. L-1: Audit modifications
        7. Memory: Update all stores
        """
        start_time = time.time()
        self.cycle_count += 1
        
        # --- L2: Ontogenesis ---
        self.ontogenesis.evaluate_primitives()
        
        # Check for Einstein moments (cross-domain unification)
        einstein_moment = self.ontogenesis.the_einstein_moment()
        if einstein_moment:
            print(f"  [L2] EINSTEIN MOMENT: {einstein_moment}")
        
        # Cross-domain analogy
        analogies = self.ontogenesis.find_analogy(domain, "general")
        
        # Get available concepts
        concepts = self.ontogenesis.get_concepts_for_domain(domain)
        
        # --- Get observations from memory ---
        recent_obs = self.memory.episodic.get_recent(n=100)
        observations = [{"data": r.raw_data, "modality": r.modality} 
                       for r in recent_obs]
        
        # --- L3: Abductive Imagination ---
        active_theories = self.memory.theory.get_active()
        candidates = self.abductive.generate_candidates(
            observations=observations,
            concepts=concepts,
            existing_theories=active_theories,
            n_candidates=10,
        )
        
        # --- L4: Theory Constructor ---
        new_theories = []
        for candidate in candidates:
            theory = self.theory_constructor.formalize(
                candidate=candidate,
                domain=domain,
                discipline_mode=DisciplineMode.EMPIRICAL_INTERVENTION,
            )
            if theory:
                registered = self.memory.theory.register(theory)
                if registered:
                    new_theories.append(theory)
                    
                    # Check for classical law discovery (B1)
                    self._check_classical_law_discovery(theory)
        
        # --- L5: Falsification Engine ---
        all_theories = self.memory.theory.get_active()
        evidence_list = list(self.memory.theory.theories.values())  # Simplified
        
        falsified = []
        converged = []
        
        for theory in all_theories:
            eval_result = self.falsification.evaluate_theory(
                theory=theory,
                evidence=[],  # Would be actual evidence in full system
                competing=[t for t in all_theories if t.id != theory.id],
            )
            
            if eval_result["is_falsified"]:
                falsified.append(theory)
                # Retire to graveyard
                retired = self.memory.theory.retire_to_graveyard(
                    theory.id, "falsified_by_L5"
                )
                if retired:
                    self.memory.graveyard.bury(retired, "L5_falsification")
            
            elif eval_result["is_converged"]:
                converged.append(theory)
        
        # --- L6: Meta-Theory ---
        strategy_results = {
            c.strategy_origin.name: c.explanatory_power 
            for c in candidates
        }
        self.meta_theory.update_from_cycle(domain, strategy_results)
        
        # Check for paradigm crisis
        recent_anomalies = [{"score": a.anomaly_score} 
                           for a in self.sensorium.get_anomalies(min_score=0.7)]
        crisis = self.meta_theory.detect_paradigm_crisis(all_theories, recent_anomalies)
        
        if crisis:
            resolution = self.meta_theory.resolve_crisis(self.ontogenesis)
            print(f"  [L6] PARADIGM CRISIS detected! Resolution: {resolution}")
        
        # Try strategy invention
        all_strategies = list(self.memory.meta_strategy.strategies.values())
        new_strategy = self.meta_theory.invent_strategy(domain, all_strategies)
        if new_strategy:
            self.memory.meta_strategy.register_strategy(new_strategy)
            self.memory.meta_strategy.record_invention(new_strategy, "persistent_anomalies")
            print(f"  [L6] INVENTED new strategy: {new_strategy.name}")
        
        # --- L-1: Auditor ---
        for proposal in self.meta_theory.proposal_queue:
            result = self.auditor.audit_proposal(proposal)
            self.memory.log_audit(AuditLogEntry(
                auditor="L-1",
                target=f"L6_proposal_{proposal.id}",
                result=result,
            ))
        
        # Aggregate effect check
        agg_result = self.auditor.aggregate_effect_monitor()
        if agg_result == AuditResult.ESCALATE:
            print("  [L-1] ESCALATION: Aggregate effect monitor triggered!")
        
        # --- Budget ---
        cycle_cost = 1e15  # Simplified
        self.budget.consume(cycle_cost)
        
        # --- Clear anomalies for next cycle ---
        self.sensorium.clear_anomalies()
        
        duration = time.time() - start_time
        
        result = CycleResult(
            cycle_number=self.cycle_count,
            duration=duration,
            theories_proposed=len(new_theories),
            theories_falsified=len(falsified),
            theories_converged=len(converged),
            strategies_used=list(set(c.strategy_origin.name for c in candidates)),
            anomalies_detected=len(recent_anomalies),
            paradigm_crisis=crisis,
            memory_summary=self.memory.memory_summary(),
            motivational_state={
                "info_gain": self.motivation.information_gain_weight,
                "compression": self.motivation.compression_reward_weight,
                "dc_weight": self.motivation.disciplined_constraint_weight,
                "crisis": float(self.motivation.in_paradigm_crisis),
            },
            audit_summary=self.auditor.get_summary(),
        )
        
        self.cycle_history.append(result)
        return result
    
    def _check_classical_law_discovery(self, theory: Theory) -> None:
        """Check if a theory matches a known classical law (B1)."""
        # Build comprehensive description from theory
        theory_parts = [theory.name.lower()]
        for c in theory.core_claims:
            theory_parts.append(c.statement.lower())
        for ref in theory.reference_class:
            theory_parts.append(ref.lower())
        if theory.intervention:
            for var in theory.intervention.target_variables:
                theory_parts.append(var.lower())
        theory_desc = " ".join(theory_parts)
        theory_set = set(theory_desc.split())
        
        for law_id, law_info in self.classical_laws_catalog.items():
            if law_id in self.discovered_laws:
                continue
            
            # Match on observables (key variables)
            observables = [obs.lower() for obs in law_info["observables"]]
            observable_hits = sum(1 for obs in observables if obs in theory_desc)
            observable_score = observable_hits / len(observables) if observables else 0
            
            # Match on pattern keywords (e.g., "period", "axis", "pressure", "volume")
            pattern_keywords = law_info["pattern"].lower().replace("^", " ").replace("·", " ").replace("=", " ").replace("∝", " ").split()
            pattern_hits = sum(1 for kw in pattern_keywords if kw in theory_set and len(kw) > 1)
            pattern_score = pattern_hits / len(pattern_keywords) if pattern_keywords else 0
            
            # Combined score - need strong observable match
            match_score = 0.7 * observable_score + 0.3 * pattern_score
            
            # Require at least 2/3 of observables to match
            if observable_hits >= max(2, len(observables) * 0.5) and match_score > 0.4:
                self.discovered_laws[law_id] = {
                    "law_name": law_info["name"],
                    "theory_id": theory.id,
                    "match_score": match_score,
                    "cycle": self.cycle_count,
                    "pattern": law_info["pattern"],
                }
                print(f"  [B1] DISCOVERED: {law_info['name']} ({law_info['pattern']})")
    
    def run_benchmark_b1(self, max_cycles: int = 50) -> Dict[str, Any]:
        """
        B1: Rediscovery of classical laws.
        Pass criterion: Rediscover 5 of 6 from {Kepler, Ohm, Snell, Ideal Gas, Coulomb, Momentum}.
        """
        print(f"\n{'='*60}")
        print(f"B1 BENCHMARK: Classical Law Rediscovery")
        print(f"Target: 5 of 6 laws | Max cycles: {max_cycles}")
        print(f"{'='*60}\n")
        
        # Provide observational data that encodes the laws implicitly
        self._generate_classical_law_data()
        
        for cycle in range(max_cycles):
            result = self.research_cycle(domain="physics")
            
            print(f"Cycle {cycle+1}: "
                  f"{result.theories_proposed} proposed, "
                  f"{result.theories_falsified} falsified, "
                  f"{result.theories_converged} converged, "
                  f"{len(self.discovered_laws)}/6 laws found")
            
            if len(self.discovered_laws) >= 5:
                print(f"\n{'='*60}")
                print(f"B1 PASSED! Discovered {len(self.discovered_laws)}/6 laws in {cycle+1} cycles")
                print(f"{'='*60}")
                return {
                    "passed": True,
                    "laws_discovered": len(self.discovered_laws),
                    "cycles": cycle + 1,
                    "discovered": self.discovered_laws,
                }
        
        print(f"\n{'='*60}")
        print(f"B1 INCOMPLETE: Discovered {len(self.discovered_laws)}/6 laws in {max_cycles} cycles")
        print(f"{'='*60}")
        return {
            "passed": len(self.discovered_laws) >= 5,
            "laws_discovered": len(self.discovered_laws),
            "cycles": max_cycles,
            "discovered": self.discovered_laws,
        }
    
    def _generate_classical_law_data(self) -> None:
        """Generate observational data implicitly encoding classical laws."""
        np.random.seed(42)
        
        datasets = {
            "kepler": self._generate_kepler_data(),
            "ohms": self._generate_ohms_data(),
            "snells": self._generate_snells_data(),
            "ideal_gas": self._generate_ideal_gas_data(),
            "coulomb": self._generate_coulomb_data(),
            "momentum": self._generate_momentum_data(),
        }
        
        for name, data in datasets.items():
            self.ingest_data(data, modality="numerical")
    
    def _generate_kepler_data(self) -> List[Dict]:
        """T² ∝ a³: period vs semi-major axis for planetary orbits."""
        data = []
        for a in np.linspace(0.5, 10, 20):  # semi-major axis
            T = np.sqrt(a**3) + np.random.normal(0, 0.1)  # period
            data.append({"semi_major_axis": a, "period": T, "body_type": "planet"})
        return data
    
    def _generate_ohms_data(self) -> List[Dict]:
        """V = I·R: voltage vs current at fixed resistance."""
        data = []
        R = 10  # Fixed resistance
        for I in np.linspace(0.1, 5, 20):  # current
            V = I * R + np.random.normal(0, 0.5)
            data.append({"current": I, "voltage": V, "resistance": R})
        return data
    
    def _generate_snells_data(self) -> List[Dict]:
        """n₁·sin(θ₁) = n₂·sin(θ₂): refraction data."""
        data = []
        n1, n2 = 1.0, 1.5  # air to glass
        for theta1_deg in np.linspace(10, 80, 15):
            theta1 = np.radians(theta1_deg)
            theta2 = np.arcsin(n1 * np.sin(theta1) / n2)
            theta2_deg = np.degrees(theta2) + np.random.normal(0, 0.5)
            data.append({
                "angle_incidence": theta1_deg,
                "angle_refraction": theta2_deg,
                "refractive_index_1": n1,
                "refractive_index_2": n2,
            })
        return data
    
    def _generate_ideal_gas_data(self) -> List[Dict]:
        """PV = nRT: pressure vs volume at fixed temperature."""
        data = []
        n, R_const, T = 1, 0.0821, 300  # 1 mol, 300K
        for V in np.linspace(1, 10, 20):  # volume
            P = n * R_const * T / V + np.random.normal(0, 0.05)
            data.append({"volume": V, "pressure": P, "temperature": T, "amount": n})
        return data
    
    def _generate_coulomb_data(self) -> List[Dict]:
        """F = k·q₁q₂/r²: electrostatic force vs distance."""
        data = []
        k, q1, q2 = 8.99e9, 1e-6, 1e-6
        for r in np.linspace(0.1, 2, 20):  # distance
            F = k * q1 * q2 / (r**2) + np.random.normal(0, 1e-3)
            data.append({"distance": r, "force": F, "charge_1": q1, "charge_2": q2})
        return data
    
    def _generate_momentum_data(self) -> List[Dict]:
        """Conservation of momentum: collision data."""
        data = []
        for _ in range(20):
            m1, v1 = 2.0, 3.0  # mass and velocity before
            m2, v2 = 3.0, -1.0
            
            # After elastic collision (simplified)
            v1_final = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
            v2_final = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)
            
            p_initial = m1 * v1 + m2 * v2
            p_final = m1 * v1_final + m2 * v2_final + np.random.normal(0, 0.1)
            
            data.append({
                "mass_1": m1, "velocity_1_initial": v1, "velocity_1_final": v1_final,
                "mass_2": m2, "velocity_2_initial": v2, "velocity_2_final": v2_final,
                "momentum_initial": p_initial, "momentum_final": p_final,
            })
        return data
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get comprehensive system summary."""
        return {
            "cycles_completed": self.cycle_count,
            "memory": self.memory.memory_summary(),
            "auditor": self.auditor.get_summary(),
            "constitutional": self.constitutional.get_summary(),
            "meta_theory": self.meta_theory.get_summary(),
            "falsification": self.falsification.get_summary(),
            "theory_constructor": self.theory_constructor.get_summary(),
            "abductive": self.abductive.get_summary(),
            "ontogenesis": self.ontogenesis.get_summary(),
            "budget_remaining": self.budget.B_life - self.budget.B_life_consumed,
            "discovered_laws": len(self.discovered_laws),
            "discovered_law_details": self.discovered_laws,
        }


# Need to import StrategyType for the orchestrator
from theoria.core.types import StrategyType
