"""Validate DES lower_gemm_v2 predictions against measured GEMM durations.

Reports:
- Bound validity: DES_time <= actual_time (target: 100%)
- Tightness: (actual - DES) / actual (target: < 15% for large GEMMs)
- Comparison with classical roofline
"""

import pandas as pd
import numpy as np
from pathlib import Path

from event_simulator import (
    lower_gemm_v2,
    load_hardware_config,
    derive_calibration,
    derive_resource_config,
    schedule,
    build_report,
)
from event_simulator.structural import ceil_div


def classical_roofline(row, hw_config):
    """Simple roofline: time = max(compute_bound, memory_bound)."""
    m, n, k = int(row["M"]), int(row["N"]), int(row["K"])
    element_bytes = 2  # bf16

    flops = 2.0 * m * n * k
    memory_bytes = (m * k + n * k + m * n) * element_bytes

    compute_time_us = flops / (hw_config.tc_bf16 * 1e12) * 1e6
    memory_time_us = memory_bytes / hw_config.mem_bandwidth_bytes_per_us

    return max(compute_time_us, memory_time_us)


def des_predict(row, hw_config, calibration, resource_config):
    """Run DES lower_gemm_v2 and return makespan."""
    m = int(row["M"])
    n = int(row["N"])
    k = int(row["K"])
    tile_m = int(row["tile_M"])
    tile_n = int(row["tile_N"])

    if tile_m <= 0 or tile_n <= 0 or m <= 0 or n <= 0 or k <= 0:
        return None

    try:
        events = lower_gemm_v2(
            "gemm-val",
            m=m, n=n, k=k,
            tile_m=tile_m, tile_n=tile_n,
            calibration=calibration,
            hardware=hw_config,
            element_bytes=2,
        )
        result = schedule(events, resource_config)
        return result.makespan
    except Exception as e:
        return None


def main():
    hw_path = Path("hardware/H100.json")
    hw = load_hardware_config(hw_path)
    cal = derive_calibration(hw)
    rc = derive_resource_config(hw, operator_type="gemm_v2")

    df = pd.read_csv("dataset/gemm_test.csv")
    df_h100 = df[df["hardware"].str.contains("H100")].copy()
    print(f"H100 GEMM test samples: {len(df_h100)}")

    # Filter to representative subset (sample across sizes)
    # Use large GEMMs first for best tightness demonstration
    df_large = df_h100[(df_h100["M"] >= 1024) & (df_h100["N"] >= 1024) & (df_h100["K"] >= 1024)]
    df_medium = df_h100[(df_h100["M"] >= 256) & (df_h100["M"] < 1024)]
    df_small = df_h100[df_h100["M"] < 256]

    print(f"  Large (M,N,K >= 1024): {len(df_large)}")
    print(f"  Medium (256 <= M < 1024): {len(df_medium)}")
    print(f"  Small (M < 256): {len(df_small)}")

    # Sample up to 200 from each category
    sample_large = df_large.sample(min(200, len(df_large)), random_state=42)
    sample_medium = df_medium.sample(min(100, len(df_medium)), random_state=42)
    sample_small = df_small.sample(min(100, len(df_small)), random_state=42)

    for label, sample in [("Large", sample_large), ("Medium", sample_medium), ("Small", sample_small)]:
        print(f"\n{'='*60}")
        print(f"Category: {label} ({len(sample)} samples)")
        print(f"{'='*60}")

        des_times = []
        roofline_times = []
        actual_times = []
        skipped = 0

        for _, row in sample.iterrows():
            actual = row["avg_duration"]
            if actual <= 0 or pd.isna(actual):
                skipped += 1
                continue

            des_time = des_predict(row, hw, cal, rc)
            if des_time is None:
                skipped += 1
                continue

            roof_time = classical_roofline(row, hw)

            des_times.append(des_time)
            roofline_times.append(roof_time)
            actual_times.append(actual)

        if not des_times:
            print("  No valid predictions. Skipping.")
            continue

        des_arr = np.array(des_times)
        roof_arr = np.array(roofline_times)
        actual_arr = np.array(actual_times)

        # Bound validity: DES_time <= actual_time
        des_violations = np.sum(des_arr > actual_arr)
        des_violation_rate = des_violations / len(des_arr) * 100

        # Tightness gap: (actual - DES) / actual
        des_gap = (actual_arr - des_arr) / actual_arr
        roof_gap = (actual_arr - roof_arr) / actual_arr

        print(f"  Evaluated: {len(des_arr)}, Skipped: {skipped}")
        print()
        print(f"  --- DES Refined Roofline ---")
        print(f"  Bound violations: {des_violations}/{len(des_arr)} ({des_violation_rate:.1f}%)")
        print(f"  Tightness gap (actual-DES)/actual:")
        print(f"    Mean: {np.mean(des_gap)*100:.1f}%")
        print(f"    Median: {np.median(des_gap)*100:.1f}%")
        print(f"    P5: {np.percentile(des_gap, 5)*100:.1f}%")
        print(f"    P95: {np.percentile(des_gap, 95)*100:.1f}%")
        print()
        print(f"  --- Classical Roofline ---")
        roof_violations = np.sum(roof_arr > actual_arr)
        print(f"  Bound violations: {roof_violations}/{len(roof_arr)} ({roof_violations/len(roof_arr)*100:.1f}%)")
        print(f"  Tightness gap (actual-Roof)/actual:")
        print(f"    Mean: {np.mean(roof_gap)*100:.1f}%")
        print(f"    Median: {np.median(roof_gap)*100:.1f}%")
        print()
        print(f"  --- Improvement ---")
        if np.mean(roof_gap) > 0:
            improvement = np.mean(roof_gap) / max(np.mean(des_gap), 0.001)
            print(f"  DES is {improvement:.1f}x tighter than classical roofline (mean gap)")


if __name__ == "__main__":
    main()
