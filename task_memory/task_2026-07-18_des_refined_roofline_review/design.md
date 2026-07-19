# DES Refined Roofline Review and Remediation Design

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added the reviewed two-contract architecture boundary and final evidence-status model. |
| 2026-07-18 | Established the review model and bounded metric contract. |

## Review Model

The review treats the DES claim as a chain rather than four independent slogans:

```text
hardware/workload specification
        -> operator lowering
        -> Event IR work + dependencies + resources
        -> deterministic schedule
        -> makespan + attribution
        -> matched measured-actual and classical/cycle-accurate comparisons
```

A failure in units, structural work, dependencies, resource capacity, scheduler complexity, or validation matching invalidates downstream claims even when structural tests pass.

## Metric Contract

For a valid latency lower bound:

```text
0 < DES_bound <= actual_time
optimization_gap = (actual_time - DES_bound) / actual_time
hardware_efficiency = DES_bound / actual_time
optimization_gap + hardware_efficiency = 1
```

`optimization_gap` represents the fraction of measured runtime not explained by the accepted structural bound. `hardware_efficiency` represents closeness to the bound. Neither metric is computed for non-positive times or silently accepted bound violations.

## Goal Evaluation Model

| Goal | Review Question |
|---|---|
| Structural tightness | Do modeled waves, tiles, cache traffic, resource lanes, and overlap materially improve a valid matched lower bound over a corrected classical roofline? |
| Design-space speed | Can prediction runtime be measured at the declared workload granularity, and is there a real cycle-accurate comparator for the `10000x` ratio? |
| Interpretability / zero-shot | Does the output explain the resource-critical path, and does the code avoid trained target-latency inference and target-hardware fitting? |
| Optimization gap | Are formulas, names, ranges, validation behavior, tests, and docs consistent with the bounded contract? |

## Change Boundary

Read-only review precedes every code edit. Confirmed local defects may receive surgical TDD fixes. Architectural rewrites, new external simulators, large benchmark campaigns, or bulk public-doc rewrites require a separate decision and clean workspace.

## Reviewed Contract Separation

The current implementation has two valid but deliberately disconnected public concepts:

```text
Event DAG + resources
        -> schedule(...)
        -> SimulationResult.makespan
           (heuristic explanatory feasible schedule)

caller-accepted positive bound + actual latency
        -> compare_des_bound(...)
        -> BoundComparison
           (validated numeric comparison only)
```

`compare_des_bound()` validates values but does not prove provenance. There is no automatic edge from `SimulationResult` to `BoundComparison`. A future certified design should add a separate order-invariant `SafeBoundEvaluator`; it must not rename or silently reinterpret the current scheduler result.

## Final Evidence Status

| Goal | Final design status |
|---|---|
| Structural interpretability | Established for explicit Event IR, resource work, selected timeline, and selected critical path; hardware-attribution agreement remains Experimental. |
| Tighter than classical roofline | Category/sample-scoped positive evidence for Large/Medium/Other, contradicted as a global claim by Small behavior and violations. |
| `10000x` design-space speed | Unproven because no matched cycle-accurate comparator exists; current scheduler scaling is itself an open risk. |
| Cross-hardware zero-shot | Mechanistic/specification-driven path exists; empirical transfer accuracy is Unproven. |
| Optimization gap | Implemented only for externally accepted values satisfying `0 < des_bound <= actual_time`. |
| Universal theoretical lower bound | Blocked pending a safe evaluator and matched policy/residency/measurement contracts. |
