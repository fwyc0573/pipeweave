# DES Refined Roofline — Design Rules and Invariants

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Reclassified DES claims by evidence status and corrected scheduler, metric, traffic, and resource contracts. |

## Core Positioning

DES is a deterministic, mechanistic, event-level analytical prototype. It
exposes explicit work, dependencies, resources, timelines, and a selected
critical path without using an MLP/RF latency closure. The current greedy list
scheduler returns one feasible schedule for the modeled Event DAG; its makespan
is **not a certified lower bound** on actual hardware latency or on the optimum
schedule of that DAG.

## Scientific Status

| Claim or capability | Status | Contract |
|---|---|---|
| Fail-fast Event IR, explicit resource capacities, deterministic timeline | **Established** | Covered by unit/integration tests. |
| Mechanistic interpretability without an ML latency closure | **Established structurally** | Events and resource accounting are auditable, but attribution agreement with hardware counters remains **Experimental**. |
| GEMM v2 and FA2/FA3 structural timing | **Experimental** | Useful for mechanism studies only; unsupported launch policies are rejected. |
| Globally tighter than classical roofline | **Unproven** | Compare only on identical measurement boundaries and rows where both candidate bounds are valid. Existing samples are category-dependent. |
| `10000x` faster than cycle-accurate simulation | **Unproven** | No named, matched cycle-accurate comparator is available; large Event DAGs also show a scalability problem. |
| Empirical cross-hardware zero-shot accuracy | **Unproven** | Specification-driven execution is not equivalent to held-out transfer evidence. |
| Universal theoretical lower-bound evaluator | **Blocked** | Requires a proven safe evaluator plus residency, policy, and measurement-contract work. |

## Fundamental Invariant

The strict invariant applies only after a candidate value has independently
passed the bound-validity gate:

```text
0 < des_bound <= actual_time
```

`SimulationResult.makespan` is an explanatory schedule estimate and must not be
renamed, cast, or passed implicitly as `des_bound`. A row with
`makespan > actual_time` is a bound violation and remains evidence of an
unmatched model or measurement contract; it must not be clamped, scaled, or
silently omitted.

## Design Rules

### Rule 1: Peak Rate Calibration

Every primitive `duration_per_unit` MUST use the **peak achievable throughput** — the fastest rate the hardware can sustain for that operation in isolation.

- Memory: chip-wide peak bandwidth (GB/s from spec sheet)
- Compute: per-SM peak throughput (ops/cycle × clock frequency)
- Fixed overheads: ZERO (not part of the roofline bound)

Non-positive, non-finite, or dimensionally inconsistent required rates are
invalid configuration and must fail fast. Peak-rate primitives are idealized
inputs; they do not by themselves prove that a composed schedule is a bound.

### Rule 2: Structural Effects Require Physical Conservation

Every structural term must have a named physical meaning, consistent units,
and a testable measurement boundary. A label is not a timing mechanism:

- current full-wave/tail-wave admission events have zero duration and do not
  hold an SM-residency token;
- current partial-tile MMA events count useful work and do not model padded or
  masked execution cost;
- `tile_k` is carried through validation but does not yet change timing;
- cache residency and split-K execution are not inferred from tile labels.

Mandatory work must never be reduced below conservation limits. Under the
current cold-HBM GEMM contract, unique A and B bytes each enter from HBM once,
while output C terminates at the L2 boundary.

### Rule 3: Un-modeled Effects = Assume Ideal

For any hardware behavior NOT explicitly modeled:
- Assume zero overhead
- Assume perfect efficiency
- Assume no contention

This keeps individual primitive assumptions explicit and optimistic. It does
not certify the greedy composition as a lower bound.

Examples: bank conflicts = 0, instruction replay = 0, TLB miss = 0, warp scheduler stalls = 0.

### Rule 4: Overlap Requires an Explicit Dependency and Resource Contract

Independent resources may overlap only when the Event DAG intentionally omits a
dependency and the measurement boundary permits the overlap. Required ordering
must be represented by dependencies. The current GEMM v2 model overlaps one
aggregate cold-input HBM event with per-CTA compute/store chains; it does not
claim to model an actual double-buffered K-stage pipeline.

### Rule 5: Resource Model Consistency

| Resource Type | Lanes | Rate Unit | Rationale |
|---|---|---|---|
| DRAM bandwidth | 1 | bytes/us chip-wide | Single shared memory bus |
| L2 bandwidth | 1 | bytes/us chip-wide | One aggregate chip-wide pool |
| Tensor core | num_sms | instrs/us per-SM | Each SM has independent TC |
| ALU/SFU | num_sms | ops/us per-SM | Per-SM compute units |
| SM slots | num_sms | - | CTA admission parallelism |

The calibration rate and resource lane count must be CONSISTENT:
- If rate = chip-wide → lanes = 1 (scheduler serializes for total BW)
- If rate = per-SM → lanes = num_sms (scheduler parallelizes)

`GlobalStore` uses the chip-wide L2 coefficient because the current GEMM output
boundary ends at L2. It must not use a DRAM coefficient while consuming an L2
resource lane.

### Rule 6: Unit Convention (tc_bf16 / fma_fp32 / xu_fp32)

Hardware JSON values are in **ops per cycle per SM** (NOT TFLOPS):
```
per_SM_throughput_ops_per_us = spec_value × sm_freq_mhz
chip_wide_TFLOPS = spec_value × sm_freq_mhz × num_sms / 1e6
```

MMA instruction = 256 FLOPs. MMA count = `ceil(2 * M * N * K / 256)`.

## Metrics

### Primary: Candidate-Bound Validity
```
violation_rate = count(candidate_time > actual_time) / evaluated_supported_rows
```

Unsupported rows, including split-K and rows whose dataset `cta_count` differs
from the reconstructed tile grid, are reported by reason and excluded from the
evaluated denominator. Unexpected exceptions propagate.

### Accepted-Bound Metrics

Only after `0 < des_bound <= actual_time` has been checked:

```
optimization_gap = (actual_time - des_bound) / actual_time
hardware_efficiency = des_bound / actual_time
optimization_gap + hardware_efficiency = 1
```

The public `compare_des_bound()` API enforces finite positive values and rejects
bound violations. It does not certify provenance and does not accept a
`SimulationResult` implicitly. The optimization gap is the distance to the
accepted bound; the current model cannot yet attribute that entire distance to
specific real-kernel overheads.

### Classical-Roofline Comparison

Use the same boundary for both candidates:

```
compute_time = 2*M*N*K / chip_wide_bf16_flops_per_us
hbm_input_time = bytes(A+B) / chip_wide_hbm_bytes_per_us
l2_output_time = bytes(C) / chip_wide_l2_bytes_per_us
classical_time = max(compute_time, hbm_input_time, l2_output_time)
```

Compare mean/median gaps and strict per-row tightness only on rows where both
candidate values are positive and do not exceed the same actual measurement.
Do not divide by a clamped DES gap or convert violations into improvement.

## Validation Protocol

Before any commit that modifies `lower_gemm_v2`, `derive_calibration`, or `derive_resource_config`:

1. Run `PYTHONPATH="$PWD" python -m pytest tests -q` and record the exact result.
2. Run the matched-boundary validator and report evaluated rows, every
   unsupported reason, DES/classical violations, both-valid pair count, actual
   and predicted time scales, gap statistics, and DES wall-clock runtime.
3. Treat category/sample tightness as scoped evidence only. Do not generalize a
   Large/Medium result to Small shapes, all H100 rows, or other hardware.
4. A `10000x` speed claim requires the same workload, a named cycle-accurate
   reference, and measured runtime for both tools. A zero-shot claim requires a
   held-out multi-hardware evaluation.

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

The report explains the selected greedy schedule. It does not transform the
schedule into a certified bound or prove that its critical path is the hardware
kernel's necessary critical path.

Event DAG structure (GEMM v2):
```
KernelLaunch
  ├── GlobalLoad_L2Miss (cold unique A+B bytes, 1 chip-wide HBM lane)
  ├── Per-CTA (×total_ctas, parallel on SM lanes):
  │     CTAAdmission label → useful-work MMA → GlobalStore (1 chip-wide L2 lane)
  └── KernelComplete (depends on ALL stores + DRAM event)

Makespan = max(cold_HBM_path, selected_compute_to_L2_store_schedule)
```

Current launch-policy boundary:

- `total_ctas = ceil(M/tile_M) * ceil(N/tile_N)`;
- dataset rows with `is_split_k != 0` are unsupported;
- dataset rows whose `cta_count` differs from `total_ctas` are unsupported;
- persistent CTA behavior, replicated split-K work, and split-K reduction are
  blocked architecture work rather than inferred or silently approximated.
