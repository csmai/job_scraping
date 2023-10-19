import pandas as pd
import pytest
from unittest.mock import patch
from scripts.analyze_data import (
    fetch_data_from_db,
    preprocess_tech_stack,
    analyze_tech_stack,
)


# Mocked data for testing
@pytest.fixture
def mocked_data():
    return pd.DataFrame(
        {
            "job_title": ["Python Developer", "Java Developer"],
            "job_tech_stack": [["Python", "Java"], ["Java", "SQL"]],
        }
    )


# Mock the create_engine function
@pytest.fixture
def mock_create_engine():
    with patch("script_name.create_engine") as mock_engine:
        yield mock_engine


def test_fetch_data_from_db(mocked_data, mock_create_engine):
    mock_create_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [
        ("Python Developer", '["Python", "Java"]')
    ]

    table_names = [
        "python_developer_nof",
        "python_developer_prf",
    ]  # Update with your actual table names
    result = fetch_data_from_db(table_names)

    expected_data = pd.DataFrame(
        {"job_title": ["Python Developer"], "job_tech_stack": [["Python", "Java"]]}
    )

    pd.testing.assert_frame_equal(result, expected_data)


def test_preprocess_tech_stack():
    input_series = pd.Series(
        ['["Python", "Java"]', '["C++", "JavaScript"]', '["Ruby", "Rust"]']
    )
    expected_series = pd.Series(
        [["Python", "Java"], ["C++", "JavaScript"], ["Ruby", "Rust"]]
    )

    result = preprocess_tech_stack(input_series)

    pd.testing.assert_series_equal(result, expected_series)


def test_analyze_tech_stack(mocked_data):
    tech_stack, tech_stack_counts = analyze_tech_stack(mocked_data)

    expected_tech_stack = ["PYTHON", "JAVA", "JAVA", "SQL"]
    expected_tech_stack_counts = pd.Series([2, 1, 1], name="tech")

    assert tech_stack == expected_tech_stack
    pd.testing.assert_series_equal(tech_stack_counts, expected_tech_stack_counts)


# Add more tests for visualize_tech_stack if needed

if __name__ == "__main__":
    pytest.main()
