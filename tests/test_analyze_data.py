import pandas as pd
import pytest
from config import search_kws
from unittest.mock import patch
from scripts.analyze_data import (
    fetch_data_from_db,
    preprocess_tech_stack,
    analyze_tech_stack,
    filter_jobs_by_title,
)


# Define fixtures to provide the common data
@pytest.fixture
def job_tech_stack_str_data():
    return [
        '["Python", "SQL"]',
        '["Java", "Python", "Angol (B2)"]',
        "[]",
    ]


@pytest.fixture
def job_tech_stack_list_data():
    return [["Python", "SQL"], ["Java", "Python", "Angol (B2)"], []]


@pytest.fixture
def job_title_data():
    return [
        "Python Developer",
        "Senior Python Developer",
        "Python Developer",
    ]


@patch("sqlalchemy.create_engine")
def test_fetch_data_from_db(
    mock_create_engine,
):
    """Check The types and column names of the data from the database"""
    # get table name constants
    table_names = [
        f"{search_kws[0].lower()}_{search_kws[1].lower()}_prf",
        f"{search_kws[0].lower()}_{search_kws[1].lower()}_nof",
    ]
    # Call the function with the table_names in config
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

    # Check each column type and name in the dataframe
    for column_name, expected_class in expected_column_types.items():
        actual_class = type(combined_result[column_name].iloc[0])
        actual_name = combined_result[column_name].name
        assert actual_class == expected_class
        assert actual_name == column_name


def test_filter_jobs_by_title(job_tech_stack_str_data):
    """Check if Invalid title and its tech stack  is filtered out"""
    tech_stack_to_filter = job_tech_stack_str_data
    senior_title = f"Senior {search_kws[1].title()} of {search_kws[0].lower()}"
    simple_title = f"{search_kws[0]} {search_kws[1]}"
    title_to_filter = [
        senior_title,
        "INVALID",
        simple_title,
    ]

    df_to_filter = pd.DataFrame(
        {
            "job_title": title_to_filter,
            "job_tech_stack": tech_stack_to_filter,
        }
    )
    expected_df = pd.DataFrame(
        {
            "job_title": [
                senior_title,
                simple_title,
            ],
            "job_tech_stack": [
                '["Python", "SQL"]',
                "[]",
            ],
        }
    )
    result_df = filter_jobs_by_title(df_to_filter)
    # Check if the result dataframe equals to the expected ignoring the index
    pd.testing.assert_frame_equal(
        result_df.reset_index(drop=True), expected_df.reset_index(drop=True)
    )


def test_preprocess_tech_stack(job_tech_stack_str_data, job_tech_stack_list_data):
    input_series = pd.Series(job_tech_stack_str_data)
    expected_series = pd.Series(job_tech_stack_list_data)

    result = preprocess_tech_stack(input_series)

    pd.testing.assert_series_equal(result, expected_series)


@patch("scripts.analyze_data.preprocess_tech_stack")
def test_analyze_tech_stack(
    mock_preprocess_tech_stack,
    job_tech_stack_str_data,
    job_tech_stack_list_data,
    job_title_data,
):
    mocked_data = pd.DataFrame(
        {
            "job_title": job_title_data,
            "job_tech_stack": job_tech_stack_str_data,
        }
    )
    mock_preprocess_tech_stack.return_value = pd.Series(job_tech_stack_list_data)

    tech_stack, tech_stack_counts = analyze_tech_stack(mocked_data)

    expected_tech_stack = ["PYTHON", "SQL", "JAVA", "PYTHON", "ANGOL"]
    expected_tech_stack_counts = pd.Series(
        {"PYTHON": 2, "SQL": 1, "JAVA": 1, "ANGOL": 1}
    )

    assert tech_stack == expected_tech_stack
    pd.testing.assert_series_equal(
        tech_stack_counts, expected_tech_stack_counts, check_names=False
    )


if __name__ == "__main__":
    pytest.main()
