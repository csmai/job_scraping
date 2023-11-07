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


@pytest.fixture
def sample_html():
    # Replace this with a sample HTML content that you want to use for testing
    # For example, you can use a mock HTML file or create an HTML string for testing.
    return "<html><body><a class='posting-list-item'></a></body></html>"


@pytest.fixture
def scraper(sample_html):
    # Initialize the NofScraper with a sample URL
    scraper = NofScraper("https://example.com")
    # Mock the BeautifulSoup object with the sample HTML content
    scraper.soup = BeautifulSoup(sample_html, "html.parser")
    return scraper


def test_find_job_items(scraper):
    job_items = scraper.find_job_items(scraper.soup)
    assert len(job_items) == 1


def test_get_job_info_data(scraper):
    sample_html = """
    <a class='posting-list-item' href='/job/123'>
        <h3 class='posting-title__position'>Job Title</h3>
    </a>
    """
    scraper.soup = BeautifulSoup(sample_html, "html.parser")
    item_iter = scraper.find_job_items(scraper.soup)[0]
    (
        job_title,
        company_name,
        job_summary,
        job_link,
        job_tech_stack,
    ) = scraper.get_job_info_data(item_iter)

    assert job_title == "Job Title"
    assert company_name == ""  # Update with expected company name
    assert job_summary == ""  # Update with expected job summary
    assert job_link == "https://example.com/job/123"
    assert job_tech_stack == []  # Update with expected tech stack list


def test_extract_job_tech_stack_from_result(scraper):
    sample_html = """
    <section branch='musts'>
        <li>Technology 1</li>
        <li>Technology 2</li>
    </section>
    """
    scraper.soup = BeautifulSoup(sample_html, "html.parser")
    tech_stack_list = scraper.extract_job_tech_stack_from_result(scraper.soup)
    assert tech_stack_list == ["Technology 1", "Technology 2"]


def test_extract_job_summary_from_subpage(scraper):
    sample_html = """
    <h2>projekt rövid leírása</h2>
    <nfj-read-more><div>Job Summary Text</div></nfj-read-more>
    """
    scraper.soup = BeautifulSoup(sample_html, "html.parser")
    job_summary = scraper.extract_job_summary_from_subpage(scraper.soup)
    assert job_summary == "Job Summary Text"


def test_extract_company_name_from_subpage(scraper):
    sample_html = "<a id='postingCompanyUrl'>Company Name</a>"
    scraper.soup = BeautifulSoup(sample_html, "html.parser")
    company_name = scraper.extract_company_name_from_subpage(scraper.soup)
    assert company_name == "Company Name"


if __name__ == "__main__":
    pytest.main()
