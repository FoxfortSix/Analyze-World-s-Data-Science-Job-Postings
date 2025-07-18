"""
This script analyzes data analyst job postings to find the most in-demand skills
and their associated median salaries. It loads a public dataset, processes the data,
groups skills by frequency and salary, maps skills to technology categories, and
visualizes the results in a scatter plot.
"""

# Importing necessary libraries
import ast  # For safely evaluating string representations of Python objects
import pandas as pd  # For data manipulation
import seaborn as sns  # For plotting
from datasets import load_dataset  # To load the dataset from HuggingFace
import matplotlib.pyplot as plt  # For plotting
from adjustText import adjust_text  # To prevent text overlap in plots
import numpy as np  # For numerical operations
from matplotlib.ticker import (
    PercentFormatter,
)  # For formatting axis ticks as percentages

# Load the dataset from HuggingFace
dataset = load_dataset("lukebarousse/data_jobs")
df = dataset["train"].to_pandas()  # Convert to pandas DataFrame

# Preprocessing
df["job_posted_date"] = pd.to_datetime(
    df["job_posted_date"]
)  # Convert date column to datetime
# Convert string representation of lists to actual Python lists
df["job_skills"] = df["job_skills"].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) else x
)

# Filter only Data Analyst jobs
df_da = df[df["job_title_short"] == "Data Analyst"].copy()
df_da = df_da.dropna(subset=["salary_year_avg"])  # Remove rows without salary info
df_da_explode = df_da.explode("job_skills")  # Expand each skill into its own row

# Group by skill to get count and median salary for each skill
df_da_group = (
    df_da_explode.groupby("job_skills")["salary_year_avg"]
    .agg(["count", "median"])
    .sort_values(by="count", ascending=False)
    .rename(columns={"count": "skill_count", "median": "median_salary"})
)

# Calculate the percentage of jobs requiring each skill
da_job_count = len(df_da)
df_da_group["skill_percent"] = df_da_group.skill_count / da_job_count * 100

# Filter to keep only skills that appear in more than 'skill_limit' percent of jobs
skill_limit = 5  # Minimum percent threshold for high-demand skills
df_da_high_demand_skill = df_da_group[df_da_group.skill_percent > skill_limit]

# Technology mapping: map each skill to its technology category
df_technology = df["job_type_skills"].drop_duplicates().dropna()

technology_dict = {}
for row in df_technology:
    row_dict = ast.literal_eval(row)  # Convert string to dictionary
    for key, value in row_dict.items():
        technology_dict.setdefault(key, []).extend(
            value
        )  # Add skills to each technology

# Remove duplicate skills within each technology
for key in technology_dict:
    technology_dict[key] = list(set(technology_dict[key]))

# Create a DataFrame mapping each skill to its technology
df_technology = pd.DataFrame(
    [(tech, skill) for tech, skills in technology_dict.items() for skill in skills],
    columns=["technology", "skills"],
)

# Merge skill statistics with technology mapping
df_DA_skills_tech = df_da_group.merge(
    df_technology, left_on="job_skills", right_on="skills"
)
# Keep only high-demand skills and remove duplicates
df_DA_skills_tech_high_demand = df_DA_skills_tech[
    df_DA_skills_tech["skill_percent"] > skill_limit
].drop_duplicates(subset="skills")

# Plotting
plt.figure(figsize=(14, 7))  # Set plot size
sns.set_theme(style="ticks")  # Set plot style
sns.despine()  # Remove top and right plot borders

# Scatter plot: skill percent vs. median salary, colored by technology
sns.scatterplot(
    data=df_DA_skills_tech_high_demand,
    x="skill_percent",
    y="median_salary",
    hue="technology",
    s=60,
)

# Add text labels for each skill point
texts = []
for _, row in df_DA_skills_tech_high_demand.iterrows():
    texts.append(
        plt.text(
            row["skill_percent"],
            row["median_salary"],
            row["skills"],
            fontsize=9,
            ha="center",
            va="center",
        )
    )

# Adjust text labels to avoid overlap, with short connecting lines
adjust_text(
    texts,
    arrowprops=dict(arrowstyle="-", color="gray", lw=0.6),
    expand_text=(1.05, 1.2),
    expand_points=(1.2, 1.4),
    force_text=0.5,
    force_points=0.2,
    only_move={"points": "y", "text": "xy"},
)

# Formatting axes and title
plt.xlabel("Percent of Data Analyst Jobs")  # X-axis label
plt.ylabel("Median Yearly Salary")  # Y-axis label
plt.title("Most Optimal Skills for Data Analysts in the World")  # Plot title
plt.legend(
    title="Technology", bbox_to_anchor=(1.05, 1), loc="upper left"
)  # Legend position

# Format y-axis as $K and x-axis as percent
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, pos: f"${int(y/1000)}K"))
ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))

plt.tight_layout()  # Adjust layout to fit everything
plt.show()  # Display the plot
