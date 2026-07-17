import pytest

from event_simulator import Event, ResourceConfig, schedule


def test_event_dependencies_are_scheduled_in_order():
    events = [
        Event("load", "GlobalLoad", "kernel", "stream-0", "memory", 3.0),
        Event(
            "compute",
            "MMA",
            "kernel",
            "stream-1",
            "tensor",
            2.0,
            dependencies=("load",),
        ),
        Event(
            "store",
            "GlobalStore",
            "kernel",
            "stream-1",
            "memory",
            1.0,
            dependencies=("compute",),
        ),
    ]

    result = schedule(events, ResourceConfig({"memory": 1, "tensor": 1}))
    by_id = result.by_id()

    assert by_id["load"].start_time == 0.0
    assert by_id["compute"].start_time == by_id["load"].end_time == 3.0
    assert by_id["store"].start_time == by_id["compute"].end_time == 5.0
    assert result.makespan == 6.0


def test_resource_events_do_not_overlap_on_exclusive_resource():
    events = [
        Event("a", "GlobalLoad", "kernel-a", "stream-a", "memory", 4.0),
        Event("b", "GlobalLoad", "kernel-b", "stream-b", "memory", 2.0),
    ]

    result = schedule(events, ResourceConfig({"memory": 1}))
    first, second = result.events

    assert first.start_time == 0.0
    assert first.end_time <= second.start_time
    assert second.end_time == 6.0


def test_resource_capacity_allows_parallel_events_on_distinct_lanes():
    events = [
        Event("a", "MMA", "kernel-a", "stream-a", "tensor", 4.0),
        Event("b", "MMA", "kernel-b", "stream-b", "tensor", 2.0),
    ]

    result = schedule(events, ResourceConfig({"tensor": 2}))
    by_id = result.by_id()

    assert by_id["a"].start_time == 0.0
    assert by_id["b"].start_time == 0.0
    assert result.makespan == 4.0


def test_same_stream_events_keep_input_order_without_explicit_dependencies():
    events = [
        Event("first", "FMA", "kernel", "stream-0", "alu", 2.0),
        Event("second", "SFU", "kernel", "stream-0", "sfu", 1.0),
    ]

    result = schedule(events, ResourceConfig({"alu": 1, "sfu": 1}))
    by_id = result.by_id()

    assert by_id["first"].end_time == by_id["second"].start_time


@pytest.mark.parametrize(
    ("events", "resources", "message"),
    [
        (
            [Event("event", "MMA", "kernel", "stream", "missing", 1.0)],
            ResourceConfig({"tensor": 1}),
            "unknown resource",
        ),
        (
            [
                Event("duplicate", "MMA", "kernel", "stream-a", "tensor", 1.0),
                Event("duplicate", "MMA", "kernel", "stream-b", "tensor", 1.0),
            ],
            ResourceConfig({"tensor": 1}),
            "duplicate event id",
        ),
        (
            [
                Event(
                    "event",
                    "MMA",
                    "kernel",
                    "stream",
                    "tensor",
                    1.0,
                    dependencies=("missing",),
                )
            ],
            ResourceConfig({"tensor": 1}),
            "unknown dependency",
        ),
        (
            [
                Event(
                    "a",
                    "MMA",
                    "kernel",
                    "stream-a",
                    "tensor",
                    1.0,
                    dependencies=("b",),
                ),
                Event(
                    "b",
                    "MMA",
                    "kernel",
                    "stream-b",
                    "tensor",
                    1.0,
                    dependencies=("a",),
                ),
            ],
            ResourceConfig({"tensor": 1}),
            "dependency cycle",
        ),
    ],
)
def test_schedule_fails_fast_for_invalid_graphs(events, resources, message):
    with pytest.raises(ValueError, match=message):
        schedule(events, resources)


def test_event_rejects_negative_duration():
    with pytest.raises(ValueError, match="duration"):
        Event("event", "MMA", "kernel", "stream", "tensor", -1.0)


@pytest.mark.parametrize(
    "event_kwargs",
    [
        {"duration": "1.0"},
        {"duration": 1.0, "bytes": "1024"},
        {"duration": 1.0, "instruction_count": "4"},
    ],
)
def test_event_rejects_non_numeric_work_fields(event_kwargs):
    kwargs = {
        "event_id": "event",
        "event_type": "MMA",
        "kernel_id": "kernel",
        "stream_id": "stream",
        "resource": "tensor",
    }
    kwargs.update(event_kwargs)

    with pytest.raises(ValueError):
        Event(**kwargs)


def test_event_rejects_invalid_dependency_identifiers():
    with pytest.raises(ValueError, match="dependencies"):
        Event(
            "event",
            "MMA",
            "kernel",
            "stream",
            "tensor",
            1.0,
            dependencies=("valid", 7),
        )


def test_resource_config_rejects_non_positive_capacity():
    with pytest.raises(ValueError, match="capacity"):
        ResourceConfig({"tensor": 0})
