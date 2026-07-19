# Safe Bound Evaluator Implementation Plan

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Defined the staged RED -> GREEN -> review -> artifact-closure execution plan. |
| 2026-07-19 | Closed RED/GREEN, independent review, regression verification, and artifact-closure steps before commit. |
| 2026-07-19 | Recorded the pushed SafeBound checkpoint and completed the final plan step. |

> **For agentic workers:** Execute this plan with strict RED -> GREEN -> REFACTOR and independent review checkpoints. Do not expand the supported domain without a new design decision.

**Goal:** Add an additive, order-invariant `SafeBoundEvaluator` for independent unresource-bound Event workloads while preserving the existing heuristic scheduler contract.

**Architecture:** Keep `event_simulator/scheduler.py` unchanged. Place the proof-domain checks and the exact `max(duration)` calculation in a focused `event_simulator/safe_bound.py` module. Return a frozen `SafeBound` value object so callers must explicitly choose `.bound`; no implicit edge to `SimulationResult` or `BoundComparison` exists.

**Tech Stack:** Python 3.12, pytest, dataclasses, repository Event model, StepCode Claude review.

## Global Constraints

- Follow `task_memory/task_2026-07-19_safe_bound_evaluator/design.md` and `harness.md` as binding.
- Do not modify scheduler behavior, cache/resource models, CTA semantics, split-K, or benchmark claims.
- Do not add fallback logic, empirical correction factors, or broad shared abstractions.
- The historical `=10.1` path remains outside all active work by the prior user instruction.

---

### Task 1: Lock the scheduler counterexample

**Files:**
- Test: `tests/unit/test_safe_bound.py`

**Interfaces:**
- Consumes: existing `Event`, `ResourceConfig`, and `schedule` APIs.
- Produces: a checked-in regression proving the same DAG can yield `21.0` and `11.0` solely from input order.

- [x] **Step 1: Write the regression test**

```python
def test_existing_scheduler_order_counterexample_is_recorded():
    results = {
        name: schedule(events, ResourceConfig({"a": 1, "b": 1})).makespan
        for name, events in (long_first_events(), short_first_events())
    }
    assert results == {"long-first": 21.0, "short-first": 11.0}
```

Use the exact Event definitions from `design.md`; keep the fixture local to the test.

- [x] **Step 2: Run the focused test**

Run: `PYTHONPATH="$PWD" python -m pytest tests/unit/test_safe_bound.py::test_existing_scheduler_order_counterexample_is_recorded -q`

Expected: PASS with `1 passed`; this records the existing behavior and is not a production change.

### Task 2: Define the failing evaluator contract

**Files:**
- Create: `tests/unit/test_safe_bound.py`

**Interfaces:**
- Consumes: the Event fixture from Task 1.
- Produces: RED tests for `SafeBoundEvaluator.evaluate` and `SafeBound` provenance.

- [x] **Step 1: Add the supported-domain test**

```python
def test_safe_bound_is_invariant_under_input_order():
    evaluator = SafeBoundEvaluator()
    events = independent_events()
    assert evaluator.evaluate(events).bound == 10.0
    assert evaluator.evaluate(tuple(reversed(events))).bound == 10.0
```

- [x] **Step 2: Add rejection and edge tests**

Cover an empty iterable, duplicate IDs, explicit dependencies, stream-ordered events, resource-assigned events, and a non-empty all-zero workload. Assert exact `ValueError` messages for unsupported cases and `0.0` for the all-zero result.

- [x] **Step 3: Add provenance separation**

```python
def test_safe_bound_is_not_implicitly_a_bound_comparison_input():
    result = SafeBoundEvaluator().evaluate(independent_events())
    with pytest.raises(ValueError):
        compare_des_bound(actual_time=10.0, des_bound=result)
```

- [x] **Step 4: Run the RED suite**

Run: `PYTHONPATH="$PWD" python -m pytest tests/unit/test_safe_bound.py -q`

Expected: FAIL because `SafeBoundEvaluator` and `SafeBound` are not yet exported; the failure must be an import/API failure, not a test typo.

### Task 3: Implement the minimal evaluator

**Files:**
- Create: `event_simulator/safe_bound.py`
- Modify: `event_simulator/__init__.py`

**Interfaces:**
- Consumes: `Iterable[Event]`.
- Produces: `SafeBoundEvaluator.evaluate(events) -> SafeBound` with `bound = max(duration)` for the supported domain.

- [x] **Step 1: Implement only the proven domain**

```python
@dataclass(frozen=True)
class SafeBound:
    bound: float


class SafeBoundEvaluator:
    def evaluate(self, events: Iterable[Event]) -> SafeBound:
        ordered = tuple(events)
        if not ordered:
            raise ValueError("safe bound requires at least one event")
        ids = [event.event_id for event in ordered]
        if len(set(ids)) != len(ids):
            raise ValueError("safe bound requires unique event ids")
        for event in ordered:
            if event.dependencies:
                raise ValueError("safe bound supports independent events only")
            if event.stream_ordered:
                raise ValueError("safe bound requires stream_ordered=False")
            if event.resource is not None:
                raise ValueError("safe bound requires resource=None")
        return SafeBound(max(event.duration for event in ordered))
```

Do not import `schedule`, `ResourceConfig`, or `BoundComparison` in this module.

- [x] **Step 2: Run the focused GREEN suite**

Run: `PYTHONPATH="$PWD" python -m pytest tests/unit/test_safe_bound.py -q`

Expected: all evaluator tests pass, including the `21.0`/`11.0` scheduler fixture and the zero-work edge case.

- [x] **Step 3: Run the existing scheduler and package tests**

Run: `PYTHONPATH="$PWD" python -m pytest tests/unit/test_event_scheduler.py tests/unit/test_bound_comparison.py -q`

Expected: all existing tests pass with no scheduler behavior change.

### Task 4: Review, regression, and artifact closure

**Files:**
- Modify: `task_memory/task_2026-07-19_safe_bound_evaluator/progress.md`, `review.md`, `summary.md`, `test_report_2026-07-19_safe_bound_evaluator.md`, `checksums.sha256`

**Interfaces:**
- Consumes: focused and full test evidence plus the independent Claude review artifacts.
- Produces: a reviewable task record with exact numeric results and no unsupported scientific claim.

- [x] **Step 1: Run post-implementation `ask Claude` review**

Use `omx ask claude` with the module, tests, design, and harness as context. Record the artifact path, verdict, findings, and any accepted/rejected suggestions in `review.md`.

- [x] **Step 2: Run final verification**

Run the focused evaluator suite, full `tests` suite, `compileall`, the order-counterexample command, `git diff --check`, and the task-manifest checksum audit. Record exact counts and timings.

- [x] **Step 3: Complete the English summary**

Include `Task Overview`, `Deliverables Inventory` with exact paths and hashes, `Validation Status` with numeric matrices, and `Open Items/Future Extensions`. Keep the existing universal-bound and measured-hardware claims explicitly outside scope.

- [x] **Step 4: Commit and push the next-stage checkpoint**

Use a Lore-protocol commit containing only the new evaluator module/test and this task's artifacts. Push with `git push` only after a clean staged diff and fresh verification.
