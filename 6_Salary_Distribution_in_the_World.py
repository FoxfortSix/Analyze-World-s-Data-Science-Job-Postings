"""
This script analyzes and visualizes the salary distribution of different data job titles worldwide.
It loads a dataset of data jobs, cleans and processes the data, and then creates a boxplot to show
the salary ranges for the top 6 most common job titles.
"""

# Importing necessary libraries
import ast  # For safely evaluating string representations of Python objects
import pandas as pd  # For data manipulation and analysis
import seaborn as sns  # For data visualization
from datasets import load_dataset  # To load datasets from the Hugging Face Hub
import matplotlib.pyplot as plt  # For plotting graphs

# Load the data_jobs dataset from Hugging Face
dataset = load_dataset("lukebarousse/data_jobs")
# Convert the 'train' split of the dataset to a pandas DataFrame
df = dataset["train"].to_pandas()

# Convert the 'job_posted_date' column to datetime objects for easier handling
df["job_posted_date"] = pd.to_datetime(df["job_posted_date"])

# Convert the 'job_skills' column from string representation of lists to actual Python lists
df["job_skills"] = df["job_skills"].apply(
    lambda x: ast.literal_eval(x) if pd.notna(x) else x
)

# Remove rows where the average yearly salary is missing (NaN)
df = df.dropna(subset=["salary_year_avg"])

# Find the 6 most common job titles in the dataset
job_titles = df.job_title_short.value_counts().index[:6].tolist()

# Filter the DataFrame to only include rows with one of the top 6 job titles
top_6 = df[df.job_title_short.isin(job_titles)]

# Determine the order of job titles based on their median salary (highest to lowest)
job_order = (
    top_6.groupby("job_title_short")["salary_year_avg"]
    .median()
    .sort_values(ascending=False)
    .index
)

# Create a boxplot to show the salary distribution for each of the top 6 job titles
sns.boxplot(
    data=top_6, x=top_6.salary_year_avg, y=top_6.job_title_short, order=job_order
)

# Set the visual theme for the plot
sns.set_theme(style="ticks")

# Set the title and axis labels for the plot
plt.title("Salary Distribution in the World")
plt.xlabel("Yearly Salary ($USD)")
plt.ylabel("")

# Format the x-axis to show salaries in thousands (e.g., $100K)
ax = plt.gca()
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"${int(x/1000)}K"))

# Set the x-axis limits to show salaries from $0 to $600,000
plt.xlim(0, 600000)

# Display the plot
plt.show()
