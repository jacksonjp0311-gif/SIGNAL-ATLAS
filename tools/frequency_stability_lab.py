#!/usr/bin/env python3
"""Generate a fixed-seed synthetic fractional-frequency series and Allan deviation."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def synthetic_series(count: int = 128, seed: int = 1065) -> list[float]:
    rng = random.Random(seed)
    return [1.2e-10 + (index - count / 2) * 1.5e-13 + rng.gauss(0.0, 2.0e-10) for index in range(count)]


def allan_deviation(values: list[float], tau_samples: int) -> dict:
    if tau_samples < 1:
        raise ValueError("tau_samples must be positive")
    averages = [sum(values[i:i + tau_samples]) / tau_samples for i in range(0, len(values) - tau_samples + 1, tau_samples)]
    if len(averages) < 2:
        raise ValueError("at least two non-overlapping averages are required")
    variance = sum((averages[i + 1] - averages[i]) ** 2 for i in range(len(averages) - 1)) / (2 * (len(averages) - 1))
    return {"tau_samples": tau_samples, "tau_seconds": tau_samples, "block_average_count": len(averages), "allan_variance": variance, "allan_deviation": math.sqrt(variance)}


def result() -> dict:
    values = synthetic_series()
    serialized = json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return {
        "schema": "signal-atlas-synthetic-frequency-stability/0.6",
        "data_status": "synthetic illustration; not a measured device or calibration result",
        "generator": {"method": "Python random.Random Gaussian samples plus deterministic linear drift", "seed": 1065, "python_dependency": "standard library only", "nominal_frequency_hz": 10_000_000, "sample_interval_seconds": 1, "fractional_frequency_unit": "dimensionless"},
        "sample_count": len(values), "input_sha256": hashlib.sha256(serialized).hexdigest(),
        "fractional_frequency_samples": values,
        "estimator": "non-overlapping adjacent block means; Allan variance = mean squared adjacent difference / 2; deviation = square root",
        "results": [allan_deviation(values, tau) for tau in (1, 2, 4, 8, 16)],
        "limitations": ["Synthetic values do not model a particular oscillator.", "Stability at an averaging interval does not establish frequency accuracy.", "No traceability or calibration uncertainty budget is simulated.", "The simple non-overlapping estimator assumes regularly sampled data with no gaps."]
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    content = json.dumps(result(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.replace("\r\n", "\n").encode("utf-8"))
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
