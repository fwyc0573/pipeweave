# DES Refined Roofline Review and Remediation Issues

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Reclassified R-027 as a user-directed ignored-path scope exclusion; it is not a blocker and receives no filesystem operation. |
| 2026-07-18 | Reconciled every issue with the bounded fixes, retained the scientific BLOCK items, and added post-fix API/source/FA2 WATCH records. |
| 2026-07-18 | Added architecture-review blockers R-021 through R-023 for scheduler optimality, traffic conservation, and matched launch metadata. |
| 2026-07-18 | Added matched-bound counterexamples, legacy GEMM work-count drift, hardware fail-fast gaps, and FA scheduler-contract drift. |
| 2026-07-18 | Added source-audit findings R-004 through R-016 and classified scientific claim risks. |
| 2026-07-18 | Created the issue register with the resolved metric conflict and open evidence gaps. |

## Issue Register

### R-001 — Requested time-domain optimization-gap formula has the wrong sign

- **Evidence:** The requested expression `(DES_bound - actual_time) / DES_bound` is non-positive whenever `DES_bound <= actual_time`.
- **Root Cause:** A rate-domain utilization-gap intuition was written directly in the time domain without inverting the ratio.
- **Impact:** Valid lower bounds would appear as negative optimization opportunity, and the metric would be unbounded below.
- **Resolution:** The user selected `optimization_gap = (actual_time - DES_bound) / actual_time` and `hardware_efficiency = DES_bound / actual_time`.
- **Status:** Resolved. `compare_des_bound()` and the public documents implement the selected contract; direct and factory construction are covered by `17` unit tests.

### R-002 — Four top-level design claims do not yet have one reproducible acceptance matrix

- **Evidence:** Existing docs describe the goals, but the current task has not yet verified matched refined/classical bounds, a cycle-accurate runtime baseline, held-out hardware behavior, or report-level metrics.
- **Root Cause:** Prior work focused on implementation stories and bounded GEMM validation rather than a single end-to-end goal audit.
- **Impact:** Marketing-style statements can be repeated without proving scientific or performance acceptance.
- **Proposed Resolution:** Audit code and available datasets, run matched measurements, label each claim PASS/FAIL/UNPROVEN, and repair only evidence-backed defects.
- **Status:** Resolved as an audit deliverable. The final matrix is category-scoped: interpretability is structurally established, the bounded metric API passes, and the global tightness, `10000x`, zero-shot, and universal-bound claims are not accepted.

### R-003 — Workspace contains pre-existing untracked task artifacts

- **Evidence:** The current worktree contains uncommitted DES changes and untracked task artifacts; the historical `=10.1` path is explicitly excluded by the user.
- **Root Cause:** The prior documentation task and this remediation were prepared across sessions and have not yet reached a branch checkpoint.
- **Impact:** Only the uncommitted branch state affects delivery readiness; the ignored path is not a workspace or staging blocker.
- **Proposed Resolution:** Complete the bounded review, stage an explicit file list, commit, and push. Do not inspect or manage the ignored path.
- **Status:** Resolved for the current delivery checkpoint.

### R-004 — Classical roofline compute peak is dimensionally incorrect

- **Evidence:** `tests/validation/validate_gemm_v2.py:32` treats `HardwareConfig.tc_bf16` as chip-wide TFLOPS. `event_simulator/hardware_adapter.py:57-68` and `hardware/H100.json:4,12,16` define it as `4096 ops/cycle/SM`, with `132 SMs` at `1830 MHz`.
- **Root Cause:** The validator bypasses the hardware adapter's explicit throughput properties and mixes per-SM ops/cycle with chip-wide TFLOPS.
- **Numeric Impact:** H100 chip-wide BF16 peak is `4096 * 1830 * 132 / 1e6 = 989.42976 TFLOPS`; the validator effectively uses `4096 TFLOPS`, a `4.1397582381x` overestimate. Its roofline compute time is therefore about `4.14x` too optimistic.
- **Proposed Resolution:** Compute the bound from `hw_config.tc_bf16_flops_per_us` and add unit tests for both compute-bound and memory-bound cases.
- **Status:** Resolved locally. The validator uses `tc_bf16_flops_per_us`; the original `4.1397582381x` peak-rate error remains recorded as historical evidence.

### R-005 — GEMM validation silently discards simulator failures

- **Evidence:** `tests/validation/validate_gemm_v2.py:49-61` catches every `Exception` and returns `None`; lines `105-108` count that result as a skipped row.
- **Root Cause:** The validation harness conflates invalid source rows with simulator defects.
- **Impact:** Acceptance sample size can shrink silently and a broken simulator can still print apparently favorable metrics.
- **Proposed Resolution:** Validate row fields explicitly and let unexpected lowering/scheduling errors propagate with row context.
- **Status:** Resolved. Only named `UnsupportedGemmRow` rejections are counted; unexpected lowering or scheduling failures propagate.

### R-006 — Dataset `tile_K` is not passed into GEMM v2

- **Evidence:** `dataset/gemm_test.csv` contains `tile_K`, but `tests/validation/validate_gemm_v2.py:38-57` reads only `tile_M` and `tile_N`.
- **Root Cause:** Validator plumbing predates the `tile_k` argument.
- **Impact:** The validation does not evaluate the recorded kernel configuration and cannot test K-tiling structural behavior.
- **Proposed Resolution:** Require a positive `tile_K`, pass it to `lower_gemm_v2`, and test propagation.
- **Status:** Resolved for validator plumbing. Positive dataset `tile_K` is passed through and tested; its lack of timing behavior remains R-007.

### R-007 — GEMM v2 accepts `tile_k` but it has no behavioral effect

- **Evidence:** `lower_gemm_v2` validates and documents `tile_k`, but its B-tile working set is based on full `k`; a reproduced `4096^3`, `tile_M=tile_N=128` case produced identical `3,075` events and `143.257862154871 us` makespan for `tile_k=0` and `tile_k=64` (`delta=0`).
- **Root Cause:** The earlier working-set implementation was replaced by full-K effective-traffic aggregation without removing or redefining the public parameter.
- **Impact:** The structural model and validator imply a K-tiling sensitivity that does not exist.
- **Proposed Resolution:** Either design a physically justified K-tile reuse/residency model or remove the unsupported parameter in a separately approved API change; do not add an empirical penalty.
- **Status:** Open; likely material design decision.

### R-008 — Wave split is primarily an event label, not a timed residency mechanism

- **Evidence:** `compute_wave_split` classifies full/tail waves, while GEMM v2 emits zero-duration `CTAAdmission_FullWave`/`CTAAdmission_TailWave` events and does not hold an SM residency token for CTA lifetime.
- **Root Cause:** Wave taxonomy was added without an occupancy/residency lifetime model.
- **Impact:** The documentation says waves add structural time, but classification alone does not change makespan.
- **Proposed Resolution:** Correct the public claim immediately. A genuine residency/occupancy model requires separate architecture design and lower-bound proof before implementation.
- **Status:** Open; broad structural-model work may require explicit approval.

### R-009 — Partial-tile events model only useful work and do not encode a structural penalty

- **Evidence:** GEMM v2 clamps edge dimensions and computes MMA instructions from `2 * actual_m * actual_n * k`; `compute_tile_efficiency` exists in `event_simulator/structural.py` but is not consumed by the lowering.
- **Root Cause:** Partial-tile naming was added without deciding whether hardware executes padded work or how under-utilization can be bounded optimistically.
- **Impact:** A partial tile can make the predicted time smaller, contradicting the current rule that partial-tile structure adds time.
- **Proposed Resolution:** Replace the unsupported claim with exact implemented semantics. Any padded-work/efficiency model requires evidence and a lower-bound-safe design.
- **Status:** Open; documentation fix is local, model change is material.

### R-010 — L2 calibration and lane count multiply chip-wide capacity

- **Evidence:** `event_simulator/hardware_adapter.py:121-132` documents one lane for chip-wide L2 but configures `l2_bandwidth=hw.num_sms`; `docs/des_design_rules.md:69,74-76` simultaneously says L2 has `num_sms` lanes at a chip-wide rate and chip-wide rates require one lane.
- **Root Cause:** Per-slice parallelism and aggregate chip-wide throughput were mixed in one scheduler resource.
- **Impact:** Up to `num_sms` events can each consume a full chip-wide rate, multiplying represented aggregate capacity.
- **Proposed Resolution:** Make rate/lane units consistent. Before changing behavior, establish which GEMM events should use L2 and prove lower-bound effects with targeted tests.
- **Status:** Resolved locally. L2 is one chip-wide lane, so the represented aggregate H100 capacity is `8,820,000 B/us`, not `132x` that value.

### R-011 — `GlobalStore` uses DRAM calibration while scheduled on L2 lanes

- **Evidence:** `derive_calibration` assigns the GEMM `GlobalStore` coefficient from chip-wide DRAM time-per-byte, while GEMM v2 schedules stores on `l2_bandwidth`; `derive_resource_config` exposes `num_sms` L2 lanes.
- **Root Cause:** Event meaning, resource identity, and coefficient unit drifted during the memory-model revisions.
- **Impact:** The scheduler can grant many concurrent stores, each at a chip-wide DRAM-derived rate. Existing documentation that describes this coefficient as an L2 rate is inaccurate.
- **Proposed Resolution:** Define whether the store represents L2 injection or HBM writeback, then align event bytes, resource, rate, and lane count. Do not calibrate with a scaling factor.
- **Status:** Resolved for the declared output-to-L2 boundary. `GlobalStore` uses the L2 coefficient and the chip-wide L2 resource; HBM writeback is not claimed.

### R-012 — Literal L2 hit/miss event split is no longer implemented

- **Evidence:** GEMM v2 emits one aggregate `GlobalLoad_L2Miss` event with discounted effective DRAM bytes; `compute_l2_hit_ratio` is imported but unused.
- **Root Cause:** The implementation moved from literal cache events to an analytical effective-traffic model, but design claims were not updated.
- **Impact:** The model may still represent reuse analytically, but claims of event-level L2 hit/miss decomposition are false.
- **Proposed Resolution:** Document the current effective-traffic abstraction precisely; reserve literal split claims for a future tested implementation.
- **Status:** Resolved for truthfulness. Public docs state that no literal cache hierarchy or hit/miss split is implemented, and the dead `compute_l2_hit_ratio` operator import was removed.

### R-013 — Scheduler ready-event selection scales approximately quadratically

- **Evidence:** `event_simulator/scheduler.py` scans the full ordered event list for each scheduled event. Prior controlled measurements for `387`, `771`, `1,539`, `3,075`, and `6,147` events were `0.014453`, `0.032426`, `0.087180`, `0.278809`, and `1.026491 s`; the largest doubling exponent was `1.882`.
- **Root Cause:** Dependency readiness is recomputed by repeated global scanning rather than maintained with indegrees and a deterministic ready queue.
- **Impact:** Large validation/design-space sweeps are CPU-expensive, weakening the exploration-speed goal independently of model accuracy.
- **Proposed Resolution:** Add deterministic scheduler scalability tests and plan a behavior-preserving topological ready-queue refactor. Because this is a core algorithm rewrite, apply the clean-workspace/explicit-approval gate before implementation.
- **Status:** Open; broad refactor classification.

### R-014 — Simulation report does not implement the optimization metric contract

- **Evidence:** `event_simulator/report.py:18-26` exposes makespan, critical path, kernel durations, resource busy time, and timeline only.
- **Root Cause:** Reporting was designed for simulated-event attribution before measured-actual comparison semantics were resolved.
- **Impact:** Users cannot obtain a validated `optimization_gap`, `hardware_efficiency`, bound-violation status, or classical-bound comparison through a stable API.
- **Proposed Resolution:** Add a focused comparison-result/helper API that validates positive finite times and rejects `DES_bound > actual_time`; do not force measured data into the pure simulation report.
- **Status:** Resolved through the separate public `compare_des_bound()` API. The pure simulation report remains provenance-neutral and does not accept measured actual latency implicitly.

### R-015 — Public documentation overstates current DES support and evidence

- **Evidence:** `docs/des_design_rules.md:9-12` presents all four research goals as achieved; `README.md:173-175` says attention/cache hierarchy are unsupported despite experimental GEMM-v2 reuse and FlashAttention lowering.
- **Root Cause:** Research targets, implemented mechanisms, and empirically accepted claims are not labeled separately.
- **Impact:** Readers can mistake a phase target or experimental event taxonomy for a validated result.
- **Proposed Resolution:** Add explicit Implemented/Validated/Unproven status tables and update README wording without claiming full attention or cache-hierarchy fidelity.
- **Status:** Resolved for public truthfulness. README and both design documents use Established/Experimental/Unproven/Blocked status and have contract tests.

### R-016 — Existing data cannot prove cycle-accurate speedup or cross-hardware DES zero-shot

- **Evidence:** Repository search found no named cycle-accurate simulator/runtime benchmark. `dataset/fa3_benchmark_h800.csv` has `2` H800-only rows. `dataset/gemm_test.csv` spans `11` hardware names, but the current validator hard-codes H100 and no held-out multi-hardware DES protocol exists. Existing `e2e/*.csv` evaluate legacy predictors, not the DES path.
- **Root Cause:** DES implementation and bounded H100 validation were developed before claim-level benchmark protocols.
- **Impact:** `10000x` and empirical cross-hardware zero-shot claims are currently UNPROVEN, even though the DES code path is mechanistic and does not load ML checkpoints.
- **Proposed Resolution:** Mark both claims UNPROVEN. Future acceptance requires a matched cycle-accurate runtime benchmark and a held-out multi-hardware DES accuracy study without target-hardware fitting.
- **Status:** Open evidence gap, not repairable by a local code patch.

### R-017 — Matched H100 rows include real DES lower-bound violations

- **Evidence:** The post-fix deterministic Small sample evaluated `62` supported rows and found `4` DES violations. Their actual/predicted pairs were `10.472800/11.358228 us`, `10.619200/11.324017 us`, `8.213200/10.016648 us`, and `10.056400/10.243910 us`, with relative excesses `8.454552%`, `6.637193%`, `21.957916%`, and `1.864583%`.
- **Root Cause:** The candidate and measurement do not have a proven matched initial-residency/scheduling/kernel-policy boundary. Warm L2 is one plausible hypothesis, but the available aggregate data does not isolate cache state from greedy scheduling, kernel policy, measurement boundary, or measurement provenance.
- **Impact:** The universal `DES_bound <= actual_time` claim is false for the current validation contract, and bounded comparison metrics must reject these rows rather than produce negative gaps.
- **Proposed Resolution:** Define cold, warm, or explicit initial-residency semantics before accepting lower-bound evidence. Until then, validators must count and report every violation and the public docs must label universal lower-bound validity as unaccepted.
- **Status:** Open measurement-contract blocker for scientific acceptance; no empirical scaling fix is allowed.

### R-018 — Legacy `lower_gemm` undercounts MMA work by a factor of two

- **Evidence:** `event_simulator/operators.py:101` uses `ceil(actual_m * actual_n * k / 256)`, while the documented calibration convention and `lower_gemm_v2` use `ceil(2 * M * N * K / 256)`.
- **Root Cause:** The original lowering retained a multiply-count convention after calibration was standardized on FLOPs per MMA instruction.
- **Impact:** The public Phase-0 GEMM lowering reports half the required tensor-core work under the current calibration contract.
- **Proposed Resolution:** Add a one-tile RED test for the exact instruction count, then apply the factor-of-two correction.
- **Status:** Resolved by strict RED/GREEN. The reproduced count changed from `256` to the required `512`; all legacy operator tests pass.

### R-019 — Invalid hardware throughput can silently become zero-duration work

- **Evidence:** `derive_calibration` maps non-positive tensor/FMA/XU rates to `0.0` duration coefficients instead of rejecting them; optional hardware fields default to zero.
- **Root Cause:** Missing or invalid performance fields are treated as zero-cost ideal work rather than an invalid operator/hardware contract.
- **Impact:** A malformed hardware specification can produce a spuriously fast bound without any error.
- **Proposed Resolution:** Validate every rate required by the emitted primitives as positive and finite before division. Do not add a default or alternate-rate fallback.
- **Status:** Resolved locally. Required rates must be finite and positive, unknown operator types fail fast, and all `11` hardware JSONs pass the known-operator smoke matrix.

### R-020 — DES FA3 schedule-threshold formula drifts from the reused scheduler contract

- **Evidence:** `event_simulator/operators.py` computes `max_num_works_per_head = sum(ceil(q/cta_q)) * batch_size`; `analytical_model/fa3_calculator.py` computes `ceil(sum(q_lengths)/cta_q) + batch_size - 1` before deciding `same_schedule_for_all_heads`.
- **Root Cause:** The threshold logic was copied and re-derived instead of delegated to one source of truth.
- **Impact:** Some batches can select a different scheduling regime and head multiplier than the underlying FA3 calculator, changing event count and work.
- **Proposed Resolution:** Add threshold-boundary integration tests and share the exact scheduler decision logic rather than maintaining two formulas.
- **Status:** Resolved locally. The canonical formula is used and regression tests cover both `<=8192` and `>8192` schedule-selection branches.

### R-021 — Greedy list scheduling is not a proven latency lower-bound evaluator

- **Evidence:** `event_simulator/scheduler.py:68-112` commits each ready event to the earliest available lane in input order. An independent architecture review found a same-DAG/same-resource counterexample whose makespan changes from `21.0` to `11.0` when only independent-event input order changes.
- **Root Cause:** A deterministic feasible list schedule was equated with the minimum feasible schedule. For a minimization problem, a feasible schedule is generally an upper bound on the modeled optimum, not a lower bound.
- **Impact:** Even with optimistic primitive rates, the scheduler can serialize work more than necessary and produce `DES_time > modeled_optimum`; actual hardware may use a better schedule. Therefore `SimulationResult.makespan` is not unconditionally a theoretical latency lower bound.
- **Proposed Resolution:** Narrow work may add a regression counterexample and correct documentation. A scientifically safe architecture must separate an explanatory feasible schedule from a proven bound evaluator (for example, analytical resource/dependency lower bounds or an exact/relaxed optimization contract). This is a broad architecture decision requiring explicit approval and a clean workspace.
- **Status:** Open CRITICAL architecture blocker for public lower-bound acceptance.

### R-022 — Effective B traffic violates cold first-touch conservation and monotonicity

- **Evidence:** `event_simulator/operators.py:452-462` starts from unique `B_bytes` and divides it again by `b_reuse_factor`. For `M=N=K=4096`, `tile_M=tile_N=128`, unique B is `33,554,432 B`, reuse is `32`, and modeled B DRAM is only `1,048,576 B` (`3.125%` of unique B). An independent fixed-policy counterexample (`M=128 -> 129`, `N=4096`, `K=64`, tile `128x16`) reduces modeled DRAM bytes `540,672 -> 278,656` and makespan `0.161283 -> 0.083123 us` while work increases.
- **Root Cause:** Cross-CTA reuse reduction was applied to already-unique matrix bytes rather than to repeated CTA demand; the model lacks an explicit warm-cache/initial-residency contract.
- **Impact:** The event named `GlobalLoad_L2Miss` can represent less than cold first-touch traffic and can make predicted time decrease when workload size increases. This is not an honest literal cache-miss model and can manufacture apparent tightness.
- **Resolution:** The approved local repair now enforces cold unique A+B traffic exactly once and fixed-policy monotonicity; no cache hierarchy or warm-state fallback was added. On `100` supported Small rows this raised mean candidate time from `8.654575482592` to `9.962412046531 us`, improved MAPE from `46.2212474501%` to `34.6070571352%`, and increased violations from `6` to `8`.
- **Status:** Local conservation defect resolved. Explicit cache-state and matched-measurement semantics remain open through R-017 and require broad design/proof.

### R-023 — Validation does not reproduce measured CTA count or split-K policy

- **Evidence:** GEMM v2 derives `total_ctas = ceil(M/tile_M) * ceil(N/tile_N)` at `event_simulator/operators.py:419-421`. H100 dataset `cta_count` differs on `6,554/10,800` rows (`60.685185%`); mismatch rates are Large `3,788/4,231` (`89.529662%`), Medium `414/1,798` (`23.025584%`), and Small `1,454/3,562` (`40.819764%`). All `437/437` split-K rows mismatch, and `is_split_k` is unused.
- **Root Cause:** The lowering reconstructs a simple tile grid instead of consuming the measured kernel launch/persistent grouping and split-K configuration.
- **Impact:** CTA admission, wave count, resource concurrency, and event count are not matched to the measured kernel on most Large rows; split-K replicated work and reduction are absent. A favorable latency comparison cannot be attributed to correctly modeled measured structure.
- **Proposed Resolution:** Extend the explicit operator configuration contract to represent CTA work assignment and split-K semantics, then validate exact launch metadata. This is material modeling work; the local validator should at minimum detect and report/reject mismatched rows rather than claim structural validation.
- **Status:** Mitigated in validation: all mismatches and split-K rows are rejected and counted by reason. Persistent CTA and split-K execution semantics remain an open broad scientific-validity blocker.

### R-024 — Public `BoundComparison` construction originally bypassed invariant ownership

- **Evidence:** The first public frozen dataclass accepted caller-supplied derived fields, so direct construction could bypass the factory's validation and forge `optimization_gap` or `hardware_efficiency`.
- **Root Cause:** Validation lived only in `compare_des_bound()` while the concrete value object was also publicly exported.
- **Impact:** The advertised validated entry point was safe, but the public type did not own its invariants.
- **Resolution:** Derived fields are `init=False`; `__post_init__` validates both times, rejects violations, normalizes numeric values, and computes both metrics. Direct-construction RED tests now pass.
- **Status:** Resolved; StepCode Claude F-1 was closed before delivery.

### R-025 — Internal source documentation retained obsolete universal-bound wording

- **Evidence:** Source comments/docstrings still contained `never causes DES_time > actual_time`, `XU safely omitted for roofline bound`, and `Setting to zero ensures the bound` after public docs had been corrected.
- **Root Cause:** The initial truthfulness pass covered public Markdown but not embedded source documentation.
- **Impact:** Maintainers could still infer that optimistic primitives certify the greedy composition.
- **Resolution:** Reworded the source documentation and added a repository-source contract test for all three phrases.
- **Status:** Resolved.

### R-026 — FA2 uses a fixed experimental `cta_kv=64`

- **Evidence:** `lower_flash_attention()` fixes FA2 `cta_kv` at `64`, whereas the canonical calculator can derive other values from head dimension, CTA-Q, warp configuration, and shared-memory capacity.
- **Root Cause:** The current FA2 integration reuses task scheduling but does not import the full kernel-traits selection contract.
- **Impact:** The path executes and its repaired binary-search contract is tested, but it cannot claim canonical kernel-trait or hardware-scheduler equivalence.
- **Proposed Resolution:** Resolve only within the separately approved attention architecture work; do not add a heuristic fallback or empirical constant adjustment in this task.
- **Status:** Open non-blocking WATCH under the explicitly Experimental FA2 surface.

### R-027 — Historical `=10.1` path is explicitly ignored by user instruction

- **Evidence:** The user explicitly directed this task to ignore the historical path named `=10.1`.
- **Root Cause:** The path is outside the requested code, documentation, validation, staging, and next-stage scope; its filesystem state is not needed to complete the branch checkpoint.
- **Impact:** None for the approved remediation or delivery. Treating it as a blocker would expand scope and violate the user's instruction.
- **Proposed Resolution:** Do not inspect, create, delete, move, or modify the path. Exclude it from active validation and staging, and continue with the reviewed DES artifacts.
- **Status:** Closed as a user-directed scope exclusion; not a code, test, or delivery blocker.
