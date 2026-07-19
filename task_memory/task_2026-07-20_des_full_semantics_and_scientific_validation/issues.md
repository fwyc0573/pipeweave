# DES Full Semantics and Scientific Validation Issues

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Resolved FSV-033 by excluding Python `__future__` compiler directives from the final unused-import audit. |
| 2026-07-20 | Reconciled FSV-002 through FSV-006 and FSV-013 with the delivered Wave-1–4 modeled implementation while retaining measured/data evidence gaps. |
| 2026-07-20 | Resolved the final Wave-4 added-line length failure at its single test-expression owner and restored the complete static gate. |
| 2026-07-20 | Closed FSV-031 after the Wave-4 tests-only migration produced a clean 145-case behavior RED with zero collection/setup errors. |
| 2026-07-20 | Recorded the Wave-4 focused-suite collection failure as the expected legacy-test migration boundary and prohibited a compatibility shim. |
| 2026-07-20 | Extended FSV-022 with the Wave-4 added-line path-filtering wrapper defect and corrected five-file evidence. |
| 2026-07-20 | Reapplied the resolved diff-scoped static-audit rule during Wave 4 and recorded the multi-file `python -m ast` wrapper error. |
| 2026-07-20 | Resolved generated benchmark CSV CRLF output at its unique writer and added a focused LF regression test. |
| 2026-07-20 | Closed the Wave-3 scheduler measurement obligation and recorded the historical-runtime provenance WATCH. |
| 2026-07-20 | Resolved the lifetime-covered SafeBound safety violation, documented greedy-policy no-progress, and opened the lifetime-validation complexity WATCH. |
| 2026-07-20 | Resolved the Wave-3/Wave-4 focused-test ownership and scheduler benchmark path conflicts through an independent Claude gate. |
| 2026-07-20 | Resolved the resource-free SafeBound `max` call defect found during the first GREEN attempt. |
| 2026-07-20 | Resolved the Wave-2 review/test arithmetic defects and preserved the sound per-SM exact-domain boundary. |
| 2026-07-20 | Resolved the Wave-1 line-length audit scope defect without reformatting unrelated legacy imports or weakening the diff gate. |
| 2026-07-20 | Reopened the lifetime-progress implementation audit for an external-event wait-for case raised by the Wave-1 read-only reviewer. |
| 2026-07-20 | Resolved the comparator approval issue and froze modeled-universal, held-out, and calibration evidence boundaries. |
| 2026-07-20 | Narrowed the missing comparator to a source-backed Accel-Sim A100 candidate and recorded its explicit approval/build prerequisites. |
| 2026-07-20 | Selected exhaustive serial SGS for the small exact oracle and added its self-contained coverage proof and independent time-grid audit. |
| 2026-07-20 | Added the static cache-order versus hardware-interleaving boundary and corrected the reviewed lower-bound direction. |
| 2026-07-20 | Added the corrected lifetime-deadlock and scheduler-complexity issues found while reconciling the shared execution review. |
| 2026-07-20 | Corrected the analytical provenance of `tensor_all_ops` and added the missing measured-counter evidence issue. |
| 2026-07-20 | Added the exact-engine review arithmetic/proof inconsistency and narrowed the remaining decision to an exhaustive standard-library oracle candidate. |
| 2026-07-20 | Resolved the four-layer exact-bound ambiguity and added quantified split-K, partial-tile, and report-provenance issues. |
| 2026-07-20 | Updated the solver-dependency issue with current SciPy/HiGHS availability, absent project packaging, and formulation-proof requirements. |
| 2026-07-20 | Added implicit stream-order, exact-certificate, and unapproved-solver risks found by source inspection and preliminary Claude review. |
| 2026-07-20 | Added quantified cross-architecture coverage and authoritative-benchmark fail-fast issues from the evidence audit. |
| 2026-07-20 | Initialized the semantic, architecture, benchmark, calibration, and universal-claim issue register. |

## Open Issues

### FSV-001 — “Exact bound” has two materially different meanings

- **Status:** Resolved on 2026-07-20 by the user's Option A selection.
- **Root cause:** Exact modeled optimum and scalable analytical lower bound are different mathematical objects. General resource-constrained scheduling is not expected to have a scalable exact solver without a restricted domain.
- **Impact:** The implementation must preserve four distinct contracts and may not implicitly convert among them.
- **Resolution:** Provide an exact modeled optimum, scalable safe analytical bound, deterministic feasible schedule, and measured-hardware comparison as separate result/evidence layers. Concrete APIs and engines remain subject to the remaining design decisions.

### FSV-002 — Universal modeled theorem and universal hardware claim are not separated in the request

- **Status:** Modeled proof implemented and validated; final modeled and empirical audits pending.
- **Root cause:** Event-model proofs quantify over declared abstractions; real hardware contains behavior outside that abstraction and requires matched empirical evidence.
- **Impact:** The requested universal lower-bound claim could otherwise overstate evidence.
- **Resolution:** The universal theorem quantifies only over a finite normalized fixed-duration EventGraph with explicit dependencies, declared global/per-SM capacities, and one manifest-order resolved cache state. Affinity and lifetime reservations may be removed only as named relaxations. Real hardware receives a separate finite empirical audit that reports every violation and makes no universal claim.

### FSV-003 — Current Event IR cannot express requested execution semantics

- **Status:** Resolved in Waves 1–4 on 2026-07-20.
- **Root cause:** An Event owns at most one `resource` and has no simultaneous demand, CTA lifetime, affinity, cache state, persistent grouping, or split-K metadata.
- **Impact:** Items 4–8 cannot be represented or tested faithfully.
- **Resolution:** Implemented one immutable Event specification, one normalized EventGraph, one ScheduleEntry result, one ResourceLifetime reservation, and one two-level ResourceConfig. The exact oracle, SafeBound, scheduler, report, cache/manifest lowerer, and FA path share that boundary; the full repository passes `400/400` tests with no duplicate graph or resource validator.

### FSV-004 — Current scheduler is order-sensitive and approximately quadratic

- **Status:** Resolved for the declared deterministic feasible policy; historical performance provenance remains WATCH.
- **Root cause:** The greedy scheduler repeatedly scans the caller-provided Event list and schedules the first ready item.
- **Evidence:** The same DAG yields makespans `21.0` and `11.0` under two input orders; historical `58,467`-event runtime was `115.882818766s`.
- **Impact:** It is not a public bound and is unsuitable for large design-space claims.
- **Resolution:** Implemented descending remaining dependency-path duration with `event_id` tie-break, explicit dependencies only, atomic placement, blocker-indexed wakeups, and separate graph/scheduler/report timing. The `58,467`-Event primary pipeline measured `24.404565954988s` versus the historical `115.882818766s`, labeled only as a size-matched historical ratio because stages and host provenance are not controlled. No unsupported total asymptotic or cycle-level claim is made.

### FSV-005 — Cache/residency contract is absent

- **Status:** Modeled implementation resolved; matched measured evidence pending.
- **Root cause:** Current lowering uses aggregate cold traffic and has no literal cache state, transition, capacity, or eviction model.
- **Impact:** Warm-L2 causes cannot be asserted, and monotonic/traffic-conservation reasoning is incomplete.
- **Resolution:** Implemented one fully associative, size-aware, deterministic LRU HBM+abstract-L2 model over the canonical manifest access order, with explicit initial recency/dirty state and output visibility. Cache and lowering tests report zero HBM/L2 byte-conservation delta, including warm state and L2/HBM visibility. It remains manifest-order modeled evidence, not a hardware-universal cache theorem; Wave 5 owns matched counter evidence.

### FSV-006 — Persistent CTA, split-K, and partial-tile metadata are unmatched

- **Status:** Modeled implementation resolved for explicit authoritative manifests; dataset manifest coverage and evaluation pending.
- **Root cause:** Current lowering does not consume full measured launch-policy semantics; `tile_k` is behaviorally inert, split-K replication/reduction is absent, and partial tiles count useful work only.
- **Evidence:** Historical H100 coverage supported `4,246/10,800` rows; `6,554/10,800` had CTA mismatch; all `437/437` split-K rows were unsupported. Across the full split-K dataset, CTA ratios do not uniquely recover a split factor: H100/H200/H800 have non-integer ratios from `1.178571` to `4.137931`, H20 has `85` rows below the base CTA grid and a minimum ratio of `0.131313`, and several other targets have thousands of rows with `cta_count == base_ctas` despite `is_split_k=1`. For non-split Hopper rows, `tensor_all_ops` equals a simple padded-tile formula in H100 `9,366/10,363`, H20 `9,202/9,534`, H200 `9,358/10,392`, and H800 `9,379/10,343`, but p95 padded ratios above `1.0` remain on three targets.
- **Impact:** Structural comparisons cannot claim matched execution.
- **Resolution:** `GemmLaunchManifest` is the implemented sole new-path policy source. Worker assignment expresses persistent CTAs; explicit K partitions and accumulator topology express split-K; logical and issued extents derive useful and physical work; lowering gives every Worker one lifetime and keeps reductions outside lifetimes. Rows without authoritative manifests are counted and rejected. Wave 5 must provision real row-indexed manifests before dataset validation; heuristic reconstruction remains prohibited.

### FSV-007 — No matched cycle-accurate comparator exists in the repository

- **Status:** Dependency/toolchain approved by the user; provisioning and benchmark evidence pending.
- **Root cause:** Existing data contains hardware measurements and DES outputs but no named cycle-accurate simulator runtime/result for the same workload and boundary.
- **Impact:** Item 9 and any speedup claim are currently UNPROVEN.
- **Resolution:** The user approved pinned Accel-Sim Framework/GPGPU-Sim plus a pinned CUDA/`nvcc` environment for one synthetic A100 matched GEMM. Phase 2 must provision and verify exact revisions/config hashes and report it as a GPGPU-Sim cycle-level PTX-mode comparison. No `nsys`, Hopper, pre-traced, or silicon-equivalence substitution is allowed.

### FSV-008 — Held-out multi-hardware protocol is absent

- **Status:** Design resolved; execution pending.
- **Root cause:** The dataset names multiple hardware targets, but the current end-to-end validator is materially centered on H100 and no frozen held-out protocol exists.
- **Impact:** Item 10 is currently UNPROVEN.
- **Resolution:** Run four fixed leave-one-hardware-out Hopper folds over H100/H20/H200/H800 using only target hardware specifications and explicit launch manifests; target latency is read once for final scoring. Cross-architecture results are reported only after authoritative manifests yield nonzero support, with every unsupported row counted.

### FSV-009 — Calibration can contaminate zero-shot evidence

- **Status:** Design resolved; campaign pending.
- **Root cause:** Target-hardware measured calibration and target-held-out zero-shot evaluation use incompatible data-access rules unless explicitly separated.
- **Impact:** Items 10 and 11 could become circular.
- **Resolution:** Zero-shot folds use specification-derived target rates and no target primitive or operator timing. A separate measured-primitive-calibrated study may use target primitive measurements but is explicitly non-zero-shot; it cannot use complete-operator latency or silently certify a real-hardware lower bound.

### FSV-010 — Existing small-row bound violations are not causally attributed

- **Status:** Open scientific risk.
- **Root cause:** Measurement/model boundary mismatch has not been isolated among cache state, launch policy, scheduling, timing visibility, and provenance.
- **Evidence:** Four historical rows had actual/DES values `10.472800/11.358228`, `10.619200/11.324017`, `8.213200/10.016648`, and `10.056400/10.243910` microseconds.
- **Impact:** Universal measured-hardware lower-bound acceptance is currently contradicted.
- **Resolution required:** Use matched semantics and measurements; do not clamp, scale, skip, or label warm-L2 without evidence.

### FSV-011 — Current multi-hardware support is Hopper-only

- **Status:** Open; depends on persistent/split-K semantics.
- **Root cause:** All measured rows for seven Ampere, Ada, and Blackwell hardware targets use split-K, which the current validator rejects.
- **Evidence:** Current-policy support is H100 `4,246`, H20 `2,879`, H200 `4,239`, H800 `3,800`, total `15,164`; every other target has `0/10,800` supported rows.
- **Impact:** A current offline study can establish only within-Hopper held-out evidence, not broad cross-architecture zero-shot.
- **Resolution required:** Complete matched split-K/persistent semantics before the cross-architecture study, and label interim evidence narrowly.

### FSV-012 — Existing FA3 benchmark control flow is not authoritative

- **Status:** Open; relevant only if reused.
- **Root cause:** `tests/validation/benchmark_fa3.py` catches broad exceptions and continues, while this task requires fail-fast evidence.
- **Impact:** Missing configurations could be hidden and completeness metrics corrupted.
- **Resolution required:** If the benchmark becomes part of this task, first add a RED test and remove the catch-all continuation at its root cause; otherwise do not cite it as authoritative evidence.

### FSV-013 — Implicit stream order is caller-order semantics

- **Status:** Resolved in Waves 1–4 on 2026-07-20.
- **Root cause:** `scheduler._validated_dependencies()` adds each stream predecessor while iterating the caller-provided Event sequence, and `test_same_stream_events_keep_input_order_without_explicit_dependencies` locks that behavior.
- **Impact:** A certified dependency-DAG bound cannot claim input-permutation invariance while silently deriving different DAG edges from permutation.
- **Resolution:** Removed `stream_ordered` and iterable-derived stream edges from the EventGraph path. Lowerers emit explicit dependencies, `stream_id` is metadata only, and reversed Event tuples produce identical schedule entries and makespan in GEMM/FA tests. No compatibility adapter was added.

### FSV-014 — Exactness needs a complete optimality certificate

- **Status:** Design resolved; implementation/search-completion evidence pending.
- **Root cause:** “Exact” is not established by a best-known feasible schedule. Exhaustive search completion or an optimization solver's proven zero gap is required.
- **Impact:** Timeout/search exhaustion could otherwise be mislabeled exact.
- **Resolution:** Exhaustively enumerate all precedence-feasible permutations and apply serial SGS within the declared fixed-duration anonymous-resource domain. Return an ExactScheduleResult only after complete enumeration; budget exhaustion raises and returns no result. Cross-check tiny integer cases with independent bounded start-time enumeration.

### FSV-015 — Proposed external solver dependency is unapproved

- **Status:** Resolved for the first exact oracle; no dependency change made.
- **Root cause:** Preliminary Claude review recommended OR-Tools CP-SAT, but the project forbids new dependencies without explicit approval. OR-Tools is unavailable. SciPy `1.17.1` and its HiGHS-backed `milp` interface are available only as ambient host packages; the repository declares no dependency environment and has no existing solver imports.
- **Evidence:** A two-integer SciPy MILP completed with `status=0`, objective `2.0`, solution `[0.0, 2.0]`, and `mip_gap=0.0`; this validates the installed API only, not a scheduling formulation.
- **Impact:** The exact-oracle implementation plan cannot assume OR-Tools or silently depend on ambient SciPy. A solver's optimal status cannot prove that an incorrect formulation matches the Event model.
- **Resolution:** The first exact oracle uses only the Python standard library. SciPy/HiGHS and OR-Tools are not selected, imported, or declared. Any future solver remains a separately approved extension with formulation proof and tiny-case cross-checking.

### FSV-016 — Current report conflates dependency and schedule evidence

- **Status:** Design resolved; implementation pending.
- **Root cause:** `build_report()` sets `critical_path` equal to `SimulationResult.makespan`, even though the makespan includes resource-policy serialization beyond the dependency longest path. Its `resource_busy_time` also sums one duration per single-resource Event and has no demand weighting.
- **Impact:** The current report name can overstate a feasible schedule as a proof term, and the busy-time metric will become dimensionally incorrect once simultaneous demands are supported.
- **Resolution:** Report dependency critical path from SafeBound/graph evidence, exact optimum from `ExactScheduleResult`, feasible makespan/timeline from `SimulationResult`, and measured comparisons separately. Global and per-SM resource attribution is `duration * demand`; lifetime reservation evidence is separate and is not silently added to the first SafeBound.

### FSV-017 — Exact-engine review contains a corrected example but an unverified theorem adaptation

- **Status:** Design resolved; code-level proof obligations pending.
- **Root cause:** The first Claude exact-engine review computed a hand example as `7` although the resource-complete makespan is `8`. The correction pass fixed the example and recommended exhaustive serial SGS, but changed its characterization from generating every active schedule to generating only a dominant set without supplying verifiable theorem text. Its proposed induction also requires careful project-specific handling of float time, simultaneous demands, ties, and zero-duration nodes.
- **Impact:** The high-level engine recommendation is plausible, but its review text cannot itself serve as the Search-Coverage Gate proof.
- **Resolution:** The continuation directive authorizes completion with the reviewed dependency-free engine. `design.md` now gives the self-contained active-schedule/serial-SGS proof for float duration, simultaneous demand, ties, and half-open zero-duration intervals. GREEN still requires independent bounded time-indexed enumeration over tiny integer cases.

### FSV-018 — `tensor_all_ops` is analytical feature data, not measured counter evidence

- **Status:** Open evidence gap; prior interpretation corrected.
- **Root cause:** The CSV column name resembles a profiler quantity, but repository source computes the same field from padded shapes and CTA ratios for legacy MLP features. No collection script, counter identifier, raw profiler output, or environment metadata ties it to hardware counters.
- **Evidence:** The complete non-split Hopper `gemm_9_calculator.py` formula matches `tensor_all_ops` within `rtol=1e-12`, `atol=1e-6` for `40,632/40,632` rows. The calculator itself infers split/replication from CTA ratios.
- **Impact:** The column cannot validate physical issued work, partial-tile hardware behavior, or measured primitive calibration. Treating it as a counter would make R8/R11 circular.
- **Resolution required:** Keep logical work, explicit-policy issued work, legacy analytical feature work, and separately collected measured-counter work distinct. R8 implementation uses explicit policy metadata; R11 requires an authoritative counter/microbenchmark campaign or remains blocked.

### FSV-019 — Dependency acyclicity alone does not prevent lifetime resource deadlock

- **Status:** Core lifetime safety semantics resolved; fixed-priority scheduler completeness remains a documented WATCH.
- **Root cause:** Dependency acyclicity does not eliminate resource wait cycles. Cross-lifetime members can demand each other's held resources, and a fixed greedy priority can also admit a lifetime before an independent release prerequisite that needs the same exhausted resource.
- **Impact:** Without semantic separation, the scheduler can stall or double-count demand. Even after that correction, the greedy policy can raise no-progress on a graph that another event order could schedule; this affects scheduler completeness, not feasibility of returned outputs.
- **Resolution:** `EventGraph` rejects cross-lifetime member demand, `ResourceLifetime` owns reservation-to-transient demand normalization, and the scheduler admits additional transient demand atomically. Alternate-SM progress and genuinely unavailable no-progress are tested. For the independent-prerequisite counterexample, `SchedulingNoProgressError` remains an explicit policy/domain boundary. No backtracking, retry, second policy, or blanket graph rejection is added: `EventGraph` does not own `ResourceConfig`, and an unconditional dependency-cone rejection would reject the required alternate-SM feasible case. A future complete lifetime scheduler would require a separately approved design.

### FSV-020 — Ready-queue bookkeeping does not prove total scheduler complexity

- **Status:** Wave-3 measurement complete; broad asymptotic claims remain intentionally absent.
- **Root cause:** The shared-kernel review derived `O((V+E) log V)` while separately acknowledging eligible-SM scans. It also omitted repeated checks of blocked ready Events under simultaneous multi-resource demand and lifetime reservations.
- **Impact:** The scheduler rewrite could repeat the current mistake of presenting a partial complexity analysis as an end-to-end performance result.
- **Resolution:** `tests/performance/benchmark_event_scheduler.py` separately times normalized graph construction/validation, scheduling, and report assembly and reports the four frozen counters. The actual `58,467`-Event row measured graph build `0.720789447980s`, scheduling `23.005453476013s`, report assembly `0.678323030996s`, and primary pipeline `24.404565954988s`; counters were `5,491,878` ready-queue operations, `2,687,472` blocked rechecks, `2,587,872` placement checks, and `0` lifetime checks. The historical scheduler-time value was `115.882818766s`, giving a size-matched historical ratio of `4.748407284921x`. The stages are not identical, so this is not a controlled speedup study. No total O-notation or cycle-level speed claim is made.

### FSV-021 — Static cache order is a modeled input, not a hardware-universal trace

- **Status:** Design resolved for the initial model; measured equivalence remains open.
- **Root cause:** Concurrent workers do not imply one physical access order. Any pre-scheduling cache trace selects an abstract order and can produce more or fewer misses than another interleaving.
- **Impact:** The resulting fixed durations can support an exact optimum and SafeBound only for the declared manifest-order model, not a universal lower bound over arbitrary real-hardware cache arbitration.
- **Resolution:** Use one canonical manifest-order CacheAccess trace for every modeled provenance layer and label the theorem accordingly. Do not add the Claude-proposed isolated-worker cache path: overcounting misses can increase a resource-work term and is not a safe lower-bound relaxation. Hardware claims require separate matched evidence.

### FSV-022 — Whole-file line-length auditing misclassified pre-existing lines

- **Status:** Resolved on 2026-07-20.
- **Root cause:** A fresh helper scanned every line in files touched by Wave 1, while the recorded acceptance metric concerns newly added Python lines. Two long import lines in `event_simulator/__init__.py` already existed at `HEAD` and were therefore incorrectly attributed to this wave.
- **Impact:** The combined verification wrapper exited `1` even though `76/76` tests and `git diff --check` passed; treating that result as a production failure would trigger unrelated formatting work.
- **Resolution:** Compare only added Python lines from `git diff --unified=0`. The corrected audit reports `0` newly added lines over 88 characters. No code was reformatted, no exception was added, and the failed helper plus resolution are preserved in the Wave-1 test report. During Wave 4, one wrapper also invoked `python -m ast` with three paths even though that CLI accepts one input, then repeated the already-rejected whole-file length scope. A later wrapper inspected diff additions but failed to track the `+++ b/<path>` header, so long Markdown additions were misclassified as Python. The corrected parser uses `ast.parse` per file and checks added lines only while the current diff path ends in `.py`; `5/5` files parsed and the added-Python-line violation count remained `0`.

### FSV-023 — Per-SM proof-boundary review contained an incorrect SafeBound value

- **Status:** Resolved on 2026-07-20; the corrected review remains WATCH evidence.
- **Root cause:** The first independent review confused one Event's `2/3` share of a single SM's register capacity with the aggregate resource-time bound over three Events and two SMs.
- **Impact:** The stated test expectation `2/3` contradicted the accepted formula and could have driven a false production correction even though the Option-B placement counterexample itself was sound.
- **Resolution:** A bounded StepCode Claude correction verified `sum(duration * demand) / (sm_count * capacity) = 6 / 6 = 1.0`, aggregate-pool optimum `1.0`, and true placed optimum `2.0`. The exact oracle still rejects multi-SM nonzero per-SM demand, while SafeBound retains the `1.0` aggregate relaxation. No scaling factor, fallback, or additional topology model was introduced.

### FSV-024 — Initial Wave-2 tests contained one collection warning and two incorrect expectations

- **Status:** Resolved on 2026-07-20 before production implementation.
- **Root cause:** A lazy `itertools.product` object was passed directly to `pytest.mark.parametrize`; one permutation optimum omitted the long Event's resource serialization (`5.0` instead of `6.0`); one critical-path expectation ignored an independent duration-`10` Event (`8.0` instead of `10.0`).
- **Impact:** The warning would violate the clean TDD gate, and the two arithmetic errors would falsely reject correct production behavior.
- **Resolution:** Materialized the parameter cases, corrected the exact optimum to `6.0`, and corrected the graph critical path to `10.0`. The fresh focused run has `76` ordinary failures, `0` collection errors, and `0` warnings, all attributable to the intentionally missing Wave-2 APIs.

### FSV-025 — SafeBound failed when the resource-term collections were empty

- **Status:** Resolved on 2026-07-20.
- **Root cause:** `max(critical_path, *global_terms, *per_sm_terms)` becomes the one-argument call `max(critical_path)` when both mappings are empty. Python interprets a one-argument `max` call as an iterable form, so the float critical-path value raised `TypeError`.
- **Impact:** The first SafeBound GREEN attempt reported `4 failed, 48 passed`; every failing case used a valid resource-free configuration. Resource-bearing cases already passed.
- **Resolution:** Construct one tuple containing the critical path and all resource terms, then call `max` on that tuple. This directly models the mathematical set of proven terms, covers the empty-resource boundary without a special-case branch, and preserves fail-fast semantics. The rerun passed `52/52`; the combined Wave-2 suite passed `76/76`.

### FSV-026 — Wave-3 focused tests and benchmark paths crossed ownership boundaries

- **Status:** Resolved on 2026-07-20 before Wave-3 RED.
- **Root cause:** The Wave-3 command included `tests/integration/test_operator_simulation.py` even though its `operators.py` and `hardware_adapter.py` callers still use the deliberately removed legacy API and are assigned to Wave 4. `experiments.md` also named `benchmark_scheduler_scaling.py` while `plan.md` owned `benchmark_event_scheduler.py`.
- **Impact:** Running the operator integration in Wave 3 would fail before scheduler behavior and create pressure for either premature Wave-4 edits or a forbidden compatibility adapter. Two benchmark paths would duplicate the same evidence owner.
- **Resolution:** StepCode Claude returned **APPROVE** for hand-built EventGraph/ResourceConfig scheduler/report tests in Wave 3, retaining operator integration under Wave 4, and using only `tests/performance/benchmark_event_scheduler.py`. The review also approved one frozen SchedulerCounters value, zero-result empty scheduling, smallest-feasible-SM tie behavior, and deferral of a measured-comparison report parameter until its concrete type exists.

### FSV-027 — SafeBound counted lifetime-covered demand as transient work

- **Status:** Resolved on 2026-07-20.
- **Root cause:** The scheduler privately removed resources served by a lifetime reservation, while `SafeBoundEvaluator` summed raw `event.per_sm_demand`. With one reserved slot and two parallel covered members, the aggregate term became `2.0` although the feasible makespan was `1.0`.
- **Impact:** `SafeBound.bound <= modeled optimum` was false for an accepted lifetime graph, violating the inherited Safety Gate.
- **Resolution:** Added one `ResourceLifetime.transient_per_sm_demand()` owner operation and used it in both scheduler admission/release and SafeBound resource-time accounting. Covered demand is omitted with the relaxed reservation; additional endpoint/member transient demand remains counted; explicit-zero non-reservation entries remain unchanged. The reproduced term changed from `2.0` to `0.0`, feasible makespan remained `1.0`, and the 192-test Wave-1–3 regression passed.

### FSV-028 — Lifetime membership validation is not linear in graph size

- **Status:** WATCH; benchmark accounting corrected, implementation unchanged.
- **Root cause:** `EventGraph.__post_init__` calls reachability checks from the acquire endpoint and to the release endpoint for each lifetime member. In the worst case this is `O(M * (V + E))`, not one global `O(V + E)` pass.
- **Impact:** A lifetime-heavy graph can spend material time in construction/validation even when scheduler-local queue processing is efficient. A scheduler-only timer could misattribute or hide this cost.
- **Resolution:** The Wave-3 benchmark now times graph construction/validation separately from scheduling and report assembly. Its no-lifetime graph intentionally does not claim to measure the `O(M * (V + E))` lifetime-heavy case. No reachability refactor was added; any future optimization still needs its own design, RED cases, and equivalence proof.

### FSV-029 — Historical scheduler runtime environment is only partially recorded

- **Status:** Low-severity WATCH; documented and non-blocking for the Wave-3 checkpoint.
- **Root cause:** The six historical old-runtime constants originate from the parent task's reviewed scheduler evidence, whose report records `/usr/bin/python` `3.12.3`, no active conda/venv, and pytest `9.1.1`, but does not identify the host CPU or a standalone raw benchmark artifact for those six points.
- **Impact:** The parent names the first five values as legacy scheduler-time medians, while the new denominator includes graph construction/validation, scheduling, and report assembly. The ratio is useful size-matched historical context but is not a stage-matched or fully controlled machine-to-machine performance study and cannot support a cycle-level or `10000x` claim.
- **Resolution:** The Wave-3 benchmark and report name the exact parent source, record the available environment, preserve every absolute value, and label the ratio as a size-matched historical comparison only. Reproducing the retired implementation on a pinned host is not required by the current design and is not replaced by an invented stage or environment claim.

### FSV-030 — The benchmark CSV writer emitted CRLF on the Linux delivery path

- **Status:** Resolved on 2026-07-20 before commit.
- **Root cause:** Python's `csv.DictWriter` inherited the default Excel dialect, whose line terminator is `\r\n`. The initial untracked-text grep did not classify the carriage return as a blank character, but staged `git diff --check` correctly rejected all eight generated CSV lines as trailing whitespace.
- **Impact:** The numeric benchmark data and tests were correct, but the authoritative raw artifact could not pass the repository delivery gate. Manually editing only the CSV would allow the unique writer to reproduce the defect later.
- **Resolution:** Added an observed RED test that runs the unique benchmark writer on the exact small case and rejects carriage returns. Set only `lineterminator="\n"` on that `csv.DictWriter`, normalized the existing eight-row artifact while asserting eight replacements and zero remaining CR bytes, and reran the module and Wave-1--3 regressions. The focused module passed `12/12`; the full checkpoint passed `205/205`; the normalized artifact SHA-256 is `13dad9670800d8362c5c16f182b48255bf26e0c86cf0986b1156fe08e6a125f5`.

### FSV-031 — Wave-4 focused tests still construct the removed flat resource API

- **Status:** Resolved on 2026-07-20; production compatibility remains explicitly prohibited.
- **Root cause:** Wave 1 deliberately replaced `ResourceConfig({...})` with `ResourceConfig(global_capacities=..., sm_count=..., per_sm_capacities=...)`, while Wave-4-owned operator integration fixtures and legacy lowerers were intentionally deferred to their declared migration wave. The first Wave-4 combined command therefore fails during collection before exercising lowering behavior.
- **Impact:** The command reports `1` collection error and exit code `2`, so it is not a valid behavior RED for operator/hardware/validator implementation. Adding a one-dict constructor shim would hide the planned API break and violate the design/harness.
- **Resolution:** Migrated only the Wave-4 tests to the frozen two-level `EventGraph`/report and manifest-map contracts, without changing production or adding a compatibility shim. The authoritative focused command then collected `145` tests and produced `98` passes, `47` ordinary behavior failures, `0` setup errors, and `0` collection errors. The remaining failures identify only the planned production work; the old constructor and old `lower_gemm_v2` signature remain deliberately broken.

### FSV-032 — One newly added manifest assertion exceeded the line-length gate

- **Status:** Resolved on 2026-07-20 before staging.
- **Root cause:** The first final diff-scoped audit correctly measured a one-line generator-expression assertion in `tests/unit/test_gemm_manifest.py` at 90 characters, two above the accepted 88-character limit.
- **Impact:** Behavioral tests and production logic passed, but the Wave-4 delivery gate could not pass while the new test line violated the recorded style criterion.
- **Resolution:** Wrapped only the generator expression at its test owner without changing the assertion or production behavior. The exact focused test passed `1/1`; the complete static rerun parsed `14/14` changed/new Python files, found `0` added Python lines over 88 characters, and passed `git diff --check`. No formatter dependency, exception, fallback, or adjacent reformat was introduced.

### FSV-033 — Final unused-import audit treated a compiler directive as a runtime symbol

- **Status:** Resolved on 2026-07-20 before staging.
- **Root cause:** The inline AST checker collected every `ImportFrom` binding but detected usage only through loaded `Name` nodes. `from __future__ import annotations` changes compiler behavior and does not create a runtime use of the bound word `annotations`, so the checker produced a false positive.
- **Impact:** The first final static command exited before the downstream legacy/history/diff checks even though `operators.py` had no actual unused runtime import. Editing production to satisfy the faulty checker would have removed intentional annotation semantics.
- **Resolution:** Excluded only imports whose module is `__future__` from the unused-runtime-symbol audit and reran the complete gate. Actual unused imports are `0`; all `14/14` Python files parse; added lines over 88, forbidden hits, and diff errors are `0`; signature match is `1`; histories pass `19/19`. No repository source or test was changed for this checker-only defect.
