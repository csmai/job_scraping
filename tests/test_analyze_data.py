import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from scripts.analyze_data import (
    fetch_data_from_db,
    preprocess_tech_stack,
    analyze_tech_stack,
)


def test_fetch_data_from_db():
    # Create a MagicMock for the create_engine function
    mock_create_engine = MagicMock()

    # Use the MagicMock to simulate the execute and fetchall methods
    mock_create_engine.return_value.__enter__.return_value.execute.return_value.fetchall.return_value = [
        ("Python Developer", '["Python", "Java"]')
    ]

    # Call the function with the mock
    table_names = ["python_developer_nof", "python_developer_prf"]
    result = fetch_data_from_db(table_names)

    # Define the expected DataFrame based on the mock data
    expected_data = pd.DataFrame(
        {"job_title": ["Python Developer"], "job_tech_stack": [["Python", "Java"]]}
    )

    pd.testing.assert_frame_equal(result, expected_data)


def test_preprocess_tech_stack():
    input_series = pd.Series(
        [
            '["Python", "SQL"]',
            '["Java", "Python", "Angol (B2)"]',
            "[]",
        ]
    )
    expected_series = pd.Series(
        [["Python", "SQL"], ["Java", "Python", "Angol (B2)"], []]
    )

    result = preprocess_tech_stack(input_series)

    pd.testing.assert_series_equal(result, expected_series)


@patch("scripts.analyze_data.preprocess_tech_stack")
def test_analyze_tech_stack(mock_preprocess_tech_stack):
    mocked_data = pd.DataFrame(
        {
            "job_title": [
                "Python Developer",
                "Senior Python Developer",
                "Python Developer",
            ],
            "job_tech_stack": [
                '["Python", "SQL"]',
                '["Java", "Python", "Angol (B2)"]',
                '[""]',
            ],
        }
    )
    mock_preprocess_tech_stack.return_value = pd.Series(
        [["Python", "SQL"], ["Java", "Python", "Angol (B2)"], []]
    )

    tech_stack, tech_stack_counts = analyze_tech_stack(mocked_data)

    expected_tech_stack = ["PYTHON", "SQL", "JAVA", "PYTHON", "ANGOL"]
    expected_tech_stack_counts = pd.Series(
        {"PYTHON": 2, "SQL": 1, "JAVA": 1, "ANGOL": 1}
    )

    assert tech_stack == expected_tech_stack
    pd.testing.assert_series_equal(
        tech_stack_counts, expected_tech_stack_counts, check_names=False
    )


# Add more tests for visualize_tech_stack if needed

if __name__ == "__main__":
    pytest.main()
