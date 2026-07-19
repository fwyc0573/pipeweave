# DES Refined Roofline Review and Remediation Progress

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Added the final post-document verification snapshot with authoritative timings, exit codes, and artifact-integrity results. |
| 2026-07-19 | Resumed the task, independently reran the final verification stack, and applied the user-directed ignored-path boundary. |
| 2026-07-18 | Closed Phase 7 with the formal report, final task-artifact audit, English summary, and checksum inventory. |
| 2026-07-18 | Recorded fresh final targeted/full/compile/validator/diagnostic evidence and the corrected hardware-smoke command. |
| 2026-07-18 | Recorded the precise README Small-category correction, post-fix review closure, and complete FA3 threshold branch coverage. |
| 2026-07-18 | Recorded internal source-documentation truthfulness and all-hardware adapter smoke validation. |
| 2026-07-18 | Recorded the post-fix public-value-object invariant repair and dead-import cleanup. |
| 2026-07-18 | Recorded documentation truthfulness, exhaustive validator partitioning, fresh full regression, and post-fix Small/L2 WATCH evidence. |
| 2026-07-18 | Recorded RED/GREEN evidence for all approved narrow code and validator corrections. |
| 2026-07-18 | Recorded the completed independent review gates and the approved narrow remediation boundary. |
| 2026-07-18 | Recovered the independent-review checkpoint and persisted matched-bound and scalability evidence. |
| 2026-07-18 | Recorded source/data audit findings and the fresh baseline test run. |
| 2026-07-18 | Initialized the review task and recorded the metric-contract decision. |

## Status

- Overall: Completed for the approved bounded remediation and user-directed scope reconciliation; broad scientific/architecture claims remain blocked or unproven, and R-027 is closed as a scope exclusion.
- Current phase: Phase 9 — Branch checkpoint and next-stage handoff in progress
- Completed phases: 8/9

## Session Log

### 2026-07-18 — Task initialization and metric-contract resolution

- **Motivation:** The requested optimization-gap formula conflicts with the time-domain lower-bound direction and would be negative for valid DES bounds.
- **Expectation:** Resolve the metric semantics before reviewing or changing validators, reports, or design documents.
- **Method:** Classified the work as complex code/design review, loaded the review/debug/TDD/planning skills, obtained an independent StepCode Claude metric analysis, and asked one structured user question through `omx question`.
- **Result:** The user selected the bounded-only contract: `optimization_gap = (actual-DES)/actual` plus `hardware_efficiency = DES/actual`. The first Claude verdict was WATCH, with no implementation BLOCK. A new durable task directory and all 11 base artifacts were created.

### 2026-07-18 — Source/data map and fresh baseline

- **Motivation:** Establish whether the current implementation and available evidence can support the four Refined Roofline claims before changing behavior.
- **Expectation:** Identify unit, structural, reporting, performance, and benchmark gaps; confirm the existing test baseline independently.
- **Method:** Inspected the DES modules, validators, hardware JSONs, legacy MLP/analytical path, datasets, e2e CSVs, docs, and commit history. Searched for named cycle-accurate comparators and claim evidence. Ran the full test suite from the repository root.
- **Result:** The issue register now contains R-004 through R-016. Available data does not contain a cycle-accurate DES comparator or a held-out multi-hardware DES study. The first timing command failed before pytest because `/usr/bin/time` is not installed; this known environment constraint was diagnosed from `task_memory/env_handbook.md`. Re-running with Bash `time` and `PYTHONPATH="$PWD"` passed: `74 passed in 2.76s`, process elapsed `3.759s`, user `2.482s`, system `0.096s`, exit code `0`.

### 2026-07-18 — Baseline timing-command correction

- **Motivation:** The initial reproducibility command could not run because it referenced a missing GNU executable.
- **Expectation:** Use an existing, documented repository recipe without installing dependencies or masking test failures.
- **Method:** Replaced `/usr/bin/time` with Bash's `time` keyword exactly as documented in `task_memory/env_handbook.md`; no code or environment package was changed.
- **Result:** The full baseline completed successfully with `74/74` tests passing. The failure was an environment-command issue, not a code or test failure.

### 2026-07-18 — Dimensionally corrected classical roofline audit

- **Motivation:** The existing `improvement_vs_roofline` result cannot be interpreted until the reference roofline uses the hardware schema's actual throughput units.
- **Expectation:** Quantify the error introduced by the validator and establish matched baseline statistics without modifying production code.
- **Method:** Evaluated all `10,800` valid H100 rows with chip-wide BF16 peak `989.429760 TFLOPS`, conventional BF16 A+B+C bytes, and the same measured `avg_duration`; compared with the current `4096 TFLOPS` interpretation.
- **Result:** The current code overstates peak compute by `4.139758238119x`. For `4,231` Large rows, corrected roofline violations were `0/4,231`, mean bound `1000.886758 us`, mean actual `1205.750795 us`, mean gap `0.213733935`, and median gap `0.194005585`; the invalid formula reported mean gap `0.765382219`. Across all H100 rows the corrected baseline had `160/10,800` violations, all in the Small category, so those rows require explicit rejection or a cache-aware measurement-boundary analysis rather than silent inclusion.

### 2026-07-18 — Independent-review checkpoint recovery

- **Motivation:** Resume from the prior model checkpoint without repeating expensive source and dataset analysis, while making the evidence durable under the task artifact taxonomy.
- **Expectation:** Preserve every reproduced counterexample and distinguish local fixes from architecture work requiring a separate approval gate.
- **Method:** Re-read all review-task artifacts, inspected current Git status and relevant source history, confirmed the two independent `code-reviewer` and `architect` lanes are still active, and transferred the checkpoint's matched-sample and scheduler-scaling measurements into `notes.md` and `issues.md`.
- **Result:** The durable issue register now includes R-017 through R-020. The current global verdict remains `REQUEST CHANGES`: lower-bound and tighter-than-roofline claims have direct counterexamples; `10000x` and empirical zero-shot remain unproven. Narrow TDD candidates are separated from deferred scheduler/cache/CTA architecture changes.

### 2026-07-18 — Matched DES-vs-classical and simulator-runtime audit

- **Motivation:** Determine whether structural DES is actually tighter than a corrected classical roofline on identical measured rows and quantify current design-space evaluation cost.
- **Expectation:** Both bounds remain valid; DES improves the relative gap where its modeled structural constraints add legitimate time; runtime remains practical at representative graph sizes.
- **Method:** Deterministically sampled `20` H100 rows per Large/Medium/Small category (`random_state=42`), passed dataset `tile_K`, measured event lowering plus scheduling with `perf_counter`, and compared DES/classical gaps only on the same actual measurement.
- **Result:** All `60` sampled DES and classical bounds were below actual. DES was tighter on `20/20` Large rows and `16/20` Medium rows, but `0/20` Small rows. Mean gaps were Large `19.704517508%` DES versus `21.586894783%` classical, Medium `43.573626188%` versus `47.475469259%`, and Small `52.141733893%` versus `34.975713588%`. Runtime was strongly graph-size dependent: a `58,467`-event Large row took `115.882818766s`; Large median was `0.307063607s` and mean `8.079464427s`. These results support only a bounded sample/category claim and expose a major DSE scalability problem; they do not establish `10000x` versus cycle-accurate simulation.

### 2026-07-18 — Independent review-gate closure and narrow-scope approval

- **Motivation:** Implementation must not begin while the scientific-validity and architecture reviews disagree about whether the current greedy schedule is a certified bound or whether the proposed fixes cross the user-approval boundary.
- **Expectation:** Obtain independent, evidence-aware verdicts; reconcile disagreements explicitly; separate reversible local corrections from blocked architecture work.
- **Method:** Completed the Codex native `architect` and `code-reviewer` lanes, supplied the exact scheduler-order, traffic-conservation, CTA-policy, corrected-roofline, L2-capacity, runtime, and bound-violation counterexamples to an adversarial StepCode Claude review, and then sent the exact file-level narrow TDD plan to a separate StepCode Claude scope reviewer.
- **Result:** The architect returned **BLOCK**, the code reviewer returned **REQUEST CHANGES**, and adversarial Claude returned **BLOCK** for public scientific acceptance and broad architecture. Claude explicitly withdrew its earlier greedy-lower-bound and unrestricted-tighter-than-roofline conclusions. A separate narrow-scope Claude review returned **APPROVE with WATCH**, permitting only the bounded comparison API, corrected classical units/boundary, cold unique A+B conservation, one-lane chip-wide L2 consistency, legacy GEMM factor-two correction, hardware fail-fast behavior, FA2/FA3 integration fixes, validator rejection accounting, and public-documentation corrections. Broad scheduler/bound/cache/residency/persistent/split-K/performance work remains blocked. The L2/cold-traffic WATCH requires numeric post-fix reporting, especially for small or output-heavy kernels.

### 2026-07-18 — Bounded comparison and legacy GEMM RED/GREEN cycles

- **Motivation:** The repository lacked a public implementation of the binding bounded metric contract, and the legacy GEMM lowering counted only `M*N*K` rather than `2*M*N*K` work.
- **Expectation:** Valid positive bounds produce finite complementary metrics; all invalid inputs and bound violations fail fast; one legacy GEMM tile reports the exact factor-two MMA count.
- **Method:** Added tests before production changes. The comparison RED first exposed the missing public API as `15` assertion failures; the legacy RED reproduced `256` instructions where `512` were required. Implemented a frozen `BoundComparison`, strict finite/positive validation, package export, and the one-line legacy work correction.
- **Result:** `tests/unit/test_bound_comparison.py` passed `15/15`; `tests/integration/test_operator_simulation.py` passed `8/8`. No `SimulationResult` is accepted or certified implicitly, and `des_bound == 0` remains invalid under the user-selected contract.

### 2026-07-18 — Hardware/L2 and cold-input conservation RED/GREEN cycles

- **Motivation:** Chip-wide L2 bandwidth was multiplied by `num_sms`, stores used the DRAM coefficient on an L2 resource, non-positive throughput became zero-duration work, and already-unique B bytes were divided below one mandatory cold read.
- **Expectation:** The aggregate L2 rate is represented exactly once; output stores use the L2 coefficient; required rates and operator types fail fast; cold input traffic equals unique A+B bytes and is monotonic under a fixed policy.
- **Method:** Wrote unit/integration tests first. Hardware RED produced `9 failed, 6 passed`, including the `132`-lane L2 mismatch, wrong store coefficient, zero/non-finite rates, and unknown operator type. Traffic RED observed `393,216 B` versus the required `524,288 B` and reproduced `M=129` traffic below `M=128`. Changed L2 to one chip-wide lane, selected the L2 coefficient for `GlobalStore`, removed zero-throughput fallbacks, restricted known operator types, and replaced the B reuse division with cold unique A+B conservation.
- **Result:** Hardware tests passed `19/19`; GEMM v2 integration tests passed `12/12`. The `tile_k` docstring now states that the parameter is carried but behaviorally inert; no cache hierarchy, warm-cache fallback, or empirical factor was added.

### 2026-07-18 — FlashAttention and GEMM-validator RED/GREEN cycles

- **Motivation:** FA2 called the reused binary-search API with scalar values where arrays were required, failed to unpack its tuple, FA3 used a drifted schedule threshold, and the GEMM validator mixed units/boundaries while silently discarding unsupported rows and unexpected failures.
- **Expectation:** FA2 ragged/paged paths execute; FA3 matches the canonical threshold; malformed attention inputs fail fast; validation uses chip-wide compute plus cold A+B HBM and C-to-L2 boundaries, passes `tile_K`, rejects unsupported launch policies explicitly, propagates unexpected errors, and computes tightness only on both-valid pairs.
- **Method:** Added integration/unit tests before changing implementation. FA RED produced `8` failures, including the exact `TypeError: object of type 'int' has no len()`, canonical task count `182` versus current `91`, and missing validation. Validator RED produced `8/8` failures covering all required branches. Corrected the FA2 call contract and tuple unpack, aligned the FA3 formula, added exact attention/head/length validation, introduced explicit `UnsupportedGemmRow` reasons, removed broad exception handling and the gap clamp, and added paired-only summaries plus simulator-runtime capture. A subsequent test failure revealed that pure-numeric `pandas.iterrows()` promotes integers to `float`; the root fix accepts finite integer-valued numerics while still rejecting fractional, non-finite, and bool values.
- **Result:** FA integration tests passed `18/18`; validator unit tests passed `10/10`; the combined affected suite passed `82/82` in `2.59s`. Unsupported split-K and CTA-policy rows are excluded with named counts, never silently treated as modeled or included in the acceptance denominator.

### 2026-07-18 — Public-documentation truthfulness RED/GREEN cycle

- **Motivation:** `README.md` and both DES design documents still presented experimental or absent behavior as established, including universal lower-bound, universal tighter-than-classical, `10000x`, empirical zero-shot, cache/residency, and metric-attribution claims.
- **Expectation:** Public documents use one explicit `Established` / `Experimental` / `Unproven` / `Blocked` vocabulary, expose only the bounded metric formula, and distinguish an explanatory greedy schedule from a certified theoretical lower bound.
- **Method:** Added `tests/unit/test_des_documentation.py` before editing the documents. The RED run produced `5 failed, 1 passed`. Updated the three existing documents in place, added or maintained their Modification History tables, published `compare_des_bound(...)`, and removed or downgraded claims that lack matched evidence.
- **Result:** The documentation contract passed `6/6`. The public position is now a deterministic, mechanistic, event-level analytical prototype; it does not claim that `SimulationResult.makespan` is a certified bound or that the four scientific goals are already validated.

### 2026-07-18 — Exhaustive validator-category partition correction

- **Motivation:** The validator's Large/Medium/Small categories silently omitted H100 rows that met none of the three predicates, violating the no-silent-skip and exhaustive-accounting gates.
- **Expectation:** Every input row belongs to exactly one disjoint category and every sampled, evaluated, unsupported, and violating row is visible in the reported denominator.
- **Method:** Added a failing unit test for a disjoint exhaustive partition, identified the missing complement as `Other`, and implemented `partition_categories(...)` so `Other` is the exact remainder rather than a heuristic fourth predicate.
- **Result:** The validator tests passed `11/11`. The H100 partition is now exhaustive: Large `4,231`, Medium `1,798`, Small `3,562`, Other `1,209`, totaling `10,800`; the prior implementation silently omitted `1,209/10,800` rows (`11.194444%`).

### 2026-07-18 — Fresh full regression and compile validation after bounded fixes

- **Motivation:** Targeted RED/GREEN cycles do not establish that the combined changes preserve unrelated repository behavior or that all edited Python files compile.
- **Expectation:** The complete test tree passes with zero failures and all affected source/test modules compile under the recorded environment.
- **Method:** Set `PYTHONPATH="$PWD"`; ran `time python -m pytest tests -q` using Bash `time`; then ran `python -m compileall -q event_simulator tests/unit tests/integration tests/validation`.
- **Result:** The full suite passed `127/127` in pytest-reported `2.72s`; process elapsed `3.176s`, user `4.763s`, system `0.127s`, exit code `0`. `compileall` returned exit code `0` with no output. Environment was `/usr/bin/python` `3.12.3`, pytest `9.1.1`, pandas `3.0.3`, numpy `2.4.6`, with no active conda environment.

### 2026-07-18 — Post-fix matched H100 validator evidence

- **Motivation:** Code correctness tests alone cannot establish the scientific claims; the revised resource, traffic, launch-policy, and baseline contracts must be evaluated against measured rows with violations and unsupported cases visible.
- **Expectation:** Supported rows are evaluated without hidden skips; both DES and classical violations are counted; category-level actual, predicted, error, tightness, and simulator-runtime values are recorded without converting a violation into an optimization gap.
- **Method:** Ran `python tests/validation/validate_gemm_v2.py` with `PYTHONPATH="$PWD"` and the corrected chip-wide compute, cold A+B HBM, C-to-L2, dataset `tile_K`, split-K rejection, and exact reconstructed-grid policy. Collected an additional deterministic diagnostic for mean actual/DES/classical values on the same samples.
- **Result:** Only `4,246/10,800` H100 rows (`39.314815%`) match the supported launch policy; `6,554/10,800` are CTA mismatches and all `437/437` split-K rows are unsupported. Sampled results were: Large `24/200` evaluated, `0` DES violations, mean actual/DES/classical `39.014666667/31.429699238/29.104068002 us`, DES/classical MAPE `25.136598599%/31.453028079%`, DES tighter `24/24`; Medium `83/100`, `0` violations, `22.669559036/15.055291025/13.544613415 us`, `44.382446381%/50.961102480%`, DES tighter `80/83` with `3` equal; Small `62/100`, `4` DES and `4` classical violations, `13.203912903/9.500076111/9.495655200 us`, both-valid DES/classical mean gaps `40.925578445%/41.004775343%`, DES strictly tighter `1/58`; Other `26/100`, `0` violations, `16.843523077/11.099008314/9.963211561 us`, `42.470372669%/49.920482044%`, DES tighter `26/26`. Validator process elapsed was `3.528s`, user `5.186s`, system `0.091s`. The evidence refutes an unrestricted tighter-than-classical or universal-bound claim and does not supply a cycle-accurate comparator.

### 2026-07-18 — One-lane L2 and cold-traffic WATCH audit on Small kernels

- **Motivation:** The independent scope reviewer approved the physical consistency corrections with a WATCH that they could materially affect small or output-heavy kernels and increase measured-bound violations when the dataset is not cold-cache matched.
- **Expectation:** Quantify the direction and scale of the change on an identical deterministic supported-Small sample; do not interpret improved aggregate error as proof of bound validity.
- **Method:** Reconstructed the prior-equivalent contract (`unique B / reuse`, `num_sms` L2 lanes, store charged with the DRAM coefficient) and compared it row-by-row against the new contract (cold unique A+B, one chip-wide L2 lane, store charged with the L2 coefficient) on the same `100` supported Small rows.
- **Result:** Mean actual latency was `13.792804000000 us`; old-equivalent mean was `8.654575482592 us`; new mean was `9.962412046531 us`; mean absolute increase was `1.307836563939 us`; mean per-row increase ratio was `40.2620008539%`; maximum increase ratio was `195.4199574412%`. MAPE improved from `46.2212474501%` to `34.6070571352%`, but violations increased from `6` to `8`. This confirms that the old contract undercounted its declared cold traffic/capacity and that the revised candidate is not a valid bound for every measured Small row. These aggregate results alone do not prove warm-L2 residency or isolate cache state from scheduler and measurement-provenance effects; no clamp, scale, fallback, or silent exclusion was added.

### 2026-07-18 — Post-fix comparison-value-object invariant RED/GREEN cycle

- **Motivation:** StepCode Claude found that `BoundComparison` was publicly exported but its generated dataclass constructor accepted arbitrary times and arbitrary derived metrics, allowing callers to bypass `compare_des_bound(...)` and create an internally invalid public result.
- **Expectation:** Every public construction path enforces the same finite-positive and `des_bound <= actual_time` contract, and derived metrics cannot be supplied inconsistently by a caller.
- **Method:** Added two tests before production changes. The RED run failed `2` new tests because direct construction required caller-supplied `optimization_gap` and `hardware_efficiency` and performed no invariant validation. Moved the invariant to frozen `BoundComparison.__post_init__`, made both derived metrics `init=False`, computed them from validated times, and reduced `compare_des_bound(...)` to delegation through that single invariant-owning value object. Separately removed the now-unused `compute_l2_hit_ratio` import from `operators.py`.
- **Result:** The focused suite passed `17/17`; the integration-plus-comparison regression passed `55/55` in `2.21s`. Direct construction can no longer supply forged derived metrics, invalid bounds raise `ValueError`, and no public constructor path certifies bound provenance beyond the caller's explicit numeric input.

### 2026-07-18 — Internal source-documentation truthfulness RED/GREEN cycle

- **Motivation:** Although the three public Markdown documents had been corrected, internal source docstrings and comments still stated that an estimated L2 ratio “never causes DES_time > actual_time,” that XU was “safely omitted for roofline bound,” and that zero fixed overhead “ensures the bound.” Those statements contradict the demonstrated order-dependent scheduler and measured violations.
- **Expectation:** No maintained source documentation certifies a composed heuristic schedule from optimistic primitive choices alone.
- **Method:** Extended the documentation contract test before editing source comments. The RED run failed `1` test on the exact legacy guarantee. Reworded `structural.py`, `hardware_adapter.py`, and the FlashAttention lowering docstring to distinguish idealized estimates and omitted work from bound certification; no executable behavior changed.
- **Result:** The documentation/source contract passed `7/7`. Public and internal descriptions now agree that cache ratios, peak rates, and omitted overhead/XU work do not independently prove a composed latency bound.

### 2026-07-18 — All-hardware adapter smoke validation

- **Motivation:** Fail-fast rate validation now checks every emitted primitive capability, so repository hardware JSONs outside the H100 test path could regress if required positive fields were absent.
- **Expectation:** Every checked-in hardware specification loads, derives all primitive calibrations, and produces each known operator resource configuration without fallback.
- **Method:** Ran a direct Python smoke loop over all `hardware/*.json` and the five supported operator types. The first diagnostic invocation incorrectly passed the keyword-only `operator_type` positionally and failed all `11` rows with the same caller `TypeError`; after diagnosing the command error, reran with `operator_type=name` and no code change.
- **Result:** The corrected command passed `11/11` hardware files; each produced `22` calibration coefficients and `5/5` resource configurations. The initial failure was a diagnostic-script invocation error, not a repository defect, and no fallback or environment change was introduced.

### 2026-07-18 — README Small-category evidence correction

- **Motivation:** The README initially summarized the Small sample as consistently looser, but the larger post-fix matched sample contained one strictly tighter row and many exact ties; the prose no longer matched the current evidence.
- **Expectation:** Public evidence must reproduce the paired counts exactly and must keep bound violations separate from tightness comparisons.
- **Method:** Added a documentation assertion that rejects the stale phrase, then replaced it with the current sampled counts from the matched validator.
- **Result:** README now reports `1/58` DES strictly tighter, `29/58` classical strictly tighter, `28/58` equal, and `4` Small DES violations. The documentation contract passes and no category-level result is generalized globally.

### 2026-07-18 — Post-fix independent review closure

- **Motivation:** Completion requires a reviewer lane independent from the authoring path and a separate cross-model review of the bounded implementation and scientific claims.
- **Expectation:** No Critical/Important bounded defect remains; any broad scientific or architectural shortfall remains explicitly blocked rather than silently accepted.
- **Method:** StepCode Claude reviewed the current diff and returned `APPROVE with WATCH`; its bounded findings were the public `BoundComparison` invariant and one dead import, both resolved before the final review. The Codex native `code-reviewer` then reran `92` targeted tests, `130` full tests, the validator, the `11`-hardware smoke probe, and `git diff --check` in a read-only lane.
- **Result:** The native reviewer returned `APPROVE WITH WATCH` for bounded remediation with `0` new Critical and `0` new Important findings. It retained BLOCK for universal lower-bound, global tighter-than-classical, `10000x`, and empirical zero-shot claims. Its non-blocking WATCH items were experimental FA2 `cta_kv=64`, explicit coverage of the FA3 threshold's high branch, and inclusion of absolute time scales in the formal test report.

### 2026-07-18 — FA3 high-threshold branch coverage

- **Motivation:** The existing regression distinguished the old formula from the canonical formula on the `<=8192` branch but did not directly assert the `>8192` branch selected a shared schedule.
- **Expectation:** Both sides of the changed schedule-selection branch are executed without creating a prohibitively large task graph.
- **Method:** Added a focused integration test that replaces only the reused scheduler with a capture stub, supplies a canonical work count of `8,193`, and checks the exact `same_schedule_for_all_heads=True` argument. No production behavior changed.
- **Result:** `tests/integration/test_fa_simulation.py` passed `19/19` in `1.75s`; the canonical threshold now has explicit coverage on both sides.

### 2026-07-18 — Fresh final regression and scientific evidence run

- **Motivation:** The earlier `127/127` run predated direct-construction, source-documentation, README-evidence, and FA3 high-threshold tests, so it could not be used as final completion evidence.
- **Expectation:** Every changed path and the complete repository pass in the recorded environment; the matched validator reproduces deterministic counts and absolute scales; compilation and cross-hardware construction remain clean.
- **Method:** With `/usr/bin/python` `3.12.3`, pytest `9.1.1`, pandas `3.0.3`, numpy `2.4.6`, no conda environment, `PYTHONPATH="$PWD"`, and bytecode/pytest caches disabled, ran the `93`-test targeted set, full `tests/`, `compileall`, the H100 validator, an absolute-time/violation diagnostic, the scheduler-order counterexample, the Small old/new resource-traffic audit, and an `11`-hardware adapter smoke.
- **Result:** Targeted passed `93/93` in `2.66s` (elapsed `3.114s`); full regression passed `131/131` in `2.75s` (elapsed `3.281s`); compileall exited `0` in `0.108s`; validator exited `0` in `3.583s`. The deterministic validator reproduced `4,246/10,800` supported rows and four Small violations. Absolute actual/DES/classical scales, MAE, MAPE, both-valid gaps, per-row violations, runtimes, and the Small old/new comparison are recorded in the formal test report.

### 2026-07-18 — Final hardware-smoke assertion correction

- **Motivation:** The final smoke added an explicit one-L2-lane assertion beyond the prior load/calibration/config checks.
- **Expectation:** The assertion uses the actual `ResourceConfig` public surface and passes for GEMM/GEMM-v2 across all hardware files.
- **Method:** The first read-only command incorrectly called a nonexistent `ResourceConfig.capacity(...)` method and raised `AttributeError` before producing results. Inspected `ResourceConfig`, corrected the command to `config.capacities["l2_bandwidth"]`, and reran without changing repository code.
- **Result:** The corrected command passed `11/11` hardware files; each produced `22` calibration coefficients and `5/5` known operator resource configs, with one chip-wide L2 lane for GEMM/GEMM-v2. The failure was a diagnostic-command API typo, not a simulator/test defect.

### 2026-07-18 — Task artifact and delivery closure

- **Motivation:** Passing code tests is insufficient under the task governance contract; the durable task record, English summary, exact deliverable inventory, and checksum verification must also be complete and internally consistent.
- **Expectation:** All `11` required base artifacts plus the formal test report exist; every Markdown file has Modification History; all requirements, progress, review, issue, summary, and hash constraints pass; no draft status remains.
- **Method:** Ran a Python artifact-structure audit, replaced the draft English summary with the final claim/test/deliverable matrix, generated a SHA-256 manifest for every delivered source/test/public/task file except the self-referential manifest, and verified the manifest from the repository root.
- **Result:** The final task directory contains `13` files: `11` required base artifacts, one formal test report, and one checksum manifest. Governance records contain `9` `[Original Request]` items, `24` complete progress entries, `8` review entries with all required fields, and contiguous issues `R-001` through `R-026`. The checksum manifest is the authoritative self-hash source for `summary.md`; no task remains pending inside the approved bounded scope.

### 2026-07-19 — Resume audit and historical metrics

- **Motivation:** The user requested task recovery after an interruption, while the prior records claimed bounded remediation was complete. Completion needed fresh evidence rather than reliance on the prior session's timings.
- **Expectation:** Reproduce the changed-path and full regression results, compilation, matched validator, hardware-adapter smoke, and diff checks without expanding into unrelated architecture work.
- **Method:** Re-read the task artifacts and Git history, then ran the targeted suite (`93` tests), full suite (`131` tests), `compileall`, the H100 validator, the `11`-hardware smoke loop, and `git diff --check`. The historical path check from that prior session is retained only as historical evidence; it is not part of the current user-directed scope.
- **Result:** Targeted `93/93` passed in `8.52s` (shell elapsed `9.741s`); full `131/131` passed in `2.76s` (shell elapsed `3.225s`); compilation exited `0` (`0.265s`); validator exited `0` (`3.618s`); hardware smoke passed `11/11` files with `22` calibration coefficients and `5/5` configs each; `git diff --check` exited `0`. The bounded code scope remained complete, and the active task now excludes the historical path per explicit user instruction.

### 2026-07-19 — Resume artifact reconciliation

- **Motivation:** Adding the recovery evidence and R-027 changed task governance documents, so the previous checksum and structural-audit snapshot was no longer authoritative.
- **Expectation:** Keep the required 11 base artifacts plus report/manifest, preserve all mandatory history and audit fields, maintain contiguous issue IDs, and verify every manifest entry from the repository root.
- **Method:** Recomputed the 28-entry SHA-256 manifest (excluding the manifest itself), ran `sha256sum -c`, and ran an inline artifact audit for required files, Modification History, `[Original Request]` tags, progress/review field completeness, and issue-ID continuity.
- **Result:** All `28/28` checksums passed; `11/11` base artifacts exist; `12/12` Markdown files have Modification History; `9` original-request tags, `26` complete progress entries, `9` complete review entries, and contiguous `R-001`–`R-027` issues were verified. Phase 8 is closed for the approved bounded scope; the later user instruction reclassifies R-027 as a closed scope exclusion.

### 2026-07-19 — Final post-document verification

- **Motivation:** The final documentation reconciliation changed the report, summary, notes, progress, and review records after the earlier resume snapshot, so the older timing values and checksum manifest could not remain the authoritative completion evidence.
- **Expectation:** Fresh targeted/full tests, compilation, the H100 validator, hardware smoke, whitespace validation, and checksum verification complete successfully against the final files; the exact observed numeric timings are recorded without replacing historical measurements.
- **Method:** Read the completed session `97006` output and captured its complete command stack: targeted pytest, full pytest, `compileall`, H100 validator, all-hardware smoke, `git diff --check`, and `sha256sum -c`. The historical path was excluded from the active closure by explicit user instruction.
- **Result:** Targeted `93/93` passed in pytest `2.63s` (shell elapsed `3.088s`, user `4.996s`, system `0.169s`); full `131/131` passed in pytest `2.65s` (shell elapsed `3.118s`, user `4.739s`, system `0.116s`); `compileall` exited `0` in `0.046s`; the validator exited `0` in `3.401s` (user `5.322s`, system `0.080s`); hardware smoke passed `11/11`; `git diff --check` and all `28/28` checksum entries passed. The bounded remediation is complete, R-027 is a closed scope exclusion, and the broad architecture BLOCK remains unchanged.

### 2026-07-19 — User-directed ignored-path and delivery-boundary reconciliation

- **Motivation:** The user explicitly instructed the agent to ignore the historical `=10.1` path and to deliver the current branch before entering the next stage.
- **Expectation:** The path does not affect code review, validation, staging, or task completion; only confirmed DES artifacts are prepared for commit and push.
- **Method:** Reclassified R-027 as a scope exclusion, removed path existence/preservation checks from the active closure criteria, preserved the path-free staging rule, and retained the two-contract `design.md`/`harness.md` boundary.
- **Result:** R-027 is closed as a non-blocking user-directed exclusion. No operation targeted the path. The branch remains ready for independent pre-commit review and explicit-file staging.

### 2026-07-19 — Pre-commit Claude review and staging-scope adjudication

- **Motivation:** The user required an independent Claude review before branch delivery and a clean handoff into the next stage.
- **Expectation:** The review must detect over-defensive or redundant implementation, confirm the two-contract boundary, and identify any staging or next-stage risk before commit.
- **Method:** Ran `omx ask claude` with the binding `design.md`/`harness.md` context. Claude returned **APPROVE** with no Critical findings, one non-blocking numpy/pandas integer-boundary WATCH, and cosmetic WATCH items; it recommended staging only source/tests. Reconciled that recommendation against the task-artifact governance and user request.
- **Result:** The bounded code/test scope is approved. The primary lane will stage the completed task records and environment handbook as durable deliverables, exclude `.omx/` runtime artifacts and the user-ignored path, and defer the integer-boundary cleanup to the next stage rather than adding defensive code now.

### 2026-07-19 — Fresh pre-commit verification stack

- **Motivation:** Documentation reconciliation and the independent Claude review changed the delivery checkpoint, so all acceptance evidence had to be rerun from the current bytes before staging.
- **Expectation:** Targeted/full tests, compilation, matched validation, hardware smoke, checksums, and whitespace checks pass without changing production behavior or expanding the ignored-path scope.
- **Method:** Ran the targeted `pytest` selection, full `pytest` suite, `compileall`, H100 validator, all-hardware adapter smoke, the 28-entry checksum manifest, and `git diff --check` using the environment recipes in `task_memory/env_handbook.md`.
- **Result:** Targeted `93/93` and full `131/131` passed; compile exit `0`; validator exit `0` with `4,246/10,800` supported rows and four Small violations visible; hardware smoke `11/11`; checksums `28/28`; diff check exit `0`. The branch is ready for explicit staging and Lore-protocol commit; the historical `=10.1` path remains outside scope.
