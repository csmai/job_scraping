import os
import sys
import pytest
from bs4 import BeautifulSoup

# Get the absolute path of the current script
current_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Calculate the path to the 'scripts' directory which is at the same level as 'tests'
scripts_path = os.path.join(current_parent_dir, "scripts")
# Add the 'scripts' directory to sys.path
sys.path.append(scripts_path)

from scripts.pagescrapers.prf_scraper import PrfScraper


# Define a fixture to create a sample BeautifulSoup object for testing
@pytest.fixture
def sample_soup():
    sample_html = """
    <ul class="job-cards">
        <li data-prof-name="Job Title 1" data-item-brand="Company 1" data-link="https://example.com/job_link_1">
            <div class="job-card__text">Job Summary 1</div>
        </li>
        <li data-prof-name="Job Title 2" data-item-brand="Company 2" data-link="https://example.com/job_link_2">
            <div class="job-card__text">Job Summary 2</div>
        </li>
    </ul>
    """
    return BeautifulSoup(sample_html, "html.parser")


# Define test cases for the PrfScraper class
def test_find_job_items(sample_soup):
    scraper = PrfScraper("https://example.com")
    job_items = list(scraper.find_job_items(sample_soup))
    assert len(job_items) == 2


def test_get_job_info_data(sample_soup):
    scraper = PrfScraper("https://example.com")
    item_iter = sample_soup.find_all("li")[0]
    (
        job_title,
        company_name,
        job_summary,
        job_link,
        job_tech_stack,
    ) = scraper.get_job_info_data(item_iter)
    assert job_title == "Job Title 1"
    assert company_name == "Company 1"
    assert job_summary == "Job Summary 1"
    assert job_link == "https://example.com/job_link_1"


def test_extract_job_tech_stack_from_result(sample_soup):
    scraper = PrfScraper("https://example.com")
    tech_stack_list = scraper.extract_job_tech_stack_from_result(sample_soup)
    assert tech_stack_list == []


# Run the tests
if __name__ == "__main__":
    pytest.main()
