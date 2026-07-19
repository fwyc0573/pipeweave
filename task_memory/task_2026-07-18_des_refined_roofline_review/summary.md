# DES Refined Roofline Review and Bounded Remediation Summary

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Added the fresh pre-commit verification matrix with exact numeric metrics and updated the branch-delivery evidence. |
| 2026-07-19 | Added the pre-commit Claude review disposition and current task-artifact counts for branch delivery. |
| 2026-07-19 | Updated the authoritative validation matrix to the final post-document run (`97006`) and recorded the final artifact-integrity evidence. |
| 2026-07-19 | Added the recovered-session verification matrix, updated fresh numeric timings, and recorded the user-directed ignored-path disposition for R-027. |
| 2026-07-18 | Replaced the draft with the final deliverable inventory, review disposition, validation matrices, scientific verdicts, and deferred architecture boundary. |
| 2026-07-18 | Created the English completion-summary draft. |

## Task Overview

This task reviewed the DES event simulator implementation and documentation against the requested Refined Roofline goals, reconstructed the required durable `task_memory` record, consulted independent StepCode Claude and Codex-native review lanes, applied only the approved bounded fixes through RED -> GREEN TDD, and reran the full scientific and regression evidence stack.

The binding metric decision is:

```text
0 < des_bound <= actual_time
optimization_gap = (actual_time - des_bound) / actual_time
hardware_efficiency = des_bound / actual_time
optimization_gap + hardware_efficiency = 1
```

The user rejected `(DES_bound - actual_time) / DES_bound`. The implemented `compare_des_bound()` API enforces the selected numeric contract, including direct public value-object construction, but deliberately does not certify provenance or accept `SimulationResult` implicitly.

The central architecture result is that the current scheduler is a deterministic, auditable **heuristic feasible list scheduler**, not a certified theoretical lower-bound evaluator. The same initial Event DAG, durations, and resource capacities produce makespans `21.0` and `11.0` when only non-semantic input order changes. For the modeled minimization problem, a feasible schedule witnesses an upper bound on the modeled optimum; relative to actual hardware latency, the current result is neither a proven lower nor upper bound.

### Bounded remediation completed

1. Added the invariant-owning bounded comparison API and package export.
2. Corrected legacy GEMM work from `M*N*K` to `2*M*N*K` FLOPs.
3. Restored one chip-wide L2 lane and used the L2 coefficient for GEMM output stores.
4. Rejected non-positive/non-finite required rates and unknown operator types instead of creating zero-duration work.
5. Restored cold-input conservation to unique A+B once; output C terminates at L2.
6. Fixed FA2 binary-search call/tuple handling and aligned the FA3 scheduling threshold with the reused canonical formula.
7. Corrected the classical roofline from an effective `4096 TFLOPS` interpretation to H100's `989.429760 TFLOPS` chip-wide BF16 peak and matched the cold-A+B/HBM plus C/L2 boundary.
8. Made validator rejection accounting explicit for split-K, CTA-grid mismatch, invalid rows, and unexpected exceptions; added an exhaustive `Other` category.
9. Replaced overstated public and source claims with Established/Experimental/Unproven/Blocked status.

No empirical scale, clamp, fallback, silent skip, implicit warm-cache state, cache hierarchy, scheduler rewrite, CTA residency, persistent CTA approximation, or split-K approximation was added.

### Independent review disposition

- Codex-native independent architect: **BLOCK** for universal-bound and broad architecture acceptance.
- Adversarial StepCode Claude: **BLOCK** for broad scientific acceptance, while allowing narrow remediation.
- StepCode Claude implementation-scope review: **APPROVE with WATCH** for the exact bounded plan.
- Post-fix StepCode Claude: **APPROVE with WATCH**; its public-constructor and dead-import findings were closed.
- Final Codex-native code/docs reviewer: **APPROVE WITH WATCH** for bounded remediation, with `0` new Critical and `0` new Important source findings; broad scientific claims remain **BLOCK / UNPROVEN**.

Claude's stronger causal wording that the Small violations prove warm-L2 residency was not adopted. Available evidence proves an unmatched candidate/measurement contract, but does not isolate cache state from greedy scheduling, kernel policy, completion boundary, or measurement provenance.

## Deliverables Inventory

Paths are repository-relative. The summary cannot embed its own final digest without changing that digest; the authoritative summary hash is therefore stored in `task_memory/task_2026-07-18_des_refined_roofline_review/checksums.sha256`. The manifest intentionally excludes its own digest.

### Public documentation and source

| Deliverable | Exact Path | SHA-256 |
|---|---|---|
| Public DES status and API | `README.md` | `b96e12305de6c7180bdd226f0cf97887e0317fabc32b4d0554e270220416b1a0` |
| DES rules and invariants | `docs/des_design_rules.md` | `13e76aef109324a7e2573aad5e906d7ac2548f49f96c480f6c5b52924ce7680b` |
| Reconciled simulator design | `docs/event_simulator_design.md` | `920f55a7084f8c2c1cddac7973d96d9ce37c91a5fde375cf41cc18e00af5499b` |
| Public package surface | `event_simulator/__init__.py` | `5a2ab94c02ea303778d05416edd78745353268d8704b34cdf9478d24eaf6b638` |
| Bounded comparison API | `event_simulator/comparison.py` | `784ab8043173c672fe17a2a7f56d5047c823f6050d8eb740f6922b7330dd4447` |
| Hardware adapter | `event_simulator/hardware_adapter.py` | `9431de970f76b534ab89f555c2c54918d51e0d2c5b9ba5d6474f8ae5e83c923c` |
| Operator lowering fixes | `event_simulator/operators.py` | `031d6f41e2f947b7ad742417b60c4313cfd7cdee898ecae309cbec432ec54bbf` |
| Structural documentation correction | `event_simulator/structural.py` | `817d66cf6f1540f706923e7876ffa58df37fc750127bbc87b000f8bd4be32567` |

### Tests and validator

| Deliverable | Exact Path | SHA-256 |
|---|---|---|
| FA integration tests | `tests/integration/test_fa_simulation.py` | `9c88a7468db27ed29fd664b61ec632aa1d35bfb8cf76f2eab126172bb9cd9ab0` |
| GEMM-v2 integration tests | `tests/integration/test_gemm_v2_simulation.py` | `9bf84c876e246a1729e850a83d71da7d0908b0066be7978cd805135590b81f96` |
| Legacy operator integration tests | `tests/integration/test_operator_simulation.py` | `e1a9901c62189202b141022a11172ed19271905e0acf5e37f3eb81380d2b1c88` |
| Bounded comparison unit tests | `tests/unit/test_bound_comparison.py` | `911166aa12ad53587fbb327b957c6b779a41618453f6dc26479e90f7b85f55d9` |
| Documentation/source contract tests | `tests/unit/test_des_documentation.py` | `cef292edf8661b0d0938768571a49a564658461d98c11077bd4441a0322afc74` |
| Validator unit tests | `tests/unit/test_gemm_validation.py` | `3eb43bd0e612d6d7a412025b0c65151f6ebc2e39ec9f2e459ce0853812c275e2` |
| Hardware-adapter unit tests | `tests/unit/test_hardware_adapter.py` | `36dac74b1b4cc0724348a2d3ecf38034bca9ad8069ba16c46f6f05564c85d598` |
| Matched GEMM validator | `tests/validation/validate_gemm_v2.py` | `e289df3107bfaf908ec23d842030c515de94d27e34b5a981504bad58d4febd89` |

### Task governance artifacts

| Deliverable | Exact Path | SHA-256 |
|---|---|---|
| Plan | `task_memory/task_2026-07-18_des_refined_roofline_review/plan.md` | `a0fe6177e58ec9c367c851238c4e791c27541906b1fb08dd9e5ed4f36a6fca71` |
| Requirements | `task_memory/task_2026-07-18_des_refined_roofline_review/requirements.md` | `9c82b12c3d6ad2bcdc5dfd0415039678089ab5704f5fde27e097c51ef28c5952` |
| Operational notes | `task_memory/task_2026-07-18_des_refined_roofline_review/notes.md` | `235fb113b6361d0c074552c7504964b60d64ff029cbf57da7f64bcc9925166d8` |
| Progress log | `task_memory/task_2026-07-18_des_refined_roofline_review/progress.md` | `e249151e192489e8e5b0b25b68787bc82ea17254262916837a32f3681cbab0cd` |
| Issues and root causes | `task_memory/task_2026-07-18_des_refined_roofline_review/issues.md` | `6393ba28c04281b4ccde435ccad48102a2cae466081e6732827bb7cd7577e75b` |
| Review log | `task_memory/task_2026-07-18_des_refined_roofline_review/review.md` | `57f2c860b03a1a98992f726e8fa45ab5adeab63cc4b027397ba22251b4ce6774` |
| Vetted lessons | `task_memory/task_2026-07-18_des_refined_roofline_review/lessons.md` | `42f41e28ef0fc76cf18cdd2c86b002468397cf450deba0c6de20368e06b75f3f` |
| Task harness | `task_memory/task_2026-07-18_des_refined_roofline_review/harness.md` | `685775d7d0c04a97a4bb2fd67505a76e3bfa2da05e1dbd0aeebf2c69a0a0e287` |
| Task design | `task_memory/task_2026-07-18_des_refined_roofline_review/design.md` | `4dbe08be9bdfe827cf65b8af3e2c3e351b8f8597a6091a34d281f5d8dbfc26eb` |
| Future work | `task_memory/task_2026-07-18_des_refined_roofline_review/future.md` | `3f76def8a2d7018331405274682887f31353d4cf7fd8f699d600dbd9f0d144ff` |
| Formal test report | `task_memory/task_2026-07-18_des_refined_roofline_review/test_report_2026-07-18_des_refined_roofline_review.md` | `385f8445bf3edb2888bd1e15e909c69d34d4c834f1ddb4f6c4273323d9674525` |
| Final summary | `task_memory/task_2026-07-18_des_refined_roofline_review/summary.md` | See authoritative entry in `checksums.sha256` |
| Checksum manifest | `task_memory/task_2026-07-18_des_refined_roofline_review/checksums.sha256` | Manifest intentionally excludes its own digest |

## Validation Status

### Environment and regression

| Validation | Expected | Actual | Status |
|---|---:|---:|---|
| Python environment | Recorded and reproducible | `/usr/bin/python` `3.12.3`; no conda env; pytest `9.1.1`; pandas `3.0.3`; numpy `2.4.6` | PASS |
| Targeted changed-path tests | All pass | `93/93` in `2.66s`; elapsed `3.108s`; user `5.032s`; sys `0.096s` | PASS |
| Full test suite | All pass | `131/131` in `2.77s`; elapsed `3.218s`; user `4.807s`; sys `0.170s` | PASS |
| Python compilation | Exit `0` | Exit `0`; `0.046s`; user `0.037s`; sys `0.008s`; no output | PASS |
| H100 validator | Exit `0`, no hidden failure | Exit `0`; `3.461s`; user `5.328s`; sys `0.107s` | PASS as an audit |
| Hardware adapter smoke | `11` hardware files, `22` coefficients, `5` known configs | `11/11`, `22/22`, `5/5` | PASS |

The earlier resume-audit run independently reproduced the bounded snapshot with targeted `93/93` tests in pytest `8.52s` (shell elapsed `9.741s`), full `131/131` tests in pytest `2.76s` (shell elapsed `3.225s`), compilation `0.265s`, and validator `3.618s`. The authoritative final post-document run (`97006`) then passed targeted `93/93` in pytest `2.63s` (shell elapsed `3.088s`), full `131/131` in pytest `2.65s` (shell elapsed `3.118s`), compilation in `0.046s`, validator in `3.401s`, cross-hardware smoke `11/11`, `git diff --check`, and all `28/28` checksum entries. The historical `=10.1` path was excluded from active validation and staging by explicit user instruction. The latest pre-commit run independently reproduced the suites with targeted `93/93` in pytest `2.66s` (shell elapsed `3.108s`), full `131/131` in pytest `2.77s` (shell elapsed `3.218s`), compilation `0.046s`, validator `3.461s`, hardware smoke `11/11`, checksum `28/28`, and `git diff --check` exit `0`.

### Matched H100 evidence

Supported-policy coverage is `4,246/10,800 = 39.314814815%`. CTA-grid mismatches are `6,554/10,800`; all `437/437` split-K rows are explicitly unsupported rather than simulated with missing semantics.

| Category | Sampled | Evaluated | Unsupported | DES Violations | Both Valid | DES Tighter | Classical Tighter | Equal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Large | 200 | 24 | 176 | 0 | 24 | 24 | 0 | 0 |
| Medium | 100 | 83 | 17 | 0 | 83 | 80 | 0 | 3 |
| Small | 100 | 62 | 38 | 4 | 58 | 1 | 29 | 28 |
| Other | 100 | 26 | 74 | 0 | 26 | 26 | 0 | 0 |

| Category | Mean Actual (us) | Mean DES (us) | Mean Classical (us) | DES MAE (us) | Classical MAE (us) |
|---|---:|---:|---:|---:|---:|
| Large | `39.014666666667` | `31.429699237947` | `29.104068002429` | `7.584967428720` | `9.910598664238` |
| Medium | `22.669559036145` | `15.055291025114` | `13.544613414728` | `7.614268011031` | `9.124945621416` |
| Small | `13.203912903226` | `9.500076111021` | `9.495655199596` | `3.819359456605` | `3.823780368030` |
| Other | `16.843523076923` | `11.099008313674` | `9.963211560753` | `5.744514763249` | `6.880311516171` |

Both-valid mean gaps are:

| Category | DES | Classical | Delta Favoring DES |
|---|---:|---:|---:|
| Large | `25.136598598951%` | `31.453028079252%` | `6.316429480301` percentage points |
| Medium | `44.382446381328%` | `50.961102480044%` | `6.578656098716` points |
| Small | `40.926363100408%` | `41.005060883398%` | `0.078697782990` points in aggregate, but only `1/58` rows are strictly tighter |
| Other | `42.470372669348%` | `49.920482043962%` | `7.450109374614` points |

The four Small violations have actual/DES pairs:

```text
10.472800000000 / 11.358228331424 us  (+8.454552091362%)
10.619200000000 / 11.324016800305 us  (+6.637193011766%)
 8.213200000000 / 10.016647575410 us (+21.957916225228%)
10.056400000000 / 10.243909889271 us  (+1.864582646580%)
```

The full per-row metadata, all-row MAPE, medians, runtime matrix, RED/GREEN history, exact commands, failure resolutions, and Small old/new resource-traffic audit are in the formal test report.

### Goal verdict matrix

| Design Goal | Final Status | Evidence Boundary |
|---|---|---|
| Tighter than traditional roofline | **PARTIAL locally / UNPROVEN globally** | Strong sampled Large/Medium/Other results; Small has only `1/58` strictly tighter, `29` classical tighter, `28` equal, and `4` violations. |
| `10000x` faster than cycle-accurate | **UNPROVEN** | No named matched cycle-accurate comparator exists; a historical `58,467`-event row took `115.882818766s`. |
| More interpretable than an ML predictor | **ESTABLISHED structurally / Experimental scientifically** | Explicit event work/resources/dependencies/timeline/selected critical path and no ML latency closure; no counter-attribution agreement study. |
| Cross-hardware zero-shot | **UNPROVEN** | All `11` hardware specs construct, but there is no held-out multi-hardware accuracy protocol without target-hardware fitting. |
| Optimization gap | **PASS for externally accepted bounds** | Exact API contract and `17` comparison tests; scheduler makespan is not certified or consumed implicitly. |
| Universal theoretical lower bound | **BLOCKED** | Order-dependent `21.0` vs `11.0` schedule, missing launch/residency semantics, and real violations. |

### Task-artifact governance

| Metric | Expected | Actual | Status |
|---|---:|---:|---|
| Required base artifacts | `11` | `11` | PASS |
| Final task files including report/manifest | `13` | `13` | PASS |
| Markdown files with Modification History | `12` | `12` | PASS |
| Requirements tagged `[Original Request]` | `11` | `11` | PASS |
| Progress entries with all four audit fields | `30` | `30` | PASS |
| Review entries with all five required fields | `11` | `11` | PASS |
| Contiguous issue IDs | R-001 through R-027 | `27` contiguous IDs | PASS |
| Draft markers/stale status | `0` | `0` | PASS |
| Checksum entries verified | `28` | `28` | PASS |

The historical `=10.1` path is explicitly ignored by the user and is outside the active code, validation, staging, and delivery scope. It was not inspected or targeted by any filesystem operation. Issue `R-027` is closed as a user-directed scope exclusion, not a code or test blocker.

## Open Items/Future Extensions

There is no pending code work inside the approved bounded remediation. Issue `R-027` is closed as a user-directed scope exclusion. The following items remain intentionally outside this session and require explicit approval plus a clean workspace:

1. Separate an order-invariant, proven `SafeBoundEvaluator` from the heuristic explanatory scheduler.
2. Define explicit cold-HBM, warm-L2, and initial-residency contracts and rerun controlled measurements.
3. Add CTA lifetime residency, multi-resource demand, and SM/lane affinity.
4. Add persistent-CTA multi-tile assignment and complete split-K replicated work/reduction semantics.
5. Give `tile_k` and partial tiles physically justified K-stage/padded-work behavior or migrate the API.
6. Replace experimental FA2 `cta_kv=64` and aggregate FA timing with validated canonical kernel-trait and phase semantics.
7. Refactor the near-quadratic ready scan only under a behavior-preserving scheduler plan and performance harness.
8. Run a named matched cycle-accurate benchmark before evaluating `10000x`.
9. Run a frozen held-out multi-hardware accuracy study before making an empirical zero-shot claim.
10. Validate interpretability against independent hardware counters and critical-path agreement, not final latency alone.

These are research and architecture tasks, not reasons to add a scale factor, clamp, fallback, or silent exclusion to the current prototype.
