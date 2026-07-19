# Test Report: DES Wave-3 Scheduler, Report, and Scaling Benchmark

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Recorded the exact 25-path staging audit, ignored/OMX exclusions, and 40-entry checksum verification. |
| 2026-07-20 | Added the CSV LF-line-ending RED/GREEN root-cause fix, normalized raw-artifact hash, and 205-case final regression. |
| 2026-07-20 | Refreshed the final pre-delivery regression and static-audit evidence after the historical-denominator wording correction. |
| 2026-07-20 | Recorded Wave-3 RED/GREEN, the complete historical-size benchmark, SafeBound correction evidence, independent review, and fresh regression. |

**Date:** 2026-07-20
**Working directory:** `/data/ycfeng/pipeweave/.worktrees/des`
**Branch:** `des`
**Baseline SHA before Wave-3 delivery:** `126187c37d29ad6197b9cd89b85809f7badbb2ac`

## 1. Test Script Information

### Environment

| Item | Actual value |
|---|---|
| Python | `3.12.3` |
| Python executable | `/usr/bin/python` |
| pytest | `9.1.1` |
| Active conda environment | none |
| Active virtual environment | none |
| Import root | `PYTHONPATH=/data/ycfeng/pipeweave/.worktrees/des` |
| Cache policy | `PYTHONDONTWRITEBYTECODE=1`; pytest `-p no:cacheprovider` |
| Timing implementation | Bash `time` with `TIMEFORMAT`; GNU `/usr/bin/time` is unavailable |

### Scripts and Modules

- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_event_graph.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_resource_semantics.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_exact_oracle.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_safe_bound.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_safe_bound_permutation_properties.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_safe_bound_conservation_properties.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_event_scheduler.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_report.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_benchmark_event_scheduler.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_bound_oracle_scheduler.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/performance/benchmark_event_scheduler.py`
- Raw benchmark output: `/data/ycfeng/pipeweave/.worktrees/des/task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/wave3_scheduler_benchmark.csv`

### Reproducible Commands

#### Benchmark API RED

```bash
TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider \
  tests/unit/test_benchmark_event_scheduler.py -q
```

The RED command was executed before `tests/performance/benchmark_event_scheduler.py` existed.

#### Benchmark API GREEN

```bash
TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider \
  tests/unit/test_benchmark_event_scheduler.py -q
```

#### Complete Scaling Benchmark

```bash
set -o pipefail
TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python tests/performance/benchmark_event_scheduler.py \
  | tee task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/wave3_scheduler_benchmark.csv
```

#### Fresh Wave-1--3 Regression

```bash
TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider \
  tests/unit/test_event_graph.py \
  tests/unit/test_resource_semantics.py \
  tests/unit/test_exact_oracle.py \
  tests/unit/test_safe_bound.py \
  tests/unit/test_safe_bound_permutation_properties.py \
  tests/unit/test_safe_bound_conservation_properties.py \
  tests/unit/test_event_scheduler.py \
  tests/unit/test_report.py \
  tests/unit/test_benchmark_event_scheduler.py \
  tests/integration/test_bound_oracle_scheduler.py \
  -q
```

## 2. Validation Criteria

1. Benchmark tests must be observed RED before the benchmark module exists, then GREEN after the minimal implementation.
2. Historical sizes must be exactly `387`, `771`, `1,539`, `3,075`, `6,147`, and `58,467` Events with `sm_count=132`.
3. Every benchmark row must report all 18 frozen fields: Event/edge/resource counts; graph, scheduler, and report time; four scheduler counters; old/new runtime and ratio; makespan; exact result/gap when available; feasibility violations; and determinism mismatches.
4. Graph construction/validation, scheduling, and report assembly must be timed separately. `new_runtime_seconds` must equal their sum.
5. The six-Event one-CTA case must return feasible makespan `3.5`, exact optimum `3.5`, and relative optimality gap `0.0`.
6. Every returned benchmark schedule must have `feasibility_violation_count=0` and `determinism_mismatch_count=0`.
7. The lifetime-covered SafeBound regression must retain aggregate covered-slot term `0.0`; the feasible makespan and SafeBound must both be `1.0`; the additional transient `alu` term must remain `4.0` in its focused case.
8. All Wave-1--3 unit/property/integration tests must pass with zero failures and zero collection errors.
9. No measured scheduler runtime may be labeled a cycle-level comparator result or evidence of `10000x` speedup.
10. Independent StepCode Claude review must return `APPROVE` or a documented non-blocking `WATCH`; `BLOCK` would stop delivery.
11. Authoritative benchmark CSV output must use LF line endings so the generated artifact passes the repository whitespace/diff gate on this Linux environment.

## 3. Test Results and Evidence

### Outcome Summary

| Validation | Expected | Actual | Result |
|---|---:|---:|---|
| Benchmark RED | Failure caused only by absent benchmark module | `11 failed`; all failures were `ModuleNotFoundError`; pytest `0.82s`; wrapper `1.199s`; exit `1` | PASS |
| Benchmark GREEN | `11/11` pass | `11/11` passed; pytest `0.78s`; wrapper `1.173s`; exit `0` | PASS |
| CSV newline RED | Detect default CRLF output | `1/1` failed because `"\r"` was present; pytest `0.87s`; exit `1` | PASS |
| CSV newline GREEN | Explicit LF output | benchmark module `12/12` passed; pytest `0.78s`; wrapper `1.157s`; exit `0` | PASS |
| Wave-1--3 regression | All pass | `205/205` passed; pytest `1.34s`; wrapper `1.797s`; user `1.598s`; system `0.060s`; exit `0` | PASS |
| Benchmark rows | one exact row plus six historical rows | `7/7` rows completed; maximum `58,467` Events | PASS |
| Benchmark integrity | zero feasibility/determinism failures | `0` feasibility violations and `0` determinism mismatches on every row | PASS |
| Post-fix independent review | no `BLOCK` | StepCode Claude `APPROVE`; zero mandatory code corrections; one low provenance WATCH | PASS |

### Benchmark Phase Timings and Results

`new_runtime_seconds` is the primary prediction pipeline:

```text
graph construction/validation + schedule + report
```

It excludes the small exact-oracle cross-check, the independent feasibility audit, and the second reversed-input determinism schedule. Those are validation work, not the production prediction path. The full command took `49.918s`; the largest primary pipeline took `24.404565954988s`.

| Events | Edges | Resources | Graph build (s) | Schedule (s) | Report (s) | New pipeline (s) | Legacy scheduler (s) | New - legacy (s) | Legacy / new | Makespan | Exact | Relative gap |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 | 6 | 5 | 0.000167946011 | 0.000153045985 | 0.000077720993 | 0.000398712989 | N/A | N/A | N/A | 3.5 | 3.5 | 0.0 |
| 387 | 514 | 5 | 0.004997962998 | 0.016227167012 | 0.002473911998 | 0.023699042009 | 0.014082000000 | +0.009617042009 | 0.594201233732 | 3.5 | N/A | N/A |
| 771 | 1,026 | 5 | 0.007796467020 | 0.033519179007 | 0.005000823992 | 0.046316470020 | 0.034505000000 | +0.011811470020 | 0.744983371692 | 5.5 | N/A | N/A |
| 1,539 | 2,050 | 5 | 0.015810890007 | 0.078728923982 | 0.010293867992 | 0.104833681980 | 0.090736000000 | +0.014097681980 | 0.865523353620 | 9.5 | N/A | N/A |
| 3,075 | 4,098 | 5 | 0.032626621978 | 0.169271833001 | 0.031407553004 | 0.233306007984 | 0.280886000000 | -0.047579992016 | 1.203938134417 | 17.5 | N/A | N/A |
| 6,147 | 8,194 | 5 | 0.063724503008 | 0.439431876992 | 0.043557094992 | 0.546713474992 | 1.038378000000 | -0.491664525008 | 1.899309322885 | 33.5 | N/A | N/A |
| 58,467 | 77,954 | 5 | 0.720789447980 | 23.005453476013 | 0.678323030996 | 24.404565954988 | 115.882818766000 | -91.478252811012 | 4.748407284921 | 297.5 | N/A | N/A |

Positive `New - legacy` means the new measured pipeline took longer at that size point; negative means it took less time. The parent source names the first five old values as scheduler-time medians, while the new denominator includes graph construction/validation, scheduling, and report assembly. Therefore these ratios are size-matched historical context, not a stage-matched speedup study. They are also not summarized as a universal improvement because the three smallest ratios are below `1.0`.

### Scheduler Operation Counters

| Events | Ready-queue operations | Blocked-ready rechecks | Placement checks | Lifetime checks | Feasibility violations | Determinism mismatches |
|---:|---:|---:|---:|---:|---:|---:|
| 6 | 12 | 0 | 2 | 0 | 0 | 0 |
| 387 | 774 | 0 | 16,512 | 0 | 0 | 0 |
| 771 | 2,038 | 248 | 33,056 | 0 | 0 | 0 |
| 1,539 | 6,054 | 1,488 | 66,240 | 0 | 0 | 0 |
| 3,075 | 20,038 | 6,944 | 132,992 | 0 | 0 | 0 |
| 6,147 | 69,830 | 28,768 | 268,032 | 0 | 0 | 0 |
| 58,467 | 5,491,878 | 2,687,472 | 2,587,872 | 0 | 0 | 0 |

The benchmark graph intentionally has no `ResourceLifetime`; therefore `lifetime_checks=0` is expected and does not claim lifetime-heavy graph-construction scaling. Lifetime semantics are covered by unit and integration tests instead.

### SafeBound Lifetime Regression Evidence

| Metric | Expected | Actual | Absolute delta | Result |
|---|---:|---:|---:|---|
| Reservation-covered `slot` aggregate term | 0.0 | 0.0 | 0.0 | PASS |
| Feasible makespan | 1.0 | 1.0 | 0.0 | PASS |
| SafeBound | 1.0 | 1.0 | 0.0 | PASS |
| Feasible minus SafeBound | 0.0 | 0.0 | 0.0 | PASS |
| Additional transient `alu` aggregate term | 4.0 | 4.0 | 0.0 | PASS |

The corrected owner is `ResourceLifetime.transient_per_sm_demand()`. Scheduler admission/release and SafeBound use that same operation. No reservation-duration tightening term, scaling factor, clamp, retry, or fallback was added.

### Raw Artifact Integrity

| Artifact | Rows | SHA-256 |
|---|---:|---|
| `task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/wave3_scheduler_benchmark.csv` | 8 including header | `13dad9670800d8362c5c16f182b48255bf26e0c86cf0986b1156fe08e6a125f5` |

The numeric CSV cells are unchanged from the measured benchmark run. The delivery correction changed only the eight line terminators from CRLF to LF after a staged `git diff --check` exposed Python `csv.writer`'s default dialect. The writer now declares `lineterminator="\n"`, and an automated RED/GREEN test prevents recurrence.

### Historical-Runtime Provenance Boundary

The old constants come from the reviewed parent evidence in:

```text
task_memory/task_2026-07-18_des_refined_roofline_review/
test_report_2026-07-18_des_refined_roofline_review.md
```

The first five constants are listed as three-run median legacy scheduler times in the parent `notes.md`; the `58,467`-Event value is the reviewed large-row runtime. The parent report records `/usr/bin/python` `3.12.3`, no active conda/venv, and pytest `9.1.1`, but it does not preserve host-CPU identity or a standalone raw six-point benchmark artifact. The new denominator also includes graph construction/validation and report assembly. Therefore the `legacy/new` column is labeled a size-matched historical comparison, not a stage-matched, controlled cycle-level benchmark and not evidence for a `10000x` claim.

### Independent Review Evidence

Artifact:

```text
.omx/artifacts/
claude-you-are-the-independent-post-fix-completion-reviewer-for-pip-2026-07-19T21-43-22-782Z.md
```

Verdict: **APPROVE**. Claude explicitly authorized Wave-3 commit/push before Wave 4, found zero mandatory code corrections, and retained only the low historical-provenance WATCH documented above.

The later CSV LF root-cause correction received a separate bounded review:

```text
.omx/artifacts/
ask-claude-wave3-csv-lf-bounded-review-2026-07-19T21-58-55Z.md
```

Verdict: **APPROVE**. Claude independently confirmed one focused test, one unique-writer `lineterminator="\n"` fix, byte-identical numeric cells, no fallback/compatibility/duplicate module, no claim expansion, and no mandatory action.

### Final Pre-Staging Static Evidence

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| Python AST parse | Every changed/new Python file parses | `12/12` parsed | PASS |
| Added/new Python line length | Zero lines over 88 characters | `0` | PASS |
| Untracked text trailing whitespace | Zero matches | `0` | PASS |
| Task Markdown Modification History | Every task Markdown file contains the section | `18/18` | PASS |
| Tracked `git diff --check` excluding only `=10.1` | Exit `0` | Exit `0`; `0` errors | PASS |

The first static helper scanned complete modified Python files and reported two unchanged legacy import lines over 88 characters in `event_simulator/__init__.py`. That was an audit-scope defect: neither line was added by this checkpoint. The intended added-line audit returned `0`. The same first helper found three Markdown hard-break spaces in this report's metadata; those spaces were removed, and the final trailing-whitespace audit returned `0`.

### Final Staging and Integrity Evidence

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| Exact staged paths | `25` approved paths | `25`; mismatch lines `0` | PASS |
| Permanently ignored `=10.1` staged paths | `0` | `0` | PASS |
| `.omx` staged paths | `0` | `0` | PASS |
| Relevant unstaged tracked paths | `0` | `0` | PASS |
| Relevant untracked repository paths | `0` | `0` | PASS |
| SHA-256 manifest entries | `40/40` validate | `40/40` | PASS |
| Staged `git diff --check` | Exit `0` | Exit `0`; `0` errors | PASS |

Files were staged through an explicit path list; `git add .` was not used. The local `.omx` Claude artifacts remain intentionally outside the repository delivery set.

### Full-Repository Scope Boundary

The Wave-3 command intentionally excludes legacy operator callers. Those callers still construct the removed one-level `ResourceConfig`, pass raw Event lists to `schedule()`, and read removed `result.events`, `report.makespan`, or `report.critical_path` fields. Their root-cause migration is owned by Wave 4 in:

```text
tests/unit/test_cache.py
tests/unit/test_gemm_manifest.py
tests/unit/test_gemm_validation.py
tests/integration/test_gemm_v2_simulation.py
tests/integration/test_fa_simulation.py
tests/integration/test_operator_simulation.py
```

No compatibility shim is added to make those callers pass early. The full repository suite becomes a required passing gate after Wave 4 migration; this staged ownership is not a fallback or silent skip.

## Conclusion

Wave 3 meets its local design/harness gates: the SafeBound theorem defect is corrected at its invariant owner, every returned schedule is independently validated as feasible, the fixed greedy no-progress limit is explicit, report provenance is separated, the complete `58,467`-Event benchmark is recorded with counters and absolute phase times, both independent completion reviews are `APPROVE`, and the exact staging/static/checksum gates pass. Delivery now requires only the Lore commit, push, and `HEAD == origin/des` equality check before Wave 4 starts.
