# Safe Bound Evaluator Next-Stage Issues

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Initialized the issue register for the narrow evaluator stage. |
| 2026-07-19 | Closed the final command-layer timing/quoting failure and recorded the resolution. |

## Issue Register

### S-001 — Existing scheduler is order-dependent

- **Evidence:** The fixed Event DAG produces `21.0` for long-first input and `11.0` for short-first input under `schedule()`.
- **Root Cause:** The current deterministic list scheduler selects the first ready event in caller-provided order and is not an order-invariant optimizer.
- **Impact:** `SimulationResult.makespan` cannot be silently certified as a universal lower bound.
- **Proposed Resolution:** Preserve the counterexample and add a separate evaluator with a mathematically explicit supported domain; do not rewrite `schedule()` here.
- **Status:** Open research boundary; addressed only by the next-stage scope.

### S-002 — Supported safe-bound domain is intentionally narrow

- **Evidence:** Resource contention, dependencies, and stream ordering introduce constraints not covered by `max(duration)` exactness.
- **Root Cause:** A general lower-bound proof requires additional scheduling and launch semantics that are deferred by the parent harness.
- **Impact:** Most current operator-generated event graphs remain unsupported by this evaluator.
- **Proposed Resolution:** Reject unsupported inputs explicitly and report coverage honestly; expand only through a separate reviewed task.
- **Status:** Open by design.

### S-003 — Initial final-verification shell wrapper was invalid

- **Evidence:** The first wrapper returned `/usr/bin/time: No such file or directory` for three commands and a Python `SyntaxError` from escaped inline f-string expressions; no test body ran in that attempt.
- **Root Cause:** The environment provides `time` as a shell keyword rather than `/usr/bin/time`, and the one-line quoting style escaped literals inside a heredoc unnecessarily.
- **Impact:** The first verification attempt produced no valid metrics, but it did not indicate a production-code failure.
- **Proposed Resolution:** Use the shell `time` keyword and compute counterexample values in intermediate Python variables before printing.
- **Status:** Resolved; the corrected verification completed with all required checks passing.
