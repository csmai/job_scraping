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


# Function to perform scraping
def perform_scraping(prefix):
    # Initialize an empty DataFrame to store all job info
    all_job_info_df = pd.DataFrame()
    # Perform scraping with rate limiting
    logging.info(f"Begin the {prefix} scraper script")

    for page_num in range(1, 2 + (prefix == "prf") * 3):
        # construct the search URL
        if prefix == "prf":
            URL = f"{PRF_URL}{page_num},10,23,{search_kws[0].lower()}%20{search_kws[1].lower()}"
            scrape_function = prf_scrape_main_page
        elif prefix == "nof":
            URL = f"{NOF_URL}{search_kws[0]}?criteria=keyword%3D{search_kws[1]}&page={page_num}"
            scrape_function = nof_scrape_main_page
        try:
            # conduct a request of the stated URL above:
            job_info_df = scrape_function(URL)

            if job_info_df is not None:
                # Convert tech stack strings to valid JSON arrays
                job_info_df["job_tech_stack"] = job_info_df["job_tech_stack"].apply(
                    lambda x: json.dumps(x)
                )
                print(type(job_info_df["job_tech_stack"].iloc[0]))
                print((job_info_df["job_tech_stack"].iloc[0]))
                # Append the scraped data to the all_job_info_df
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

    # Begin the database load
    table_name = f"{search_kws[0].lower()}_{search_kws[1].lower()}_{prefix}"
    logging.info(f"Begin the database load for {prefix} prefix, to table {table_name}")
    engine = create_engine(DB_URI)
    all_job_info_df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
    )
    logging.info(f"Data loaded into '{table_name}' table.")

    # Save to CSV
    csv_filename = os.path.join(
        OUTPUT_CSV_FOLDER,
        f"{prefix}_{search_kws[0].lower()}_{search_kws[1].lower()}_job_data.csv",
    )
    all_job_info_df.to_csv(csv_filename, index=False)
    logging.info(f"Data loaded into {csv_filename}.")


if __name__ == "__main__":
    # Perform scraping for prf website
    perform_scraping("prf")

    # Perform scraping for nof website
    perform_scraping("nof")

    # Analyze and Visualize the Data
    subprocess.run(["python", os.path.join("scripts", "analyze_data.py")])
