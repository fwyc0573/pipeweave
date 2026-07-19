# DES Full Semantics and Scientific Validation Design

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Corrected lifetime-covered transient-demand ownership and documented the greedy scheduler's explicit no-progress policy boundary. |
| 2026-07-20 | Froze the reviewed Wave-3 SchedulerCounters, SimulationResult, report provenance, empty-graph, placement-tie, and lifetime timing contracts. |
| 2026-07-20 | Froze the measured-calibration, held-out zero-shot, modeled-universal theorem, comparator approval, and Phase-2 ownership contracts. |
| 2026-07-20 | Identified Accel-Sim/GPGPU-Sim A100 as the only source-backed comparator candidate and recorded its approval/toolchain boundary. |
| 2026-07-20 | Selected the dependency-free exhaustive serial SGS exact oracle and added the project-domain completeness proof obligation and independent cross-check. |
| 2026-07-20 | Reconciled the cache/GEMM-manifest Claude WATCH, selected one static manifest-order cache contract, and rejected its unsafe isolated-cache bound recommendation. |
| 2026-07-20 | Reconciled the shared execution-kernel Claude review, retained its narrow type split, and corrected its lifetime-deadlock and scheduler-complexity reasoning. |
| 2026-07-20 | Corrected `tensor_all_ops` from presumed counter evidence to an analytical-feature value and separated future measured counters as a fourth provenance layer. |
| 2026-07-20 | Reconciled two exact-engine Claude reviews, retained the standard-library exhaustive SGS recommendation as WATCH, and rejected their erroneous example and over-broad zero-duration/result suggestions. |
| 2026-07-20 | Accepted the user-selected four-layer Option A contract and added dataset-grounded split-K, work-accounting, and report-semantics boundaries. |
| 2026-07-20 | Added a measured exact-oracle option matrix and rejected environment availability as implicit dependency approval. |
| 2026-07-20 | Reconciled the preliminary StepCode Claude WATCH, corrected unsafe/unsupported recommendations, and added a source-grounded conditional architecture candidate. |
| 2026-07-20 | Added the evidence-domain separation for Hopper-only transfer, cross-architecture transfer, primitive calibration, and cycle-accurate comparison. |
| 2026-07-20 | Established the unreviewed phase-1 design frame, provenance layers, inherited invariants, and unresolved semantic decisions. |

## Status

This is the **independently approved and checkpointed implementation design**. Phase 1 and the reviewed Wave-1/2 proof kernel are committed and pushed; Phase 2 Wave 3 is active. The four-layer provenance split, shared execution kernel, exact engine, cache/manifest semantics, calibration/held-out/theorem boundaries, and Accel-Sim/GPGPU-Sim dependency are resolved. StepCode Claude returned `APPROVE` at the complete design gate, both implemented module gates, and the Wave-3 pre-implementation ownership/interface gate.

## Design Objective

Extend the DES model without collapsing four different forms of evidence into one number:

```text
declared workload + declared execution semantics
        -> exact modeled optimum for a supported finite domain
        -> scalable analytical lower bound for a declared broader domain
        -> deterministic feasible schedule for explanation and execution-policy study
        -> matched measured-hardware comparison
```

Each arrow has its own result type, supported domain, proof obligation, and failure behavior. None may silently certify another.

## Non-Negotiable Inherited Invariants

1. `SimulationResult.makespan` remains a feasible-schedule estimate unless a separate proof establishes otherwise.
2. Bound results must be invariant to irrelevant caller ordering.
3. Warm-cache or initial-residency assumptions are explicit state, never implicit traffic discounts.
4. Required work and traffic are conserved; replicated or padded physical work cannot be relabeled as useful work.
5. CTA policy, resource occupancy, affinity, persistent grouping, split-K, and reduction behavior are explicit declared inputs or are rejected.
6. Unsupported states fail fast; there is no approximation fallback hidden behind an exact or bound API.
7. Measured-hardware claims require matched workload, launch policy, units, visibility boundary, and state.
8. Held-out zero-shot evaluation cannot use target-hardware latency fitting.
9. A universal real-hardware lower-bound claim is not implied by a proof over a declared Event model.

## Required Provenance Layers

### Layer A: Exact Modeled Optimum

The exact solver/oracle, if accepted, must declare a finite supported domain and return a proof-auditable optimum for that domain. Complexity limits must be explicit and must fail fast rather than silently switching algorithms.

### Layer B: Scalable Safe Bound

The scalable evaluator must combine only individually proven lower-bound terms. It must be order-invariant and may be looser than the exact optimum. Exactness and safety are separate claims.

### Layer C: Feasible Scheduler

The scheduler produces a deterministic feasible schedule, attribution, and timeline. Its policy and complexity target must be explicit. Scheduler speed does not establish bound validity.

### Layer D: Measured-Hardware Evidence

Calibration and evaluation data are tracked by provenance. Calibration data, development data, held-out hardware, and final measured comparisons must not be mixed.

## Frozen Semantic Decisions

1. “Universal” means universal only over the declared normalized fixed-duration model; real hardware receives a separate finite empirical audit.
2. Cache state is one manifest-order, fully associative, size-aware LRU abstract L2 over HBM, with explicit initial recency/dirty state and output visibility.
3. `Event` owns immutable event-local demand; `ResourceLifetime` owns cross-event CTA occupancy reservation and the normalization from raw member demand to uncovered transient demand; `ScheduleEntry` owns placement and time.
4. Scheduler priority is descending remaining dependency-path duration with `event_id` tie-break; implicit iterable stream order and scheduler-written dependencies are removed.
5. The exact oracle exhaustively evaluates every precedence-feasible permutation with serial SGS over its declared no-lifetime/no-affinity domain.
6. `GemmLaunchManifest` is the sole new-path source for persistent worker assignment, split-K partitions, reduction topology, and issued extents.
7. Logical work, explicit-policy physical issued work, legacy analytical work, and measured-counter work remain separate quantities.
8. The approved comparator is a pinned Accel-Sim/GPGPU-Sim A100 synthetic GEMM, reported as a GPGPU-Sim cycle-level PTX-mode comparison.
9. Target-hardware zero-shot evaluation uses specification-derived calibration only; target primitive measurement belongs to a separate explicitly non-zero-shot calibrated audit.

## Simplicity Boundary

Prefer extending existing deep modules over adding parallel representations. A new module is justified only when it owns a distinct proof or provenance contract that cannot be safely represented by the existing interface. Validation belongs at the semantic boundary that owns the invariant; adjacent callers must not duplicate it defensively.

## Evaluation-Domain Separation

The final design must keep the following evidence labels distinct:

1. **Within-Hopper held-out transfer:** the current-policy offline domain has at most `15,164` supported rows across H100, H20, H200, and H800.
2. **Cross-architecture held-out transfer:** requires split-K/persistent semantics for the currently unsupported Ampere, Ada, and Blackwell rows and cannot be inferred from Hopper-only evidence.
3. **Idealized specification calibration:** current hardware-JSON peak-rate conversion; useful as a mechanistic input but not measured calibration.
4. **Measured primitive calibration:** versioned microbenchmark/counter evidence with calibration/evaluation separation; complete operator latency is evaluation data, not a hidden correction factor.
5. **Cycle-accurate runtime comparison:** a named, version-pinned comparator on the same workload, launch/cache state, output boundary, and host protocol. DES runtime alone cannot establish a speedup ratio.
6. **Modeled-domain theorem:** a proof over declared Event/resource semantics.
7. **Measured-hardware audit:** finite empirical comparisons with explicit violations and uncertainty; it cannot by itself prove a universal theorem.

## Architecture Candidate After Option A

The separation below is accepted by the user's Option A decision. The concrete APIs, algorithms, and execution semantics remain conditional until the remaining discussion decisions and the full phase-1 independent review are complete.

### Centralized graph semantics

The current private `scheduler._validated_dependencies()` owns duplicate-ID and dependency checks but also creates stream edges from caller iteration order. That behavior is incompatible with a bound advertised as invariant to non-semantic input permutation. The certified path therefore needs one invariant-owning graph normalization boundary shared by the bound, exact oracle, and rewritten scheduler. It must either:

1. receive all ordering as explicit dependency edges; or
2. receive explicit per-stream sequence metadata independent of container iteration order.

Until such metadata exists, a certified evaluator must reject `stream_ordered=True` rather than infer a proof graph from list order. The existing scheduler contract remains separate until its migration is explicitly accepted.

### Separate proof and execution results

The current draft continues to favor three separate result contracts:

```text
SafeBound
    scalable proven lower bound + immutable term evidence

ExactScheduleResult
    exact modeled optimum + optimality evidence for a declared computational domain

SimulationResult
    deterministic feasible schedule + timeline
```

The exact oracle is a genuinely different module because its exponential/optimization complexity and failure semantics differ from the linear-time analytical evaluator. This is not duplicate implementation. Conversely, graph validation, resource-demand representation, and operator work accounting must not be copied into both solvers.

### Candidate scalable terms

For a normalized acyclic graph with fixed non-negative event durations and fixed resource demands during each event, the initial candidate is:

```text
critical_path = longest weighted dependency path
resource_work[r] = sum(event.duration * event.demand[r]) / capacity[r]
safe_bound = max(critical_path, max(resource_work.values()))
```

Each term is no greater than the exact modeled optimum under the declared fixed-duration/capacity semantics:

- dependency-chain events must occur sequentially;
- every resource can provide at most `capacity[r] * makespan` resource-time units.

The per-resource inequality remains safe, though potentially loose, for simultaneous multi-resource demand. Affinity can support tighter subset/pool terms, but a global capacity term remains safe only when `capacity[r]` denotes the same eligible pool used by every counted demand. Dynamic cache state, persistent CTA, split-K, and partial tiles must first lower into explicit durations, demands, physical work, and dependencies; the bound evaluator must not guess those semantics.

**State-matching correction:** a cold-cache duration is not automatically safe for a workload whose declared initial state is warm. Safety is relative to the exact same cache-state contract. A cold assumption can produce a larger value and may exceed the warm-state modeled optimum or measured latency.

### Exact-oracle boundary

The oracle must return an exact value only after a complete proof of optimality. If a search/solver budget expires, it raises an explicit error and returns no `ExactScheduleResult`; a best-known feasible schedule is not relabeled exact. Event-count limits, time limits, solver choice, and optional third-party dependencies will be selected from measured behavior and explicit user approval rather than fixed speculatively.

### Exact-oracle algorithm options

| Option | Dependency | Exactness evidence | Semantic reach | Main cost/risk |
|---|---|---|---|---|
| Exhaustive active-schedule / branch-and-bound enumeration | Python standard library only | Complete search-tree exhaustion; optional stored search statistics | Fixed-duration non-preemptive DAGs with simultaneous renewable-resource demand; fixed affinity can be encoded | Exponential and requires a carefully proven schedule-generation rule |
| SciPy/HiGHS MILP | SciPy is installed on the current host but not declared by the repo | Solver optimal status plus zero reported MIP gap | Strong for fixed-duration precedence and finite resource/assignment formulations | Big-M/formulation correctness, cumulative lifetime constraints, reproducibility, and undeclared dependency |
| OR-Tools CP-SAT | Not installed | Solver optimal status | Natural interval/cumulative constraints if integerized safely | New dependency, integer time scaling, and explicit approval required |

The selected first engine is the Python-standard-library exhaustive serial schedule-generation scheme. It adds no dependency, matches the small verification-oracle role, and exposes a search whose completeness can be audited directly. SciPy/HiGHS remains an unselected comparison option, not an ambient dependency. Dynamic cache state or schedule-dependent durations must not be smuggled into this fixed-duration formulation.

For the renewable-resource RCPSP subset, exhaustive enumeration visits every precedence-feasible Event permutation. For each permutation, serial SGS places each fixed-duration Event at its earliest dependency- and resource-feasible time against already placed Events. Resource intervals are half-open `[start, end)`; a zero-duration Event occupies no resource-time, while its precedence completion remains at its start time. Affinity alternatives, cross-event CTA reservations, and dynamic cache transitions require additional state/assignment enumeration and are rejected by this oracle.

The supported semantic domain is:

- non-empty finite normalized acyclic EventGraph;
- fixed finite non-negative float durations;
- non-preemptive Events;
- explicit precedence dependencies;
- simultaneous non-negative integer demand vectors;
- positive integer anonymous renewable-resource capacities;
- no `ResourceLifetime`, eligible-SM restriction, SM identity, or schedule-dependent duration.

`ExactScheduleResult` contains only `makespan: float` and an immutable tuple of ScheduleEntry witnesses in canonical Event order. A caller-provided search budget may abort computation, but budget exhaustion raises an explicit incomplete-search error and returns no exact result. No best-known schedule, gap estimate, mutable statistics dictionary, or solver-success flag is exposed as exact evidence.

The project-specific completeness argument is:

1. Every serial-SGS output is feasible because an Event is inserted only after all predecessors and only over intervals whose accumulated demand plus its vector is within every capacity.
2. For the regular makespan objective, at least one optimal feasible schedule is active: repeatedly left-shifting any individually movable Event preserves feasibility and cannot increase makespan; with a finite set of scheduled interval endpoints, this reaches a schedule in which no Event can move earlier alone.
3. Take an active optimum and order Events by nondecreasing start time, breaking equal-start ties by a precedence-feasible topological order. This is one enumerated permutation.
4. Induct over that permutation. Assume prior Events are reproduced at their active-optimum times. The current Event is feasible at its recorded time. If SGS could place it earlier, not-yet-listed Events all start no earlier than its recorded time. Over the shifted interval before that time they are absent; after that time the shifted interval is a subset of the original interval. Therefore they cannot be the missing blocker, and the Event could also move earlier in the full schedule, contradicting activity. SGS therefore reproduces its recorded start.
5. The enumerated set contains that active optimum, so the minimum complete-search makespan is the modeled optimum.

Equal-time zero-duration predecessor/successor pairs are handled by the topological tie order. Float semantics are the repository's exact binary-float inputs and sums; the oracle does not introduce tolerance-based feasibility or time integerization.

The implementation must be falsified independently on tiny integer-time instances by enumerating all bounded start-time assignments, not by calling serial SGS twice. Required cases include simultaneous multi-resource conflict, a precedence/resource interaction where greedy caller order is suboptimal, tied starts, zero duration, input permutations, and budget exhaustion. Branch-and-bound is not part of initial GREEN; each future pruning rule needs a preservation proof and its own RED case.

### Exact-engine review reconciliation

Two independent StepCode Claude passes recommend the standard-library exhaustive serial schedule-generation scheme as the smallest first oracle. The first artifact returned `APPROVE` with a proof-document WATCH, but its proposed three-event expected optimum was arithmetically wrong (`8`, not `7`). A correction pass supplied a valid three-event optimum of `6` and again returned `APPROVE`. The engine is selected after primary-lane reconciliation, but its implementation remains proof- and TDD-gated:

- Complete enumeration over every precedence-feasible permutation is simpler and more auditable than introducing an undeclared MILP dependency for a tiny verification oracle.
- Initial GREEN implementation should be exhaustive; branch-and-bound pruning is added only after each pruning rule has a preservation proof and its own RED case.
- The accepted semantic target should consume the Wave-1 simultaneous integer demand vector directly, because multi-resource demand is an explicit user requirement. It remains fixed-duration, non-preemptive, renewable-capacity, explicit-DAG, and no-affinity. Dynamic cache duration, cross-event reservations, persistent grouping, and inferred split-K remain outside this exact domain.
- Claude's public `int` makespan recommendation conflicts with the existing float-duration model. The minimal result candidate follows repository conventions: `makespan: float` plus an immutable tuple of scheduled Event witnesses. A mutable schedule dictionary and nested search-statistics result are not required for correctness.
- Claude's proposed global rule that zero-duration Events must have zero demand is not adopted. It would change current Event semantics and operator lowerings before the resource contract is designed. The exact domain must instead state and prove its half-open zero-duration behavior or explicitly reject resource-demanding zero-duration nodes at the oracle boundary.
- The correction pass alternated between “every active schedule” and only a “dominant set” characterization without a verified source. The self-contained project-model proof above is therefore the governing obligation; the implementation cannot return `ExactScheduleResult` until its assumptions are encoded and the independent time-indexed cross-check passes.

The external source identity has been verified through Crossref as Rainer Kolisch, *Serial and parallel resource-constrained project scheduling methods revisited: Theory and computation*, European Journal of Operational Research (1996), DOI `10.1016/0377-2217(95)00357-6`. The DOI metadata establishes bibliographic identity only; it does not substitute for the required project-model proof.

### Split-K metadata boundary

The current dataset cannot support an implicit split-factor reconstruction from `is_split_k` and `cta_count`. Across split-K rows, `cta_count / base_ctas` is not uniformly an integer or even at least one: Hopper ratios span approximately `1.178571` to `4.137931`, while H20 includes `85` rows with `cta_count < base_ctas` and ratios as low as `0.131313`. Other architectures contain many rows where `cta_count == base_ctas` despite `is_split_k=1`. Therefore, neither `is_split_k` nor the CTA ratio uniquely determines replication, persistent grouping, or reduction topology. The legacy `gemm_8_calculator.py` and `gemm_9_calculator.py` use floor division and `max(1, ...)` to infer split slices, with the divisibility rejection commented out in the SM8 calculator. That feature-model heuristic is not authoritative launch metadata and cannot be reused by DES. The accepted lowering must consume an explicit launch manifest or reject the row with a counted reason.

### Four-way work accounting

The work contract must preserve three different quantities:

```text
logical_work
    useful mathematical work for the requested output

physical_issued_work
    work issued by the declared kernel policy, including padding and replication

dataset_analytical_work
    checked-in analytical feature generated by the legacy feature calculator

measured_counter_work
    future profiler-counter quantity with environment and counter provenance
```

For non-split Hopper rows, a simple padded-tile formula matches `tensor_all_ops` much more often than logical FLOPs: H100 `9,366/10,363`, H20 `9,202/9,534`, H200 `9,358/10,392`, and H800 `9,379/10,343`. The residual is not counter behavior. Recomputing the full Hopper `gemm_9_calculator.py` formula, including `max(1, cta_count / tile_count)`, matches `tensor_all_ops` within `rtol=1e-12`, `atol=1e-6` for H100 `10,363/10,363`, H20 `9,534/9,534`, H200 `10,392/10,392`, and H800 `10,343/10,343` rows. The checked-in column is therefore analytical feature evidence, not measured issued-work evidence. It supports tracing the legacy formula but does not validate physical padding or replication. Operator lowering and validation must derive physical issued work from explicit policy metadata and compare it with separately collected counters only when counter provenance exists.

### Report semantics boundary

The current `build_report()` assigns `critical_path=result.makespan`, while its event-ID chain follows the dependencies of the latest-finishing scheduled event. That number is a selected feasible-schedule makespan, not the dependency-DAG longest-path lower bound. In addition, `resource_busy_time` currently sums one `event.duration`; future multi-resource demand requires demand-weighted resource-time attribution. The report redesign must obtain proof-layer critical-path terms from the normalized graph and execution-layer makespan/timeline from `SimulationResult`, with distinct field names and provenance. It must not preserve the present conflation for compatibility.

### Shared execution-kernel candidate

The shared kernel uses the smallest set of concepts that owns the requested invariants without adding a generic topology framework:

```text
Event
    immutable unscheduled work specification

EventGraph
    one frozen normalized graph/lifetime boundary

ScheduleEntry
    event start/end plus optional SM placement

ResourceLifetime
    one explicit cross-event per-SM reservation

ResourceConfig
    chip-wide capacities plus replicated per-SM capacities
```

`Event` no longer stores `start_time` or `end_time`. It carries explicit dependencies, fixed duration, immutable global and per-SM demand vectors, optional non-lifetime SM eligibility, work/traffic metadata, and optional lifetime membership. `EventGraph` owns unique IDs, dependency existence, canonical `event_id` order, successor/indegree maps, acyclicity, and lifetime endpoint/membership validation. SafeBound, the exact oracle, the feasible scheduler, and reporting consume this same normalized object; no downstream module repeats graph validation or reconstructs stream edges.

`EventGraph` is a frozen validated value, not a mutable graph framework. A boundary function may construct it, but callers receive one typed graph contract rather than parallel tuples and dictionaries with duplicated invariants. `ScheduleEntry` is a distinct frozen result record because schedule placement is not part of the Event specification. `SimulationResult` contains the graph identity plus immutable entries, makespan, and one frozen `SchedulerCounters` value; it never rewrites semantic dependencies with scheduler-selected resource predecessors. The counters contain only `ready_queue_operations`, `blocked_ready_rechecks`, `placement_checks`, and `lifetime_checks`, keeping operational instrumentation separate from schedule evidence without adding a diagnostics module. `SimulationResult.by_id()` returns an immutable Event-ID-to-ScheduleEntry mapping. An empty EventGraph has one deterministic feasible result: empty entries, zero makespan, and zero counters; the exact-oracle and SafeBound non-empty domains remain unchanged.

All certified ordering is explicit. `stream_ordered` and caller-iterable stream inference are removed from the new path. Workload composition adds the prior kernel-completion dependency to the next launch explicitly. Existing input-order compatibility is intentionally broken rather than retained through an adapter. FA lowering must stop interleaving Event lists to manipulate lane selection and must emit explicit worker assignment/affinity semantics instead.

The GPU-scoped resource model has only two topology levels:

```text
global_capacities
    launch/HBM/L2 and other chip-wide renewable capacity

sm_count + per_sm_capacities
    replicated CTA occupancy and execution-pipe capacity
```

One Event acquires all of its event-local global and per-SM demands atomically. All per-SM demands for that Event co-locate on one assigned SM. `eligible_sms` restricts a non-lifetime Event. A lifetime owns the eligible-SM set for every member; member Events do not declare a conflicting affinity.

`ResourceLifetime` contains an ID, acquire/release Event IDs, per-SM reservation vector, eligible SMs, and explicit member IDs through Event membership. The reservation is acquired atomically immediately before the acquire Event starts, remains held through the release Event completion, and is then released. Graph validation requires every member to be ordered between the endpoints. A permanently impossible reservation is rejected before scheduling; temporary unavailability makes the lifetime wait for capacity.

An acyclic dependency graph alone does **not** rule out resource deadlock. Two lifetimes can hold different resources while their members wait for the other's held resource. The accepted contract therefore distinguishes lifetime-held CTA occupancy from transient execution resources:

- lifetime reservations cover occupancy resources held across Events, such as CTA slots, registers, and shared memory;
- a member's demand for a lifetime-held resource is served only from its own reservation and cannot exceed it;
- transient global/per-SM Event demands are acquired atomically only when the Event can start and are released at Event completion;
- no Event can hold a transient resource while waiting for another resource.

This removes cross-lifetime member hold-and-wait rather than relying on a false DAG-only deadlock argument. Persistent CTA execution is the same lifetime contract with multiple ordered work items; ordinary CTA execution uses a shorter lifetime. The exact oracle initially rejects lifetimes and affinity. The scalable SafeBound may omit those constraints as an explicit relaxation, but its aggregate per-SM term counts only demand not covered by a member's own reservation. The reservation and covered demand are omitted together; no reservation-duration tightening term is added.

The feasible scheduler uses one deterministic priority computed from the normalized graph: descending remaining dependency-path duration, then `event_id`. At each completion time it releases finished demands/reservations, exposes newly ready successors, and admits the highest-priority currently feasible Events atomically. Blocked ready Events remain pending until relevant capacity changes. Every returned result is caller-order invariant and feasible, but the fixed greedy policy is not a complete feasibility solver and does not promise a result for every graph that another ordering could schedule. If no Event can run or complete, it raises `SchedulingNoProgressError`; that error is an explicit policy/domain boundary, not a proof that the normalized graph is infeasible.

One accepted one-SM counterexample has a lifetime acquire that reserves the only
slot, an independent non-member Event that also needs the slot, and a release
that depends on both. A feasible order schedules the independent Event first,
but the frozen priority can acquire the reservation first and then report no
progress. Wave 3 records this limitation rather than adding backtracking,
retry, a second scheduling policy, or a blanket EventGraph rejection that would
incorrectly reject the corresponding alternate-SM case.

For deterministic placement, the scheduler chooses the smallest feasible SM ID.
A pure global Event with no affinity, lifetime, or per-SM demand has
`ScheduleEntry.sm_id=None`. A lifetime acquire atomically reserves its chosen
SM immediately before the acquire Event starts; the reservation remains held
through release Event completion. Member demand on a covered resource is
served from that reservation rather than added to it. Acquire/release
transient demands remain event-local and atomic. At one timestamp, completed
transient demand and completed release reservations are removed before new
admission. Zero-duration acquire/release Events occupy no resource-time but
still apply their reservation state transition and dependency completion at
that timestamp.

Wave-3 reporting accepts a `SimulationResult` plus optional existing
`ExactScheduleResult` and `SafeBound` inputs. `SimulationReport` names
`feasible_makespan`, `dependency_critical_path`, optional `exact_optimum`, and
optional `safe_bound_value` separately. It combines Event specifications from
`result.graph` with immutable ScheduleEntry witnesses and computes
demand-weighted resource-time. A measured-comparison parameter is not added
until its concrete evidence type exists; Wave 3 does not introduce an `Any`
placeholder. The report may reuse proof-layer critical-path computation but
must not re-run graph/resource validation or scheduling.

Scheduler-local topological bookkeeping has a justified `O(V + E)` cost plus priority-queue operations after it receives a validated graph. This does not describe `EventGraph` construction: current lifetime membership validation performs reachability work per member and can cost `O(M * (V + E))` for `M` lifetime members. The full multi-resource admission/placement cost is **not** claimed as `O((V+E) log V)`: blocked-event wakes, eligible-SM checks, and lifetime admission remain workload dependent. Phase 2 must time graph construction/validation, scheduling, and report assembly separately and record event/edge counts, ready-queue operations, blocked rechecks, placement checks, lifetime checks, and the historical `58,467`-Event comparison. A narrower complexity claim is accepted only after the implemented data structures and measured evidence justify it.

The following compatibility behaviors are deliberately removed rather than wrapped:

1. stream order inferred from Event iterable position;
2. scheduler-injected resource predecessors written into Event dependencies;
3. scheduled times stored on Event;
4. `critical_path` used as an alias for feasible makespan;
5. FA list interleaving used to influence lane assignment;
6. proof-layer evaluators consuming unnormalized raw Event iterables.

The independent reviewer artifact is `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-design-reviewer-revi-2026-07-19T18-37-08-457Z.md`. Claude returned `APPROVE` with four WATCH items. The primary reconciliation accepts the concept split, two-level topology, explicit compatibility breaks, and SafeBound relaxation direction. It rejects the review's DAG-only deadlock proof and total-complexity claim as written; the corrected contracts above remain WATCH until the complete Phase-1 review.

### Cache hierarchy and manifest-resolved state

The initial cache implementation is deliberately narrow: HBM backing plus one shared abstract L2. It does not claim to reproduce NVIDIA set mapping, replacement, sectoring, coherence, or request arbitration. Its purpose is to make cold/warm state, initial residency, capacity, eviction, writeback, and output visibility explicit and auditable before fixed-duration Event lowering.

```text
CacheConfig
    capacity_bytes
    manifest-defined block_bytes

InitialCacheState
    resident blocks in oldest-to-newest recency order
    dirty state per resident block

CacheAccess
    whole modeled-block read or overwrite

CacheResolution
    immutable transition records
    L2/HBM traffic totals
    final state
```

Blocks use canonical `(object_id, block_index)` identity. Most blocks have `block_bytes`; the final block of an object has its exact remaining modeled size. Capacity accounting and eviction are therefore size-aware: evict oldest blocks until the incoming modeled block fits. Duplicate blocks, inconsistent block sizes, unknown references, over-capacity initial state, and a block larger than total capacity fail at the cache boundary.

The deterministic fully associative transition is:

- read hit: update recency;
- read miss: evict until capacity, write back dirty victims, read the modeled block from HBM, and insert it clean;
- write hit: update recency and mark dirty;
- write miss: evict until capacity and insert the whole modeled block dirty without an HBM read;
- dirty eviction: write the modeled block size to HBM;
- `L2` output visibility: declared dirty output blocks may remain resident;
- `HBM` output visibility: declared dirty output blocks are flushed and become clean at completion.

A smaller final block is still a complete modeled block, so an overwrite covers the full abstract object block by definition. No read-modify-write boolean is added: such a bit would guess a physical cache-line behavior that this block abstraction explicitly does not model. Hardware-line or partial-store behavior requires separate authoritative evidence rather than defensive optional metadata.

The launch manifest supplies one total canonical CacheAccess order. Cache resolution runs once before Event lowering and produces fixed traffic/durations. Exact optimum, SafeBound, and feasible scheduling consume the same resolved EventGraph and initial state. The resulting evidence is named **manifest-order static-cache modeled evidence**. It is exact/safe only for that declared abstract fixed-duration model; it is not a lower-bound theorem over arbitrary hardware request interleavings or real Hopper L2 behavior.

No `CacheCompositionPolicy` enum or per-worker isolated alternative is introduced. The Claude review proposed isolated worker caches as “provably safe” because they overcount misses, but larger modeled traffic can increase a resource-work lower-bound term above the optimum of a shared-cache workload. That recommendation reverses the lower-bound direction and would also create two cache models across provenance layers. If future work needs schedule-dependent cache interleavings, it requires a separately proved dynamic-state model; it cannot enter through a policy switch.

Cold state is an empty `InitialCacheState`. Warm state explicitly lists resident blocks, recency, and dirty flags. Both states use the same transition rules and output boundary. Every comparison records initial/final resident bytes, hits, misses, fills, evictions, dirty writebacks, HBM read/write bytes, and L2 read/write bytes. `compute_l2_hit_ratio()` is not a cache traffic source in the new path.

### Authoritative GEMM launch manifest

`GemmLaunchManifest` is the only launch-policy source for the new GEMM path. It is validated against its declared problem (`m`, `n`, `k`, input/output element widths, accumulator width, tile policy, and output visibility) and contains ordered Workers, WorkItems, ReductionSteps, and the canonical CacheAccess order. The manifest lowers into EventGraph and ResourceLifetime; it does not own a scheduler or parallel graph representation.

A Worker contains only:

- `worker_id`;
- ordered WorkItem IDs;
- explicit CTA occupancy reservation vector;
- optional eligible SMs.

Multiple WorkItems assigned to one Worker express a persistent CTA. One WorkItem expresses an ordinary CTA. No `persistent` boolean is stored. The reservation vector is authoritative total occupancy; redundant registers-per-thread, threads-per-CTA, and derived occupancy fields are not added unless later measured metadata requires them.

A WorkItem contains:

- output-tile origin and logical M/N extents;
- explicit half-open logical K range;
- issued M/N/K extents;
- one produced accumulator ID;
- ordered input/output block accesses.

Logical K extent is derived from the range. Logical work, physical issued work, and traffic are derived rather than stored:

```text
logical_work = 2 * logical_m * logical_n * logical_k
physical_issued_work = 2 * issued_m * issued_n * issued_k
```

The issued extents must cover their logical extents and encode padding/replication explicitly. This keeps useful work separate from physical work without accepting `tensor_all_ops` as a counter.

Split-K exists only when multiple WorkItems with explicit non-overlapping K ranges produce partial accumulators for the same output tile. A ReductionStep declares input accumulator IDs, one output accumulator ID, the logical/issued element count, and ordering/dependencies. For the accepted elementwise-sum reduction, physical additions and accumulator traffic are derived from arity, issued elements, and accumulator width; separate byte totals are not stored because they would duplicate derivable facts. The final accumulator must be uniquely connected to the declared output tile and visibility boundary.

Manifest validation owns:

1. exact output-tile coverage without illegal overlap;
2. complete, non-overlapping K coverage for each output tile;
3. issued extents no smaller than logical extents;
4. unique worker membership and ordered assignment;
5. accumulator single production, acyclic use, no orphan partials, and one final result per output tile;
6. reduction arity/work/traffic conservation;
7. block-access references and canonical total order;
8. reservation capacity and eligible-SM validity.

Required rejection cases include a K gap, overlapping K ranges, duplicate accumulator producers, orphan accumulators, reduction inputs with incompatible tile/element counts, overlapping non-split output tiles, missing final reduction, and worker assignment duplication. Dataset rows without an authoritative manifest are rejected with a counted reason. `is_split_k`, CTA/base-grid ratios, legacy floor division, shape guesses, or silent non-split substitution are prohibited.

The focused independent artifact is `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-architecture-reviewe-2026-07-19T18-46-20-917Z.md`. Claude returned `WATCH`. The primary reconciliation accepts the static-model naming boundary, size-aware LRU, explicit initial recency/dirty state, manifest conservation cases, accumulator width, total problem shape, and output visibility. It rejects the proposed physical partial-block read bit, redundant low-level occupancy fields, and the isolated-cache SafeBound policy. The corrected single-model contract remains WATCH until the final Phase-1 review.

### Calibration and held-out evaluation separation

The numeric consumer remains one `PrimitiveCalibration`; provenance is not hidden inside alternate scheduler models. Two evidence sources may construct it, and every result records which source was used:

```text
Specification calibration
    deterministic conversion from versioned hardware peak-rate fields

Measured primitive calibration
    empirical duration-per-unit coefficients from versioned primitive-only
    microbenchmarks and counters
```

Specification calibration is the only calibration allowed in the zero-shot folds. It may support a theorem over the resulting declared fixed-duration model, but neither the hardware JSON nor that theorem proves a real-hardware bound. Measured primitive calibration is an explicitly empirical input to feasible scheduling and measured comparison. A theorem remains valid over its fixed numeric Event model, but finite primitive measurements do not certify that the coefficients lower-bound every future physical execution.

Measured calibration uses no complete-operator latency, residual correction, clamp, or target-output fit. Each primitive benchmark executes a known quantity repeatedly within a controlled timing region. Calibration IDs and evaluation IDs are disjoint before collection. For each primitive, the manifest records raw elapsed time and quantity, the per-unit samples, the selected median coefficient, p05/p95, warmup/repeat counts, counters when available, and environment identity. Launch and other fixed costs use their own repeated controls rather than being redistributed across throughput coefficients. Invalid, missing, non-finite, or non-positive required measurements abort the campaign.

The held-out protocol has two non-interchangeable studies:

1. **Within-Hopper zero-shot:** four fixed leave-one-hardware-out folds over H100, H20, H200, and H800. The target fold may use its versioned hardware specification and authoritative explicit launch manifest, but no target primitive measurement, operator latency, threshold selection, unsupported-row rule change, or model decision. Target latency is read only for the final scoring pass after the prediction artifact and its hash exist.
2. **Measured-primitive-calibrated audit:** may use target primitive measurements from the disjoint calibration set, but remains explicitly non-zero-shot. Held-out primitive sizes and complete-operator rows are evaluation-only.

Cross-architecture zero-shot is a third, separately named evidence tier. Ampere, Ada, or Blackwell results are produced only when authoritative manifests yield nonzero support. No CTA-ratio or split-K heuristic may manufacture coverage. Each tier reports total, supported, unsupported-by-reason, and violation counts; unsupported rows remain in the denominator.

### Universal modeled-bound theorem

Let `G` be any non-empty finite normalized acyclic EventGraph after manifest-order cache resolution. Every Event `e` has fixed finite duration `d(e) >= 0`, explicit predecessors, non-negative integer chip-global demand `g(e, r)`, and non-negative integer transient per-SM demand `s(e, r)`. Let every declared global capacity `C_g(r)` and per-SM capacity `C_s(r)` be a positive integer, with a positive integer SM count `S`. A feasible schedule is non-preemptive, respects half-open intervals `[start, end)`, precedence, atomic global/per-SM admission, and one-SM co-location of each Event's per-SM vector.

Define:

```text
dependency_critical_path
    = maximum sum of d(e) over any dependency path

global_resource_term[r]
    = sum(d(e) * g(e, r)) / C_g(r)

aggregate_per_sm_term[r]
    = sum(d(e) * s(e, r)) / (S * C_s(r))

SafeBound
    = max(dependency_critical_path,
          every global_resource_term,
          every aggregate_per_sm_term)
```

For every feasible schedule, a dependency path is serialized, each global resource supplies at most `C_g(r) * makespan` resource-time, and the SM pool supplies at most `S * C_s(r) * makespan` resource-time. Therefore every term is no greater than the modeled optimum and their maximum is also no greater than that optimum. Simultaneous multi-resource demand does not invalidate any individual capacity inequality.

Affinity and `ResourceLifetime` reservations are handled only by relaxation in the first scalable theorem: their constraints and reserved occupancy are omitted, while fixed Event durations and transient demands remain unchanged. Removing constraints cannot increase the relaxed optimum, so the bound remains safe for the original modeled instance. The result must state that no affinity- or lifetime-aware tightening was computed. A future term that counts schedule-dependent reservation duration requires a separate proof and is not part of the initial implementation.

This theorem is universal only over the exact model quantified above and the one declared manifest-order cache resolution. It is not a theorem over NVIDIA cache arbitration, warp issue, dynamic frequency, undocumented launch policy, measurement noise, or all physical GPU executions. Real hardware receives a finite matched audit. The four historical actual/DES pairs `10.472800/11.358228`, `10.619200/11.324017`, `8.213200/10.016648`, and `10.056400/10.243910` microseconds remain visible until root-cause-matched evidence resolves them; they may not be clamped, scaled, or skipped.

### Cycle-level comparator decision

The source-backed candidate is Accel-Sim Framework plus its GPGPU-Sim detailed performance model. Official upstream evidence at framework commit `3016c658f810bdae9a14bf4534ee99e9945eedae` states that the trace-driven front end consumes SASS traces and feeds GPGPU-Sim 4.x, and also documents a PTX-mode run path. Its standard configuration file includes `A100` backed by `configs/tested-cfgs/SM80_A100/gpgpusim.config`; that configuration declares compute capability `8.0`, `108` clusters, tensor-core units, L1/L2, interconnect, and DRAM timing. No standard H100/Hopper configuration was found. Upstream is BSD-2-Clause.

The user approved the dependency and pinned CUDA/`nvcc` environment. The initial matched benchmark domain is therefore a small deterministic **A100** synthetic GEMM whose source, PTX mode, launch dimensions, tile/K policy, datatype, output boundary, cache state, Accel-Sim commit/submodule revision, A100 configuration, and host timing command are versioned together. The same manifest is lowered into DES. The report records:

- DES and comparator modeled operations/bytes/CTA count;
- comparator simulated cycles and converted time using the pinned clock;
- DES predicted time;
- DES host runtime and Accel-Sim host runtime;
- absolute/relative latency delta;
- absolute speed ratio;
- build/simulation commands and exit codes.

This benchmark supports only the named A100 synthetic workload and runtime ratio. It does not validate Hopper, measured hardware, cache-policy equivalence, or the broad `10000x` claim unless the measured ratio actually reaches that value. Pre-traced assets are not assumed: the upstream trace-summary URL currently redirects to a missing page, and the local host has no comparator binary, trace, config checkout, `nvcc`, or approved build environment.

Accel-Sim/GPGPU-Sim is an approved new external dependency. It is provisioned only in Phase 2 after the Phase-1 checkpoint is committed and pushed. `nsys` remains an unacceptable substitute.

Focused StepCode Claude review artifact `.omx/artifacts/claude-you-are-the-independent-stepcode-claude-reviewer-for-one-irr-2026-07-19T18-57-46-477Z.md` returned `APPROVE` with WATCH. It supports the synthetic A100 manifest and recommends the precise label **GPGPU-Sim cycle-level PTX-mode comparison**, not strict cycle-accurate A100 hardware equivalence. The primary reconciliation accepts that naming and scope but rejects the review's statement that missing `nvcc` is irrelevant: the official GPGPU-Sim README requires a CUDA Toolkit, CUDA headers/math support, and an `nvcc`-compiled dynamically linked CUDA application for the documented PTX path. The dependency approval therefore covers a pinned CUDA/compiler/build environment as well as simulator source.

## Preliminary StepCode Claude Review Disposition

Artifact:

```text
.omx/artifacts/claude-you-are-the-independent-stepcode-claude-architecture-scienti-2026-07-19T17-58-35-661Z.md
```

Claude returned **WATCH** for continuing Phase 1 and supported Option A: separate exact oracle, scalable safe bound, feasible scheduler, and measured comparison.

Accepted review points:

- general resource-constrained DAG scheduling requires a bounded exact oracle plus a scalable analytical path;
- the exact oracle and analytical evaluator need distinct result/failure contracts;
- critical-path and resource-time/capacity terms are the minimal scalable candidates;
- stream-order semantics must be resolved before a permutation-invariant proof path;
- modeled theorem, Hopper-only evidence, cross-architecture zero-shot, measured calibration, and real-hardware claims remain separate labels.

Recommendations not accepted as design decisions:

- Adding OR-Tools is not approved; new dependencies require an explicit decision and verified environment.
- Suggested limits such as `500` events or `60s` were unsupported guesses and are not contracts.
- A mutable `dict` inside a frozen `SafeBound` is not an accepted evidence representation.
- The cited `4/3 - 1/(3m)` scheduler guarantee was conflated with a different scheduling setting and provides no accepted guarantee for the proposed precedence-constrained policy.
- The statement that a cold-cache traffic term is still safe for warm state was rejected; state contracts must match.
- The suggestion to defer requested R6/R7/R9 work was rejected because it would shrink the user's active objective. External prerequisites must remain visible, not be removed from scope.
