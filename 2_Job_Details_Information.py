"""
This script loads a dataset of data job postings from Hugging Face,
filters for Data Analyst jobs, and visualizes the distribution of
three job features (work from home, degree requirement, health insurance)
using pie charts.
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

# Dictionary mapping column names to more readable chart titles
dict_column = {
    "job_work_from_home": "Work from Home Offered",
    "job_no_degree_mention": "Degree Requirement",
    "job_health_insurance": "Health Insurance Offered",
}

# Create a figure with 1 row and 3 columns for the pie charts
fig, ax = plt.subplots(1, 3, figsize=(11, 3.5))

# Loop through each column and its title to create a pie chart
for i, (column, title) in enumerate(dict_column.items()):
    # Count the number of True/False values in the column and plot as a pie chart
    ax[i].pie(
        df_DA[column].value_counts(),
        labels=["False", "True"],  # Labels for the pie slices
        autopct="%1.1f%%",  # Show percentages on the chart
        startangle=90,  # Start the pie chart at 90 degrees
    )
    ax[i].set_title(title)  # Set the title for each pie chart

# Display the pie charts
plt.show()
