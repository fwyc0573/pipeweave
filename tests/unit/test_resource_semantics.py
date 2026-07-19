import pytest

import event_simulator


Event = event_simulator.Event
EventGraph = getattr(event_simulator, "EventGraph", None)
ResourceConfig = event_simulator.ResourceConfig
ResourceLifetime = getattr(event_simulator, "ResourceLifetime", None)


def _event(
    event_id: str = "event",
    *,
    global_demand: dict[str, int] | None = None,
    per_sm_demand: dict[str, int] | None = None,
    eligible_sms: frozenset[int] | None = None,
    lifetime_id: str | None = None,
    dependencies: tuple[str, ...] = (),
) -> Event:
    return Event(
        event_id=event_id,
        event_type="MMA",
        kernel_id="kernel",
        stream_id="stream",
        duration=1.0,
        global_demand=global_demand or {},
        per_sm_demand=per_sm_demand or {},
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
        dependencies=dependencies,
    )


def test_resource_config_has_one_global_and_one_replicated_sm_topology():
    config = ResourceConfig(
        global_capacities={"hbm": 2, "launch": 1},
        sm_count=4,
        per_sm_capacities={"cta_slots": 2, "tensor_core": 1},
    )

    assert dict(config.global_capacities) == {"hbm": 2, "launch": 1}
    assert config.sm_count == 4
    assert dict(config.per_sm_capacities) == {
        "cta_slots": 2,
        "tensor_core": 1,
    }
    with pytest.raises(TypeError):
        config.global_capacities["hbm"] = 3
    with pytest.raises(TypeError):
        config.per_sm_capacities["cta_slots"] = 3


def test_resource_config_is_detached_from_mutable_capacity_inputs():
    global_capacities = {"hbm": 2}
    per_sm_capacities = {"cta_slots": 2}

    config = ResourceConfig(global_capacities, 2, per_sm_capacities)
    global_capacities["hbm"] = 3
    per_sm_capacities["cta_slots"] = 3

    assert dict(config.global_capacities) == {"hbm": 2}
    assert dict(config.per_sm_capacities) == {"cta_slots": 2}


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "global_capacities": {"hbm": 0},
                "sm_count": 1,
                "per_sm_capacities": {},
            },
            "global resource capacity must be a positive integer",
        ),
        (
            {
                "global_capacities": {},
                "sm_count": 0,
                "per_sm_capacities": {},
            },
            "sm_count must be a positive integer",
        ),
        (
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {"cta_slots": True},
            },
            "per-SM resource capacity must be a positive integer",
        ),
        (
            {
                "global_capacities": {"shared": 1},
                "sm_count": 1,
                "per_sm_capacities": {"shared": 1},
            },
            "resource cannot be both global and per-SM",
        ),
        (
            {
                "global_capacities": {"": 1},
                "sm_count": 1,
                "per_sm_capacities": {},
            },
            "resource names must be non-empty strings",
        ),
        (
            {
                "global_capacities": {"hbm": 1.5},
                "sm_count": 1,
                "per_sm_capacities": {},
            },
            "global resource capacity must be a positive integer",
        ),
        (
            {
                "global_capacities": {},
                "sm_count": True,
                "per_sm_capacities": {},
            },
            "sm_count must be a positive integer",
        ),
    ],
)
def test_resource_config_rejects_invalid_topology(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ResourceConfig(**kwargs)


@pytest.mark.parametrize(
    ("event_kwargs", "message"),
    [
        ({"global_demand": {"": 1}}, "resource names must be non-empty"),
        ({"global_demand": {"hbm": -1}}, "demand must be a non-negative integer"),
        (
            {"per_sm_demand": {"tensor_core": True}},
            "demand must be a non-negative integer",
        ),
        ({"eligible_sms": frozenset()}, "eligible_sms must not be empty"),
        (
            {"eligible_sms": frozenset({-1})},
            "eligible SM ids must be non-negative integers",
        ),
        (
            {"eligible_sms": frozenset({True})},
            "eligible SM ids must be non-negative integers",
        ),
    ],
)
def test_event_rejects_invalid_resource_requirements(event_kwargs, message):
    with pytest.raises(ValueError, match=message):
        _event(**event_kwargs)


def test_resource_config_accepts_simultaneous_demands_at_capacity():
    graph = EventGraph(
        (
            _event(
                global_demand={"hbm": 2, "launch": 1},
                per_sm_demand={"cta_slots": 2, "tensor_core": 1},
                eligible_sms=frozenset({1, 3}),
            ),
        )
    )
    config = ResourceConfig(
        global_capacities={"hbm": 2, "launch": 1},
        sm_count=4,
        per_sm_capacities={"cta_slots": 2, "tensor_core": 1},
    )

    assert config.validate_graph(graph) is None


@pytest.mark.parametrize(
    ("event_kwargs", "config_kwargs", "message"),
    [
        (
            {"global_demand": {"unknown": 1}},
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {},
            },
            "unknown global resource",
        ),
        (
            {"per_sm_demand": {"unknown": 1}},
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {},
            },
            "unknown per-SM resource",
        ),
        (
            {"global_demand": {"hbm": 2}},
            {
                "global_capacities": {"hbm": 1},
                "sm_count": 1,
                "per_sm_capacities": {},
            },
            "global demand exceeds capacity",
        ),
        (
            {"per_sm_demand": {"tensor_core": 2}},
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {"tensor_core": 1},
            },
            "per-SM demand exceeds capacity",
        ),
        (
            {"eligible_sms": frozenset({2})},
            {
                "global_capacities": {},
                "sm_count": 2,
                "per_sm_capacities": {},
            },
            "eligible SM id is outside ResourceConfig",
        ),
    ],
)
def test_resource_config_rejects_impossible_event_requirements(
    event_kwargs, config_kwargs, message
):
    event = _event(**event_kwargs)
    config = ResourceConfig(**config_kwargs)

    with pytest.raises(ValueError, match=message):
        config.validate_graph(EventGraph((event,)))


def test_resource_config_accepts_a_valid_lifetime_reservation():
    lifetime = ResourceLifetime(
        lifetime_id="worker",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"cta_slots": 2, "registers": 1},
        eligible_sms=frozenset({0, 1}),
    )
    graph = EventGraph(
        (
            _event("acquire", lifetime_id="worker"),
            _event(
                "work",
                dependencies=("acquire",),
                lifetime_id="worker",
                per_sm_demand={"cta_slots": 2, "registers": 1, "tensor_core": 1},
            ),
            _event(
                "release",
                dependencies=("work",),
                lifetime_id="worker",
            ),
        ),
        lifetimes=(lifetime,),
    )
    config = ResourceConfig(
        global_capacities={},
        sm_count=2,
        per_sm_capacities={"cta_slots": 2, "registers": 2, "tensor_core": 1},
    )

    assert config.validate_graph(graph) is None


def test_resource_lifetime_is_immutable_and_detached_from_inputs():
    reservation = {"cta_slots": 1}
    lifetime = ResourceLifetime(
        "worker",
        "acquire",
        "release",
        reservation,
        eligible_sms=frozenset({1, 0}),
    )

    reservation["cta_slots"] = 2

    assert dict(lifetime.per_sm_reservation) == {"cta_slots": 1}
    assert lifetime.eligible_sms == frozenset({0, 1})
    with pytest.raises(TypeError):
        lifetime.per_sm_reservation["cta_slots"] = 2


def test_resource_lifetime_returns_only_transient_per_sm_demand():
    lifetime = ResourceLifetime(
        "worker",
        "acquire",
        "release",
        {"cta_slots": 1},
    )

    transient = lifetime.transient_per_sm_demand(
        {"cta_slots": 1, "tensor_core": 1, "explicit_zero": 0}
    )

    assert transient == {"tensor_core": 1, "explicit_zero": 0}


@pytest.mark.parametrize(
    ("lifetime_kwargs", "config_kwargs", "message"),
    [
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"unknown": 1},
            },
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {"cta_slots": 1},
            },
            "unknown reservation resource",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 2},
            },
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {"cta_slots": 1},
            },
            "lifetime reservation exceeds per-SM capacity",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 1},
                "eligible_sms": frozenset({1}),
            },
            {
                "global_capacities": {},
                "sm_count": 1,
                "per_sm_capacities": {"cta_slots": 1},
            },
            "lifetime eligible SM id is outside ResourceConfig",
        ),
    ],
)
def test_resource_config_rejects_impossible_lifetime_reservations(
    lifetime_kwargs, config_kwargs, message
):
    lifetime = ResourceLifetime(**lifetime_kwargs)
    config = ResourceConfig(**config_kwargs)
    graph = EventGraph(
        (
            _event("acquire", lifetime_id="worker"),
            _event(
                "release",
                dependencies=("acquire",),
                lifetime_id="worker",
            ),
        ),
        lifetimes=(lifetime,),
    )

    with pytest.raises(ValueError, match=message):
        config.validate_graph(graph)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "lifetime_id": "",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 1},
            },
            "lifetime_id must be a non-empty string",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "same",
                "release_event_id": "same",
                "per_sm_reservation": {"cta_slots": 1},
            },
            "lifetime endpoints must be distinct",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {},
            },
            "per_sm_reservation must not be empty",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 0},
            },
            "reservation must be a positive integer",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 1},
            },
            "acquire_event_id must be a non-empty string",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "",
                "per_sm_reservation": {"cta_slots": 1},
            },
            "release_event_id must be a non-empty string",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"": 1},
            },
            "resource names must be non-empty strings",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": True},
            },
            "reservation must be a positive integer",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 1},
                "eligible_sms": frozenset(),
            },
            "eligible_sms must not be empty",
        ),
        (
            {
                "lifetime_id": "worker",
                "acquire_event_id": "acquire",
                "release_event_id": "release",
                "per_sm_reservation": {"cta_slots": 1},
                "eligible_sms": frozenset({-1}),
            },
            "eligible SM ids must be non-negative integers",
        ),
    ],
)
def test_resource_lifetime_rejects_invalid_values(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ResourceLifetime(**kwargs)
