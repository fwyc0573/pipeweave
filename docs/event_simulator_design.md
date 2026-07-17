## Modification History

| Date | Summary of Changes |
|------|--------------------|
| 2026-07-17 | Added codebase-grounded design and staged research plan for the event-level simulator |

# Mechanistic Event-Level Simulator Design

## 1. Current PipeWeave workflow

PipeWeave is a hybrid operator predictor, not a discrete-event simulator. Its
current path can be summarized as follows:

```text
Model config + request trace + TP/PP settings
                    |
                    v
          workload_generator.py
                    |
                    v
       Per-layer operator workload JSON
                    |
                    v
              aggregator.py
          /            |             \
         v             v              v
 Analytical feature   MLP efficiency  Collective RF
 calculators          prediction      prediction
         \             |              /
          \            v             /
           +--- operator duration ---+
                         |
                         v
             Additive E2E aggregation
                         |
                         v
         compare_pred_real.py validation
```

The analytical calculators expose hardware-related features, but the final
compute duration still depends on a learned `overall_perf` target. That target
is derived from measured duration during training. Collective communication is
predicted by a per-hardware Random Forest. GEMM inference also consults profiled
GEMM records to select a nearby tile/CTA/split-K configuration.

Therefore, the interpretation that PipeWeave ultimately relies on substantial
measurement products is correct. The white-box components constrain and
structure the feature space; they do not close the final latency equation by
themselves.

## 2. Research position

The proposed direction is feasible if "pure white-box" means that predicted
latency is produced by an explicit causal execution model rather than an
end-to-end learned regressor. It is not realistic to require zero measurement:
undocumented hardware policies, compiler instruction selection, cache effects,
clock behavior, and runtime overhead must be characterized somehow.

The recommended definition is:

> A mechanistic, event-level simulator whose latency is computed only by
> explicit event dependencies and resource constraints. Measurements may
> calibrate named primitive costs, but may not directly fit the final operator
> or end-to-end latency target.

This boundary preserves interpretability and allows a measured component to be
replaced later by a deeper analytical model without changing the scheduler.

## 3. Implemented MVP

```text
Operator shape + tiling + explicit primitive calibration
                         |
                         v
                 Operator lowerings
       GEMM       RMSNorm       SiLU-and-Mul
          \          |              /
           +---------+-------------+
                         |
                         v
        Event IR: dependencies, work, resource
                         |
                         v
       Deterministic resource-aware list scheduler
                         |
                         v
     Timeline + makespan + kernel bounds + busy time
                  + critical path
```

The new `event_simulator/` package is independent from the legacy prediction
path. It does not import PyTorch, scikit-learn, model checkpoints, RF artifacts,
or profiling CSV files.

### Event IR

Each `Event` contains:

- stable event, kernel, stream, and optional CTA identifiers;
- event type and modeled resource;
- explicit duration and work metadata (`bytes`, `instruction_count`);
- causal dependencies;
- scheduled start/end times.

Supported event types are `KernelLaunch`, `CTAAdmission`, `GlobalLoad`,
`GlobalStore`, `SharedLoad`, `SharedStore`, `MMA`, `FMA`, `SFU`, `Barrier`,
`Reduction`, and `KernelComplete`.

### Scheduling model

The scheduler performs deterministic dependency-aware list scheduling. Every
resource has an explicit positive lane capacity. An event starts only when all
dependencies have completed and one lane of its resource is free. Resource-lane
predecessors are recorded as dependencies, which makes the reported critical
path auditable.

Kernel-internal work is marked as not stream-ordered because CUDA stream order
applies to kernel boundaries, not to a total order over every CTA instruction.
`KernelLaunch` and `KernelComplete` retain stream ordering, so consecutive
kernels on the same stream remain serialized.

### Primitive calibration

`PrimitiveCalibration` requires a duration coefficient for every primitive used
by a lowering. Duration is calculated as:

```text
event duration = explicit work quantity × primitive duration per unit
```

Examples of work quantities are bytes for global memory events, tensor
instructions for MMA, and element counts for FMA/SFU/reduction. There is no
implicit default and no missing-value fallback. Unsupported or uncalibrated work
fails immediately.

The coefficient time unit is caller-defined but must be consistent; microseconds
are recommended. Current coefficients are intentionally simple first-order
terms. They are a stable interface for replacing constant costs with piecewise
analytical curves or measurement tables later.

## 4. How measurements should be used

The simulator should separate measurements into four categories:

| Category | Examples | Allowed use |
|----------|----------|-------------|
| Hardware constants | peak issue rate, memory bandwidth, SM count | Direct resource parameters |
| Primitive characterization | launch overhead, barrier cost, L2/DRAM bandwidth curves | Explicit primitive calibration |
| Mechanism validation | CTA occupancy, cache hit rate, instruction mix | Validate or revise the event model |
| Final latency labels | complete GEMM/attention/E2E duration | Held-out evaluation only, never training the final predictor |

Hardware-event collection can use CUPTI or Nsight Compute counters to identify
instruction counts, achieved bandwidth, occupancy, cache traffic, and stall
composition. One-factor-at-a-time microbenchmarks should isolate each primitive.
Calibration data must be versioned by GPU architecture, clock/power policy,
CUDA/driver version, dtype, and relevant size regime.

If a mechanism cannot yet be expressed, represent it as a named measured event
with an explicit domain and provenance. Do not hide it inside an aggregate
operator correction factor. This keeps the unknown visible and prevents a
black-box closure from reappearing under a different name.

## 5. Mapping existing PipeWeave assets to the new model

| Existing asset | Reuse path | Required correction or extension |
|----------------|------------|----------------------------------|
| `hardware/*.json` | Seed resource counts and peak rates | Add cache, issue-port, residency, clock, and topology fields |
| GEMM calculators | Derive operation count and candidate tiling | Replace nearest-neighbor tile selection with an explicit kernel policy or measured configuration adapter |
| `fa2_calculator.py` / `fa3_calculator.py` | Reuse CTA count and wave/scheduling concepts | Lower attention phases into load, MMA, softmax, barrier, and store events; validate CTA collection logic |
| RMSNorm / SiLU calculators | Reuse shapes and pipeline work estimates | Map their pipeline counts into explicit events and size-dependent primitive costs |
| Workload JSON | Operator sequence frontend | Add request lifecycle, stream, launch, and decode-token semantics |
| Profiling datasets | Held-out validation and primitive extraction | Do not use final operator duration as a learned closure target |
| `aggregator.py` | Comparison baseline | Keep separate until event simulation covers the full operator/runtime surface |

## 6. Feasibility and research risks

### Feasible near-term mechanisms

- Kernel launch and same-stream ordering.
- CTA count, tiling, waves, and resource capacity.
- Global/shared-memory traffic at tile granularity.
- MMA/FMA/SFU/reduction/barrier work.
- Kernel critical path and resource busy time.
- First-order cache/bandwidth regime selection from hardware counters.

### Difficult mechanisms

- Warp scheduler arbitration and instruction-level dependency stalls.
- Dynamic L1/L2 reuse, memory partition camping, and TLB effects.
- Tensor Core and load/store pipeline overlap inside a CTA.
- Compiler-dependent fusion and instruction selection.
- FlashAttention persistent scheduling and work stealing.
- NCCL algorithms, link contention, topology, and compute/communication overlap.
- CUDA Graph launch behavior, runtime CPU overhead, PP bubbles, and online request scheduling.

The largest scientific risk is not scheduler implementation; it is model
identifiability. Different combinations of bandwidth, issue rate, occupancy,
and synchronization costs can produce the same final latency. Calibration must
therefore use independent counters and microbenchmarks rather than optimizing
all parameters against one total duration.

## 7. Staged plan

### Phase 0: Correctness foundation (implemented)

- Validated Event IR and fail-fast input checks.
- Deterministic resource/dependency scheduler.
- GEMM, RMSNorm, and SiLU-and-Mul lowerings.
- Timeline, resource busy time, kernel duration, and critical path report.
- Unit and integration tests.

### Phase 1: PipeWeave frontend adapters

- Convert hardware JSON into resource capacities and analytical coefficients.
- Convert workload operators into typed lowering requests.
- Replace manually supplied GEMM tiling with a policy interface.
- Add compatibility tests against representative workload JSON files.

Exit criterion: supported operators from one real workload can be simulated
without using MLP/RF inference.

### Phase 2: Hardware characterization

- Create CUDA microbenchmarks for launch, memory hierarchy, MMA, FMA, SFU,
  reduction, and barrier primitives.
- Capture CUPTI/Nsight counters and environment metadata.
- Fit only interpretable piecewise primitive curves.
- Validate parameters on disjoint microbenchmark shapes.

Exit criterion: primitive parameters reproduce held-out primitive measurements
with confidence intervals and without operator-duration fitting.

### Phase 3: Attention and realistic CTA residency

- Audit FA2/FA3 calculator CTA scheduling against actual kernel traces.
- Add shared-memory capacity, register occupancy, and CTA lifetime tokens.
- Add phase overlap within a CTA and wave admission across SMs.
- Lower QK, softmax, PV, epilogue, and synchronization events.

Exit criterion: attention latency and mechanism counters generalize across
sequence lengths and head configurations not used for calibration.

### Phase 4: Runtime and communication

- Add multiple CUDA streams and explicit event synchronization.
- Add copy engines and compute/communication overlap.
- Add NCCL algorithm/topology events and link resources.
- Add request lifecycle, decode iteration, PP scheduling, and CPU launch events.

Exit criterion: simulated E2E critical paths explain overlap and PP bubbles,
not merely sum operator durations.

### Phase 5: Scientific evaluation

Compare PipeWeave, analytical-only baselines, and the event simulator on:

- per-operator predicted vs. actual latency and MAPE;
- end-to-end predicted vs. actual latency and MAPE;
- out-of-distribution hardware, shapes, and model architectures;
- calibration sample count and transferability;
- error decomposition by event/resource;
- CTA count, occupancy, bytes, instruction counts, and critical-path agreement.

All final operator and E2E measurements must remain held out from calibration.

## 8. Current limitations

- The MVP is a static deterministic list scheduler, not a cycle-level simulator.
- Primitive cost is currently linear in one explicit work quantity.
- CTA admission does not yet hold an SM residency token for the CTA lifetime.
- Cache hierarchy, shared-memory bank conflicts, register pressure, clock
  variation, and warp scheduling are not modeled.
- Attention, MoE, communication, multi-device, PP, and runtime request scheduling
  are not implemented.
- The event simulator is not yet wired into `aggregator.py` or workload JSON.

These limitations are explicit research tasks, not silent corrections. The
legacy PipeWeave predictor remains the production comparison path while the new
mechanistic path matures independently.
