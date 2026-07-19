# DES Refined Roofline Review and Remediation Notes

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Recorded the fresh pre-commit verification stack and exact numeric metrics after Claude approval. |
| 2026-07-19 | Applied the user-directed ignored-path boundary and prepared the branch delivery/next-stage handoff. |
| 2026-07-19 | Recorded the final post-document verification timings and exit-code evidence from session `97006`. |
| 2026-07-19 | Recorded the historical resume-audit metrics; the later user instruction supersedes its path-preservation check. |
| 2026-07-18 | Recorded post-fix independent review results, evidence interpretation constraints, and final execution reminders. |
| 2026-07-18 | Recorded deterministic matched-DES sample results and scheduler-scaling measurements. |
| 2026-07-18 | Recorded baseline environment, dataset coverage, repository evidence boundaries, and timing-command constraint. |
| 2026-07-18 | Created operational constraints and the initial evidence-source register. |

## Operational Context

- Worktree: `/data/ycfeng/pipeweave/.worktrees/des`.
- Branch: `des`.
- The repository is already a linked worktree; no nested worktree is required.
- The completed documentation-backfill task and this remediation remain uncommitted until the explicit branch checkpoint. The historical `=10.1` path is ignored by user instruction and is excluded from validation/staging; do not inspect or perform any filesystem operation on it.
- Read `task_memory/env_handbook.md` before handling environment failures.
- The first Claude metric review artifact is `.omx/artifacts/claude-you-are-the-first-independent-reviewer-for-a-des-refined-roo-2026-07-18T14-45-05-448Z.md`.
- Environment: no active conda environment; `/usr/bin/python` is Python `3.12.3`, pytest `9.1.1`, pandas `3.0.3`, and numpy `2.4.6`.
- GNU `/usr/bin/time` is absent. Use the verified Bash `time` recipe in `task_memory/env_handbook.md`.
- Set `PYTHONPATH="$PWD"` for direct validation scripts; pytest from the repository root imports the local package correctly.

## Initial Evidence Sources

- `README.md`
- `docs/event_simulator_design.md`
- `docs/des_design_rules.md`
- `event_simulator/`
- `tests/unit/`, `tests/integration/`, and `tests/validation/`
- `aggregator.py` and legacy analytical/ML predictor modules
- `hardware/*.json`
- `dataset/gemm_test.csv` and FlashAttention measurement data
- completed task `task_memory/task_2026-07-18_des_event_simulator_docs_backfill/`

## Evidence Inventory

- `dataset/gemm_test.csv`: `118,800` rows across `11` hardware names and includes `tile_M`, `tile_N`, and `tile_K`.
- `dataset/fa3_benchmark_h800.csv`: `2` H800-only measured rows.
- `dataset/gemm_train.csv`: Git LFS pointer content in this worktree, not the materialized training table.
- `e2e/*.csv`: legacy PipeWeave/roofline/Habitat/NeuSight/vLLM comparisons; they are not DES Event IR validation artifacts.
- No repository file identifies a matched cycle-accurate simulator runtime benchmark for DES.
- H100 raw hardware values used by DES: `numSms=132`, `tcBf16=4096 ops/cycle/SM`, `smFreq=1830 MHz`, `memBandwidth=3352.32 GB/s`, `l2CacheBandwidth=8820 GB/s`.

## Corrected Classical Roofline Audit

Using all `10,800` positive H100 rows and `chip_peak = 4096 * 1830 * 132 = 989,429,760 FLOPs/us`:

| Category | Rows | Bound Violations | Mean Actual (us) | Mean Bound (us) | Mean Gap | Median Gap |
|---|---:|---:|---:|---:|---:|---:|
| All | 10,800 | 160 (1.481481%) | 513.498840 | 423.317660 | 0.340438211 | 0.266873391 |
| Large | 4,231 | 0 (0%) | 1,205.750795 | 1,000.886758 | 0.213733935 | 0.194005585 |
| Medium | 1,798 | 0 (0%) | 25.994158 | 16.019065 | 0.495233493 | 0.474933850 |
| Small | 3,562 | 160 (4.491859%) | 63.302788 | 51.990033 | 0.392593362 | 0.333049712 |

The existing invalid compute formula reported a Large mean gap of `0.765382219` instead of `0.213733935`. The `160` small-row violations are memory-bound in both formulas and require a separate cache-residency/measurement-boundary analysis; they must not be hidden or mixed into accepted lower-bound metrics.

## Scheduler Workload Shape

H100 CTA-count distribution (`ceil(M/tile_M) * ceil(N/tile_N)`):

| Category | Min | Median | P95 | P99 | Max |
|---|---:|---:|---:|---:|---:|
| Large | 108 | 1,056 | 12,936 | 19,488 | 29,369 |
| Medium | 36 | 126 | 224 | 259 | 1,188 |
| Small | 10 | 84 | 396 | 792 | 1,188 |

This distribution explains why the current approximately quadratic scheduler makes the official `200`-row Large validation sweep impractical.

## Deterministic Matched DES Sample

The review selected H100 rows with `ceil(M/tile_M) * ceil(N/tile_N) <= 512` and then sampled `500` rows deterministically by original row index. The corrected classical bound used chip-wide BF16 throughput and conventional `A+B+C` BF16 traffic.

| Metric | Observed Value |
|---|---:|
| Evaluated rows | 500 |
| DES bound violations | 5 (1.0%) |
| Corrected classical violations | 9 (1.8%) |
| DES tighter than corrected classical | 206 |
| DES looser than corrected classical | 294 |
| Both bounds valid | 491 |
| DES tighter among both-valid rows | 206 |
| DES looser among both-valid rows | 285 |
| Mean DES gap | 44.8348% |
| Mean corrected-classical gap | 41.1596% |
| Median DES gap | 40.4518% |
| Median corrected-classical gap | 37.1834% |
| Sampling wall time | 10.7324 s |

This bounded-CTA sample is not a population estimate, but its counterexamples are sufficient to reject an unrestricted global tighter-than-roofline or universal-lower-bound claim.

For the narrower large compute-bound regime (`M,N,K >= 1024`, at most `1024` DES CTAs), a deterministic `40`-row sample had `0/40` violations for both bounds and DES was tighter on `40/40` rows. Mean DES gap was `21.9493%`; mean corrected-classical gap was `25.5221%`. This is positive sample evidence only, not full acceptance.

## Scheduler Scaling Measurement

Three runs per point, median wall-clock time:

| CTAs | Events | Median Scheduler Time (s) |
|---:|---:|---:|
| 128 | 387 | 0.014082 |
| 256 | 771 | 0.034505 |
| 512 | 1,539 | 0.090736 |
| 1,024 | 3,075 | 0.280886 |
| 2,048 | 6,147 | 1.038378 |

The final event-count doubling increased runtime by approximately `3.70x`, corresponding to a local scaling exponent of approximately `1.89`.

## Matched 20-Row-Per-Category DES Audit

The audit used H100, `random_state=42`, dataset `tile_K`, the dimensionally corrected classical roofline, and measured lowering-plus-scheduling wall time. No rows were skipped.

| Category | Rows | DES Violations | Roofline Violations | DES Tighter Rows | Mean Actual (us) | Mean DES (us) | Mean Roofline (us) | Mean DES Gap | Mean Roofline Gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Large | 20 | 0 | 0 | 20 | 906.176420 | 764.793404 | 752.490591 | 0.197045175 | 0.215868948 |
| Medium | 20 | 0 | 0 | 16 | 17.611150 | 11.427687 | 10.580632 | 0.435736262 | 0.474754693 |
| Small | 20 | 0 | 0 | 0 | 95.850450 | 78.682559 | 80.760871 | 0.521417339 | 0.349757136 |

Runtime evidence:

| Category | Mean Runtime (s) | Median Runtime (s) | P95 Runtime (s) | Max Runtime (s) | Mean Events | Max Events |
|---|---:|---:|---:|---:|---:|---:|
| Large | 8.079464427 | 0.307063607 | 21.208354107 | 115.882818766 | 8,325.6 | 58,467 |
| Medium | 0.015358914 | 0.015623670 | 0.016429490 | 0.016614872 | 371.1 | 399 |
| Small | 0.018262359 | 0.011416614 | 0.068955441 | 0.069269140 | 391.65 | 1,191 |

Interpretation: the sampled Large mean gap is `1.882377275` percentage points tighter than classical (`21.586894783% - 19.704517508%`), and Medium is `3.901843071` points tighter on average, but the improvement is not universal. Small is `17.166020305` points looser. Therefore the honest current statement is category- and sample-scoped, not a general proof that DES is always tighter.

## Launch-Metadata and Structural Diagnostics

- H100 `cta_count` mismatch definition: `dataset.cta_count != ceil(M/tile_M) * ceil(N/tile_N)`.
- Overall mismatch: `6,554/10,800 = 60.685185%`.
- Large mismatch: `3,788/4,231 = 89.529662%`; Medium: `414/1,798 = 23.025584%`; Small: `1,454/3,562 = 40.819764%`.
- All split-K rows mismatch: `437/437`; `is_split_k` is not consumed by GEMM v2.
- L2 store resource represented aggregate rate: `132 / GlobalStore_us_per_byte = 442,506,240 B/us`, versus declared chip-wide L2 `8,820,000 B/us`, a `50.170775510204x` excess.
- `4096^3` effective B traffic: unique `33,554,432 B`, modeled `1,048,576 B`, ratio `0.03125`.
- Partial-tile probe: `M=128 -> 129`, `N=128`, `K=4096`, tile `128x128` adds one `MMA_PartialTile` (`4,096` instructions, `0.139890710 us`) but makespan remains exactly `17.915785652139 us` because the partial CTA overlaps the full CTA on another tensor-core lane.

## Execution Reminders

- Facts must be retrieved from code or measurements rather than asked from the user.
- Material design choices are presented one at a time.
- Every fix record in `progress.md` must contain Motivation, Expectation, Method, and Result.
- No comparison claim is accepted when the baseline uses inconsistent hardware units or unmatched workloads.
- The final native reviewer independently observed `92/92` targeted and `130/130` full tests before the final FA3 high-branch test was added; the authoring lane must run a newer full suite and report its actual count.
- StepCode Claude's post-fix artifact is `.omx/artifacts/claude-you-are-the-post-fix-independent-scientific-code-reviewer-fo-2026-07-18T15-54-47-545Z.md` with verdict `APPROVE with WATCH`.
- Do not repeat Claude's unsupported causal wording that Small violations prove warm-L2 residency. The evidence establishes an unmatched contract, not one isolated root cause.
- FA2 `cta_kv=64` remains an explicitly Experimental simplification; no empirical fallback is permitted.
- The final formal report must include absolute actual/DES/classical time scales, all four Small violations, and supported/unsupported denominators.

## Resume Audit (2026-07-19)

- Fresh targeted suite: `93/93` passed; pytest `8.52s`, shell elapsed `9.741s`.
- Fresh full suite: `131/131` passed; pytest `2.76s`, shell elapsed `3.225s`.
- Fresh compilation: exit `0`, shell elapsed `0.265s`.
- Fresh H100 validator: exit `0`, shell elapsed `3.618s`; deterministic supported-row and Small-violation counts remain those recorded in the formal report.
- Fresh hardware smoke: `11/11` hardware files, `22` calibration coefficients and `5/5` known operator configs per file; GEMM/GEMM-v2 use one L2 lane.
- `git diff --check`: exit `0`.
- Historical `=10.1` path: explicitly ignored and outside scope; no existence check or filesystem operation is part of this task. See issue `R-027`.

## Final Post-Document Verification (2026-07-19)

- The final verification session (`97006`) ran after the task documents were reconciled. Targeted tests passed `93/93` with pytest time `2.63s`, shell elapsed `3.088s`, user `4.996s`, and system `0.169s`.
- The full suite passed `131/131` with pytest time `2.65s`, shell elapsed `3.118s`, user `4.739s`, and system `0.116s`.
- `compileall` exited `0` in `0.046s` (user `0.042s`, system `0.004s`).
- The H100 validator exited `0` in `3.401s` (user `5.322s`, system `0.080s`); the deterministic output still reports `4,231` Large, `1,798` Medium, `3,562` Small, and `1,209` Other rows, with four Small DES violations.
- The cross-hardware smoke passed `11/11` hardware files, with `22` calibration coefficients and `5` known operator configurations per file. `git diff --check` exited `0`.
- The checksum check passed all `28/28` entries after the final artifact update. The historical `=10.1` path remains explicitly excluded by user instruction; no existence check or filesystem operation was performed for delivery.

## Pre-commit Verification (2026-07-19)

- Targeted tests: `93/93` passed; pytest `2.66s`, shell elapsed `3.108s`, user `5.032s`, system `0.096s`.
- Full tests: `131/131` passed; pytest `2.77s`, shell elapsed `3.218s`, user `4.807s`, system `0.170s`.
- Compilation: exit `0`, elapsed `0.046s`, user `0.037s`, system `0.008s`.
- H100 validator: exit `0`, elapsed `3.461s`, user `5.328s`, system `0.107s`; `4,246/10,800` supported policy rows and four sampled Small violations remain visible.
- Hardware smoke: `11/11` files, `22` calibration coefficients and `5` known operator configurations per file; GEMM/GEMM-v2 use one L2 lane.
- Checksums: `28/28` entries passed; `git diff --check` exit `0`.
- The historical `=10.1` path is excluded by user instruction and was not inspected or staged.
