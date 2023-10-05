import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

# Use the configured logger from main.py
logger = logging.getLogger(__name__)
# Set user agent in headers to mimic a web browser request
from common_utils import headers


# Function to extract job titles and job links from the soup
def extract_job_info_from_result(soup):
    job_info = []
    logging.info("Start list creation: search soup")
    job_card_items = soup.select("ul.job-cards > li")
    logging.info("job_card_items found")
    for item in job_card_items:
        logging.debug("Processing item: %s", item)
        job_title, company_name, job_summary, job_link, job_tech_stack = [None] * 5

        if item.has_attr("data-prof-name"):
            job_title = str(item["data-prof-name"])
        if item.has_attr("data-item-brand"):
            company_name = str(item["data-item-brand"])
        if item.has_attr("data-item-brand"):
            job_summary = str(item["data-item-brand"])
        if item.has_attr("data-link"):
            job_link = str(item["data-link"])
            job_tech_stack = scrape_subpage(job_link)

        job_summary = item.find("div", class_="job-card__text").text.strip()

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


# Function to extract job tech stack from the soup
def extract_job_tech_stack_from_result(soup):
    tech_stack_list = []
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


# Function to scrape the subpage to get the tech stack
def scrape_subpage(url):
    page = requests.get(url, headers=headers)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        tech_stack_list = extract_job_tech_stack_from_result(soup)
        return tech_stack_list
    else:
        logging.warning(f"Failed to retrieve the page. Status code:{page.status_code}")
        return None


# Function to scrape the main page
def scrape_main_page(url):
    page = requests.get(url, headers=headers)
    if page.status_code == 200:
        soup = BeautifulSoup(page.text, "html.parser")
        job_info = extract_job_info_from_result(soup)
        logging.info("Successful soup creation")
        return pd.DataFrame(job_info)
    else:
        logging.warning(f"Failed to retrieve the page. Status code:{page.status_code}")
        return None
