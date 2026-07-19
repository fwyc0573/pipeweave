# Safe Bound Evaluator Next-Stage Harness

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Defined the narrow-domain, provenance, TDD, and review gates for the evaluator stage. |

## Acceptance Gates

1. **Two-Contract Gate:** `SimulationResult.makespan` remains a heuristic schedule estimate. `SafeBound` is a distinct result type and is never implicitly converted to `BoundComparison`.
2. **Order-Invariance Gate:** Permuting independent supported events does not change `SafeBound.bound`.
3. **Proof-Domain Gate:** The evaluator supports only non-empty events with unique IDs, no dependencies, `stream_ordered=False`, and `resource=None`; every other domain fails fast with `ValueError`.
4. **Exactness Gate:** For the supported domain, `bound == max(event.duration)` including an all-zero non-empty workload.
5. **No-Fallback Gate:** Unsupported dependencies, stream ordering, resource assignments, duplicate IDs, and empty input are rejected; no call to the heuristic scheduler is used to produce a substitute value.
6. **TDD Gate:** The order-dependence fixture and evaluator behavior each have observed RED -> GREEN evidence before completion.
7. **Simplicity Gate:** Add only the evaluator module, its focused unit tests, package exports, and task evidence; do not extract shared helpers or refactor adjacent scheduler code.
8. **Review Gate:** Obtain StepCode Claude design review before implementation and an independent post-implementation review after the module/test milestone.
9. **Regression Gate:** The full existing test suite remains green, and the scheduler's `21.0` / `11.0` evidence remains unchanged.
10. **Scientific Boundary Gate:** Do not describe the evaluator result as a measured-hardware lower bound, a universal DES bound, or evidence for `10000x`, zero-shot, cache, CTA, or cycle-accurate claims.
11. **Artifact Gate:** Every task artifact has Modification History, exact commands and numeric outputs are recorded, and the final manifest verifies all listed files.
