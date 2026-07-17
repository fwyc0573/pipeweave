from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .scheduler import SimulationResult


@dataclass(frozen=True)
class SimulationReport:
    makespan: float
    critical_path: float
    critical_path_event_ids: tuple[str, ...]
    kernel_durations: dict[str, float]
    resource_busy_time: dict[str, float]
    timeline: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "makespan": self.makespan,
            "critical_path": self.critical_path,
            "critical_path_event_ids": list(self.critical_path_event_ids),
            "kernel_durations": dict(self.kernel_durations),
            "resource_busy_time": dict(self.resource_busy_time),
            "timeline": [dict(event) for event in self.timeline],
        }


def build_report(result: SimulationResult) -> SimulationReport:
    kernel_bounds: dict[str, list[float]] = {}
    resource_busy_time: dict[str, float] = {}
    timeline = []
    for event in result.events:
        bounds = kernel_bounds.setdefault(
            event.kernel_id, [event.start_time, event.end_time]
        )
        bounds[0] = min(bounds[0], event.start_time)
        bounds[1] = max(bounds[1], event.end_time)
        if event.resource is not None:
            resource_busy_time[event.resource] = (
                resource_busy_time.get(event.resource, 0.0) + event.duration
            )
        timeline.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "kernel_id": event.kernel_id,
                "stream_id": event.stream_id,
                "cta_id": event.cta_id,
                "resource": event.resource,
                "bytes": event.bytes,
                "instruction_count": event.instruction_count,
                "dependencies": list(event.dependencies),
                "duration": event.duration,
                "start_time": event.start_time,
                "end_time": event.end_time,
            }
        )

    kernel_durations = {
        kernel_id: end - start for kernel_id, (start, end) in kernel_bounds.items()
    }
    by_id = result.by_id()
    critical_path: list[str] = []
    if result.events:
        current = max(result.events, key=lambda event: event.end_time)
        while True:
            critical_path.append(current.event_id)
            if not current.dependencies:
                break
            current = max(
                (by_id[dependency] for dependency in current.dependencies),
                key=lambda event: event.end_time,
            )
        critical_path.reverse()
    return SimulationReport(
        makespan=result.makespan,
        critical_path=result.makespan,
        critical_path_event_ids=tuple(critical_path),
        kernel_durations=kernel_durations,
        resource_busy_time=resource_busy_time,
        timeline=tuple(timeline),
    )
