# DES Event Simulator Documentation Backfill Lessons

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added double-checked documentation, unit, scheduling, and acceptance lessons. |
| 2026-07-18 | Created the vetted lessons register. |

## Vetted Reusable Lessons

### 1. Runtime ledgers are evidence, not durable acceptance records

Ignored `.omc` state can preserve useful execution history, but a `COMPLETE` row is not equivalent to satisfying the story's exit criterion. Durable task docs must reconstruct status from code, fresh tests, and the original numeric target.

### 2. Use three status dimensions

For research simulators, record `implemented`, `tested`, and `accepted` separately. G005 demonstrates why: the harness exists, structural tests pass, and the lower-bound sample has zero violations, yet the large-GEMM mean-gap target still fails.

### 3. Hardware JSON throughput is ops/cycle/SM

The verified conversion is:

```text
per_SM_ops_per_us = value * sm_freq_mhz
chip_wide_TFLOPS = value * sm_freq_mhz * num_sms / 1e6
```

For H100 BF16, `4096 * 1830 * 132 / 1e6 = 989.42976` TFLOPS. Treating `4096` directly as chip-wide TFLOPS overstates peak by `4.1397582381x` and invalidates comparative tightness metrics.

### 4. Rate units and lane counts form one contract

Resource capacity cannot be reviewed separately from calibration units. A chip-wide bytes/us coefficient on `num_sms` independent lanes multiplies aggregate service rate by `num_sms`; use one chip-wide lane or convert the coefficient to per-lane bandwidth.

### 5. Event labels do not prove a structural mechanism is modeled

An event type may be declared, calibrated, and tested for construction without being emitted. Likewise, naming an event `MMA_PartialTile` does not model partial-tile inefficiency if its work is only the useful clamped FLOPs. Validate the actual work/dependency/duration effect.

### 6. Scheduler scalability is part of validation credibility

The current repeated ready-event scan approaches O(V²). With p95 42,861 events in the 200-row Large sample, the official validation cannot finish interactively. Scientific acceptance requires a reproducible harness whose runtime scales to the declared dataset.

### 7. Preserve historical intent and current truth separately

`docs/event_simulator_design.md` is valuable as the Phase 0 research roadmap even though attention and GEMM v2 code now exist. Reconciliation should label it historical/stale in specific sections rather than rewrite history or silently copy current behavior into old claims.
