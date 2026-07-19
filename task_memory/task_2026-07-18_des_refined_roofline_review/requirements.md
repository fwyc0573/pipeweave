# DES Refined Roofline Review and Remediation Requirements

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added the original task-memory documentation-backfill requirement to the durable source of truth. |
| 2026-07-19 | Added the user-directed ignored-path, branch-delivery, and next-stage review requirements. |
| 2026-07-18 | Captured the original review/remediation request and the resolved metric-contract Q&A. |

## Requirements

1. **[Original Request]** Review the current DES code modules and documentation against the stated Refined Roofline design goals.
2. **[Original Request]** Determine whether DES is tighter than a traditional roofline because it models structural effects.
3. **[Original Request]** Determine whether DES is at least `10000x` faster than a cycle-accurate simulator and suitable for design-space exploration.
4. **[Original Request]** Determine whether DES is more interpretable than an ML predictor and supports zero-shot transfer across hardware.
5. **[Original Request]** Provide a scientifically valid optimization-gap metric for comparing the DES bound with actual latency.
6. **[Original Request]** Fix and supplement code and documentation when evidence shows the implementation or claims are incorrect, unreasonable, or incomplete.
7. **[Original Request]** Consult StepCode Claude extensively for design discussion and independent review.
8. **[Original Request]** Create the missing `task_memory/` task record and complete the required documentation artifacts from the existing design documents, ignored Ultragoal records, implementation, tests, review evidence, and final validation.
9. **[Original Request]** Ignore the historical path named `=10.1`; do not include it in active validation or staging, and do not create, delete, move, inspect, or modify it.
10. **[Original Request]** Organize, commit, and push the current branch, then enter the next bounded stage while keeping `design.md` and `harness.md` binding and obtaining StepCode Claude reviews after key module implementation and stage reviews.

## Follow-up Q&A

1. **[Original Request]** Metric contract decision: expose only the bounded time-domain metrics `optimization_gap = (actual_time - DES_bound) / actual_time` and `hardware_efficiency = DES_bound / actual_time`; do not expose `(DES_bound - actual_time) / DES_bound` as an optimization-gap metric.
