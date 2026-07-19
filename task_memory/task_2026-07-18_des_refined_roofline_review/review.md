# DES Refined Roofline Review and Remediation Review Log

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Added the final post-document verification review entry with session `97006` timing, checksum, and user-directed scope evidence. |
| 2026-07-19 | Added the independent resume-audit checkpoint, fresh verification evidence, and the user-directed ignored-path disposition. |
| 2026-07-18 | Recorded the post-fix StepCode Claude review, closed its bounded findings, and captured the final native code-review verdict and WATCH items. |
| 2026-07-18 | Recorded the two-lane code-review synthesis and Claude approval of the narrow implementation scope. |
| 2026-07-18 | Recorded the structural Claude challenge, adversarial correction, and independent architecture BLOCK. |
| 2026-07-18 | Recorded the independent Claude metric-semantics review. |

## Review Entry — Metric Semantics

- **Target Component/Phase:** Optimization-gap definition and Phase 1 requirements gate.
- **Reviewer Agent Identity:** StepCode Claude `claude-opus-4-6[1m]`, effort `max`; artifact `.omx/artifacts/claude-you-are-the-first-independent-reviewer-for-a-des-refined-roo-2026-07-18T14-45-05-448Z.md`.
- **Inspected Artifacts:** User goal statement, existing lower-bound invariant, current `(actual-DES)/actual` definition, and the requested `(DES-actual)/DES` expression.
- **Identified Issues/Anomalies:** Verdict **WATCH**. The requested literal time-domain expression is non-positive and unbounded below for valid lower bounds. In performance-rate space, the scientifically meaningful normalized gap is algebraically equivalent to `(actual_time-DES_time)/actual_time`.
- **Remediation/Verification Code Actions Taken:** No code was changed. The user selected the bounded-only contract through `omx question`; the decision is captured in `requirements.md`, `design.md`, and `harness.md`. Code/docs consistency will be checked during the source audit.

## Review Entry — Initial Structural Challenge

- **Target Component/Phase:** GEMM v2 structural semantics, scheduler composition, resource units, and the four public Refined Roofline claims during Phase 3.
- **Reviewer Agent Identity:** StepCode Claude `claude-opus-4-6[1m]`, effort `max`; artifacts `.omx/artifacts/claude-you-are-the-second-independent-reviewer-for-the-des-refined--2026-07-18T15-03-34-976Z.md` and `.omx/artifacts/claude-you-are-the-second-independent-reviewer-for-the-des-refined--2026-07-18T15-09-57-161Z.md`.
- **Inspected Artifacts:** `docs/des_design_rules.md`, `docs/event_simulator_design.md`, DES hardware adapter/operator/scheduler/report/structural modules, GEMM and hardware tests, the validator, and the task evidence available before the scheduler and traffic counterexamples were supplied.
- **Identified Issues/Anomalies:** Verdict **WATCH** / **APPROVE with WATCH** for a narrow remediation plan. Claude correctly confirmed the dead `tile_k` behavior, zero-duration admission labels, useful-work-only partial tiles, L2 lane/rate mismatch, `GlobalStore` mismatch, aggregate rather than literal L2 splitting, and near-quadratic scheduler scan. Its assertion that the greedy schedule remained lower-bound-safe and its unrestricted tighter-than-classical PASS were not accepted: they were later refuted by the `21.0` versus `11.0` same-DAG counterexample, corrected roofline units, traffic-conservation failure, launch-metadata mismatch, and observed DES violations. The second artifact also recommended silently rejecting every positive `tile_k`; that recommendation was not adopted because it would make all measured positive-`tile_K` rows unsupported without resolving the model contract.
- **Remediation/Verification Code Actions Taken:** No repository code was changed from this review. Confirmed findings were added to `issues.md` and `harness.md`. Disputed conclusions were explicitly sent back to a separate adversarial Claude pass rather than being copied into the implementation plan.

## Review Entry — Independent Architecture and Scientific-Validity Review

- **Target Component/Phase:** Event IR, greedy scheduler, GEMM v2 memory/launch semantics, report contract, FlashAttention integration, hardware fail-fast behavior, validation evidence, and Phase 3 architecture gate.
- **Reviewer Agent Identity:** Codex native `architect` lane `/root/des_architect`, independent read-only context.
- **Inspected Artifacts:** All DES source modules; relevant unit, integration, and validation tests; hardware JSONs; GEMM dataset schema and H100 rows; both public design documents; README; legacy GEMM and FA calculators; task evidence and reproducible counterexamples.
- **Identified Issues/Anomalies:** Architecture status **BLOCK**. The greedy list scheduler returns an input-order-dependent feasible schedule, which is generally an upper-bound witness for the modeled optimum rather than a lower-bound evaluator. Unique B traffic is divided below one cold read and produces a workload-monotonicity failure. H100 `cta_count` mismatches the reconstructed tile grid on `6,554/10,800` rows and all `437/437` split-K rows are unsupported. The H100 store path represents `442,506,240 B/us`, `50.170775510204x` declared L2 bandwidth. The reviewer also confirmed the classical roofline unit error, O(V^2)-like scheduling, missing public metric API, unproven cycle-accurate and zero-shot claims, FA2 argument failure, FA3 threshold drift, and zero-rate hardware fallback.
- **Remediation/Verification Code Actions Taken:** The BLOCK was accepted. It prevents calling `SimulationResult.makespan` a certified theoretical bound and prevents broad scheduler/residency/cache/persistent/split-K architecture work in this task. It does not prevent narrow TDD fixes for documentation honesty, validator correctness, bounded metric computation, traffic conservation under an explicitly cold contract, L2 unit consistency, arithmetic defects, and fail-fast behavior. No file was modified by the architect lane.

## Review Entry — Adversarial Claude Re-adjudication

- **Target Component/Phase:** Re-evaluation of the prior Claude WATCH after supplying scheduler-order, traffic, CTA-policy, bound-violation, corrected-roofline, and L2-capacity evidence.
- **Reviewer Agent Identity:** StepCode Claude `claude-opus-4-6[1m]`, effort `max`; artifact `.omx/artifacts/claude-you-are-the-adversarial-follow-up-reviewer-for-the-same-des--2026-07-18T15-13-26-785Z.md`.
- **Inspected Artifacts:** The prior Claude conclusions plus the exact `21.0` versus `11.0` scheduler reproduction, unique-B and `M=128 -> 129` monotonicity reproduction, H100 launch-metadata counts, `5/500` DES violations, corrected `989.42976 TFLOPS` baseline, matched 20-row/category results, and L2 `50.1708x` capacity mismatch.
- **Identified Issues/Anomalies:** Verdict **BLOCK** for public scientific acceptance and broad implementation. Claude explicitly retracted its earlier greedy-lower-bound and unrestricted tighter-than-classical conclusions. It classified the schedule as a feasible upper bound on the modeled optimum but neither a proven lower nor upper bound relative to actual hardware. It approved narrow docs, validator, metric, classical-unit, and L2 unit fixes. One wording error in the artifact says Large CTA mismatch is a `89.5% match`; the reproduced value is `3,788/4,231 = 89.529662% mismatch`. Its suggestion to add a split-K parameter stub was rejected because a signature-only stub would conceal missing replicated work and reduction semantics; the validator will explicitly reject unsupported split-K rows instead.
- **Remediation/Verification Code Actions Taken:** Broad work remains stopped. The scientific claim matrix is constrained to FAIL/PARTIAL/UNPROVEN as supported by evidence. A fourth Claude pass was launched solely to adjudicate the exact narrow file-level remediation plan, especially whether restoring unique cold A+B traffic is a safe local correction rather than an unapproved cache-hierarchy redesign.

## Review Entry — Independent Code/Spec Review

- **Target Component/Phase:** Code/spec/security/quality lane for all DES modules, validators, tests, public docs, reused FA calculators, H100 configuration, and task evidence.
- **Reviewer Agent Identity:** Codex native `code-reviewer` lane `/root/des_code_reviewer`, independent read-only context.
- **Inspected Artifacts:** `23` files/artifact groups covering `README.md`, both DES design documents, every core `event_simulator/` module, unit/integration/validation tests, FA2/FA3 calculators, `hardware/H100.json`, measurement data, and task review records.
- **Identified Issues/Anomalies:** Recommendation **REQUEST CHANGES**. CRITICAL findings were the non-bound greedy scheduler, cold-B traffic conservation failure, and invalid classical roofline comparison. HIGH findings were the `50.1708x` L2 capacity mismatch, `60.685%` H100 CTA mismatch plus all `437/437` split-K rows unsupported, validation exception swallowing/skips/clamp, zero-rate hardware fallback, and FA2/FA3 integration drift. MEDIUM findings included legacy GEMM `2x` work undercount, near-quadratic scheduling, overstated wave/partial semantics, and aggregate lane-time being mislabeled as attribution. The reviewer recommended allowing narrow metric/validator/L2/arithmetic/fail-fast/FA/docs work while deferring the same broad architecture identified by the architect.
- **Remediation/Verification Code Actions Taken:** No file was modified by the reviewer. One reviewer suggestion allowed a zero bound, but the binding user contract is stricter (`0 < DES_bound <= actual_time`) and takes precedence. Under the deterministic code-review synthesis rule, `code-reviewer = REQUEST CHANGES` plus `architect = BLOCK` yields final pre-remediation verdict **REQUEST CHANGES**.

## Review Entry — Narrow Implementation-Scope Approval

- **Target Component/Phase:** Exact file-level TDD remediation sequence after accepting the architecture BLOCK.
- **Reviewer Agent Identity:** StepCode Claude `claude-opus-4-6[1m]`, effort `max`; artifact `.omx/artifacts/claude-you-are-the-independent-implementation-scope-reviewer-after--2026-07-18T15-23-02-024Z.md`.
- **Inspected Artifacts:** The binding scheduler BLOCK and the proposed bounded comparison, validator, cold-input traffic, L2 unit, legacy GEMM, hardware fail-fast, FA integration, and documentation fixes, together with the explicit broad-deferred list.
- **Identified Issues/Anomalies:** Verdict **APPROVE** with one **WATCH** for the one-lane chip-wide L2 correction on output-heavy/small kernels. Claude explicitly approved restoring unique A+B cold-HBM traffic as a narrow conservation repair, not a cache-hierarchy implementation. Its statement that increasing the cold traffic would make the bound “safer” and fix violations was not adopted: a larger time value is a tighter candidate and may increase violations against warm-cache measurements. The accepted reason is traffic conservation under the explicit cold-start contract, while any observed violation remains evidence that the measurement contract is unmatched.
- **Remediation/Verification Code Actions Taken:** The exact narrow plan in `plan.md` is approved for RED → GREEN execution. Broad scheduler/bound/cache/residency/persistent/split-K/performance work remains blocked. Post-change validation must report L2 and cold-traffic effects numerically rather than treating favorable or unfavorable error movement as automatic scientific acceptance.

## Review Entry — Post-fix StepCode Claude Scientific and Code Review

- **Target Component/Phase:** Completed bounded implementation, public API invariants, GEMM/FA semantics, validator accounting, public/source documentation, and post-fix scientific evidence before the final native review.
- **Reviewer Agent Identity:** StepCode Claude `claude-opus-4-6[1m]`, effort `max`; artifact `.omx/artifacts/claude-you-are-the-post-fix-independent-scientific-code-reviewer-fo-2026-07-18T15-54-47-545Z.md`.
- **Inspected Artifacts:** Current working-tree diff; `README.md`; both DES design documents; comparison, hardware-adapter, operator, and validator code; every new/modified test; core task requirements/plan/harness/design/issues/progress/review artifacts; the `4,246/10,800` supported-row evidence and Small old/new resource-traffic audit.
- **Identified Issues/Anomalies:** Verdict **APPROVE with WATCH** and no bounded BLOCK. IMPORTANT F-1 found that the originally public `BoundComparison` constructor did not own its invariant; MEDIUM F-2 found a dead `compute_l2_hit_ratio` operator import. F-3 retained the Small measurement-boundary WATCH, and F-4 retained inert `tile_k` as deferred architecture. Claude's stronger wording that the evidence proves warm-L2 residency or proves the cold-HBM contract wrong was not accepted: the evidence proves only that the current candidate and some measured rows are unmatched; cache state, greedy scheduling, kernel policy, visibility boundary, and measurement provenance have not been isolated.
- **Remediation/Verification Code Actions Taken:** Added direct-construction RED tests, moved validation and derived-metric computation into frozen `BoundComparison.__post_init__`, made derived fields `init=False`, and removed the dead import. The focused comparison suite passed `17/17` and the combined comparison/integration suite passed `55/55`. The Small WATCH remains open without a clamp, scale, fallback, or unsupported causal attribution.

## Review Entry — Final Post-fix Native Code and Documentation Review

- **Target Component/Phase:** Stable post-fix source/docs/tests plus reviewer-owned regression, validator, hardware-smoke, and claim-matrix verification for Phase 7.
- **Reviewer Agent Identity:** Codex native `code-reviewer` lane `/root/des_code_reviewer`, independent read-only context; final verdict returned after the StepCode findings were remediated.
- **Inspected Artifacts:** All modified and new DES source/test/public-documentation files; task artifacts; scheduler and reused FA calculator contracts; `hardware/*.json`; H100 validation data; targeted and full pytest results; matched validator output; absolute-time diagnostic; all-hardware adapter smoke; static diff checks.
- **Identified Issues/Anomalies:** Bounded verdict **APPROVE WITH WATCH**, with `0` new CRITICAL and `0` new HIGH/Important source findings. Broad scientific verdict remains **BLOCK** for universal theoretical lower bound, global tighter-than-classical, `10000x` cycle-accurate speedup, and empirical cross-hardware zero-shot. Non-blocking WATCH items are experimental FA2 `cta_kv=64`, previously missing direct FA3 `>8192` branch coverage, and the need to include actual/DES/classical absolute scales in the formal report.
- **Remediation/Verification Code Actions Taken:** The reviewer modified no files. It independently observed `92/92` targeted tests and `130/130` full tests pass, validator exit `0` in `3.667s`, all `11` hardware files produce `22` calibration coefficients and `5/5` known operator configs, and `git diff --check` exit `0`. The authoring lane then added the requested FA3 high-branch regression (`19/19` FA tests) and will record all absolute scales in the formal test report. No additional production-code change is required.

## Review Entry — Resume-Audit and Integrity Reconciliation

- **Target Component/Phase:** Phase 8 task recovery, bounded-remediation closure, and task-artifact consistency.
- **Reviewer Agent Identity:** `/root/context_audit` independent read-only recovery lane, followed by the primary `/root` verification pass.
- **Inspected Artifacts:** All 13 task files; current Git status/history and worktree metadata; modified DES source, tests, validator, and public docs; `checksums.sha256`; fresh targeted/full pytest, `compileall`, H100 validator, hardware smoke, and `git diff --check` outputs.
- **Identified Issues/Anomalies:** Bounded implementation and task artifacts were internally consistent and freshly reproducible. The historical path was recorded in the prior session but is now explicitly excluded by user instruction. No code regression or checksum failure was found. The broad scheduler/bound/cache/launch architecture BLOCK remains unchanged.
- **Remediation/Verification Code Actions Taken:** No production code or external path was targeted. Added Phase 8 traceability and preserved the fresh evidence with exact counts and timings. The bounded task remains complete for its approved scope; the later user instruction closes R-027 as a scope exclusion.

## Review Entry — Final Post-Document Verification

- **Target Component/Phase:** Final Phase 8 documentation reconciliation, regression evidence, checksum integrity, and user-directed scope closure.
- **Reviewer Agent Identity:** Primary `/root` verification lane after the recovered session `97006` completed; this was a read-only evidence and artifact-integrity pass with no production-code edits.
- **Inspected Artifacts:** Final `notes.md`, `progress.md`, `test_report_2026-07-18_des_refined_roofline_review.md`, `summary.md`, `review.md`, `checksums.sha256`, all modified DES source/tests/docs, fresh targeted/full pytest output, `compileall`, H100 validator, all-hardware smoke, and `git diff --check`.
- **Identified Issues/Anomalies:** All bounded checks passed with the final timing values recorded below. The historical path is explicitly excluded by user instruction and is not a task issue. The four Small DES bound violations and the broad scientific/architecture BLOCK are expected, visible findings rather than hidden failures.
- **Remediation/Verification Code Actions Taken:** Updated the task report, summary, notes, and progress with the final run's exact metrics; regenerated the checksum manifest; reran checksum and artifact audits; made no production-code change. Final evidence: targeted `93/93` in `2.63s` pytest (`3.088s` shell), full `131/131` in `2.65s` pytest (`3.118s` shell), compile `0.046s`, validator `3.401s`, hardware smoke `11/11`, `git diff --check` exit `0`, and `28/28` checksums passed.

## Review Entry — Pre-commit StepCode Claude Review after Scope Reconciliation

- **Target Component/Phase:** Current working-tree remediation, task artifacts, user-directed ignored-path boundary, and minimal next-stage handoff before branch commit/push.
- **Reviewer Agent Identity:** StepCode Claude `claude-opus-4-6[1m]`, effort `max`; artifact `.omx/artifacts/claude-review-the-current-working-tree-changes-in-data-ycfeng-pipew-2026-07-19T15-56-03-653Z.md`.
- **Inspected Artifacts:** Tracked DES diff; `event_simulator/comparison.py`; changed tests and validator; `README.md` and DES design documents; current task artifacts; `design.md`; `harness.md`; and the user's explicit instruction to ignore `=10.1`.
- **Identified Issues/Anomalies:** Verdict **APPROVE with WATCH**. No Critical findings and no over-defensive or redundant-module violation. WATCH I-1 retains the pre-existing `lower_gemm`/`lower_gemm_v2` store-boundary divergence; WATCH I-2 notes that the FA2 binary-search contract has integration coverage but no isolated unit test. Neither blocks this bounded checkpoint. The historical `=10.1` path is outside scope by user instruction and is not a blocker.
- **Remediation/Verification Code Actions Taken:** No production code was changed by the reviewer. The primary lane recorded the verdict, reclassified R-027 as a closed scope exclusion, kept `SimulationResult.makespan` separate from accepted `des_bound`, and bounded the next stage to an additive independent-work `SafeBoundEvaluator` design with a checked-in order-dependence regression.
- **Staging-scope adjudication:** Claude recommended staging only the code/test diff and leaving `task_memory/` out. The primary lane rejected that narrower staging recommendation because the repository governance requires durable task artifacts and the user asked to restore and deliver the task context; the explicit staging list will include both completed task records and `task_memory/env_handbook.md`, while still excluding the ignored `=10.1` path and `.omx/` runtime artifacts.
