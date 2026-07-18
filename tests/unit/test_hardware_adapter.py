"""Tests for event_simulator.hardware_adapter."""

import json
import tempfile
from pathlib import Path

import pytest

from event_simulator.hardware_adapter import (
    HardwareConfig,
    derive_calibration,
    derive_resource_config,
    load_hardware_config,
)


@pytest.fixture
def h100_json(tmp_path):
    """Create a minimal H100 hardware JSON for testing."""
    data = {
        "name": "NVIDIA H100",
        "totalGlobalMem": 84929216512,
        "numSms": 132,
        "memBandwidth": 3352.32,
        "l2CacheBandwidth": 8820,
        "l2CacheSize": 51200,
        "sharedMemorySize": 228,
        "sharedMemoryBandwidth": 128,
        "tcBf16": 4096,
        "tcFp8": 8192,
        "xuFp32": 16,
        "FmaFp32": 128,
        "smFreq": 1830,
        "architecture": "hopper",
        "registerFileSize": 256,
        "l1CacheSize": 256,
    }
    path = tmp_path / "H100.json"
    path.write_text(json.dumps(data))
    return path


def test_load_hardware_config_parses_h100(h100_json):
    hw = load_hardware_config(h100_json)
    assert hw.name == "NVIDIA H100"
    assert hw.num_sms == 132
    assert hw.sm_freq_mhz == 1830.0
    assert hw.mem_bandwidth_gb_s == 3352.32
    assert hw.l2_cache_size_kb == 51200
    assert hw.tc_bf16 == 4096.0
    assert hw.architecture == "hopper"


def test_load_hardware_config_raises_on_missing_file():
    with pytest.raises(FileNotFoundError):
        load_hardware_config("/nonexistent/path.json")


def test_hardware_config_derived_properties(h100_json):
    hw = load_hardware_config(h100_json)
    assert hw.mem_bandwidth_bytes_per_us == pytest.approx(3352.32e3, rel=1e-3)
    assert hw.l2_bandwidth_bytes_per_us == pytest.approx(8820e3, rel=1e-3)
    assert hw.l2_cache_size_bytes == 51200 * 1024
    # tc_bf16=4096 ops/cycle/SM, sm_freq=1830 MHz → 7,495,680 FLOPs/us/SM
    assert hw.tc_bf16_flops_per_sm_per_us == pytest.approx(4096 * 1830, rel=1e-3)
    # Chip-wide: 7,495,680 × 132 = 989,429,760 FLOPs/us ≈ 989.4 TFLOPS
    assert hw.tc_bf16_flops_per_us == pytest.approx(4096 * 1830 * 132, rel=1e-3)


def test_derive_calibration_produces_valid_entries(h100_json):
    hw = load_hardware_config(h100_json)
    cal = derive_calibration(hw)

    # All values should be non-negative
    for key, val in cal.duration_per_unit.items():
        assert val >= 0.0, f"{key} has negative calibration"

    # L2 hit should be faster than DRAM miss
    assert cal.duration_per_unit["GlobalLoad_L2Hit"] < cal.duration_per_unit["GlobalLoad_L2Miss"]

    # MMA variants should have same rate
    assert cal.duration_per_unit["MMA"] == cal.duration_per_unit["MMA_FullTile"]
    assert cal.duration_per_unit["MMA"] == cal.duration_per_unit["MMA_PartialTile"]

    # FA_TaskSync should be zero-cost
    assert cal.duration_per_unit["FA_TaskSync"] == 0.0


def test_derive_calibration_physical_sanity(h100_json):
    hw = load_hardware_config(h100_json)
    cal = derive_calibration(hw)

    # Memory rates are CHIP-WIDE. 1MB load from DRAM = ~0.3us on H100 (3.35 TB/s)
    load_1mb_us = cal.duration_per_unit["GlobalLoad_L2Miss"] * 1024 * 1024
    assert 0.1 < load_1mb_us < 1.0

    # Compute rates are PER-SM. One MMA instruction per SM is measurable.
    # Per-SM TC = 4096 TFLOPS / 132 = 31 TFLOPS → 121M MMA-instr/s → ~8us per instr
    assert cal.duration_per_unit["MMA"] > 1e-7

    # Fixed overheads are zero for pure roofline bound
    assert cal.duration_per_unit["KernelLaunch"] == 0.0
    assert cal.duration_per_unit["CTAAdmission"] == 0.0


def test_derive_resource_config_gemm(h100_json):
    hw = load_hardware_config(h100_json)
    rc = derive_resource_config(hw, operator_type="gemm_v2")
    assert rc.capacities["launch"] == 1
    assert rc.capacities["sm"] == 132
    assert rc.capacities["tensor_core"] == 132
    assert rc.capacities["dram_bandwidth"] == 1  # chip-wide shared pool
    assert rc.capacities["l2_bandwidth"] == 132  # per-SM parallel slices


def test_derive_resource_config_flash_attention(h100_json):
    hw = load_hardware_config(h100_json)
    rc = derive_resource_config(hw, operator_type="flash_attention")
    assert rc.capacities["launch"] == 1
    assert rc.capacities["tensor_core"] == 132
    assert rc.capacities["dram_bandwidth"] == 1


def test_loads_real_hardware_file():
    """Verify against actual hardware files in the repo."""
    hw_path = Path("hardware/H100.json")
    if not hw_path.exists():
        pytest.skip("hardware/H100.json not found")
    hw = load_hardware_config(hw_path)
    assert hw.num_sms == 132
    cal = derive_calibration(hw)
    assert cal.duration_per_unit["GlobalLoad_L2Miss"] > 0
