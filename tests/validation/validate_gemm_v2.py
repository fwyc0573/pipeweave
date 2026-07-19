"""Audit DES GEMM schedule estimates against measured durations.

Reports:
- Bound violations for DES and a dimensionally correct classical roofline
- Paired tightness only where both candidate bounds are valid
- Explicit unsupported-policy counts and simulator wall-clock runtime

The greedy DES scheduler is an explanatory estimate. This harness checks, but
does not certify, whether a returned estimate is a lower bound on a given row.
"""

from collections import Counter
from dataclasses import dataclass
from math import isfinite
from numbers import Real
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from event_simulator import (
    derive_calibration,
    derive_resource_config,
    load_hardware_config,
    lower_gemm_v2,
    schedule,
)
from event_simulator.structural import ceil_div


class UnsupportedGemmRow(ValueError):
    """A dataset row whose launch policy is not modeled by GEMM v2."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"unsupported GEMM row: {reason}")


@dataclass(frozen=True)
class GemmValidationCase:
    m: int
    n: int
    k: int
    tile_m: int
    tile_n: int
    tile_k: int
    cta_count: int


@dataclass(frozen=True)
class ValidationBatch:
    actual_times: tuple[float, ...]
    des_times: tuple[float, ...]
    roofline_times: tuple[float, ...]
    simulator_runtimes: tuple[float, ...]
    unsupported_counts: dict[str, int]


def classical_roofline(row, hw_config):
    """Return a roofline estimate on the cold-input/L2-output boundary."""
    m = _positive_row_int(row, "M", "non_positive_problem_dimension")
    n = _positive_row_int(row, "N", "non_positive_problem_dimension")
    k = _positive_row_int(row, "K", "non_positive_problem_dimension")
    element_bytes = 2  # bf16

    flops = 2.0 * m * n * k
    hbm_input_bytes = (m * k + n * k) * element_bytes
    l2_output_bytes = m * n * element_bytes

    compute_time_us = flops / hw_config.tc_bf16_flops_per_us
    hbm_input_time_us = hbm_input_bytes / hw_config.mem_bandwidth_bytes_per_us
    l2_output_time_us = l2_output_bytes / hw_config.l2_bandwidth_bytes_per_us

    return max(compute_time_us, hbm_input_time_us, l2_output_time_us)


def des_predict(row, hw_config, calibration, resource_config):
    """Run GEMM v2 for a supported launch policy and return its makespan."""
    case = _parse_supported_case(row)
    events = lower_gemm_v2(
        "gemm-val",
        m=case.m,
        n=case.n,
        k=case.k,
        tile_m=case.tile_m,
        tile_n=case.tile_n,
        tile_k=case.tile_k,
        calibration=calibration,
        hardware=hw_config,
        element_bytes=2,
    )
    result = schedule(events, resource_config)
    if not isfinite(result.makespan) or result.makespan <= 0.0:
        raise ValueError("DES schedule estimate must be finite and positive")
    return result.makespan


def _parse_supported_case(row) -> GemmValidationCase:
    m = _positive_row_int(row, "M", "non_positive_problem_dimension")
    n = _positive_row_int(row, "N", "non_positive_problem_dimension")
    k = _positive_row_int(row, "K", "non_positive_problem_dimension")
    tile_m = _positive_row_int(row, "tile_M", "non_positive_tile")
    tile_n = _positive_row_int(row, "tile_N", "non_positive_tile")
    tile_k = _positive_row_int(row, "tile_K", "non_positive_tile")
    cta_count = _positive_row_int(row, "cta_count", "non_positive_cta_count")

    split_k = row["is_split_k"]
    if not _is_finite_integer(split_k):
        raise UnsupportedGemmRow("invalid_split_k")
    if int(split_k) != 0:
        raise UnsupportedGemmRow("split_k")

    tile_grid_count = ceil_div(m, tile_m) * ceil_div(n, tile_n)
    if cta_count != tile_grid_count:
        raise UnsupportedGemmRow("cta_count_mismatch")

    return GemmValidationCase(
        m=m,
        n=n,
        k=k,
        tile_m=tile_m,
        tile_n=tile_n,
        tile_k=tile_k,
        cta_count=cta_count,
    )


def _positive_row_int(row, name: str, reason: str) -> int:
    value = row[name]
    if not _is_finite_integer(value) or value <= 0:
        raise UnsupportedGemmRow(reason)
    return int(value)


def _is_finite_integer(value) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Real)
        and isfinite(value)
        and float(value).is_integer()
    )


def _actual_time(row) -> float:
    value = row["avg_duration"]
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not isfinite(value)
        or value <= 0.0
    ):
        raise UnsupportedGemmRow("invalid_actual_time")
    return float(value)


def evaluate_sample(sample, hw_config, calibration, resource_config) -> ValidationBatch:
    """Evaluate supported rows while counting every deliberate rejection."""
    actual_times: list[float] = []
    des_times: list[float] = []
    roofline_times: list[float] = []
    simulator_runtimes: list[float] = []
    unsupported_counts: Counter[str] = Counter()

    for _, row in sample.iterrows():
        try:
            actual = _actual_time(row)
            start_time = perf_counter()
            des_time = des_predict(row, hw_config, calibration, resource_config)
        except UnsupportedGemmRow as error:
            unsupported_counts[error.reason] += 1
            continue
        simulator_runtime = perf_counter() - start_time
        roofline_time = classical_roofline(row, hw_config)

        actual_times.append(actual)
        des_times.append(des_time)
        roofline_times.append(roofline_time)
        simulator_runtimes.append(simulator_runtime)

    return ValidationBatch(
        actual_times=tuple(actual_times),
        des_times=tuple(des_times),
        roofline_times=tuple(roofline_times),
        simulator_runtimes=tuple(simulator_runtimes),
        unsupported_counts=dict(sorted(unsupported_counts.items())),
    )


def summarize_predictions(
    des_times, roofline_times, actual_times
) -> dict[str, int | float | None]:
    """Summarize violations and paired gaps without clamping invalid values."""
    des_arr = np.asarray(des_times, dtype=float)
    roof_arr = np.asarray(roofline_times, dtype=float)
    actual_arr = np.asarray(actual_times, dtype=float)
    if des_arr.shape != roof_arr.shape or des_arr.shape != actual_arr.shape:
        raise ValueError("prediction arrays must have identical shapes")
    if des_arr.ndim != 1 or des_arr.size == 0:
        raise ValueError("prediction arrays must be non-empty and one-dimensional")
    if (
        not np.all(np.isfinite(des_arr))
        or not np.all(np.isfinite(roof_arr))
        or not np.all(np.isfinite(actual_arr))
        or np.any(des_arr <= 0.0)
        or np.any(roof_arr <= 0.0)
        or np.any(actual_arr <= 0.0)
    ):
        raise ValueError("prediction and actual times must be finite and positive")

    des_valid = des_arr <= actual_arr
    roof_valid = roof_arr <= actual_arr
    both_valid = des_valid & roof_valid
    paired_des = des_arr[both_valid]
    paired_roof = roof_arr[both_valid]
    paired_actual = actual_arr[both_valid]

    summary: dict[str, int | float | None] = {
        "evaluated": int(des_arr.size),
        "des_violations": int(np.sum(~des_valid)),
        "roofline_violations": int(np.sum(~roof_valid)),
        "both_valid": int(np.sum(both_valid)),
        "des_strictly_tighter": int(np.sum(paired_des > paired_roof)),
        "roofline_strictly_tighter": int(np.sum(paired_roof > paired_des)),
        "equal_bounds": int(np.sum(paired_des == paired_roof)),
        "des_mean_gap": None,
        "des_median_gap": None,
        "roofline_mean_gap": None,
        "roofline_median_gap": None,
    }
    if paired_actual.size:
        des_gap = (paired_actual - paired_des) / paired_actual
        roofline_gap = (paired_actual - paired_roof) / paired_actual
        summary.update(
            {
                "des_mean_gap": float(np.mean(des_gap)),
                "des_median_gap": float(np.median(des_gap)),
                "roofline_mean_gap": float(np.mean(roofline_gap)),
                "roofline_median_gap": float(np.median(roofline_gap)),
            }
        )
    return summary


def partition_categories(df) -> dict[str, pd.DataFrame]:
    """Partition every row into one disjoint validation category."""
    large_mask = (df["M"] >= 1024) & (df["N"] >= 1024) & (df["K"] >= 1024)
    medium_mask = (df["M"] >= 256) & (df["M"] < 1024)
    small_mask = df["M"] < 256
    other_mask = ~(large_mask | medium_mask | small_mask)
    return {
        "Large": df[large_mask],
        "Medium": df[medium_mask],
        "Small": df[small_mask],
        "Other": df[other_mask],
    }


def main():
    hw_path = Path("hardware/H100.json")
    hw = load_hardware_config(hw_path)
    cal = derive_calibration(hw)
    rc = derive_resource_config(hw, operator_type="gemm_v2")

    df = pd.read_csv("dataset/gemm_test.csv")
    df_h100 = df[df["hardware"].str.contains("H100")].copy()
    print(f"H100 GEMM test samples: {len(df_h100)}")

    categories = partition_categories(df_h100)
    if sum(len(category) for category in categories.values()) != len(df_h100):
        raise RuntimeError("validation category partition is not exhaustive")
    print(f"  Large (M,N,K >= 1024): {len(categories['Large'])}")
    print(f"  Medium (256 <= M < 1024): {len(categories['Medium'])}")
    print(f"  Small (M < 256): {len(categories['Small'])}")
    print(f"  Other (M >= 1024 with N or K < 1024): {len(categories['Other'])}")

    sample_limits = {"Large": 200, "Medium": 100, "Small": 100, "Other": 100}
    samples = {
        label: category.sample(
            min(sample_limits[label], len(category)), random_state=42
        )
        for label, category in categories.items()
    }

    for label, sample in samples.items():
        print(f"\n{'='*60}")
        print(f"Category: {label} ({len(sample)} samples)")
        print(f"{'='*60}")

        batch = evaluate_sample(sample, hw, cal, rc)
        unsupported_total = sum(batch.unsupported_counts.values())
        print(f"  Evaluated: {len(batch.actual_times)}")
        print(f"  Unsupported/rejected: {unsupported_total}")
        for reason, count in batch.unsupported_counts.items():
            print(f"    {reason}: {count}")

        if not batch.actual_times:
            print("  No supported rows were available for numeric comparison.")
            continue

        summary = summarize_predictions(
            batch.des_times, batch.roofline_times, batch.actual_times
        )
        evaluated = summary["evaluated"]
        assert isinstance(evaluated, int)
        runtime_arr = np.asarray(batch.simulator_runtimes)
        print()
        print("  --- Bound audit ---")
        print(
            "  DES schedule-estimate violations: "
            f"{summary['des_violations']}/{evaluated} "
            f"({summary['des_violations'] / evaluated * 100:.1f}%)"
        )
        print(
            "  Classical roofline violations: "
            f"{summary['roofline_violations']}/{evaluated} "
            f"({summary['roofline_violations'] / evaluated * 100:.1f}%)"
        )
        print()
        print("  --- Both-valid paired tightness ---")
        print(f"  Both-valid rows: {summary['both_valid']}/{evaluated}")
        print(f"  DES strictly tighter: {summary['des_strictly_tighter']}")
        print(f"  Classical strictly tighter: {summary['roofline_strictly_tighter']}")
        print(f"  Equal candidate bounds: {summary['equal_bounds']}")
        if summary["both_valid"]:
            print(f"  DES mean gap: {summary['des_mean_gap'] * 100:.3f}%")
            print(f"  DES median gap: {summary['des_median_gap'] * 100:.3f}%")
            print(
                "  Classical mean gap: "
                f"{summary['roofline_mean_gap'] * 100:.3f}%"
            )
            print(
                "  Classical median gap: "
                f"{summary['roofline_median_gap'] * 100:.3f}%"
            )
        print()
        print("  --- DES runtime ---")
        print(f"  Mean: {np.mean(runtime_arr):.9f}s")
        print(f"  Median: {np.median(runtime_arr):.9f}s")
        print(f"  P95: {np.percentile(runtime_arr, 95):.9f}s")
        print(f"  Max: {np.max(runtime_arr):.9f}s")


if __name__ == "__main__":
    main()
