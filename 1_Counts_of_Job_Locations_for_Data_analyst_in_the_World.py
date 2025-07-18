"""
This script analyzes and visualizes the top 10 countries with the most Data Analyst job postings.
It loads a public dataset, filters for Data Analyst roles, counts job postings by country,
and displays the results in a bar chart.
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

# Filter the DataFrame to include only rows where the job title is 'Data Analyst'
df_DA = df[df["job_title_short"] == "Data Analyst"]

# Count the number of Data Analyst jobs in each country, get the top 10 countries
df_plot = df_DA["job_country"].value_counts().head(10).reset_index()
# The resulting DataFrame has columns: 'index' (country name) and 'job_country' (count)

# Set the visual style for the plot
sns.set_theme(style="ticks")

# Create a horizontal bar plot showing the number of jobs per country
sns.barplot(
    data=df_plot,
    x="count",  # Number of jobs (will be created by value_counts)
    y="job_country",  # Country name
    hue="count",  # Color bars by count (for visual effect)
    palette="dark:b_r",
    legend=False,  # Do not show the legend
)

# Remove the top and right spines from the plot for a cleaner look
sns.despine()

# Add a title and axis labels to the plot
plt.title("Counts of Job Locations for Data Analyst in the World")
plt.xlabel("Number of Jobs")
plt.ylabel("")  # No label for y-axis (country names are self-explanatory)

# Display the plot
plt.show()
