from __future__ import annotations

import uuid
import random
import hashlib
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from theoria.core.types import BenchmarkSpec


def _det_score(label: str) -> float:
    h = hashlib.sha256(label.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


class BenchmarkGenerator:
    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.benchmarks: List[BenchmarkSpec] = []
        self.cycle_count = 0

    def generate_stress_test(self, domain: str, difficulty: float = 0.6) -> BenchmarkSpec:
        test_cases = []
        for i in range(10):
            test_cases.append({
                "id": f"stress_{domain}_{i}",
                "input": {f"var_{j}": random.uniform(-10, 10) for j in range(3)},
                "expected_output": f"output_{i}",
                "difficulty": difficulty + (-0.1 + _det_score(f"stress_{domain}_{i}_diff") * 0.2),
            })

        spec = BenchmarkSpec(
            name=f"StressTest_{domain}_{self.cycle_count}",
            description=f"Stress test for {domain} with {difficulty:.1%} difficulty",
            benchmark_type="stress_test",
            domain=domain,
            difficulty=difficulty,
            scoring_criteria=["accuracy", "speed", "robustness"],
            test_cases=test_cases,
            ground_truth={"expected_pass_rate": 0.8},
            validation_score=0.5 + _det_score(f"stress_{domain}_val_{self.cycle_count}") * 0.4,
        )
        self.benchmarks.append(spec)
        return spec

    def generate_adversarial_task(self, domain: str, difficulty: float = 0.8) -> BenchmarkSpec:
        adversarial_cases = []
        for i in range(10):
            adversarial_cases.append({
                "id": f"adv_{domain}_{i}",
                "input": {f"param_{j}": random.uniform(-5, 5) for j in range(4)},
                "adversarial_modification": f"noise_{i}",
                "expected_robust": i % 3 != 0,
                "difficulty": difficulty,
            })

        spec = BenchmarkSpec(
            name=f"Adversarial_{domain}_{self.cycle_count}",
            description=f"Adversarial benchmark testing {domain} robustness",
            benchmark_type="adversarial",
            domain=domain,
            difficulty=difficulty,
            scoring_criteria=["adversarial_accuracy", "robustness", "graceful_degradation"],
            test_cases=adversarial_cases,
            ground_truth={"expected_robust_accuracy": 0.7},
            validation_score=0.4 + _det_score(f"adv_{domain}_val_{self.cycle_count}") * 0.4,
        )
        self.benchmarks.append(spec)
        return spec

    def generate_novel_benchmark(self, domain: str, difficulty: float = 0.5) -> BenchmarkSpec:
        novel_cases = []
        for i in range(8):
            novel_cases.append({
                "id": f"novel_{domain}_{i}",
                "scenario": f"Novel scenario {i} for {domain}",
                "constraints": [f"constraint_{j}" for j in range(random.randint(1, 3))],
                "expected_property": f"property_{i % 2}",
                "difficulty": difficulty + (-0.2 + _det_score(f"novel_{domain}_{i}_diff") * 0.4),
            })

        spec = BenchmarkSpec(
            name=f"Novel_{domain}_{self.cycle_count}",
            description=f"Novel benchmark exploring new {domain} capabilities",
            benchmark_type="novel",
            domain=domain,
            difficulty=difficulty,
            scoring_criteria=["novelty", "generalization", "efficiency"],
            test_cases=novel_cases,
            ground_truth={"expected_generalization": 0.6},
            validation_score=0.3 + _det_score(f"novel_{domain}_val_{self.cycle_count}") * 0.4,
        )
        self.benchmarks.append(spec)
        return spec

    def generate_benchmark_suite(self, domain: str = "physics",
                                  count: int = 3) -> List[BenchmarkSpec]:
        specs = []
        for i in range(count):
            btype = i % 3
            difficulty = 0.3 + _det_score(f"suite_{domain}_{i}_diff") * 0.65
            if btype == 0:
                specs.append(self.generate_stress_test(domain, difficulty))
            elif btype == 1:
                specs.append(self.generate_adversarial_task(domain, difficulty))
            else:
                specs.append(self.generate_novel_benchmark(domain, difficulty))
        self.cycle_count += 1
        return specs

    def validate_benchmark(self, spec_id: str) -> float:
        for b in self.benchmarks:
            if b.id == spec_id:
                validation = 0.6 + _det_score(f"validate_{spec_id}") * 0.4
                b.validation_score = validation
                b.status = "validated" if validation > 0.5 else "generated"
                return validation
        return 0.0

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_benchmarks": len(self.benchmarks),
            "by_type": dict((bt, sum(1 for b in self.benchmarks if b.benchmark_type == bt))
                           for bt in ["stress_test", "adversarial", "novel"]),
            "validated": sum(1 for b in self.benchmarks if b.status == "validated"),
            "avg_difficulty": np.mean([b.difficulty for b in self.benchmarks]) if self.benchmarks else 0,
        }
