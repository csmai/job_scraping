from bs4 import BeautifulSoup
from typing import List, Tuple, Iterable, Iterator

from base_scraper import Scraper


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
            self.logger.info("img found")
            # Get the parent span
            parent_span = tech_img.parent

            # Find the next sibling div at the same level as the parent span
            next_div = parent_span.find_next_sibling("div")

            if next_div:
                # Get all the spans inside the div and extract their text
                spans = next_div.find_all("span")
                tech_stack_list = [str(span.get_text().strip()) for span in spans]

            else:
                self.logger.info("No next sibling div found.")
        else:
            self.logger.info('Image with alt="technologies" not found.')
        return tech_stack_list
