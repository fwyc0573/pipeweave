# Safe Bound Evaluator Next-Stage Requirements

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Captured the bounded next-stage request after the DES remediation branch checkpoint. |

## Requirements

1. **[Original Request]** Continue the DES work from the pushed bounded-remediation checkpoint without reopening the deferred scheduler, cache, CTA, split-K, or cycle-accurate architecture work.
2. **[Original Request]** Preserve the two-contract boundary in `task_memory/task_2026-07-18_des_refined_roofline_review/design.md`: the existing `SimulationResult.makespan` remains a heuristic schedule estimate, while any accepted bound must have a separate provenance-bearing API.
3. **[Original Request]** Establish and test the known order-dependence counterexample in which the same Event DAG produces `21.0` for long-first input and `11.0` for short-first input under the existing scheduler.
4. **[Original Request]** Enter the smallest reversible next stage for an order-invariant `SafeBoundEvaluator` over a narrowly supported independent-work domain, with unsupported domains rejected explicitly rather than approximated.
5. **[Original Request]** Obtain an independent StepCode Claude design review before implementation and a separate review after the key module and tests are implemented.
6. **[Original Request]** Keep implementation and tests minimal, avoid over-defensive validation and redundant abstractions, and keep all acceptance criteria aligned with this task's `design.md` and `harness.md`.

## Follow-up Q&A

No additional user questions were required; the prior checkpoint's independent review supplied the minimal next-stage boundary.
