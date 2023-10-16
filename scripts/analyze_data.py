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
    print(tech_stack_counts.head(19))

    # Calculate percentages
    total_techs = len(tech_stack)
    tech_stack_percentages = (tech_stack_counts / total_techs) * 100

    # Create a colorful horizontal bar plot in Seaborn
    plt.figure(figsize=(10, 6))
    colors = sns.color_palette("ch:s=0.25,rot=-0.25", len(tech_stack))

    ax = sns.barplot(
        x=tech_stack_percentages.head(19).values,
        y=tech_stack_percentages.head(19).index,
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
    ax.set_title("Top 10 Tech Stack Frequencies (Percentage)")

    # Hide the frame (spines) and x-axis
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.axes.get_xaxis().set_visible(False)

    plt.show()

    # Save the figure to a file in the "presentation" folder
    script_dir = os.path.dirname(os.path.realpath(__file__))
    presentation_folder = os.path.join(script_dir, "..", "presentation")
    if not os.path.exists(presentation_folder):
        os.makedirs(presentation_folder)

    graph_filename = os.path.join(presentation_folder, "res_tech_stack_graph.png")
    plt.savefig(graph_filename)
    plt.close()


if __name__ == "__main__":
    # Fetch data from the database
    combined_data = fetch_data_from_db()

    # # Save the combined data to a CSV (for analysis outside this script)
    # csv_filename = os.path.join(OUTPUT_CSV_FOLDER)
    # combined_data.to_csv(csv_filename, index=False)

    # Analyze the tech stack based on the fetched data
    analyze_and_visualize_tech_stack(combined_data)
