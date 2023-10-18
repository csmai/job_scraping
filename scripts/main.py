from prf_search import scrape_main_page as prf_scrape_main_page
from nof_search import scrape_main_page as nof_scrape_main_page
from common_utils import search_kws
import pandas as pd
import time
import random
import logging
from sqlalchemy import create_engine
import os
import json
import subprocess
from typing import Optional


# Set up logging
logging.basicConfig(
    level=logging.INFO, filename="output.log", filemode="w", encoding="utf-8"
)
# Define constants
DB_URI = f"postgresql://postgres:{os.getenv('P4PASSWD')}@localhost:5432/prof_scrape"
PRF_URL = os.getenv("PRF_URL")
NOF_URL = os.getenv("NOF_URL")
OUTPUT_CSV_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "generated_csv_files"
)


def construct_url(prefix: str, page_num: int) -> Optional[str]:
    """Constructs the search URL based on the prefix and page number"""
    url: Optional[str] = None
    if prefix == "prf":
        url = f"{PRF_URL}{page_num},10,23,{search_kws[0].lower()}%20{search_kws[1].lower()}"
    elif prefix == "nof":
        url = f"{NOF_URL}{search_kws[0]}?criteria=keyword%3D{search_kws[1]}&page={page_num}"
    return url


def define_scraper_func(prefix: str) -> Optional[callable]:
    """Define the scraper function based on the prefix"""
    func: Optional[callable] = None
    if prefix == "prf":
        func = prf_scrape_main_page
    elif prefix == "nof":
        func = nof_scrape_main_page
    return func


def convert_series_to_json(series: Optional[pd.Series]) -> Optional[pd.Series]:
    """Convert a series of strings to valid JSON arrays"""
    if series is not None:
        series = series.apply(lambda x: json.dumps(x))
        logging.info(f"Type of first row: {type(series.iloc[0])}")
        logging.info(f"First Row: {series.iloc[0]}")
    else:
        logging.info(f"No Data about job's tech stack.")
    return series


def perform_scraping(prefix: str) -> pd.DataFrame:
    """Function to perform scraping with rate limiting"""
    # Initialize an empty DataFrame to store all job info
    all_job_info_df = pd.DataFrame()
    logging.info(f"Begin the {prefix} scraper script")
    for page_num in range(1, 2 + (prefix == "prf") * 3):
        search_url = construct_url(prefix, page_num)
        scrape_function = define_scraper_func(prefix)
        try:
            # Get the info of the job for this page using the stated URL above
            job_info_df = scrape_function(search_url)
            job_info_df["job_tech_stack"] = convert_series_to_json(
                job_info_df["job_tech_stack"]
            )
            # Add the data to all the job data
            if job_info_df is not None:
                all_job_info_df = pd.concat(
                    (all_job_info_df, job_info_df), ignore_index=True
                )
            # Wait for a random amount of time between 5 to 10 seconds before making the next request
            time.sleep(random.uniform(5, 10))

        except Exception as e:
            logging.exception("An error occurred: %s", str(e))

    logging.info(
        f"Scraping for {prefix} done. Number of data rows: {len(all_job_info_df)}"
    )
    return all_job_info_df


def load_data_to_db(prefix: str, df_to_load: pd.DataFrame) -> None:
    """Load all the job data for the given prefix to a database"""
    table_name = f"{search_kws[0].lower()}_{search_kws[1].lower()}_{prefix}"
    logging.info(f"Begin the database load for {prefix} prefix, to table {table_name}")
    engine = create_engine(DB_URI)
    df_to_load.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
    )
    logging.info(f"Data loaded into '{table_name}' table.")
    return


def load_data_to_csv(prefix: str, df_to_load: pd.DataFrame) -> None:
    """Load all the job data for the given prefix to a csv file"""
    csv_filename = os.path.join(
        OUTPUT_CSV_FOLDER,
        f"{prefix}_{search_kws[0].lower()}_{search_kws[1].lower()}_job_data.csv",
    )
    df_to_load.to_csv(csv_filename, index=False)
    logging.info(f"Data loaded into {csv_filename}.")
    return


def get_and_store_job_data(prefix: str) -> None:
    """Get and store all the job data for a website defined with a prefix"""

    # Perform scraping with rate limiting"
    all_job_info_df = perform_scraping(prefix)

    # Load data to the database
    load_data_to_db(prefix, all_job_info_df)

    # Save data to CSV
    load_data_to_csv(prefix, all_job_info_df)


if __name__ == "__main__":
    # Get and store all the job data from prf and nof websites
    get_and_store_job_data("prf")
    get_and_store_job_data("nof")

    # Analyze and Visualize the Data
    subprocess.run(["python", os.path.join("scripts", "analyze_data.py")])
