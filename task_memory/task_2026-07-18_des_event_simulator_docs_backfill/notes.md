# DES Event Simulator Documentation Backfill Notes

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added bounded validation metrics, scheduler scaling evidence, event-usage facts, and test coverage counts. |
| 2026-07-18 | Added verified Python/test environment and global environment-handbook reference. |
| 2026-07-18 | Recorded GEMM validation-schema and throughput-unit evidence. |
| 2026-07-18 | Added implementation inventory, commit provenance, and post-Ultragoal FlashAttention evidence. |
| 2026-07-18 | Recorded the initial source-document audit and provenance hierarchy. |
| 2026-07-18 | Created operational notes for the documentation backfill. |

## Operational Context

- Working directory: `/data/ycfeng/pipeweave/.worktrees/des`.
- Git branch: `des`.
- The task is a documentation-only reconstruction; no code behavior changes are authorized.
- `.omc/ultragoal/plan.md` and `.omc/ultragoal/ledger.md` are ignored runtime records and must be treated as evidence, not as the durable final task record.
- Preserve the existing `docs/des_design_rules.md` and `docs/event_simulator_design.md` as source artifacts.
- An unrelated untracked path named `=10.1` existed before this task and must not be modified.
- Repository safety rules prohibit `rm` and `mv` without explicit user permission.

## Execution Reminders

- Read `task_memory/env_handbook.md` first if an environment problem is encountered.
- Record discrepancies and root-cause analysis in `issues.md`; do not hide them with fallback explanations.
- Use exact repository paths and symbol names when linking implementation evidence.
- Update `progress.md` after each phase and keep status synchronized with `plan.md`.

## Verified Local Test Environment

- Conda environment: none (`CONDA_DEFAULT_ENV` unset).
- Virtual environment: none (`VIRTUAL_ENV` unset).
- Python: `/usr/bin/python`, version `3.12.3`.
- pytest: version `9.1.1` (invoked as `python -m pytest`).
- numpy: `2.4.6`; pandas: `3.0.3`.
- `event_simulator` imports from this worktree.
- GNU `/usr/bin/time` is unavailable; use the verified Bash timing recipe in `task_memory/env_handbook.md`.

## Source Register

| Source | Role in Reconstruction | Initial Observation |
|---|---|---|
| `README.md` | Public repository and MVP usage boundary | Documents the independent Phase 0 simulator and three original operator lowerings, but not the later refined-roofline Phase 1+2 work. |
| `docs/event_simulator_design.md` | Historical Phase 0 architecture and staged research plan | Explicitly labels Phase 0 implemented and Phase 1+ pending; current-state claims require reconciliation with later code. |
| `docs/superpowers/plans/2026-07-17-event-simulator-mvp.md` | Original MVP scope and acceptance criteria | Confirms deterministic single-device scheduler, fail-fast validation, three lowerings, reports, and tests. |
| `docs/des_design_rules.md` | Refined-roofline invariants and validation protocol | Defines the lower-bound invariant, resource/rate consistency, structural effects, overlap rules, metrics, and GEMM v2 DAG. |
| `.omc/ultragoal/plan.md` | Ignored Phase 1+2 execution plan | Defines five stories: Event IR extension, hardware adapter, structural utilities, GEMM v2, and dataset validation. |
| `.omc/ultragoal/ledger.md` | Ignored execution ledger | Claims all five stories completed, but records a deferred `tile_K`/L2 working-set limitation for large compute-bound GEMMs. |

## Guidance Provenance

- No repository-local `AGENTS.md` or `CLAUDE.md` file exists in this worktree.
- The active task rules are supplied through the conversation/runtime and are being applied to this task directory.

## Implementation Inventory

| Ultragoal Story / Later Work | Current Evidence | Audit State |
|---|---|---|
| G001 Event IR extension | `event_simulator/events.py` defines lifecycle, wave-aware CTA, cache-aware memory, utilization-aware compute, synchronization, and FlashAttention event types. | Implemented and exercised by the 74-test regression suite. |
| G002 hardware adapter | `event_simulator/hardware_adapter.py` defines `HardwareConfig`, `load_hardware_config`, `derive_resource_config`, and `derive_calibration`. | Implemented; 8/8 adapter tests pass. |
| G003 Structural utilities | `event_simulator/structural.py` defines wave split, L2 ratio, tile efficiency, edge detection, and actual tile dimensions. | Implemented; 24/24 structural tests pass. |
| G004 GEMM v2 | `event_simulator/operators.py:374` defines `lower_gemm_v2` and emits one chip-level DRAM event plus per-CTA admission/MMA/store events. | Implemented with a discovered `tile_k` regression; see I-004. |
| G005 dataset validation | `tests/validation/validate_gemm_v2.py` exists. | Harness implemented; bounded metrics audited; **not accepted**. |
| Post-Ultragoal FlashAttention | `lower_flash_attention` is exported by `event_simulator/__init__.py` and covered by `tests/integration/test_fa_simulation.py`. | Implemented after the five-story plan; durable design docs are stale. |

## Commit Provenance

- `418ba05`: Phase 0 mechanistic simulator MVP.
- `b29607d`: Refined-roofline Phase 1+2 implementation.
- `cd44a4c` through `04e19f9`: successive GEMM calibration/memory-model corrections.
- `a7db073` and `0ee2110`: FlashAttention lowering and scheduling correction.
- `57d923f`: added `docs/des_design_rules.md` and corrected throughput/memory conventions.

## Validation Data Facts

- `dataset/gemm_test.csv` contains 118,800 rows and 10,800 H100 rows.
- The H100 subset has zero rows with non-positive `M`, `N`, `K`, `tile_M`, or `tile_N`.
- The H100 dataset exposes `tile_K`, and its observed value is `64`, but `tests/validation/validate_gemm_v2.py::des_predict` neither reads nor forwards that column.
- `hardware/H100.json` defines `tcBf16=4096`, `smFreq=1830`, and `numSms=132`; by the repository's unit convention this is `989.42976` chip-wide TFLOPS, not `4096` TFLOPS.
- `tests/validation/validate_gemm_v2.py::classical_roofline` treats `tcBf16` as chip-wide TFLOPS, overstates peak throughput by `4.1397582381x`, and therefore understates the compute-bound baseline time by the same factor.

## Fresh Validation Evidence

### Regression Coverage

| Test File | Collected Tests | Result |
|---|---:|---|
| `tests/unit/test_event_scheduler.py` | 14 | PASS |
| `tests/unit/test_hardware_adapter.py` | 8 | PASS |
| `tests/unit/test_structural.py` | 24 | PASS |
| `tests/integration/test_operator_simulation.py` | 7 | PASS |
| `tests/integration/test_gemm_v2_simulation.py` | 11 | PASS |
| `tests/integration/test_fa_simulation.py` | 10 | PASS |
| **Total** | **74** | **PASS** |

### Deterministic Bounded GEMM Validation

The local audit used `pandas.DataFrame.sample(n=5, random_state=42)` independently for Large, Medium, and Small H100 categories.

| Category | Evaluated | Violations | Violation Rate | Mean Gap | Median Gap | Gap Range |
|---|---:|---:|---:|---:|---:|---:|
| Large | 5 | 0 | 0.000000% | 16.922601% | 18.139800% | 13.702786%–20.754829% |
| Medium | 5 | 0 | 0.000000% | 46.647680% | 44.013243% | 29.472309%–65.989583% |
| Small | 5 | 0 | 0.000000% | 45.909409% | 57.965279% | 14.202214%–81.805879% |

This bounded sample supports the lower-bound invariant but fails the G005 `<15%` large-GEMM mean-gap criterion (`16.922601%`, +`1.922601` percentage points).

### `tile_k` Behavioral Check

For `M=N=K=4096`, `tile_M=tile_N=128`, `tile_k=0` and `tile_k=64` both produced 3,075 events with identical full event signatures and identical makespan `143.257862154871 us`; absolute delta was `0.000000000000 us`.

### Full-Validation Scalability

- The current script selects 200 Large + 100 Medium + 100 Small H100 rows.
- Large-sample event counts: minimum 381, median 3,555, p90 28,517, p95 42,861, maximum 70,371, mean 9,667.935 events.
- The full run remained in the 200-row Large category after more than 16 minutes at 100% of one CPU core and was interrupted.
- Controlled scaling from 387 to 6,147 events increased scheduler time from `0.014453 s` to `1.026491 s`; the doubling exponent rose from `1.172` to `1.882`, approaching quadratic scaling.

### Current Event-IR Usage

- `EVENT_TYPES` contains 22 values.
- `GlobalLoad_L2Hit`, `MMA_PipelineDrain`, and `FA_Memory` are declared and calibrated but are not emitted by any current lowering.
- GEMM v2 expresses L2 reuse by reducing the one chip-level `GlobalLoad_L2Miss` byte count; it does not emit a literal L2 hit/miss event split.
- `dataset/fa3_benchmark_h800.csv` contains only 2 measured configurations plus its header, while the benchmark driver enumerates 21 configurations; no tracked script compares those measurements with DES output.
