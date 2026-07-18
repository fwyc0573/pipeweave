from __future__ import annotations

from math import ceil

from .events import Event
from .hardware_adapter import HardwareConfig
from .resources import PrimitiveCalibration
from .structural import (
    ceil_div,
    compute_actual_tile_dims,
    compute_l2_hit_ratio,
    compute_wave_split,
    is_edge_tile,
)


def _positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _event(
    event_id: str,
    event_type: str,
    kernel_id: str,
    stream_id: str,
    resource: str,
    calibration: PrimitiveCalibration,
    *,
    quantity: int = 1,
    cta_id: str | None = None,
    dependencies: tuple[str, ...] = (),
    bytes: int = 0,
    instruction_count: int = 0,
    stream_ordered: bool = False,
) -> Event:
    return Event(
        event_id=event_id,
        event_type=event_type,
        kernel_id=kernel_id,
        stream_id=stream_id,
        resource=resource,
        duration=calibration.duration(event_type, quantity),
        cta_id=cta_id,
        dependencies=dependencies,
        bytes=bytes,
        instruction_count=instruction_count,
        stream_ordered=stream_ordered,
    )


def lower_gemm(
    kernel_id: str,
    *,
    m: int,
    n: int,
    k: int,
    tile_m: int,
    tile_n: int,
    calibration: PrimitiveCalibration,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
) -> list[Event]:
    """Lower a tiled GEMM into per-CTA memory and tensor-core events."""

    for name, value in (
        ("m", m),
        ("n", n),
        ("k", k),
        ("tile_m", tile_m),
        ("tile_n", tile_n),
        ("element_bytes", element_bytes),
    ):
        _positive_integer(name, value)

    launch_id = f"{kernel_id}:launch"
    events = [
        _event(
            launch_id,
            "KernelLaunch",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            stream_ordered=True,
        )
    ]
    stores: list[str] = []
    cta_index = 0
    for row in range(ceil(m / tile_m)):
        actual_m = min(tile_m, m - row * tile_m)
        for column in range(ceil(n / tile_n)):
            actual_n = min(tile_n, n - column * tile_n)
            cta_id = f"{kernel_id}:cta-{cta_index}"
            admission_id = f"{cta_id}:admission"
            load_id = f"{cta_id}:load"
            mma_id = f"{cta_id}:mma"
            store_id = f"{cta_id}:store"
            load_bytes = (actual_m * k + actual_n * k) * element_bytes
            store_bytes = actual_m * actual_n * element_bytes
            mma_instructions = ceil(actual_m * actual_n * k / 256)
            events.extend(
                [
                    _event(
                        admission_id,
                        "CTAAdmission",
                        kernel_id,
                        stream_id,
                        "sm",
                        calibration,
                        cta_id=cta_id,
                        dependencies=(launch_id,),
                    ),
                    _event(
                        load_id,
                        "GlobalLoad",
                        kernel_id,
                        stream_id,
                        "global_memory",
                        calibration,
                        quantity=load_bytes,
                        cta_id=cta_id,
                        dependencies=(admission_id,),
                        bytes=load_bytes,
                    ),
                    _event(
                        mma_id,
                        "MMA",
                        kernel_id,
                        stream_id,
                        "tensor_core",
                        calibration,
                        quantity=mma_instructions,
                        cta_id=cta_id,
                        dependencies=(load_id,),
                        instruction_count=mma_instructions,
                    ),
                    _event(
                        store_id,
                        "GlobalStore",
                        kernel_id,
                        stream_id,
                        "global_memory",
                        calibration,
                        quantity=store_bytes,
                        cta_id=cta_id,
                        dependencies=(mma_id,),
                        bytes=store_bytes,
                    ),
                ]
            )
            stores.append(store_id)
            cta_index += 1

    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            dependencies=tuple(stores),
            stream_ordered=True,
        )
    )
    return events


def lower_rmsnorm(
    kernel_id: str,
    *,
    rows: int,
    hidden_size: int,
    calibration: PrimitiveCalibration,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
) -> list[Event]:
    """Lower RMSNorm into one explicit reduction/normalization chain per row."""

    for name, value in (
        ("rows", rows),
        ("hidden_size", hidden_size),
        ("element_bytes", element_bytes),
    ):
        _positive_integer(name, value)

    launch_id = f"{kernel_id}:launch"
    events = [
        _event(
            launch_id,
            "KernelLaunch",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            stream_ordered=True,
        )
    ]
    stores: list[str] = []
    for row in range(rows):
        cta_id = f"{kernel_id}:row-{row}"
        load_id = f"{cta_id}:load"
        reduction_id = f"{cta_id}:reduction"
        barrier_id = f"{cta_id}:barrier"
        normalize_id = f"{cta_id}:normalize"
        store_id = f"{cta_id}:store"
        row_bytes = hidden_size * element_bytes
        events.extend(
            [
                _event(
                    load_id,
                    "GlobalLoad",
                    kernel_id,
                    stream_id,
                    "global_memory",
                    calibration,
                    quantity=row_bytes,
                    cta_id=cta_id,
                    dependencies=(launch_id,),
                    bytes=row_bytes,
                ),
                _event(
                    reduction_id,
                    "Reduction",
                    kernel_id,
                    stream_id,
                    "alu",
                    calibration,
                    quantity=hidden_size,
                    cta_id=cta_id,
                    dependencies=(load_id,),
                    instruction_count=hidden_size,
                ),
                _event(
                    barrier_id,
                    "Barrier",
                    kernel_id,
                    stream_id,
                    "barrier",
                    calibration,
                    cta_id=cta_id,
                    dependencies=(reduction_id,),
                ),
                _event(
                    normalize_id,
                    "FMA",
                    kernel_id,
                    stream_id,
                    "alu",
                    calibration,
                    quantity=hidden_size,
                    cta_id=cta_id,
                    dependencies=(barrier_id,),
                    instruction_count=hidden_size,
                ),
                _event(
                    store_id,
                    "GlobalStore",
                    kernel_id,
                    stream_id,
                    "global_memory",
                    calibration,
                    quantity=row_bytes,
                    cta_id=cta_id,
                    dependencies=(normalize_id,),
                    bytes=row_bytes,
                ),
            ]
        )
        stores.append(store_id)

    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            dependencies=tuple(stores),
            stream_ordered=True,
        )
    )
    return events


def lower_silu_and_mul(
    kernel_id: str,
    *,
    elements: int,
    calibration: PrimitiveCalibration,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
) -> list[Event]:
    """Lower fused SiLU-and-Mul into a memory/SFU/FMA event chain."""

    _positive_integer("elements", elements)
    _positive_integer("element_bytes", element_bytes)
    launch_id = f"{kernel_id}:launch"
    load_id = f"{kernel_id}:load"
    sfu_id = f"{kernel_id}:sfu"
    fma_id = f"{kernel_id}:fma"
    store_id = f"{kernel_id}:store"
    input_bytes = elements * element_bytes * 2
    output_bytes = elements * element_bytes
    return [
        _event(
            launch_id,
            "KernelLaunch",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            stream_ordered=True,
        ),
        _event(
            load_id,
            "GlobalLoad",
            kernel_id,
            stream_id,
            "global_memory",
            calibration,
            quantity=input_bytes,
            dependencies=(launch_id,),
            bytes=input_bytes,
        ),
        _event(
            sfu_id,
            "SFU",
            kernel_id,
            stream_id,
            "sfu",
            calibration,
            quantity=elements,
            dependencies=(load_id,),
            instruction_count=elements,
        ),
        _event(
            fma_id,
            "FMA",
            kernel_id,
            stream_id,
            "alu",
            calibration,
            quantity=elements,
            dependencies=(sfu_id,),
            instruction_count=elements,
        ),
        _event(
            store_id,
            "GlobalStore",
            kernel_id,
            stream_id,
            "global_memory",
            calibration,
            quantity=output_bytes,
            dependencies=(fma_id,),
            bytes=output_bytes,
        ),
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            dependencies=(store_id,),
            stream_ordered=True,
        ),
    ]


def lower_gemm_v2(
    kernel_id: str,
    *,
    m: int,
    n: int,
    k: int,
    tile_m: int,
    tile_n: int,
    calibration: PrimitiveCalibration,
    hardware: HardwareConfig,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
    max_ctas_per_sm: int = 1,
    tile_k: int = 0,
) -> list[Event]:
    """Lower a tiled GEMM with structural decomposition.

    Compared to lower_gemm, this version models:
    - L2 cache hit/miss split for memory loads (using tile_K working set)
    - Full-wave vs tail-wave CTA admission
    - Full vs partial tile MMA efficiency
    - Pipeline overlap: load and compute run in parallel

    The resulting event DAG produces a tighter lower bound on execution
    time by capturing these structural effects explicitly.

    The tile_k parameter controls L2 working set estimation. When tile_k > 0,
    the live working set per CTA is (tile_m*tile_k + tile_n*tile_k) bytes
    (only one K-iteration's data is live at a time due to double-buffering).
    When tile_k == 0 (default), falls back to using full K dimension.
    """

    for name, value in (
        ("m", m),
        ("n", n),
        ("k", k),
        ("tile_m", tile_m),
        ("tile_n", tile_n),
        ("element_bytes", element_bytes),
        ("max_ctas_per_sm", max_ctas_per_sm),
    ):
        _positive_integer(name, value)
    if tile_k < 0:
        raise ValueError("tile_k must be non-negative")

    m_tiles = ceil_div(m, tile_m)
    n_tiles = ceil_div(n, tile_n)
    total_ctas = m_tiles * n_tiles

    # Structural analysis
    full_wave_ctas, tail_wave_ctas = compute_wave_split(
        total_ctas, hardware.num_sms, max_ctas_per_sm
    )

    # L2 hit ratio: use tile_K-based working set if available.
    # The "live" data at any moment is one K-iteration of A and B panels.
    # With double-buffering, this fits in L2 for typical tile sizes.
    effective_tile_k = tile_k if tile_k > 0 else k
    working_set_per_cta = (tile_m * effective_tile_k + tile_n * effective_tile_k) * element_bytes
    concurrent_full = min(total_ctas, hardware.num_sms * max_ctas_per_sm)
    concurrent_tail = tail_wave_ctas if tail_wave_ctas > 0 else concurrent_full
    l2_hit_full = compute_l2_hit_ratio(
        working_set_per_cta, hardware.l2_cache_size_bytes, concurrent_full
    )
    l2_hit_tail = compute_l2_hit_ratio(
        working_set_per_cta, hardware.l2_cache_size_bytes, concurrent_tail
    )

    # Emit events
    launch_id = f"{kernel_id}:launch"
    events: list[Event] = [
        _event(
            launch_id,
            "KernelLaunch",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            stream_ordered=True,
        )
    ]
    stores: list[str] = []

    for cta_index in range(total_ctas):
        cta_id = f"{kernel_id}:cta-{cta_index}"
        is_tail = cta_index >= full_wave_ctas
        is_partial = is_edge_tile(cta_index, m_tiles, n_tiles, m, n, tile_m, tile_n)
        l2_hit = l2_hit_tail if is_tail else l2_hit_full

        actual_m, actual_n = compute_actual_tile_dims(cta_index, m, n, tile_m, tile_n, n_tiles)

        # 1. CTA Admission (wave-aware)
        admission_type = "CTAAdmission_TailWave" if is_tail else "CTAAdmission_FullWave"
        admission_id = f"{cta_id}:admission"
        events.append(
            _event(
                admission_id,
                admission_type,
                kernel_id,
                stream_id,
                "sm",
                calibration,
                cta_id=cta_id,
                dependencies=(launch_id,),
            )
        )

        # 2. Memory loads — roofline memory model
        #    For a valid lower bound, the key insight is:
        #    - Per-CTA memory access is overlapped with compute (pipeline)
        #    - The chip-wide DRAM bottleneck is: total_unique_bytes / peak_BW
        #    - Per-CTA, we model the memory demand as this CTA's share of
        #      the total unique DRAM traffic, using the lower of:
        #      (a) full per-CTA load (pessimistic, no sharing)
        #      (b) chip-wide unique / total_CTAs (optimistic, perfect sharing)
        #    We use (b) for a valid lower bound — each CTA's DRAM event
        #    represents its proportional share of the chip-wide memory cost.
        #
        #    Total unique DRAM for entire GEMM = (M*K + N*K) * element_bytes
        #    Per CTA share = total_unique / total_ctas
        total_unique_bytes = (m * k + n * k) * element_bytes
        per_cta_dram_share = total_unique_bytes // total_ctas

        # L2 hit portion: any bytes beyond the DRAM share (served from cache)
        total_cta_load = (actual_m * k + actual_n * k) * element_bytes
        l2_hit_bytes = max(0, total_cta_load - per_cta_dram_share)
        l2_miss_bytes = min(per_cta_dram_share, total_cta_load)

        load_event_ids: list[str] = []

        if l2_hit_bytes > 0:
            l2_hit_id = f"{cta_id}:load-l2hit"
            events.append(
                _event(
                    l2_hit_id,
                    "GlobalLoad_L2Hit",
                    kernel_id,
                    stream_id,
                    "l2_bandwidth",
                    calibration,
                    quantity=l2_hit_bytes,
                    cta_id=cta_id,
                    dependencies=(admission_id,),
                    bytes=l2_hit_bytes,
                )
            )
            load_event_ids.append(l2_hit_id)

        if l2_miss_bytes > 0:
            l2_miss_id = f"{cta_id}:load-l2miss"
            events.append(
                _event(
                    l2_miss_id,
                    "GlobalLoad_L2Miss",
                    kernel_id,
                    stream_id,
                    "dram_bandwidth",
                    calibration,
                    quantity=l2_miss_bytes,
                    cta_id=cta_id,
                    dependencies=(admission_id,),
                    bytes=l2_miss_bytes,
                )
            )
            load_event_ids.append(l2_miss_id)

        # 3. MMA (tile-aware) — runs in PARALLEL with memory loads
        #    This models the K-iteration double-buffering pipeline overlap:
        #    in steady state, load[k+1] overlaps with compute[k].
        #    For the roofline lower bound, CTA time = max(load_time, compute_time).
        mma_type = "MMA_PartialTile" if is_partial else "MMA_FullTile"
        mma_instructions = ceil_div(actual_m * actual_n * k, 256)
        mma_id = f"{cta_id}:mma"
        events.append(
            _event(
                mma_id,
                mma_type,
                kernel_id,
                stream_id,
                "tensor_core",
                calibration,
                quantity=mma_instructions,
                cta_id=cta_id,
                dependencies=(admission_id,),
                instruction_count=mma_instructions,
            )
        )

        # 4. Store — depends on BOTH load and MMA completing (join point)
        #    This gives CTA duration = max(load_time, compute_time) + store_time
        store_bytes = actual_m * actual_n * element_bytes
        store_id = f"{cta_id}:store"
        store_deps = tuple(load_event_ids + [mma_id]) if load_event_ids else (mma_id,)
        events.append(
            _event(
                store_id,
                "GlobalStore",
                kernel_id,
                stream_id,
                "dram_bandwidth",
                calibration,
                quantity=store_bytes,
                cta_id=cta_id,
                dependencies=store_deps,
                bytes=store_bytes,
            )
        )
        stores.append(store_id)

    # Kernel completion
    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            dependencies=tuple(stores),
            stream_ordered=True,
        )
    )
    return events
