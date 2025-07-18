"""
This script analyzes trending top skills for Data Analysts worldwide using job posting data.
It loads a dataset, cleans and processes the data, calculates the percentage of job postings
requiring each skill per month, and visualizes the top 5 trending skills over the months of 2023.
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

# Filter the DataFrame to include only Data Analyst job postings
df_da = df[df.job_title_short == "Data Analyst"]

# Expand the 'job_skills' lists so each skill gets its own row
df_da_explode = df_da.explode("job_skills")

# Extract the month number from the job posting date
df_da_explode["job_posted_month_no"] = df_da_explode.job_posted_date.dt.month

# Create a pivot table: rows are months, columns are skills, values are counts of postings
df_da_pivot = df_da_explode.pivot_table(
    index="job_posted_month_no", columns="job_skills", aggfunc="size", fill_value=0
)

# Add a 'total' row to sum up the counts for each skill across all months
df_da_pivot.loc["total"] = df_da_pivot.sum()

# Sort the columns (skills) by their total count in descending order
df_da_pivot = df_da_pivot[df_da_pivot.loc["total"].sort_values(ascending=False).index]

# Remove the 'total' row as it's no longer needed
df_da_pivot = df_da_pivot.drop("total")

# Calculate the total number of Data Analyst job postings per month
df_da_total = df_da_explode.groupby("job_posted_month_no").size()

# Convert counts to percentages (likelihood) for each skill per month
df_da_pivot = df_da_pivot.div(df_da_total / 100, axis=0)

# Reset index to turn 'job_posted_month_no' into a column and make a copy
df_da_percent = df_da_pivot.reset_index().copy()

# Convert month number to month abbreviation (e.g., 1 -> Jan)
df_da_percent["job_posted_month"] = df_da_percent["job_posted_month_no"].apply(
    lambda x: pd.to_datetime(x, format="%m").strftime("%b")
)

# Set the month abbreviation as the index and drop the month number column
df_da_percent = df_da_percent.set_index("job_posted_month")
df_da_percent = df_da_percent.drop(columns="job_posted_month_no")

# Select only the top 5 skills (columns) for plotting
df_plot = df_da_percent.iloc[:, :5]

# Plot the trends of the top 5 skills over the months
sns.lineplot(data=df_plot, dashes=False, palette="tab10")
sns.set_theme(style="ticks")

plt.title("Trending Top Skills for Data Analysts in the World")  # Set plot title
plt.ylabel("Likehood in Job Postings")  # Set y-axis label
plt.xlabel("2023")  # Set x-axis label
plt.legend().remove()  # Remove the legend for a cleaner look

# Add skill names at the end of each line for clarity
for i in range(5):
    plt.text(11.2, df_plot.iloc[-1, i], df_plot.columns[i])

sns.despine()  # Remove the top and right spines from the plot

from matplotlib.ticker import PercentFormatter

# Format the y-axis to show percentages (no decimal places)
ax = plt.gca()
ax.yaxis.set_major_formatter(PercentFormatter(decimals=0))
