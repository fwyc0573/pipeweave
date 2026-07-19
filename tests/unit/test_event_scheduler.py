from itertools import permutations
from types import MappingProxyType

import pytest

import event_simulator
from event_simulator import (
    Event,
    EventGraph,
    ResourceConfig,
    ResourceLifetime,
    ScheduleEntry,
    schedule,
)


def _event(
    event_id,
    duration,
    *,
    event_type="MMA",
    dependencies=(),
    global_demand=None,
    per_sm_demand=None,
    eligible_sms=None,
    lifetime_id=None,
    kernel_id="kernel",
    stream_id="stream",
):
    return Event(
        event_id=event_id,
        event_type=event_type,
        kernel_id=kernel_id,
        stream_id=stream_id,
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
        per_sm_demand=per_sm_demand or {},
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
    )


def _config(*, global_capacities=None, sm_count=1, per_sm_capacities=None):
    return ResourceConfig(
        global_capacities=global_capacities or {},
        sm_count=sm_count,
        per_sm_capacities=per_sm_capacities or {},
    )


def test_empty_graph_returns_zero_feasible_result_and_zero_counters():
    graph = EventGraph(())
    result = schedule(graph, _config(sm_count=2))

    counter_type = event_simulator.SchedulerCounters
    assert result.graph is graph
    assert result.entries == ()
    assert result.makespan == 0.0
    assert result.counters == counter_type(0, 0, 0, 0)
    assert dict(result.by_id()) == {}


def test_explicit_dependencies_determine_start_times():
    graph = EventGraph(
        (
            _event(
                "load",
                3.0,
                event_type="GlobalLoad",
                global_demand={"memory": 1},
            ),
            _event(
                "compute",
                2.0,
                dependencies=("load",),
                global_demand={"tensor": 1},
            ),
            _event(
                "store",
                1.0,
                event_type="GlobalStore",
                dependencies=("compute",),
                global_demand={"memory": 1},
            ),
        )
    )

    result = schedule(
        graph,
        _config(global_capacities={"memory": 1, "tensor": 1}),
    )
    by_id = result.by_id()

    assert by_id["load"].start_time == 0.0
    assert by_id["compute"].start_time == by_id["load"].end_time == 3.0
    assert by_id["store"].start_time == by_id["compute"].end_time == 5.0
    assert result.makespan == 6.0


def test_remaining_path_priority_avoids_the_historical_long_first_schedule():
    graph = EventGraph(
        (
            _event("long", 10.0, global_demand={"engine": 1}),
            _event("short", 1.0, global_demand={"engine": 1}),
            _event("tail", 10.0, dependencies=("short",)),
        )
    )

    result = schedule(graph, _config(global_capacities={"engine": 1}))
    by_id = result.by_id()

    assert by_id["short"].start_time == 0.0
    assert by_id["long"].start_time == 1.0
    assert by_id["tail"].start_time == 1.0
    assert result.makespan == 11.0


def test_equal_priority_uses_event_id_and_is_caller_order_invariant():
    events = (
        _event("b", 2.0, global_demand={"engine": 1}),
        _event("a", 2.0, global_demand={"engine": 1}),
    )
    config = _config(global_capacities={"engine": 1})

    baseline = schedule(EventGraph(events), config)
    permuted = [
        schedule(EventGraph(order), config)
        for order in permutations(events)
    ]

    assert baseline.by_id()["a"].start_time == 0.0
    assert baseline.by_id()["b"].start_time == 2.0
    assert all(result.entries == baseline.entries for result in permuted)
    assert all(result.counters == baseline.counters for result in permuted)


def test_same_stream_without_dependency_does_not_create_hidden_order():
    graph = EventGraph(
        (
            _event(
                "memory",
                2.0,
                event_type="GlobalLoad",
                global_demand={"memory": 1},
                stream_id="same",
            ),
            _event(
                "compute",
                3.0,
                global_demand={"compute": 1},
                stream_id="same",
            ),
        )
    )

    result = schedule(
        graph,
        _config(global_capacities={"memory": 1, "compute": 1}),
    )

    assert result.by_id()["memory"].start_time == 0.0
    assert result.by_id()["compute"].start_time == 0.0
    assert result.makespan == 3.0


def test_global_capacity_allows_parallel_events_when_vector_fits():
    graph = EventGraph(
        (
            _event("a", 4.0, global_demand={"engine": 1}),
            _event("b", 2.0, global_demand={"engine": 1}),
        )
    )

    result = schedule(graph, _config(global_capacities={"engine": 2}))

    assert result.by_id()["a"].start_time == 0.0
    assert result.by_id()["b"].start_time == 0.0
    assert result.makespan == 4.0


def test_multi_resource_admission_is_atomic_and_skips_blocked_ready_event():
    graph = EventGraph(
        (
            _event("holder", 4.0, global_demand={"r2": 1}),
            _event("holder_tail", 10.0, dependencies=("holder",)),
            _event("both", 3.0, global_demand={"r1": 1, "r2": 1}),
            _event("r1_only", 2.0, global_demand={"r1": 1}),
        )
    )
    result = schedule(
        graph,
        _config(global_capacities={"r1": 1, "r2": 1}),
    )
    by_id = result.by_id()

    assert by_id["holder"].start_time == 0.0
    assert by_id["r1_only"].start_time == 0.0
    assert by_id["both"].start_time == 4.0
    assert result.counters.blocked_ready_rechecks > 0


def test_per_sm_vectors_are_co_located_instead_of_split_across_sms():
    graph = EventGraph(
        (
            _event(
                "x_holder",
                3.0,
                per_sm_demand={"x": 1},
                eligible_sms=frozenset({0}),
            ),
            _event("x_tail", 10.0, dependencies=("x_holder",)),
            _event(
                "y_holder",
                3.0,
                per_sm_demand={"y": 1},
                eligible_sms=frozenset({1}),
            ),
            _event("y_tail", 10.0, dependencies=("y_holder",)),
            _event("composite", 2.0, per_sm_demand={"x": 1, "y": 1}),
        )
    )

    result = schedule(
        graph,
        _config(
            sm_count=2,
            per_sm_capacities={"x": 1, "y": 1},
        ),
    )
    composite = result.by_id()["composite"]

    assert result.by_id()["x_holder"].sm_id == 0
    assert result.by_id()["y_holder"].sm_id == 1
    assert composite.start_time == 3.0
    assert composite.sm_id == 0


def test_saturated_per_sm_pool_avoids_redundant_placement_scans():
    graph = EventGraph(
        tuple(
            _event(f"work_{index:02d}", 1.0, per_sm_demand={"slot": 1})
            for index in range(12)
        )
    )

    result = schedule(
        graph,
        _config(sm_count=4, per_sm_capacities={"slot": 1}),
    )

    assert result.makespan == 3.0
    assert result.counters.placement_checks == 30


def test_affinity_is_enforced_and_smallest_feasible_sm_breaks_ties():
    graph = EventGraph(
        (
            _event(
                "a_flexible",
                2.0,
                per_sm_demand={"slot": 1},
                eligible_sms=frozenset({0, 1}),
            ),
            _event(
                "b_fixed",
                2.0,
                per_sm_demand={"slot": 1},
                eligible_sms=frozenset({1}),
            ),
        )
    )

    result = schedule(
        graph,
        _config(sm_count=2, per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["a_flexible"].sm_id == 0
    assert result.by_id()["b_fixed"].sm_id == 1
    assert result.by_id()["a_flexible"].start_time == 0.0
    assert result.by_id()["b_fixed"].start_time == 0.0


def test_global_and_per_sm_admission_is_atomic():
    graph = EventGraph(
        (
            _event(
                "slot_0",
                2.0,
                per_sm_demand={"slot": 1},
                eligible_sms=frozenset({0}),
            ),
            _event("slot_0_tail", 10.0, dependencies=("slot_0",)),
            _event(
                "slot_1",
                2.0,
                per_sm_demand={"slot": 1},
                eligible_sms=frozenset({1}),
            ),
            _event("slot_1_tail", 10.0, dependencies=("slot_1",)),
            _event(
                "combined",
                5.0,
                global_demand={"engine": 1},
                per_sm_demand={"slot": 1},
            ),
            _event("global_only", 1.0, global_demand={"engine": 1}),
        )
    )

    result = schedule(
        graph,
        _config(
            global_capacities={"engine": 1},
            sm_count=2,
            per_sm_capacities={"slot": 1},
        ),
    )

    assert result.by_id()["global_only"].start_time == 0.0
    assert result.by_id()["combined"].start_time == 2.0


def test_same_timestamp_completions_release_full_vector_before_admission():
    graph = EventGraph(
        (
            _event("r1_holder", 1.0, global_demand={"r1": 1}),
            _event("r1_tail", 10.0, dependencies=("r1_holder",)),
            _event("r2_holder", 1.0, global_demand={"r2": 1}),
            _event("r2_tail", 10.0, dependencies=("r2_holder",)),
            _event("combined", 2.0, global_demand={"r1": 1, "r2": 1}),
        )
    )

    result = schedule(
        graph,
        _config(global_capacities={"r1": 1, "r2": 1}),
    )

    assert result.by_id()["r1_holder"].end_time == 1.0
    assert result.by_id()["r2_holder"].end_time == 1.0
    assert result.by_id()["combined"].start_time == 1.0


def test_lifetime_reservation_is_held_through_release_completion():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event("acquire", 1.0, lifetime_id="cta"),
            _event(
                "member",
                2.0,
                dependencies=("acquire",),
                per_sm_demand={"slot": 1},
                lifetime_id="cta",
            ),
            _event(
                "release",
                1.0,
                dependencies=("member",),
                lifetime_id="cta",
            ),
            _event("external", 1.0, per_sm_demand={"slot": 1}),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(sm_count=1, per_sm_capacities={"slot": 1}),
    )
    by_id = result.by_id()

    assert by_id["acquire"].sm_id == 0
    assert by_id["member"].sm_id == 0
    assert by_id["release"].sm_id == 0
    assert by_id["external"].start_time == by_id["release"].end_time == 4.0
    assert result.counters.lifetime_checks > 0


def test_lifetime_affinity_uses_smallest_eligible_sm():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
        eligible_sms=frozenset({1, 2}),
    )
    graph = EventGraph(
        (
            _event("acquire", 1.0, lifetime_id="cta"),
            _event(
                "release",
                1.0,
                dependencies=("acquire",),
                lifetime_id="cta",
            ),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(sm_count=3, per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["acquire"].sm_id == 1
    assert result.by_id()["release"].sm_id == 1


def test_lifetime_endpoints_keep_transient_demand_event_local():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event(
                "acquire",
                2.0,
                per_sm_demand={"slot": 1, "alu": 1},
                lifetime_id="cta",
            ),
            _event(
                "release",
                2.0,
                dependencies=("acquire",),
                per_sm_demand={"slot": 1, "alu": 1},
                lifetime_id="cta",
            ),
            _event("external", 1.0, per_sm_demand={"alu": 1}),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(
            per_sm_capacities={"slot": 1, "alu": 1},
        ),
    )

    assert result.by_id()["acquire"].start_time == 0.0
    assert result.by_id()["release"].start_time == 2.0
    assert result.by_id()["external"].start_time == 4.0


def test_lifetime_acquire_waits_for_temporary_reservation_capacity():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event("holder", 2.0, per_sm_demand={"slot": 1}),
            _event("holder_tail", 10.0, dependencies=("holder",)),
            _event("acquire", 1.0, lifetime_id="cta"),
            _event(
                "release",
                1.0,
                dependencies=("acquire",),
                lifetime_id="cta",
            ),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["holder"].start_time == 0.0
    assert result.by_id()["acquire"].start_time == 2.0


def test_lifetime_member_waits_for_transient_capacity_on_its_sm():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event("acquire", 1.0, lifetime_id="cta"),
            _event(
                "member",
                1.0,
                dependencies=("acquire",),
                per_sm_demand={"slot": 1, "alu": 1},
                lifetime_id="cta",
            ),
            _event(
                "release",
                1.0,
                dependencies=("member",),
                lifetime_id="cta",
            ),
            _event("alu_holder", 3.0, per_sm_demand={"alu": 1}),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(per_sm_capacities={"slot": 1, "alu": 1}),
    )

    assert result.by_id()["acquire"].start_time == 0.0
    assert result.by_id()["alu_holder"].start_time == 0.0
    assert result.by_id()["member"].start_time == 3.0
    assert result.by_id()["release"].start_time == 4.0


def _external_wait_graph():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event("acquire", 1.0, lifetime_id="cta"),
            _event(
                "external",
                2.0,
                dependencies=("acquire",),
                per_sm_demand={"slot": 1},
            ),
            _event(
                "release",
                1.0,
                dependencies=("external",),
                lifetime_id="cta",
            ),
        ),
        (lifetime,),
    )
    return graph


def test_external_wait_uses_an_alternate_sm_and_makes_progress():
    result = schedule(
        _external_wait_graph(),
        _config(sm_count=2, per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["acquire"].sm_id == 0
    assert result.by_id()["external"].sm_id == 1
    assert result.by_id()["release"].sm_id == 0
    assert result.makespan == 4.0


def test_external_wait_without_any_feasible_sm_raises_no_progress():
    error_type = event_simulator.SchedulingNoProgressError

    with pytest.raises(error_type, match="no progress"):
        schedule(
            _external_wait_graph(),
            _config(sm_count=1, per_sm_capacities={"slot": 1}),
        )


def test_zero_duration_transient_demand_consumes_no_resource_time():
    graph = EventGraph(
        (
            _event("positive", 1.0, global_demand={"engine": 1}),
            _event("zero", 0.0, global_demand={"engine": 1}),
        )
    )

    result = schedule(graph, _config(global_capacities={"engine": 1}))

    assert result.by_id()["positive"].start_time == 0.0
    assert result.by_id()["zero"].start_time == 0.0
    assert result.by_id()["zero"].end_time == 0.0
    assert result.makespan == 1.0


def test_explicit_zero_per_sm_demand_does_not_require_sm_placement():
    graph = EventGraph(
        (_event("zero_demand", 1.0, per_sm_demand={"slot": 0}),)
    )

    result = schedule(
        graph,
        _config(per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["zero_demand"].sm_id is None
    assert result.makespan == 1.0


def test_zero_duration_lifetime_endpoints_apply_state_transitions():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event("acquire", 0.0, lifetime_id="cta"),
            _event(
                "release",
                0.0,
                dependencies=("acquire",),
                lifetime_id="cta",
            ),
            _event(
                "external",
                1.0,
                dependencies=("release",),
                per_sm_demand={"slot": 1},
            ),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(sm_count=1, per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["acquire"].start_time == 0.0
    assert result.by_id()["release"].start_time == 0.0
    assert result.by_id()["external"].start_time == 0.0
    assert result.makespan == 1.0


def test_zero_duration_release_rechecks_deferred_event_at_same_timestamp():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
    )
    graph = EventGraph(
        (
            _event("acquire", 1.0, lifetime_id="cta"),
            _event(
                "member",
                1.0,
                dependencies=("acquire",),
                lifetime_id="cta",
            ),
            _event(
                "release",
                0.0,
                dependencies=("member",),
                lifetime_id="cta",
            ),
            _event("external", 2.0, per_sm_demand={"slot": 1}),
        ),
        (lifetime,),
    )

    result = schedule(
        graph,
        _config(per_sm_capacities={"slot": 1}),
    )

    assert result.by_id()["release"].start_time == 2.0
    assert result.by_id()["release"].end_time == 2.0
    assert result.by_id()["external"].start_time == 2.0
    assert result.counters.blocked_ready_rechecks > 0


def test_all_zero_duration_graph_completes_without_running_events():
    graph = EventGraph(
        (
            _event("a", 0.0, global_demand={"engine": 1}),
            _event(
                "b",
                0.0,
                dependencies=("a",),
                global_demand={"engine": 1},
            ),
        )
    )

    result = schedule(graph, _config(global_capacities={"engine": 1}))

    assert result.by_id()["a"].start_time == 0.0
    assert result.by_id()["b"].start_time == 0.0
    assert result.makespan == 0.0


def test_blocked_ready_event_is_rechecked_after_capacity_release():
    graph = EventGraph(
        (
            _event("a", 2.0, global_demand={"engine": 1}),
            _event("b", 1.0, global_demand={"engine": 1}),
        )
    )

    result = schedule(graph, _config(global_capacities={"engine": 1}))

    assert result.by_id()["a"].start_time == 0.0
    assert result.by_id()["b"].start_time == 2.0
    assert result.counters.blocked_ready_rechecks >= 1
    assert result.counters.ready_queue_operations >= 4


def test_blocked_event_is_not_rechecked_for_unrelated_resource_release():
    graph = EventGraph(
        (
            _event("a_holder", 5.0, global_demand={"a": 1}),
            _event("a_waiter", 1.0, global_demand={"a": 1}),
            _event("b_1", 1.0, global_demand={"b": 1}),
            _event(
                "b_2",
                1.0,
                dependencies=("b_1",),
                global_demand={"b": 1},
            ),
            _event(
                "b_3",
                1.0,
                dependencies=("b_2",),
                global_demand={"b": 1},
            ),
            _event(
                "b_4",
                1.0,
                dependencies=("b_3",),
                global_demand={"b": 1},
            ),
            _event(
                "b_5",
                1.0,
                dependencies=("b_4",),
                global_demand={"b": 1},
            ),
        )
    )

    result = schedule(
        graph,
        _config(global_capacities={"a": 1, "b": 1}),
    )

    assert result.by_id()["a_waiter"].start_time == 5.0
    assert result.counters.blocked_ready_rechecks == 1


def test_schedule_uses_resource_config_validation_without_partial_result():
    graph = EventGraph(
        (_event("too_large", 1.0, global_demand={"engine": 2}),)
    )

    with pytest.raises(ValueError, match="exceeds capacity"):
        schedule(graph, _config(global_capacities={"engine": 1}))


def test_result_keeps_graph_and_schedule_witnesses_immutable():
    event = _event("work", 1.0)
    graph = EventGraph((event,))

    result = schedule(graph, _config())

    assert result.graph is graph
    assert result.graph.by_id["work"] is event
    assert isinstance(result.entries[0], ScheduleEntry)
    assert not hasattr(event, "start_time")
    assert event.dependencies == ()

    by_id = result.by_id()
    assert isinstance(by_id, MappingProxyType)
    with pytest.raises(TypeError):
        by_id["other"] = result.entries[0]
