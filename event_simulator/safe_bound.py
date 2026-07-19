"""Exact safe bounds for a narrowly supported independent-work domain."""

from collections.abc import Iterable
from dataclasses import dataclass

from .events import Event


@dataclass(frozen=True)
class SafeBound:
    """A bound with provenance distinct from a heuristic simulation result."""

    bound: float


class SafeBoundEvaluator:
    """Evaluate the exact bound for independent, unresource-bound events."""

    def evaluate(self, events: Iterable[Event]) -> SafeBound:
        ordered = tuple(events)
        if not ordered:
            raise ValueError("safe bound requires at least one event")

        event_ids = [event.event_id for event in ordered]
        if len(set(event_ids)) != len(event_ids):
            raise ValueError("safe bound requires unique event ids")

        for event in ordered:
            if event.dependencies:
                raise ValueError("safe bound supports independent events only")
            if event.stream_ordered:
                raise ValueError("safe bound requires stream_ordered=False")
            if event.resource is not None:
                raise ValueError("safe bound requires resource=None")

        # Event.__post_init__ guarantees finite, non-negative durations.
        return SafeBound(bound=max(event.duration for event in ordered))
