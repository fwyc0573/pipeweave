from dataclasses import FrozenInstanceError

import pytest

from event_simulator import (
    Event,
    EventGraph,
    ResourceConfig,
    ResourceLifetime,
    SafeBound,
    SafeBoundEvaluator,
    compare_des_bound,
)


def _event(
    event_id: str,
    duration: float,
    *,
    dependencies: tuple[str, ...] = (),
    global_demand: dict[str, int] | None = None,
    per_sm_demand: dict[str, int] | None = None,
    eligible_sms: frozenset[int] | None = None,
    lifetime_id: str | None = None,
) -> Event:
    return Event(
        event_id=event_id,
        event_type="MMA",
        kernel_id="kernel",
        stream_id="stream",
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
        per_sm_demand=per_sm_demand or {},
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
    )


def _config(
    global_capacities: dict[str, int] | None = None,
    *,
    sm_count: int = 1,
    per_sm_capacities: dict[str, int] | None = None,
) -> ResourceConfig:
    return ResourceConfig(
        global_capacities=global_capacities or {},
        sm_count=sm_count,
        per_sm_capacities=per_sm_capacities or {},
    )


def _evaluate(
    events,
    config: ResourceConfig | None = None,
    *,
    lifetimes=(),
) -> SafeBound:
    return SafeBoundEvaluator().evaluate(
        EventGraph(tuple(events), lifetimes=tuple(lifetimes)),
        config or _config(),
    )


def test_independent_resource_free_bound_preserves_prior_exact_result():
    result = _evaluate(
        (
            _event("long", 10.0),
            _event("short", 1.0),
            _event("middle", 4.0),
        )
    )

    assert result.bound == 10.0
    assert result.dependency_critical_path == 10.0
    assert dict(result.global_resource_terms) == {}
    assert dict(result.aggregate_per_sm_terms) == {}
    assert result.relaxations == ()


def test_dependency_critical_path_sums_the_longest_chain():
    result = _evaluate(
        (
            _event("load", 2.0),
            _event("compute", 3.0, dependencies=("load",)),
            _event("store", 4.0, dependencies=("compute",)),
            _event("independent", 8.0),
        )
    )

    assert result.dependency_critical_path == 9.0
    assert result.bound == 9.0


def test_global_resource_term_uses_demand_weighted_resource_time():
    result = _evaluate(
        (
            _event("a", 2.0, global_demand={"hbm": 2}),
            _event("b", 3.0, global_demand={"hbm": 1}),
        ),
        _config({"hbm": 2}),
    )

    assert dict(result.global_resource_terms) == {"hbm": 3.5}
    assert result.bound == 3.5


def test_aggregate_per_sm_term_uses_total_replicated_capacity():
    result = _evaluate(
        (
            _event("a", 2.0, per_sm_demand={"tensor": 1}),
            _event("b", 3.0, per_sm_demand={"tensor": 2}),
        ),
        _config(sm_count=2, per_sm_capacities={"tensor": 2}),
    )

    assert dict(result.aggregate_per_sm_terms) == {"tensor": 2.0}
    assert result.bound == 3.0


def test_bound_is_the_maximum_of_proven_terms():
    result = _evaluate(
        (
            _event("a", 4.0, global_demand={"hbm": 1}),
            _event(
                "b",
                4.0,
                dependencies=("a",),
                global_demand={"hbm": 1},
            ),
            _event("c", 10.0, global_demand={"hbm": 1}),
        ),
        _config({"hbm": 1}),
    )

    assert result.dependency_critical_path == 10.0
    assert dict(result.global_resource_terms) == {"hbm": 18.0}
    assert result.bound == 18.0


def test_term_evidence_and_result_are_immutable():
    result = _evaluate(
        (_event("event", 2.0, global_demand={"hbm": 1}),),
        _config({"hbm": 1}),
    )

    with pytest.raises(FrozenInstanceError):
        result.bound = 3.0
    with pytest.raises(TypeError):
        result.global_resource_terms["hbm"] = 3.0
    with pytest.raises(TypeError):
        result.aggregate_per_sm_terms["tensor"] = 1.0


def test_all_zero_non_empty_graph_has_zero_bound():
    result = _evaluate((_event("a", 0.0), _event("b", 0.0)))

    assert result.bound == 0.0
    assert result.dependency_critical_path == 0.0


def test_safe_bound_rejects_empty_graph():
    with pytest.raises(ValueError, match="non-empty"):
        SafeBoundEvaluator().evaluate(EventGraph(()), _config())


def test_safe_bound_uses_the_shared_resource_validator():
    graph = EventGraph((_event("event", 1.0, global_demand={"missing": 1}),))

    with pytest.raises(ValueError, match="unknown global resource"):
        SafeBoundEvaluator().evaluate(graph, _config())


def test_safe_bound_names_affinity_and_lifetime_relaxations():
    lifetime = ResourceLifetime(
        lifetime_id="worker",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slots": 1},
        eligible_sms=frozenset({0}),
    )
    events = (
        _event("acquire", 0.0, lifetime_id="worker"),
        _event(
            "work",
            2.0,
            dependencies=("acquire",),
            per_sm_demand={"slots": 1},
            lifetime_id="worker",
        ),
        _event(
            "release",
            0.0,
            dependencies=("work",),
            lifetime_id="worker",
        ),
        _event("affine", 1.0, eligible_sms=frozenset({1})),
    )
    config = _config(sm_count=2, per_sm_capacities={"slots": 1})

    result = _evaluate(events, config, lifetimes=(lifetime,))

    assert result.relaxations == (
        "eligible_sm_affinity",
        "resource_lifetime_reservations",
    )
    assert result.bound == 2.0


def test_safe_bound_is_not_implicitly_a_bound_comparison_input():
    result = _evaluate((_event("event", 3.0),))

    with pytest.raises(ValueError, match="finite and positive"):
        compare_des_bound(actual_time=10.0, des_bound=result)
