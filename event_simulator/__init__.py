"""Mechanistic event-level simulation primitives for PipeWeave research."""

from .cache import (
    CacheAccess,
    CacheBlock,
    CacheConfig,
    CacheResolution,
    CacheTransition,
    InitialCacheState,
    ResidentCacheBlock,
    resolve_cache,
)
from .comparison import BoundComparison, compare_des_bound
from .events import EVENT_TYPES, Event, EventGraph
from .exact_oracle import (
    ExactScheduleResult,
    IncompleteExactSearchError,
    solve_exact_schedule,
)
from .gemm_manifest import (
    GemmLaunchManifest,
    GemmReductionStep,
    GemmWorkItem,
    GemmWorker,
)
from .hardware_adapter import HardwareConfig, derive_calibration, derive_resource_config, load_hardware_config
from .operators import lower_flash_attention, lower_gemm, lower_gemm_v2, lower_rmsnorm, lower_silu_and_mul
from .structural import (
    compute_actual_tile_dims,
    compute_l2_hit_ratio,
    compute_tile_efficiency,
    compute_wave_split,
    is_edge_tile,
)
from .report import SimulationReport, build_report
from .safe_bound import SafeBound, SafeBoundEvaluator
from .resources import PrimitiveCalibration, ResourceConfig, ResourceLifetime
from .scheduler import (
    ScheduleEntry,
    SchedulerCounters,
    SchedulingNoProgressError,
    SimulationResult,
    schedule,
)

__all__ = [
    "EVENT_TYPES",
    "BoundComparison",
    "CacheAccess",
    "CacheBlock",
    "CacheConfig",
    "CacheResolution",
    "CacheTransition",
    "Event",
    "EventGraph",
    "ExactScheduleResult",
    "GemmLaunchManifest",
    "GemmReductionStep",
    "GemmWorkItem",
    "GemmWorker",
    "HardwareConfig",
    "IncompleteExactSearchError",
    "InitialCacheState",
    "PrimitiveCalibration",
    "ResourceConfig",
    "ResourceLifetime",
    "ResidentCacheBlock",
    "SafeBound",
    "SafeBoundEvaluator",
    "ScheduleEntry",
    "SchedulerCounters",
    "SchedulingNoProgressError",
    "SimulationReport",
    "SimulationResult",
    "build_report",
    "compare_des_bound",
    "compute_actual_tile_dims",
    "compute_l2_hit_ratio",
    "compute_tile_efficiency",
    "compute_wave_split",
    "derive_calibration",
    "derive_resource_config",
    "is_edge_tile",
    "load_hardware_config",
    "lower_flash_attention",
    "lower_gemm",
    "lower_gemm_v2",
    "lower_rmsnorm",
    "lower_silu_and_mul",
    "resolve_cache",
    "schedule",
    "solve_exact_schedule",
]
