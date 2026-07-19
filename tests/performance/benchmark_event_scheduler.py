"""Measure normalized graph, scheduler, and report scaling separately."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import sys
from time import perf_counter
from typing import Mapping

from event_simulator import (
    Event,
    EventGraph,
    ResourceConfig,
    build_report,
    schedule,
    solve_exact_schedule,
)


FIELD_NAMES = (
    "event_count",
    "edge_count",
    "resource_count",
    "graph_build_seconds",
    "schedule_seconds",
    "report_seconds",
    "ready_queue_operations",
    "blocked_ready_rechecks",
    "placement_checks",
    "lifetime_checks",
    "old_runtime_seconds",
    "new_runtime_seconds",
    "speedup",
    "makespan",
    "exact_optimum",
    "optimality_gap",
    "feasibility_violation_count",
    "determinism_mismatch_count",
)


@dataclass(frozen=True)
class BenchmarkCase:
    cta_count: int
    sm_count: int
    old_runtime_seconds: float | None
    run_exact: bool = False


@dataclass(frozen=True)
class BenchmarkInput:
    graph: EventGraph
    config: ResourceConfig


@dataclass(frozen=True)
class BenchmarkResult:
    event_count: int
    edge_count: int
    resource_count: int
    graph_build_seconds: float
    schedule_seconds: float
    report_seconds: float
    ready_queue_operations: int
    blocked_ready_rechecks: int
    placement_checks: int
    lifetime_checks: int
    old_runtime_seconds: float | None
    new_runtime_seconds: float
    speedup: float | None
    makespan: float
    exact_optimum: float | None
    optimality_gap: float | None
    feasibility_violation_count: int
    determinism_mismatch_count: int

    def to_row(self) -> dict[str, int | float | None]:
        return {
            field_name: getattr(self, field_name)
            for field_name in FIELD_NAMES
        }


EXACT_CASE = BenchmarkCase(
    cta_count=1,
    sm_count=1,
    old_runtime_seconds=None,
    run_exact=True,
)

# These reviewed parent-task values are legacy scheduler-time measurements.
# They provide size-matched historical context, not a stage-matched speed study.
HISTORICAL_CASES = (
    BenchmarkCase(128, 132, 0.014082),
    BenchmarkCase(256, 132, 0.034505),
    BenchmarkCase(512, 132, 0.090736),
    BenchmarkCase(1_024, 132, 0.280886),
    BenchmarkCase(2_048, 132, 1.038378),
    BenchmarkCase(19_488, 132, 115.882818766),
)

DEFAULT_CASES = (EXACT_CASE, *HISTORICAL_CASES)


def build_benchmark_input(
    *,
    cta_count: int,
    sm_count: int,
) -> BenchmarkInput:
    """Build one deterministic GEMM-like normalized scheduling workload."""

    _require_positive_integer("cta_count", cta_count)
    _require_positive_integer("sm_count", sm_count)

    launch_id = "benchmark-gemm:launch"
    hbm_id = "benchmark-gemm:hbm"
    events = [
        Event(
            event_id=launch_id,
            event_type="KernelLaunch",
            kernel_id="benchmark-gemm",
            stream_id="stream-0",
            duration=0.5,
            global_demand={"launch": 1},
        ),
        Event(
            event_id=hbm_id,
            event_type="GlobalLoad_L2Miss",
            kernel_id="benchmark-gemm",
            stream_id="stream-0",
            duration=1.0,
            dependencies=(launch_id,),
            global_demand={"hbm": 1},
        ),
    ]
    store_ids = []
    for cta_index in range(cta_count):
        cta_id = f"benchmark-gemm:cta-{cta_index:05d}"
        admission_id = f"{cta_id}:admission"
        mma_id = f"{cta_id}:mma"
        store_id = f"{cta_id}:store"
        events.extend(
            (
                Event(
                    event_id=admission_id,
                    event_type="CTAAdmission_FullWave",
                    kernel_id="benchmark-gemm",
                    stream_id="stream-0",
                    duration=0.25,
                    dependencies=(launch_id,),
                    per_sm_demand={"cta": 1},
                    cta_id=cta_id,
                ),
                Event(
                    event_id=mma_id,
                    event_type="MMA_FullTile",
                    kernel_id="benchmark-gemm",
                    stream_id="stream-0",
                    duration=2.0,
                    dependencies=(admission_id,),
                    per_sm_demand={"tensor": 1},
                    cta_id=cta_id,
                ),
                Event(
                    event_id=store_id,
                    event_type="GlobalStore",
                    kernel_id="benchmark-gemm",
                    stream_id="stream-0",
                    duration=0.5,
                    dependencies=(mma_id,),
                    global_demand={"l2": 1},
                    cta_id=cta_id,
                ),
            )
        )
        store_ids.append(store_id)

    events.append(
        Event(
            event_id="benchmark-gemm:complete",
            event_type="KernelComplete",
            kernel_id="benchmark-gemm",
            stream_id="stream-0",
            duration=0.25,
            dependencies=(hbm_id, *store_ids),
            global_demand={"launch": 1},
        )
    )
    return BenchmarkInput(
        graph=EventGraph(tuple(events)),
        config=ResourceConfig(
            global_capacities={"hbm": 1, "l2": 132, "launch": 1},
            sm_count=sm_count,
            per_sm_capacities={"cta": 1, "tensor": 1},
        ),
    )


def run_benchmark_case(case: BenchmarkCase) -> BenchmarkResult:
    graph_started = perf_counter()
    benchmark_input = build_benchmark_input(
        cta_count=case.cta_count,
        sm_count=case.sm_count,
    )
    graph_build_seconds = perf_counter() - graph_started

    exact_result = None
    if case.run_exact:
        exact_result = solve_exact_schedule(
            benchmark_input.graph,
            benchmark_input.config,
        )

    schedule_started = perf_counter()
    simulation_result = schedule(
        benchmark_input.graph,
        benchmark_input.config,
    )
    schedule_seconds = perf_counter() - schedule_started

    report_started = perf_counter()
    report = build_report(
        simulation_result,
        exact_result=exact_result,
    )
    report_seconds = perf_counter() - report_started
    if report.feasible_makespan != simulation_result.makespan:
        raise AssertionError("report changed the feasible makespan")

    exact_optimum = (
        None if exact_result is None else exact_result.makespan
    )
    optimality_gap = None
    if exact_optimum is not None:
        if exact_optimum <= 0.0:
            raise AssertionError("exact benchmark optimum must be positive")
        optimality_gap = (
            simulation_result.makespan - exact_optimum
        ) / exact_optimum

    new_runtime_seconds = (
        graph_build_seconds + schedule_seconds + report_seconds
    )
    speedup = (
        None
        if case.old_runtime_seconds is None
        else case.old_runtime_seconds / new_runtime_seconds
    )
    feasibility_violation_count = _count_feasibility_violations(
        benchmark_input,
        simulation_result.by_id(),
    )
    determinism_mismatch_count = _determinism_mismatch_count(
        benchmark_input,
        simulation_result,
    )

    counters = simulation_result.counters
    return BenchmarkResult(
        event_count=len(benchmark_input.graph.events),
        edge_count=sum(
            len(event.dependencies)
            for event in benchmark_input.graph.events
        ),
        resource_count=(
            len(benchmark_input.config.global_capacities)
            + len(benchmark_input.config.per_sm_capacities)
        ),
        graph_build_seconds=graph_build_seconds,
        schedule_seconds=schedule_seconds,
        report_seconds=report_seconds,
        ready_queue_operations=counters.ready_queue_operations,
        blocked_ready_rechecks=counters.blocked_ready_rechecks,
        placement_checks=counters.placement_checks,
        lifetime_checks=counters.lifetime_checks,
        old_runtime_seconds=case.old_runtime_seconds,
        new_runtime_seconds=new_runtime_seconds,
        speedup=speedup,
        makespan=simulation_result.makespan,
        exact_optimum=exact_optimum,
        optimality_gap=optimality_gap,
        feasibility_violation_count=feasibility_violation_count,
        determinism_mismatch_count=determinism_mismatch_count,
    )


def _count_feasibility_violations(
    benchmark_input: BenchmarkInput,
    entries: Mapping,
) -> int:
    graph = benchmark_input.graph
    config = benchmark_input.config
    violations = len(set(graph.by_id).symmetric_difference(entries))
    global_deltas = {
        resource: {} for resource in config.global_capacities
    }
    per_sm_deltas: dict[tuple[int, str], dict[float, int]] = {}

    for event in graph.events:
        entry = entries.get(event.event_id)
        if entry is None:
            continue
        if entry.end_time - entry.start_time != float(event.duration):
            violations += 1
        for dependency in event.dependencies:
            dependency_entry = entries.get(dependency)
            if (
                dependency_entry is not None
                and entry.start_time < dependency_entry.end_time
            ):
                violations += 1

        if event.duration == 0.0:
            continue
        for resource, quantity in event.global_demand.items():
            if quantity > 0:
                _add_interval_delta(
                    global_deltas[resource],
                    entry.start_time,
                    entry.end_time,
                    quantity,
                )
        if any(event.per_sm_demand.values()):
            if entry.sm_id is None or not 0 <= entry.sm_id < config.sm_count:
                violations += 1
                continue
            for resource, quantity in event.per_sm_demand.items():
                if quantity > 0:
                    deltas = per_sm_deltas.setdefault(
                        (entry.sm_id, resource),
                        {},
                    )
                    _add_interval_delta(
                        deltas,
                        entry.start_time,
                        entry.end_time,
                        quantity,
                    )

    for resource, deltas in global_deltas.items():
        violations += _count_capacity_violations(
            deltas,
            config.global_capacities[resource],
        )
    for (_, resource), deltas in per_sm_deltas.items():
        violations += _count_capacity_violations(
            deltas,
            config.per_sm_capacities[resource],
        )
    return violations


def _add_interval_delta(
    deltas: dict[float, int],
    start_time: float,
    end_time: float,
    quantity: int,
) -> None:
    deltas[start_time] = deltas.get(start_time, 0) + quantity
    deltas[end_time] = deltas.get(end_time, 0) - quantity


def _count_capacity_violations(
    deltas: Mapping[float, int],
    capacity: int,
) -> int:
    in_use = 0
    violations = 0
    for time in sorted(deltas):
        in_use += deltas[time]
        if in_use < 0 or in_use > capacity:
            violations += 1
    if in_use != 0:
        violations += 1
    return violations


def _determinism_mismatch_count(
    benchmark_input: BenchmarkInput,
    baseline_result,
) -> int:
    reversed_graph = EventGraph(
        tuple(reversed(benchmark_input.graph.events))
    )
    repeated_result = schedule(reversed_graph, benchmark_input.config)
    baseline_signature = (
        baseline_result.entries,
        baseline_result.makespan,
        baseline_result.counters,
    )
    repeated_signature = (
        repeated_result.entries,
        repeated_result.makespan,
        repeated_result.counters,
    )
    return int(baseline_signature != repeated_signature)


def _require_positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def main() -> None:
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=FIELD_NAMES,
        lineterminator="\n",
    )
    writer.writeheader()
    for case in DEFAULT_CASES:
        result = run_benchmark_case(case)
        if result.feasibility_violation_count:
            raise AssertionError(
                f"feasibility violations for {result.event_count} Events: "
                f"{result.feasibility_violation_count}"
            )
        if result.determinism_mismatch_count:
            raise AssertionError(
                f"determinism mismatch for {result.event_count} Events"
            )
        writer.writerow(result.to_row())


if __name__ == "__main__":
    main()
