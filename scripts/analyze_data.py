import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import os

# Define constants
DB_URI = f"postgresql://postgres:{os.getenv('P4PASSWD')}@localhost:5432/prof_scrape"
TABLE_NAMES = ["data_eng_prf", "data_eng_nof"]


def analyze_and_visualize_tech_stack(dataframe):
    # 'job_tech_stack' is a column containing tech stack information in the DataFrame
    tech_stack = [
        item for sublist in dataframe["job_tech_stack"].dropna() for item in sublist
    ]
    tech_stack_df = pd.DataFrame(tech_stack, columns=["tech"])
    tech_stack_counts = tech_stack_df["tech"].value_counts()

    # Plot the tech stack counts
    plt.figure(figsize=(10, 6))
    tech_stack_counts.plot(kind="bar")
    plt.xlabel("Tech Stack")
    plt.ylabel("Frequency")
    plt.title("Tech Stack Frequency")
    plt.show()
