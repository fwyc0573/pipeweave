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

    # Chip-level memory event: total unique INPUT bytes (A + B matrices).
    # Output C excluded (L2 writeback, not on critical path).
    #
    # For the roofline lower bound, use the FASTEST possible path:
    # - If total input fits in L2 → use L2 bandwidth (faster, more ideal)
    # - Otherwise → use DRAM bandwidth
    # This ensures DES_time ≤ actual_time even when L2 caching helps.
    total_unique_input_bytes = (m * k + n * k) * element_bytes

    if total_unique_input_bytes <= hardware.l2_cache_size_bytes:
        dram_event_id = f"{kernel_id}:mem-total"
        events.append(
            _event(
                dram_event_id,
                "GlobalLoad_L2Hit",
                kernel_id,
                stream_id,
                "l2_bandwidth",
                calibration,
                quantity=total_unique_input_bytes,
                dependencies=(launch_id,),
                bytes=total_unique_input_bytes,
            )
        )
    else:
        dram_event_id = f"{kernel_id}:mem-total"
        events.append(
            _event(
                dram_event_id,
                "GlobalLoad_L2Miss",
                kernel_id,
                stream_id,
                "dram_bandwidth",
                calibration,
                quantity=total_unique_input_bytes,
                dependencies=(launch_id,),
                bytes=total_unique_input_bytes,
            )
        )

    stores: list[str] = []

    for cta_index in range(total_ctas):
        cta_id = f"{kernel_id}:cta-{cta_index}"
        is_tail = cta_index >= full_wave_ctas
        is_partial = is_edge_tile(cta_index, m_tiles, n_tiles, m, n, tile_m, tile_n)

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

        # 2. MMA (tile-aware) — the per-SM compute work
        #    MMA instructions: 2*M*N*K FLOPs / 256 FLOPs-per-instruction
        mma_type = "MMA_PartialTile" if is_partial else "MMA_FullTile"
        mma_instructions = ceil_div(2 * actual_m * actual_n * k, 256)
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

        # 3. Store — depends on MMA completing. Uses L2 writeback path
        #    (not the chip-level DRAM lane; output bytes already counted there).
        store_bytes = actual_m * actual_n * element_bytes
        store_id = f"{cta_id}:store"
        events.append(
            _event(
                store_id,
                "GlobalStore",
                kernel_id,
                stream_id,
                "l2_bandwidth",
                calibration,
                quantity=store_bytes,
                cta_id=cta_id,
                dependencies=(mma_id,),
                bytes=store_bytes,
            )
        )
        stores.append(store_id)

    # Kernel completion — depends on all stores AND the chip-level DRAM event.
    # Makespan = max(total_DRAM_time, total_compute_time + store_time)
    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            dependencies=tuple(stores) + (dram_event_id,),
            stream_ordered=True,
        )
    )
    return events


def _import_fa_schedulers():
    """Import FA scheduler functions from analytical_model package."""
    import sys
    from pathlib import Path

    am_dir = str(Path(__file__).resolve().parent.parent / "analytical_model")
    if am_dir not in sys.path:
        sys.path.insert(0, am_dir)
    from fa3_calculator import (  # noqa: E402
        FA3GetCTATileSize,
        calculate_fa3_ops,
        fa3_scheduler,
    )
    from fa2_calculator import (  # noqa: E402
        FA2DetermineCtaTileQ,
        NVIDIACTASchedulerRR,
        PrefillBinarySearchKVChunkSize,
        calculate_fa2_ops,
        create_fa2_cta_workload,
    )

    return {
        "fa3_scheduler": fa3_scheduler,
        "FA3GetCTATileSize": FA3GetCTATileSize,
        "calculate_fa3_ops": calculate_fa3_ops,
        "fa2_scheduler_cls": NVIDIACTASchedulerRR,
        "FA2DetermineCtaTileQ": FA2DetermineCtaTileQ,
        "PrefillBinarySearchKVChunkSize": PrefillBinarySearchKVChunkSize,
        "create_fa2_cta_workload": create_fa2_cta_workload,
        "calculate_fa2_ops": calculate_fa2_ops,
    }


def lower_flash_attention(
    kernel_id: str,
    *,
    batch_size: int,
    q_lengths: list[int],
    kv_lengths: list[int],
    num_qo_heads: int,
    num_kv_heads: int,
    head_dim: int,
    calibration: PrimitiveCalibration,
    hardware: HardwareConfig,
    attention_type: str = "fa3_ragged",
    causal: bool = True,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
) -> list[Event]:
    """Lower FlashAttention into task-level DES events.

    Design:
    - Reuses existing FA2/FA3 schedulers for task-to-SM assignment
    - Each task = one (request, q_tile, head) work unit
    - Per-SM: tasks execute sequentially (persistent kernel)
    - Compute and memory are modeled as parallel paths (roofline)
    - Makespan = max(total_DRAM_time, max_SM_compute_chain)

    Memory model:
    - Single chip-level DRAM event with total unique bytes (Q+K+V+O)
    - GQA-aware: K/V uses num_kv_heads, Q/O uses num_qo_heads

    Compute model:
    - Per-SM MMA compute chains (tensor_core lanes, per-SM rate)
    - MMA dominates XU by ~248x; XU safely omitted for roofline bound
    """

    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if len(q_lengths) != batch_size or len(kv_lengths) != batch_size:
        raise ValueError("q_lengths and kv_lengths must have length batch_size")
    if num_qo_heads <= 0 or num_kv_heads <= 0 or head_dim <= 0:
        raise ValueError("num_qo_heads, num_kv_heads, head_dim must be positive")
    _positive_integer("element_bytes", element_bytes)

    fa = _import_fa_schedulers()

    # Step 1: Determine tile sizes and run FA scheduler
    is_fa3 = "fa3" in attention_type
    layout = "paged" if "paged" in attention_type else "ragged"

    if is_fa3:
        cta_q, cta_kv = fa["FA3GetCTATileSize"](head_dim, head_dim, layout, causal)

        # Determine same_schedule_for_all_heads threshold
        total_q_tiles = sum(ceil_div(q, cta_q) for q in q_lengths)
        max_num_works_per_head = total_q_tiles * batch_size
        same_schedule = max_num_works_per_head > 8192

        sm_task_iterations = fa["fa3_scheduler"](
            batch_size=batch_size,
            q_lengths=q_lengths,
            kv_lengths=kv_lengths,
            num_sm=hardware.num_sms,
            cta_tile_q=cta_q,
            cta_tile_kv=cta_kv,
            causal=causal,
            num_qo_heads=num_qo_heads,
            same_schedule_for_all_heads=same_schedule,
        )

        head_multiplier = num_qo_heads if same_schedule else 1
    else:
        # FA2 path
        avg_q = sum(q_lengths) // batch_size
        gqa_group_size = num_qo_heads // num_kv_heads
        cta_q = fa["FA2DetermineCtaTileQ"](avg_q * gqa_group_size, head_dim)
        cta_kv = 64

        kv_chunk_size = fa["PrefillBinarySearchKVChunkSize"](
            max(kv_lengths), batch_size, hardware.num_sms, cta_q
        )

        cta_workload = fa["create_fa2_cta_workload"](
            q_lengths, kv_lengths, num_kv_heads, causal,
            cta_q, cta_kv, gqa_group_size, kv_chunk_size
        )

        scheduler_obj = fa["fa2_scheduler_cls"](hardware.num_sms, max_ctas_per_sm=2)
        sm_task_iterations = scheduler_obj.schedule_ctas(cta_workload)
        head_multiplier = 1

    # Step 2: Emit events
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

    # Chip-level DRAM event: total unique bytes (Q + K + V + O)
    total_kv_bytes = sum(kv_lengths) * num_kv_heads * head_dim * 2 * element_bytes
    total_q_bytes = sum(q_lengths) * num_qo_heads * head_dim * element_bytes
    total_o_bytes = sum(q_lengths) * num_qo_heads * head_dim * element_bytes
    total_unique_dram = total_kv_bytes + total_q_bytes + total_o_bytes

    dram_event_id = f"{kernel_id}:dram-total"
    events.append(
        _event(
            dram_event_id,
            "GlobalLoad_L2Miss",
            kernel_id,
            stream_id,
            "dram_bandwidth",
            calibration,
            quantity=total_unique_dram,
            dependencies=(launch_id,),
            bytes=total_unique_dram,
        )
    )

    # Per-SM task chains (compute only, on tensor_core lanes)
    # Build event lists per SM first, then interleave by task round.
    # Interleaving ensures the scheduler assigns different SMs' tasks to
    # different lanes in parallel (scheduler is greedy first-ready-in-order).
    sm_event_chains: list[list[Event]] = []
    sm_last_sync_ids: list[str] = []

    for sm_idx, task_iterations in enumerate(sm_task_iterations):
        if not task_iterations:
            continue

        chain: list[Event] = []
        prev_sync_id = launch_id

        for task_idx, iterations in enumerate(task_iterations):
            if iterations <= 0:
                continue

            effective_iterations = iterations * head_multiplier
            task_prefix = f"{kernel_id}:sm{sm_idx}:t{task_idx}"

            mma_ops = 4 * cta_q * cta_kv * head_dim * effective_iterations
            mma_instructions = ceil_div(mma_ops, 256)

            compute_id = f"{task_prefix}:compute"
            chain.append(
                _event(
                    compute_id,
                    "FA_Compute",
                    kernel_id,
                    stream_id,
                    "tensor_core",
                    calibration,
                    quantity=mma_instructions,
                    cta_id=task_prefix,
                    dependencies=(prev_sync_id,),
                    instruction_count=mma_instructions,
                )
            )

            sync_id = f"{task_prefix}:sync"
            chain.append(
                Event(
                    event_id=sync_id,
                    event_type="FA_TaskSync",
                    kernel_id=kernel_id,
                    stream_id=stream_id,
                    resource=None,
                    duration=0.0,
                    cta_id=task_prefix,
                    dependencies=(compute_id,),
                    stream_ordered=False,
                )
            )

            prev_sync_id = sync_id

        if chain:
            sm_event_chains.append(chain)
            sm_last_sync_ids.append(prev_sync_id)

    # Interleave: emit events round-robin across SMs (task0 from all SMs,
    # then task1 from all SMs, ...) so scheduler parallelizes across lanes.
    max_chain_len = max((len(c) for c in sm_event_chains), default=0)
    for round_idx in range(max_chain_len):
        for chain in sm_event_chains:
            if round_idx < len(chain):
                events.append(chain[round_idx])

    # Kernel completion: depends on all SM chains + DRAM event
    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            "launch",
            calibration,
            dependencies=tuple(sm_last_sync_ids) + (dram_event_id,),
            stream_ordered=True,
        )
    )
    return events
