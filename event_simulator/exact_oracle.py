"""Complete exact scheduling oracle for the declared finite RCPSP domain."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from .events import Event, EventGraph
from .resources import ResourceConfig
from .scheduler import ScheduleEntry


class IncompleteExactSearchError(RuntimeError):
    """Raised when a caller-supplied permutation budget prevents completion."""


@dataclass(frozen=True)
class ExactScheduleResult:
    """Exact modeled makespan and one canonical optimal schedule witness."""

    makespan: float
    entries: tuple[ScheduleEntry, ...]


def solve_exact_schedule(
    graph: EventGraph,
    config: ResourceConfig,
    *,
    max_permutations: int | None = None,
) -> ExactScheduleResult:
    """Exhaustively solve the supported fixed-duration renewable-resource model."""

    if not graph.events:
        raise ValueError("exact oracle requires a non-empty EventGraph")
    if max_permutations is not None and (
        isinstance(max_permutations, bool)
        or not isinstance(max_permutations, int)
        or max_permutations <= 0
    ):
        raise ValueError("max_permutations must be a positive integer")

    config.validate_graph(graph)
    if graph.lifetimes:
        raise ValueError("exact oracle does not support resource lifetimes")
    if any(event.eligible_sms is not None for event in graph.events):
        raise ValueError("exact oracle does not support eligible-SM affinity")
    if config.sm_count > 1 and any(
        any(demand > 0 for demand in event.per_sm_demand.values())
        for event in graph.events
    ):
        raise ValueError(
            "exact oracle requires one SM for nonzero per-SM demand"
        )

    capacities = dict(config.global_capacities)
    if config.sm_count == 1:
        capacities.update(config.per_sm_capacities)
    demands = {
        event.event_id: _combined_demand(event, config.sm_count)
        for event in graph.events
    }

    best_makespan: float | None = None
    best_entries: tuple[ScheduleEntry, ...] | None = None
    permutation_count = 0
    for order in _precedence_feasible_orders(graph):
        permutation_count += 1
        if (
            max_permutations is not None
            and permutation_count > max_permutations
        ):
            raise IncompleteExactSearchError(
                "exact search incomplete: max_permutations exhausted"
            )
        entries = _serial_sgs(graph, order, capacities, demands)
        makespan = max(entry.end_time for entry in entries)
        if best_makespan is None or makespan < best_makespan:
            best_makespan = makespan
            best_entries = tuple(sorted(entries, key=lambda entry: entry.event_id))

    if best_makespan is None or best_entries is None:
        raise AssertionError("validated EventGraph has no topological order")
    return ExactScheduleResult(best_makespan, best_entries)


def _combined_demand(event: Event, sm_count: int) -> dict[str, int]:
    demand = dict(event.global_demand)
    if sm_count == 1:
        demand.update(event.per_sm_demand)
    return demand


def _precedence_feasible_orders(
    graph: EventGraph,
) -> Iterator[tuple[str, ...]]:
    ready = tuple(
        event.event_id
        for event in graph.events
        if graph.indegrees[event.event_id] == 0
    )
    yield from _extend_order(graph, (), graph.indegrees, ready)


def _extend_order(
    graph: EventGraph,
    prefix: tuple[str, ...],
    indegrees,
    ready: tuple[str, ...],
) -> Iterator[tuple[str, ...]]:
    if len(prefix) == len(graph.events):
        yield prefix
        return

    for event_id in ready:
        next_indegrees = dict(indegrees)
        next_ready = [candidate for candidate in ready if candidate != event_id]
        for successor in graph.successors[event_id]:
            next_indegrees[successor] -= 1
            if next_indegrees[successor] == 0:
                next_ready.append(successor)
        yield from _extend_order(
            graph,
            prefix + (event_id,),
            next_indegrees,
            tuple(sorted(next_ready)),
        )


def _serial_sgs(
    graph: EventGraph,
    order: tuple[str, ...],
    capacities: dict[str, int],
    demands: dict[str, dict[str, int]],
) -> tuple[ScheduleEntry, ...]:
    entries: list[ScheduleEntry] = []
    by_id: dict[str, ScheduleEntry] = {}
    for event_id in order:
        event = graph.by_id[event_id]
        dependency_end = max(
            (by_id[dependency].end_time for dependency in event.dependencies),
            default=0.0,
        )
        start_time = _earliest_feasible_start(
            event,
            dependency_end,
            entries,
            capacities,
            demands,
        )
        entry = ScheduleEntry(
            event_id=event_id,
            start_time=start_time,
            end_time=start_time + float(event.duration),
        )
        entries.append(entry)
        by_id[event_id] = entry
    return tuple(entries)


def _earliest_feasible_start(
    event: Event,
    dependency_end: float,
    entries: list[ScheduleEntry],
    capacities: dict[str, int],
    demands: dict[str, dict[str, int]],
) -> float:
    duration = float(event.duration)
    if duration == 0.0 or not any(demands[event.event_id].values()):
        return dependency_end

    candidates = {dependency_end}
    candidates.update(
        entry.end_time
        for entry in entries
        if entry.end_time >= dependency_end
    )
    for start_time in sorted(candidates):
        if _resource_feasible(
            event,
            start_time,
            duration,
            entries,
            capacities,
            demands,
        ):
            return start_time
    raise AssertionError("validated demand has no feasible insertion time")


def _resource_feasible(
    event: Event,
    start_time: float,
    duration: float,
    entries: list[ScheduleEntry],
    capacities: dict[str, int],
    demands: dict[str, dict[str, int]],
) -> bool:
    end_time = start_time + duration
    check_times = {start_time}
    check_times.update(
        entry.start_time
        for entry in entries
        if start_time < entry.start_time < end_time
    )
    event_demand = demands[event.event_id]
    for time in sorted(check_times):
        active_ids = (
            entry.event_id
            for entry in entries
            if entry.start_time <= time < entry.end_time
        )
        active_demands = tuple(demands[event_id] for event_id in active_ids)
        for resource, quantity in event_demand.items():
            if quantity + sum(
                demand.get(resource, 0) for demand in active_demands
            ) > capacities[resource]:
                return False
    return True
