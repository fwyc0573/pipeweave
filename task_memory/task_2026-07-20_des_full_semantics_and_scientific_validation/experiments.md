# DES Full Semantics and Scientific Validation Experiments

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Aligned E1 with the reviewed Wave-3 scheduler/report test ownership, unique benchmark path, and separated admission counters. |
| 2026-07-20 | Froze the approved GPGPU-Sim cycle-level benchmark, Hopper held-out folds, primitive-calibration separation, and modeled-theorem quantifiers. |
| 2026-07-20 | Corrected E3 to treat `tensor_all_ops` as legacy analytical feature evidence and require separately proven measured-counter provenance. |
| 2026-07-20 | Added the source-data constraints that E3 must test explicitly for split-K metadata and provenance-separated partial-tile work accounting. |
| 2026-07-20 | Defined the phase-2 experiment matrix, planned test locations, required raw evidence, metrics, and claim-specific acceptance boundaries. |

## Status and Use

This is a Phase-1 experiment design, not executed evidence. Planned file paths and commands become authoritative only after the corresponding RED tests, implementation, environment check, and module review pass. Missing external comparator or GPU evidence is reported as blocked; it is never replaced by a proxy.

## E0 — Exact Oracle and Scalable Bound Validation

### Intended coverage

- Resource-constrained exact modeled optimum for the accepted finite domain.
- Order-invariant dependency-DAG lower bound.
- Cross-check between exact optimum, safe bound, and feasible scheduler.

### Planned test locations

```text
tests/unit/test_event_graph.py
tests/unit/test_resource_semantics.py
tests/unit/test_exact_oracle.py
tests/unit/exact_time_grid_reference.py
tests/unit/test_safe_bound.py
tests/unit/test_safe_bound_permutation_properties.py
tests/unit/test_safe_bound_conservation_properties.py
tests/integration/test_bound_oracle_scheduler.py
tests/performance/benchmark_exact_oracle.py
```

These paths are frozen by the final GSD ownership review; duplicate files for the same contract are prohibited.

### Required cases

1. Empty input, duplicate IDs, unknown dependencies, self-dependency, and cycles.
2. Zero-duration nodes and all-zero non-empty graphs.
3. Independent resource-free Events, preserving the existing `max(duration)` result.
4. Explicit dependency chains, forks, joins, and disconnected components.
5. Capacity `1`, capacity greater than `1`, saturated and under-saturated resource pools.
6. Simultaneous multi-resource demand at exact capacity, below capacity, and above capacity.
7. Fixed affinity with feasible and impossible placements.
8. Non-semantic input permutations.
9. Search/solver completion, search exhaustion, timeout, nonzero optimality gap, and unsupported semantics.

### Mandatory numeric evidence

| Metric | Required values |
|---|---|
| Exact comparison | expected optimum, returned optimum, absolute delta |
| Safety | safe bound, exact optimum, `exact - bound`, `(exact-bound)/exact` when exact is positive |
| Feasible schedule | exact optimum, scheduled makespan, optimality gap |
| Permutation | permutations checked, mismatches, minimum/maximum returned value |
| Search | event count, edge count, resource count, search nodes/MIP nodes, runtime, completion status, optimality gap |
| Rejections | total by explicit rejection reason |

### Acceptance

For every accepted case under one identical modeled contract:

```text
safe_bound <= exact_optimum <= feasible_schedule_makespan
```

- Exact values match hand-derived cases and an independently enumerated tiny-case corpus with zero delta.
- Bound and exact result are invariant under all tested non-semantic permutations.
- Timeout/search exhaustion/nonzero optimality gap returns no exact result.
- Every bound term has a proof linked from `design.md`.

## E1 — Scheduler Feasibility, Determinism, and Scaling

### Planned test locations

```text
tests/unit/test_event_scheduler.py
tests/unit/test_report.py
tests/integration/test_bound_oracle_scheduler.py
tests/performance/benchmark_event_scheduler.py
```

### Required comparison

- Historical scheduler behavior is retained as a named baseline, including the `21.0` versus `11.0` caller-order counterexample.
- If the accepted policy intentionally changes makespan, compatibility is judged by declared policy and feasibility, not by forcing the old heuristic result.
- Runtime is measured at graph sizes comparable to the historical `387`, `771`, `1,539`, `3,075`, `6,147`, and `58,467` Event points when practical.

### Mandatory numeric evidence

```text
event_count
edge_count
resource_count
ready_queue_operations
blocked_ready_rechecks
placement_checks
lifetime_checks
old_runtime_seconds
new_runtime_seconds
speedup
makespan
exact_optimum for small cases
optimality_gap
feasibility_violation_count
determinism_mismatch_count
```

No performance target is accepted before the policy and benchmark environment are frozen. Complexity labels must agree with measured scaling and inspected implementation.

## E2 — Cache Hierarchy, Warm L2, and Initial Residency

### Required explicit states

```text
ColdHBM
WarmL2
ExplicitResidency
```

Every state records:

- input request bytes;
- L2-served bytes;
- HBM-miss bytes;
- resident tensors/ranges and bytes;
- cache capacity and eviction policy;
- preload/flush procedure;
- kernel-sequence context;
- output visibility boundary.

### Planned test and evidence locations

```text
tests/unit/test_cache_state.py
tests/integration/test_cache_aware_lowering.py
tests/performance/benchmark_cache_states.py
tests/performance/data/cache_states/environment.json
tests/performance/data/cache_states/raw_latency.csv
tests/performance/data/cache_states/raw_counters.csv
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/results_cache_states.md
```

### Mandatory numeric evidence

| Metric | Compared values |
|---|---|
| Traffic | predicted and measured L2 request bytes, HBM bytes, absolute/relative error |
| State effect | cold latency, warm latency, explicit-residency latency, absolute/relative deltas |
| Capacity | initial resident bytes, admitted bytes, evicted bytes, final resident bytes |
| Integrity | traffic-conservation failures, capacity violations, unexpected evictions |

GPU execution requires the authoritative GPU handbook and controlled environment provenance. No violation may be attributed to cache without counter/state evidence.

## E3 — CTA Lifetime, Multi-Resource Demand, Affinity, Persistent CTA, Split-K, and Partial Tiles

### Planned test locations

```text
tests/unit/test_execution_constraints.py
tests/unit/test_persistent_cta.py
tests/unit/test_split_k_semantics.py
tests/unit/test_partial_tile_semantics.py
tests/integration/test_gemm_execution_semantics.py
tests/validation/validate_gemm_launch_policy.py
```

### Required invariant families

1. CTA resource reservations begin/end at the declared lifecycle boundary and remain held across required phases.
2. Simultaneous resource demands are admitted atomically; no partial acquisition is hidden.
3. SM/lane affinity placements are explicit, deterministic where policy requires, and capacity-feasible.
4. Persistent CTA worker count, tile assignment, completion, and total-work conservation match explicit metadata.
5. Split-K records replicated work/traffic, partial outputs, reduction work/traffic/resource, barrier/dependency, and final visibility.
6. Partial tiles expose logical useful work and physical issued/padded work separately, including zero remainder and one-element tail boundaries.

### Mandatory numeric evidence

```text
declared_cta_count / generated_cta_count / delta
active_ctas_per_sm
reservation_start / reservation_end / lifetime
resource_demand / capacity / peak_occupancy
tiles_total / tiles_assigned / duplicates / missing
logical_flops / physical_flops / replicated_flops
logical_bytes / physical_bytes / reduction_bytes
full_tiles / partial_tiles / padded_elements / useful_elements
unsupported_rows_by_reason
```

The validation denominator includes every source row. Unsupported rows are counted by reason and never silently disappear.

### Source evidence constraining E3

- `is_split_k` plus `cta_count / base_ctas` does not identify one authoritative split factor. Hopper ratios are often non-integer, H20 has `85` below-base-grid rows, and several non-Hopper targets have thousands of rows with `is_split_k=1` but `cta_count == base_ctas`.
- A simple padded-tile FLOP formula matches most non-split Hopper `tensor_all_ops` rows, while the full legacy Hopper calculator formula matches `40,632/40,632`. This proves analytical-feature provenance, not physical issued work. E3 must report logical, explicit-policy physical-issued, legacy analytical-feature, and separately collected measured-counter work rather than fitting the DES model to this column.
- Any row lacking authoritative persistent/split/reduction metadata remains explicitly unsupported and contributes to the denominator.

## E4 — GPGPU-Sim Cycle-Level PTX-Mode Comparator Benchmark

### External prerequisite

The user approved Accel-Sim/GPGPU-Sim plus a pinned CUDA/`nvcc` environment. Phase 2 must verify the selected Accel-Sim commit, the GPGPU-Sim submodule revision pinned by it, the official A100 configuration hash, CUDA/compiler versions, executable, and synthetic workload manifest. Missing or mismatched assets abort the benchmark; event counts, `nsys`, or algorithmic complexity are not runtime substitutes.

### Planned locations

```text
tests/performance/run_gpgpu_sim_comparison.py
tests/performance/cycle_level/a100_gemm.cu
tests/performance/cycle_level/workload_manifest.json
tests/performance/cycle_level/toolchain_lock.json
tests/performance/data/cycle_level/environment.json
tests/performance/data/cycle_level/des_runtime_raw.jsonl
tests/performance/data/cycle_level/gpgpu_sim_runtime_raw.jsonl
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/results_cycle_level_comparator.md
```

### Match key

- kernel/workload and dimensions;
- datatype;
- launch, CTA, tile, persistent, and split-K policy;
- cache/initial-residency state;
- output/timing boundary;
- host/toolchain environment.

### Mandatory numeric evidence

```text
workload_id
DES event/edge count
comparator simulated cycles/time
DES lowering/scheduling/report/total wall time raw samples
comparator setup/simulation/total wall time raw samples
median and p95 runtime
speedup = comparator_simulation_runtime / DES_total_runtime
confidence interval
simulated latency/cycle delta
matched_manifest_sha256
accel_sim_commit / gpgpu_sim_submodule_commit / config_sha256
failure/rejection count
```

Any `10000x` claim requires the same declared numerator/denominator across all reported rows and a user-approved acceptance statistic; a single favorable case is insufficient.

The evidence label is **GPGPU-Sim cycle-level PTX-mode comparison**. It is not strict A100 silicon cycle equivalence and is not Hopper evidence.

## E5 — Multi-Hardware Held-Out Zero-Shot

### Two evidence tiers

1. **Within-Hopper held-out:** H100 `4,246`, H20 `2,879`, H200 `4,239`, and H800 `3,800` currently supported rows, total `15,164`.
2. **Cross-architecture held-out:** Ampere, Ada, and Blackwell only after matched split-K/persistent semantics provide nonzero support.

### Planned locations

```text
tests/validation/validate_multi_hardware_zero_shot.py
tests/validation/data/zero_shot_split.json
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/multi_hardware_raw.csv
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/results_multi_hardware.md
```

### Freeze and leakage rules

- The four within-Hopper folds are fixed as target=`H100`, target=`H20`, target=`H200`, and target=`H800`; the other three Hopper devices form the source/development set in each fold.
- Row inclusion is determined only from immutable non-latency schema, authoritative manifest availability, and the frozen supported domain. No actual-time threshold or post-score rule may alter support.
- Lowering, resource model, cache/launch semantics, calibration policy, thresholds, and supported-domain rules are frozen before reading held-out target latency.
- Target hardware specification and explicit launch metadata are allowed inputs.
- Specification-derived target calibration is allowed; target measured primitive calibration is forbidden in this zero-shot tier.
- Target final latency is evaluation-only and never used for fitting or rule selection.
- Complete-operator latency is not used as primitive calibration.
- Prediction rows, rejection reasons, manifest/calibration hashes, and the command log are written and hashed before the target latency column is joined for final scoring.

### Mandatory numeric evidence

For every hardware and category:

```text
total_rows
supported_rows
unsupported_rows_by_reason
actual_us
DES_us
classical_us
absolute_error_us
relative_error
median / p95 / MAPE
bound_violation_count and rate
each violating actual/DES pair
DES runtime
calibration_manifest_hash
```

Macro-average and worst-hardware metrics are reported in addition to pooled metrics.

## E6 — Measured Primitive Calibration

### Calibration boundary

Calibration operates on named primitives rather than correcting complete operator latency:

```text
launch
DRAM
L2
MMA
FMA
SFU
barrier
reduction
```

The campaign is a separate explicitly non-zero-shot empirical study when it uses target-hardware primitive measurements. It does not replace the specification-calibrated zero-shot folds and does not certify a universal physical lower bound.

### Planned locations

```text
tests/performance/benchmark_des_primitives.py
tests/validation/validate_primitive_calibration.py
tests/performance/data/primitive_calibration/environment.json
tests/performance/data/primitive_calibration/raw_measurements.csv
tests/performance/data/primitive_calibration/raw_counters.csv
tests/performance/data/primitive_calibration/calibration_manifest.json
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/results_primitive_calibration.md
```

### Required provenance

- schema version;
- hardware name, UUID, and architecture;
- driver, CUDA, compiler, and benchmark commit;
- clock, power, temperature, dtype, and size regime;
- calibration and held-out sample IDs;
- formula/coefficients and source-data SHA-256;
- warmup, repeats, raw samples, and uncertainty.
- disjoint primitive calibration IDs and held-out primitive evaluation IDs fixed before collection;
- per-sample known quantity and timing boundary;
- selected coefficient rule: median of valid duration-per-unit calibration samples, with p05/p95 retained rather than hidden;
- separate fixed-cost controls for launch/synchronization rather than redistributing them into throughput coefficients.

### Mandatory numeric evidence

```text
primitive
quantity
predicted_duration
actual_duration
absolute_error
relative_error
p50 / p95 / confidence interval
counter-predicted work / measured work / delta
held-out bound violations
```

No ML scaling closure, final-latency correction factor, clamp, or hidden target-hardware fitting is accepted.

## E7 — Universal Lower-Bound Audit

### Modeled theorem evidence

- formal supported-domain quantifiers: every non-empty finite normalized acyclic EventGraph after one manifest-order cache resolution, fixed finite non-negative durations, non-negative integer global/transient per-SM demands, positive integer capacities and SM count, non-preemptive half-open scheduling, and explicit dependencies;
- fixed graph/resource/cache/launch semantics;
- proof that dependency critical path, each chip-global resource-time/capacity term, and each aggregate per-SM resource-time/aggregate-capacity term is no greater than modeled optimum;
- proof that dropping affinity and lifetime reservation constraints is a safe named relaxation, with no unproved lifetime/affinity tightening term;
- exact-oracle comparison on exhaustive/property-generated small cases;
- permutation, conservation, monotonicity, and rejection evidence.

### Planned locations

```text
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/formal_bound_contract.md
tests/unit/test_safe_bound_permutation_properties.py
tests/unit/test_safe_bound_conservation_properties.py
tests/validation/validate_safe_bound_exact_oracle.py
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/safe_bound_oracle_cases.json
task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/results_universal_bound_audit.md
```

### Mandatory numeric evidence

```text
oracle_cases_total / passed
permutations_checked / mismatches
conservation_failures
monotonicity_failures
unsupported counts by reason
measured rows / supported rows
bound violations
actual_us / bound_us / excess_us / excess_percent for every violation
```

### Claim boundary

A MODELED THEOREM is universal only over its declared model domain. A finite measured-hardware audit can support an empirical coverage statement but cannot prove a theorem over all physical executions. These conclusions remain separate in every report and public document.

The four historical violations remain mandatory regression evidence with actual/DES pairs `10.472800/11.358228`, `10.619200/11.324017`, `8.213200/10.016648`, and `10.056400/10.243910` microseconds. They remain failures until a matched root-cause correction changes the underlying modeled inputs; they are never dropped or clamped.

## Planned Reproducibility Wrapper

Each implemented experiment will record:

1. full script path;
2. exact command;
3. Python/conda/venv and dependency versions;
4. input manifest and SHA-256;
5. expected acceptance conditions;
6. exit code and raw-log path;
7. actual compared values and derived metrics;
8. every failure, diagnosis, fix, and rerun.

The final authoritative commands will be copied into `test_report_2026-07-20_des_full_semantics_and_scientific_validation.md`; this draft does not invent commands before scripts exist.
