import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple
import pandas as pd
import logging
import os


# Set user agent in headers to mimic a web browser request
from common_utils import headers

# Use the configured logger from main.py
logger = logging.getLogger(__name__)
# Define base url based on envrinment variable: slice the first 23 characters
NOF_URL_BASE = os.getenv("NOF_URL")[:23]


def extract_job_info_from_result(soup: BeautifulSoup) -> List[Dict]:
    """Function to extract job titles and job links from the soup"""
    job_info: List[Dict] = []
    logging.info("Start list creation: search soup")
    job_items = soup.find_all("a", class_="posting-list-item")
    logging.info("job_card_items found")
    for item in job_items:
        logging.debug("Processing item: %s", item)
        job_title, company_name, job_summary, job_link, job_tech_stack = [None] * 5

        job_title = item.find("h3", class_="posting-title__position").text.strip()
        if item.has_attr("href"):
            job_link = f'{NOF_URL_BASE}{item["href"]}'
            company_name, job_summary, job_tech_stack = scrape_subpage(job_link)

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


def extract_job_tech_stack_from_result(soup: BeautifulSoup) -> List[str]:
    """Function to extract job tech stack from the soup"""
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


def extract_job_summary_from_result(soup: BeautifulSoup) -> str:
    """Function to extract job summary from the soup"""
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
                logging.info("Next element or its div of 'projekt r's h2 is not found.")
        else:
            logging.info("'projekt r' text from 'projekt rövid leírása' not found")
    return job_summary


def scrape_subpage(url: str) -> Tuple[str, str, List[str]]:
    """Function to scrape the subpage to get the tech stack"""
    page = requests.get(url, headers=headers)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        tech_stack_list = extract_job_tech_stack_from_result(soup)
        company_name = soup.find("a", id="postingCompanyUrl").text.strip()
        job_summary = extract_job_summary_from_result(soup)
        return company_name, job_summary, tech_stack_list
    else:
        logging.warning(f"Failed to retrieve the page. Status code:{page.status_code}")
        return "", "", []


def scrape_main_page(url: str) -> pd.DataFrame:
    """Function to scrape the main page"""
    page = requests.get(url, headers=headers)
    logging.info("In the scraper function")
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        logging.info("Soup created")
        job_info = extract_job_info_from_result(soup)
        logging.info("Successful soup creation")
        return pd.DataFrame(job_info)
    else:
        logging.warning(f"Failed to retrieve the page. Status code:{page.status_code}")
        return pd.DataFrame()
