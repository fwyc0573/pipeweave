# DES Refined Roofline Review and Remediation Lessons

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added vetted scheduler, boundary, traffic, resource-unit, unsupported-accounting, zero-shot, and evidence-interpretation lessons. |
| 2026-07-18 | Added the verified time-domain versus rate-domain metric lesson. |

## Vetted Reusable Lessons

### Time lower bounds and performance rates invert the apparent gap direction

For `DES_time <= actual_time`, the bounded time-domain gap is:

```text
optimization_gap = (actual_time - DES_time) / actual_time
```

The equivalent rate-domain expression is `(peak_rate - actual_rate) / peak_rate`, because rate is inverse time for fixed work. Copying the rate-domain numerator directly into a time-domain formula reverses the sign and changes the range.

### A feasible list schedule is not a lower bound on optimal makespan

For a minimization problem, any feasible schedule witnesses an **upper bound** on the modeled optimum. A greedy scheduler can add ordering-dependent serialization even when every primitive duration is optimistic. Peak-rate events therefore do not certify the composed makespan. A safe public design must separate an explanatory schedule from a proven bound evaluator or prove optimality for the supported DAG class.

### Comparisons require one named completion and residency boundary

Classical and refined candidates are comparable only when they use the same datatype, input residency, output visibility, work convention, and hardware rate units. Charging output C to HBM for one candidate and ending at L2 for the other is not a matched roofline comparison. A validation row also cannot prove a cold-HBM bound when the measurement does not record its cache initial state.

### A chip-wide rate must be represented exactly once

When a calibration coefficient is derived from a chip-wide bandwidth, the scheduler resource must have one aggregate lane. Combining a chip-wide rate with `num_sms` lanes silently multiplies capacity. A per-SM lane model is valid only when the coefficient is explicitly per-SM and events preserve the required affinity.

### Reuse cannot reduce unique cold traffic below one first touch

L2 reuse can reduce repeated CTA demand down to unique matrix bytes. It cannot divide already-unique cold bytes again. Under a cold-HBM contract, unique A and unique B each cross HBM once. A different result requires an explicit initial-residency state rather than an implicit reuse discount.

### Unsupported rows must remain in the accounting story

Rejecting split-K or launch-policy mismatches is scientifically preferable to simulating the wrong kernel, but rejection must be named and counted. The supported subset, full input population, and rejection reasons must all remain visible; otherwise favorable metrics can be created by silently shrinking the denominator.

### A no-ML execution path is not empirical zero-shot evidence

Loading only hardware specifications and avoiding a learned final-latency closure establishes a mechanistic path. It does not establish held-out transfer accuracy, especially when the target row supplies kernel policy such as tile sizes. Empirical zero-shot acceptance requires a pre-declared held-out multi-hardware protocol without target-hardware fitting.

### Better aggregate error does not establish a scientific bound

The corrected Small candidate improved MAPE while increasing bound violations. This is not contradictory: moving a candidate closer to measured time can improve average error and simultaneously cross above some measurements. Bound acceptance depends on every declared invariant and measurement precondition, not on MAPE alone.

### Public value objects should own their invariants

If a validated factory returns a publicly constructible type, factory-only validation is insufficient. The value object must compute derived fields from validated primary fields and reject inconsistent direct construction. This prevents a safe convenience function from coexisting with an unsafe public constructor.
