# DES Refined Roofline Review and Remediation Harness

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added provenance separation, absolute-scale reporting, and final artifact-integrity gates. |
| 2026-07-18 | Added scheduler-bound, traffic-conservation, monotonicity, and matched-launch gates discovered during architecture review. |
| 2026-07-19 | Added the user-directed ignored-path and branch-delivery gates. |
| 2026-07-18 | Defined the scientific, performance, interpretability, and implementation gates. |

## Review Gates

1. **Matched-Baseline Gate:** Refined and classical roofline comparisons must use the same workload rows, actual measurements, hardware units, datatype, and fixed-overhead convention.
2. **Lower-Bound Gate:** Accepted rows satisfy `DES_bound <= actual_time`; violations are counted and cannot be hidden by skipping.
3. **Tightness Gate:** “Tighter” means a smaller absolute relative distance to actual latency while both candidates remain valid lower bounds.
4. **Performance-Claim Gate:** The `10000x` claim requires measured wall-clock runtimes against an identified cycle-accurate reference on the same modeled workload; event-count or complexity proxies are insufficient.
5. **Zero-Shot Gate:** A no-ML code path is necessary but not sufficient for an empirical zero-shot claim; held-out hardware evidence is required.
6. **Interpretability Gate:** A prediction must expose event work, resource attribution, overlap/serialization, and critical-path evidence sufficient to explain the makespan.
7. **Metric Gate:** `optimization_gap = (actual-DES)/actual` and `hardware_efficiency = DES/actual`; valid values are finite and bounded in `[0, 1]`.
8. **No-Fallback Gate:** Unexpected inputs, schema mismatches, simulation failures, and missing baselines fail fast.
9. **Root-Cause Gate:** No empirical correction factor or temporary scaling patch may stand in for a structural/unit/scheduler fix.
10. **TDD Gate:** Every behavior fix starts with a targeted failing test observed before production code changes.
11. **Review-Separation Gate:** Code/spec and architecture reviews must be independent; important decisions receive StepCode Claude challenge.
12. **Workspace-Safety Gate:** A broad refactor cannot start while pre-existing local changes remain uncommitted or unstashed.
13. **Scheduler-Bound Gate:** A feasible greedy schedule is not called a theoretical lower bound unless its makespan is proven no greater than every feasible actual schedule under the declared model. Input ordering must not change any public bound result.
14. **Traffic-Conservation Gate:** A cold-first-touch event cannot carry fewer bytes than the declared unique cold data. Any warm-cache assumption must be an explicit input state, not an implicit discount.
15. **Monotonicity Gate:** Under a fixed hardware/configuration policy, increasing required work or required traffic must not decrease the accepted lower-bound result without an explicit state transition that explains the change.
16. **Matched-Launch Gate:** Structural validation must reproduce or explicitly reject measured `cta_count`, persistent grouping, split-K, and reduction policy; reconstructing a different tile grid is not a matched structural comparison.
17. **Provenance-Separation Gate:** `SimulationResult.makespan` and an externally accepted `des_bound` are distinct types of evidence; no API or documentation may certify or convert the former implicitly.
18. **Absolute-Scale Gate:** Every scientific report must include actual, DES, and classical values in time units in addition to ratios, gaps, MAPE, or tightness counts.
19. **Artifact-Integrity Gate:** Completion requires all task artifacts, exact reproducible commands, fresh exit codes, an English summary, and a verified SHA-256 manifest; draft or stale status text is a failure.
20. **User-Scope Gate:** The historical `=10.1` path is ignored by explicit user instruction; it is excluded from active validation and staging, and no filesystem operation may target it.
21. **Delivery Gate:** The reviewed branch must be committed with the required decision-record trailers and pushed to `origin/des` before the next-stage implementation begins.

## Claim Status Vocabulary

- **PASS:** Reproducible evidence meets the stated acceptance criterion.
- **FAIL:** Reproducible evidence contradicts the criterion.
- **UNPROVEN:** Required baseline, dataset, or measurement does not exist or cannot be matched.
- **NOT APPLICABLE:** The goal is outside the reviewed component's declared scope.
