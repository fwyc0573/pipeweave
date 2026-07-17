"""Mechanistic event-level simulation primitives for PipeWeave research."""

from .events import EVENT_TYPES, Event
from .operators import lower_gemm, lower_rmsnorm, lower_silu_and_mul
from .report import SimulationReport, build_report
from .resources import PrimitiveCalibration, ResourceConfig
from .scheduler import SimulationResult, schedule

__all__ = [
    "EVENT_TYPES",
    "Event",
    "PrimitiveCalibration",
    "ResourceConfig",
    "SimulationReport",
    "SimulationResult",
    "build_report",
    "lower_gemm",
    "lower_rmsnorm",
    "lower_silu_and_mul",
    "schedule",
]
