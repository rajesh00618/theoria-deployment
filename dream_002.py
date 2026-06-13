"""
DREAM-002: Surprise vs Dream Intensity

Tests whether surprising days produce stronger dreams.

Simulates 60 days of daily life with prediction errors,
then measures correlation between surprise and dream vividness.

Prediction: Higher surprise -> Higher dream vividness
Success criterion: Correlation > 0.5
"""

import numpy as np
import csv
import json
import time
from dataclasses import dataclass
from typing import List, Dict


# ============================================================================
# Daily Life Simulator
# ============================================================================

@dataclass
class DailyEvent:
    event_type: str
    expected: float  # 0-1, what the agent expected
    actual: float    # 0-1, what actually happened
    surprise: float  # |expected - actual|
    emotional_weight: float  # 0-1, how important the event was


@dataclass
class DailyRecord:
    day: int
    events: List[DailyEvent]
    total_surprise: float
    total_stress: float
    emotional_intensity: float


@dataclass
class DreamRecord:
    day: int
    vividness: float  # 0-1
    recall: float  # 0-1
    content_surprise: float  # how much surprise in dream content
    n_errors_replayed: int
    resolution: float  # 0-1, how much error was resolved


class DailyLifeSimulator:
    """Simulate daily life with prediction errors."""

    def __init__(self, n_days=60, seed=42):
        self.n_days = n_days
        self.rng = np.random.RandomState(seed)

        # Event types with base probabilities
        self.event_types = [
            ("social_interaction", 0.3, 0.5),   # type, freq, emotional_weight
            ("work_task", 0.25, 0.6),
            ("unexpected_news", 0.1, 0.8),
            ("routine_activity", 0.2, 0.2),
            ("creative_problem", 0.15, 0.7),
        ]

        # Prediction accuracy improves over time (learning)
        self.prediction_accuracy = 0.5  # starts at 50%

    def simulate_day(self, day: int) -> DailyRecord:
        """Simulate one day of events."""
        events = []
        n_events = self.rng.randint(3, 8)

        for _ in range(n_events):
            # Select event type
            probs = [e[1] for e in self.event_types]
            probs = np.array(probs) / sum(probs)
            type_idx = self.rng.choice(len(self.event_types), p=probs)
            event_type, _, emotional_weight = self.event_types[type_idx]

            # Generate expected outcome
            expected = self.rng.uniform(0, 1)

            # Generate actual outcome (correlated with expectation)
            # Higher prediction accuracy = actual closer to expected
            noise = self.rng.normal(0, 1 - self.prediction_accuracy)
            actual = np.clip(expected + noise * 0.3, 0, 1)

            # Surprise = prediction error
            surprise = abs(expected - actual)

            events.append(DailyEvent(
                event_type=event_type,
                expected=expected,
                actual=actual,
                surprise=surprise,
                emotional_weight=emotional_weight,
            ))

        # Compute daily metrics
        total_surprise = sum(e.surprise * e.emotional_weight for e in events) / len(events)
        total_stress = sum(e.surprise for e in events) / len(events)
        emotional_intensity = sum(e.emotional_weight for e in events) / len(events)

        # Learning: prediction accuracy improves slightly
        self.prediction_accuracy = min(0.9, self.prediction_accuracy + 0.005)

        return DailyRecord(
            day=day,
            events=events,
            total_surprise=float(total_surprise),
            total_stress=float(total_stress),
            emotional_intensity=float(emotional_intensity),
        )

    def simulate_n_days(self) -> List[DailyRecord]:
        """Simulate multiple days."""
        return [self.simulate_day(d) for d in range(self.n_days)]


# ============================================================================
# Dream Generator (Prediction Error Theory)
# ============================================================================

class DreamGenerator:
    """
    Generate dreams based on prediction error theory.

    Core mechanism:
    - During sleep, the brain replays prediction errors from the day
    - Larger errors produce more vivid dreams
    - Some errors are resolved (reduced emotional charge)
    - Some errors persist (nightmares, recurrent dreams)
    """

    def __init__(self, seed=42):
        self.rng = np.random.RandomState(seed)
        self.memory_errors = []  # Accumulated unresolved errors

    def generate_dream(self, daily_record: DailyRecord, day: int) -> DreamRecord:
        """Generate a dream based on the day's prediction errors."""
        # Collect prediction errors from the day
        errors = []
        for event in daily_record.events:
            if event.surprise > 0.2:  # Only significant errors are replayed
                errors.append({
                    "type": event.event_type,
                    "error": event.surprise,
                    "weight": event.emotional_weight,
                })

        # Add some accumulated errors from previous days
        if self.memory_errors:
            # Old errors fade (exponential decay)
            self.memory_errors = [
                {"error": e["error"] * 0.8, "weight": e["weight"]}
                for e in self.memory_errors
                if e["error"] * 0.8 > 0.1  # Drop if too small
            ]
            errors.extend(self.memory_errors[:3])  # Add top 3 old errors

        if not errors:
            # No significant errors -> boring dream
            return DreamRecord(
                day=day,
                vividness=0.1,
                recall=0.1,
                content_surprise=0.0,
                n_errors_replayed=0,
                resolution=0.9,
            )

        # Dream vividness = sum of error magnitudes
        total_error_weight = sum(e["error"] * e["weight"] for e in errors)
        vividness = min(1.0, total_error_weight * 2)

        # Dream recall = vividness * random factor
        recall = vividness * self.rng.uniform(0.5, 1.0)

        # Content surprise = how surprising the dream content is
        content_surprise = min(1.0, np.mean([e["error"] for e in errors]) * 2)

        # Resolution = some errors are partially resolved in dream
        resolution = self.rng.uniform(0.2, 0.8)

        # Some errors persist to next day (unresolved)
        unresolved = [e for e in errors if self.rng.random() > resolution]
        self.memory_errors.extend(unresolved)

        return DreamRecord(
            day=day,
            vividness=float(vividness),
            recall=float(recall),
            content_surprise=float(content_surprise),
            n_errors_replayed=len(errors),
            resolution=float(resolution),
        )


# ============================================================================
# Analysis
# ============================================================================

def analyze_surprise_dream_correlation(daily_records: List[DailyRecord],
                                        dream_records: List[DreamRecord]) -> Dict:
    """Analyze correlation between surprise and dream intensity."""
    surprises = [d.total_surprise for d in daily_records]
    vividness = [dr.vividness for dr in dream_records]
    recall = [dr.recall for dr in dream_records]
    content_surprise = [dr.content_surprise for dr in dream_records]

    # Pearson correlation
    from scipy.stats import pearsonr, spearmanr

    r_vividness, p_vividness = pearsonr(surprises, vividness)
    r_recall, p_recall = pearsonr(surprises, recall)
    r_content, p_content = pearsonr(surprises, content_surprise)

    # Spearman (rank) correlation
    rho_vividness, _ = spearmanr(surprises, vividness)

    return {
        "pearson_surprise_vividness": float(r_vividness),
        "pearson_p_value": float(p_vividness),
        "pearson_surprise_recall": float(r_recall),
        "pearson_surprise_content": float(r_content),
        "spearman_surprise_vividness": float(rho_vividness),
        "mean_surprise": float(np.mean(surprises)),
        "std_surprise": float(np.std(surprises)),
        "mean_vividness": float(np.mean(vividness)),
        "std_vividness": float(np.std(vividness)),
        "mean_recall": float(np.mean(recall)),
        "mean_errors_replayed": float(np.mean([dr.n_errors_replayed for dr in dream_records])),
        "mean_resolution": float(np.mean([dr.resolution for dr in dream_records])),
    }


def run_experiment(n_days=60, n_trials=10, seed=42):
    """Run the full experiment."""
    all_results = []

    for trial in range(n_trials):
        # Simulate daily life
        simulator = DailyLifeSimulator(n_days=n_days, seed=seed + trial)
        daily_records = simulator.simulate_n_days()

        # Generate dreams
        dream_gen = DreamGenerator(seed=seed + trial + 1000)
        dream_records = [dream_gen.generate_dream(d, d.day) for d in daily_records]

        # Analyze
        result = analyze_surprise_dream_correlation(daily_records, dream_records)
        result["trial"] = trial
        all_results.append(result)

    return all_results


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 70)
    print("  DREAM-002: Surprise vs Dream Intensity")
    print("  Testing: Do surprising days produce stronger dreams?")
    print("=" * 70)

    t0 = time.time()

    # Run experiment
    print("\n  Running experiment (60 days x 10 trials)")
    results = run_experiment(n_days=60, n_trials=10)

    # Aggregate results
    r_vividness = [r["pearson_surprise_vividness"] for r in results]
    r_recall = [r["pearson_surprise_recall"] for r in results]
    r_content = [r["pearson_surprise_content"] for r in results]
    p_values = [r["pearson_p_value"] for r in results]

    mean_r = np.mean(r_vividness)
    std_r = np.std(r_vividness)
    mean_p = np.mean(p_values)

    print(f"\n  RESULTS")
    print(f"  {'='*50}")
    print(f"  Surprise-Vividness correlation: r = {mean_r:.3f} +/- {std_r:.3f}")
    print(f"  Mean p-value: {mean_p:.4f}")
    print(f"  Mean surprise: {np.mean([r['mean_surprise'] for r in results]):.3f}")
    print(f"  Mean vividness: {np.mean([r['mean_vividness'] for r in results]):.3f}")
    print(f"  Mean errors replayed: {np.mean([r['mean_errors_replayed'] for r in results]):.1f}")
    print(f"  Mean resolution: {np.mean([r['mean_resolution'] for r in results]):.3f}")

    # Verdict
    print(f"\n  VERDICT")
    print(f"  {'='*50}")

    if mean_r > 0.5 and mean_p < 0.05:
        print(f"  SUCCESS: Surprise-Dream correlation confirmed (r = {mean_r:.3f} > 0.5)")
        print(f"  The prediction error theory is SUPPORTED")
        verdict = "SUPPORTED"
    elif mean_r > 0.3:
        print(f"  PARTIAL: Moderate correlation (r = {mean_r:.3f})")
        print(f"  The prediction error theory is PARTIALLY SUPPORTED")
        verdict = "PARTIAL"
    else:
        print(f"  FAILURE: Weak correlation (r = {mean_r:.3f} < 0.3)")
        print(f"  The prediction error theory is NOT SUPPORTED")
        verdict = "NOT_SUPPORTED"

    # Individual trial results
    print(f"\n  INDIVIDUAL TRIALS")
    print(f"  {'='*50}")
    for r in results:
        print(f"  Trial {r['trial']:2d}: r = {r['pearson_surprise_vividness']:.3f}, "
              f"p = {r['pearson_p_value']:.4f}")

    # Save
    with open("dream_surprise_results.json", "w") as f:
        json.dump({
            "verdict": verdict,
            "mean_correlation": float(mean_r),
            "std_correlation": float(std_r),
            "mean_p_value": float(mean_p),
            "trial_results": results,
        }, f, indent=2)
    print("\n  Saved dream_surprise_results.json")

    with open("dream_surprise_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print("  Saved dream_surprise_results.csv")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")

    print("\n" + "=" * 70)
    print("  DREAM-002 COMPLETE")
    print("=" * 70)

    return verdict


if __name__ == "__main__":
    main()
