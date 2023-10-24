from bs4 import BeautifulSoup
from typing import List, Tuple, Iterable, Iterator
import os

from base_scraper import Scraper


class NofScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def find_job_items(self, soup: BeautifulSoup) -> Iterable:
        """Method to find the job items"""
        return soup.find_all("a", class_="posting-list-item")

    def get_job_info_data(self, item_iter: Iterator) -> Tuple[str, str, str, str, str]:
        """Method to gather the data for a job item"""
        job_title = item_iter.find("h3", class_="posting-title__position").text.strip()
        # Define base url based on envrinment variable: slice the first 23 characters
        nof_url_base = os.getenv("NOF_URL")[:23]
        if item_iter.has_attr("href"):
            job_link = f'{nof_url_base}{item_iter["href"]}'
            company_name, job_summary, job_tech_stack = self.scrape_subpage(job_link)
        return job_title, company_name, job_summary, job_link, job_tech_stack

    def extract_job_tech_stack_from_result(self, soup: BeautifulSoup) -> List[str]:
        """Method to extract job tech stack from the soup"""
        tech_stack_list: List[str] = []
        # Find the musts_section
        musts_section = soup.find("section", {"branch": "musts"})

        # Find all <li> elements within the musts_section
        li_elements = musts_section.find_all("li")

        # Extract and print the text from each <li> element
        if li_elements:
            tech_stack_list = [str(li.get_text().strip()) for li in li_elements]
        else:
            self.logger.info("li_elements not found in musts section")
        return tech_stack_list

    def extract_job_summary_from_subpage(self, soup: BeautifulSoup) -> str:
        """Method to extract job summary from the soup"""
        job_summary: str = ""

        # Find the desired <h2> element
        h2_elements = soup.find_all("h2")
        for h2 in h2_elements:
            if "projekt r" in h2.get_text().strip():
                self.logger.info("'projekt r' text found from 'projekt rövid leírása'")
                # Get the next sibling element (which contains the desired text)
                next_element = h2.find_next_sibling("nfj-read-more")
                if next_element and next_element.div:
                    job_summary = next_element.div.get_text(strip=True)
                    self.logger.info("Next element and its div is found")
                    break
                else:
                    self.logger.info(
                        "Next element or its div of 'projekt r's h2 is not found."
                    )
            else:
                self.logger.info(
                    "'projekt r' text from 'projekt rövid leírása' not found"
                )
        return job_summary

    def extract_company_name_from_subpage(self, soup: BeautifulSoup) -> str:
        """Return company name based on id"""
        return soup.find("a", id="postingCompanyUrl").text.strip()
