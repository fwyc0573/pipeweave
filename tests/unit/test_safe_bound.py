"""Tests for the narrow, provenance-separated safe-bound evaluator."""

import pytest

from event_simulator import Event, ResourceConfig, compare_des_bound, schedule


def _order_counterexample_events(order):
    long = Event(
        "long",
        "MMA",
        "kernel",
        "stream-long",
        "a",
        10.0,
        stream_ordered=False,
    )
    short = Event(
        "short",
        "MMA",
        "kernel",
        "stream-short",
        "a",
        1.0,
        stream_ordered=False,
    )
    tail = Event(
        "tail",
        "FMA",
        "kernel",
        "stream-tail",
        "b",
        10.0,
        dependencies=("short",),
        stream_ordered=False,
    )
    by_id = {event.event_id: event for event in (long, short, tail)}
    return [by_id[event_id] for event_id in order]


def _independent_events():
    return [
        Event("long", "MMA", "kernel", "stream-long", None, 10.0, stream_ordered=False),
        Event("short", "FMA", "kernel", "stream-short", None, 1.0, stream_ordered=False),
        Event("middle", "SFU", "kernel", "stream-middle", None, 4.0, stream_ordered=False),
    ]


def test_existing_scheduler_order_counterexample_is_recorded():
    resources = ResourceConfig({"a": 1, "b": 1})
    results = {
        name: schedule(events, resources).makespan
        for name, events in (
            ("long-first", _order_counterexample_events(("long", "short", "tail"))),
            ("short-first", _order_counterexample_events(("short", "long", "tail"))),
        )
    }

    assert results == {"long-first": 21.0, "short-first": 11.0}


def test_safe_bound_is_invariant_under_input_order():
    from event_simulator import SafeBoundEvaluator

    evaluator = SafeBoundEvaluator()
    events = _independent_events()

    assert evaluator.evaluate(events).bound == 10.0
    assert evaluator.evaluate(tuple(reversed(events))).bound == 10.0


def test_safe_bound_matches_the_exact_zero_work_edge_case():
    from event_simulator import SafeBoundEvaluator

    events = [
        Event("zero-a", "MMA", "kernel", "stream-a", None, 0.0, stream_ordered=False),
        Event("zero-b", "FMA", "kernel", "stream-b", None, 0.0, stream_ordered=False),
    ]

    assert SafeBoundEvaluator().evaluate(events).bound == 0.0


def test_safe_bound_uses_duration_not_prior_schedule_times():
    from event_simulator import SafeBoundEvaluator

    event = Event(
        "event",
        "MMA",
        "kernel",
        "stream",
        None,
        3.0,
        stream_ordered=False,
        start_time=20.0,
        end_time=23.0,
    )

    assert SafeBoundEvaluator().evaluate([event]).bound == 3.0


@pytest.mark.parametrize(
    ("events", "message"),
    [
        ([], "at least one event"),
        (
            [
                Event("duplicate", "MMA", "kernel", "stream-a", None, 1.0, stream_ordered=False),
                Event("duplicate", "FMA", "kernel", "stream-b", None, 2.0, stream_ordered=False),
            ],
            "unique event ids",
        ),
        (
            [
                Event(
                    "dependent",
                    "MMA",
                    "kernel",
                    "stream",
                    None,
                    1.0,
                    dependencies=("other",),
                    stream_ordered=False,
                )
            ],
            "independent events",
        ),
        ([Event("ordered", "MMA", "kernel", "stream", None, 1.0)], "stream_ordered=False"),
        ([Event("resource", "MMA", "kernel", "stream", "tensor", 1.0, stream_ordered=False)], "resource=None"),
    ],
)
def test_safe_bound_rejects_inputs_outside_the_proven_domain(events, message):
    from event_simulator import SafeBoundEvaluator

    with pytest.raises(ValueError, match=message):
        SafeBoundEvaluator().evaluate(events)


def test_safe_bound_is_not_implicitly_a_bound_comparison_input():
    from event_simulator import SafeBoundEvaluator

    result = SafeBoundEvaluator().evaluate(_independent_events())

    with pytest.raises(ValueError, match="finite and positive"):
        compare_des_bound(actual_time=10.0, des_bound=result)
