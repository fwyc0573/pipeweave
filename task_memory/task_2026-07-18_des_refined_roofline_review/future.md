# DES Refined Roofline Review and Remediation Future Work

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Replaced the initial boundary with the reviewed architecture, scheduler, cache, policy, and benchmark backlog. |
| 2026-07-18 | Created the initial outside-session boundary. |

## Outside the Current Session

The items below are intentionally excluded from the current bounded remediation. Any implementation requires an explicit user-approved task and a clean workspace.

### P0 — Separate bound and explanatory scheduling contracts

- Design a `SafeBoundEvaluator` that is order-invariant and proven no greater than the modeled optimum for its supported domain.
- Keep the current feasible timeline under a distinct `HeuristicScheduler` / schedule-estimate contract.
- Define exact public types and provenance so neither result can be silently cast into the other.
- Validate small DAGs against an exact enumerator or optimization formulation before generalizing.

### P0 — Define measurement and cache-state semantics

- Make cold HBM, warm L2, and explicit initial residency named input states.
- Represent L2 request bytes, HBM miss bytes, capacity/eviction assumptions, and output visibility without violating traffic conservation.
- Re-run the four Small violations under a controlled measurement protocol before attributing them to cache state.

### P1 — Model launch policy and CTA lifetime

- Add explicit persistent-CTA multi-tile work grouping.
- Add split-K replicated work, partial-K slices, reduction events, and completion semantics.
- Add CTA lifetime residency, simultaneous resource demand, and SM/lane affinity.
- Distinguish actual CTA admission from analytical output-tile tasks.

### P1 — Complete structural operator semantics

- Give `tile_k` a physically justified K-stage/cache-pipeline meaning or remove it through an approved API migration.
- Define padded/masked partial-tile work and pipeline drain from kernel-specific evidence.
- Replace experimental FA2 `cta_kv=64` with the canonical kernel-traits contract.
- Expand FA2/FA3 from aggregate task timing to explicit QK, softmax, PV, synchronization, memory, and persistent-scheduling phases where validated.

### P1 — Make design-space evaluation scalable

- Replace repeated global ready scans with a deterministic indegree/ready-queue/resource-heap design while preserving schedule semantics.
- Add event-count and wall-clock performance tests across representative DAG sizes.
- Consider operator-specific closed-form aggregation where event enumeration adds no explanatory value.

### P2 — Establish the missing scientific evidence

- Select a named cycle-accurate comparator and benchmark the same workload, boundary, and host environment before testing the `10000x` target.
- Create a held-out multi-hardware DES protocol with frozen calibration and no target-hardware latency fitting.
- Validate event/resource attribution against independent hardware counters, not only final latency.
- Report supported-policy coverage, violations, absolute times, MAPE, paired tightness, and runtime for every hardware/category.

### Explicitly rejected direction

- Do not train or add an ML scaling/correction closure to hide structural discrepancies.
- Do not clamp violations, infer warm cache silently, or skip unsupported/failing rows.
