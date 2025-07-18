"""
This script analyzes a dataset of data job postings to find out which companies have posted the most Data Analyst jobs worldwide.
It loads the data, cleans it, filters for Data Analyst roles, counts the top companies, and visualizes the results in a bar chart.
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

# Filter the DataFrame to only include rows where the job title is 'Data Analyst'
df_DA = df[df["job_title_short"] == "Data Analyst"]

# Count the number of job postings for each company and select the top 10 companies
df_plot = df_DA["company_name"].value_counts().head(10).reset_index()

# Set the theme for the plot
sns.set_theme(style="ticks")

# Create a horizontal bar plot showing the number of Data Analyst jobs per company
sns.barplot(
    data=df_plot,
    x="count",  # Number of jobs
    y="company_name",  # Company names
    hue="count",  # Color bars by count (for visual effect)
    palette="dark:b_r",  # Color palette
    legend=False,  # Do not show legend
)

# Remove the top and right spines from the plot for a cleaner look
sns.despine()

# Add a title and axis labels to the plot
plt.title("Counts of Companies for Data Analyst in the World")
plt.xlabel("Number of Jobs")
plt.ylabel("")  # No label for y-axis (company names are self-explanatory)

# Display the plot
plt.show()
