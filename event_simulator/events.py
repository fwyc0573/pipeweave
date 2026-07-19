from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import isfinite
from numbers import Real
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from .resources import ResourceLifetime


EVENT_TYPES = frozenset(
    {
        # Kernel lifecycle
        "KernelLaunch",
        "KernelComplete",
        # CTA scheduling (wave-aware)
        "CTAAdmission",
        "CTAAdmission_FullWave",
        "CTAAdmission_TailWave",
        # Global memory (cache-aware)
        "GlobalLoad",
        "GlobalLoad_L2Hit",
        "GlobalLoad_L2Miss",
        "GlobalStore",
        # Shared memory
        "SharedLoad",
        "SharedStore",
        # Compute (utilization-aware)
        "MMA",
        "MMA_FullTile",
        "MMA_PartialTile",
        "MMA_PipelineDrain",
        "FMA",
        "SFU",
        "Reduction",
        # Synchronization
        "Barrier",
        # FlashAttention task-level events
        "FA_Compute",
        "FA_Memory",
        "FA_TaskSync",
    }
)


@dataclass(frozen=True)
class Event:
    """An immutable, unscheduled unit of simulated GPU work.

    Durations use the same time unit as the supplied primitive calibration.
    Microseconds are recommended for human-readable reports.
    """

    event_id: str
    event_type: str
    kernel_id: str
    stream_id: str
    duration: float
    dependencies: tuple[str, ...] = ()
    global_demand: Mapping[str, int] = field(default_factory=dict)
    per_sm_demand: Mapping[str, int] = field(default_factory=dict)
    eligible_sms: frozenset[int] | None = None
    lifetime_id: str | None = None
    cta_id: str | None = None
    bytes: int = 0
    instruction_count: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("event_id", self.event_id),
            ("event_type", self.event_type),
            ("kernel_id", self.kernel_id),
            ("stream_id", self.stream_id),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"unknown event type: {self.event_type}")
        if (
            isinstance(self.duration, bool)
            or not isinstance(self.duration, Real)
            or not isfinite(self.duration)
            or self.duration < 0.0
        ):
            raise ValueError("duration must be finite and non-negative")
        if (
            isinstance(self.bytes, bool)
            or not isinstance(self.bytes, int)
            or self.bytes < 0
        ):
            raise ValueError("bytes must be non-negative")
        if (
            isinstance(self.instruction_count, bool)
            or not isinstance(self.instruction_count, int)
            or self.instruction_count < 0
        ):
            raise ValueError("instruction_count must be non-negative")
        if isinstance(self.dependencies, (str, bytes)):
            raise ValueError("dependencies must be a sequence of identifiers")
        dependencies = tuple(self.dependencies)
        if any(
            not isinstance(dependency, str) or not dependency
            for dependency in dependencies
        ):
            raise ValueError("dependencies must contain non-empty strings")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError("dependencies must not contain duplicates")
        if self.event_id in dependencies:
            raise ValueError("event cannot depend on itself")
        object.__setattr__(self, "dependencies", tuple(sorted(dependencies)))
        for name, value in (("cta_id", self.cta_id), ("lifetime_id", self.lifetime_id)):
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError(f"{name} must be None or a non-empty string")

        global_demand = _freeze_demand(self.global_demand)
        per_sm_demand = _freeze_demand(self.per_sm_demand)
        object.__setattr__(self, "global_demand", global_demand)
        object.__setattr__(self, "per_sm_demand", per_sm_demand)

        if self.eligible_sms is not None:
            eligible_sms = frozenset(self.eligible_sms)
            if not eligible_sms:
                raise ValueError("eligible_sms must not be empty")
            if any(
                isinstance(sm_id, bool)
                or not isinstance(sm_id, int)
                or sm_id < 0
                for sm_id in eligible_sms
            ):
                raise ValueError("eligible SM ids must be non-negative integers")
            object.__setattr__(self, "eligible_sms", eligible_sms)


def _freeze_demand(demand: Mapping[str, int]) -> Mapping[str, int]:
    normalized = dict(demand)
    for resource, quantity in normalized.items():
        if not isinstance(resource, str) or not resource:
            raise ValueError("resource names must be non-empty strings")
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity < 0
        ):
            raise ValueError("demand must be a non-negative integer")
    return MappingProxyType(dict(sorted(normalized.items())))


@dataclass(frozen=True)
class EventGraph:
    """A canonical, validated Event DAG and its resource lifetimes."""

    events: tuple[Event, ...]
    lifetimes: tuple[ResourceLifetime, ...] = ()
    by_id: Mapping[str, Event] = field(init=False, repr=False)
    successors: Mapping[str, tuple[str, ...]] = field(init=False, repr=False)
    indegrees: Mapping[str, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        events = tuple(self.events)
        event_ids = tuple(event.event_id for event in events)
        if len(set(event_ids)) != len(event_ids):
            raise ValueError("duplicate event id")

        events = tuple(sorted(events, key=lambda event: event.event_id))
        by_id = {event.event_id: event for event in events}
        successors = {event_id: [] for event_id in by_id}
        indegrees = {}
        for event in events:
            for dependency in event.dependencies:
                if dependency not in by_id:
                    raise ValueError(
                        f"unknown dependency for {event.event_id}: {dependency}"
                    )
                successors[dependency].append(event.event_id)
            indegrees[event.event_id] = len(event.dependencies)

        frozen_successors = {
            event_id: tuple(sorted(event_successors))
            for event_id, event_successors in successors.items()
        }
        if not _is_acyclic(frozen_successors, indegrees):
            raise ValueError("dependency cycle")

        lifetimes = tuple(sorted(self.lifetimes, key=lambda item: item.lifetime_id))
        lifetime_ids = tuple(lifetime.lifetime_id for lifetime in lifetimes)
        if len(set(lifetime_ids)) != len(lifetime_ids):
            raise ValueError("duplicate lifetime id")
        lifetime_by_id = {lifetime.lifetime_id: lifetime for lifetime in lifetimes}

        for event in events:
            if (
                event.lifetime_id is not None
                and event.lifetime_id not in lifetime_by_id
            ):
                raise ValueError(
                    f"unknown lifetime for {event.event_id}: {event.lifetime_id}"
                )

        reserved_resources = {
            resource
            for lifetime in lifetimes
            for resource in lifetime.per_sm_reservation
        }
        for lifetime in lifetimes:
            members = tuple(
                event for event in events if event.lifetime_id == lifetime.lifetime_id
            )
            member_ids = {event.event_id for event in members}
            if (
                lifetime.acquire_event_id not in member_ids
                or lifetime.release_event_id not in member_ids
            ):
                raise ValueError("lifetime endpoints must be members")

            for member in members:
                if member.eligible_sms is not None:
                    raise ValueError("lifetime member cannot declare eligible_sms")
                if (
                    member.event_id != lifetime.acquire_event_id
                    and not _is_reachable(
                        lifetime.acquire_event_id,
                        member.event_id,
                        frozen_successors,
                    )
                ) or (
                    member.event_id != lifetime.release_event_id
                    and not _is_reachable(
                        member.event_id,
                        lifetime.release_event_id,
                        frozen_successors,
                    )
                ):
                    raise ValueError(
                        "lifetime members must be ordered between lifetime endpoints"
                    )

                for resource, demand in member.per_sm_demand.items():
                    if resource not in reserved_resources or demand == 0:
                        continue
                    if resource not in lifetime.per_sm_reservation:
                        raise ValueError(
                            "lifetime member cannot demand another reserved "
                            "occupancy resource"
                        )
                    if demand > lifetime.per_sm_reservation[resource]:
                        raise ValueError(
                            "lifetime member demand exceeds its lifetime reservation"
                        )

        object.__setattr__(self, "events", events)
        object.__setattr__(self, "lifetimes", lifetimes)
        object.__setattr__(self, "by_id", MappingProxyType(by_id))
        object.__setattr__(
            self, "successors", MappingProxyType(frozen_successors)
        )
        object.__setattr__(self, "indegrees", MappingProxyType(indegrees))


def _is_acyclic(
    successors: Mapping[str, tuple[str, ...]], indegrees: Mapping[str, int]
) -> bool:
    remaining = dict(indegrees)
    ready = deque(
        event_id for event_id, degree in remaining.items() if degree == 0
    )
    visited = 0
    while ready:
        event_id = ready.popleft()
        visited += 1
        for successor in successors[event_id]:
            remaining[successor] -= 1
            if remaining[successor] == 0:
                ready.append(successor)
    return visited == len(remaining)


def _is_reachable(
    source: str,
    target: str,
    successors: Mapping[str, tuple[str, ...]],
) -> bool:
    pending = [source]
    visited = set()
    while pending:
        event_id = pending.pop()
        if event_id == target:
            return True
        if event_id in visited:
            continue
        visited.add(event_id)
        pending.extend(successors[event_id])
    return False
