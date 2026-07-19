from itertools import permutations

from event_simulator import Event, EventGraph, ResourceConfig, SafeBoundEvaluator


def _event(event_id, duration, dependencies=(), global_demand=None):
    return Event(
        event_id=event_id,
        event_type="MMA",
        kernel_id="kernel",
        stream_id="stream",
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
    )


def _signature(result):
    return (
        result.bound,
        result.dependency_critical_path,
        tuple(result.global_resource_terms.items()),
        tuple(result.aggregate_per_sm_terms.items()),
        result.relaxations,
    )


def test_safe_bound_is_invariant_across_all_event_input_permutations():
    events = (
        _event("load", 2.0, global_demand={"hbm": 2}),
        _event(
            "compute-a",
            3.0,
            dependencies=("load",),
            global_demand={"tensor": 1},
        ),
        _event(
            "compute-b",
            4.0,
            dependencies=("load",),
            global_demand={"tensor": 1},
        ),
        _event(
            "store",
            1.0,
            dependencies=("compute-a", "compute-b"),
            global_demand={"hbm": 1},
        ),
    )
    config = ResourceConfig(
        global_capacities={"tensor": 1, "hbm": 2},
        sm_count=1,
        per_sm_capacities={},
    )

    signatures = {
        _signature(SafeBoundEvaluator().evaluate(EventGraph(order), config))
        for order in permutations(events)
    }

    assert len(signatures) == 1
    assert next(iter(signatures)) == (
        7.0,
        7.0,
        (("hbm", 2.5), ("tensor", 7.0)),
        (),
        (),
    )


def test_resource_term_order_is_canonical_not_mapping_insertion_order():
    event = _event(
        "event",
        2.0,
        global_demand={"z-resource": 1, "a-resource": 1},
    )
    config = ResourceConfig(
        global_capacities={"z-resource": 1, "a-resource": 1},
        sm_count=1,
        per_sm_capacities={},
    )

    result = SafeBoundEvaluator().evaluate(EventGraph((event,)), config)

    assert tuple(result.global_resource_terms) == (
        "a-resource",
        "z-resource",
    )
