import pandas as pd
import os
import json
from unittest.mock import patch
import pytest
import urllib.parse
import sys

# Get the absolute path of the current script
current_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Calculate the path to the 'scripts' directory which is at the same level as 'tests'
scripts_path = os.path.join(current_parent_dir, "scripts")
# Add the 'scripts' directory to sys.path
sys.path.append(scripts_path)

from scripts.pagescrapers.nof_scraper import NofScraper
from scripts.pagescrapers.prf_scraper import PrfScraper
from scripts.main import (
    construct_url,
    get_scraper,
    convert_series_to_json,
    perform_scraping,
)


def test_construct_url():
    prf_url = construct_url("prf", 1)
    nof_url = construct_url("nof", 1)

    assert urllib.parse.urlparse(prf_url).scheme in ("http", "https")
    assert urllib.parse.urlparse(nof_url).scheme in ("http", "https")


def test_get_scraper():
    prf_scraper = get_scraper("prf", "https://example.com/prf/")
    nof_scraper = get_scraper("nof", "https://example.com/nof/")

    assert type(type(prf_scraper)) is type(PrfScraper)
    assert type(type(nof_scraper)) is type(NofScraper)


def test_convert_series_to_json():
    series = pd.Series(["a", "b", "c"])
    result = convert_series_to_json(series)
    assert isinstance(result, pd.Series)
    assert result[0] == json.dumps("a")


# Slow test, disable to run fast
def test_perform_scraping():
    with patch("time.sleep", return_value=None):
        job_info_df = perform_scraping("prf")
        assert isinstance(job_info_df, pd.DataFrame)
        assert len(job_info_df) > 0


if __name__ == "__main__":
    pytest.main()
