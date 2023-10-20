import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.engine import Connection
from scripts.analyze_data import (
    fetch_data_from_db,
    preprocess_tech_stack,
    analyze_tech_stack,
)

# Define common data for testing
job_tech_stack_str_list = [
    '["Python", "SQL"]',
    '["Java", "Python", "Angol (B2)"]',
    "[]",
]
job_tech_stack_list_list = [["Python", "SQL"], ["Java", "Python", "Angol (B2)"], []]
job_title_list = [
    "Python Developer",
    "Senior Python Developer",
    "Python Developer",
]


@patch("sqlalchemy.create_engine")
def test_fetch_data_from_db(mock_create_engine):
    # Call the function with the table_names in config
    table_names = ["python_developer_nof", "python_developer_prf"]
    combined_result = fetch_data_from_db(table_names)

    # Ensure that there is a minimum of one row of data in the combined table
    table_data = combined_result["job_title"].notnull()
    assert len(table_data) >= 1

    # Define the expected classes for each column type
    expected_column_types = {
        "job_title": str,
        "company_name": str,
        "job_summary": str,
        "job_link": str,
        "job_tech_stack": str,
    }

    # Ensure that there is a minimum of one row of data in each table
    for column_name, expected_class in expected_column_types.items():
        actual_class = type(combined_result[column_name].iloc[0])
        assert actual_class == expected_class


def test_filter_jobs_by_title():
    pass


def test_preprocess_tech_stack():
    input_series = pd.Series(job_tech_stack_str_list)
    expected_series = pd.Series(job_tech_stack_list_list)

    result = preprocess_tech_stack(input_series)

    pd.testing.assert_series_equal(result, expected_series)


@patch("scripts.analyze_data.preprocess_tech_stack")
def test_analyze_tech_stack(mock_preprocess_tech_stack):
    mocked_data = pd.DataFrame(
        {
            "job_title": job_title_list,
            "job_tech_stack": job_tech_stack_str_list,
        }
    )
    mock_preprocess_tech_stack.return_value = pd.Series(job_tech_stack_list_list)

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
