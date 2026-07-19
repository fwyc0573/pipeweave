# DES Full Semantics and Scientific Validation Harness

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Added the reviewed Wave-4 manifest-only lowering, cache-traffic primitive, worker/reduction, FA-affinity, topology, and authoritative-validator gates. |
| 2026-07-20 | Added reservation-normalized SafeBound demand, explicit greedy no-progress, and graph-validation timing boundaries. |
| 2026-07-20 | Added Phase-1 checkpoint, calibration-use separation, held-out prediction freeze, modeled-universal quantifier, and approved comparator lock gates. |
| 2026-07-20 | Added the manifest-order cache-domain gate after rejecting an unsafe isolated-cache lower-bound recommendation. |
| 2026-07-20 | Added lifetime-progress and scheduler-complexity-accounting gates after reconciling the shared execution-kernel review. |
| 2026-07-20 | Added explicit launch-metadata and report-provenance gates after the split-K, partial-tile, and report audits. |
| 2026-07-20 | Added solver-formulation and environment-reproducibility gates after the exact-solver audit. |
| 2026-07-20 | Added graph-normalization, exact-result, dependency-approval, and matched-state gates after the preliminary Claude review. |
| 2026-07-20 | Added explicit cross-architecture, environment-provenance, benchmark fail-fast, and exact-oracle evidence gates from the independent audit. |
| 2026-07-20 | Defined the phase, provenance, semantic, scientific-evidence, simplicity, and delivery gates for the new task. |

## Phase Gates

1. **Recovery Gate:** Parent design, harness, issues, review, SafeBound handoff, current source, tests, data, and branch state are recovered before new design decisions.
2. **Discussion Gate:** Every material ambiguity is resolved one question at a time and captured in `requirements.md` before implementation planning is finalized.
3. **Design-Review Gate:** Phase 1 ends only after an independent StepCode Claude review of the complete design, GSD decomposition, tests, and evidence plan. `BLOCK` stops execution for user adjudication.
4. **Production-Freeze Gate:** No production code is modified before the Design-Review Gate passes.
5. **TDD Gate:** Every behavior change has personally observed RED evidence, minimal GREEN implementation, and focused refactor verification.
6. **Module-Review Gate:** Each important module milestone receives an independent Claude review before the dependent wave begins.
7. **Final-Verification Gate:** Completion requires targeted tests, full regression, static checks, scientific evaluations, numeric reports, independent review, clean commit, and pushed remote equality.
8. **Phase-1 Checkpoint Gate:** Phase 2 begins only after the complete design/GSD package passes fresh regression and document checks, is committed with Lore trailers, is pushed, and local `HEAD` equals `origin/des`.

## Bound and Scheduler Gates

9. **Provenance-Separation Gate:** Exact optimum, scalable safe bound, feasible scheduler, and measured-hardware comparison use distinct result contracts.
10. **Exactness Gate:** Any “exact” result equals the modeled optimum for every accepted input in its declared domain; complexity/domain limits fail fast.
11. **Order-Invariance Gate:** Permuting semantically equivalent Event input does not alter any public exact or safe-bound result.
12. **Safety Gate:** Every scalable bound is proven no greater than the exact modeled optimum for the accepted model domain.
13. **Scheduler-Feasibility Gate:** Every returned scheduler output respects dependency, capacity, lifetime, simultaneous-demand, and affinity constraints. Explicit no-progress is permitted for the fixed greedy policy but must not be mislabeled as a proof that the graph is infeasible.
14. **Scheduler-Policy Gate:** Determinism and compatibility are tested against the accepted policy; caller list order cannot be an undocumented policy input.
15. **Scheduler-Performance Gate:** Complexity claims use measured wall-clock runtime across declared graph sizes and report absolute event/edge counts.

## Execution-Semantics Gates

16. **Cache-State Gate:** Cache hierarchy, residency, warm state, transitions, capacity, and eviction are explicit and auditable.
17. **Traffic-Conservation Gate:** Cold unique bytes, warm hits, evictions, writebacks, and reductions conserve declared physical traffic.
18. **CTA-Lifetime Gate:** CTA resources are held for the declared lifetime; simultaneous multi-resource demand is acquired consistently without partial hidden admission.
19. **Affinity Gate:** SM/lane affinity is explicit and enforced; unsupported or impossible affinity fails fast.
20. **Persistent-CTA Gate:** Persistent worker count and work assignment come from explicit policy metadata and preserve total work.
21. **Split-K Gate:** Replicated input/work, partial outputs, and reduction work/traffic are modeled explicitly and matched to launch metadata.
22. **Partial-Tile Gate:** Useful logical work and padded physical execution are distinct quantities; reports and bounds state which one they use.
23. **Monotonicity Gate:** Increasing required physical work or traffic cannot reduce a bound under fixed policy/state without an explicit state transition explaining the change.

## Scientific-Evidence Gates

24. **Cycle-Level Comparator Gate:** Speedup requires the approved version-pinned GPGPU-Sim PTX-mode comparator, the same A100 manifest/boundary, reproducible commands, and measured wall-clock runtime; strict silicon cycle-accuracy is not claimed.
25. **Held-Out Zero-Shot Gate:** Target hardware is excluded from fitting, measured calibration, threshold selection, rule changes, and development decisions for the held-out study.
26. **Calibration-Provenance Gate:** Measured-hardware calibration declares the fitted primitive parameters, calibration workload, units, uncertainty, and non-overlap with evaluation data.
27. **Calibration-Use Separation Gate:** Specification calibration is the only target calibration allowed in zero-shot. Target measured primitive calibration is reported as a separate non-zero-shot empirical audit and never silently certifies a physical lower bound.
28. **Held-Out Prediction Freeze Gate:** The prediction artifact, supported/unsupported decisions, manifest/calibration hashes, and commands are frozen before target final latency is read for scoring.
29. **Matched-Hardware Gate:** DES and measurements match hardware, datatype, shape, launch policy, cache/residency state, timing boundary, and fixed-overhead convention.
30. **Universal-Claim Gate:** A universal claim states its quantifiers and proof domain. A modeled-domain theorem and a real-hardware empirical claim are never merged.
31. **Modeled-Quantifier Gate:** The initial theorem is limited to finite normalized fixed-duration graphs after one manifest-order cache resolution; lifetime and affinity are named relaxations rather than unproved tightening terms.
32. **Absolute-Scale Gate:** Every comparison reports expected/actual values, absolute delta, relative delta, sample count, and unsupported/violation counts.

## Engineering and Safety Gates

33. **No-Fallback Gate:** Unexpected inputs, unsupported semantics, missing evidence, and schema mismatch raise explicit errors.
34. **Root-Cause Gate:** No scaling factor, clamp, skip, or temporary correction may replace a semantic/modeling fix.
35. **Simplicity Gate:** Avoid duplicate validators, parallel data models, speculative extension points, and defensive checks outside the invariant-owning boundary.
36. **Regression Gate:** Unit tests cover every changed function and branch; integration/e2e tests cover cross-module and scientific workflows.
37. **Workspace-Safety Gate:** No broad change starts from a dirty pre-existing workspace; no `rm` or `mv` occurs without explicit permission.
38. **Ignored-Path Gate:** No operation, inspection, staging, or blocker analysis targets `=10.1`.
39. **Artifact-Integrity Gate:** All task documents have Modification History; the final English summary includes exact paths, hashes, test/evaluation matrices, and open items.
40. **Cross-Architecture Naming Gate:** Hopper-only transfer evidence is never labeled broad cross-architecture zero-shot evidence.
41. **Environment-Provenance Gate:** Measured results record hardware identity, driver/CUDA/compiler, clock/power policy, dtype, benchmark revision, warmup/repeats, and raw-sample or uncertainty data.
42. **Benchmark-Fail-Fast Gate:** A benchmark failure aborts with the exact context; catch-all-and-continue behavior is prohibited in authoritative validation.
43. **Exact-Oracle Audit Gate:** Small accepted resource/DAG cases are checked against an independent exact oracle, including input permutations, conservation, monotonicity, and unsupported-domain counts.
44. **Graph-Normalization Gate:** Certified bound/oracle paths consume one normalized graph contract; implicit stream order may not depend on iterable order.
45. **Exact-Result Gate:** Solver timeout, search exhaustion, or nonzero optimality gap returns no exact result and raises an explicit error; partial/heuristic output is never relabeled exact.
46. **Dependency-Approval Gate:** No third-party solver or package is added without explicit approval and a clean environment/baseline check. Accel-Sim/GPGPU-Sim and its pinned CUDA/`nvcc` environment are the only newly approved dependency set for this task.
47. **Matched-State Gate:** Bound proof, exact oracle, feasible schedule, and measured comparison use the same declared cache/residency state; cold and warm states cannot be exchanged as a safety argument.
48. **Solver-Formulation Gate:** Every accepted solver constraint has a model-level proof, including precedence, capacity, simultaneous demand, affinity, lifetime reservation, and makespan objective; solver `success` alone does not validate the formulation.
49. **Solver-Reproducibility Gate:** The selected solver/version is declared by the project and recorded in the test environment; ambient host availability is insufficient.
50. **Search-Coverage Gate:** A built-in enumerator is exact only after proving that its generated schedules cover at least one optimum for every accepted input and after complete-search evidence is returned.
51. **Launch-Metadata Gate:** Split factor, persistent grouping, work assignment, and reduction topology come from authoritative explicit metadata; `is_split_k`, CTA ratios, or shape heuristics may not be used as a fallback reconstruction.
52. **Report-Provenance Gate:** Dependency critical path, exact optimum, analytical bound, feasible-schedule makespan, and measured comparison remain separately named report quantities; multi-resource busy time is demand-weighted resource time rather than one unqualified duration sum.
53. **Lifetime-Progress Gate:** Lifetime-held occupancy and transient execution demand are distinct. Members consume held resources only from their own sufficient reservation; SafeBound and scheduler share the same reservation normalization; additional transient demands remain atomic and event-local; cross-lifetime member hold-and-wait is rejected; and greedy-policy no-progress raises explicitly rather than stalling or returning a partial schedule.
54. **Scheduler-Complexity-Accounting Gate:** Graph construction/validation, scheduler graph/queue work, multi-resource placement, and report assembly are reported separately. No total asymptotic claim may omit per-member lifetime reachability, blocked-ready wakes, eligible-SM checks, lifetime admission, or actual measured runtime.
55. **Static-Cache-Domain Gate:** Cache resolution, exact optimum, SafeBound, and feasible scheduling consume one identical manifest-order fixed-state model. Its theorem is labeled as abstract modeled evidence and is never generalized to arbitrary hardware interleavings; an overcounting cache alternative cannot be called lower-bound-safe.
56. **Manifest-Only Lowering Gate:** `lower_gemm_v2` requires one validated `GemmLaunchManifest` and explicit `InitialCacheState`, returns `EventGraph`, and accepts no legacy dimension/tile/hardware compatibility signature or inferred stream order.
57. **Resource-Specific Traffic Gate:** One cache resolution lowers to byte-conserving `HBMRead`, `HBMWrite`, `L2Read`, and `L2Write` Events on the shared `hbm_bandwidth` and `l2_bandwidth` resources; clean eviction emits no resource-time Event and no second traffic model exists.
58. **Worker-and-Reduction Gate:** Every Worker owns one acquire-to-release `ResourceLifetime`; ordered WorkItems use physical-issued work; reductions remain outside Worker lifetimes, depend on authoritative accumulator producers, and output flushes explicitly precede completion.
59. **Hardware-Topology Gate:** `sm_count` expresses lane replication, chip-wide launch/HBM/L2 capacities remain global, and tensor/ALU/SFU/barrier/CTA capacities are per-SM rather than multiplied by the number of SMs.
60. **Authoritative-Validator-and-FA Gate:** The sole GEMM validator requires row-indexed authoritative manifests and counts missing/mismatched entries without policy reconstruction. FA uses explicit singleton SM affinity and dependency chains; tuple order cannot influence placement.

## Claim Status Vocabulary

- **PASS:** Reproducible evidence meets the declared acceptance criterion.
- **FAIL:** Reproducible evidence contradicts the criterion.
- **UNPROVEN:** Required proof, comparator, dataset, or matched measurement is absent.
- **BLOCKED:** An external or user-adjudicated condition prevents the required work.
- **NOT APPLICABLE:** The claim is outside the declared component or evaluation domain.
