from dataclasses import FrozenInstanceError, fields

import pytest

import event_simulator


Event = event_simulator.Event
EventGraph = getattr(event_simulator, "EventGraph", None)
ResourceLifetime = getattr(event_simulator, "ResourceLifetime", None)


def test_shared_kernel_types_are_public():
    assert EventGraph is not None
    assert ResourceLifetime is not None


def _event(
    event_id: str = "event",
    *,
    event_type: str = "MMA",
    kernel_id: str = "kernel-0",
    stream_id: str = "stream-0",
    duration: float = 1.0,
    dependencies=(),
    global_demand: dict[str, int] | None = None,
    lifetime_id: str | None = None,
    cta_id: str | None = None,
    eligible_sms: frozenset[int] | None = None,
    per_sm_demand: dict[str, int] | None = None,
    bytes: int = 0,
    instruction_count: int = 0,
) -> Event:
    return Event(
        event_id=event_id,
        event_type=event_type,
        kernel_id=kernel_id,
        stream_id=stream_id,
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
        lifetime_id=lifetime_id,
        cta_id=cta_id,
        eligible_sms=eligible_sms,
        per_sm_demand=per_sm_demand or {},
        bytes=bytes,
        instruction_count=instruction_count,
    )


def _lifetime(
    lifetime_id: str = "lifetime-0",
    *,
    acquire_event_id: str = "acquire",
    release_event_id: str = "release",
    reservation: dict[str, int] | None = None,
    eligible_sms: frozenset[int] | None = None,
) -> ResourceLifetime:
    return ResourceLifetime(
        lifetime_id=lifetime_id,
        acquire_event_id=acquire_event_id,
        release_event_id=release_event_id,
        per_sm_reservation=reservation or {"cta_slots": 1},
        eligible_sms=eligible_sms,
    )


def test_event_is_an_unscheduled_immutable_specification():
    event = _event(
        "event-0",
        eligible_sms=frozenset({3, 1}),
        per_sm_demand={"tensor_core": 1},
    )

    field_names = {field.name for field in fields(Event)}

    assert "resource" not in field_names
    assert "stream_ordered" not in field_names
    assert "start_time" not in field_names
    assert "end_time" not in field_names
    assert event.eligible_sms == frozenset({1, 3})
    assert dict(event.per_sm_demand) == {"tensor_core": 1}
    with pytest.raises(TypeError):
        event.per_sm_demand["tensor_core"] = 2
    with pytest.raises(FrozenInstanceError):
        event.duration = 2.0


@pytest.mark.parametrize(
    ("event_kwargs", "message"),
    [
        ({"event_id": ""}, "event_id must be a non-empty string"),
        ({"event_type": "unknown"}, "unknown event type"),
        ({"kernel_id": ""}, "kernel_id must be a non-empty string"),
        ({"stream_id": ""}, "stream_id must be a non-empty string"),
        ({"duration": True}, "duration must be finite and non-negative"),
        ({"duration": float("nan")}, "duration must be finite and non-negative"),
        ({"duration": float("inf")}, "duration must be finite and non-negative"),
        ({"duration": -1.0}, "duration must be finite and non-negative"),
        ({"bytes": True}, "bytes must be non-negative"),
        ({"bytes": -1}, "bytes must be non-negative"),
        (
            {"instruction_count": True},
            "instruction_count must be non-negative",
        ),
        (
            {"instruction_count": -1},
            "instruction_count must be non-negative",
        ),
        ({"cta_id": ""}, "cta_id must be None or a non-empty string"),
        (
            {"lifetime_id": ""},
            "lifetime_id must be None or a non-empty string",
        ),
    ],
)
def test_event_rejects_invalid_scalar_values(event_kwargs, message):
    with pytest.raises(ValueError, match=message):
        _event(**event_kwargs)


@pytest.mark.parametrize(
    "dependencies",
    [
        ("",),
        ("duplicate", "duplicate"),
        ("event",),
        ("valid", 7),
    ],
)
def test_event_rejects_invalid_dependency_values(dependencies):
    with pytest.raises(ValueError, match="depend"):
        _event(dependencies=dependencies)


def test_event_demand_mappings_are_detached_from_mutable_input():
    global_demand = {"hbm": 1}
    per_sm_demand = {"tensor_core": 1}

    event = _event(
        global_demand=global_demand,
        per_sm_demand=per_sm_demand,
    )
    global_demand["hbm"] = 2
    per_sm_demand["tensor_core"] = 2

    assert dict(event.global_demand) == {"hbm": 1}
    assert dict(event.per_sm_demand) == {"tensor_core": 1}


def test_event_graph_canonicalizes_order_and_owns_graph_maps():
    events = (
        _event("c", dependencies=("a", "b")),
        _event("a"),
        _event("b", dependencies=("a",)),
    )

    graph = EventGraph(events)

    assert tuple(event.event_id for event in graph.events) == ("a", "b", "c")
    assert tuple(graph.by_id) == ("a", "b", "c")
    assert graph.by_id["b"].dependencies == ("a",)
    assert dict(graph.successors) == {
        "a": ("b", "c"),
        "b": ("c",),
        "c": (),
    }
    assert dict(graph.indegrees) == {"a": 0, "b": 1, "c": 2}
    with pytest.raises(TypeError):
        graph.by_id["d"] = _event("d")
    with pytest.raises(TypeError):
        graph.successors["a"] = ()
    with pytest.raises(TypeError):
        graph.indegrees["a"] = 1


def test_event_graph_is_invariant_to_input_permutation():
    events = (
        _event("root"),
        _event("left", dependencies=("root",)),
        _event("right", dependencies=("root",)),
        _event("join", dependencies=("left", "right")),
    )

    first = EventGraph(events)
    second = EventGraph(tuple(reversed(events)))

    assert first.events == second.events
    assert first.successors == second.successors
    assert first.indegrees == second.indegrees


def test_event_dependencies_are_canonical_and_detached_from_mutable_input():
    dependencies = ["right", "left"]

    event = _event("join", dependencies=dependencies)
    dependencies.append("later")

    assert event.dependencies == ("left", "right")


def test_event_rejects_a_string_dependency_container():
    with pytest.raises(ValueError, match="dependencies must be a sequence"):
        _event("event", dependencies="ab")


def test_same_stream_does_not_create_implicit_dependencies():
    graph = EventGraph((_event("second"), _event("first")))

    assert graph.by_id["first"].dependencies == ()
    assert graph.by_id["second"].dependencies == ()
    assert dict(graph.indegrees) == {"first": 0, "second": 0}


def test_event_graph_accepts_an_empty_graph_without_inventing_semantics():
    graph = EventGraph(())

    assert graph.events == ()
    assert graph.lifetimes == ()
    assert dict(graph.by_id) == {}
    assert dict(graph.successors) == {}
    assert dict(graph.indegrees) == {}


def test_event_graph_accepts_zero_duration_with_nonzero_demand():
    event = _event(
        "zero",
        duration=0.0,
        global_demand={"launch": 1},
        per_sm_demand={"cta_slots": 1},
    )

    assert EventGraph((event,)).by_id["zero"] == event


@pytest.mark.parametrize(
    ("event_specs", "message"),
    [
        (
            ({"event_id": "duplicate"}, {"event_id": "duplicate"}),
            "duplicate event id",
        ),
        (
            ({"event_id": "event", "dependencies": ("missing",)},),
            "unknown dependency",
        ),
        (
            (
                {"event_id": "a", "dependencies": ("c",)},
                {"event_id": "b", "dependencies": ("a",)},
                {"event_id": "c", "dependencies": ("b",)},
            ),
            "dependency cycle",
        ),
    ],
)
def test_event_graph_rejects_invalid_graphs(event_specs, message):
    events = tuple(_event(**event_spec) for event_spec in event_specs)

    with pytest.raises(ValueError, match=message):
        EventGraph(events)


def test_event_graph_accepts_a_well_ordered_lifetime():
    lifetime = _lifetime(eligible_sms=frozenset({0, 2}))
    graph = EventGraph(
        (
            _event("release", dependencies=("work",), lifetime_id="lifetime-0"),
            _event(
                "work",
                dependencies=("acquire",),
                lifetime_id="lifetime-0",
                per_sm_demand={"cta_slots": 1, "tensor_core": 1},
            ),
            _event("acquire", lifetime_id="lifetime-0"),
        ),
        lifetimes=(lifetime,),
    )

    assert graph.lifetimes == (lifetime,)
    assert graph.by_id["work"].lifetime_id == "lifetime-0"


def test_event_graph_canonicalizes_lifetimes_by_id():
    lifetimes = (
        _lifetime(
            "z-life",
            acquire_event_id="z-acquire",
            release_event_id="z-release",
            reservation={"registers": 1},
        ),
        _lifetime(
            "a-life",
            acquire_event_id="a-acquire",
            release_event_id="a-release",
            reservation={"cta_slots": 1},
        ),
    )
    events = (
        _event("z-acquire", lifetime_id="z-life"),
        _event(
            "z-release",
            dependencies=("z-acquire",),
            lifetime_id="z-life",
        ),
        _event("a-acquire", lifetime_id="a-life"),
        _event(
            "a-release",
            dependencies=("a-acquire",),
            lifetime_id="a-life",
        ),
    )

    graph = EventGraph(events, lifetimes=lifetimes)

    assert tuple(item.lifetime_id for item in graph.lifetimes) == (
        "a-life",
        "z-life",
    )


@pytest.mark.parametrize(
    ("event_specs", "lifetime_specs", "message"),
    [
        (
            ({"event_id": "event", "lifetime_id": "missing"},),
            (),
            "unknown lifetime",
        ),
        (
            (
                {"event_id": "acquire"},
                {"event_id": "release", "dependencies": ("acquire",)},
            ),
            ({},),
            "lifetime endpoints must be members",
        ),
        (
            (
                {"event_id": "acquire", "lifetime_id": "lifetime-0"},
                {"event_id": "member", "lifetime_id": "lifetime-0"},
                {
                    "event_id": "release",
                    "dependencies": ("acquire",),
                    "lifetime_id": "lifetime-0",
                },
            ),
            ({},),
            "ordered between lifetime endpoints",
        ),
        (
            (
                {"event_id": "acquire", "lifetime_id": "lifetime-0"},
                {
                    "event_id": "member",
                    "dependencies": ("acquire",),
                    "lifetime_id": "lifetime-0",
                    "eligible_sms": frozenset({0}),
                },
                {
                    "event_id": "release",
                    "dependencies": ("member",),
                    "lifetime_id": "lifetime-0",
                },
            ),
            ({},),
            "lifetime member cannot declare eligible_sms",
        ),
        (
            (
                {"event_id": "acquire", "lifetime_id": "lifetime-0"},
                {
                    "event_id": "member",
                    "dependencies": ("acquire",),
                    "lifetime_id": "lifetime-0",
                    "per_sm_demand": {"cta_slots": 2},
                },
                {
                    "event_id": "release",
                    "dependencies": ("member",),
                    "lifetime_id": "lifetime-0",
                },
            ),
            ({"reservation": {"cta_slots": 1}},),
            "exceeds its lifetime reservation",
        ),
    ],
)
def test_event_graph_rejects_invalid_lifetime_membership(
    event_specs, lifetime_specs, message
):
    events = tuple(_event(**event_spec) for event_spec in event_specs)
    lifetimes = tuple(
        _lifetime(**lifetime_spec) for lifetime_spec in lifetime_specs
    )

    with pytest.raises(ValueError, match=message):
        EventGraph(events, lifetimes=lifetimes)


def test_event_graph_rejects_duplicate_lifetime_ids():
    events = (
        _event("acquire", lifetime_id="lifetime-0"),
        _event(
            "release",
            dependencies=("acquire",),
            lifetime_id="lifetime-0",
        ),
    )

    with pytest.raises(ValueError, match="duplicate lifetime id"):
        EventGraph(events, lifetimes=(_lifetime(), _lifetime()))


def test_event_graph_excludes_cross_lifetime_hold_and_wait():
    lifetimes = (
        _lifetime(
            "register-life",
            acquire_event_id="register-acquire",
            release_event_id="register-release",
            reservation={"registers": 1},
        ),
        _lifetime(
            "shared-life",
            acquire_event_id="shared-acquire",
            release_event_id="shared-release",
            reservation={"shared_memory": 1},
        ),
    )
    events = (
        _event("register-acquire", lifetime_id="register-life"),
        _event(
            "register-work",
            dependencies=("register-acquire",),
            lifetime_id="register-life",
            per_sm_demand={"registers": 1, "shared_memory": 1},
        ),
        _event(
            "register-release",
            dependencies=("register-work",),
            lifetime_id="register-life",
        ),
        _event("shared-acquire", lifetime_id="shared-life"),
        _event(
            "shared-work",
            dependencies=("shared-acquire",),
            lifetime_id="shared-life",
            per_sm_demand={"shared_memory": 1, "registers": 1},
        ),
        _event(
            "shared-release",
            dependencies=("shared-work",),
            lifetime_id="shared-life",
        ),
    )

    with pytest.raises(ValueError, match="reserved occupancy resource"):
        EventGraph(events, lifetimes=lifetimes)
