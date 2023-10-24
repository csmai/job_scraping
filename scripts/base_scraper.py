import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Iterable, Iterator
from abc import ABC, abstractmethod
import pandas as pd
import logging

# Define common user agent headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class Scraper(ABC):
    def __init__(self, url: str):
        self.logger = logging.getLogger(__name__)
        self.url = url

    @abstractmethod
    def find_job_items(self, soup: BeautifulSoup) -> Iterable:
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
        """Method to extract job summary from the subpage"""
        # By default no job summary from the subpage
        return ""

    def extract_company_name_from_subpage(self, soup: BeautifulSoup) -> str:
        """Method to extract company name from the subpage"""
        # By default no company from the subpage
        return ""

    def extract_job_info_from_result(self, soup: BeautifulSoup) -> List[dict]:
        """Method to extract job information from the soup"""
        job_info: List[Dict] = []
        self.logger.info("Start list creation: search soup")
        job_items = self.find_job_items(soup)

        for item in job_items:
            self.logger.debug("Processing item: %s", item)
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
        self.logger.info("job_info collected")
        return job_info

    def scrape_subpage(self, url: str) -> Tuple[str, str, List[str]]:
        """Method to scrape the subpage to get the company name, summary, and tech stack"""
        page = requests.get(url, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")
            tech_stack_list = self.extract_job_tech_stack_from_result(soup)
            company_name = self.extract_company_name_from_subpage(soup)
            job_summary = self.extract_job_summary_from_subpage(soup)
            return company_name, job_summary, tech_stack_list
        else:
            self.logger.warning(
                f"Failed to retrieve the page. Status code: {page.status_code}"
            )
            return "", "", []

    def scrape_main_page(self) -> pd.DataFrame:
        """Method to scrape the main page"""
        page = requests.get(self.url, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text, "html.parser")
            job_info = self.extract_job_info_from_result(soup)
            self.logger.info("Successful soup creation")
            return pd.DataFrame(job_info)
        else:
            self.logger.warning(
                f"Failed to retrieve the page. Status code: {page.status_code}"
            )
            return pd.DataFrame()
