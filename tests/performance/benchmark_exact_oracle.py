"""Measure complete-search scaling and explicit budget failure semantics."""

from __future__ import annotations

from dataclasses import dataclass
from math import factorial
from time import perf_counter

from event_simulator import (
    Event,
    EventGraph,
    IncompleteExactSearchError,
    ResourceConfig,
    solve_exact_schedule,
)


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    graph: EventGraph
    config: ResourceConfig
    expected_permutations: int
    expected_makespan: float


def main() -> None:
    cases = [
        _independent_case(event_count)
        for event_count in range(1, 10)
    ]
    cases.extend((_resource_serial_case(8), _chain_case(128)))

    print(
        "case,event_count,edge_count,resource_count,"
        "precedence_feasible_permutations,completion_status,"
        "expected_makespan,actual_makespan,absolute_delta,runtime_seconds"
    )
    for case in cases:
        started = perf_counter()
        result = solve_exact_schedule(case.graph, case.config)
        elapsed = perf_counter() - started
        delta = abs(result.makespan - case.expected_makespan)
        if delta != 0.0:
            raise AssertionError(
                f"unexpected exact result for {case.name}: {result.makespan}"
            )
        edge_count = sum(len(event.dependencies) for event in case.graph.events)
        resource_count = len(case.config.global_capacities) + len(
            case.config.per_sm_capacities
        )
        print(
            f"{case.name},{len(case.graph.events)},{edge_count},"
            f"{resource_count},{case.expected_permutations},complete,"
            f"{case.expected_makespan},{result.makespan},{delta},"
            f"{elapsed:.9f}"
        )

    _benchmark_budget_exhaustion()


def _independent_case(event_count: int) -> BenchmarkCase:
    graph = EventGraph(
        tuple(_event(index) for index in range(event_count))
    )
    return BenchmarkCase(
        name=f"independent-{event_count}",
        graph=graph,
        config=ResourceConfig({}, 1, {}),
        expected_permutations=factorial(event_count),
        expected_makespan=1.0,
    )


def _resource_serial_case(event_count: int) -> BenchmarkCase:
    graph = EventGraph(
        tuple(
            _event(index, global_demand={"resource": 1})
            for index in range(event_count)
        )
    )
    return BenchmarkCase(
        name=f"resource-serial-{event_count}",
        graph=graph,
        config=ResourceConfig({"resource": 1}, 1, {}),
        expected_permutations=factorial(event_count),
        expected_makespan=float(event_count),
    )


def _chain_case(event_count: int) -> BenchmarkCase:
    events = []
    for index in range(event_count):
        dependencies = () if index == 0 else (_event_id(index - 1),)
        events.append(_event(index, dependencies=dependencies))
    return BenchmarkCase(
        name=f"chain-{event_count}",
        graph=EventGraph(tuple(events)),
        config=ResourceConfig({}, 1, {}),
        expected_permutations=1,
        expected_makespan=float(event_count),
    )


def _benchmark_budget_exhaustion() -> None:
    event_count = 9
    budget = 1_000
    graph = EventGraph(tuple(_event(index) for index in range(event_count)))
    started = perf_counter()
    try:
        solve_exact_schedule(
            graph,
            ResourceConfig({}, 1, {}),
            max_permutations=budget,
        )
    except IncompleteExactSearchError:
        elapsed = perf_counter() - started
    else:
        raise AssertionError("budget exhaustion returned an exact result")
    print(
        f"budget-exhaustion-{event_count},{event_count},0,0,{budget},"
        f"incomplete,,,,{elapsed:.9f}"
    )


def _event(
    index: int,
    *,
    dependencies: tuple[str, ...] = (),
    global_demand: dict[str, int] | None = None,
) -> Event:
    return Event(
        event_id=_event_id(index),
        event_type="MMA",
        kernel_id="kernel",
        stream_id="stream",
        duration=1.0,
        dependencies=dependencies,
        global_demand=global_demand or {},
    )


def _event_id(index: int) -> str:
    return f"event-{index:03d}"


if __name__ == "__main__":
    main()
