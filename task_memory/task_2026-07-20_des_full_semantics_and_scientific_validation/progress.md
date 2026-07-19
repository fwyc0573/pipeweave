# DES Full Semantics and Scientific Validation Progress

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Recovered the interrupted Wave-3 handoff and completed a fresh pre-commit Wave-1/2 verification gate. |
| 2026-07-20 | Passed the fresh Wave-2 handoff gate and advanced to Wave-3 feasible scheduler/report TDD. |
| 2026-07-20 | Passed the independent Wave-2 Claude proof/code gate with APPROVE and retained only its documented non-blocking WATCH observations. |
| 2026-07-20 | Completed Wave-2 exact/SafeBound GREEN, exhaustive 4,725-case validation, formal proof contract, and measured exact-search benchmark. |
| 2026-07-20 | Recorded the Wave-2 ownership/domain reviews, corrected three test-side defects, and established a clean 76-case proof-layer RED baseline. |
| 2026-07-20 | Closed the bounded Wave-1 Claude correction review, completed the numeric Wave-1 report, and advanced to Wave 2. |
| 2026-07-20 | Passed the Wave-1 StepCode Claude APPROVE gate, reconciled its two WATCH items, and expanded focused shared-kernel coverage to 76 cases. |
| 2026-07-20 | Established the 40-case Wave-1 RED baseline, implemented the minimal shared kernel, and reached 41 focused GREEN tests including dependency canonicalization. |
| 2026-07-20 | Entered Phase 2 Wave 1, observed the initial RED collection failure, and corrected the test-fixture construction boundary before production changes. |
| 2026-07-20 | Diagnosed and corrected a pre-commit trailing-whitespace failure in the Phase-1 test report without weakening the validator. |
| 2026-07-20 | Passed Phase-1 document validation and fresh 141-test regression after resolving the known missing-GNU-time environment issue. |
| 2026-07-20 | Passed the complete independent Phase-1 Claude design gate and reconciled its low-severity test-path, float, and scheduler-complexity WATCH items. |
| 2026-07-20 | Captured comparator Option A and completed the calibration, held-out, theorem, and executable GSD Phase-1 design freeze. |
| 2026-07-20 | Completed focused Claude review of the comparator choice and corrected its PTX toolchain assumption against official GPGPU-Sim docs. |
| 2026-07-20 | Researched official comparator support, identified Accel-Sim A100, and recorded the dependency approval blocker and GitHub API quota failure. |
| 2026-07-20 | Selected the dependency-free serial SGS exact oracle and recorded its self-contained completeness and independent-cross-check obligations. |
| 2026-07-20 | Reconciled the cache/GEMM-manifest Claude WATCH and selected a single manifest-order static-cache model. |
| 2026-07-20 | Recovered and reconciled the shared execution-kernel Claude review, correcting lifetime progress and total-complexity claims. |
| 2026-07-20 | Corrected `tensor_all_ops` provenance after source/formula tracing and reopened authoritative measured-counter evidence for R8/R11. |
| 2026-07-20 | Recorded the exact-engine Claude review, detected its arithmetic defect, ran a correction review, and retained a proof-gated WATCH recommendation. |
| 2026-07-20 | Recorded the user's Option A decision and the corrected split-K, partial-tile, and report-provenance audits. |
| 2026-07-20 | Added the centralized E0–E7 experiment protocol with raw evidence, numeric metrics, planned test locations, and claim boundaries. |
| 2026-07-20 | Recorded the exact-solver dependency audit and successful numeric SciPy/HiGHS API smoke without selecting or adding a dependency. |
| 2026-07-20 | Recorded the preliminary StepCode Claude WATCH, source-level reconciliation, accepted findings, and rejected unsupported recommendations. |
| 2026-07-20 | Recorded the completed independent parent-gate and scientific-evidence audits with quantified coverage and blockers. |
| 2026-07-20 | Initialized the continuation log with branch recovery, parent-contract recovery, baseline verification, and phase-1 documentation creation. |

## Status

- Overall: In progress.
- Current phase: Phase 2 Wave 3 — feasible scheduler and report TDD.
- Completed: Phase-1 design checkpoint; Wave-1 shared kernel; Wave-2 exact oracle and SafeBound proof layer; focused tests, proof audits, benchmarks, and mandatory Claude reviews.
- In progress: reviewed Wave-1/2 checkpoint commit and push before Wave-3 behavior changes.
- Pending: Waves 3–5, scientific evaluation, final review, full regression, delivery commit, and final push.

## Session Log

### 2026-07-20 — Continuation recovery and branch verification

- **Motivation:** Resume after interruption without repeating completed remediation or beginning a broad implementation from stale assumptions.
- **Expectation:** Confirm the exact branch checkpoint, clean workspace, parent contracts, and current regression baseline before designing the next stage.
- **Method:** Verified `des` against `origin/des`, read the parent `design.md`/`harness.md` and SafeBound handoff, inspected the current implementation and evidence boundaries, and ran the full repository tests with bytecode/cache writes disabled.
- **Result:** Local and remote both resolve to `d596e1bd7f5cb8e12e4d1034ad4be51c37ae248b`; the baseline passed `141/141` tests in `7.82s` (`8.979s` wrapper elapsed); no production code was changed.

### 2026-07-20 — New task-contract initialization

- **Motivation:** The requested work is a new large-scale scientific/modeling stage and must not be appended to the completed bounded SafeBound task.
- **Expectation:** Create one non-redundant source of truth for raw intent, design gates, evidence, progress, and unresolved questions.
- **Method:** Created `task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/` with the required task taxonomy plus one requirement-to-evidence matrix. Captured all twelve requested outcomes and the two-phase/review/simplicity constraints.
- **Result:** Phase 1 has a durable draft contract. Production code remains frozen pending discussion and independent Claude design review.

### 2026-07-20 — Independent parent-gate and scientific-evidence audits

- **Motivation:** Prevent the twelve outcomes from silently reopening the completed SafeBound task or relying on evidence that the repository does not contain.
- **Expectation:** Map every outcome to inherited gates, quantify available multi-hardware coverage, and identify external prerequisites before discussion decisions.
- **Method:** Ran independent read-only context and evidence lanes over parent task artifacts, SafeBound artifacts, source, validators, hardware files, datasets, E2E data, and benchmark surfaces. No production file, test output, GPU, Docker, network, or ignored path was touched.
- **Result:** The twelve outcomes are confirmed as a new umbrella architecture/science task. The dataset has `118,800` GEMM rows across `11` hardware names, but only `15,164` rows across four Hopper devices satisfy the current policy. No named cycle-accurate comparator or measured primitive-calibration campaign exists. These facts are now explicit design/evaluation gates rather than hidden assumptions.

### 2026-07-20 — Preliminary StepCode Claude challenge and reconciliation

- **Motivation:** Continue decision-independent Phase 1 progress while the first user semantic decision is pending, and satisfy the independent cross-model gate for a key architecture question.
- **Expectation:** Challenge the A/B/C exact-bound decision tree, identify minimal proof/API boundaries, and expose premature assumptions without authorizing code.
- **Method:** Ran `omx ask claude` through StepCode Claude Opus 4.6 at effort `max` with the parent contracts, all twelve outcomes, current source/data facts, and requested review questions. Then inspected `events.py`, `resources.py`, `scheduler.py`, `safe_bound.py`, `operators.py`, `structural.py`, and the focused scheduler/SafeBound tests to adjudicate the response.
- **Result:** Claude returned **WATCH** for continuing Phase 1 and recommended Option A. The task accepted the separation of exact oracle, scalable bound, feasible schedule, and measured evidence. It rejected unapproved OR-Tools adoption, arbitrary `500`-event/`60s` limits, a mutable evidence dictionary, an inapplicable scheduler approximation claim, cold-state safety over warm-state workloads, and scope-shrinking deferrals. Production code remains frozen.

### 2026-07-20 — Exact-solver environment and algorithm feasibility audit

- **Motivation:** Replace speculative solver recommendations with current-host evidence while the mathematical A/B/C decision remains pending.
- **Expectation:** Determine which solver APIs already exist, whether the repo declares them, and what evidence an exact result can actually expose.
- **Method:** Inspected packaging files and Python-only solver references, queried module metadata without installing anything, and ran a two-variable integer problem through `scipy.optimize.milp` with bytecode writes disabled.
- **Result:** No project dependency file or solver import exists. SciPy `1.17.1` is available, while OR-Tools, direct `highspy`, PuLP, and Z3 are unavailable. The smoke returned status `0`, objective `2.0`, solution `[0.0, 2.0]`, and `mip_gap=0.0`. This establishes API feasibility only. The design now requires explicit dependency approval, a proved scheduling formulation, and exhaustive tiny-case cross-checking before any solver can support an exactness claim.

### 2026-07-20 — Centralized experiment and evidence protocol

- **Motivation:** Prevent twelve implementation slices from defining inconsistent metrics or using narrow tests to support broad scientific claims.
- **Expectation:** Give every requested outcome a planned authoritative test location, raw evidence schema, numeric metrics, and acceptance boundary before code begins.
- **Method:** Consolidated the parent harness, independent evidence audit, source constraints, and preliminary Claude review into E0–E7 protocols for bound/oracle, scheduler, cache, execution semantics, cycle-accurate comparison, zero-shot, primitive calibration, and universal-claim audit.
- **Result:** `experiments.md` now specifies the values that must be compared, unsupported/violation accounting, external prerequisites, and modeled-versus-hardware claim separation. It is design-only; no script or production behavior was added.

### 2026-07-20 — Option A decision capture

- **Motivation:** Resolve the first blocking ambiguity without allowing one numeric result to carry incompatible exactness, scalability, feasibility, and hardware-evidence claims.
- **Expectation:** Freeze the provenance split while leaving algorithms and APIs open for the remaining design review.
- **Method:** Captured the user's explicit “选择a” follow-up in `requirements.md` and reconciled the design, issue register, plan, and requirement matrix.
- **Result:** The task now requires separate exact modeled optimum, scalable SafeBound, deterministic feasible schedule, and measured-hardware comparison layers. FSV-001 is resolved; production code remains frozen because the exact engine and execution/evidence semantics remain open.

### 2026-07-20 — Split-K, partial-tile, and report audit

- **Motivation:** Prevent heuristic launch reconstruction and useful-work-only counters from entering the design as unreviewed assumptions.
- **Expectation:** Determine whether current CSV metadata uniquely defines split-K and whether a padded-tile work formula is supported strongly enough to become a candidate rather than a universal rule.
- **Method:** Audited all `118,800` GEMM rows using `is_split_k`, CTA/base-grid ratios, tile shapes, and `tensor_all_ops`; inspected `event_simulator/report.py`. The first partial-tile query incorrectly used short hardware aliases and returned zero rows; the corrected query used the CSV's full `NVIDIA ...` names and asserted non-empty groups.
- **Result:** CTA ratios do not uniquely recover split factor or persistent grouping; H20 includes `85` split-K rows with fewer CTAs than the base grid. Padded-tile FLOPs equal the counter on `9,202–9,379` rows per Hopper target and have median ratio `1.0`, but p95 residuals remain up to `1.090909`. The design now separates logical, physical-issued, and counter-observed work and records that current report `critical_path` is actually scheduled makespan. No production code changed.

### 2026-07-20 — Exact-engine independent review and correction

- **Motivation:** Select the smallest trustworthy exact oracle without adding an undeclared solver or building redundant validation machinery.
- **Expectation:** Obtain an independent recommendation, exact semantic boundary, proof obligation, minimal result contract, and falsifying RED cases.
- **Method:** Ran StepCode Claude twice at effort `max`. After the first review returned `APPROVE + WATCH`, manually traced its three-event example and found the claimed optimum `7` ignored the long event's resource completion; the correct value is `8`. A focused correction pass supplied a valid optimum-`6` example and reissued `APPROVE`. Crossref confirmed the cited Kolisch paper identity and DOI, but no accessible theorem text was treated as proof.
- **Result:** Standard-library exhaustive serial SGS remains the leading engine because it matches the small-oracle role and avoids dependency/formulation duplication. The review is recorded as WATCH until the user selects it and a self-contained proof covers the final float-time, simultaneous-demand, tie, and zero-duration domain. Claude's `int` makespan, mutable/dict witness, nested statistics, global zero-duration rule, and inconsistent active-schedule statement were not adopted. No production code changed.

### 2026-07-20 — Analytical-feature versus measured-counter correction

- **Motivation:** Prevent a checked-in legacy model feature from being cited as hardware proof for partial-tile or calibration semantics.
- **Expectation:** Trace `tensor_all_ops` to its producer and determine whether the residual against a simple padded formula is measured behavior or another analytical term.
- **Method:** Searched all source references, inspected `gemm_8_calculator.py`, `gemm_9_calculator.py`, `aggregator.py`, and `pipes.py`, and recomputed the complete non-split Hopper formula including CTA-derived replication.
- **Result:** The full formula matches `40,632/40,632` rows within `rtol=1e-12`, `atol=1e-6`; `tensor_all_ops` is analytical feature data. The earlier counter interpretation was corrected in all active design/evidence artifacts. The legacy floor-ratio split heuristic is explicitly disallowed for DES. Measured issued work remains an external R8/R11 evidence requirement. No production code changed.

### 2026-07-20 — Shared execution-kernel review reconciliation

- **Motivation:** Complete the interrupted Phase-1 review of the common graph/resource/lifetime/scheduler boundary without copying current bugs or accepting overconfident external reasoning.
- **Expectation:** Keep only the minimum distinct concepts, establish caller-order-invariant execution semantics, and identify any unproved feasibility or performance claim before code begins.
- **Method:** Recovered the completed StepCode Claude artifact from session `83038`, read the full response, and checked every recommendation against `events.py`, `resources.py`, `scheduler.py`, `safe_bound.py`, `report.py`, FA lowering, current tests, the parent contracts, and resource-scheduling counterexamples.
- **Result:** Claude returned `APPROVE` with WATCH items. The design accepted Event/EventGraph/ScheduleEntry/ResourceLifetime separation, two topology levels, explicit dependencies, and deliberate compatibility breaks. It corrected two review defects: an acyclic DAG does not by itself prevent cross-lifetime hold-and-wait, and priority-queue bookkeeping does not prove total `O((V+E) log V)` multi-resource scheduling. The corrected lifetime-progress and complexity-accounting gates are recorded. Production code remains frozen.

### 2026-07-20 — Cache and GEMM manifest review reconciliation

- **Motivation:** Freeze warm-L2, initial-residency, persistent-worker, split-K, reduction, and partial-tile semantics without inventing launch policy or duplicating proof/execution models.
- **Expectation:** Obtain an independent challenge of the smallest static cache and launch-manifest contract, then verify the lower-bound direction and concept count against the harness.
- **Method:** Ran StepCode Claude Opus 4.6 at effort `max` on the explicit HBM+L2 LRU candidate and authoritative GEMM launch manifest. Evaluated its `WATCH` response against cache-state mathematics, the fixed-duration proof boundary, the no-fallback rule, and the simplicity requirement.
- **Result:** The design adopted one manifest-order static cache model with explicit initial LRU/dirty state, size-aware blocks, deterministic transitions, output visibility, and immutable resolution evidence. It adopted explicit worker/K-partition/reduction manifests and derived logical/physical work. It rejected the review's isolated-worker cache alternative because overcounted traffic is not lower-bound-safe, and rejected physical partial-line metadata outside the abstract block model. Production code remains frozen.

### 2026-07-20 — Exact-oracle engine selection and proof freeze

- **Motivation:** Remove the final engine ambiguity without adding an undeclared dependency or treating a solver status as a model proof.
- **Expectation:** Select the smallest exact verification oracle, state its complete supported domain, and provide a project-specific coverage argument that can drive RED tests.
- **Method:** Reconciled both prior Claude passes, the corrected hand examples, RCPSP serial-SGS dominance reasoning, current float Event semantics, simultaneous integer demands, half-open zero-duration intervals, and the no-arbitrary-limit requirement.
- **Result:** Phase 1 selects exhaustive standard-library serial SGS over all precedence-feasible permutations. `design.md` records feasibility, active-optimum existence, reproduction by start-time/topological order, and complete-search optimality. A caller budget may abort only by raising with no result. Initial GREEN has no pruning and must match an independent bounded time-grid enumeration on tiny integer cases. No dependency or production code changed.

### 2026-07-20 — Cycle-accurate comparator source audit

- **Motivation:** Replace the vague missing-comparator blocker with one named, versionable candidate and a truthful matched domain before requesting dependency approval.
- **Expectation:** Establish official simulator/config support, hardware scope, trace/toolchain prerequisites, and whether existing pre-traced assets can be assumed.
- **Method:** Queried upstream Git refs and official raw README/config/license files for Accel-Sim and GPGPU-Sim without cloning, installing, building, using GPU/Docker, or changing production code. Diagnosed one GitHub API failure from its response headers rather than retrying blindly.
- **Result:** Accel-Sim/GPGPU-Sim has an official A100 `SM80` detailed configuration and no observed H100/Hopper standard configuration. The pre-trace summary URL redirects to `404`; local simulator/compiler assets are absent. One recursive-tree request returned HTTP `403` with API quota `0/60`; direct raw evidence succeeded. The recommended R9 domain is a pinned synthetic A100 GEMM, but fetching/building the new dependency requires explicit user approval.

### 2026-07-20 — Comparator decision Claude review and correction

- **Motivation:** Independently challenge the only source-backed external dependency before asking the user to approve an irreversible build/toolchain commitment.
- **Expectation:** Verify comparator naming, PTX-versus-SASS scope, synthetic-manifest authority, required match keys, and build risk without inflating the claim.
- **Method:** Ran StepCode Claude Opus 4.6 at effort `max` with official A100 configuration facts and the proposed synthetic matched benchmark. Then checked its PTX toolchain statement against the official GPGPU-Sim installation/run instructions.
- **Result:** Claude returned `APPROVE` with WATCH and supports a narrowly named GPGPU-Sim cycle-level PTX-mode A100 comparison. Its claim that `nvcc` absence is irrelevant was rejected: official instructions require CUDA Toolkit support and an `nvcc`-compiled CUDA executable. User approval must therefore cover simulator plus pinned compiler/CUDA build environment. No dependency was fetched or installed.

### 2026-07-20 — Comparator approval and Phase-1 semantic freeze

- **Motivation:** Resume at the interrupted design checkpoint, apply the user's comparator Option A decision, and eliminate stale/open wording before any production change.
- **Expectation:** Freeze calibration/zero-shot/non-zero-shot separation, exact modeled theorem quantifiers, user-approved comparator scope, file ownership, TDD commands, and wave gates without adding defensive or redundant modules.
- **Method:** Re-read the parent contracts, all current task artifacts, Event/resource/scheduler/report/operator source, focused tests, and prior Claude artifacts. Captured the user decision, reconciled every formerly open semantic issue, specified the SafeBound terms and relaxation proof, fixed four Hopper folds, and assigned one invariant owner to each production/test surface.
- **Result:** Wave 0 is fully resolved. The GSD plan now has exact entry/exit invariants and reproducible commands. Accel-Sim/GPGPU-Sim plus pinned CUDA/`nvcc` is approved for Phase 2, but no dependency or production code has been touched. The next mandatory action is the complete independent Phase-1 Claude gate.

### 2026-07-20 — Complete Phase-1 independent design gate

- **Motivation:** Satisfy the independent cross-model gate before checkpointing the architecture and beginning production implementation.
- **Expectation:** Receive `APPROVE` or bounded `WATCH`, identify proof/API/test drift, and prevent redundant or over-defensive modules from entering Phase 2.
- **Method:** Ran StepCode Claude Opus 4.6 at effort `max` over both parent contracts, every active task artifact, all `event_simulator` source, and focused tests. Reconciled the response rather than applying it blindly.
- **Result:** Claude returned **APPROVE** with no blocker. It accepted the exact proof, SafeBound inequalities/relaxations, lifetime progress rule, cache/manifest design, evidence separation, comparator label, and GSD executability. The only concrete drift was duplicate candidate test filenames; E0 now uses the same ownership paths as `plan.md`. Binary-float and scheduler-complexity WATCH items remain explicit verification gates. Production code is still unchanged.

### 2026-07-20 — Phase-1 checkpoint validation and timing-tool resolution

- **Motivation:** Produce fresh evidence before claiming the Phase-1 design is ready to commit and push.
- **Expectation:** Validate the task taxonomy/contracts and pass the full `141`-test regression without modifying production code.
- **Method:** Ran an inline document-contract validator and the complete pytest suite with bytecode/cache writes disabled. The first wrapper referenced absent GNU `/usr/bin/time`, so pytest did not start. Read `task_memory/env_handbook.md`, confirmed Bash's `time` keyword, and reran with the handbook's verified `TIMEFORMAT` command.
- **Result:** Document validation passed with `13/13` required files, `22` original-request tags, `5/5` review fields, and `0` stale duplicate E0 test paths. The rerun passed `141/141` tests in pytest `3.47s`, Bash elapsed `3.965s`, user `4.426s`, system `0.124s`, exit code `0`. The initial wrapper failure was environment-only and is documented in the Phase-1 test report. Production source changes remain `0`.

### 2026-07-20 — Pre-commit trailing-whitespace correction

- **Motivation:** Enforce artifact integrity before committing the Phase-1 checkpoint.
- **Expectation:** The current task documents and staged diff contain zero trailing whitespace.
- **Method:** Ran the inline document validator and `git diff --cached --check`. Both identified lines 9–11 of the new test report. Inspected the exact lines and found Markdown two-space hard breaks.
- **Result:** Replaced the hard-break spaces with blank-line separation and retained the strict validator. The failed staged state was not committed. A complete document/test/staged-diff rerun is required next.

### 2026-07-20 — Wave-1 initial RED collection failure and root-cause correction

- **Motivation:** Begin the shared `EventGraph`/resource-kernel implementation with personally observed RED evidence and no production edits.
- **Expectation:** Collect both new Wave-1 test modules and observe ordinary failures caused by the missing `EventGraph`, `ResourceLifetime`, and two-level resource APIs.
- **Method:** Ran `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider tests/unit/test_event_graph.py tests/unit/test_resource_semantics.py -q`, inspected both stack traces, and traced object construction to module-level `pytest.mark.parametrize` arguments.
- **Result:** The first run exited `2` with `2` collection errors: `Event.__init__()` rejected `lifetime_id` and `global_demand` while importing the test modules. The root cause was eager construction of the new API in parameter tables, not a production defect beyond the intentionally missing feature. Parameter tables now carry plain specifications and construct objects inside test bodies. The fresh rerun collected all cases and exited `1` with `40 failed`, `0` collection errors, and failures caused by the intentionally missing `EventGraph`, `ResourceLifetime`, new `Event` fields, and two-level `ResourceConfig`. This is the accepted Wave-1 RED baseline; production code remains unchanged.

### 2026-07-20 — Wave-1 minimal shared-kernel GREEN

- **Motivation:** Establish the single graph/resource semantic boundary required by every later proof, scheduler, cache, and lowering wave without preserving rejected legacy fields or adding a parallel model.
- **Expectation:** Make the authored EventGraph/resource tests pass with immutable unscheduled Events, canonical explicit dependencies, one normalized EventGraph, two-level capacities, lifetime membership validation, and no cross-lifetime occupancy demand.
- **Method:** Implemented `EventGraph` and the new `Event` contract in `event_simulator/events.py`; implemented `ResourceLifetime` and the two-level `ResourceConfig.validate_graph()` boundary in `event_simulator/resources.py`; exported the two public types; used `MappingProxyType`, canonical ordering, one-way type-only imports, and linear acyclicity traversal. After the initial 40-case GREEN, added a focused dependency-canonicalization case, observed it fail because a mutable list remained attached, then normalized dependencies to a sorted tuple.
- **Result:** The initial valid RED was `40 failed`; the first GREEN was `40 passed`; the added canonicalization RED was `1 failed`; the final focused run passed `41/41` in `0.80s` with exit code `0`. `git diff --check` passed for the changed shared-kernel/test/progress paths. Scheduler, exact, cache, manifest, and empirical behavior were not implemented in this slice.

### 2026-07-20 — Wave-1 independent code gate and coverage expansion

- **Motivation:** Satisfy the mandatory post-module `ask Claude` gate, avoid over-defensive lifetime restrictions, and cover the changed validation branches before handing the shared kernel to the proof layer.
- **Expectation:** Receive an independent `APPROVE`, bounded `WATCH`, or `BLOCK`; preserve the frozen public API and assign any scheduler-only risk to the scheduler wave rather than patching it into graph validation.
- **Method:** Ran `omx ask claude` through StepCode Claude Opus 4.6 at effort `max` against both parent contracts, the current task design/harness/plan, the actual shared-kernel diff, and RED/GREEN evidence. Reconciled artifact `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-code-reviewer-for-pi-2026-07-19T19-42-58-403Z.md`. Expanded focused tests for scalar failures, dependency containers, mutable-input detachment, empty graphs, zero-duration/nonzero-demand semantics, immutable graph maps, lifetime canonicalization, capacity schemas, and lifetime value branches.
- **Result:** Claude returned **APPROVE** with no blocker. W-1 records the intentional old-caller break until Waves 2–4; no adapter is allowed. W-2 assigns the external-event/same-occupancy placement case to an explicit Wave-3 RED and runtime no-progress handling, not a blanket Wave-1 rejection. A post-review string-dependency RED failed `1/1` because `"ab"` was silently interpreted as two IDs; the minimal fix now rejects string/bytes containers. The expanded focused suite passes `76/76` in `0.83s`. A short correction review is required because that final fail-fast fix postdates the main Claude artifact.

### 2026-07-20 — Wave-1 bounded correction review and handoff

- **Motivation:** Close the independent-review gap created when the final string/bytes dependency-container fix landed after the main shared-kernel Claude review.
- **Expectation:** Confirm that the post-review delta remains minimal, that the 76-case expansion is non-redundant, and that no unresolved finding blocks Wave 2.
- **Method:** Recovered the already-running `omx ask claude` session instead of launching a duplicate review, then reconciled artifact `.omx/artifacts/claude-this-is-a-bounded-correction-pass-for-your-pipeweave-phase-2-2026-07-19T19-48-58-214Z.md` against the actual diff, parent/current design and harness, and existing WATCH assignments.
- **Result:** StepCode Claude returned **APPROVE**. It confirmed that the only production delta is the two-line fail-fast guard, each added test covers a distinct branch, the simplicity gate remains satisfied, and prior W-1/W-2/W-3 dispositions are unchanged. Wave 2 is authorized.

### 2026-07-20 — Wave-1 fresh verification and style-audit correction

- **Motivation:** Produce current numeric evidence and a reproducible Wave-1 test report before changing proof-layer code.
- **Expectation:** Pass all 76 focused tests, report zero newly added Python lines over 88 characters, and pass `git diff --check`.
- **Method:** Ran the focused suite under Python 3.12.3/pytest 9.1.1 with Bash timing. The first style helper scanned every line of every modified file and reported two long imports in `event_simulator/__init__.py`; Git comparison showed both lines already existed at `HEAD`. Re-ran the intended diff-added-line audit rather than editing unrelated legacy formatting or weakening the criterion.
- **Result:** Pytest passed `76/76` in `1.05s` with Bash elapsed `1.539s`; added Python lines over 88 characters were `0`; `git diff --check` returned exit code `0`. The initial whole-file style helper's exit code `1` was a validation-scope defect, not a product defect, and is recorded in the Wave-1 test report.

### 2026-07-20 — Wave-2 result-type ownership and per-SM exact-domain reviews

- **Motivation:** Resolve two narrow proof-layer ownership questions without duplicating schedule witness types, prematurely rewriting scheduler behavior, or calling an aggregate per-SM relaxation exact.
- **Expectation:** Freeze the smallest design-consistent `ScheduleEntry` introduction and a sound per-SM exact-oracle domain before production implementation.
- **Method:** Ran two read-only StepCode Claude Opus 4.6 reviews at effort `max`. The first compared placing `ScheduleEntry` in `scheduler.py` against a temporary oracle-local type, `events.py`, and a new shared module. The second compared rejecting, aggregating, or explicitly placing multi-SM demand. A bounded correction review then rechecked the counterexample arithmetic.
- **Result:** Claude returned **APPROVE** for adding only the frozen `ScheduleEntry` value type to `scheduler.py` in Wave 2 while leaving `schedule()`, `_validated_dependencies()`, and `SimulationResult` untouched. The exact oracle accepts per-SM demand only when `sm_count == 1`; for `sm_count > 1`, any nonzero per-SM demand fails fast while global-only and explicit-zero demand remain supported. The correction returned **WATCH** because the original review wrote `2/3`; the correct aggregate SafeBound is `6 / 6 = 1.0`, aggregate-pool optimum `1.0`, and true placement optimum `2.0`. The proof/rejection boundary remains valid. The result witness field is `entries`, matching the frozen immutable witness-tuple wording and authored tests; no `schedule` alias or compatibility duplication will be added.

### 2026-07-20 — Wave-2 test-fixture correction and clean RED

- **Motivation:** Separate test-construction and arithmetic defects from the intentionally missing proof-layer implementation before writing production code.
- **Expectation:** Collect all Wave-2 tests with no warnings and observe ordinary failures caused only by missing `ScheduleEntry`/exact-oracle APIs and the old SafeBound interface.
- **Method:** Materialized the `itertools.product(...)` parameter values to satisfy pytest's collection contract; recomputed the permutation case as `short 0–2`, `long 2–6`, `tail 2–5`, so the optimum is `6.0`; included the independent duration-`10` Event in the critical-path maximum. Re-ran the four-file focused suite with bytecode and pytest cache disabled.
- **Result:** The corrected suite collected normally and reported `76 failed`, `0` collection errors, `0` warnings, exit code `1`, pytest time `1.29s`, and wrapper elapsed `1.684990352s`. Failures are concentrated in absent `ExactScheduleResult`, `ScheduleEntry`, `solve_exact_schedule`, `IncompleteExactSearchError`, and the old single-argument `SafeBoundEvaluator.evaluate()` API. Production proof-layer code remains unchanged at this RED checkpoint.

### 2026-07-20 — Wave-2 exact-oracle and SafeBound GREEN

- **Motivation:** Implement the smallest proof layer that returns exact evidence only after complete search and computes only individually proven, order-invariant analytical terms.
- **Expectation:** Pass all exact and SafeBound tests without modifying legacy scheduler behavior, adding a duplicate schedule type, introducing pruning, or conflating proof and simulation results.
- **Method:** Added only frozen `ScheduleEntry` data ownership to `scheduler.py`; implemented precedence-feasible permutation enumeration and earliest-insertion serial SGS in `exact_oracle.py`; implemented dependency critical path, chip-global resource conservation, aggregate per-SM conservation, immutable mappings, and named relaxation evidence in `safe_bound.py`; exported the four new public proof-layer symbols. The exact-only run passed `24/24`. The first SafeBound run exposed one implementation defect: with no resource terms, positional `max` received one float and treated it as an iterable.
- **Result:** The root cause was fixed by passing one tuple containing all proof terms, without adding a special-case branch or fallback. The failed SafeBound attempt reported `4 failed, 48 passed`; the rerun passed `52/52` in `0.82s`. The combined Wave-2 suite passed `76/76` in `0.93s` (wrapper `1.319273480s`), and the Wave-1+2 regression passed `152/152` in `1.06s` (wrapper `1.432078337s`). Legacy `schedule()` behavior is unchanged and remains assigned to Wave 3.

### 2026-07-20 — Wave-2 exhaustive proof audit and search scaling

- **Motivation:** Meet the exit invariant with an oracle independent of serial SGS and quantify the practical exponential search boundary instead of inventing a default event-count or time limit.
- **Expectation:** Obtain zero exact mismatches, zero SafeBound violations, zero permutation/conservation/monotonicity failures, and explicit complete/incomplete search timings.
- **Method:** Exhausted capacities `{1, 2}`, three independently selected durations in `{0, 1, 2}`, every integer demand through capacity, and five DAG shapes. Compared the production oracle against bounded integer start-assignment enumeration; repeated every case under all six input permutations; checked conservation and all one-step duration/demand monotonic neighbors. Generated `safe_bound_oracle_cases.json`, wrote `formal_bound_contract.md`, and benchmarked independent graphs through `9!` permutations, a resource-serial eight-Event graph, a 128-Event chain, and explicit budget exhaustion.
- **Result:** Validation passed `4,725/4,725` cases, `28,350` permutations, and `18,360` monotonicity comparisons with every failure count `0`, maximum exact delta `0.0`, and case-record SHA-256 `5e173514000270d7c5d2a504b1adcd9d62f9285ee6d12819a48397c63724da67`. Independent `9! = 362,880` complete search took `8.757123135s`; resource-serial `8! = 40,320` took `5.286754904s`; a 128-Event/127-edge chain took `0.001141802s`; a 1,000-permutation budget raised incomplete with no result in `0.023271485s`. The Wave-2 Claude proof-layer gate remains pending.

### 2026-07-20 — Wave-2 independent code/proof APPROVE gate

- **Motivation:** Obtain the required independent cross-model check before treating exactness, SafeBound safety, or the proof/simulation boundary as a completed module milestone.
- **Expectation:** Detect any proof/code mismatch, incomplete-search leak, unsafe relaxation, duplicate type/API, over-defensive validation, or premature scheduler migration; treat any hard exactness/safety defect as BLOCK.
- **Method:** Ran StepCode Claude Opus 4.6 at effort `max` over both parent contracts, every Wave-2 source/test/evidence artifact, the formal proof, generated JSON summary, benchmark, and numeric test report. Reconciled the raw review against the actual implementation rather than applying suggestions automatically.
- **Result:** Claude returned **APPROVE** with no blocker. It confirmed complete-search/budget semantics, half-open multi-resource feasibility, truthful one-SM/multi-SM domain rejection, SafeBound term/relaxation safety, provenance separation, test independence, one shared ScheduleEntry, and unchanged legacy scheduler behavior. Four minor observations require no code change: the endpoint proof is already documented; recursive sorting is accepted deterministic overhead; the tuple `max` fix is correct; and integer-grid exhaustive evidence is explicitly a subdomain of the float proof. Fresh handoff verification remains before Wave 3.

### 2026-07-20 — Wave-2 fresh handoff completion

- **Motivation:** Close the proof-layer milestone with evidence generated after the independent review and before any scheduler behavior changes.
- **Expectation:** Reconfirm shared-kernel/proof regression, generated-case integrity, required task artifacts, added-line style, and diff cleanliness.
- **Method:** Re-ran the six Wave-1+2 test modules, regenerated the exhaustive proof corpus, validated all required task files and Modification History sections, recomputed the case-record digest, audited added Python lines, and ran `git diff --check` while excluding only the permanently ignored `=10.1` path.
- **Result:** `152/152` tests passed in `0.99s` (wrapper `1.429912324s`); `4,725/4,725` cases, `28,350` permutations, and `18,360` monotonicity checks passed with all failure counts `0`; `17/17` required artifacts exist; digest remained `5e173514000270d7c5d2a504b1adcd9d62f9285ee6d12819a48397c63724da67`; added long Python lines were `0`; `git diff --check` exited `0`. Wave 2 is complete and Wave 3 is active.

### 2026-07-20 — Interruption recovery and Wave-1/2 pre-commit gate

- **Motivation:** Resume at the exact Wave-3 interruption point while honoring the user requirement to organize, commit, and push the already reviewed checkpoint before any next-stage behavior change.
- **Expectation:** Reconfirm that the local branch matches `origin/des`, the dirty set contains only the reviewed Wave-1/2 implementation/evidence, all phase tests and independent proof checks still pass, and no ignored-path operation occurs.
- **Method:** Compared local `HEAD` with `origin/des`; inspected status/diff using `:(exclude)=10.1`; re-read the parent/current design, harness, plan, progress, issues, and review contracts; ran the six-module regression, exhaustive exact/SafeBound validator, exact-search benchmark, 17-artifact check, 15-file AST parse, added-line audit, and `git diff --check`. Two initial wrapper constructions failed before executing repository commands: one shell task variable was not assigned inside the command, and one JavaScript template interpolated a shell timing variable. Both orchestration defects were corrected without changing source or test behavior. The first staged diff gate then exposed three Markdown trailing-space errors in the previously untracked Wave-2 report; the hard-break spaces were removed directly and the staged gate was rerun.
- **Result:** Local and remote started at `96f94c7b20349fb11bf8c4669c8d9d618704d5f6`. The fresh regression passed `152/152` in `0.99s` (`1.367510628s` wrapper); validation passed `4,725/4,725` cases, `28,350` permutations, and `18,360` monotonicity checks with every failure count `0` in `4.134851064s`; the benchmark completed in `14.896103679s`, including `9! = 362,880` permutations in `8.494442112s`, resource-serial `8! = 40,320` in `5.264503544s`, and explicit incomplete-search failure in `0.033102431s`. All `17/17` artifacts existed, all `15/15` Python files parsed, and added long lines were `0`. The initial staged diff check failed on exactly `3` report metadata lines; after the root-cause correction, the final staged `git diff --check` returned `0` across `23` paths, with `0` ignored paths staged.
