# DES Full Semantics and Scientific Validation Notes

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Recorded asynchronous `omx ask` completion behavior and the restored Wave-3 review artifacts. |
| 2026-07-20 | Recorded user approval for the pinned Accel-Sim/GPGPU-Sim and CUDA/`nvcc` comparator environment. |
| 2026-07-20 | Reconciled the comparator Claude APPROVE/WATCH and corrected its unsupported claim that PTX mode makes `nvcc` irrelevant. |
| 2026-07-20 | Added official Accel-Sim/GPGPU-Sim A100 configuration evidence, absent Hopper support, and the GitHub API rate-limit diagnosis. |
| 2026-07-20 | Recorded and reconciled the cache/GEMM-manifest Claude WATCH, including the rejected isolated-cache bound direction. |
| 2026-07-20 | Recorded the shared execution-review artifact, its two corrected reasoning gaps, and the GPU/comparator availability process note. |
| 2026-07-20 | Corrected the provenance of `tensor_all_ops`, quantified its exact agreement with the legacy Hopper analytical formula, and recorded the non-authoritative split heuristic. |
| 2026-07-20 | Added the corrected split-K/partial-tile dataset audit and current report-provenance source facts. |
| 2026-07-20 | Added exact-solver environment availability and a numeric SciPy/HiGHS MILP smoke result. |
| 2026-07-20 | Added the independent evidence inventory, multi-hardware coverage counts, calibration boundary, and external-evaluation prerequisites. |
| 2026-07-20 | Recorded the recovered workspace, baseline, parent-contract, environment, and execution constraints. |

## Recovered Workspace

- Repository worktree: `/data/ycfeng/pipeweave/.worktrees/des`
- Branch: `des`
- Local HEAD: `d596e1bd7f5cb8e12e4d1034ad4be51c37ae248b`
- Remote baseline: `origin/des` at the same commit.
- Recovery status: clean working tree before this task's documentation initialization.
- Trellis status: no `.trellis/` directory; the repository is not trellis-initialized.
- Historical path `=10.1`: explicitly excluded from all operations and evidence.

## Fresh Baseline

- Python: `/usr/bin/python`, version `3.12.3`.
- pytest: `9.1.1`.
- Active conda/virtual environment: none.
- Command:

  ```bash
  PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider tests -q
  ```

- Result: `141 passed in 7.82s`; wrapper elapsed `8.979s`, user `4.980s`, system `0.100s`; exit code `0`.

## Inherited Scientific Constraints

- `SimulationResult.makespan` is a heuristic feasible-schedule estimate, not a certified bound.
- `SafeBound` is a distinct provenance type and is currently exact only for non-empty, independent, unresource-bound events.
- No implicit conversion from a scheduler result to a measured-hardware bound is permitted.
- No fallback, empirical scaling, clamp, silent skip, or unsupported causal attribution is permitted.
- Any behavior change must start with an observed targeted RED test.
- Scientific reports must include absolute actual, candidate-bound, and baseline values, not ratios alone.

## Operational Reminders

- Phase 1 is documentation, discussion, design, and independent review only.
- Production code remains frozen until the phase-1 Claude verdict is `APPROVE` or `WATCH`; `BLOCK` requires user adjudication.
- External simulator, GPU, or Docker work must follow the applicable authoritative handbook before commands are run.
- Any new environment problem must first be checked against `task_memory/env_handbook.md`.

## StepCode Claude Runtime Note

- Two Wave-3 `omx ask claude` wrapper calls returned a StepCode session ID before the underlying local Claude process finished. The actual reviews continued in `~/.stepcode/sessions/*.jsonl` and later produced normal `.omx/artifacts/` files with exit code `0`.
- Before treating an early wrapper return as failure or launching a duplicate review, check the referenced process/session log and newest artifact. Do not kill a still-running local review solely because the wrapper returned first.
- The recovered focused artifacts are `.omx/artifacts/claude-independent-read-only-pipeweave-des-wave-3-decision-review-i-2026-07-19T21-18-41-544Z.md` and `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-architecture-proof-r-2026-07-19T21-19-44-165Z.md`.

## Independent Evidence Inventory

- `dataset/gemm_test.csv` contains `118,800` measured rows across `11` hardware names, `10,800` rows per hardware.
- Under the current validator contract, only four Hopper devices have any supported non-split-K, matched-grid rows:
  - H100: `4,246`
  - H20: `2,879`
  - H200: `4,239`
  - H800: `3,800`
  - Total: `15,164`
- The seven Ampere, Ada, and Blackwell targets have `0` currently supported rows because all `10,800/10,800` rows per target are split-K under the dataset policy. They cannot support a cross-architecture DES study until split-K/persistent launch semantics are modeled.
- Existing measured CSV files omit the driver, CUDA, clock, power, kernel-binary, cache-state, repeat, and uncertainty provenance required for the strongest matched-hardware claim.
- `derive_calibration()` currently converts hardware JSON peak rates into idealized coefficients; it is not measured primitive calibration.
- The repository contains no named cycle-accurate comparator, executable/configuration, workload manifest, or matched comparator runtime.
- DES is not connected to the existing `aggregator.py`/workload E2E path, so measured E2E JSONL files are not current DES evidence.
- `compute_l2_hit_ratio()` is an exported/tested analytical helper but is not part of production lowering or cache state.
- `tests/validation/benchmark_fa3.py` catches broad exceptions and continues; it cannot serve as this task's final fail-fast validation harness without a root-cause change.

## External Evaluation Prerequisites

- Objective 9 requires a selected, version-pinned, matched cycle-accurate comparator and its binary/trace/configuration inputs.
- Objectives 4, 10, and 11 may require actual GPU access plus CUPTI/Nsight permissions and controlled clock/power/environment provenance.
- Any GPU allocation will follow `/data/ycfeng/stepfun-env-handbook/guidence.md` exactly and will begin with `--predict-only` when the design reaches that stage.

## Exact-Solver Environment Audit

- The repository has no `pyproject.toml`, `setup.py`, `setup.cfg`, requirements file, environment YAML, or Pipfile within depth two; no solver dependency is currently declared.
- Available modules in the current Python environment:
  - SciPy `1.17.1`
  - NumPy `2.4.4`
  - NetworkX `3.6.1`
- Unavailable modules:
  - OR-Tools
  - `highspy` as a direct package
  - PuLP
  - Z3
- No Python source file currently imports or references SciPy, OR-Tools, HiGHS, PuLP, Z3, `milp`, `linprog`, or NetworkX.
- A read-only SciPy `optimize.milp` smoke used a two-variable integer problem and completed with:
  - `status=0`
  - `success=True`
  - objective `2.0`
  - solution `[0.0, 2.0]`
  - `mip_gap=0.0`
  - `mip_node_count=0`
- This proves only that the current host can execute SciPy's HiGHS-backed MILP interface. It does not approve SciPy as a project dependency or prove that a scheduling formulation is correct or scalable.

## Split-K and Partial-Tile Dataset Audit

- Dataset: `dataset/gemm_test.csv`, `118,800` rows, `30` columns.
- The schema includes `is_split_k`, `cta_count`, tile dimensions, and `tensor_all_ops`, but not a split factor, persistent worker count, work assignment, reduction tree/policy, partial-accumulator format, or kernel binary identity.
- Split-K CTA-grid results:

| Hardware | Split-K rows | CTA count divisible by base grid | CTA count equals base grid | CTA count below base grid | CTA ratio range |
|---|---:|---:|---:|---:|---:|
| A100 | 10,800 | 10,800 | 8,899 | 0 | 1.000000–24.000000 |
| A40 | 10,800 | 10,800 | 8,464 | 0 | 1.000000–16.000000 |
| H100 | 437 | 353 | 0 | 0 | 1.178571–4.137931 |
| H20 | 1,266 | 912 | 0 | 85 | 0.131313–7.800000 |
| H200 | 408 | 335 | 0 | 0 | 1.178571–4.137931 |
| H800 | 457 | 395 | 0 | 0 | 1.178571–4.137931 |
| L20 | 10,800 | 10,800 | 6,186 | 0 | 1.000000–56.000000 |
| L40 | 10,800 | 10,800 | 5,025 | 0 | 1.000000–56.000000 |
| RTX 6000 Ada | 10,800 | 10,800 | 5,025 | 0 | 1.000000–56.000000 |
| RTX A6000 | 10,800 | 10,800 | 8,587 | 0 | 1.000000–13.000000 |
| Blackwell | 10,800 | 10,800 | 8,512 | 0 | 1.000000–16.000000 |

- Non-split Hopper `tensor_all_ops` comparison against simple logical and padded formulas:

| Hardware | Rows | Equals logical FLOPs | Equals padded-tile FLOPs | Logical ratio median / p95 | Padded ratio median / p95 |
|---|---:|---:|---:|---:|---:|
| H100 | 10,363 | 1,189 | 9,366 | 1.017668 / 1.333333 | 1.000000 / 1.090909 |
| H20 | 9,534 | 475 | 9,202 | 1.015404 / 1.230769 | 1.000000 / 1.000000 |
| H200 | 10,392 | 1,197 | 9,358 | 1.017668 / 1.333333 | 1.000000 / 1.090909 |
| H800 | 10,343 | 638 | 9,379 | 1.017812 / 1.280000 | 1.000000 / 1.043478 |

- A first audit attempt filtered by short aliases such as `H100` and produced zero rows because the CSV stores full names such as `NVIDIA H100`. The corrected command validated non-empty groups before computing metrics. This was an analysis-script input-label error, not a repository defect.
- Source tracing shows that `tensor_all_ops` is a legacy analytical feature, not a documented hardware profiler counter. The full `gemm_9_calculator.py` formula uses padded M/N/K plus `max(1, cta_count / tile_count)` for non-split Hopper rows and matches the CSV within `rtol=1e-12`, `atol=1e-6` on:
  - H100: `10,363/10,363`
  - H20: `9,534/9,534`
  - H200: `10,392/10,392`
  - H800: `10,343/10,343`
  - Total: `40,632/40,632`
- `analytical_model/gemm_8_calculator.py:42-49` comments out the split-grid divisibility rejection and derives `split_k_slices = max(1, cta_count // tile_count)`. `gemm_9_calculator.py:43-46` uses the same floor-ratio pattern for split-K. These are feature-model heuristics and cannot supply authoritative DES split/reduction metadata.
- No checked-in source establishes `tensor_all_ops` as an Nsight/CUPTI counter. Future measured-counter evidence needs an explicit counter name, collection command, environment, raw samples, and mapping to physical work.

## Current Report Source Facts

- `event_simulator/report.py:78` sets `critical_path=result.makespan`; this is schedule evidence, not a dependency-only longest path.
- `event_simulator/report.py:39-42` sums `event.duration` once for a single optional resource; it cannot represent demand-weighted simultaneous resource usage.
- The future report contract must keep graph proof terms, exact optimum, feasible schedule, and measured evidence separately named.

## Shared Execution Review and Runtime Availability

- StepCode Claude artifact: `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-design-reviewer-revi-2026-07-19T18-37-08-457Z.md`.
- Raw verdict: `APPROVE` for Phase-1 inclusion with WATCH items.
- Accepted: frozen normalized graph boundary, separate ScheduleEntry, one ResourceLifetime concept, two-level GPU topology, explicit dependency ordering, and deliberate removal of the caller-order compatibility behaviors.
- Corrected by the primary lane: dependency acyclicity does not itself eliminate cross-lifetime hold-and-wait; lifetime-held occupancy and transient event-local demand require a stronger contract.
- Corrected by the primary lane: ready-queue operations do not establish total `O((V+E) log V)` behavior once blocked-ready rescans and SM placement checks are included.
- Comparator executables/configurations/traces remain absent from the repository and current host evidence. `nsys` is available at `/usr/local/bin/nsys`; `nvcc`, `ncu`, Accel-Sim, and GPGPU-Sim were not found. `nsys` is not a cycle-accurate simulator.
- A read-only GPU-availability query occurred before re-reading the mandatory GPU handbook during recovery. It established no usable GPU and performed no allocation, workload, Docker, `rlaunch`, or state mutation. This was a process-order error, not a repository defect. The handbook was then read at `/data/ycfeng/stepfun-env-handbook/guidence.md`; every future GPU action must use its verified `rlaunch` recipe and `--predict-only` before a large allocation.

## Cache and GEMM Manifest Review

- StepCode Claude artifact: `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-architecture-reviewe-2026-07-19T18-46-20-917Z.md`.
- Raw verdict: `WATCH` with one requested cache-composition decision.
- Accepted: static cache evidence must be named as manifest-order abstract-model evidence; initial recency/dirty state and size-aware eviction are load-bearing; launch manifests require total problem shape, byte widths, output visibility, explicit worker assignment, K ranges, issued extents, and accumulator topology.
- Corrected: a sequential trace that undercounts misses makes a bound looser, not unsafe. The unsafe direction is a chosen trace with more traffic than the minimum allowed by another schedule when the theorem quantifies over all interleavings.
- Rejected: per-worker isolated cache state is not lower-bound-safe merely because it overcounts misses; higher traffic can raise the resource-work bound above the shared-cache optimum.
- Rejected: a physical partial-line read-modify-write flag is outside the abstract variable-sized modeled-block contract. A final short block is overwritten in full within that abstraction.
- Simplicity decision: use one static manifest-order cache model across exact, SafeBound, scheduler, and report. Do not add a cache-policy enum or parallel cache compositions.

## Cycle-Accurate Comparator Research

- Accel-Sim Framework upstream HEAD observed: `3016c658f810bdae9a14bf4534ee99e9945eedae`.
- GPGPU-Sim distribution upstream HEAD observed separately: `a4ce3feac901c97a4b4601f679e43cf3589c79de`; an approved integration must instead record the exact submodule revision pinned by the selected framework commit.
- Official Accel-Sim README describes SASS trace generation with NVBit, trace-driven detailed simulation through GPGPU-Sim 4.x, PTX mode, hardware correlation, and the need for a real GPU when generating SASS traces.
- Official standard config includes `A100 -> SM80_A100/gpgpusim.config`. The config declares compute capability `8.0`, `108` clusters, tensor cores, caches, interconnect, and DRAM timing. No H100/Hopper entry appeared in the standard config.
- Upstream license is BSD-2-Clause.
- The upstream `get-accel-sim-traces.py` currently points to `ftp://ftp.ecn.purdue.edu/.../1.1.0.trace.summary.txt`; HTTPS redirects to a `404`, so no pre-traced A100 asset is assumed available.
- An unauthenticated GitHub recursive-tree API query failed with HTTP `403` because `X-RateLimit-Remaining: 0` (`60/60` requests used). Direct official raw files remained available and supplied the required config evidence. This was an external API quota condition; no repository fix or retry logic was added.
- Local absence remains: no `accel-sim.out`, GPGPU-Sim checkout, matched trace, `nvcc`, or approved build environment.
- Recommended matched domain if approved: a small versioned A100 synthetic GEMM using the same explicit launch/cache manifest in DES and Accel-Sim. It is not Hopper evidence.
- Focused review artifact: `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-reviewer-for-one-irr-2026-07-19T18-57-46-477Z.md`; raw verdict `APPROVE` with naming/build WATCH items.
- Accepted review boundary: report `GPGPU-Sim cycle-level PTX-mode comparison`, not strict cycle-accurate silicon equivalence.
- Corrected review statement: PTX execution does not remove the toolchain prerequisite. Official GPGPU-Sim instructions require `CUDA_INSTALL_PATH`, CUDA Toolkit headers/math support, and use `nvcc` to compile/link the CUDA benchmark. Current-host `nvcc` absence remains a real provisioning blocker.

## Comparator Approval

- The user selected Option A on 2026-07-20 and approved a version-pinned Accel-Sim/GPGPU-Sim dependency plus a pinned CUDA/`nvcc` build environment.
- Provisioning remains a Phase-2 action after the Phase-1 design checkpoint is reviewed, committed, and pushed.
- The accepted claim name is **GPGPU-Sim cycle-level PTX-mode comparison**. The approval does not change the evidence boundary: no strict silicon cycle-accuracy, Hopper equivalence, or `10000x` result is presumed.
- The integration must verify the framework commit, the GPGPU-Sim submodule revision actually pinned by that commit, the A100 config hash, CUDA/compiler versions, benchmark manifest hash, and exact commands before producing evidence.
