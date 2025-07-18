"""
This script analyzes a dataset of data job postings to find:
1. The top 10 highest paid skills for Data Analyst roles.
2. The top 10 most in-demand skills for Data Analyst roles.
It then visualizes both lists using bar plots.
"""

# Importing necessary libraries
import ast  # For safely evaluating string representations of Python objects
import pandas as pd  # For data manipulation and analysis
import seaborn as sns  # For data visualization
from datasets import load_dataset  # For loading datasets from the Hugging Face Hub
import matplotlib.pyplot as plt  # For plotting graphs

# Load the dataset from Hugging Face
dataset = load_dataset("lukebarousse/data_jobs")
# Convert the 'train' split of the dataset to a pandas DataFrame
df = dataset["train"].to_pandas()

# Convert the 'job_posted_date' column to datetime format for easier handling
df["job_posted_date"] = pd.to_datetime(df["job_posted_date"])

# Convert the 'job_skills' column from string to Python list (if not missing)
df["job_skills"] = df["job_skills"].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) else x
)

# Filter the DataFrame to only include Data Analyst job postings
df_da = df[df.job_title_short == "Data Analyst"]

# Expand the 'job_skills' lists so each skill gets its own row
df_da = df_da.explode("job_skills")

# Show the first 5 rows of salary and skills (for quick inspection)
df_da[["salary_year_avg", "job_skills"]].head(5)

# Group by skill and calculate:
# - 'count': number of times each skill appears
# - 'median': median salary for each skill
# Sort by median salary (highest first)
df_da_top_pay = (
    df_da.groupby("job_skills")["salary_year_avg"]
    .agg(["count", "median"])
    .sort_values(by="median", ascending=False)
)

# Keep only the top 10 highest paid skills
df_da_top_pay = df_da_top_pay.head(10)

# Group by skill and calculate:
# - 'count': number of times each skill appears
# - 'median': median salary for each skill
# Sort by count (most in-demand skills first)
df_da_skills = (
    df_da.groupby("job_skills")["salary_year_avg"]
    .agg(["count", "median"])
    .sort_values(by="count", ascending=False)
)
# Keep the top 10 most in-demand skills, then sort them by median salary
df_da_skills = df_da_skills.head(10).sort_values(by="median", ascending=False)

# Create two subplots (one above the other)
fig, ax = plt.subplots(2, 1)
# Set the visual style for the plots
sns.set_theme(style="ticks")

# Plot the top 10 highest paid skills
sns.barplot(
    data=df_da_top_pay,
    x="median",  # Median salary on the x-axis
    y=df_da_top_pay.index,  # Skill names on the y-axis
    ax=ax[0],
    hue="median",  # Color bars by median salary
    palette="dark:blue_r",
    legend="",  # No legend
)

# Plot the top 10 most in-demand skills
sns.barplot(
    data=df_da_skills,
    x="median",  # Median salary on the x-axis
    y=df_da_skills.index,  # Skill names on the y-axis
    ax=ax[1],
    hue="median",  # Color bars by median salary
    palette="light:blue",
    legend="",  # No legend
)

# Make sure both plots have the same x-axis range for easy comparison
ax[1].set_xlim(ax[0].get_xlim())

# Set titles and labels for the first plot (highest paid skills)
ax[0].set_title("Top 10 Highest Paid Skills for Data Analyst")
ax[0].set_xlabel("")
ax[0].set_ylabel("")
# Format x-axis labels as thousands of dollars (e.g., $80K)
ax[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${int(x/1000)}K"))

# Set titles and labels for the second plot (most in-demand skills)
ax[1].set_title("Top 10 Most in Demand Skills for Data Analyst")
ax[1].set_xlabel("")
ax[1].set_ylabel("")
# Format x-axis labels as thousands of dollars
ax[1].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${int(x/1000)}K"))

# Adjust layout so plots don't overlap
fig.tight_layout()
