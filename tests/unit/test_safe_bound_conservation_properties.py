from itertools import product

import pytest

import event_simulator


Event = event_simulator.Event
EventGraph = event_simulator.EventGraph
ResourceConfig = event_simulator.ResourceConfig
SafeBoundEvaluator = event_simulator.SafeBoundEvaluator
solve_exact_schedule = getattr(event_simulator, "solve_exact_schedule", None)


def _event(
    event_id,
    duration,
    *,
    dependencies=(),
    global_demand=None,
    per_sm_demand=None,
):
    return Event(
        event_id=event_id,
        event_type="MMA",
        kernel_id="kernel",
        stream_id="stream",
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
        per_sm_demand=per_sm_demand or {},
    )


def _config(global_capacities=None, *, sm_count=1, per_sm_capacities=None):
    return ResourceConfig(
        global_capacities=global_capacities or {},
        sm_count=sm_count,
        per_sm_capacities=per_sm_capacities or {},
    )


def test_resource_terms_equal_declared_resource_time_over_capacity():
    graph = EventGraph(
        (
            _event(
                "a",
                2.0,
                global_demand={"hbm": 2},
                per_sm_demand={"tensor": 1},
            ),
            _event(
                "b",
                3.0,
                global_demand={"hbm": 1},
                per_sm_demand={"tensor": 2},
            ),
        )
    )
    config = _config(
        {"hbm": 2},
        sm_count=2,
        per_sm_capacities={"tensor": 2},
    )

    result = SafeBoundEvaluator().evaluate(graph, config)

    assert result.global_resource_terms["hbm"] == (2.0 * 2 + 3.0) / 2
    assert result.aggregate_per_sm_terms["tensor"] == (
        2.0 + 3.0 * 2
    ) / (2 * 2)


def test_increasing_required_work_cannot_reduce_the_safe_bound():
    config = _config({"hbm": 1})
    baseline = SafeBoundEvaluator().evaluate(
        EventGraph((_event("event", 2.0, global_demand={"hbm": 1}),)),
        config,
    )
    more_duration = SafeBoundEvaluator().evaluate(
        EventGraph((_event("event", 3.0, global_demand={"hbm": 1}),)),
        config,
    )
    more_demand = SafeBoundEvaluator().evaluate(
        EventGraph((_event("event", 2.0, global_demand={"hbm": 2}),)),
        _config({"hbm": 2}),
    )

    assert more_duration.bound >= baseline.bound
    assert more_demand.global_resource_terms["hbm"] >= (
        baseline.global_resource_terms["hbm"]
    )


@pytest.mark.parametrize(
    ("durations", "demands", "dependency_shape"),
    tuple(product(
        ((0.0, 1.0, 2.0), (1.0, 1.0, 2.0), (2.0, 1.0, 2.0)),
        ((0, 1, 1), (1, 1, 1), (2, 1, 0), (2, 2, 1)),
        ("independent", "chain", "fork"),
    )),
)
def test_safe_bound_never_exceeds_exact_global_resource_optimum(
    durations, demands, dependency_shape
):
    dependencies = {
        "independent": ((), (), ()),
        "chain": ((), ("a",), ("b",)),
        "fork": ((), ("a",), ("a",)),
    }[dependency_shape]
    events = tuple(
        _event(
            event_id,
            duration,
            dependencies=event_dependencies,
            global_demand={"resource": demand},
        )
        for event_id, duration, event_dependencies, demand in zip(
            ("a", "b", "c"),
            durations,
            dependencies,
            demands,
            strict=True,
        )
    )
    graph = EventGraph(events)
    config = _config({"resource": 2})

    bound = SafeBoundEvaluator().evaluate(graph, config).bound
    exact = solve_exact_schedule(graph, config).makespan

    assert bound <= exact


def test_multi_sm_aggregate_term_is_safe_but_not_an_exact_placement_model():
    graph = EventGraph(
        tuple(
            _event(
                event_id,
                1.0,
                per_sm_demand={"registers": 2},
            )
            for event_id in ("a", "b", "c")
        )
    )
    config = _config(sm_count=2, per_sm_capacities={"registers": 3})

    result = SafeBoundEvaluator().evaluate(graph, config)

    assert result.aggregate_per_sm_terms["registers"] == 1.0
    assert result.bound == 1.0
    true_placement_optimum = 2.0
    assert result.bound < true_placement_optimum
    with pytest.raises(ValueError, match="one SM.*per-SM demand"):
        solve_exact_schedule(graph, config)
