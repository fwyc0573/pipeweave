from itertools import permutations
from math import factorial
from random import Random

from event_simulator import (
    Event,
    EventGraph,
    ResourceConfig,
    ResourceLifetime,
    SafeBoundEvaluator,
    schedule,
    solve_exact_schedule,
)


CASE_COUNT = 32
CASE_SEED = 20260720


def _event(
    event_id,
    duration,
    *,
    dependencies=(),
    global_demand=None,
    per_sm_demand=None,
    eligible_sms=None,
    lifetime_id=None,
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
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
    )


def _tiny_exact_cases():
    rng = Random(CASE_SEED)
    cases = []
    for case_index in range(CASE_COUNT):
        event_count = 1 + case_index % 5
        events = []
        for event_index in range(event_count):
            event_id = f"e{event_index}"
            dependencies = tuple(
                f"e{dependency_index}"
                for dependency_index in range(event_index)
                if rng.random() < 0.35
            )
            events.append(
                _event(
                    event_id,
                    rng.randint(0, 3),
                    dependencies=dependencies,
                    global_demand={
                        "g0": rng.randint(0, 2),
                        "g1": rng.randint(0, 2),
                    },
                    per_sm_demand={"p0": rng.randint(0, 2)},
                )
            )
        cases.append(
            (
                tuple(events),
                ResourceConfig(
                    global_capacities={"g0": 2, "g1": 2},
                    sm_count=1,
                    per_sm_capacities={"p0": 2},
                ),
            )
        )
    return tuple(cases)


def _validate_feasible_schedule(graph, config, result):
    entries = result.by_id()
    assert len(result.entries) == len(graph.events)
    assert len(entries) == len(graph.events)
    assert set(entries) == set(graph.by_id)

    for event in graph.events:
        entry = entries[event.event_id]
        assert entry.end_time - entry.start_time == float(event.duration)
        assert entry.start_time >= 0.0
        for dependency in event.dependencies:
            assert entries[dependency].end_time <= entry.start_time

        requires_sm = (
            event.lifetime_id is not None
            or event.eligible_sms is not None
            or any(event.per_sm_demand.values())
        )
        assert (entry.sm_id is not None) == requires_sm
        if event.eligible_sms is not None:
            assert entry.sm_id in event.eligible_sms

    for lifetime in graph.lifetimes:
        member_entries = {
            event.event_id: entries[event.event_id]
            for event in graph.events
            if event.lifetime_id == lifetime.lifetime_id
        }
        acquire_sm = member_entries[lifetime.acquire_event_id].sm_id
        assert acquire_sm is not None
        assert all(entry.sm_id == acquire_sm for entry in member_entries.values())
        if lifetime.eligible_sms is not None:
            assert acquire_sm in lifetime.eligible_sms

    boundaries = sorted(
        {
            value
            for entry in result.entries
            for value in (entry.start_time, entry.end_time)
        }
    )
    lifetime_by_id = {
        lifetime.lifetime_id: lifetime for lifetime in graph.lifetimes
    }
    for left, right in zip(boundaries, boundaries[1:]):
        if left == right:
            continue
        time = (left + right) / 2.0
        active_events = tuple(
            event
            for event in graph.events
            if entries[event.event_id].start_time
            <= time
            < entries[event.event_id].end_time
        )

        for resource, capacity in config.global_capacities.items():
            usage = sum(
                event.global_demand.get(resource, 0)
                for event in active_events
            )
            assert usage <= capacity

        for sm_id in range(config.sm_count):
            usage = {
                resource: 0 for resource in config.per_sm_capacities
            }
            for lifetime in graph.lifetimes:
                acquire = entries[lifetime.acquire_event_id]
                release = entries[lifetime.release_event_id]
                if acquire.start_time <= time < release.end_time:
                    assert acquire.sm_id is not None
                    if acquire.sm_id == sm_id:
                        for resource, quantity in (
                            lifetime.per_sm_reservation.items()
                        ):
                            usage[resource] += quantity

            for event in active_events:
                entry = entries[event.event_id]
                if entry.sm_id != sm_id:
                    continue
                reservation = {}
                if event.lifetime_id is not None:
                    reservation = lifetime_by_id[
                        event.lifetime_id
                    ].per_sm_reservation
                for resource, quantity in event.per_sm_demand.items():
                    if resource not in reservation:
                        usage[resource] += quantity

            for resource, capacity in config.per_sm_capacities.items():
                assert usage[resource] <= capacity

    expected_makespan = max(
        (entry.end_time for entry in result.entries),
        default=0.0,
    )
    assert result.makespan == expected_makespan


def test_tiny_exact_bound_and_feasible_layers_agree_across_input_orders():
    checked_permutations = 0
    for events, config in _tiny_exact_cases():
        graph = EventGraph(events)
        result = schedule(graph, config)
        exact = solve_exact_schedule(graph, config)
        safe_bound = SafeBoundEvaluator().evaluate(graph, config)

        _validate_feasible_schedule(graph, config, result)
        assert safe_bound.bound <= exact.makespan <= result.makespan

        for event_order in permutations(events):
            permuted_graph = EventGraph(event_order)
            permuted_result = schedule(permuted_graph, config)
            _validate_feasible_schedule(
                permuted_graph,
                config,
                permuted_result,
            )
            assert permuted_result.entries == result.entries
            assert permuted_result.counters == result.counters
            checked_permutations += 1

    expected_permutations = sum(
        factorial(1 + case_index % 5)
        for case_index in range(CASE_COUNT)
    )
    assert checked_permutations == expected_permutations == 921


def test_independent_validator_covers_lifetime_affinity_and_mixed_demand():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 1},
        eligible_sms=frozenset({1}),
    )
    events = (
        _event(
            "acquire",
            1.0,
            global_demand={"launch": 1},
            per_sm_demand={"slot": 1, "alu": 1},
            lifetime_id="cta",
        ),
        _event(
            "member",
            2.0,
            dependencies=("acquire",),
            global_demand={"memory": 1},
            per_sm_demand={"slot": 1, "alu": 1},
            lifetime_id="cta",
        ),
        _event(
            "release",
            1.0,
            dependencies=("member",),
            per_sm_demand={"slot": 1, "alu": 1},
            lifetime_id="cta",
        ),
        _event(
            "independent",
            3.0,
            global_demand={"memory": 1},
            per_sm_demand={"alu": 1},
            eligible_sms=frozenset({0}),
        ),
    )
    config = ResourceConfig(
        global_capacities={"launch": 1, "memory": 2},
        sm_count=2,
        per_sm_capacities={"slot": 1, "alu": 1},
    )

    baseline = schedule(EventGraph(events, (lifetime,)), config)
    _validate_feasible_schedule(baseline.graph, config, baseline)

    for event_order in permutations(events):
        result = schedule(EventGraph(event_order, (lifetime,)), config)
        _validate_feasible_schedule(result.graph, config, result)
        assert result.entries == baseline.entries
        assert result.counters == baseline.counters
