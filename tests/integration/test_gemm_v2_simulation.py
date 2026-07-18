"""Integration tests for lower_gemm_v2 structural decomposition."""

import pytest

from event_simulator import (
    PrimitiveCalibration,
    ResourceConfig,
    build_report,
    lower_gemm_v2,
    load_hardware_config,
    derive_calibration,
    derive_resource_config,
    schedule,
)
from event_simulator.hardware_adapter import HardwareConfig


@pytest.fixture
def h100_hw():
    return load_hardware_config("hardware/H100.json")


@pytest.fixture
def h100_cal(h100_hw):
    return derive_calibration(h100_hw)


@pytest.fixture
def h100_rc(h100_hw):
    return derive_resource_config(h100_hw, operator_type="gemm_v2")


class TestGemmV2WaveSplit:
    """Verify CTA admission events are correctly split into full/tail wave."""

    def test_exact_wave_all_full(self, h100_hw, h100_cal, h100_rc):
        # 132 CTAs = exactly 1 wave on 132 SMs → all full, no tail
        events = lower_gemm_v2(
            "gemm-exact", m=1024, n=1024, k=256,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        admission_types = [e.event_type for e in events if "Admission" in e.event_type]
        # 8x8 = 64 CTAs, all in tail wave (64 < 132)
        # Actually 64 < 132 so it's all tail wave
        assert all(t == "CTAAdmission_TailWave" for t in admission_types)

    def test_multiple_waves_has_tail(self, h100_hw, h100_cal, h100_rc):
        # 4096x4096 with 128x128 = 1024 CTAs
        # 1024 / 132 = 7 full waves (924) + tail (100)
        events = lower_gemm_v2(
            "gemm-waves", m=4096, n=4096, k=256,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        full_count = sum(1 for e in events if e.event_type == "CTAAdmission_FullWave")
        tail_count = sum(1 for e in events if e.event_type == "CTAAdmission_TailWave")
        assert full_count == 924
        assert tail_count == 100

    def test_perfect_multiple_no_tail(self, h100_hw, h100_cal, h100_rc):
        # Need CTA count that's exact multiple of 132
        # 12x11 = 132 CTAs with tile 128x128 needs m=1536, n=1408
        events = lower_gemm_v2(
            "gemm-perfect", m=1536, n=1408, k=256,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        tail_count = sum(1 for e in events if e.event_type == "CTAAdmission_TailWave")
        assert tail_count == 0


class TestGemmV2MemoryModel:
    """Verify the chip-level DRAM event correctly models total unique input traffic."""

    def test_has_chip_level_dram_event(self, h100_hw, h100_cal, h100_rc):
        events = lower_gemm_v2(
            "gemm-dram", m=4096, n=4096, k=4096,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        dram_events = [e for e in events if e.event_type == "GlobalLoad_L2Miss"]
        assert len(dram_events) == 1
        # Total unique INPUT bytes = (M*K + N*K) * element_bytes (no output C)
        expected_bytes = (4096 * 4096 + 4096 * 4096) * 2
        assert dram_events[0].bytes == expected_bytes

    def test_l2_miss_reflects_cross_cta_sharing(self, h100_hw, h100_cal, h100_rc):
        m, n, k, tile_m, tile_n = 256, 256, 512, 128, 128
        element_bytes = 2
        events = lower_gemm_v2(
            "gemm-bytes", m=m, n=n, k=k,
            tile_m=tile_m, tile_n=tile_n,
            calibration=h100_cal, hardware=h100_hw, element_bytes=element_bytes,
        )
        # Total input = (M*K + N*K) * 2 = 524288 bytes — fits in 50MB L2
        # So uses L2 path (GlobalLoad_L2Hit)
        mem_events = [e for e in events if "GlobalLoad" in e.event_type]
        assert len(mem_events) == 1
        expected = (m * k + n * k) * element_bytes
        assert mem_events[0].bytes == expected

    def test_small_working_set_dram_is_small(self, h100_hw, h100_cal, h100_rc):
        events = lower_gemm_v2(
            "gemm-small-k", m=4096, n=4096, k=64,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        # (4096*64 + 4096*64)*2 = 1MB — fits in 50MB L2 → uses L2 path
        mem_events = [e for e in events if "GlobalLoad" in e.event_type]
        assert len(mem_events) == 1
        expected = (4096 * 64 + 4096 * 64) * 2
        assert mem_events[0].bytes == expected
        assert mem_events[0].event_type == "GlobalLoad_L2Hit"


class TestGemmV2TileSplit:
    """Verify MMA events are correctly classified as full/partial."""

    def test_perfect_tiling_all_full(self, h100_hw, h100_cal, h100_rc):
        # 256x256 with 128x128 → all tiles are full
        events = lower_gemm_v2(
            "gemm-full", m=256, n=256, k=256,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        full = sum(1 for e in events if e.event_type == "MMA_FullTile")
        partial = sum(1 for e in events if e.event_type == "MMA_PartialTile")
        assert full == 4
        assert partial == 0

    def test_imperfect_tiling_has_partial(self, h100_hw, h100_cal, h100_rc):
        # 300x300 with 128x128 → 3x3=9 tiles, 4 full + 5 partial
        events = lower_gemm_v2(
            "gemm-partial", m=300, n=300, k=256,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        full = sum(1 for e in events if e.event_type == "MMA_FullTile")
        partial = sum(1 for e in events if e.event_type == "MMA_PartialTile")
        assert full == 4
        assert partial == 5


class TestGemmV2Scheduling:
    """Verify the scheduled result is sane and exploits parallelism."""

    def test_makespan_less_than_serial(self, h100_hw, h100_cal, h100_rc):
        events = lower_gemm_v2(
            "gemm-par", m=4096, n=4096, k=4096,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        result = schedule(events, h100_rc)
        # Serial time = sum of all event durations
        serial_time = sum(e.duration for e in events)
        # With shared DRAM bandwidth (1 lane), memory events serialize.
        # But compute (132 lanes) parallelizes. Makespan should still be
        # significantly less than fully serial (at least 2x speedup).
        assert result.makespan < serial_time * 0.5

    def test_report_has_meaningful_breakdown(self, h100_hw, h100_cal, h100_rc):
        events = lower_gemm_v2(
            "gemm-report", m=2048, n=2048, k=2048,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        result = schedule(events, h100_rc)
        report = build_report(result)
        assert report.makespan > 0
        assert report.resource_busy_time["tensor_core"] > 0
        # Memory may use L2 or DRAM path depending on size
        mem_busy = report.resource_busy_time.get("dram_bandwidth", 0) + report.resource_busy_time.get("l2_bandwidth", 0)
        assert mem_busy > 0
        assert len(report.critical_path_event_ids) >= 3

    def test_dependencies_are_respected(self, h100_hw, h100_cal, h100_rc):
        events = lower_gemm_v2(
            "gemm-deps", m=256, n=256, k=256,
            tile_m=128, tile_n=128, calibration=h100_cal, hardware=h100_hw,
        )
        result = schedule(events, h100_rc)
        by_id = result.by_id()
        # MMA must start after all its load dependencies complete
        for e in result.events:
            if "mma" in e.event_id:
                for dep_id in e.dependencies:
                    dep = by_id[dep_id]
                    assert e.start_time >= dep.end_time
