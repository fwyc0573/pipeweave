# DES Event Simulator Documentation Backfill Design

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Replaced the initial documentation shell with the reconciled DES technical design and current-state boundaries. |
| 2026-07-18 | Created the initial documentation architecture. |

## Purpose and Research Position

The event simulator is an independent mechanistic path beside PipeWeave's legacy analytical-plus-ML predictor. It computes latency from explicit event work, dependencies, and resource capacity rather than using an MLP/RF output to close the final operator-latency equation.

Its refined-roofline objective is an optimistic theoretical bound:

```text
DES_time <= actual_time
optimization_gap = (actual_time - DES_time) / actual_time
```

Named hardware constants and primitive calibration are allowed. Final operator/E2E latency labels are evaluation data, not a learned closure target.

## Phase-Naming Reconciliation

Two different phase schemes exist and must not be conflated:

1. `docs/event_simulator_design.md` defines a research roadmap: Phase 0 MVP, Phase 1 frontend adapters, Phase 2 hardware characterization, Phase 3 attention/residency, Phase 4 runtime/communication, and Phase 5 evaluation.
2. `.omc/ultragoal/plan.md` calls its narrower refinement scope "Phase 1 + 2": extended Event IR/infrastructure plus GEMM v2 structural decomposition.

The Ultragoal G001–G005 work does **not** mean the original research-roadmap Phase 1 or Phase 2 exit criteria were completed. Later FlashAttention code partially overlaps the roadmap's Phase 3, but does not complete realistic residency or measurement validation.

## Current Architecture

```text
hardware/*.json
      |
      v
HardwareConfig
  |                         |
  v                         v
derive_calibration()   derive_resource_config()
  |                         |
  +------------+------------+
               |
Operator lowering (GEMM v1/v2, RMSNorm, SiLU-and-Mul, FlashAttention)
               |
               v
Event IR: type + work + duration + dependencies + resource + stream/CTA identity
               |
               v
Deterministic dependency/resource list scheduler
               |
               v
SimulationResult -> SimulationReport
                   (makespan, critical path, kernel durations,
                    resource busy time, serializable timeline)
```

The package remains separate from `aggregator.py`. The legacy path still loads trained MLP checkpoints, uses GEMM dataset nearest-neighbor configuration lookup, predicts `overall_perf`, uses Random Forest communication models, and additively aggregates per-operator durations.

## Event IR and Fail-Fast Contracts

`event_simulator/events.py::Event` is frozen and validates:

- non-empty identifiers and known event type;
- valid optional resource name;
- finite non-negative duration;
- non-negative integer byte/instruction work;
- non-empty, unique, non-self dependencies;
- paired, finite, monotonic scheduled times.

`ResourceConfig` requires positive integer lane counts. `PrimitiveCalibration` requires finite non-negative coefficients and raises on missing primitive calibration. `schedule` raises on duplicate IDs, missing dependencies/resources, and dependency cycles.

The current Event IR declares 22 types. `GlobalLoad_L2Hit`, `MMA_PipelineDrain`, and `FA_Memory` are currently declaration/calibration surfaces only; no lowering emits them.

## Resource and Unit Model

| Resource | Current Lanes | Current Coefficient Basis | Current Use |
|---|---:|---|---|
| `launch` | 1 | zero fixed overhead in derived roofline calibration | Kernel boundaries |
| `sm` | `num_sms` | zero CTA admission cost | CTA admission labels |
| `tensor_core` | `num_sms` | per-SM MMA instructions/us | GEMM and FlashAttention compute |
| `dram_bandwidth` | 1 | chip-wide bytes/us | One aggregate cold-miss event |
| `l2_bandwidth` | `num_sms` | currently derived from chip-wide bytes/us | GEMM output stores; see I-011 |
| `alu`, `sfu`, `barrier` | `num_sms` | per-SM rate or zero barrier cost | Phase 0 elementwise/RMSNorm paths |

Hardware JSON `tcBf16`, `FmaFp32`, and `xuFp32` values are ops/cycle/SM:

```text
per_SM_ops_per_us = spec_value * sm_freq_mhz
chip_wide_TFLOPS = spec_value * sm_freq_mhz * num_sms / 1e6
```

For H100 this gives `4096 * 1830 * 132 / 1e6 = 989.42976` BF16 TFLOPS.

## Scheduling Semantics

The scheduler processes the provided event order deterministically. An event becomes eligible after all dependencies complete. It starts on the earliest available lane of its resource, and the selected lane predecessor is added to the scheduled dependency list so critical-path reconstruction includes resource serialization.

Stream ordering is opt-in per event. Lowering-internal events are generally `stream_ordered=False`, permitting resource overlap. `KernelLaunch` and `KernelComplete` remain stream ordered, serializing kernel boundaries on the same stream.

Current ready selection rescans the full ordered event sequence for every scheduled event. This preserves deterministic order but approaches O(V²) and prevents practical full-dataset validation for large CTA graphs (I-008).

## Operator Lowerings

### Phase 0 Lowerings

- `lower_gemm`: per-CTA admission -> load -> MMA -> store chains.
- `lower_rmsnorm`: per-row load -> reduction -> barrier -> FMA normalization -> store.
- `lower_silu_and_mul`: load -> SFU -> FMA -> store.

These paths use caller-provided calibration and remain covered by seven integration tests.

### GEMM v2 Current DAG

```text
KernelLaunch
  +--> GlobalLoad_L2Miss (one chip-level effective DRAM event)
  +--> CTAAdmission_{FullWave|TailWave} [per CTA]
          |
          v
      MMA_{FullTile|PartialTile} [per CTA, tensor_core lanes]
          |
          v
      GlobalStore [per CTA, l2_bandwidth lanes]

KernelComplete depends on every store and the aggregate DRAM event.
Makespan = max(aggregate DRAM path, slowest CTA compute/store path)
```

Current effective DRAM bytes are:

```text
A_bytes = M * K * element_bytes
B_bytes = N * K * element_bytes
B_tile_column_bytes = tile_N * K * element_bytes
B_reuse_factor = min(M_tiles, max(1, L2_bytes // B_tile_column_bytes))
effective_DRAM_bytes = A_bytes + floor(B_bytes / B_reuse_factor)
```

This is an analytical effective-traffic model, not a literal L2 hit/miss event split. `tile_k` is accepted/documented but unused (I-004). Partial tiles use actual clamped M/N dimensions with the same peak MMA coefficient; they are classified but no padded-work inefficiency is added (I-012).

### Experimental FlashAttention Lowering

`lower_flash_attention` reuses existing FA2/FA3 scheduling helpers to obtain per-SM task iterations. It emits:

- one aggregate unique-byte DRAM event for Q + K + V + O, with GQA-aware head counts;
- per-SM sequential `FA_Compute` -> zero-cost `FA_TaskSync` chains;
- interleaved event insertion so greedy lane selection parallelizes SM chains;
- kernel completion dependent on all SM chains and DRAM.

It intentionally omits XU/softmax cost from the current roofline compute path and does not implement realistic CTA residency, counter validation, or workload/aggregator integration. Ten integration tests cover event structure, scheduling, causal work reduction, and selected invalid inputs; accuracy remains unaccepted (I-010).

## Reconstructed Delivery Status

| Work Item | Implemented | Fresh Tests | Accepted | Evidence / Limitation |
|---|---|---|---|---|
| Phase 0 MVP | Yes | 21/21 related scheduler/operator tests pass | Yes for original MVP contract | `418ba05`, original plan, current tests |
| G001 Event IR extension | Yes | Full suite passes | Yes for constructibility/backward compatibility | 22 current event types; 74/74 suite |
| G002 hardware adapter | Yes | 8/8 adapter tests pass | Yes for current tested contract | H100 parsing/calibration/resource tests |
| G003 structural utilities | Yes | 24/24 structural tests pass | Yes as utilities | Some utilities are not consumed by GEMM v2 |
| G004 GEMM v2 | Yes | 11/11 GEMM v2 tests pass | **Partially accepted** | I-004, I-009, I-011, I-012 prevent claiming the exact original structural contract |
| G005 validation | Yes, harness exists | Bounded audit ran | **No — IMPLEMENTED, NOT ACCEPTED** | Large mean gap `16.922601% > 15%`; I-004/I-006/I-007/I-008 |
| FlashAttention task-level lowering | Yes | 10/10 FA tests pass | Experimental only | Only 2 benchmark rows and no prediction-vs-measurement validator |

## Artifact Responsibilities

| Artifact | Responsibility |
|---|---|
| `requirements.md` | Raw intent and Q&A only. |
| `plan.md` | Scope, ordered execution, acceptance criteria, and verification. |
| `notes.md` | Operational constraints and environment reminders. |
| `progress.md` | Auditable session actions and results. |
| `issues.md` | Contradictions, failures, root causes, and resolutions. |
| `review.md` | Independent and checkpoint review evidence. |
| `summary.md` | English completion inventory, hashes, metrics, and open items. |
| `lessons.md` | Only double-checked reusable technical knowledge. |
| `harness.md` | Gates that prevent scope, evidence, and validation drift. |
| `design.md` | Concise synthesis of the task documentation architecture. |
| `future.md` | Work explicitly excluded from this session. |

## Reconciliation Rule

When sources disagree, record both the historical claim and the current implementation fact, identify the root cause or evidence gap in `issues.md`, and avoid rewriting history as though the sources had always agreed.

## Documentation Source Hierarchy

1. `requirements.md` preserves raw user intent.
2. Existing tracked docs preserve historical intent and declared invariants.
3. Ignored `.omc/ultragoal` files preserve prior execution claims but are not durable authority.
4. Current source and fresh tests establish implemented/tested state.
5. Acceptance requires the original numeric/behavioral exit criteria, not merely an implementation or passing structural tests.
