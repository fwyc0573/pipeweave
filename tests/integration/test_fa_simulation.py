"""Integration tests for lower_flash_attention."""

import pytest

from event_simulator import (
    build_report,
    derive_calibration,
    derive_resource_config,
    load_hardware_config,
    lower_flash_attention,
    schedule,
)


@pytest.fixture
def h100_hw():
    return load_hardware_config("hardware/H100.json")


@pytest.fixture
def h100_cal(h100_hw):
    return derive_calibration(h100_hw)


@pytest.fixture
def h100_rc(h100_hw):
    return derive_resource_config(h100_hw, operator_type="flash_attention")


class TestFAEventStructure:
    """Verify correct event emission patterns."""

    def test_emits_expected_event_types(self, h100_hw, h100_cal, h100_rc):
        events = lower_flash_attention(
            "fa-struct", batch_size=2, q_lengths=[256, 256],
            kv_lengths=[512, 512], num_qo_heads=8, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        types = {e.event_type for e in events}
        assert "KernelLaunch" in types
        assert "KernelComplete" in types
        assert "GlobalLoad_L2Miss" in types
        assert "FA_Compute" in types
        assert "FA_TaskSync" in types

    def test_single_dram_event(self, h100_hw, h100_cal, h100_rc):
        events = lower_flash_attention(
            "fa-dram", batch_size=2, q_lengths=[1024, 1024],
            kv_lengths=[2048, 2048], num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        dram_events = [e for e in events if e.event_type == "GlobalLoad_L2Miss"]
        assert len(dram_events) == 1

    def test_dram_bytes_gqa_aware(self, h100_hw, h100_cal, h100_rc):
        events = lower_flash_attention(
            "fa-gqa", batch_size=1, q_lengths=[128],
            kv_lengths=[256], num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        dram = next(e for e in events if e.event_type == "GlobalLoad_L2Miss")
        # KV: 256 * 8 * 128 * 2 * 2 = 1048576 (num_kv_heads for K+V)
        # Q: 128 * 32 * 128 * 2 = 1048576 (num_qo_heads)
        # O: 128 * 32 * 128 * 2 = 1048576 (num_qo_heads)
        expected = (256 * 8 * 128 * 2 + 128 * 32 * 128 + 128 * 32 * 128) * 2
        assert dram.bytes == expected

    def test_task_count_matches_scheduler(self, h100_hw, h100_cal, h100_rc):
        events = lower_flash_attention(
            "fa-tasks", batch_size=4, q_lengths=[2048]*4,
            kv_lengths=[2048]*4, num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        n_compute = sum(1 for e in events if e.event_type == "FA_Compute")
        n_sync = sum(1 for e in events if e.event_type == "FA_TaskSync")
        assert n_compute == n_sync
        assert n_compute > 0


class TestFAScheduling:
    """Verify scheduling produces valid results."""

    def test_makespan_positive(self, h100_hw, h100_cal, h100_rc):
        events = lower_flash_attention(
            "fa-mk", batch_size=2, q_lengths=[1024, 1024],
            kv_lengths=[2048, 2048], num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        result = schedule(events, h100_rc)
        assert result.makespan > 0

    def test_longer_seq_takes_more_time(self, h100_hw, h100_cal, h100_rc):
        events_short = lower_flash_attention(
            "fa-s", batch_size=1, q_lengths=[512],
            kv_lengths=[512], num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        events_long = lower_flash_attention(
            "fa-l", batch_size=1, q_lengths=[4096],
            kv_lengths=[4096], num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        ms_short = schedule(events_short, h100_rc).makespan
        ms_long = schedule(events_long, h100_rc).makespan
        assert ms_long > ms_short

    def test_report_breakdown(self, h100_hw, h100_cal, h100_rc):
        events = lower_flash_attention(
            "fa-report", batch_size=4, q_lengths=[2048]*4,
            kv_lengths=[2048]*4, num_qo_heads=32, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw,
        )
        result = schedule(events, h100_rc)
        report = build_report(result)
        assert report.makespan > 0
        assert report.resource_busy_time["tensor_core"] > 0
        assert report.resource_busy_time["dram_bandwidth"] > 0
        assert len(report.critical_path_event_ids) >= 3


class TestFACausalMasking:
    """Verify causal masking reduces work."""

    def test_causal_less_work_than_non_causal(self, h100_hw, h100_cal, h100_rc):
        events_causal = lower_flash_attention(
            "fa-c", batch_size=1, q_lengths=[2048],
            kv_lengths=[2048], num_qo_heads=8, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw, causal=True,
        )
        events_full = lower_flash_attention(
            "fa-f", batch_size=1, q_lengths=[2048],
            kv_lengths=[2048], num_qo_heads=8, num_kv_heads=8,
            head_dim=128, calibration=h100_cal, hardware=h100_hw, causal=False,
        )
        # Causal has fewer MMA instructions total (triangular mask)
        causal_instrs = sum(e.instruction_count for e in events_causal if e.event_type == "FA_Compute")
        full_instrs = sum(e.instruction_count for e in events_full if e.event_type == "FA_Compute")
        assert causal_instrs < full_instrs


class TestFAValidation:
    """Validate input handling."""

    def test_rejects_mismatched_lengths(self, h100_hw, h100_cal, h100_rc):
        with pytest.raises(ValueError, match="batch_size"):
            lower_flash_attention(
                "fa-bad", batch_size=2, q_lengths=[1024],
                kv_lengths=[1024, 1024], num_qo_heads=8, num_kv_heads=8,
                head_dim=128, calibration=h100_cal, hardware=h100_hw,
            )

    def test_rejects_non_positive_heads(self, h100_hw, h100_cal, h100_rc):
        with pytest.raises(ValueError):
            lower_flash_attention(
                "fa-bad", batch_size=1, q_lengths=[1024],
                kv_lengths=[1024], num_qo_heads=0, num_kv_heads=8,
                head_dim=128, calibration=h100_cal, hardware=h100_hw,
            )
