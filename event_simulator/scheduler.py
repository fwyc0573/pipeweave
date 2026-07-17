from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Iterable

from .events import Event
from .resources import ResourceConfig


@dataclass(frozen=True)
class SimulationResult:
    events: tuple[Event, ...]
    makespan: float

    def by_id(self) -> dict[str, Event]:
        return {event.event_id: event for event in self.events}


def _validated_dependencies(events: tuple[Event, ...]) -> dict[str, tuple[str, ...]]:
    event_ids = [event.event_id for event in events]
    if len(set(event_ids)) != len(event_ids):
        raise ValueError("duplicate event id")

    known_ids = set(event_ids)
    dependencies: dict[str, list[str]] = {
        event.event_id: list(event.dependencies) for event in events
    }
    last_stream_event: dict[str, str] = {}
    for event in events:
        unknown = set(event.dependencies) - known_ids
        if unknown:
            raise ValueError(
                f"unknown dependency for {event.event_id}: {sorted(unknown)}"
            )
        if event.stream_ordered:
            previous = last_stream_event.get(event.stream_id)
            if previous is not None and previous not in dependencies[event.event_id]:
                dependencies[event.event_id].append(previous)
            last_stream_event[event.stream_id] = event.event_id
    return {event_id: tuple(value) for event_id, value in dependencies.items()}


def schedule(
    events: Iterable[Event], resources: ResourceConfig
) -> SimulationResult:
    """Schedule events using deterministic dependency-aware list scheduling."""

    ordered_events = tuple(events)
    dependencies = _validated_dependencies(ordered_events)
    for event in ordered_events:
        if event.resource is not None and event.resource not in resources.capacities:
            raise ValueError(
                f"unknown resource for {event.event_id}: {event.resource}"
            )

    lanes = {
        resource: [0.0] * capacity
        for resource, capacity in resources.capacities.items()
    }
    lane_owners: dict[str, list[str | None]] = {
        resource: [None] * capacity
        for resource, capacity in resources.capacities.items()
    }
    remaining = {event.event_id: event for event in ordered_events}
    completed: dict[str, Event] = {}
    scheduled: list[Event] = []

    while remaining:
        ready = next(
            (
                event
                for event in ordered_events
                if event.event_id in remaining
                and all(dep in completed for dep in dependencies[event.event_id])
            ),
            None,
        )
        if ready is None:
            unresolved = sorted(remaining)
            raise ValueError(f"dependency cycle detected among events: {unresolved}")

        effective_dependencies = list(dependencies[ready.event_id])
        dependency_end = max(
            (completed[dep].end_time for dep in effective_dependencies),
            default=0.0,
        )
        if ready.resource is None:
            start_time = dependency_end
        else:
            resource_lanes = lanes[ready.resource]
            lane_index = min(
                range(len(resource_lanes)), key=lambda index: (resource_lanes[index], index)
            )
            resource_predecessor = lane_owners[ready.resource][lane_index]
            if (
                resource_predecessor is not None
                and resource_predecessor not in effective_dependencies
            ):
                effective_dependencies.append(resource_predecessor)
            start_time = max(dependency_end, resource_lanes[lane_index])
            resource_lanes[lane_index] = start_time + ready.duration
            lane_owners[ready.resource][lane_index] = ready.event_id

        completed_event = replace(
            ready,
            dependencies=tuple(effective_dependencies),
            start_time=start_time,
            end_time=start_time + ready.duration,
        )
        completed[ready.event_id] = completed_event
        scheduled.append(completed_event)
        del remaining[ready.event_id]

    makespan = max((event.end_time for event in scheduled), default=0.0)
    return SimulationResult(tuple(scheduled), makespan)
