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

from scripts.pagescrapers.nof_scraper import NofScraper


# Define a fixture to create a sample BeautifulSoup object for testing
@pytest.fixture
def sample_soup():
    sample_html = "<html><body><a class='posting-list-item'></a></body></html>"
    # Initialize the NofScraper with a sample URL
    scraper = NofScraper("https://example.com")
    # Mock the BeautifulSoup object with the sample HTML content
    scraper.soup = BeautifulSoup(sample_html, "html.parser")
    return scraper


def test_find_job_items(sample_soup):
    job_items = sample_soup.find_job_items(sample_soup.soup)
    assert len(job_items) == 1


def test_extract_job_tech_stack_from_result(sample_soup):
    html_input = """
    <section branch='musts'>
        <li>Technology 1</li>
        <li>Technology 2</li>
    </section>
    """
    sample_soup.soup = BeautifulSoup(html_input, "html.parser")
    tech_stack_list = sample_soup.extract_job_tech_stack_from_result(sample_soup.soup)
    assert tech_stack_list == ["Technology 1", "Technology 2"]


def test_extract_job_summary_from_subpage(sample_soup):
    html_input = """
    <h2>projekt rövid leírása</h2>
    <nfj-read-more><div>Job Summary Text</div></nfj-read-more>
    """
    sample_soup.soup = BeautifulSoup(html_input, "html.parser")
    job_summary = sample_soup.extract_job_summary_from_subpage(sample_soup.soup)
    assert job_summary == "Job Summary Text"


def test_extract_company_name_from_subpage(sample_soup):
    html_input = "<a id='postingCompanyUrl'>Company Name</a>"
    sample_soup.soup = BeautifulSoup(html_input, "html.parser")
    company_name = sample_soup.extract_company_name_from_subpage(sample_soup.soup)
    assert company_name == "Company Name"


if __name__ == "__main__":
    pytest.main()
