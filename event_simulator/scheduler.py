from __future__ import annotations

import heapq
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .events import Event, EventGraph
from .resources import ResourceConfig, ResourceLifetime


_Blocker = tuple[str, str]


class SchedulingNoProgressError(RuntimeError):
    """Raised when ready Events exist but no Event can run or complete."""


@dataclass(frozen=True)
class ScheduleEntry:
    """Immutable time and optional placement witness for one Event."""

    event_id: str
    start_time: float
    end_time: float
    sm_id: int | None = None


@dataclass(frozen=True)
class SchedulerCounters:
    """Operational scheduler counters kept separate from schedule evidence."""

    ready_queue_operations: int
    blocked_ready_rechecks: int
    placement_checks: int
    lifetime_checks: int


@dataclass(frozen=True)
class SimulationResult:
    """A deterministic feasible schedule for one normalized EventGraph."""

    graph: EventGraph
    entries: tuple[ScheduleEntry, ...]
    makespan: float
    counters: SchedulerCounters

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", tuple(self.entries))

    def by_id(self) -> Mapping[str, ScheduleEntry]:
        return MappingProxyType(
            {entry.event_id: entry for entry in self.entries}
        )


def schedule(
    graph: EventGraph,
    resources: ResourceConfig,
) -> SimulationResult:
    """Schedule a normalized graph with deterministic event-completion policy."""

    resources.validate_graph(graph)
    if not graph.events:
        return SimulationResult(
            graph=graph,
            entries=(),
            makespan=0.0,
            counters=SchedulerCounters(0, 0, 0, 0),
        )

    remaining_path = _remaining_path_durations(graph)
    lifetime_by_id = {
        lifetime.lifetime_id: lifetime for lifetime in graph.lifetimes
    }
    active_lifetime_sms: dict[str, int] = {}

    global_in_use = {
        resource: 0 for resource in resources.global_capacities
    }
    per_sm_in_use = [
        {resource: 0 for resource in resources.per_sm_capacities}
        for _ in range(resources.sm_count)
    ]
    per_sm_total_in_use = {
        resource: 0 for resource in resources.per_sm_capacities
    }

    counts = {
        "ready_queue_operations": 0,
        "blocked_ready_rechecks": 0,
        "placement_checks": 0,
        "lifetime_checks": 0,
    }
    indegrees = dict(graph.indegrees)
    ready: list[tuple[float, str]] = []
    attempts: dict[str, int] = {}
    completed: set[str] = set()
    entries: dict[str, ScheduleEntry] = {}
    running: list[tuple[float, str]] = []
    blocked_on: dict[str, frozenset[_Blocker]] = {}
    blocked_by_resource: dict[_Blocker, set[str]] = {}

    def push_ready(event_id: str) -> None:
        heapq.heappush(
            ready,
            (-remaining_path[event_id], event_id),
        )
        counts["ready_queue_operations"] += 1

    def block(event_id: str, blockers: frozenset[_Blocker]) -> None:
        if not blockers:
            raise AssertionError("infeasible Event has no resource blocker")
        blocked_on[event_id] = blockers
        for blocker in blockers:
            blocked_by_resource.setdefault(blocker, set()).add(event_id)

    def wake_blocked(released: set[_Blocker]) -> None:
        event_ids = {
            event_id
            for blocker in released
            for event_id in blocked_by_resource.get(blocker, ())
        }
        for event_id in sorted(event_ids):
            blockers = blocked_on.pop(event_id, None)
            if blockers is None:
                continue
            for blocker in blockers:
                waiters = blocked_by_resource[blocker]
                waiters.remove(event_id)
                if not waiters:
                    del blocked_by_resource[blocker]
            push_ready(event_id)

    def complete(event_id: str) -> None:
        event = graph.by_id[event_id]
        entry = entries[event_id]
        released: set[_Blocker] = set()
        if event.duration > 0.0:
            released.update(_release_transient_demand(
                event,
                entry.sm_id,
                lifetime_by_id,
                global_in_use,
                per_sm_in_use,
                per_sm_total_in_use,
            ))

        if event.lifetime_id is not None:
            lifetime = lifetime_by_id[event.lifetime_id]
            if event.event_id == lifetime.release_event_id:
                sm_id = active_lifetime_sms.pop(lifetime.lifetime_id)
                _subtract_per_sm_demand(
                    per_sm_in_use[sm_id],
                    per_sm_total_in_use,
                    lifetime.per_sm_reservation,
                )
                released.update(
                    _positive_resource_blockers(
                        "per_sm",
                        lifetime.per_sm_reservation,
                    )
                )

        completed.add(event_id)
        for successor in graph.successors[event_id]:
            indegrees[successor] -= 1
            if indegrees[successor] == 0:
                push_ready(successor)
        wake_blocked(released)

    for event in graph.events:
        if indegrees[event.event_id] == 0:
            push_ready(event.event_id)

    current_time = 0.0
    while len(completed) < len(graph.events):
        while ready:
            priority = heapq.heappop(ready)
            counts["ready_queue_operations"] += 1
            event_id = priority[1]
            if attempts.get(event_id, 0) > 0:
                counts["blocked_ready_rechecks"] += 1
            attempts[event_id] = attempts.get(event_id, 0) + 1

            event = graph.by_id[event_id]
            feasible, sm_id, blockers = _find_placement(
                event,
                resources,
                lifetime_by_id,
                active_lifetime_sms,
                global_in_use,
                per_sm_in_use,
                per_sm_total_in_use,
                counts,
            )
            if not feasible:
                block(event_id, blockers)
                continue

            if event.lifetime_id is not None:
                lifetime = lifetime_by_id[event.lifetime_id]
                if event.event_id == lifetime.acquire_event_id:
                    if sm_id is None:
                        raise AssertionError(
                            "lifetime acquire requires an SM placement"
                        )
                    active_lifetime_sms[lifetime.lifetime_id] = sm_id
                    _add_per_sm_demand(
                        per_sm_in_use[sm_id],
                        per_sm_total_in_use,
                        lifetime.per_sm_reservation,
                    )

            if event.duration > 0.0:
                _acquire_transient_demand(
                    event,
                    sm_id,
                    lifetime_by_id,
                    global_in_use,
                    per_sm_in_use,
                    per_sm_total_in_use,
                )

            end_time = current_time + float(event.duration)
            entries[event_id] = ScheduleEntry(
                event_id=event_id,
                start_time=current_time,
                end_time=end_time,
                sm_id=sm_id,
            )

            if event.duration == 0.0:
                complete(event_id)
            else:
                heapq.heappush(running, (end_time, event_id))

        if len(completed) == len(graph.events):
            break
        if not running:
            blocked = tuple(sorted(blocked_on))
            raise SchedulingNoProgressError(
                f"scheduler made no progress at time {current_time}: "
                f"blocked ready events {blocked}"
            )

        current_time = running[0][0]
        finishing = []
        while running and running[0][0] == current_time:
            _, event_id = heapq.heappop(running)
            finishing.append(event_id)
        for event_id in sorted(finishing):
            complete(event_id)

    ordered_entries = tuple(
        entries[event.event_id] for event in graph.events
    )
    makespan = max(entry.end_time for entry in ordered_entries)
    return SimulationResult(
        graph=graph,
        entries=ordered_entries,
        makespan=makespan,
        counters=SchedulerCounters(**counts),
    )


def _remaining_path_durations(graph: EventGraph) -> dict[str, float]:
    indegrees = dict(graph.indegrees)
    ready = [
        event.event_id
        for event in graph.events
        if indegrees[event.event_id] == 0
    ]
    heapq.heapify(ready)
    order = []
    while ready:
        event_id = heapq.heappop(ready)
        order.append(event_id)
        for successor in graph.successors[event_id]:
            indegrees[successor] -= 1
            if indegrees[successor] == 0:
                heapq.heappush(ready, successor)

    remaining: dict[str, float] = {}
    for event_id in reversed(order):
        remaining[event_id] = float(graph.by_id[event_id].duration) + max(
            (remaining[successor] for successor in graph.successors[event_id]),
            default=0.0,
        )
    return remaining


def _find_placement(
    event: Event,
    resources: ResourceConfig,
    lifetime_by_id: Mapping[str, ResourceLifetime],
    active_lifetime_sms: Mapping[str, int],
    global_in_use: Mapping[str, int],
    per_sm_in_use: list[dict[str, int]],
    per_sm_total_in_use: Mapping[str, int],
    counts: dict[str, int],
) -> tuple[bool, int | None, frozenset[_Blocker]]:
    if event.duration > 0.0:
        global_blockers = _capacity_blockers(
            "global",
            global_in_use,
            event.global_demand,
            resources.global_capacities,
        )
        if global_blockers:
            return False, None, global_blockers

    if event.lifetime_id is not None:
        counts["lifetime_checks"] += 1
        lifetime = lifetime_by_id[event.lifetime_id]
        transient = lifetime.transient_per_sm_demand(event.per_sm_demand)
        if event.event_id == lifetime.acquire_event_id:
            candidates = _candidate_sms(lifetime.eligible_sms, resources.sm_count)
            combined = _combined_demand(
                lifetime.per_sm_reservation,
                transient if event.duration > 0.0 else {},
            )
            aggregate_blockers = _aggregate_per_sm_blockers(
                per_sm_total_in_use,
                combined,
                resources,
            )
            if aggregate_blockers:
                return False, None, aggregate_blockers
            for sm_id in candidates:
                counts["placement_checks"] += 1
                if _demand_fits(
                    per_sm_in_use[sm_id],
                    combined,
                    resources.per_sm_capacities,
                ):
                    return True, sm_id, frozenset()
            return (
                False,
                None,
                _positive_resource_blockers("per_sm", combined),
            )

        sm_id = active_lifetime_sms.get(lifetime.lifetime_id)
        if sm_id is None:
            raise AssertionError("lifetime member reached before acquire")
        counts["placement_checks"] += 1
        blockers = _capacity_blockers(
            "per_sm",
            per_sm_in_use[sm_id],
            transient,
            resources.per_sm_capacities,
        )
        if event.duration == 0.0 or not blockers:
            return True, sm_id, frozenset()
        return False, None, blockers

    requires_sm = (
        event.eligible_sms is not None
        or _has_positive_demand(event.per_sm_demand)
    )
    if not requires_sm:
        return True, None, frozenset()

    candidates = _candidate_sms(event.eligible_sms, resources.sm_count)
    demand = event.per_sm_demand if event.duration > 0.0 else {}
    aggregate_blockers = _aggregate_per_sm_blockers(
        per_sm_total_in_use,
        demand,
        resources,
    )
    if aggregate_blockers:
        return False, None, aggregate_blockers
    for sm_id in candidates:
        counts["placement_checks"] += 1
        if _demand_fits(
            per_sm_in_use[sm_id],
            demand,
            resources.per_sm_capacities,
        ):
            return True, sm_id, frozenset()
    return (
        False,
        None,
        _positive_resource_blockers("per_sm", demand),
    )


def _candidate_sms(
    eligible_sms: frozenset[int] | None,
    sm_count: int,
) -> tuple[int, ...]:
    if eligible_sms is None:
        return tuple(range(sm_count))
    return tuple(sorted(eligible_sms))


def _combined_demand(
    first: Mapping[str, int],
    second: Mapping[str, int],
) -> dict[str, int]:
    combined = dict(first)
    for resource, quantity in second.items():
        combined[resource] = combined.get(resource, 0) + quantity
    return combined


def _demand_fits(
    in_use: Mapping[str, int],
    demand: Mapping[str, int],
    capacities: Mapping[str, int],
) -> bool:
    return all(
        in_use[resource] + quantity <= capacities[resource]
        for resource, quantity in demand.items()
    )


def _capacity_blockers(
    scope: str,
    in_use: Mapping[str, int],
    demand: Mapping[str, int],
    capacities: Mapping[str, int],
) -> frozenset[_Blocker]:
    return frozenset(
        (scope, resource)
        for resource, quantity in demand.items()
        if in_use[resource] + quantity > capacities[resource]
    )


def _aggregate_per_sm_blockers(
    in_use: Mapping[str, int],
    demand: Mapping[str, int],
    resources: ResourceConfig,
) -> frozenset[_Blocker]:
    return frozenset(
        ("per_sm", resource)
        for resource, quantity in demand.items()
        if (
        in_use[resource] + quantity
        > resources.sm_count * resources.per_sm_capacities[resource]
        )
    )


def _positive_resource_blockers(
    scope: str,
    demand: Mapping[str, int],
) -> frozenset[_Blocker]:
    return frozenset(
        (scope, resource)
        for resource, quantity in demand.items()
        if quantity > 0
    )


def _has_positive_demand(demand: Mapping[str, int]) -> bool:
    return any(demand.values())


def _add_demand(
    in_use: dict[str, int],
    demand: Mapping[str, int],
) -> None:
    for resource, quantity in demand.items():
        in_use[resource] += quantity


def _subtract_demand(
    in_use: dict[str, int],
    demand: Mapping[str, int],
) -> None:
    for resource, quantity in demand.items():
        in_use[resource] -= quantity


def _add_per_sm_demand(
    sm_in_use: dict[str, int],
    total_in_use: dict[str, int],
    demand: Mapping[str, int],
) -> None:
    _add_demand(sm_in_use, demand)
    _add_demand(total_in_use, demand)


def _subtract_per_sm_demand(
    sm_in_use: dict[str, int],
    total_in_use: dict[str, int],
    demand: Mapping[str, int],
) -> None:
    _subtract_demand(sm_in_use, demand)
    _subtract_demand(total_in_use, demand)


def _acquire_transient_demand(
    event: Event,
    sm_id: int | None,
    lifetime_by_id: Mapping[str, ResourceLifetime],
    global_in_use: dict[str, int],
    per_sm_in_use: list[dict[str, int]],
    per_sm_total_in_use: dict[str, int],
) -> None:
    _add_demand(global_in_use, event.global_demand)
    transient = event.per_sm_demand
    if event.lifetime_id is not None:
        transient = lifetime_by_id[
            event.lifetime_id
        ].transient_per_sm_demand(
            event.per_sm_demand,
        )
    if _has_positive_demand(transient):
        if sm_id is None:
            raise AssertionError("per-SM demand requires an SM placement")
        _add_per_sm_demand(
            per_sm_in_use[sm_id],
            per_sm_total_in_use,
            transient,
        )


def _release_transient_demand(
    event: Event,
    sm_id: int | None,
    lifetime_by_id: Mapping[str, ResourceLifetime],
    global_in_use: dict[str, int],
    per_sm_in_use: list[dict[str, int]],
    per_sm_total_in_use: dict[str, int],
) -> set[_Blocker]:
    _subtract_demand(global_in_use, event.global_demand)
    released = set(
        _positive_resource_blockers("global", event.global_demand)
    )
    transient = event.per_sm_demand
    if event.lifetime_id is not None:
        transient = lifetime_by_id[
            event.lifetime_id
        ].transient_per_sm_demand(
            event.per_sm_demand,
        )
    if _has_positive_demand(transient):
        if sm_id is None:
            raise AssertionError("per-SM demand requires an SM placement")
        _subtract_per_sm_demand(
            per_sm_in_use[sm_id],
            per_sm_total_in_use,
            transient,
        )
        released.update(
            _positive_resource_blockers("per_sm", transient)
        )
    return released
