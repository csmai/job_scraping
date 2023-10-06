import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os

# Define constants
DB_URI = f"postgresql://postgres:{os.getenv('P4PASSWD')}@localhost:5432/prof_scrape"
TABLE_NAMES = ["data_eng_prf", "data_eng_nof"]


# Function to fetch data from the database
def fetch_data_from_db():
    engine = create_engine(DB_URI)
    combined_data = pd.DataFrame()
    for table_name in TABLE_NAMES:
        query = f"SELECT * FROM {table_name};"
        data_df = pd.read_sql_query(query, engine)
        combined_data = pd.concat([combined_data, data_df], ignore_index=True)
    return combined_data


def analyze_and_visualize_tech_stack(dataframe):
    # Filter jobs with "Data" and "Engineer" in the job title
    filtered_jobs = dataframe[
        dataframe["job_title"].str.contains("Data", case=False)
        & dataframe["job_title"].str.contains("Engineer", case=False)
    ]
    # 'job_tech_stack' is a column containing tech stack information in the DataFrame
    tech_stack = [
        item.upper()
        for sublist in filtered_jobs["job_tech_stack"].dropna()
        for item in sublist
    ]
    # Replace variations of "ANGOL" (with B2, C1 suffix) with a single category "ANGOL"
    tech_stack = ["ANGOL" if "ANGOL" in tech else tech for tech in tech_stack]

    tech_stack_df = pd.DataFrame(tech_stack, columns=["tech"])
    tech_stack_counts = tech_stack_df["tech"].value_counts()

    # Print the top 10 most frequent tech stacks
    print("Top 10 most frequent tech stacks:")
    print(tech_stack_counts.head(10))

    # Calculate percentages
    total_techs = len(tech_stack)
    tech_stack_percentages = (tech_stack_counts / total_techs) * 100

    # Plot using Seaborn
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        x=tech_stack_percentages.head(10).index,
        y=tech_stack_percentages.head(10).values,
    )
    ax.set(xlabel="Tech Stack", ylabel="Percentage")
    ax.set_title("Top 10 Tech Stack Frequencies (Percentage)")
    plt.xticks(rotation=45, ha="right")

    plt.show()


if __name__ == "__main__":
    # Fetch data from the database
    combined_data = fetch_data_from_db()

    # # Save the combined data to a CSV (for analysis outside this script)
    # csv_filename = os.path.join(OUTPUT_CSV_FOLDER)
    # combined_data.to_csv(csv_filename, index=False)

    # Analyze the tech stack based on the fetched data
    analyze_and_visualize_tech_stack(combined_data)
