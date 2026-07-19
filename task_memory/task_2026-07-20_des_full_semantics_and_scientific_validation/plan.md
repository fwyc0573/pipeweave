# DES Full Semantics and Scientific Validation Plan

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Completed the executable GSD blueprint with frozen Wave-0 decisions, exact file ownership, entry/exit invariants, TDD commands, and Phase-1 checkpoint gate. |
| 2026-07-20 | Identified the Accel-Sim/GPGPU-Sim A100 benchmark candidate and made dependency approval a Wave-0 gate. |
| 2026-07-20 | Selected the standard-library exhaustive serial SGS exact oracle and marked its proof/test obligations for Wave 2. |
| 2026-07-20 | Marked the four-layer provenance contract resolved by the user's Option A decision and retained all remaining Wave 0 gates. |
| 2026-07-20 | Linked the conditional GSD waves to one centralized experiment/evidence protocol covering all twelve outcomes. |
| 2026-07-20 | Refined the exact-oracle decision to compare built-in enumeration and currently available SciPy/HiGHS without selecting a dependency. |
| 2026-07-20 | Added the conditional GSD dependency graph and preliminary Claude WATCH disposition without authorizing implementation. |
| 2026-07-20 | Integrated the independent evidence inventory and made external comparator/hardware prerequisites explicit. |
| 2026-07-20 | Added the initial two-phase execution plan and design-review stop condition; detailed GSD tasks remain pending discussion decisions. |

## Status

- Overall: In progress.
- Current phase: Phase 1 — approved/validated checkpoint delivery.
- Production code: Frozen.

## Phase 1 — Plan, Discuss, and Design

1. Recover the parent task contracts, SafeBound handoff, current source/data/test facts, branch state, and fresh baseline.
2. Create this task's raw requirements, operational notes, issue register, harness, and requirement-to-evidence matrix.
3. Resolve each material semantic ambiguity one question at a time and append the accepted answers to `requirements.md`.
4. Produce the GSD blueprint with exact types, APIs, ownership, dependencies, failure behavior, entry/exit invariants, tests, evaluation commands, and wave gates.
5. Challenge the complete phase-1 design through independent StepCode Claude review.
6. If the verdict is `APPROVE`, proceed. If `WATCH`, record and monitor each risk. If `BLOCK`, stop for user adjudication.

Phase 1 must also freeze:

- the named cycle-level comparator and matched boundary;
- the cache/residency measurement states;
- the within-Hopper versus cross-architecture zero-shot labels and hardware splits;
- the measured primitive-calibration provenance and non-overlap rules;
- the exact quantifiers of the universal claim.

## Phase 2 — Implement and Evaluate

Phase 2 executes the GSD graph below only after the Phase-1 design gate, fresh regression/document validation, Lore commit, push, and `HEAD == origin/des` check. Every behavior slice is personally observed RED, then minimal GREEN, then focused REFACTOR. Important module milestones receive independent StepCode Claude review before their dependents begin.

External comparator or GPU campaigns cannot be replaced by proxy results. A missing required binary, permission, controlled environment, or authoritative manifest stops the affected campaign with exact context; it does not authorize a fallback or a reduced completion claim.

## Executable GSD Dependency Graph

### Wave 0 — Semantic decisions and evidence contracts

1. **Resolved:** separate exact optimum, scalable SafeBound, feasible schedule, and measured comparison contracts (user-selected Option A).
2. **Resolved:** one normalized EventGraph with explicit dependencies and no iterable-derived stream order.
3. **Resolved:** atomic global/per-SM demand, one ResourceLifetime occupancy reservation, and explicit eligible-SM affinity.
4. **Resolved:** one manifest-order abstract HBM+L2 size-aware LRU model with explicit initial state and output visibility.
5. **Resolved:** persistent work and split-K/reduction topology come only from `GemmLaunchManifest`.
6. **Resolved:** logical, explicit physical-issued, legacy analytical, and measured-counter work remain separate.
7. **Resolved:** scheduler priority is descending remaining dependency-path duration then `event_id`; old caller-order compatibility is removed.
8. **Resolved design:** standard-library exhaustive serial SGS over every precedence-feasible permutation; caller-supplied budget fails with no result, and measured runtime determines documented practical limits.
9. **Resolved and user approved:** pinned Accel-Sim/GPGPU-Sim plus pinned CUDA/`nvcc`, official A100 configuration, and one versioned synthetic PTX-mode GEMM manifest; no Hopper or `nsys` substitution.
10. **Resolved:** specification-only target calibration for four Hopper zero-shot folds, separate non-zero-shot measured primitive calibration, and a universal theorem limited to the declared fixed-duration manifest-order model.

The exact-oracle decision compared, using the accepted semantic subset:

- a no-new-dependency exhaustive/branch-and-bound implementation with proof of schedule coverage;
- the currently available but undeclared SciPy/HiGHS MILP path with a proven formulation and zero-gap completion contract;
- any newly proposed solver only after explicit dependency approval.

No default event-count or wall-clock limit becomes an acceptance contract before a focused performance experiment records actual solved-case counts, runtimes, enumerated orders, and failure behavior. A caller-supplied budget is a fail-fast computation contract, not an exact fallback.

### File ownership and interface boundaries

| File | Sole responsibility in this task | Prohibited duplication |
|---|---|---|
| `event_simulator/events.py` | Immutable `Event`, normalized frozen `EventGraph`, canonical graph maps, graph/lifetime structural validation | No downstream duplicate ID/dependency/cycle validation |
| `event_simulator/resources.py` | Two-level `ResourceConfig`, immutable `ResourceLifetime`, numeric `PrimitiveCalibration` | No scheduler-owned resource schema or alternate topology framework |
| `event_simulator/cache.py` | `CacheConfig`, `InitialCacheState`, `CacheAccess`, deterministic resolution and immutable evidence | No heuristic hit-ratio path in the new manifest flow |
| `event_simulator/gemm_manifest.py` | Worker, WorkItem, ReductionStep, `GemmLaunchManifest`, work/traffic/topology conservation | No CTA-ratio, `is_split_k`, or legacy floor-ratio reconstruction |
| `event_simulator/exact_oracle.py` | Exhaustive precedence-permutation enumeration, serial SGS, `ExactScheduleResult`, incomplete-search error | No graph validator, cache model, scheduler fallback, or pruning in initial GREEN |
| `event_simulator/safe_bound.py` | Immutable term evidence and the proven critical-path/global/per-SM aggregate bound | No feasible-schedule or measured-hardware certification |
| `event_simulator/scheduler.py` | `ScheduleEntry`, `SimulationResult`, deterministic feasible placement, admission counters | No semantic dependency mutation or graph revalidation |
| `event_simulator/report.py` | Distinct proof/exact/schedule/measured names and demand-weighted attribution | No recomputed graph proof or mislabeled makespan |
| `event_simulator/operators.py` | Lower validated manifests/operators into Events and explicit dependencies | No cache policy, launch inference, or scheduling policy |
| `event_simulator/hardware_adapter.py` | Hardware-spec parsing and specification-derived calibration/resource construction | No measured-data fitting or empirical correction |
| `tests/validation/validate_gemm_v2.py` | Shared authoritative row parsing, unsupported accounting, and absolute metrics for offline studies | No second validator with different support rules |
| `tests/performance/` | Reproducible scheduler, primitive, and GPGPU-Sim collection harnesses | No production semantic logic |

`event_simulator/__init__.py`, `README.md`, and `docs/event_simulator_design.md` expose and document the accepted interfaces only after their module tests pass. Existing references are updated in the same wave; no compatibility adapter preserves the rejected implicit-stream or mutable-Event behavior.

### Wave 1 — Shared semantic kernel

**Entry invariant:** Phase-1 checkpoint is pushed and the repository baseline passes.

1. RED `tests/unit/test_event_graph.py` for canonical order, permutations, duplicate/unknown/self dependency, cycles, explicit stream semantics, lifetime endpoints/membership, and immutability.
2. RED `tests/unit/test_resource_semantics.py` for global/per-SM capacities, simultaneous vectors, reservation limits, eligible SMs, impossible reservations, and the two-lifetime hold-and-wait counterexample.
3. GREEN only in `events.py` and `resources.py`; migrate all source/tests to the single EventGraph/ResourceConfig contract and remove scheduled times, `stream_ordered`, and single `resource` from Event.
4. REFACTOR only after focused and existing integration tests pass.

Focused command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider \
  tests/unit/test_event_graph.py tests/unit/test_resource_semantics.py \
  tests/unit/test_event_scheduler.py tests/unit/test_hardware_adapter.py \
  tests/integration/test_operator_simulation.py tests/integration/test_fa_simulation.py -q
```

**Exit invariant:** every downstream algorithm can accept exactly one validated EventGraph and ResourceConfig; no duplicate graph validator, implicit stream edge, scheduled Event mutation, partial demand acquisition, or cross-lifetime hold-and-wait state remains. Run an independent Claude shared-kernel code review before Wave 2/3.

### Wave 2 — Proof layer

**Entry invariant:** Wave 1 tests and Claude module review pass.

1. RED `tests/unit/test_exact_oracle.py` plus independent `tests/unit/exact_time_grid_reference.py` for optimality, multi-resource conflict, precedence/resource interaction, tied starts, zero duration, permutations, unsupported lifetime/affinity, and budget exhaustion.
2. GREEN dependency-free exhaustive serial SGS in `exact_oracle.py`; initial implementation has no branch-and-bound pruning.
3. RED `tests/unit/test_safe_bound.py`, `test_safe_bound_permutation_properties.py`, and `test_safe_bound_conservation_properties.py` for critical-path, global work, aggregate per-SM work, relaxation labels, monotonicity, and `SafeBound <= exact optimum`.
4. GREEN the minimal immutable term evidence in `safe_bound.py`; add `formal_bound_contract.md` and the generated tiny-case evidence only after tests pass.

Focused command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider \
  tests/unit/test_exact_oracle.py tests/unit/test_safe_bound.py \
  tests/unit/test_safe_bound_permutation_properties.py \
  tests/unit/test_safe_bound_conservation_properties.py -q
```

**Exit invariant:** every exact result was produced by complete search; every SafeBound term has a proof and is permutation-invariant; exhaustive tiny integer cases have zero exact mismatches and zero safety violations. Run independent Claude proof-layer code review.

### Wave 3 — Feasible scheduler

**Entry invariant:** Wave 1 semantic kernel is accepted; Wave 2 exact oracle is available for tiny comparisons.

1. RED scheduler tests for priority/tie order, dependency feasibility, atomic multi-resource placement, per-SM co-location, affinity, lifetime acquisition/release, blocked-ready rechecks, zero duration, impossible state, and caller-order invariance.
2. GREEN ready-queue/event-completion scheduler with immutable ScheduleEntry and explicit admission counters.
3. RED/ GREEN report tests separating dependency critical path, exact optimum, SafeBound, feasible makespan, and demand-weighted resource-time.
4. Run `tests/performance/benchmark_event_scheduler.py` on versioned graph sizes including the historical `58,467`-Event case; record events, edges, heap operations, ready scans, placement checks, lifetime checks, wall time, expected old `115.882818766s`, actual new runtime, and delta.

Focused command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider \
  tests/unit/test_event_scheduler.py tests/unit/test_report.py \
  tests/integration/test_operator_simulation.py -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python tests/performance/benchmark_event_scheduler.py
```

**Exit invariant:** every output is deterministic and feasible, no Event is mutated, no scheduler result is labeled a bound, and total performance claims include placement/scanning work plus measured wall time. Run independent Claude scheduler/report code review.

### Wave 4 — Operator lowering

**Entry invariant:** Waves 1–3 pass and their module reviews have no unresolved BLOCK.

1. RED/ GREEN `tests/unit/test_cache.py` and `event_simulator/cache.py` for cold/warm state, hit/miss recency, variable final blocks, eviction, dirty writeback, HBM/L2 visibility, and all fail-fast branches.
2. Independent Claude cache-module code review.
3. RED/ GREEN `tests/unit/test_gemm_manifest.py` and `event_simulator/gemm_manifest.py` for coverage, persistent workers, split-K partitions, reductions, logical/issued work, access references, and every rejection case in `design.md`.
4. RED/ GREEN manifest lowering in `operators.py`, hardware construction in `hardware_adapter.py`, cross-module integration tests, and updates to the existing authoritative `validate_gemm_v2.py`; no separate support-rule validator is introduced.
5. Remove the FA Event-list interleaving behavior and represent assignment/affinity explicitly, with focused RED integration tests.

Focused command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider \
  tests/unit/test_cache.py tests/unit/test_gemm_manifest.py \
  tests/unit/test_gemm_validation.py tests/integration/test_gemm_v2_simulation.py \
  tests/integration/test_fa_simulation.py tests/integration/test_operator_simulation.py -q
```

**Exit invariant:** cache traffic, lifetime occupancy, persistent assignment, split-K replication/reduction, and logical/physical work are conserved from one explicit manifest; every unavailable policy is rejected and counted. Run independent Claude manifest/lowering code review.

### Wave 5 — Evaluation infrastructure and studies

**Entry invariant:** all production modules, integration tests, and module reviews pass. GPU work first re-reads `/data/ycfeng/stepfun-env-handbook/guidence.md`, uses its verified `rlaunch` recipe, and runs `--predict-only` before a large request. Docker work first re-reads `/data/ycfeng/stepfun-env-handbook/docker.md`.

1. Run E0–E3 exact/bound/scheduler/cache/manifest validations and write numeric expected/actual/delta evidence.
2. Provision the approved pinned Accel-Sim/GPGPU-Sim + CUDA/`nvcc` environment, verify all hashes, and run the one A100 synthetic GPGPU-Sim cycle-level PTX-mode comparison.
3. Run the measured primitive campaign with disjoint calibration/evaluation IDs and raw samples/counters; keep this study explicitly non-zero-shot.
4. Freeze prediction artifacts before joining target latency, then run four within-Hopper zero-shot folds. Run cross-architecture folds only where authoritative manifests provide nonzero support; count every unsupported row.
5. Run the universal modeled-bound audit and the separate finite real-hardware audit, including all four historical violations.
6. Update README/design documentation, the required numeric test report, review log, English summary with SHA-256 inventory, lessons, and issue resolutions.
7. Run independent Claude final design/code/science review, full regression, document checks, `git diff --check`, Lore commit, push, and remote equality verification.

Authoritative final command family:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider tests -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python tests/validation/validate_safe_bound_exact_oracle.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python tests/validation/validate_gemm_v2.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python tests/validation/validate_multi_hardware_zero_shot.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python tests/validation/validate_primitive_calibration.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python tests/performance/run_gpgpu_sim_comparison.py
git diff --check
```

**Exit invariant:** every one of R1–R12 has direct authoritative evidence, every supported claim uses the exact declared label, every unsupported/violation count is visible, and no proxy, fallback, clamp, empirical scaling closure, or duplicate semantic model remains.

Every behavior task follows RED -> GREEN -> REFACTOR and cannot begin before its upstream semantic/API task passes its module-review gate.

## Acceptance Criteria

- All twelve requested outcomes have a direct row in `requirements_matrix.md` with authoritative evidence.
- All Harness gates are PASS or explicitly adjudicated as NOT APPLICABLE; no required item remains UNPROVEN or BLOCKED at completion.
- The complete repository regression passes from the documented environment.
- Scientific claims are no broader than their proof and measured evidence.
- The final branch is clean, committed with Lore trailers, pushed, and equal to `origin/des`.

The authoritative experiment design for those criteria is `experiments.md`. Implementation tasks may refine paths only during the final ownership review; they may not weaken metrics, hide unsupported rows, or substitute proxy evidence.
