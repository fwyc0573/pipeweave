# DES Full Semantics and Scientific Validation Progress

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Committed and pushed the Wave-4 checkpoint at `350159313aa3a018700e648bce7ca5e842a34e07`, verified remote equality, and opened Wave 5. |
| 2026-07-20 | Passed the first 25-path explicit staging and 54-entry index-hash audit with no ignored, OMX, unstaged, untracked, or diff findings. |
| 2026-07-20 | Passed the fresh 147/400/4,725 pre-staging regressions and the corrected final static gate; documented the checker-only `__future__` false positive. |
| 2026-07-20 | Rebuilt and verified the 54-entry Wave-4 checksum inventory and passed the final independent Claude delivery-package APPROVE/READY gate without production changes. |
| 2026-07-20 | Passed the 400-test full regression and exhaustive proof validator, resolved one added-line static failure, and produced the numeric Wave-4 test report. |
| 2026-07-20 | Passed the Wave-4 post-implementation Claude gate, closed both actionable coverage WATCH items, removed only newly orphaned imports, and reached 147 focused passes. |
| 2026-07-20 | Completed the Wave-4 operator/hardware/validator minimal GREEN and recorded the 145-case focused evidence plus the resolved calibration rename defect. |
| 2026-07-20 | Completed Wave-4 tests-only API migration and established the 145-case clean behavior RED baseline. |
| 2026-07-20 | Recorded the legacy-fixture collection RED and the independent lowering-design APPROVE gate before tests-only migration. |
| 2026-07-20 | Passed the independent manifest-module review, closed its two meaningful coverage findings, and advanced to operator lowering. |
| 2026-07-20 | Completed the first `GemmLaunchManifest` RED/GREEN cycle, corrected one test-fixture ownership defect, and reached the pre-review verification gate. |
| 2026-07-20 | Passed the independent cache-module review and closed both optional branch-coverage findings with 33 passing cache tests. |
| 2026-07-20 | Completed cache RED/GREEN, public export TDD, focused regression, and corrected static-check evidence before independent review. |
| 2026-07-20 | Recovered the interrupted Wave-4 context and revalidated the 205-case Wave-1--3 entry invariant. |
| 2026-07-20 | Committed and pushed the Wave-3 checkpoint, verified remote SHA equality, and entered Wave 4. |
| 2026-07-20 | Corrected benchmark CSV line-ending ownership through TDD and expanded the final Wave-1--3 regression to 205 tests. |
| 2026-07-20 | Completed the scheduler benchmark, 58,467-Event run, 204-test regression, and independent Wave-3 APPROVE gate. |
| 2026-07-20 | Recovered the Wave-3 benchmark interruption and established the benchmark helper/API RED baseline. |
| 2026-07-20 | Recovered the interrupted Wave-3 GREEN, fixed the lifetime-covered SafeBound theorem violation, and passed the combined Wave-1–3 regression. |
| 2026-07-20 | Established the clean 24-case Wave-3 scheduler/report RED baseline before production changes. |
| 2026-07-20 | Passed the Wave-3 pre-implementation Claude ownership/interface gate and reconciled its two WATCH items before RED. |
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
- Current phase: Phase 2 Wave 4 — full verification, evidence packaging, and branch delivery.
- Completed: Phase-1 design checkpoint; Waves 1–3; Wave-4 cache and manifest modules with independent reviews; operator/hardware/FA/validator focused GREEN.
- In progress: Wave-4 full regression, evidence packaging, and branch delivery.
- Pending: Wave-4 commit/push/remote equality; Wave-5 scientific evaluation; final review, full regression, and final push.

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

### 2026-07-20 — Wave-3 pre-implementation ownership/interface gate

- **Motivation:** Resolve the scheduler/report versus operator-lowering test boundary and freeze the smallest observable result interface before authoring Wave-3 tests.
- **Expectation:** Keep Wave 3 focused on hand-built normalized graphs, avoid compatibility adapters or duplicate benchmarks, and obtain an independent APPROVE/WATCH/BLOCK verdict for counters, report inputs, lifetime timing, empty scheduling, and SM tie behavior.
- **Method:** Ran `omx ask claude` through StepCode Claude Opus 4.6 at effort `max` against both parent contracts, all current task contracts, committed Wave-1/2 APIs, the legacy scheduler/report, and the proposed ownership/interface corrections. Reconciled artifact `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-architecture-reviewe-2026-07-19T20-34-47-298Z.md` rather than adopting suggestions blindly.
- **Result:** Claude returned **APPROVE** with no blocker. Wave 3 now owns only scheduler/report tests over hand-built EventGraph/ResourceConfig; operator integration remains mandatory in Wave 4. The unique benchmark is `tests/performance/benchmark_event_scheduler.py`. One frozen SchedulerCounters value carries four operational counters; empty graphs return an empty zero result; smallest feasible SM ID is the placement tie policy; report accepts existing exact/SafeBound evidence but no speculative measured-comparison placeholder. The two WATCH items are bound to explicit smallest-SM and empty-graph RED cases. No production code changed.

### 2026-07-20 — Wave-3 scheduler/report clean RED

- **Motivation:** Replace the legacy mutable-Event scheduler/report behavior through observable contract tests before modifying production code.
- **Expectation:** Collect normally with no warnings and fail only because `schedule()` still expects a legacy Event iterable, the no-progress/counter APIs do not exist, and report still consumes scheduled Events.
- **Method:** Rewrote `tests/unit/test_event_scheduler.py` against hand-built EventGraph/ResourceConfig inputs and added `tests/unit/test_report.py`. Covered priority/tie order, dependency feasibility, caller-order invariance, hidden stream-order removal, vector admission, per-SM co-location, affinity, smallest-SM choice, lifetime hold/release, alternate-SM progress, explicit no-progress, zero-duration transitions, blocked rechecks, immutable witnesses, provenance-separated report values, demand-weighted busy time, lifetime accounting, timeline serialization, and empty reports. Ran both modules with bytecode and pytest cache disabled.
- **Result:** The focused RED collected all tests and reported `24 failed`, `0` collection errors, `0` warnings, pytest time `1.55s`, wrapper elapsed `2.936913851s`, and exit code `1`. Twenty-three failures reached the legacy `tuple(EventGraph)` path; the explicit no-progress test failed on the absent `SchedulingNoProgressError` export. No production code changed before this RED.

### 2026-07-20 — Wave-3 scheduler/report GREEN and blocker-indexed admission

- **Motivation:** Replace the legacy mutable-Event path with the smallest deterministic feasible scheduler/report implementation while keeping proof evidence separate and avoiding repeated full blocked-set rescans.
- **Expectation:** Satisfy all Wave-3 RED cases, preserve immutable EventGraph/Event values, wake blocked Events only when a relevant resource changes, and expose measured counters without a diagnostics module.
- **Method:** Implemented immutable `SimulationResult`, `SchedulerCounters`, and `SchedulingNoProgressError`; used remaining-path/event-ID priority, atomic global/per-SM placement, smallest feasible SM choice, lifetime reservation timing, and blocker indices keyed by `(scope, resource)`. Reworked `build_report()` as a provenance-preserving assembly boundary and added the independent tiny exact/SafeBound/scheduler validator. Added aggregate per-SM capacity prechecks and relevant-resource wakes after targeted performance evidence showed redundant placement/recheck work.
- **Result:** The four focused blocker/lifetime tests passed `4/4` in `0.79s` with wrapper elapsed `1.176870253s`. The scheduler/report/integration suite passed `38/38` in `1.01s` with wrapper elapsed `1.422243272s`. The independent validator covers `32` deterministic cases, seed `20260720`, and `921` caller-input permutations; it independently checks dependency, duration, capacity, co-location, affinity, lifetime intervals, makespan, and caller-order determinism.

### 2026-07-20 — Wave-3 post-implementation Claude review and proof RED

- **Motivation:** Challenge scheduler/report correctness, complexity claims, provenance ownership, and lifetime semantics before the benchmark and branch checkpoint.
- **Expectation:** Preserve the blocker-indexed scheduler and pass-through report if sound, identify any theorem violation before commit, and reject over-defensive validators or search machinery.
- **Method:** Ran three read-only StepCode Claude reviews through `omx ask claude` at effort `max`: the broad post-implementation artifact `.omx/artifacts/claude-you-are-the-independent-post-implementation-reviewer-for-the-2026-07-19T21-16-13-604Z.md` and two focused decision artifacts ending `21-18-41-544Z.md` and `21-19-44-165Z.md`. Reproduced the lifetime-covered SafeBound counterexample locally rather than accepting the review by assertion.
- **Result:** Overall verdicts were `WATCH`, `WATCH`, and `APPROVE with WATCH`; none was an overall BLOCK. All three confirmed that raw lifetime member demand violated the theorem: actual aggregate term `2.0`, expected `0.0`, feasible makespan `1.0`. They approved one `ResourceLifetime` owner operation and rejected a new module, compatibility shim, fallback, retry, or backtracking. The blocker index and report provenance boundary were approved. The greedy one-SM independent-prerequisite case remains a policy-completeness WATCH, and the missing formal benchmark remains a Wave-3 obligation.

### 2026-07-20 — Lifetime transient-demand root-cause fix

- **Motivation:** Restore `SafeBound <= modeled optimum` without adding an unproved lifetime-reservation term or duplicating scheduler logic.
- **Expectation:** Exclude only reservation-covered per-SM demand, retain additional endpoint/member transient demand and explicit-zero entries, and leave scheduler placement behavior unchanged.
- **Method:** Observed the SafeBound RED (`2.0 != 0.0`) and a direct `ResourceLifetime` owner-method RED (`AttributeError`). Added `ResourceLifetime.transient_per_sm_demand()`, replaced all three scheduler uses of the private filter, deleted that private helper, and normalized SafeBound resource-time demand through the same owner. Added direct covered/additional/explicit-zero coverage plus SafeBound mixed-demand integration coverage. The first timing command used absent GNU `/usr/bin/time`; after re-reading `task_memory/env_handbook.md`, reran with the documented Bash `time` keyword.
- **Result:** The direct four-test GREEN passed `4/4` in `0.82s` with wrapper elapsed `1.204s`. The two SafeBound lifetime tests passed `2/2` in `0.76s` with wrapper elapsed `1.137s`. The combined Wave-1–3 semantic/proof/scheduler/report/validator suite passed `192/192` in `1.24s` with wrapper elapsed `1.620s`. The fixed evidence is aggregate slot term `0.0`, feasible makespan `1.0`, and safety delta `feasible - bound = 0.0` for the regression graph because the dependency critical path remains `1.0`.

### 2026-07-20 — Wave-3 scheduler benchmark RED

- **Motivation:** Close the remaining Wave-3 performance-evidence gap with one benchmark path that measures graph construction, scheduling, and report assembly separately and retains the six reviewed historical Event sizes.
- **Expectation:** Freeze the GEMM-like graph shape, exact output schema, reviewed old runtimes, small-case exact/feasibility/determinism evidence, and invalid-size failure behavior before adding the benchmark implementation.
- **Method:** Added `tests/unit/test_benchmark_event_scheduler.py` with the required 18 output fields; historical `387`, `771`, `1,539`, `3,075`, `6,147`, and `58,467` Event points; graph/edge/resource counts; a one-CTA exact case; zero feasibility and determinism mismatches; and boolean/zero/negative/non-integer input rejection. Ran the test module with repository-root `PYTHONPATH`, bytecode disabled, and pytest cache disabled before creating the benchmark script.
- **Result:** The fresh RED reported `11 failed`, `0` collection errors, and exit code `1` in pytest `0.82s` with wrapper elapsed `1.199s`. Every failure had the expected root cause: `ModuleNotFoundError` for the intentionally absent `tests.performance.benchmark_event_scheduler` module. No scheduler/report production code changed in this RED step.

### 2026-07-20 — Wave-3 scheduler benchmark GREEN and measured scaling

- **Motivation:** Satisfy the Scheduler-Performance and Scheduler-Complexity-Accounting gates with actual wall-clock and counter evidence rather than event-count or asymptotic proxies.
- **Expectation:** Run the one-CTA exact case and all six historical sizes through one deterministic benchmark, including `58,467` Events, with zero feasibility violations and zero caller-order mismatches.
- **Method:** Implemented only `tests/performance/benchmark_event_scheduler.py` around a hand-built normalized GEMM-like graph (`3 * CTA_count + 3` Events, `4 * CTA_count + 2` edges, five resources). Timed Event/EventGraph/ResourceConfig construction, `schedule()`, and `build_report()` separately; compared a one-SM six-Event case with the exact oracle; audited capacity/dependency feasibility through an independent sweep; and reran every case from reversed Event input for determinism. Preserved raw output in `wave3_scheduler_benchmark.csv` with SHA-256 `d8d4b446cc8b07af336ce69e13a3c1ddba4536b8e4c0a7cfceb76f47631aedab`.
- **Result:** Benchmark unit GREEN passed `11/11` in pytest `0.78s` (`1.173s` wrapper). The exact case returned feasible `3.5`, exact `3.5`, relative optimality gap `0.0`, violations `0`, and mismatches `0`. All six historical sizes completed. At `58,467` Events, graph build was `0.720789447980s`, schedule `23.005453476013s`, report `0.678323030996s`, primary pipeline `24.404565954988s`, historical runtime `115.882818766s`, and ratio `4.748407284921x`; the entire command took `49.918s` because the required second determinism schedule is outside the primary pipeline denominator. Every row had `0` feasibility violations, `0` determinism mismatches, and `0` lifetime checks. No cycle-level or `10000x` claim is made.

### 2026-07-20 — Wave-3 post-fix completion APPROVE and fresh regression

- **Motivation:** Obtain the user-required independent review after the SafeBound correction and benchmark implementation, then regenerate verification evidence before delivery.
- **Expectation:** Confirm theorem safety, returned-schedule feasibility, provenance-separated reporting, honest benchmark denominators, and the absence of redundant defense, fallback, compatibility, or speculative modules.
- **Method:** Ran `omx ask claude` with StepCode Claude Opus 4.6 at effort `max` over both parent/current contracts, all Wave-3 source/tests, and the raw benchmark CSV. Reconciled artifact `.omx/artifacts/claude-you-are-the-independent-post-fix-completion-reviewer-for-pip-2026-07-19T21-43-22-782Z.md`. Then reran the complete Wave-1–3 semantic/proof/scheduler/report/benchmark/integration command.
- **Result:** Claude returned **APPROVE** and explicitly authorized commit/push before Wave 4. It found no mandatory code correction and one low WATCH: the historical constants lack host-CPU provenance; FSV-029 now records that limit. The fresh combined regression passed `204/204` in pytest `1.25s`, wrapper elapsed `1.630s`, exit code `0`.

### 2026-07-20 — Wave-3 resumed final delivery verification

- **Motivation:** Resume from the interrupted delivery checkpoint and produce evidence generated after the comment-only historical-denominator correction, before any commit or push.
- **Expectation:** Reconfirm all Wave-1--3 behavior with zero failures, then pass AST, added-line, whitespace, diff, checksum, and staging gates without touching the permanently ignored `=10.1` path.
- **Method:** Re-read the parent/current design, harness, plan, progress, issues, review, source diff, tests, benchmark, and prior Claude `APPROVE` artifact; interrupted the stale shared-file writer lane to keep delivery serial; reran the ten-module Wave-1--3 command with bytecode and pytest cache disabled. The first static helper intentionally surfaced two audit-scope defects: it scanned all Python lines rather than only added lines and therefore reported two unchanged legacy imports over 88 characters, and it treated three Markdown hard-break spaces in the untracked test report as trailing whitespace. The report metadata was normalized, and the final audit uses the intended added-line criterion.
- **Result:** Fresh regression passed `204/204` in pytest `1.54s`, wrapper elapsed `1.958s`, user `1.636s`, system `0.063s`, exit code `0`. All `12/12` changed/new Python files parsed successfully. The initial static wrapper exited `1` only because of the two audit-scope findings above; no production defect or test failure was observed. Final static, checksum, and staging results are recorded below after their fresh rerun.

### 2026-07-20 — Benchmark CSV line-ending root-cause correction

- **Motivation:** The first exact staged-path audit passed, but staged `git diff --check` rejected all eight benchmark CSV rows because their generated line terminators contained carriage returns.
- **Expectation:** Fix the output owner rather than manually masking the artifact, preserve every numeric benchmark cell, add a regression test that fails on CRLF, and restore the staged diff gate without fallback or a second benchmark writer.
- **Method:** Traced the bytes to the only writer, `csv.DictWriter(sys.stdout, fieldnames=FIELD_NAMES)`, whose default Excel dialect emits `\r\n`. Added `test_benchmark_csv_uses_lf_line_endings` and observed its expected RED: `1/1` failed because `"\r"` was present. Set only `lineterminator="\n"` on that writer, observed the complete benchmark unit module GREEN at `12/12`, and normalized the existing eight-row raw artifact from CRLF to LF while asserting exactly eight replacements, zero remaining carriage returns, and unchanged row count.
- **Result:** Focused GREEN passed `12/12` in pytest `0.78s`, wrapper `1.157s`, user `1.078s`, system `0.040s`, exit code `0`. The normalized artifact has `8` LF rows, `0` CR bytes, and SHA-256 `13dad9670800d8362c5c16f182b48255bf26e0c86cf0986b1156fe08e6a125f5`; numeric cells remain unchanged. Fresh Wave-1--3 regression passed `205/205` in pytest `1.34s`, wrapper `1.797s`, user `1.598s`, system `0.060s`, exit code `0`.

### 2026-07-20 — Wave-3 bounded correction review and final staging gate

- **Motivation:** Because the CSV writer correction occurred after the main Wave-3 completion review, preserve writer/reviewer separation and prove the exact repository delivery set before committing.
- **Expectation:** Obtain an independent no-BLOCK verdict for the tiny delta, then stage only the 25 approved repository paths, exclude `.omx` and `=10.1`, validate every checksum entry, and pass staged `git diff --check`.
- **Method:** Ran StepCode Claude Opus 4.6 at effort `max` in read-only mode and captured session `d599e31f-acfd-4e74-9fa8-dad0b8bf20da` in `.omx/artifacts/ask-claude-wave3-csv-lf-bounded-review-2026-07-19T21-58-55Z.md`. Regenerated the task checksum manifest from the complete Wave-1--3 module/test/evidence/task-document set, staged files through an explicit path list, compared sorted actual paths with the exact expected set, counted forbidden path classes, checked unstaged/untracked state, verified the manifest, and ran staged `git diff --check`.
- **Result:** Claude returned **APPROVE**, severity none, and zero mandatory actions; it confirmed one test, one unique-writer fix, byte-identical numeric cells, and no fallback, compatibility layer, duplicate module, over-defense, or claim expansion. The repository gate reported `25/25` staged paths, path mismatches `0`, `=10.1` staged `0`, `.omx` staged `0`, relevant unstaged tracked paths `0`, relevant untracked repository paths `0`, checksum validations `40/40`, and staged diff errors `0` with exit code `0`.

### 2026-07-20 — Wave-3 Lore commit, push, and Wave-4 handoff

- **Motivation:** Satisfy the user's explicit branch-delivery checkpoint and the harness remote-equality gate before changing cache or operator semantics.
- **Expectation:** Commit exactly the reviewed 25-path Wave-3 delivery, push `des`, fetch the remote, prove byte-identical local/remote commit identity, and start Wave 4 from a clean relevant workspace.
- **Method:** Created Lore commit `0a733ec597056924f9c10236071eb6892550080d` with tested/not-tested boundaries, pushed `des` to `origin`, fetched `origin/des`, compared both SHA values, and checked status while excluding only the permanently ignored `=10.1` path.
- **Result:** Push advanced `origin/des` from `126187c37d29ad6197b9cd89b85809f7badbb2ac` to `0a733ec597056924f9c10236071eb6892550080d`; local `HEAD` and `origin/des` both equal `0a733ec597056924f9c10236071eb6892550080d`; remote equality is `1`; the relevant working tree was clean. Wave 4 is active.

### 2026-07-20 — Interrupted Wave-4 recovery and entry verification

- **Motivation:** Resume from the precise post-push handoff without repeating delivered Wave-3 work or allowing legacy operator breakage to drive a compatibility shim.
- **Expectation:** Confirm `HEAD == origin/des`, retain only the three intended Wave-4 status-document edits, recover the frozen cache/manifest/operator contracts, and pass the complete Wave-1--3 regression before authoring new behavior.
- **Method:** Checked branch state while excluding only the permanently ignored `=10.1` path; re-read the parent/current `design.md` and `harness.md`, current plan/progress/issues/review records, README, relevant Event/resource interfaces, legacy operator/hardware lowering, and all Wave-4-owned tests; then ran the authoritative 205-case Wave-1--3 pytest command with bytecode and pytest cache writes disabled.
- **Result:** Local and remote commits remain `0a733ec597056924f9c10236071eb6892550080d`; only `design.md`, `plan.md`, and `progress.md` carried the expected handoff edits before this entry. The entry regression passed `205/205` in pytest `1.27s`, wrapper elapsed `1.663s`, user `1.554s`, system `0.085s`, exit code `0`. Cache production code remains unchanged; the next action is the cache RED suite.

### 2026-07-20 — Wave-4 cache RED/GREEN and static verification

- **Motivation:** Implement the one frozen manifest-order shared-L2/HBM model while keeping cold/warm state, exact-sized final blocks, dirty traffic, and output visibility explicit and auditable.
- **Expectation:** Observe failures before production code exists; make every cache transition and fail-fast branch pass through one `cache.py`; expose the reviewed public contract; preserve all 205 delivered Wave-1--3 tests; and introduce no policy switch, isolated-cache path, hit-ratio traffic source, fallback, or second module.
- **Method:** Added `tests/unit/test_cache.py` first and ran it with imports delayed into test bodies, then implemented only `event_simulator/cache.py`. The initial run produced `30` ordinary failures because the module was absent. The first GREEN passed `30/30`. Added a public-package export test, observed its isolated `1/1` RED, then exported the eight cache symbols from `event_simulator/__init__.py`. Ran the 31-case cache suite, the 205-case Wave-1--3 suite, AST parsing, added-line length audit, and `git diff --check`.
- **Result:** Cache tests passed `31/31` in pytest `0.80s`, wrapper elapsed `1.182s`, user `1.121s`, system `0.056s`; Wave-1--3 passed `205/205` in pytest `1.33s`, wrapper elapsed `1.718s`, user `1.632s`, system `0.056s`. All `3/3` changed/new Python files parse; newly added Python lines over 88 characters are `0`; diff errors are `0`; all `8/8` cache symbols are public. The first static wrapper used `python -m ast` with three files and exited because that CLI accepts one input; the corrected parser used `ast.parse`. A subsequent whole-file length scan rediscovered the two unchanged legacy import lines already recorded in FSV-022; the accepted diff-added-line audit passed without unrelated reformatting. Independent cache-module review is next.

### 2026-07-20 — Wave-4 cache independent review and reconciliation

- **Motivation:** Satisfy the mandatory post-module independent review gate and explicitly challenge cache correctness, traffic conservation, simplicity, and branch coverage before manifest code can depend on the API.
- **Expectation:** Obtain no `BLOCK`; correct every validated mandatory issue; avoid speculative refactors; and preserve the one-file/one-model cache boundary.
- **Method:** Ran `omx ask claude` through StepCode Claude Opus 4.6 at effort `max`, artifact `.omx/artifacts/claude-you-are-the-independent-post-implementation-reviewer-for-pip-2026-07-19T22-16-05-676Z.md`. Reconciled the full verdict against source/tests rather than applying it blindly. Claude found no production defect and raised two LOW test gaps: repeated eviction-loop execution and dirty-state preservation on read hit. Added one focused test for each path, ran each test individually, then reran the complete cache and Wave-1--3 suites plus AST/diff checks.
- **Result:** Verdict **APPROVE**, zero mandatory fixes, and explicit authorization to proceed to `GemmLaunchManifest`. Claude found no over-defense, duplicate semantic model, fallback, mutable leak, output-flush bug, or traffic inconsistency. Both LOW coverage paths now pass. Final cache suite is `33/33` in pytest `0.80s`, wrapper elapsed `1.177s`, user `1.089s`, system `0.072s`; Wave-1--3 is `205/205` in pytest `1.36s`, wrapper elapsed `1.756s`, user `1.639s`, system `0.044s`; `3/3` files parse and diff errors are `0`. Production code did not change after the review.

### 2026-07-20 — Wave-4 `GemmLaunchManifest` RED/GREEN and pre-review verification

- **Motivation:** Implement the sole authoritative source for persistent worker assignment, split-K partitions, explicit reduction topology, issued extents, and canonical cache-access ownership without inferring policy from `is_split_k`, CTA ratios, shapes, or legacy floor division.
- **Expectation:** Preserve the accepted frozen design, observe the manifest suite fail before the module exists, make the smallest immutable API pass every semantic and fail-fast branch, keep cache validation in `CacheConfig`, and preserve all delivered Wave-1--3 behavior.
- **Method:** Added `tests/unit/test_gemm_manifest.py` before production implementation and observed `39/39` ordinary failures because the module and package exports were absent. Implemented `event_simulator/gemm_manifest.py` plus the narrow canonical-block lookup in `CacheConfig`. The first GREEN attempt passed `37/39`; one test fixture constructed a duplicate reduction input and was correctly rejected before reaching its intended duplicate-cache-ownership branch, while the public package still lacked the four manifest exports. Rebuilt that fixture from a topology-valid split-K manifest, changed only its reduction cache reference to an already-owned index, and added the four package exports. Ran the two formerly failing cases, the combined cache/manifest suite, the complete Wave-1--3 regression, AST parsing, added-Python-line length audit, and `git diff --check`.
- **Result:** The initial RED was `39 failed` in pytest `1.69s`, wrapper elapsed `2.076s`, user `1.970s`, system `0.064s`, exit code `1`. The first GREEN attempt was `37 passed, 2 failed` in pytest `0.85s`, wrapper elapsed `1.229s`, user `1.148s`, system `0.068s`, exit code `1`. The two root-cause cases then passed `2/2` in pytest `0.81s`; the combined cache/manifest suite passed `72/72` in pytest `0.93s`, wrapper elapsed `1.309s`, user `1.209s`, system `0.060s`; Wave-1--3 passed `205/205` in pytest `1.34s`, wrapper elapsed `1.736s`, user `1.655s`, system `0.060s`. All `5/5` changed/new Python files parse, newly added Python lines over 88 characters are `0`, and diff errors are `0`. The first length wrapper failed because it scanned added Markdown lines instead of filtering `.py` paths; the corrected diff parser tracks each `+++ b/<path>` header and checks Python additions only. No production validation was weakened, and independent manifest review is the next gate.

### 2026-07-20 — Wave-4 manifest independent review and reconciliation

- **Motivation:** Satisfy the mandatory key-module review gate and challenge manifest correctness, completeness, simplicity, and test independence before lowerings are allowed to consume it.
- **Expectation:** Obtain no `BLOCK`, correct every validated coverage or behavior gap without adding policy abstractions, and preserve the manifest as the sole new-path source for persistent/split-K/reduction semantics.
- **Method:** Ran `omx ask claude` through StepCode Claude Opus 4.6 at effort `max`, artifact `.omx/artifacts/claude-you-are-the-independent-post-implementation-reviewer-for-pip-2026-07-19T22-32-47-486Z.md`, and reconciled each finding against source/tests. Claude returned APPROVE with no mandatory correction, one MEDIUM chained-reduction coverage gap, and one meaningful LOW unrestricted-affinity coverage gap. Added only those two tests; did not change production code, error wording, public API, or module ownership. Reran the focused cases, complete cache/manifest suite, Wave-1--3 regression, AST, added-Python-line, and diff checks.
- **Result:** Raw verdict **APPROVE** and explicit authorization to proceed. The two review witnesses passed `2/2` in pytest `0.81s`, wrapper elapsed `1.193s`, user `1.108s`, system `0.056s`; cache/manifest passed `74/74` in pytest `0.92s`, wrapper elapsed `1.314s`, user `1.202s`, system `0.081s`; Wave-1--3 passed `205/205` in pytest `1.32s`, wrapper elapsed `1.722s`, user `1.626s`, system `0.053s`. All `5/5` Python files parse, added Python lines over 88 characters are `0`, and diff errors are `0`. Manifest production code is unchanged after review; operator/hardware/validator lowering is now active.

### 2026-07-20 — Wave-4 lowering collection RED and pre-implementation review

- **Motivation:** Establish the real migration boundary before production edits and independently challenge the manifest/hardware/operator/validator design for hidden fallback, compatibility, over-defense, or duplicate ownership.
- **Expectation:** Confirm that the focused suite fails only because Wave-4-owned tests and lowerers still use deliberately removed APIs, then freeze the smallest EventGraph lowering rules and obtain a non-BLOCK verdict before writing behavior tests.
- **Method:** Ran the cache/manifest/GEMM/FA/operator focused command with bytecode and pytest cache disabled. It stopped during collection at `tests/integration/test_operator_simulation.py:30`, where the legacy one-dict `ResourceConfig({...})` fixture no longer satisfies the two-level topology. Reviewed current `events.py`, `resources.py`, `operators.py`, `hardware_adapter.py`, validator, and Wave-4 tests, then ran `omx ask claude` through StepCode Claude Opus 4.6 at effort `max`; artifact `.omx/artifacts/claude-you-are-the-independent-pre-implementation-design-reviewer-f-2026-07-19T22-43-13-316Z.md`.
- **Result:** The initial command produced `1` collection error in pytest `1.46s`, wrapper elapsed `1.924s`, user `3.468s`, system `0.101s`, exit code `2`; root cause is the intended Wave-1 API removal, not an environment or production regression, so no shim is authorized. Claude returned **APPROVE** and required explicit `hbm_bandwidth`/`l2_bandwidth` ownership, ALU demand for reductions, flush-to-completion edges, and documentation of sequential miss expansion as a fixed-model simplification. It approved the required `initial_cache_state`, manifest-only `lower_gemm_v2`, one Worker lifetime, reductions outside lifetimes, FA affinity, two-level hardware topology, and authoritative manifest-map validator. Tests-only migration is the next action.

### 2026-07-20 — Wave-4 tests-only migration and clean behavior RED

- **Motivation:** Remove the deferred Wave-4 test fixtures' dependence on deliberately deleted flat resources, raw Event lists, caller-order stream semantics, legacy report fields, dimension-derived GEMM policy, and heuristic validator support rules before any production change.
- **Expectation:** Collect the complete focused owner set with zero errors and observe ordinary failures only at the missing HBM/L2 primitives, two-level hardware adapter, EventGraph lowerers, manifest-only GEMM path, explicit FA affinity, and authoritative manifest-map validator.
- **Method:** Migrated the operator tests to two-level `ResourceConfig`, `EventGraph`, `schedule(graph, resources)`, and provenance-separated report fields; replaced legacy GEMM-v2 expectations with cache-byte conservation, one Worker lifetime, persistent ordering, physical-issued MMA work, split-K release/reduction topology, output flush, schedule/report, signature, and tuple-permutation witnesses; migrated FA tests to explicit singleton affinity and order-invariant graphs; migrated validator tests to row-indexed authoritative manifests, explicit cold state, mismatch/missing accounting, and propagated failures. The first focused run collected all tests but reported `13` setup errors because the FA fixture still called the intentionally unimplemented hardware adapter; the fixture was corrected to a valid hand-built two-level config without changing production, and the authoritative command was rerun.
- **Result:** Clean RED collected `145` tests with `98 passed`, `47 failed`, `0 errors`, and `0` collection errors; pytest time was `2.09s`, wrapper elapsed `2.545s`, user `4.053s`, system `0.172s`, exit code `1`. Every remaining failure is attributable to the frozen missing production behavior: `HBMRead/HBMWrite/L2Read/L2Write` calibration/event types, two-level resource construction, manifest-only `lower_gemm_v2`, EventGraph simple/FA lowerers, explicit FA affinity, or authoritative manifest-map validation. No compatibility shim or invalid test fixture remains.

### 2026-07-20 — Wave-4 operator/hardware/validator minimal GREEN

- **Motivation:** Implement only the production behavior proven missing by the clean RED while preserving the frozen manifest/cache/lifetime/affinity/validator ownership boundaries and avoiding a compatibility or duplicate-policy layer.
- **Expectation:** Add the four HBM/L2 primitives and two-level topology; return normalized `EventGraph` values from every lowerer; lower one cache resolution through byte-conserving traffic Events; give every GEMM Worker one lifetime; keep reductions outside lifetimes; make FA assignment explicit; require authoritative row-indexed manifests; and pass all `145` focused cases.
- **Method:** Added `HBMRead`, `HBMWrite`, `L2Read`, and `L2Write` to `EVENT_TYPES` and specification calibration; replaced flat hardware construction with one global/per-SM topology; migrated the existing `operators.py` helper and simple lowerers without adding a module; replaced legacy GEMM-v2 policy reconstruction with the required manifest-only signature, one cache-transition lowering helper, Worker acquire/work/release chains, physical-issued MMA work, out-of-lifetime reduction work, and explicit output-flush dependencies; removed FA round-robin list interleaving in favor of singleton `eligible_sms`; and changed the sole validator to use `Mapping[row_index, GemmLaunchManifest]` with explicit shape/tile/Worker-count checks. The first hardware targeted run exposed one stale `dram_us_per_byte` reference left by the local HBM variable rename; the traceback isolated that exact source reference, which was changed to `hbm_us_per_byte` and the same suite was rerun.
- **Result:** Hardware adapter passed `19/19` after the one-reference root-cause fix; simple operator integration passed `8/8`; manifest GEMM integration passed `11/11`; FA integration passed `21/21`; validator unit tests passed `12/12`. The complete focused command passed `145/145` in pytest `1.89s`, wrapper elapsed `2.372s`, user `3.789s`, system `0.113s`, exit code `0`. The lowerer signature is exactly `(kernel_id, *, manifest, calibration, initial_cache_state, stream_id='stream-0')`; the focused forbidden-legacy scan and `git diff --check` both pass. No fallback, compatibility shim, second cache model, second validator, stream-order dependency, or new production module was introduced. Independent post-implementation Claude review is the next gate.

### 2026-07-20 — Wave-4 post-implementation APPROVE and coverage reconciliation

- **Motivation:** Close the required independent module/stage review before delivery and verify that the completed lowering remains minimal, manifest-owned, and free of fallback, compatibility, hidden stream order, duplicate traffic policy, and redundant defense.
- **Expectation:** Obtain no `BLOCK`; correct only validated behavior or coverage gaps; preserve production design when the review finds no correctness defect; and regenerate focused evidence after every accepted test or cleanup delta.
- **Method:** The first `omx ask claude` transport returned session `596cf4e7-ecd9-4795-a156-7ecd48cf0281` after only session/hook startup and produced no review artifact, so it was not counted. A PTY-backed StepCode Claude Opus 4.6 review at effort `max` completed with artifact `.omx/artifacts/claude-you-are-the-independent-post-implementation-reviewer-for-pip-2026-07-19T23-19-03-079Z.md`. Reconciled the raw verdict against source/tests, added only the suggested warm-initial-state and L2-output-visibility integration witnesses, and left production unchanged. A source-reference audit then proved that `compute_actual_tile_dims`, `compute_wave_split`, and `is_edge_tile` had become unused only because this wave replaced the legacy dimension-derived GEMM-v2 path; removed those three imports without adjacent refactoring. Reran the full focused owner set with bytecode and pytest cache disabled.
- **Result:** Raw verdict **APPROVE**, zero mandatory findings. Claude independently confirmed byte conservation, one Worker lifetime, persistent order, physical-issued MMA work, split-K/reduction dependencies, output-flush predecessors, FA affinity, two-level topology, row-indexed authoritative validation, and absence of fallback/compatibility/duplicate models/over-defense. The two actionable WATCH cases now pass and the unchanged-topology `operator_type` dispatch remains a documented transition boundary with no action required. Fresh focused evidence is `147/147` passed in pytest `1.79s`, wrapper elapsed `2.252s`, user `3.662s`, system `0.152s`, exit code `0`; the changed `operators.py` has zero locally unused imports and `git diff --check` passes. Wave 4 has entered full regression and delivery verification.

### 2026-07-20 — Wave-4 full regression, proof audit, and numeric report

- **Motivation:** Prove that the complete Wave-4 delta preserves every delivered Wave-1--3 behavior and package the required absolute expected/actual/delta evidence before staging or commit.
- **Expectation:** Pass every collected repository test, preserve all exact/SafeBound corpus metrics, parse every changed/new Python file, report zero newly added long Python lines and forbidden legacy patterns, and produce one reproducible Wave-4 report with no broadened scientific claim.
- **Method:** Ran the entire `tests/` tree, the independent exact/SafeBound validator, a read-only numeric contract probe over the accepted H100 and synthetic GEMM/FA fixtures, and the diff-scoped AST/line-length/import/signature/history/legacy/diff gate. The first static run found one newly added 90-character generator-expression assertion at `tests/unit/test_gemm_manifest.py:444`; the accepted maximum is 88. Wrapped only that expression, ran its exact test, and reran the complete static gate. Wrote `test_report_2026-07-20_wave4_operator_lowering.md` with commands, environment, RED history, root-cause resolutions, absolute values, review evidence, and claim boundaries.
- **Result:** Full pytest passed `400/400` in `2.16s`, wrapper elapsed `2.645s`, user `4.181s`, system `0.176s`, exit code `0`. The proof validator passed `4,725/4,725` cases, `28,350` permutations, and `18,360` monotonicity comparisons with every failure count `0`, maximum exact delta `0.0`, and unchanged canonical digest. The style-focused test passed `1/1`; final static evidence is `14/14` Python files parsed, added Python lines over 88 characters `0`, forbidden legacy hits `0`, changed-operator unused imports `0`, signature match `1`, task Markdown history `18/18` before adding the new report, and diff errors `0`. The report records zero byte/work/lifetime/affinity equality deltas and explicitly labels its `10.0 us` validator value as a synthetic fixture rather than hardware evidence.

### 2026-07-20 — Wave-4 checksum rebuild and final delivery-package review

- **Motivation:** Close the artifact-integrity and independent stage-review gates before any staging, commit, push, or Wave-5 work.
- **Expectation:** Hash every Wave-1--4 production, proof, test, evidence, and current task-document input in one self-excluding manifest; obtain no Claude `BLOCK`; and avoid production churn for non-defects or already-owned invariants.
- **Method:** Rebuilt `checksums.sha256` from an explicit `54`-path inventory, including the independent time-grid reference and the new Wave-4 modules/tests/report, then ran `sha256sum -c`. Ran the final read-only `omx ask claude` delivery review through StepCode Claude Opus 4.6 at effort `max`; artifact `.omx/artifacts/claude-you-are-the-independent-final-delivery-package-reviewer-for--2026-07-19T23-39-55-025Z.md`. Reconciled its three WATCH observations against the simplicity, fail-fast, topology, and validator boundaries.
- **Result:** Checksums passed `54/54`, failed `0`; all `19/19` task Markdown histories were present; all `37/37` hashes listed directly in `summary.md` matched; and `git diff --check` returned zero findings. Claude returned **APPROVE**, mandatory fixes **None**, and staging status **READY**. No production code changed: an extra cache-action guard would duplicate upstream validation, a second topology policy would be speculative, and a validator CLI workaround would violate the authoritative-manifest fail-fast contract. Fresh full regression, proof validation, static gate, exact-path staging, Lore commit, push, and remote equality remain the delivery actions.

### 2026-07-20 — Wave-4 fresh pre-staging verification and checker correction

- **Motivation:** Satisfy the evidence-before-commit gate with commands run after final delivery review and document changes.
- **Expectation:** Reproduce all focused/full/proof results, then pass AST, diff-added line length, unused-import, forbidden-pattern, signature, document-history, checksum, and diff checks with no production correction.
- **Method:** Reran the `147`-case focused suite, full `tests/` tree, and independent exact/SafeBound validator with bytecode and pytest cache writes disabled. Ran the complete static wrapper. Its first attempt flagged `annotations`; traced that name to `from __future__ import annotations`, confirmed it is a compiler directive rather than a runtime symbol, changed only the inline checker to exclude `__future__`, and reran the whole static gate.
- **Result:** Focused tests passed `147/147` in pytest `1.69s`, wrapper `2.161s`; full regression passed `400/400` in pytest `2.24s`, wrapper `2.698s`; and the oracle passed `4,725/4,725`, `28,350` permutations, and `18,360` monotonicity checks in wrapper `4.283s`, with every mismatch/violation/failure count `0`. The corrected static gate parsed `14/14` Python files, found `0` added lines over 88, `0` actual unused imports, `0` forbidden hits, signature match `1`, histories `19/19`, and a clean diff. The failure belonged solely to the audit script; production and tests were unchanged.

### 2026-07-20 — Wave-4 first exact-path staging audit

- **Motivation:** Prove that the index contains exactly the reviewed Wave-4 delivery and no ignored, advisor-runtime, unrelated, stale, or unhashed content before commit.
- **Expectation:** Stage the explicit `25`-path list without `git add .`; match expected and actual paths exactly; match all `54` checksum inputs against index blobs; and leave no relevant tracked or untracked delta outside the index.
- **Method:** Ran one explicit `git add -- <25 exact paths>` command, compared the expected path set against `git diff --cached --name-only`, hashed every manifest path from `git show :<path>`, checked excluded/runtime prefixes, counted relevant unstaged and untracked paths, and ran staged `git diff --check`.
- **Result:** Expected and actual staged paths were `25/25`, path mismatches `0`, ignored-path entries `0`, `.omx/` entries `0`, index checksum failures `0/54`, relevant unstaged tracked paths `0`, relevant untracked paths `0`, and staged diff errors `0`. This documentation update now requires a bounded checksum rebuild and re-stage before the final index audit.

### 2026-07-20 — Wave-4 Lore commit, push, and remote equality

- **Motivation:** Close the mandatory branch-delivery gate before any Wave-5 environment provisioning or scientific campaign.
- **Expectation:** Preserve the reviewed 25-path index, create one Lore-compliant checkpoint, push without force, fetch the remote ref, prove exact SHA equality, and leave the relevant worktree clean.
- **Method:** Rebuilt the post-audit checksum manifest, explicitly re-staged only the five changed delivery documents, repeated the full index audit, committed with the intent `Model authoritative GPU execution semantics before scientific evaluation`, pushed `des`, fetched `origin/des`, compared both full SHAs, and ran the safe status command excluding `=10.1`.
- **Result:** The final index retained `25/25` exact paths, `54/54` index hashes, `38/38` summary hashes, zero path mismatches, zero ignored/OMX paths, zero relevant unstaged/untracked paths, and clean staged/unstaged diff checks. Commit `350159313aa3a018700e648bce7ca5e842a34e07` was pushed successfully; local `HEAD` and `origin/des` both equal that SHA; remote equality is `1`; and the relevant status was clean. Wave 5 is active.
