from __future__ import annotations

from math import ceil
from typing import Mapping

from .cache import CacheTransition, InitialCacheState
from .events import Event, EventGraph
from .gemm_manifest import GemmLaunchManifest
from .hardware_adapter import HardwareConfig
from .resources import PrimitiveCalibration, ResourceLifetime
from .structural import ceil_div


def _positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _event(
    event_id: str,
    event_type: str,
    kernel_id: str,
    stream_id: str,
    calibration: PrimitiveCalibration,
    *,
    quantity: int = 1,
    cta_id: str | None = None,
    dependencies: tuple[str, ...] = (),
    global_demand: Mapping[str, int] | None = None,
    per_sm_demand: Mapping[str, int] | None = None,
    eligible_sms: frozenset[int] | None = None,
    lifetime_id: str | None = None,
    bytes: int = 0,
    instruction_count: int = 0,
) -> Event:
    return Event(
        event_id=event_id,
        event_type=event_type,
        kernel_id=kernel_id,
        stream_id=stream_id,
        duration=calibration.duration(event_type, quantity),
        cta_id=cta_id,
        dependencies=dependencies,
        global_demand={} if global_demand is None else global_demand,
        per_sm_demand={} if per_sm_demand is None else per_sm_demand,
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
        bytes=bytes,
        instruction_count=instruction_count,
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
) -> EventGraph:
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
            calibration,
            global_demand={"launch": 1},
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
            mma_instructions = ceil(2 * actual_m * actual_n * k / 256)
            events.extend(
                [
                    _event(
                        admission_id,
                        "CTAAdmission",
                        kernel_id,
                        stream_id,
                        calibration,
                        cta_id=cta_id,
                        dependencies=(launch_id,),
                        per_sm_demand={"cta_slots": 1},
                    ),
                    _event(
                        load_id,
                        "GlobalLoad",
                        kernel_id,
                        stream_id,
                        calibration,
                        quantity=load_bytes,
                        cta_id=cta_id,
                        dependencies=(admission_id,),
                        global_demand={"hbm_bandwidth": 1},
                        bytes=load_bytes,
                    ),
                    _event(
                        mma_id,
                        "MMA",
                        kernel_id,
                        stream_id,
                        calibration,
                        quantity=mma_instructions,
                        cta_id=cta_id,
                        dependencies=(load_id,),
                        per_sm_demand={"tensor_core": 1},
                        instruction_count=mma_instructions,
                    ),
                    _event(
                        store_id,
                        "GlobalStore",
                        kernel_id,
                        stream_id,
                        calibration,
                        quantity=store_bytes,
                        cta_id=cta_id,
                        dependencies=(mma_id,),
                        global_demand={"l2_bandwidth": 1},
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
            calibration,
            dependencies=tuple(stores),
            global_demand={"launch": 1},
        )
    )
    return EventGraph(tuple(events))


def lower_rmsnorm(
    kernel_id: str,
    *,
    rows: int,
    hidden_size: int,
    calibration: PrimitiveCalibration,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
) -> EventGraph:
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
            calibration,
            global_demand={"launch": 1},
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
                    calibration,
                    quantity=row_bytes,
                    cta_id=cta_id,
                    dependencies=(launch_id,),
                    global_demand={"hbm_bandwidth": 1},
                    bytes=row_bytes,
                ),
                _event(
                    reduction_id,
                    "Reduction",
                    kernel_id,
                    stream_id,
                    calibration,
                    quantity=hidden_size,
                    cta_id=cta_id,
                    dependencies=(load_id,),
                    per_sm_demand={"alu": 1},
                    instruction_count=hidden_size,
                ),
                _event(
                    barrier_id,
                    "Barrier",
                    kernel_id,
                    stream_id,
                    calibration,
                    cta_id=cta_id,
                    dependencies=(reduction_id,),
                    per_sm_demand={"barrier": 1},
                ),
                _event(
                    normalize_id,
                    "FMA",
                    kernel_id,
                    stream_id,
                    calibration,
                    quantity=hidden_size,
                    cta_id=cta_id,
                    dependencies=(barrier_id,),
                    per_sm_demand={"alu": 1},
                    instruction_count=hidden_size,
                ),
                _event(
                    store_id,
                    "GlobalStore",
                    kernel_id,
                    stream_id,
                    calibration,
                    quantity=row_bytes,
                    cta_id=cta_id,
                    dependencies=(normalize_id,),
                    global_demand={"l2_bandwidth": 1},
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
            calibration,
            dependencies=tuple(stores),
            global_demand={"launch": 1},
        )
    )
    return EventGraph(tuple(events))


def lower_silu_and_mul(
    kernel_id: str,
    *,
    elements: int,
    calibration: PrimitiveCalibration,
    stream_id: str = "stream-0",
    element_bytes: int = 2,
) -> EventGraph:
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
    events = [
        _event(
            launch_id,
            "KernelLaunch",
            kernel_id,
            stream_id,
            calibration,
            global_demand={"launch": 1},
        ),
        _event(
            load_id,
            "GlobalLoad",
            kernel_id,
            stream_id,
            calibration,
            quantity=input_bytes,
            dependencies=(launch_id,),
            global_demand={"hbm_bandwidth": 1},
            bytes=input_bytes,
        ),
        _event(
            sfu_id,
            "SFU",
            kernel_id,
            stream_id,
            calibration,
            quantity=elements,
            dependencies=(load_id,),
            per_sm_demand={"sfu": 1},
            instruction_count=elements,
        ),
        _event(
            fma_id,
            "FMA",
            kernel_id,
            stream_id,
            calibration,
            quantity=elements,
            dependencies=(sfu_id,),
            per_sm_demand={"alu": 1},
            instruction_count=elements,
        ),
        _event(
            store_id,
            "GlobalStore",
            kernel_id,
            stream_id,
            calibration,
            quantity=output_bytes,
            dependencies=(fma_id,),
            global_demand={"l2_bandwidth": 1},
            bytes=output_bytes,
        ),
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            calibration,
            dependencies=(store_id,),
            global_demand={"launch": 1},
        ),
    ]
    return EventGraph(tuple(events))


def lower_gemm_v2(
    kernel_id: str,
    *,
    manifest: GemmLaunchManifest,
    calibration: PrimitiveCalibration,
    initial_cache_state: InitialCacheState,
    stream_id: str = "stream-0",
) -> EventGraph:
    """Lower one authoritative GEMM manifest into a normalized EventGraph."""

    resolution = manifest.resolve_cache(initial_cache_state)
    transitions_by_access: dict[int, list[tuple[int, CacheTransition]]] = {}
    flush_transitions: list[tuple[int, CacheTransition]] = []
    for transition_index, transition in enumerate(resolution.transitions):
        if transition.access_index is None:
            flush_transitions.append((transition_index, transition))
        else:
            transitions_by_access.setdefault(
                transition.access_index,
                [],
            ).append((transition_index, transition))

    launch_id = f"{kernel_id}:launch"
    events: list[Event] = [
        _event(
            launch_id,
            "KernelLaunch",
            kernel_id,
            stream_id,
            calibration,
            global_demand={"launch": 1},
        )
    ]
    lifetimes: list[ResourceLifetime] = []
    work_item_release: dict[str, str] = {}
    access_tail: dict[int, str] = {}
    terminal_ids: list[str] = []

    def append_accesses(
        access_indices: tuple[int, ...],
        kind: str,
        dependencies: tuple[str, ...],
        *,
        owner_id: str,
        lifetime_id: str | None,
    ) -> tuple[str, ...]:
        for access_index in access_indices:
            if manifest.cache_accesses[access_index].kind != kind:
                continue
            dependencies = _append_cache_transitions(
                events,
                transitions_by_access.get(access_index, ()),
                dependencies,
                kernel_id=kernel_id,
                stream_id=stream_id,
                calibration=calibration,
                owner_id=owner_id,
                lifetime_id=lifetime_id,
            )
        return dependencies

    for worker in manifest.workers:
        lifetime_id = f"{kernel_id}:lifetime:{worker.worker_id}"
        acquire_id = f"{kernel_id}:worker:{worker.worker_id}:acquire"
        release_id = f"{kernel_id}:worker:{worker.worker_id}:release"
        events.append(
            Event(
                event_id=acquire_id,
                event_type="CTAAdmission",
                kernel_id=kernel_id,
                stream_id=stream_id,
                duration=0.0,
                dependencies=(launch_id,),
                lifetime_id=lifetime_id,
                cta_id=worker.worker_id,
            )
        )
        dependencies = (acquire_id,)

        for work_item_id in worker.work_item_ids:
            work_item = manifest.work_item_by_id[work_item_id]
            dependencies = append_accesses(
                work_item.cache_access_indices,
                "read",
                dependencies,
                owner_id=work_item_id,
                lifetime_id=lifetime_id,
            )
            mma_instructions = ceil_div(
                work_item.physical_issued_work,
                256,
            )
            mma_id = f"{kernel_id}:work:{work_item_id}:mma"
            events.append(
                _event(
                    mma_id,
                    "MMA",
                    kernel_id,
                    stream_id,
                    calibration,
                    quantity=mma_instructions,
                    cta_id=work_item_id,
                    dependencies=dependencies,
                    per_sm_demand={"tensor_core": 1},
                    lifetime_id=lifetime_id,
                    instruction_count=mma_instructions,
                )
            )
            dependencies = append_accesses(
                work_item.cache_access_indices,
                "overwrite",
                (mma_id,),
                owner_id=work_item_id,
                lifetime_id=lifetime_id,
            )

        events.append(
            Event(
                event_id=release_id,
                event_type="CTAAdmission",
                kernel_id=kernel_id,
                stream_id=stream_id,
                duration=0.0,
                dependencies=dependencies,
                lifetime_id=lifetime_id,
                cta_id=worker.worker_id,
            )
        )
        lifetimes.append(
            ResourceLifetime(
                lifetime_id=lifetime_id,
                acquire_event_id=acquire_id,
                release_event_id=release_id,
                per_sm_reservation=worker.per_sm_reservation,
                eligible_sms=worker.eligible_sms,
            )
        )
        terminal_ids.append(release_id)
        for work_item_id in worker.work_item_ids:
            work_item_release[work_item_id] = release_id
            for access_index in manifest.work_item_by_id[
                work_item_id
            ].cache_access_indices:
                access_tail[access_index] = release_id

    accumulator_tail = {
        work_item.accumulator_id: work_item_release[work_item.work_item_id]
        for work_item in manifest.work_items
    }
    for step in manifest.reduction_steps:
        dependencies = tuple(
            sorted(
                {
                    accumulator_tail[accumulator_id]
                    for accumulator_id in step.input_accumulator_ids
                }
            )
        )
        dependencies = append_accesses(
            step.cache_access_indices,
            "read",
            dependencies,
            owner_id=step.reduction_id,
            lifetime_id=None,
        )
        reduction_id = f"{kernel_id}:reduction:{step.reduction_id}"
        events.append(
            _event(
                reduction_id,
                "Reduction",
                kernel_id,
                stream_id,
                calibration,
                quantity=step.physical_issued_work,
                cta_id=step.reduction_id,
                dependencies=dependencies,
                per_sm_demand={"alu": 1},
                instruction_count=step.physical_issued_work,
            )
        )
        dependencies = append_accesses(
            step.cache_access_indices,
            "overwrite",
            (reduction_id,),
            owner_id=step.reduction_id,
            lifetime_id=None,
        )
        reduction_tail = dependencies[0]
        accumulator_tail[step.output_accumulator_id] = reduction_tail
        terminal_ids.append(reduction_tail)
        for access_index in step.cache_access_indices:
            access_tail[access_index] = reduction_tail

    output_access_by_block = {
        access.block.identity: access_index
        for access_index, access in enumerate(manifest.cache_accesses)
        if access.is_output
    }
    flush_tail_ids: list[str] = []
    for transition_index, transition in flush_transitions:
        access_index = output_access_by_block[transition.block.identity]
        dependencies = _append_cache_transitions(
            events,
            ((transition_index, transition),),
            (access_tail[access_index],),
            kernel_id=kernel_id,
            stream_id=stream_id,
            calibration=calibration,
            owner_id=None,
            lifetime_id=None,
        )
        flush_tail_ids.append(dependencies[0])

    completion_dependencies = tuple(
        sorted(set(terminal_ids + flush_tail_ids))
    )
    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            calibration,
            dependencies=completion_dependencies,
            global_demand={"launch": 1},
        )
    )
    return EventGraph(tuple(events), tuple(lifetimes))


def _append_cache_transitions(
    events: list[Event],
    indexed_transitions,
    dependencies: tuple[str, ...],
    *,
    kernel_id: str,
    stream_id: str,
    calibration: PrimitiveCalibration,
    owner_id: str | None,
    lifetime_id: str | None,
) -> tuple[str, ...]:
    for transition_index, transition in indexed_transitions:
        for step_index, (event_type, byte_count) in enumerate(
            _cache_transition_steps(transition)
        ):
            event_id = (
                f"{kernel_id}:cache:{transition_index}:{step_index}:"
                f"{event_type.lower()}"
            )
            resource = (
                "hbm_bandwidth"
                if event_type.startswith("HBM")
                else "l2_bandwidth"
            )
            events.append(
                _event(
                    event_id,
                    event_type,
                    kernel_id,
                    stream_id,
                    calibration,
                    quantity=byte_count,
                    cta_id=owner_id,
                    dependencies=dependencies,
                    global_demand={resource: 1},
                    lifetime_id=lifetime_id,
                    bytes=byte_count,
                )
            )
            dependencies = (event_id,)
    return dependencies


def _cache_transition_steps(
    transition: CacheTransition,
) -> tuple[tuple[str, int], ...]:
    if transition.action == "read_hit":
        return (("L2Read", transition.l2_read_bytes),)
    if transition.action == "read_miss":
        return (
            ("HBMRead", transition.hbm_read_bytes),
            ("L2Write", transition.l2_write_bytes),
            ("L2Read", transition.l2_read_bytes),
        )
    if transition.action in {"overwrite_hit", "overwrite_miss"}:
        return (("L2Write", transition.l2_write_bytes),)
    if transition.action == "evict_clean":
        return ()
    return (
        ("L2Read", transition.l2_read_bytes),
        ("HBMWrite", transition.hbm_write_bytes),
    )

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
) -> EventGraph:
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
    - XU work is omitted by this experimental task-level model; the omission
      does not certify the composed schedule as a lower bound
    """

    _positive_integer("batch_size", batch_size)
    if len(q_lengths) != batch_size or len(kv_lengths) != batch_size:
        raise ValueError("q_lengths and kv_lengths must have length batch_size")
    for index, length in enumerate(q_lengths):
        _positive_integer(f"q_lengths[{index}]", length)
    for index, length in enumerate(kv_lengths):
        _positive_integer(f"kv_lengths[{index}]", length)
    _positive_integer("num_qo_heads", num_qo_heads)
    _positive_integer("num_kv_heads", num_kv_heads)
    _positive_integer("head_dim", head_dim)
    if num_qo_heads % num_kv_heads != 0:
        raise ValueError("num_qo_heads must be divisible by num_kv_heads")
    _positive_integer("element_bytes", element_bytes)
    supported_attention_types = {
        "fa2_paged",
        "fa2_ragged",
        "fa3_paged",
        "fa3_ragged",
    }
    if (
        not isinstance(attention_type, str)
        or attention_type not in supported_attention_types
    ):
        raise ValueError(f"unsupported attention_type: {attention_type}")

    fa = _import_fa_schedulers()

    # Step 1: Determine tile sizes and run FA scheduler
    is_fa3 = attention_type.startswith("fa3")
    layout = attention_type.split("_", maxsplit=1)[1]

    if is_fa3:
        cta_q, cta_kv = fa["FA3GetCTATileSize"](head_dim, head_dim, layout, causal)

        # Determine same_schedule_for_all_heads threshold
        max_num_works_per_head = ceil_div(sum(q_lengths), cta_q) + batch_size - 1
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
        gqa_group_size = num_qo_heads // num_kv_heads
        packed_qo_lengths = [length * gqa_group_size for length in q_lengths]
        avg_packed_qo_length = sum(packed_qo_lengths) // batch_size
        cta_q = fa["FA2DetermineCtaTileQ"](avg_packed_qo_length, head_dim)
        cta_kv = 64

        max_batch_size_if_split = 2 * hardware.num_sms // num_kv_heads
        page_size = 16 if layout == "paged" else 1
        _, kv_chunk_size = fa["PrefillBinarySearchKVChunkSize"](
            max_batch_size_if_split=max_batch_size_if_split,
            packed_qo_len_arr=packed_qo_lengths,
            kv_len_arr=list(kv_lengths),
            qo_chunk_size=cta_q,
            min_kv_chunk_size=max(128 // page_size, 1),
        )

        cta_workload = fa["create_fa2_cta_workload"](
            q_lengths=q_lengths,
            kv_lengths=kv_lengths,
            num_kv_heads=num_kv_heads,
            causal=causal,
            cta_tile_q=cta_q,
            cta_tile_kv=cta_kv,
            gqa_group_size=gqa_group_size,
            kv_chunk_size=kv_chunk_size,
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
            calibration,
            global_demand={"launch": 1},
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
            calibration,
            quantity=total_unique_dram,
            dependencies=(launch_id,),
            global_demand={"hbm_bandwidth": 1},
            bytes=total_unique_dram,
        )
    )

    # Per-SM task chains (compute only, on tensor_core lanes)
    sm_last_sync_ids: list[str] = []

    for sm_idx, task_iterations in enumerate(sm_task_iterations):
        if not task_iterations:
            continue

        prev_sync_id = launch_id

        for task_idx, iterations in enumerate(task_iterations):
            if iterations <= 0:
                continue

            effective_iterations = iterations * head_multiplier
            task_prefix = f"{kernel_id}:sm{sm_idx}:t{task_idx}"

            mma_ops = 4 * cta_q * cta_kv * head_dim * effective_iterations
            mma_instructions = ceil_div(mma_ops, 256)

            compute_id = f"{task_prefix}:compute"
            events.append(
                _event(
                    compute_id,
                    "FA_Compute",
                    kernel_id,
                    stream_id,
                    calibration,
                    quantity=mma_instructions,
                    cta_id=task_prefix,
                    dependencies=(prev_sync_id,),
                    per_sm_demand={"tensor_core": 1},
                    eligible_sms=frozenset({sm_idx}),
                    instruction_count=mma_instructions,
                )
            )

            sync_id = f"{task_prefix}:sync"
            events.append(
                _event(
                    sync_id,
                    "FA_TaskSync",
                    kernel_id,
                    stream_id,
                    calibration,
                    cta_id=task_prefix,
                    dependencies=(compute_id,),
                    eligible_sms=frozenset({sm_idx}),
                )
            )

            prev_sync_id = sync_id

        if prev_sync_id != launch_id:
            sm_last_sync_ids.append(prev_sync_id)

    # Kernel completion: depends on all SM chains + DRAM event
    events.append(
        _event(
            f"{kernel_id}:complete",
            "KernelComplete",
            kernel_id,
            stream_id,
            calibration,
            dependencies=tuple(sm_last_sync_ids) + (dram_event_id,),
            global_demand={"launch": 1},
        )
    )
    return EventGraph(tuple(events))
