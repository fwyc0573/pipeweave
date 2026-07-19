# DES Full Semantics and Scientific Validation Requirements

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Captured the user's approval of Option A for the pinned Accel-Sim/GPGPU-Sim comparator and CUDA/`nvcc` build environment. |
| 2026-07-20 | Captured the user's follow-up selection of Option A as four separate provenance/result layers. |
| 2026-07-20 | Captured the user's raw two-phase objective, twelve requested outcomes, inherited contracts, review requirements, and ignored-path boundary. |

## Original Requests

1. **[Original Request]** Create a separate task directory under `task_memory/` for this next stage.
2. **[Original Request]** Complete the task in two stages: `plan + discuss + design`, followed by `implement + eval`.
3. **[Original Request]** Design and complete an exact bound for resource-constrained workloads.
4. **[Original Request]** Design and complete an order-invariant bound for dependency DAGs.
5. **[Original Request]** Rewrite or optimize the scheduler.
6. **[Original Request]** Model cache hierarchy, warm-L2 behavior, and initial residency.
7. **[Original Request]** Model CTA lifetime, simultaneous multi-resource demand, and SM/lane affinity.
8. **[Original Request]** Model persistent CTA execution.
9. **[Original Request]** Model split-K replicated work and reduction.
10. **[Original Request]** Define and implement partial-tile semantics.
11. **[Original Request]** Provide a cycle-accurate benchmark.
12. **[Original Request]** Provide a multi-hardware held-out zero-shot study.
13. **[Original Request]** Provide measured-hardware bound calibration.
14. **[Original Request]** Establish the requested universal lower-bound claim.
15. **[Original Request]** Keep every boundary consistent with `task_memory/task_2026-07-18_des_refined_roofline_review/design.md` and `task_memory/task_2026-07-18_des_refined_roofline_review/harness.md`.
16. **[Original Request]** Use independent `ask Claude` review after important code-module milestones and at phase-review checkpoints.
17. **[Original Request]** Avoid over-defensive implementation and redundant modules; keep implementation and tests tightly centered on the inherited `design.md` and `harness.md` contracts.
18. **[Original Request]** Ignore the historical path named `=10.1`; do not inspect, create, delete, move, modify, stage, or treat it as a blocker.
19. **[Original Request]** Organize, commit, and push the prior branch checkpoint before entering this next stage.

## Discussion Decisions

1. **[Original Request]** The user selected Option A: provide the exact modeled optimum, scalable order-invariant analytical lower bound, deterministic feasible schedule, and measured-hardware comparison as four separate result/evidence layers rather than treating any one as an implicit substitute for another.
2. **[Original Request]** The user selected comparator Option A: approve introduction of a version-pinned Accel-Sim/GPGPU-Sim dependency together with a pinned CUDA/`nvcc` build environment for the matched A100 cycle-level PTX-mode comparison. The approval does not authorize broader Hopper, silicon-equivalence, or `10000x` claims without measured evidence.

Each later accepted discussion answer will be added here as a separate **[Original Request]** follow-up before implementation planning is finalized.
