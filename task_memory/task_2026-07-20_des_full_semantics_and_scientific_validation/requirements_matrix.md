# DES Full Semantics and Scientific Validation Requirements Matrix

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Updated Phase-1 decisions for exact engine, shared semantics, comparator approval, held-out protocol, calibration separation, and theorem quantifiers. |
| 2026-07-20 | Corrected partial-tile evidence from presumed counters to legacy analytical features and restored measured-counter collection as a separate requirement. |
| 2026-07-20 | Recorded the accepted Option A provenance split and the dataset evidence blocking heuristic split-factor inference. |
| 2026-07-20 | Added exact-oracle certificate, formulation, dependency, and tiny-case cross-validation evidence requirements. |
| 2026-07-20 | Added quantified Hopper-only coverage and explicit external prerequisites for cycle-accurate and measured-calibration outcomes. |
| 2026-07-20 | Mapped all twelve requested outcomes to current evidence, required proof/evaluation, and blocking decisions. |

| ID | Requested outcome | Current authoritative state | Required completion evidence | Current status |
|---|---|---|---|---|
| R1 | Resource-constrained exact bound | Option A and a dependency-free exhaustive serial-SGS engine are selected for the declared finite fixed-duration renewable-resource domain | Complete-search implementation, independent bounded time-grid cross-check, permutation tests, budget-exhaustion behavior, and measured search/runtime evidence | DESIGN COMPLETE; implementation UNPROVEN |
| R2 | Order-invariant dependency-DAG bound | Current scheduler is order-sensitive (`21.0` vs `11.0`) | Proven DAG bound, permutation/property tests, comparison with exact oracle | UNPROVEN |
| R3 | Scheduler rewrite/optimization | Caller-order greedy scan; historical near-quadratic scaling | Feasibility tests, deterministic policy tests, before/after runtime across graph sizes, no semantic regression | UNPROVEN |
| R4 | Cache hierarchy, warm L2, initial residency | One manifest-order abstract HBM+L2, size-aware LRU, explicit initial state, and output-visibility contract is frozen | State/transition/eviction implementation, traffic conservation, cold/warm/residency tests, matched measured study | DESIGN COMPLETE; implementation UNPROVEN |
| R5 | CTA lifetime, multi-resource demand, affinity | One normalized EventGraph/ResourceLifetime/two-level ResourceConfig contract and no-hold-and-wait rule are frozen | Atomic admission/lifetime/affinity implementation, impossibility/deadlock counterexamples, unit and integration tests | DESIGN COMPLETE; implementation UNPROVEN |
| R6 | Persistent CTA | Multiple ordered WorkItems per explicit Worker plus one ResourceLifetime is the sole persistent representation | Conserved assignment lowering, lifetime scheduling, matched CTA/worker tests | DESIGN COMPLETE; implementation UNPROVEN |
| R7 | Split-K replicated work/reduction | Explicit K partitions and accumulator reduction topology are required; heuristic recovery is prohibited | Authoritative manifests, replication/reduction compute and traffic semantics, launch matching, targeted/e2e tests | DESIGN COMPLETE; implementation UNPROVEN |
| R8 | Partial-tile semantics | Logical and issued extents derive separate useful and physical work; legacy analytical and measured-counter quantities remain separate | Boundary/tail implementation tests, report/bound conservation, authoritative policy and counter provenance | DESIGN COMPLETE; implementation UNPROVEN |
| R9 | Cycle-accurate benchmark | User approved pinned Accel-Sim/GPGPU-Sim and CUDA/`nvcc`; official A100 config and synthetic PTX-mode boundary are selected | Verified source/submodule/config/toolchain hashes, same manifest/boundary, raw cycle/time and host-runtime samples | DESIGN/DEPENDENCY APPROVED; implementation UNPROVEN |
| R10 | Multi-hardware held-out zero-shot | Four within-Hopper leave-one-hardware-out folds are frozen; cross-architecture evidence requires nonzero authoritative-manifest support | No-target-fitting run, per-hardware absolute metrics/violations/unsupported counts; separate cross-architecture run after manifest support | DESIGN COMPLETE; evaluation UNPROVEN |
| R11 | Measured-hardware calibration | Primitive-only empirical calibration is separated from specification calibration and zero-shot; complete-operator fitting is prohibited | Controlled versioned campaign, disjoint primitive calibration/evaluation IDs, counters, uncertainty, matched non-zero-shot audit | DESIGN COMPLETE; evaluation UNPROVEN |
| R12 | Universal lower-bound claim | Quantifiers are limited to the declared normalized fixed-duration manifest-order model; real hardware is a separate finite audit with four known historical violations | Proof for every term/relaxation, exact-oracle cross-checks, property tests, and complete measured violation table | DESIGN COMPLETE; implementation/evaluation UNPROVEN |
