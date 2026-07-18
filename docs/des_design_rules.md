# DES Refined Roofline — Design Rules and Invariants

## Core Positioning

The DES (Discrete Event Simulator) produces a **theoretical lower bound on kernel execution time** — the minimum achievable time under ideal conditions for un-modeled factors.

```
DES Refined Roofline:
  → Tighter than classical roofline (models structural effects: waves, tiles, L2/DRAM split)
  → 10000x faster than cycle-accurate simulation (enables design space exploration)
  → More interpretable than ML predictors AND zero-shot cross-hardware transfer
  → Provides: optimization_gap = (actual - DES_bound) / actual
```

## Fundamental Invariant

```
DES_time ≤ actual_time    (MUST hold for ALL configurations)
```

The DES value is always **more ideal** (shorter/faster) than actual measurement. The gap between DES and actual represents un-modeled overhead (warp scheduling, bank conflicts, instruction replay, etc.).

Any change that risks violating this invariant MUST be rejected.

## Design Rules

### Rule 1: Peak Rate Calibration

Every primitive `duration_per_unit` MUST use the **peak achievable throughput** — the fastest rate the hardware can sustain for that operation in isolation.

- Memory: chip-wide peak bandwidth (GB/s from spec sheet)
- Compute: per-SM peak throughput (ops/cycle × clock frequency)
- Fixed overheads: ZERO (not part of the roofline bound)

Violation of this rule → DES becomes pessimistic → may exceed actual time.

### Rule 2: Structural Effects Only Add Time

Every structural effect modeled in the DES (wave split, partial tiles, L2/DRAM regime) **adds execution time** relative to the naive ideal. This is correct because these are REAL physical effects that slow down actual execution.

Structural effects MUST NOT be over-estimated. When uncertain about the magnitude of a structural effect, use the MORE OPTIMISTIC (smaller) estimate.

### Rule 3: Un-modeled Effects = Assume Ideal

For any hardware behavior NOT explicitly modeled:
- Assume zero overhead
- Assume perfect efficiency
- Assume no contention

This guarantees the DES remains optimistic (lower bound).

Examples: bank conflicts = 0, instruction replay = 0, TLB miss = 0, warp scheduler stalls = 0.

### Rule 4: Pipeline Overlap = Maximum Feasible

When two operations CAN overlap (use different resources), model them as parallel. The scheduler resolves this naturally through independent resource lanes.

- Load and Compute on the same CTA: parallel (double-buffering)
- Different CTAs on different SMs: parallel (per-SM resource lanes)
- DRAM and L2 traffic: parallel (different physical paths)

Never serialize operations that CAN overlap — serialization is pessimistic.

### Rule 5: Resource Model Consistency

| Resource Type | Lanes | Rate Unit | Rationale |
|---|---|---|---|
| DRAM bandwidth | 1 | bytes/us chip-wide | Single shared memory bus |
| L2 bandwidth | num_sms | bytes/us chip-wide | Per-SM L2 slices parallel |
| Tensor core | num_sms | instrs/us per-SM | Each SM has independent TC |
| ALU/SFU | num_sms | ops/us per-SM | Per-SM compute units |
| SM slots | num_sms | - | CTA admission parallelism |

The calibration rate and resource lane count must be CONSISTENT:
- If rate = chip-wide → lanes = 1 (scheduler serializes for total BW)
- If rate = per-SM → lanes = num_sms (scheduler parallelizes)

### Rule 6: Unit Convention (tc_bf16 / fma_fp32 / xu_fp32)

Hardware JSON values are in **ops per cycle per SM** (NOT TFLOPS):
```
per_SM_throughput_ops_per_us = spec_value × sm_freq_mhz
chip_wide_TFLOPS = spec_value × sm_freq_mhz × num_sms / 1e6
```

MMA instruction = 256 FLOPs. MMA count = `ceil(2 * M * N * K / 256)`.

## Metrics

### Primary: Bound Validity
```
violation_rate = count(DES_time > actual_time) / total_configs
TARGET: 0%
```

### Secondary: Tightness (Gap)
```
gap = (actual_time - DES_time) / actual_time
TARGET: < 30% mean for compute-bound GEMMs
```

### Research Metric: Optimization Gap
```
optimization_gap = (actual - DES_bound) / actual
```
This tells the user "your kernel is X% away from the theoretical ideal — here's the breakdown of where the time goes."

### Comparison Metric
```
improvement_vs_roofline = roofline_gap / DES_gap
TARGET: > 1.0 (DES is tighter than classical roofline)
```

## Validation Protocol

Before any commit that modifies `lower_gemm_v2`, `derive_calibration`, or `derive_resource_config`:

1. Run `python -m pytest tests/ -q` — all tests MUST pass
2. Run validation on H100 GEMM dataset — 0% violations for Large and Medium categories
3. Verify DES_gap < roofline_gap (DES is at least as tight as classical roofline)

## Architecture Summary

```
Hardware JSON → HardwareConfig → derive_calibration() → PrimitiveCalibration
                              → derive_resource_config() → ResourceConfig

Operator params → lower_gemm_v2() → Event DAG (structural decomposition)
                                        ↓
                               schedule(events, resources) → SimulationResult
                                        ↓
                               build_report(result) → breakdown metrics
```

Event DAG structure (GEMM v2):
```
KernelLaunch
  ├── GlobalLoad_L2Miss (chip-level: total unique DRAM bytes, 1 DRAM lane)
  ├── Per-CTA (×total_ctas, parallel on SM lanes):
  │     CTAAdmission → MMA → GlobalStore (L2 writeback)
  └── KernelComplete (depends on ALL stores + DRAM event)

Makespan = max(DRAM_total_time, slowest_CTA_compute_chain)
```
