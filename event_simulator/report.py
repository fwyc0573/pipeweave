from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Mapping

from .safe_bound import dependency_critical_path
from .scheduler import SimulationResult

if TYPE_CHECKING:
    from .exact_oracle import ExactScheduleResult
    from .safe_bound import SafeBound


@dataclass(frozen=True)
class SimulationReport:
    feasible_makespan: float
    dependency_critical_path: float
    dependency_critical_path_event_ids: tuple[str, ...]
    exact_optimum: float | None
    safe_bound_value: float | None
    kernel_durations: Mapping[str, float]
    resource_busy_time: Mapping[str, float]
    timeline: tuple[Mapping[str, Any], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "kernel_durations",
            MappingProxyType(dict(sorted(self.kernel_durations.items()))),
        )
        object.__setattr__(
            self,
            "resource_busy_time",
            MappingProxyType(dict(sorted(self.resource_busy_time.items()))),
        )
        object.__setattr__(
            self,
            "timeline",
            tuple(
                MappingProxyType(dict(item))
                for item in self.timeline
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        timeline = []
        for item in self.timeline:
            serialized = dict(item)
            serialized["dependencies"] = list(item["dependencies"])
            serialized["global_demand"] = dict(item["global_demand"])
            serialized["per_sm_demand"] = dict(item["per_sm_demand"])
            eligible_sms = item["eligible_sms"]
            serialized["eligible_sms"] = (
                None if eligible_sms is None else list(eligible_sms)
            )
            timeline.append(serialized)
        return {
            "feasible_makespan": self.feasible_makespan,
            "dependency_critical_path": self.dependency_critical_path,
            "dependency_critical_path_event_ids": list(
                self.dependency_critical_path_event_ids
            ),
            "exact_optimum": self.exact_optimum,
            "safe_bound_value": self.safe_bound_value,
            "kernel_durations": dict(self.kernel_durations),
            "resource_busy_time": dict(self.resource_busy_time),
            "timeline": timeline,
        }


def build_report(
    result: SimulationResult,
    *,
    exact_result: ExactScheduleResult | None = None,
    safe_bound: SafeBound | None = None,
) -> SimulationReport:
    entries = result.by_id()
    kernel_bounds: dict[str, list[float]] = {}
    resource_busy_time: dict[str, float] = {}
    timeline = []

    lifetime_by_id = {
        lifetime.lifetime_id: lifetime
        for lifetime in result.graph.lifetimes
    }
    for entry in result.entries:
        event = result.graph.by_id[entry.event_id]
        bounds = kernel_bounds.setdefault(
            event.kernel_id,
            [entry.start_time, entry.end_time],
        )
        bounds[0] = min(bounds[0], entry.start_time)
        bounds[1] = max(bounds[1], entry.end_time)

        for resource, quantity in event.global_demand.items():
            _add_resource_time(
                resource_busy_time,
                resource,
                float(event.duration) * quantity,
            )

        reservation = {}
        if event.lifetime_id is not None:
            reservation = lifetime_by_id[
                event.lifetime_id
            ].per_sm_reservation
        for resource, quantity in event.per_sm_demand.items():
            if resource in reservation:
                continue
            _add_resource_time(
                resource_busy_time,
                resource,
                float(event.duration) * quantity,
            )

        timeline.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "kernel_id": event.kernel_id,
                "stream_id": event.stream_id,
                "cta_id": event.cta_id,
                "bytes": event.bytes,
                "instruction_count": event.instruction_count,
                "dependencies": event.dependencies,
                "global_demand": MappingProxyType(
                    dict(event.global_demand)
                ),
                "per_sm_demand": MappingProxyType(
                    dict(event.per_sm_demand)
                ),
                "eligible_sms": (
                    None
                    if event.eligible_sms is None
                    else tuple(sorted(event.eligible_sms))
                ),
                "lifetime_id": event.lifetime_id,
                "duration": float(event.duration),
                "start_time": entry.start_time,
                "end_time": entry.end_time,
                "sm_id": entry.sm_id,
            }
        )

    for lifetime in result.graph.lifetimes:
        acquire = entries[lifetime.acquire_event_id]
        release = entries[lifetime.release_event_id]
        hold_duration = release.end_time - acquire.start_time
        for resource, quantity in lifetime.per_sm_reservation.items():
            _add_resource_time(
                resource_busy_time,
                resource,
                hold_duration * quantity,
            )

    kernel_durations = {
        kernel_id: end - start
        for kernel_id, (start, end) in kernel_bounds.items()
    }
    critical_path, critical_path_ids = dependency_critical_path(
        result.graph
    )
    return SimulationReport(
        feasible_makespan=result.makespan,
        dependency_critical_path=critical_path,
        dependency_critical_path_event_ids=critical_path_ids,
        exact_optimum=(
            None if exact_result is None else exact_result.makespan
        ),
        safe_bound_value=(
            None if safe_bound is None else safe_bound.bound
        ),
        kernel_durations=kernel_durations,
        resource_busy_time=resource_busy_time,
        timeline=tuple(timeline),
    )


def _add_resource_time(
    totals: dict[str, float],
    resource: str,
    quantity: float,
) -> None:
    totals[resource] = totals.get(resource, 0.0) + quantity
