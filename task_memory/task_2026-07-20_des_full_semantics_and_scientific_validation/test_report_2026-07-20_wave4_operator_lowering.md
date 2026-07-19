# Test Report: Phase-2 Wave-4 Operator Lowering

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Recorded the pushed Wave-4 Lore commit and exact local/remote SHA equality. |
| 2026-07-20 | Recorded the exact-path staging and index-hash audit before the Wave-4 Lore commit. |
| 2026-07-20 | Added the final Claude delivery-package verdict, fresh pre-staging regression/proof/static results, checksum totals, and resolved static-wrapper false positive. |
| 2026-07-20 | Recorded Wave-4 RED/GREEN evidence, independent review reconciliation, full regression, proof validation, static delivery checks, and absolute numeric contract metrics. |

## Scope and Claim Boundary

This report validates Phase-2 Wave 4 only:

- manifest-order HBM/L2 cache resolution;
- authoritative `GemmLaunchManifest` validation;
- manifest-only GEMM lowering with required initial cache state;
- persistent Worker lifetime and WorkItem ordering;
- split-K physical work, accumulator dependencies, reduction, and output flush;
- two-level hardware topology and specification calibration;
- explicit FA singleton-SM affinity;
- row-indexed authoritative GEMM validation;
- regression of the previously delivered exact, SafeBound, scheduler, and report layers.

The four provenance layers remain separate:

```text
ExactScheduleResult
SafeBound
SimulationResult
measured-hardware comparison
```

The synthetic unit/integration fixtures below are contract evidence, not a
measured-hardware accuracy result. This report does not claim Hopper silicon
equivalence, cross-architecture zero-shot accuracy, measured primitive
calibration, a GPGPU-Sim result, or `10000x` speedup. Those remain Wave-5 work.

## 1. Test Script Information

### Environment

| Item | Actual value |
|---|---|
| Worktree | `/data/ycfeng/pipeweave/.worktrees/des` |
| Branch baseline | `0a733ec597056924f9c10236071eb6892550080d` |
| Python executable | `/usr/bin/python` |
| Python version | `3.12.3` |
| pytest version | `9.1.1` |
| `CONDA_DEFAULT_ENV` | empty |
| Python bytecode writes | disabled with `PYTHONDONTWRITEBYTECODE=1` |
| pytest cache writes | disabled with `-p no:cacheprovider` |

### Authoritative Wave-4 test paths

| Type | Full path |
|---|---|
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_cache.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_gemm_manifest.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_hardware_adapter.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_gemm_validation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_gemm_v2_simulation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_fa_simulation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_operator_simulation.py` |
| Proof validation | `/data/ycfeng/pipeweave/.worktrees/des/tests/validation/validate_safe_bound_exact_oracle.py` |
| Authoritative GEMM harness | `/data/ycfeng/pipeweave/.worktrees/des/tests/validation/validate_gemm_v2.py` |

`validate_gemm_v2.py` is exercised through unit tests in this wave. Its direct
CLI intentionally raises because a real row-indexed authoritative manifest
artifact does not yet exist. Wave 5 owns that provisioning; a heuristic
manifest reconstruction is prohibited.

### Exact commands

#### Focused Wave-4 owner set

```bash
set -o pipefail
TIMEFORMAT=$'WRAPPER_ELAPSED=%3R\nWRAPPER_USER=%3U\nWRAPPER_SYSTEM=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider \
    tests/unit/test_cache.py \
    tests/unit/test_gemm_manifest.py \
    tests/unit/test_hardware_adapter.py \
    tests/unit/test_gemm_validation.py \
    tests/integration/test_gemm_v2_simulation.py \
    tests/integration/test_fa_simulation.py \
    tests/integration/test_operator_simulation.py \
    -q
```

#### Full repository regression

```bash
set -o pipefail
TIMEFORMAT=$'WRAPPER_ELAPSED=%3R\nWRAPPER_USER=%3U\nWRAPPER_SYSTEM=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider tests -q
```

#### Independent exact/SafeBound corpus

```bash
set -o pipefail
TIMEFORMAT=$'WRAPPER_ELAPSED=%3R\nWRAPPER_USER=%3U\nWRAPPER_SYSTEM=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python tests/validation/validate_safe_bound_exact_oracle.py
```

#### Focused legacy-behavior scan

```bash
if rg -n \
  "resource=|stream_ordered|dram_bandwidth|ResourceConfig\\(\\s*\\{" \
  event_simulator/operators.py \
  event_simulator/hardware_adapter.py \
  tests/validation/validate_gemm_v2.py; then
  exit 1
fi
```

#### Repository diff check

```bash
git diff --check -- . ':(exclude)=10.1'
```

The AST, added-line, signature, import, and task-document audit was run as one
read-only Python/shell gate over the exact changed/untracked path list returned
by Git while excluding `=10.1`. It parsed every changed/new Python file,
checked only newly added Python lines against the 88-character project limit,
compared the public `lower_gemm_v2` signature byte-for-byte, checked the
changed `operators.py` imports, and required Modification History in every task
Markdown document.

## 2. Validation Criteria

### Behavioral criteria

1. All cache transitions are deterministic, capacity-safe, immutable, and
   byte-conserving for cold, warm, eviction, dirty writeback, and output
   visibility states.
2. `GemmLaunchManifest` is the only source of Worker assignment, persistent
   ordering, issued extents, split-K partitions, reduction topology, and cache
   access order.
3. `lower_gemm_v2` accepts only the reviewed manifest API and returns one
   normalized `EventGraph`; no compatibility signature or inferred stream
   order exists.
4. Lowered HBM/L2 bytes exactly equal the single cache resolution.
5. Every Worker owns exactly one acquire-to-release `ResourceLifetime`.
6. MMA instruction count uses `ceil_div(physical_issued_work, 256)` rather
   than logical work.
7. Reductions remain outside Worker lifetimes, demand one per-SM ALU lane, and
   wait for every authoritative accumulator producer.
8. HBM output flush Events are direct predecessors of `KernelComplete`; L2
   output visibility emits no final HBM flush.
9. FA compute/sync Events have singleton SM affinity; FA adds no lifetime in
   this wave; tuple permutation cannot alter its schedule.
10. Hardware topology has global launch/HBM/L2 capacity and unit per-SM
    tensor/ALU/SFU/barrier/CTA capacities replicated through `sm_count`.
11. The authoritative validator counts every missing/mismatched manifest by
    reason and never reconstructs launch policy from `is_split_k`, CTA ratio,
    tile grid, shape, or floor division.
12. All prior exact, SafeBound, scheduler, report, structural, and operator
    tests continue to pass.

### Static and delivery criteria

- every changed/new Python file parses;
- newly added Python lines over 88 characters: `0`;
- newly orphaned imports in changed `operators.py`: `0`;
- forbidden legacy patterns: `0`;
- every current-task Markdown file has Modification History;
- `git diff --check` returns exit code `0`;
- `.omx/` and `=10.1` are never staged.

## 3. RED Evidence and Root-Cause Resolutions

### Clean behavior RED before production lowering

| Metric | Expected RED | Actual | Delta |
|---|---:|---:|---:|
| Collected tests | `145` | `145` | `0` |
| Passing tests | incomplete by design | `98` | not a completion metric |
| Ordinary failures | missing reviewed behavior | `47` | all mapped to Wave-4 production work |
| Setup errors | `0` | `0` | `0` |
| Collection errors | `0` | `0` | `0` |
| Exit code | `1` | `1` | `0` |

Before that clean RED, one collection attempt exited `2` because an old
operator fixture still constructed the deliberately removed flat
`ResourceConfig({...})` API. The root cause was test ownership deferred from
Wave 1 to Wave 4. Only Wave-4 tests were migrated; no production compatibility
shim was introduced. A later FA RED attempt reported `13` setup errors because
the fixture still called the intentionally unimplemented adapter. It was
corrected to a hand-built valid two-level test config before production edits.

### First hardware-adapter GREEN attempt

| Metric | Expected | Actual before fix | Delta / failure |
|---|---:|---:|---:|
| Hardware-focused tests | `19/19` | `16/19` | `3` failed |
| Stale symbol references | `0` | `1` | `dram_us_per_byte` remained in `GlobalLoad` |

Root cause: the local calibration variable was renamed from
`dram_us_per_byte` to `hbm_us_per_byte`, but one `GlobalLoad` reference was not
updated. The single owner reference was corrected; no fallback or scaling
factor was added. The rerun passed `19/19`.

### Static delivery failure

The first final static audit found one newly added line of length `90` at
`tests/unit/test_gemm_manifest.py:444`, versus the accepted maximum `88`.
The generator expression was wrapped without changing behavior. Its focused
test passed `1/1`; the complete static rerun reported `0` long added lines.

## 4. Test Results and Evidence

### Test-suite summary

| Suite | Expected | Actual | Delta / failures | Result |
|---|---:|---:|---:|---|
| Cache module final | `33/33` | `33/33` | `0` | PASS |
| Cache + manifest after manifest review | `74/74` | `74/74` | `0` | PASS |
| Hardware adapter | `19/19` | `19/19` | `0` | PASS |
| Simple operator integration | `8/8` | `8/8` | `0` | PASS |
| GEMM-v2 integration before WATCH additions | `11/11` | `11/11` | `0` | PASS |
| FA integration | `21/21` | `21/21` | `0` | PASS |
| Authoritative validator unit tests | `12/12` | `12/12` | `0` | PASS |
| Two Claude WATCH integration witnesses | `2/2` | `2/2` | `0` | PASS |
| Final Wave-4 focused owner set | `147/147` | `147/147` in pytest `1.79s` | `0` | PASS |
| Full repository regression | all collected | `400/400` in pytest `2.16s` | `0` | PASS |

Focused owner-set timing:

```text
wrapper elapsed = 2.252s
user            = 3.662s
system          = 0.152s
exit code       = 0
```

Full repository timing:

```text
wrapper elapsed = 2.645s
user            = 4.181s
system          = 0.176s
exit code       = 0
```

### Exact/SafeBound regression evidence

| Metric | Expected | Actual | Delta / failures |
|---|---:|---:|---:|
| Oracle cases | `4,725` | `4,725` passed | `0` |
| Exact mismatches | `0` | `0` | `0` |
| SafeBound violations | `0` | `0` | `0` |
| Maximum exact delta | `0.0` | `0.0` | `0.0` |
| Minimum `exact - bound` | `>= 0.0` | `0.0` | boundary equality |
| Input permutations | `28,350` | `28,350` | `0` mismatches |
| Conservation failures | `0` | `0` | `0` |
| Monotonicity checks | `18,360` | `18,360` | `0` failures |
| Case-record digest | frozen | `5e173514000270d7c5d2a504b1adcd9d62f9285ee6d12819a48397c63724da67` | unchanged |

The direct validation command reported `4.150281247s` internal elapsed,
`4.242s` wrapper elapsed, and exit code `0`.

### H100 specification calibration and topology

| Metric | Expected | Actual | Absolute delta |
|---|---:|---:|---:|
| SM count | `132` | `132` | `0` |
| HBM coefficient | `1 / 3,352,320 bytes/us` | `2.98300878197785e-07 us/byte` | `0` within float arithmetic |
| L2 coefficient | `1 / 8,820,000 bytes/us` | `1.13378684807256e-07 us/byte` | `0` within float arithmetic |
| HBM time for 1 MiB | derived | `0.312791141657 us` | direct coefficient product |
| L2 time for 1 MiB | derived | `0.118886167800 us` | direct coefficient product |
| Global capacities | launch/HBM/L2 each `1` | each `1` | `0` |
| Per-SM capacities | ALU/barrier/CTA/SFU/tensor each `1` | each `1` | `0` |

These are specification-derived idealized coefficients, not measured primitive
calibration.

### Manifest work and cache-traffic conservation

| Metric | Expected | Actual | Absolute delta |
|---|---:|---:|---:|
| Ordinary logical work | `128` FLOPs | `128` | `0` |
| Ordinary physical issued work | `1,024` FLOPs | `1,024` | `0` |
| Ordinary MMA instructions | `ceil(1,024 / 256) = 4` | `4` | `0` |
| Ordinary Worker lifetimes | `1` | `1` | `0` |
| L2-visibility final HBM flushes | `0` | `0` | `0` |
| Warm-state HBM read bytes | `0` | `0` | `0` |
| Split-K HBM read bytes | `16` | `16` | `0` |
| Split-K HBM write bytes | `4` | `4` | `0` |
| Split-K L2 read bytes | `28` | `28` | `0` |
| Split-K L2 write bytes | `28` | `28` | `0` |
| Split-K Workers / lifetimes | `2 / 2` | `2 / 2` | `0 / 0` |
| Release ancestors of reduction | `2` | `2` | `0` |
| Direct output-flush predecessors | `1` | `1` | `0` |

The split-K fixture lowered to `28` Events, `31` explicit dependency edges,
and `13` cache transitions:

```text
evict_clean=3
flush_dirty_output=1
overwrite_miss=3
read_hit=2
read_miss=4
```

Clean eviction contributes zero resource-time Events. Every emitted cache
Event has positive bytes, and all four byte totals match the one cache
resolution exactly.

### Feasible schedule and report provenance

| Metric | Expected / relation | Actual | Delta |
|---|---:|---:|---:|
| Split-K feasible makespan | positive | `0.000111599637132002 us` | not a measured-hardware comparison |
| Dependency critical path | `0 < path <= makespan` | `0.000110120259584877 us` | makespan minus path `1.479377547125e-06 us` |
| Reversed-Event makespan delta | `0` | `0` | `0` |
| Reversed-Event entry mismatches | `0` | `0` | `0` |
| HBM resource busy time | positive | `5.96601756395571e-06 us` | positive |
| L2 resource busy time | positive | `6.34920634920635e-06 us` | positive |
| Tensor-core busy time | positive | `6.83060109289617e-05 us` | positive |
| ALU busy time | positive | `6.83060109289617e-05 us` | positive |

`SimulationResult.makespan` remains a deterministic feasible schedule value,
not a SafeBound or measured-hardware result.

### FA affinity evidence

| Metric | Expected | Actual | Absolute delta |
|---|---:|---:|---:|
| FA compute/sync task Events | positive | `96` | not a fixed acceptance count |
| Singleton-affinity violations | `0` | `0` | `0` |
| FA compute Events | positive | `48` | not a fixed acceptance count |
| Tensor-core demand violations | `0` | `0` | `0` |
| FA lifetimes | `0` | `0` | `0` |

### Authoritative validator evidence

The four-row contract fixture produced:

| Metric | Expected | Actual | Delta |
|---|---:|---:|---:|
| Source rows | `4` | `4` | `0` |
| Supported rows | `1` | `1` | `0` |
| `cta_count_mismatch` | `1` | `1` | `0` |
| `invalid_actual_time` | `1` | `1` | `0` |
| `missing_authoritative_manifest` | `1` | `1` | `0` |

For the deliberately synthetic `4 x 4 x 4` contract fixture:

| Metric | Actual |
|---|---:|
| Fixture actual time | `10.0 us` |
| Fixture DES schedule time | `0.0000388069861862083 us` |
| Absolute error | `9.99996119301381 us` |
| Relative error | `0.999996119301381` |

This fixture verifies data flow and explicit rejection accounting only. It is
not a scientific accuracy sample because its `10.0 us` value is an arbitrary
unit-test constant rather than a matched hardware measurement.

The bounded summary fixture used actual values `[10, 10, 10]`, DES values
`[8, 11, 6]`, and classical values `[7, 5, 12]`. It produced:

```text
evaluated=3
DES violations=1
classical violations=1
both valid=1
DES strictly tighter=1
DES mean gap=0.2
classical mean gap=0.3
```

### Static and artifact checks

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| Changed/new repository paths | recorded | `21` before this report | PASS |
| Changed/new Python paths | all parse | `14/14` parsed | PASS |
| Added Python lines over 88 after correction | `0` | `0` | PASS |
| Locally unused imports in changed `operators.py` | `0` | `0` | PASS |
| Forbidden legacy scan hits | `0` | `0` | PASS |
| Reviewed `lower_gemm_v2` signature match | `1` | `1` | PASS |
| Current task Markdown Modification History | all | `18/18` before this report | PASS |
| Tracked `git diff --check` errors | `0` | `0` | PASS |

The Modification History count becomes `19/19` after adding this report and
must be revalidated by the final delivery gate.

## 5. Independent Review Evidence

StepCode Claude `claude-opus-4-6[1m]` at effort `max` returned `APPROVE` in:

```text
.omx/artifacts/
claude-you-are-the-independent-post-implementation-reviewer-for-pip-
2026-07-19T23-19-03-079Z.md
```

Mandatory findings: `0`.

The two actionable WATCH items were:

1. warm initial cache state through the lowering integration;
2. L2 output visibility suppressing the final HBM flush.

Both now have explicit integration tests and passed first as `2/2`, then as
part of the fresh `147/147` owner-set result. Production code did not change in
response to the review. The remaining topology-dispatch WATCH is documented
only; adding a second policy would violate the current simplicity boundary.

The first advisor transport session
`596cf4e7-ecd9-4795-a156-7ecd48cf0281` produced no substantive review or
artifact and is not counted.

The final delivery-package review also returned `APPROVE`, with no mandatory
fix and staging status `READY`:

```text
.omx/artifacts/
claude-you-are-the-independent-final-delivery-package-reviewer-for--
2026-07-19T23-39-55-025Z.md
```

Its three WATCH items were reconciled without production changes. The cache
transition action remains owned by upstream `CacheTransition` validation; a
second topology policy remains speculative; and the direct validator CLI
continues to fail fast until Wave 5 provisions an authoritative manifest.

## 6. Final Pre-Staging Refresh

| Validation | Expected | Fresh actual | Failure count |
|---|---:|---:|---:|
| Focused Wave-4 suite | `147/147` | `147/147` in pytest `1.69s`; wrapper `2.161s` | `0` |
| Full repository suite | all collected pass | `400/400` in pytest `2.24s`; wrapper `2.698s` | `0` |
| Exact/SafeBound cases | `4,725/4,725` | `4,725/4,725`; wrapper `4.283s` | `0` |
| Exact permutations | `28,350` | `28,350` | `0` mismatches |
| Monotonicity checks | `18,360` | `18,360` | `0` failures |
| Changed/new Python AST | all parse | `14/14` | `0` |
| Added Python lines over 88 | `0` | `0` | `0` |
| Changed `operators.py` unused imports | `0` | `0` | `0` |
| Forbidden legacy patterns | `0` | `0` | `0` |
| `lower_gemm_v2` signature match | `1` | `1` | `0` |
| Task Markdown histories | all | `19/19` | `0` |
| Delivery checksums | all | `54/54` | `0` |
| `git diff --check` | clean | PASS | `0` |

The first explicit staging audit then recorded:

| Staging metric | Expected | Actual | Delta / failures |
|---|---:|---:|---:|
| Expected versus actual staged paths | `25` | `25` | `0` mismatches |
| Ignored `=10.1` paths staged | `0` | `0` | `0` |
| `.omx/` paths staged | `0` | `0` | `0` |
| Index content versus checksum inventory | `54/54` | `54/54` | `0` failures |
| Relevant unstaged tracked paths | `0` | `0` | `0` |
| Relevant untracked paths | `0` | `0` | `0` |
| Staged `git diff --check` | PASS | PASS | `0` |

The first final static wrapper reported `annotations` as an unused import.
Root-cause inspection showed that the checker treated
`from __future__ import annotations` as a runtime-bound import even though it
is a compiler directive and therefore has no loaded `Name` node. The checker
was corrected to exclude only `__future__` directives; the same complete gate
then reported zero unused imports. No source or test behavior changed in
response to this validation-script defect.

## 7. Result

Wave-4 implementation and regression evidence are **PASS** at this checkpoint:

- focused owner set: `147/147`;
- full repository: `400/400`;
- exact/SafeBound corpus: `4,725/4,725`, with zero mismatch, safety,
  permutation, conservation, or monotonicity failures;
- all reported traffic/work/topology/affinity deltas: `0` where equality is
  required;
- static/diff checks: zero remaining findings;
- independent post-implementation and final-package verdicts: `APPROVE`, zero
  mandatory fixes.

The final re-stage audit reproduced `25/25` exact paths, `54/54` index hashes,
`38/38` summary hashes, zero ignored/OMX/unstaged/untracked findings, and clean
staged/unstaged diffs. Lore commit
`350159313aa3a018700e648bce7ca5e842a34e07` was pushed to `origin/des`; a fresh
fetch returned the same local and remote SHA, so remote equality was `1` and
the relevant worktree was clean. Wave 5 may now begin from that checkpoint.
