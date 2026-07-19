# DES Exact Oracle and SafeBound Formal Contract

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Established the Wave-2 exact-oracle domain, SafeBound proof, named relaxations, and exhaustive tiny-case evidence. |

## Status

This contract covers the Phase-2 Wave-2 proof layer only. It certifies an
exact modeled optimum for the finite domain below and an order-invariant
analytical lower bound for the broader normalized fixed-duration domain. It
does not certify a feasible scheduler result, hardware latency, cycle accuracy,
or a measured-hardware lower bound.

## Provenance Separation

The public evidence layers remain distinct:

```text
ExactScheduleResult
    complete-search optimum for the declared exact-oracle domain

SafeBound
    scalable analytical lower bound with immutable term evidence

SimulationResult
    deterministic feasible schedule; not a proof-layer result

MeasuredHardwareComparison
    matched finite empirical evidence; not supplied by Wave 2
```

`ExactScheduleResult.entries` is an immutable tuple of the one shared
`ScheduleEntry` type in canonical `event_id` order. No alias, mutable schedule
mapping, best-known incomplete result, or implicit conversion between evidence
layers exists.

## Normalized Modeled Domain

The SafeBound theorem applies after construction of one validated `EventGraph`
and one validated `ResourceConfig` with:

1. a non-empty finite acyclic graph;
2. explicit dependency edges only;
3. fixed finite non-negative Event durations;
4. non-preemptive half-open execution intervals `[start, end)`;
5. non-negative integer chip-global and transient per-SM demand vectors;
6. positive integer chip-global and replicated per-SM capacities;
7. a positive integer SM count; and
8. no schedule-dependent duration or work mutation inside the proof layer.

Eligible-SM affinity and `ResourceLifetime` reservations may be present in the
SafeBound input, but they are deliberately dropped and named as relaxations.
Dynamic cache transitions, persistent work assignment, split-K topology,
reduction work, and partial-tile issued work must first lower into the fixed
graph/duration/demand contract owned by their later modules. The proof layer
does not infer them.

The exact oracle uses the same normalized model with these narrower rules:

- `ResourceLifetime` is rejected;
- eligible-SM affinity is rejected;
- when `sm_count == 1`, per-SM demand is an ordinary anonymous renewable
  resource and is supported exactly;
- when `sm_count > 1`, every nonzero per-SM demand is rejected because SM
  placement is not enumerated;
- multi-SM graphs containing only global work or explicit zero per-SM demand
  remain supported; and
- the initial implementation performs no branch-and-bound pruning.

## Exact-Oracle Optimality Argument

For every supported input, the oracle enumerates every precedence-feasible
Event permutation. For each permutation, serial schedule generation places
each Event at its earliest dependency- and resource-feasible time against the
already placed Events.

The result is exact under the declared domain:

1. Every generated schedule is precedence feasible because an Event starts no
   earlier than the maximum completion time of its predecessors.
2. Every generated schedule is resource feasible because the complete demand
   vector is admitted atomically only where accumulated demand remains within
   every capacity over the whole half-open interval.
3. Any feasible schedule can be left-shifted, without increasing makespan,
   until no Event can move earlier by itself; therefore an active optimum
   exists for the regular makespan objective.
4. Order one active optimum by nondecreasing start time, breaking tied starts
   with a precedence-feasible topological order. That order is among the
   enumerated permutations.
5. Inducting over that order, serial SGS reproduces each active-optimum start.
   If it placed the current Event earlier, Events not yet listed could not be
   the missing blocker before the recorded start, so the Event could also move
   earlier in the full schedule, contradicting activity.
6. Complete enumeration therefore contains an optimal schedule. Selecting the
   minimum makespan yields the exact modeled optimum.

The earliest feasible insertion changes only at a predecessor completion or an
already placed Event completion. Feasibility is checked at the candidate start
and every already placed Event start strictly inside the candidate interval,
which covers every point where renewable-resource usage can increase.

A zero-duration Event has `start == end`, consumes no resource-time under the
half-open interval rule, and still contributes its completion time to explicit
precedence. Binary-float inputs and operations are used exactly; no tolerance,
integerization, clamp, or scaling factor changes feasibility.

If `max_permutations` prevents complete enumeration,
`IncompleteExactSearchError` is raised and no `ExactScheduleResult` is
returned. A partial best schedule is never relabeled exact.

## SafeBound Proof

For any feasible modeled schedule with makespan `T`, define:

```text
dependency_critical_path
    longest sum of Event durations along an explicit dependency path

global_resource_term[r]
    sum(duration[e] * global_demand[e, r]) / global_capacity[r]

aggregate_per_sm_term[r]
    sum(duration[e] * per_sm_demand[e, r])
    / (sm_count * per_sm_capacity[r])
```

Each term is a lower bound on `T`:

1. Every dependency path must execute in dependency order, so its duration sum
   cannot exceed `T`.
2. A chip-global resource can supply at most
   `global_capacity[r] * T` resource-time units.
3. Across all SMs, a replicated resource can supply at most
   `sm_count * per_sm_capacity[r] * T` resource-time units.

Therefore:

```text
SafeBound.bound = max(
    dependency_critical_path,
    every global_resource_term,
    every aggregate_per_sm_term,
)
```

is also no greater than the modeled optimum. Simultaneous multi-resource demand
does not invalidate any individual conservation inequality. Taking the maximum
of independently proven lower bounds remains safe.

Dropping eligible-SM affinity enlarges the feasible set and cannot increase the
relaxed optimum. Dropping cross-Event lifetime reservations has the same
direction. The result records these omissions as, respectively,
`eligible_sm_affinity` and `resource_lifetime_reservations`; it adds no
unproved tightening term for either constraint.

For two SMs with per-SM capacity `3` and three independent duration-`1` Events
each demanding `2`, the aggregate term is:

```text
(1 * 2 + 1 * 2 + 1 * 2) / (2 * 3) = 1.0
```

The true placed optimum is `2.0` because each SM can host only one such Event
at a time. This demonstrates why the `1.0` term is a safe relaxation and why
the exact oracle rejects this multi-SM placement domain.

## Exhaustive Tiny-Case Validation

Authoritative command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
python tests/validation/validate_safe_bound_exact_oracle.py
```

The independent reference enumerates bounded integer start assignments and
does not call serial SGS. The generated corpus exhausts:

- capacities `{1, 2}`;
- three Event durations independently selected from `{0, 1, 2}`;
- three demands independently selected from every integer in
  `[0, capacity]`; and
- independent, chain, fork, join, and chain-plus-independent DAGs.

Fresh observed evidence:

| Metric | Expected | Actual | Delta / Failures |
|---|---:|---:|---:|
| Oracle cases | 4,725 | 4,725 passed | 0 failed |
| Exact time-grid comparison | 0 mismatches | 0 mismatches | max absolute delta `0.0` |
| Bound safety | 0 violations | 0 violations | minimum `exact - bound = 0.0` |
| Input permutations | 28,350 | 28,350 checked | 0 mismatches |
| Resource conservation | 0 failures | 0 failures | 0 |
| Monotonicity | 18,360 | 18,360 checked | 0 failures |

The complete case records are stored in
`safe_bound_oracle_cases.json`. Their canonical record-list SHA-256 is:

```text
5e173514000270d7c5d2a504b1adcd9d62f9285ee6d12819a48397c63724da67
```

## Claim Boundary

This proof establishes only the normalized modeled theorem above. It does not
establish that modeled durations, cache state, launch policy, work quantities,
or capacities match a particular kernel or GPU. Those inputs require the later
manifest, cache, hardware-adapter, cycle-level, and measured-hardware gates.
Finite hardware comparisons may support empirical claims but cannot widen this
modeled theorem into a universal physical lower-bound claim.
