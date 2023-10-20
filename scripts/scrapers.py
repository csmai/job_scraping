import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Iterable, Iterator
from abc import ABC, abstractmethod
import pandas as pd
import logging
import os

# Define common user agent headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class Scraper(ABC):
    def __init__(self, url: str):
        self.logger = logging.getLogger(__name__)
        self.url = url

    @abstractmethod
    def find_job_items(soup: BeautifulSoup) -> Iterable:
        """Abstract method to find the job items"""
        pass

    @abstractmethod
    def get_job_info_data(self, item_iter: Iterator) -> Tuple[str, str, str, str, str]:
        """Abstract method to gather the data from a job item"""
        pass

    @abstractmethod
    def extract_job_tech_stack_from_result(self, soup: BeautifulSoup) -> List[str]:
        """Abstract method to get the tech stack"""
        pass

    def extract_job_summary_from_subpage(self, soup: BeautifulSoup) -> str:
        # By default no job summary from the subpage
        return ""

    def extract_company_name_from_subpage(self, soup: BeautifulSoup) -> str:
        # By default no company from the subpage
        return ""

    def extract_job_info_from_result(self, soup: BeautifulSoup) -> List[dict]:
        """Method to extract job information from the soup"""
        job_info: List[Dict] = []
        logging.info("Start list creation: search soup")
        job_items = self.find_job_items(soup)

        for item in job_items:
            logging.debug("Processing item: %s", item)
            job_title, company_name, job_summary, job_link, job_tech_stack = [None] * 5
            (
                job_title,
                company_name,
                job_summary,
                job_link,
                job_tech_stack,
            ) = self.get_job_info_data(item)

            job_info.append(
                {
                    "job_title": job_title,
                    "company_name": company_name,
                    "job_summary": job_summary,
                    "job_link": job_link,
                    "job_tech_stack": job_tech_stack,
                }
            )
        logging.info("job_info collected")
        return job_info

    def scrape_subpage(self, url: str) -> Tuple[str, str, List[str]]:
        """Function to scrape the subpage to get the company name, summary and tech stack"""
        page = requests.get(url, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")
            tech_stack_list = self.extract_job_tech_stack_from_result(soup)
            company_name = self.extract_company_name_from_subpage(soup)
            job_summary = self.extract_job_summary_from_subpage(soup)
            return company_name, job_summary, tech_stack_list
        else:
            logging.warning(
                f"Failed to retrieve the page. Status code:{page.status_code}"
            )
            return "", "", []

    def scrape_main_page(self) -> pd.DataFrame:
        """Method to scrape the main page"""
        page = requests.get(self.url, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")
            job_info = self.extract_job_info_from_result(soup)
            logging.info("Successful soup creation")
            return pd.DataFrame(job_info)
        else:
            logging.warning(
                f"Failed to retrieve the page. Status code:{page.status_code}"
            )
            return pd.DataFrame()


class PrfScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def find_job_items(self, soup: BeautifulSoup) -> Iterable:
        """Method to find the job items"""
        return soup.select("ul.job-cards > li")

    def get_job_info_data(self, item_iter: Iterator) -> Tuple[str, str, str, str, str]:
        """Method to gather the data for a job item"""

        if item_iter.has_attr("data-prof-name"):
            job_title = str(item_iter["data-prof-name"])
        if item_iter.has_attr("data-item-brand"):
            company_name = str(item_iter["data-item-brand"])
        if item_iter.has_attr("data-item-brand"):
            job_summary = str(item_iter["data-item-brand"])
        if item_iter.has_attr("data-link"):
            job_link = str(item_iter["data-link"])
            job_tech_stack = self.scrape_subpage(job_link)[2]

        job_summary = item_iter.find("div", class_="job-card__text").text.strip()
        return job_title, company_name, job_summary, job_link, job_tech_stack

    def extract_job_tech_stack_from_result(self, soup: BeautifulSoup) -> List[str]:
        """Method to extract job tech stack from the soup"""
        tech_stack_list: List[str] = []
        tech_img = soup.find("img", alt="technologies")
        if tech_img:
            logging.info("img found")
            # Get the parent span
            parent_span = tech_img.parent

            # Find the next sibling div at the same level as the parent span
            next_div = parent_span.find_next_sibling("div")

            if next_div:
                # Get all the spans inside the div and extract their text
                spans = next_div.find_all("span")
                tech_stack_list = [str(span.get_text().strip()) for span in spans]

            else:
                logging.info("No next sibling div found.")
        else:
            logging.info('Image with alt="technologies" not found.')
        return tech_stack_list


class NofScraper(Scraper):
    def __init__(self, url: str):
        super().__init__(url)

    def find_job_items(self, soup: BeautifulSoup) -> Iterable:
        """Abstract method to find the job items"""
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
            logging.info("li_elements not found in musts section")
        return tech_stack_list

    def extract_job_summary_from_subpage(self, soup: BeautifulSoup) -> str:
        """Method to extract job summary from the soup"""
        job_summary: str = ""

        # Find the desired <h2> element
        h2_elements = soup.find_all("h2")
        for h2 in h2_elements:
            if "projekt r" in h2.get_text().strip():
                logging.info("'projekt r' text found from 'projekt rövid leírása'")
                # Get the next sibling element (which contains the desired text)
                next_element = h2.find_next_sibling("nfj-read-more")
                if next_element and next_element.div:
                    job_summary = next_element.div.get_text(strip=True)
                    logging.info("Next element and its div is found")
                    break
                else:
                    logging.info(
                        "Next element or its div of 'projekt r's h2 is not found."
                    )
            else:
                logging.info("'projekt r' text from 'projekt rövid leírása' not found")
        return job_summary

    def extract_company_name_from_subpage(self, soup: BeautifulSoup) -> str:
        """Return company name based on id"""
        return soup.find("a", id="postingCompanyUrl").text.strip()
