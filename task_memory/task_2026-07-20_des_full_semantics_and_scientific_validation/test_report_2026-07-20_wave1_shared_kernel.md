# Test Report: Wave-1 Shared Semantic Kernel

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Recorded Wave-1 RED/GREEN evidence, independent reviews, fresh focused verification, numeric metrics, and validation-helper root-cause resolution. |

**Date:** 2026-07-20

**Repository:** `/data/ycfeng/pipeweave/.worktrees/des`

**Branch:** `des`

**Environment:** `CONDA_DEFAULT_ENV=<none>`; `VIRTUAL_ENV=<none>`; Python 3.12.3; pytest 9.1.1

## 1. Test Script Information

### Focused unit tests

- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_event_graph.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_resource_semantics.py`

Reproducible command:

```bash
TIMEFORMAT=$'elapsed_seconds=%3R\nuser_seconds=%3U\nsys_seconds=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider \
    tests/unit/test_event_graph.py \
    tests/unit/test_resource_semantics.py -q
```

### Added-line style and diff integrity

```bash
git diff --unified=0 -- . ':(exclude)=10.1' | python -c '
import sys

current = None
count = 0
for raw in sys.stdin:
    line = raw.rstrip("\n")
    if line.startswith("+++ b/"):
        current = line[6:]
    elif (
        line.startswith("+")
        and not line.startswith("+++")
        and current
        and current.endswith(".py")
    ):
        if len(line[1:]) > 88:
            count += 1
            print(f"{current}:added_line_length={len(line[1:])}:{line[1:]}")
print(f"changed_python_long_lines_gt_88={count}")
raise SystemExit(1 if count else 0)
'
git diff --check -- . ':(exclude)=10.1'
```

### Independent reviews

- Main shared-kernel review:
  `/data/ycfeng/pipeweave/.worktrees/des/.omx/artifacts/claude-you-are-the-independent-stepcode-claude-code-reviewer-for-pi-2026-07-19T19-42-58-403Z.md`
- Bounded post-fix correction:
  `/data/ycfeng/pipeweave/.worktrees/des/.omx/artifacts/claude-this-is-a-bounded-correction-pass-for-your-pipeweave-phase-2-2026-07-19T19-48-58-214Z.md`

Both reviews used StepCode Claude `claude-opus-4-6[1m]` at effort `max` through:

```bash
omx ask claude "<review prompt preserved in the corresponding artifact>"
```

## 2. Validation Criteria

1. Both focused test files collect without errors.
2. The initial ordinary RED fails because `EventGraph`, `ResourceLifetime`, the new immutable `Event` fields, and two-level `ResourceConfig` behavior are missing.
3. Every added regression test is personally observed failing before its production fix.
4. All final focused tests pass with zero failures.
5. `Event` remains immutable and unscheduled; graph/resource invariants have one owner; no compatibility adapter or implicit stream edge is introduced.
6. String or bytes dependency containers fail fast instead of being split into individual dependency IDs.
7. Newly added Python lines over 88 characters equal `0`.
8. `git diff --check` reports no whitespace errors.
9. Independent StepCode Claude returns `APPROVE` or bounded `WATCH`; `BLOCK` fails the handoff.

## 3. Test Results and Evidence

### RED/GREEN matrix

| Gate | Expected | Actual | Delta | Result |
|---|---:|---:|---:|---|
| Initial invalid collection attempt | Ordinary RED collection | 2 collection errors, exit 2 | 2 errors above target | FAIL, corrected |
| Initial valid RED | New behavior missing | 40 failed, 0 collection errors, exit 1 | 40 expected failures | PASS |
| First GREEN | 40 pass | 40 passed | 0 failures | PASS |
| Dependency canonicalization RED | 1 failure | 1 failed | 1 expected failure | PASS |
| Dependency canonicalization GREEN | All pass | 41 passed | 0 failures | PASS |
| String-container RED | 1 failure | 1 failed | 1 expected failure | PASS |
| Expanded pre-review GREEN | 76 pass | 76 passed in 0.86s | 0 failures | PASS |
| Post-correction fresh GREEN | 76 pass | 76 passed in 1.05s | 0 failures | PASS |
| Pre-review Bash elapsed | Record actual | 1.258s | N/A | PASS |
| Post-correction Bash elapsed | Record actual | 1.539s | N/A | PASS |
| Newly added Python lines over 88 | 0 | 0 | 0 | PASS |
| `git diff --check` errors | 0 | 0 | 0 | PASS |
| Main Claude verdict | APPROVE or WATCH | APPROVE | N/A | PASS |
| Bounded correction verdict | APPROVE or WATCH | APPROVE | N/A | PASS |

### Initial collection failure, root cause, and resolution

The first RED attempt exited `2` with two module-collection errors because `pytest.mark.parametrize` arguments constructed new-API `Event` objects during module import.

- **Root cause:** Eager fixture construction invoked the legacy production signature before pytest could collect ordinary test cases.
- **Impact:** The run did not prove the intended missing behavior; it only proved that the test modules could not import.
- **Fix:** Parameter tables now contain plain specifications and construct `Event`, `ResourceLifetime`, and `ResourceConfig` inside test bodies. No production code was changed for this correction.
- **Rerun:** `40 failed`, `0` collection errors, exit code `1`, with failures tied to the deliberately missing shared-kernel contracts.

### Dependency input failures and resolutions

1. A mutable dependency list remained attached to a frozen `Event`; mutating the caller input changed the Event after construction. The focused RED failed `1/1`. Canonicalizing and detaching dependencies to a sorted tuple produced `41/41` GREEN.
2. `dependencies="ab"` was silently interpreted as `("a", "b")`. The focused RED failed `1/1`. A two-line fail-fast guard now rejects `str` and `bytes` containers, after which the expanded suite reached `76/76`.

### Fresh style-helper failure, root cause, and resolution

The first post-correction wrapper reported:

```text
changed_python_long_lines_gt_88=2
event_simulator/__init__.py:5:110
event_simulator/__init__.py:6:106
style_exit_code=1
```

- **Root cause:** The helper scanned every line in every modified file, while the acceptance metric concerns newly added Python lines. Both long imports already exist in `HEAD`.
- **Impact:** The wrapper exited `1` even though pytest passed `76/76` and `git diff --check` passed.
- **Fix:** Audited added Python lines from `git diff --unified=0`; no unrelated code was reformatted and no validator exception was introduced.
- **Corrected result:** `changed_python_long_lines_gt_88=0`, exit code `0`.

### Numeric runtime evidence

| Metric | Pre-review final | Post-correction fresh | Delta |
|---|---:|---:|---:|
| Test cases passed | 76 | 76 | 0 |
| Pytest duration | 0.86s | 1.05s | +0.19s |
| Bash elapsed | 1.258s | 1.539s | +0.281s |
| Failures | 0 | 0 | 0 |

Runtime variation is recorded only as execution evidence; no performance claim is derived from it.

### Evidence excerpts

```text
........................................................................ [ 94%]
....                                                                     [100%]
76 passed in 1.05s
elapsed_seconds=1.539
user_seconds=1.212
sys_seconds=0.064
changed_python_long_lines_gt_88=0
diff_check_exit_code=0
```

Bounded StepCode Claude verdict:

```text
APPROVE
The post-review delta is minimal and sound.
Wave 2 may begin.
```

The deliberate legacy caller break remains assigned to Waves 2–4 without a compatibility shim. The external-event/lifetime same-resource progress case remains an explicit Wave-3 placement/no-progress RED rather than an over-defensive Wave-1 graph rejection.
