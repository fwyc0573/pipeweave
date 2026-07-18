from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


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
    """A dependency-bearing unit of simulated GPU work.

    Durations use the same time unit as the supplied primitive calibration.
    Microseconds are recommended for human-readable reports.
    """

    event_id: str
    event_type: str
    kernel_id: str
    stream_id: str
    resource: str | None
    duration: float
    cta_id: str | None = None
    dependencies: tuple[str, ...] = ()
    bytes: int = 0
    instruction_count: int = 0
    stream_ordered: bool = True
    start_time: float | None = None
    end_time: float | None = None

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
        if self.resource is not None and (
            not isinstance(self.resource, str) or not self.resource
        ):
            raise ValueError("resource must be None or a non-empty string")
        if (
            isinstance(self.duration, bool)
            or not isinstance(self.duration, Real)
            or not isfinite(self.duration)
            or self.duration < 0.0
        ):
            raise ValueError("duration must be finite and non-negative")
        if isinstance(self.bytes, bool) or not isinstance(self.bytes, int) or self.bytes < 0:
            raise ValueError("bytes must be non-negative")
        if (
            isinstance(self.instruction_count, bool)
            or not isinstance(self.instruction_count, int)
            or self.instruction_count < 0
        ):
            raise ValueError("instruction_count must be non-negative")
        if any(
            not isinstance(dependency, str) or not dependency
            for dependency in self.dependencies
        ):
            raise ValueError("dependencies must contain non-empty strings")
        if len(set(self.dependencies)) != len(self.dependencies):
            raise ValueError("dependencies must not contain duplicates")
        if self.event_id in self.dependencies:
            raise ValueError("event cannot depend on itself")
        if (self.start_time is None) != (self.end_time is None):
            raise ValueError("start_time and end_time must be set together")
        if self.start_time is not None:
            if (
                isinstance(self.start_time, bool)
                or isinstance(self.end_time, bool)
                or not isinstance(self.start_time, Real)
                or not isinstance(self.end_time, Real)
                or not isfinite(self.start_time)
                or not isfinite(self.end_time)
                or self.start_time < 0.0
                or self.end_time < self.start_time
            ):
                raise ValueError("scheduled event times are invalid")
