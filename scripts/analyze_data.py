from common_utils import search_kws
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os
import ast
import logging

# Configure logging to use the same file handler and level as main.py
logging.basicConfig(
    level=logging.INFO, filename="output.log", filemode="w", encoding="utf-8"
)
logger = logging.getLogger(__name__)

# Define Database URI
DB_URI = f"postgresql://postgres:{os.getenv('P4PASSWD')}@localhost:5432/prof_scrape"


def fetch_data_from_db(table_names):
    """Function to fetch data from the database"""
    engine = create_engine(DB_URI)
    combined_data = pd.DataFrame()
    for table in table_names:
        query = f"SELECT * FROM {table};"
        data_df = pd.read_sql_query(query, engine)
        combined_data = pd.concat([combined_data, data_df], ignore_index=True)
    return combined_data


def preprocess_tech_stack(str_series):
    """Convert the json strings to actual lists using ast.literal_eval"""
    logging.info(f"Type of first rows tech stack :{type(str_series.iloc[0])}")
    logging.info(f"first row of tech stack :{str_series.iloc[0]}")
    try:
        list_series = str_series.apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else x
        )
    except Exception as e:
        logging.info(f"An error occurred: {str(e)}")
    return list_series


def analyze_tech_stack(dataframe):
    # Filter jobs with the 2 search keywords in the job title
    filtered_jobs = dataframe[
        dataframe["job_title"].str.contains(search_kws[0], case=False)
        & dataframe["job_title"].str.contains(search_kws[1], case=False)
    ]

    # Convert the json strings to actual lists
    tech_stack_list = preprocess_tech_stack(filtered_jobs["job_tech_stack"])
    # Get upper case and remove missing data
    tech_stack = [
        item.upper() for sublist in tech_stack_list.dropna() for item in sublist
    ]
    # Replace variations of "ANGOL" (with B2, C1 suffix) with a single category "ANGOL"
    tech_stack = ["ANGOL" if "ANGOL" in tech else tech for tech in tech_stack]

    tech_stack_df = pd.DataFrame(tech_stack, columns=["tech"])
    tech_stack_counts = tech_stack_df["tech"].value_counts()

    # Log the top 15 most frequent tech stacks
    logging.info(f"{search_kws}Top 15 most frequent tech stacks:")
    logging.info(tech_stack_counts.head(15))
    return tech_stack, tech_stack_counts


def visualize_tech_stack(tech_stack, tech_stack_counts):
    # Calculate percentages
    total_techs = len(tech_stack)
    tech_stack_percentages = (tech_stack_counts / total_techs) * 100

    # Create a colorful horizontal bar plot in Seaborn
    plt.figure(figsize=(15, 6))
    colors = sns.color_palette("ch:s=0.25,rot=-0.25", len(tech_stack))

    ax = sns.barplot(
        x=tech_stack_percentages.head(15).values,
        y=tech_stack_percentages.head(15).index,
        palette=colors,
    )

    # Add percentages as text annotations
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(
            f"{width:.2f}%",
            xy=(width, p.get_y() + p.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=10,
            color="black",
        )

    ax.set(xlabel="Percentage", ylabel="Tech Stack")
    ax.set_title(f"{search_kws[0]} {search_kws[1]}'s Top 15 Tech Stack")

    # Hide the frame (spines) and x-axis
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.axes.get_xaxis().set_visible(False)

    plt.show()
    return


if __name__ == "__main__":
    # get table name constants
    table_names = [
        f"{search_kws[0].lower()}_{search_kws[1].lower()}_prf",
        f"{search_kws[0].lower()}_{search_kws[1].lower()}_nof",
    ]
    # Fetch data from the database
    combined_data = fetch_data_from_db(table_names)

    # Analyze the tech stack based on the fetched data
    tech_stack, tech_stack_counts = analyze_tech_stack(combined_data)
    visualize_tech_stack(tech_stack, tech_stack_counts)
