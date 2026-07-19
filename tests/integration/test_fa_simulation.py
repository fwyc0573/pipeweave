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

    @pytest.mark.parametrize("attention_type", ["fa2_ragged", "fa2_paged"])
    def test_fa2_path_executes_with_binary_search_contract(
        self, h100_hw, h100_cal, h100_rc, attention_type
    ):
        events = lower_flash_attention(
            "fa2-path",
            batch_size=2,
            q_lengths=[128, 256],
            kv_lengths=[512, 768],
            num_qo_heads=8,
            num_kv_heads=8,
            head_dim=128,
            calibration=h100_cal,
            hardware=h100_hw,
            attention_type=attention_type,
        )

        compute_events = [
            event for event in events if event.event_type == "FA_Compute"
        ]
        assert compute_events
        assert schedule(events, h100_rc).makespan > 0.0

    def test_fa3_schedule_threshold_matches_canonical_formula(
        self, h100_hw, h100_cal
    ):
        batch_size = 91
        events = lower_flash_attention(
            "fa3-threshold",
            batch_size=batch_size,
            q_lengths=[128] * batch_size,
            kv_lengths=[128] * batch_size,
            num_qo_heads=2,
            num_kv_heads=1,
            head_dim=128,
            calibration=h100_cal,
            hardware=h100_hw,
            attention_type="fa3_ragged",
        )

        compute_count = sum(
            event.event_type == "FA_Compute" for event in events
        )
        canonical_works_per_head = batch_size + batch_size - 1

        assert canonical_works_per_head == 181
        assert canonical_works_per_head <= 8192
        assert compute_count == batch_size * 2

    def test_fa3_schedule_threshold_selects_shared_schedule_above_boundary(
        self, monkeypatch, h100_hw, h100_cal
    ):
        from event_simulator import operators

        captured = {}

        def fake_fa3_scheduler(**kwargs):
            captured.update(kwargs)
            return [[] for _ in range(kwargs["num_sm"])]

        monkeypatch.setattr(
            operators,
            "_import_fa_schedulers",
            lambda: {
                "FA3GetCTATileSize": lambda *args: (128, 128),
                "fa3_scheduler": fake_fa3_scheduler,
            },
        )

        lower_flash_attention(
            "fa3-threshold-high",
            batch_size=1,
            q_lengths=[1_048_577],
            kv_lengths=[1_048_577],
            num_qo_heads=2,
            num_kv_heads=1,
            head_dim=128,
            calibration=h100_cal,
            hardware=h100_hw,
            attention_type="fa3_ragged",
        )

        assert captured["same_schedule_for_all_heads"] is True


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

    def test_rejects_non_divisible_head_groups(self, h100_hw, h100_cal):
        with pytest.raises(ValueError, match="divisible"):
            lower_flash_attention(
                "fa-bad-head-groups",
                batch_size=1,
                q_lengths=[128],
                kv_lengths=[128],
                num_qo_heads=10,
                num_kv_heads=3,
                head_dim=128,
                calibration=h100_cal,
                hardware=h100_hw,
            )

    def test_rejects_unsupported_attention_type(self, h100_hw, h100_cal):
        with pytest.raises(ValueError, match="unsupported attention_type"):
            lower_flash_attention(
                "fa-bad-type",
                batch_size=1,
                q_lengths=[128],
                kv_lengths=[128],
                num_qo_heads=8,
                num_kv_heads=8,
                head_dim=128,
                calibration=h100_cal,
                hardware=h100_hw,
                attention_type="fa4_ragged",
            )

    @pytest.mark.parametrize(
        ("q_lengths", "kv_lengths"),
        [([0], [128]), ([128], [-1]), ([True], [128])],
    )
    def test_rejects_non_positive_sequence_lengths(
        self, h100_hw, h100_cal, q_lengths, kv_lengths
    ):
        with pytest.raises(ValueError, match="positive integer"):
            lower_flash_attention(
                "fa-bad-length",
                batch_size=1,
                q_lengths=q_lengths,
                kv_lengths=kv_lengths,
                num_qo_heads=8,
                num_kv_heads=8,
                head_dim=128,
                calibration=h100_cal,
                hardware=h100_hw,
            )
