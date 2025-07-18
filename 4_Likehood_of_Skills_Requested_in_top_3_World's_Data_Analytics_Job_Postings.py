"""
This script analyzes the most requested skills in the top 3 data analytics job titles
from a public dataset of data job postings. It calculates the percentage of job postings
that mention each skill for the top job titles and visualizes the results using bar plots.
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

# Expand the DataFrame so each skill in 'job_skills' gets its own row
df_skill = df.explode("job_skills").copy()

# Group by both skill and job title, then count how many times each combination appears
df_skill_group = df_skill.groupby(["job_skills", "job_title_short"]).size()

# Reset the index to turn the groupby result into a DataFrame and name the count column
df_skill_group = df_skill_group.reset_index(name="skill_count")

# Sort the DataFrame so the most common skill-job title combinations come first
df_skill_group = df_skill_group.sort_values(by="skill_count", ascending=False)

# Find the top 3 most common job titles
job_titles = df.job_title_short.value_counts().sort_values(ascending=False).head(3)
job_titles = job_titles.reset_index()
job_titles = job_titles["job_title_short"].to_list()

# Count the total number of postings for each job title
df_job_title_count = (
    df.job_title_short.value_counts()
    .reset_index(name="jobs_total")
    .sort_values(by="jobs_total", ascending=False)
)

# Merge skill counts with total job counts for each job title
df_skills_percent = pd.merge(
    df_skill_group, df_job_title_count, how="left", on="job_title_short"
)

# Calculate the percentage of postings for each job title that mention each skill
df_skills_percent["skill_percent"] = (
    100 * df_skills_percent.skill_count / df_skills_percent.jobs_total
)

# Create a subplot for each of the top 3 job titles
fig, ax = plt.subplots(len(job_titles), 1)

# Set the visual style for the plots
sns.set_theme(style="ticks")

# Loop through each top job title to create a bar plot of its top 5 skills
for i, job_title in enumerate(job_titles):
    # Select the top 5 skills for the current job title
    df_plot = df_skills_percent[df_skills_percent.job_title_short == job_title].head(5)
    # Create a horizontal bar plot showing the percentage of postings for each skill
    sns.barplot(
        data=df_plot,
        x="skill_percent",
        y="job_skills",
        ax=ax[i],
        hue="skill_count",  # Color bars by skill count
        palette="dark:b_r",
        legend=False,
    )
    ax[i].set_ylabel("")  # Remove y-axis label for clarity
    ax[i].set_xlabel("")  # Remove x-axis label for clarity
    ax[i].set_xlim(0, 78)  # Set x-axis limits for consistency
    if i != len(job_titles) - 1:
        ax[i].set_xticks([])  # Hide x-axis ticks except for the last plot

    # Add text labels showing the exact percentage next to each bar
    for j, v in enumerate(df_plot.skill_percent):
        ax[i].text(v + 1, j, f"%{v:.2f}", va="center")

# Add a main title to the figure
fig.suptitle(
    "Likehood of Skills Requested in top 3 world's Data Analytics Job Postings"
)
# Adjust layout to prevent overlap
fig.tight_layout()
