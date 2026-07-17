from __future__ import annotations

from math import ceil

from .events import Event
from .resources import PrimitiveCalibration


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
