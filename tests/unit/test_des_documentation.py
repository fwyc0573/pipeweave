"""Contract checks for public DES documentation."""

from pathlib import Path

import pytest


DOC_PATHS = [
    Path("README.md"),
    Path("docs/des_design_rules.md"),
    Path("docs/event_simulator_design.md"),
]
SOURCE_DOC_PATHS = list(Path("event_simulator").glob("*.py"))


@pytest.mark.parametrize("path", DOC_PATHS)
def test_des_public_document_has_modification_history_near_the_top(path):
    first_lines = "\n".join(path.read_text().splitlines()[:20])
    assert "## Modification History" in first_lines


def test_des_rules_classify_scientific_status_explicitly():
    text = Path("docs/des_design_rules.md").read_text()

    for status in ("Established", "Experimental", "Unproven", "Blocked"):
        assert status in text


def test_public_docs_do_not_certify_the_greedy_schedule_as_a_universal_bound():
    combined = "\n".join(path.read_text() for path in DOC_PATHS)

    assert "produces a **theoretical lower bound" not in combined
    assert "MUST hold for ALL configurations" not in combined
    assert "→ 10000x faster than cycle-accurate simulation" not in combined
    assert "L2 bandwidth | num_sms" not in combined
    assert "Attention, MoE, communication" not in combined
    assert "not a certified lower bound" in combined


def test_readme_exposes_only_the_bounded_comparison_contract():
    text = Path("README.md").read_text()

    assert "compare_des_bound" in text
    assert "optimization_gap = (actual_time - des_bound) / actual_time" in text
    assert "hardware_efficiency = des_bound / actual_time" in text
    assert "(DES_bound - actual_time) / DES_bound" not in text
    assert "Small sample was consistently looser" not in text


def test_source_docstrings_do_not_certify_heuristic_composition_as_a_bound():
    combined = "\n".join(path.read_text() for path in SOURCE_DOC_PATHS)

    assert "never causes DES_time > actual_time" not in combined
    assert "XU safely omitted for roofline bound" not in combined
    assert "Setting to zero ensures the bound" not in combined
