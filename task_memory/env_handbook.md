# Environment Handbook

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Documented repository-root `PYTHONPATH` for direct validation-script execution. |
| 2026-07-18 | Documented test timing when GNU `/usr/bin/time` is not installed. |

## Command Timing Without GNU `time`

### Symptom

`/usr/bin/time: No such file or directory` on a minimal host image.

### Root Cause

The GNU `time` executable is not installed, although Bash still provides the `time` shell keyword.

### Verified Command

```bash
TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time python -m pytest tests -q
```

This preserves explicit elapsed/user/system timing without installing a dependency.

## Running Validation Scripts by File Path

### Symptom

Running `python tests/validation/validate_gemm_v2.py` from the repository root raises `ModuleNotFoundError: No module named 'event_simulator'`.

### Root Cause

Python places the script directory (`tests/validation/`) rather than the repository root at the front of `sys.path` for direct file execution.

### Verified Command

```bash
PYTHONPATH="$PWD" python tests/validation/validate_gemm_v2.py
```

The explicit repository-root `PYTHONPATH` makes the local package import deterministic.
