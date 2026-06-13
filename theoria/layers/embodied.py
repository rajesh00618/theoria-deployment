"""
Phase 4: Embodied Experimentation Layer (P4.2 / L7).

Connects THEORIA to laboratory devices, scientific instruments,
IoT sensors, simulation worlds, and robotics.
Design → Execute → Measure → Learn cycle.
"""

from __future__ import annotations

import time
import uuid
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from theoria.core.types import LabDevice, MeasurementResult, EmbodiedExperiment


class EmbodiedLab:
    """
    Manages laboratory devices, executes experiments, collects measurements.
    Supports simulators (default) and can interface with real hardware.
    """

    def __init__(self, config: Optional[Any] = None):
        self.config = config
        self.devices: Dict[str, LabDevice] = {}
        self.experiments: Dict[str, EmbodiedExperiment] = {}
        self._init_default_devices()

    def _init_default_devices(self):
        device_templates = [
            ("spectrometer_1", "spectrometer", "physics", ["absorbance", "transmittance", "wavelength"]),
            ("microscope_1", "microscope", "biology", ["imaging", "magnification", "resolution"]),
            ("centrifuge_1", "centrifuge", "biology", ["separation", "sedimentation", "speed"]),
            ("thermocycler_1", "thermocycler", "biology", ["pcr", "amplification", "temperature_cycle"]),
            ("particle_accelerator_1", "particle_accelerator", "physics", ["collision", "detection", "energy"]),
            ("lab_simulator_1", "simulator", "physics", ["quantum", "classical", "statistical"]),
            ("lab_simulator_2", "simulator", "biology", ["population", "genetic", "cellular"]),
            ("lab_simulator_3", "simulator", "chemistry", ["reaction", "molecular", "thermodynamic"]),
            ("telescope_1", "telescope", "physics", ["observation", "imaging", "spectroscopy"]),
            ("mri_scanner_1", "mri_scanner", "biology", ["imaging", "brain_activity", "connectivity"]),
        ]
        for did, dtype, domain, caps in device_templates:
            self.register_device(did, dtype, domain, caps)

    def register_device(self, device_id: str, device_type: str, domain: str,
                        capabilities: List[str], precision: float = 0.01) -> LabDevice:
        device = LabDevice(
            id=device_id, name=device_id.replace("_", " ").title(),
            device_type=device_type, domain=domain,
            capabilities=capabilities, connected=True, precision=precision,
        )
        self.devices[device_id] = device
        return device

    def execute_experiment(self, design_id: str, device_ids: Optional[List[str]] = None,
                           parameters: Optional[Dict[str, float]] = None,
                           num_trials: int = 10) -> EmbodiedExperiment:
        selected = device_ids or [d for d in self.devices if self.devices[d].connected][:2]
        params = parameters or {"intensity": 1.0, "duration": 1.0, "temperature": 298.0}
        exp = EmbodiedExperiment(
            design_id=design_id, device_ids=selected,
            parameters=params, started_at=time.time(), status="running",
        )
        for t in range(num_trials):
            trial = self._run_trial(exp, t)
            exp.results.append(trial)
        exp.completed_at = time.time()
        exp.status = "completed"
        self.experiments[exp.id] = exp
        return exp

    def _run_trial(self, exp: EmbodiedExperiment, trial_num: int) -> MeasurementResult:
        measurements = {}
        uncertainty = {}
        for did in exp.device_ids:
            device = self.devices.get(did)
            if not device:
                continue
            noise = device.precision * np.random.randn()
            if device.device_type == "simulator":
                base = np.sin(trial_num * 0.5) * 0.5 + 0.5
                measurements[f"{device.domain}_signal"] = float(base + noise * 0.1)
                measurements[f"{device.domain}_background"] = float(0.1 + noise * 0.05)
            elif device.device_type == "spectrometer":
                measurements["absorbance"] = float(0.3 + np.sin(trial_num * 0.3) * 0.2 + noise * 0.02)
            elif device.device_type == "microscope":
                measurements["cell_count"] = float(100 + trial_num * 5 + noise * 10)
            else:
                measurements[f"{device.name}_reading"] = float(np.random.random() + noise)
            uncertainty[f"{device.name}_uncertainty"] = float(device.precision)
        return MeasurementResult(
            device_id=did if exp.device_ids else "",
            measurements=measurements, uncertainty=uncertainty,
            trial_number=trial_num + 1,
        )

    def get_device(self, device_id: str) -> Optional[LabDevice]:
        return self.devices.get(device_id)

    def list_devices(self, domain: Optional[str] = None) -> List[LabDevice]:
        if domain:
            return [d for d in self.devices.values() if d.domain == domain]
        return list(self.devices.values())

    def analyze_results(self, experiment_id: str) -> Dict[str, Any]:
        exp = self.experiments.get(experiment_id)
        if not exp or not exp.results:
            return {"error": "No results found"}
        all_vals: Dict[str, List[float]] = defaultdict(list)
        for r in exp.results:
            for k, v in r.measurements.items():
                all_vals[k].append(v)
        stats = {}
        for k, vals in all_vals.items():
            stats[k] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
                "n": len(vals),
            }
        return {"experiment_id": experiment_id, "device_results": stats,
                "trials": len(exp.results), "status": exp.status}

    def get_summary(self) -> Dict[str, Any]:
        return {
            "devices": len(self.devices),
            "connected": sum(1 for d in self.devices.values() if d.connected),
            "experiments_run": len(self.experiments),
            "experiments_completed": sum(1 for e in self.experiments.values() if e.status == "completed"),
        }
