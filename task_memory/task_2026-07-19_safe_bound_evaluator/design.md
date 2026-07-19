# Safe Bound Evaluator Next-Stage Design

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Defined the smallest additive order-invariant evaluator domain and provenance boundary for the next stage. |

## Goal

Add one independently auditable bound evaluator without changing the existing heuristic scheduler. The evaluator is exact for a deliberately narrow class of Event inputs and rejects every input outside that class.

## Supported Domain

`SafeBoundEvaluator` accepts a non-empty iterable of `Event` values only when all of the following hold:

1. Every event has a unique `event_id`.
2. Every event has no explicit dependencies (`dependencies == ()`).
3. Every event is not stream-ordered (`stream_ordered is False`).
4. Every event has no resource assignment (`resource is None`).
5. Event construction has already established finite, non-negative durations.

In this domain all events can begin at time zero and no modeled constraint couples them. Therefore the exact minimum makespan of the modeled schedule is:

```text
safe_bound = max(event.duration for event in events)
```

The evaluator relies on `Event.__post_init__` for finite, non-negative duration validation; it does not duplicate that check. The evaluator returns zero for a non-empty all-zero workload. An empty iterable is rejected because it has no workload provenance. A resource assignment, dependency, stream-ordering flag, or duplicate identifier is rejected with `ValueError`; no fallback schedule is synthesized.

## Public Interface

Create `event_simulator/safe_bound.py`:

```python
from collections.abc import Iterable
from dataclasses import dataclass

from .events import Event


@dataclass(frozen=True)
class SafeBound:
    bound: float


class SafeBoundEvaluator:
    def evaluate(self, events: Iterable[Event]) -> SafeBound:
        ...
```

Export `SafeBound` and `SafeBoundEvaluator` from `event_simulator.__init__`. The result is a distinct type from `SimulationResult`; callers must explicitly select `.bound` before passing a value to `compare_des_bound`. The evaluator does not import or call `schedule` and does not claim a bound relative to measured hardware latency.

## Non-goals

This stage does not change `schedule()`, `SimulationResult`, resource capacities, stream semantics, CTA admission, cache state, persistent CTAs, split-K, partial-tile behavior, FA kernels, or benchmark claims. It does not add a convenience conversion to `BoundComparison`.

## Evidence Fixture

Keep a regression fixture for the existing scheduler's order dependence:

```text
same Event DAG:
long-first  -> makespan 21.0
short-first -> makespan 11.0
```

The fixture demonstrates why the current scheduler cannot be silently certified. The safe evaluator test covers only independent unresource-bound events and proves the result is invariant under input permutation.

## Accepted Design Review

StepCode Claude reviewed this design before implementation and returned **APPROVE**. The review confirmed that the supported-domain result is the exact optimal modeled makespan, that the `SafeBound` type preserves provenance separation, and that the five domain checks are minimal rather than over-defensive. The review artifact is `.omx/artifacts/claude-perform-an-independent-design-review-before-implementation-f-2026-07-19T16-22-50-016Z.md`.
