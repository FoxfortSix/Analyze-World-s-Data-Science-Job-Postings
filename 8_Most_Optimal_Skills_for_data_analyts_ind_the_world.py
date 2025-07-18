"""
This script analyzes data analyst job postings from a dataset.
It finds the most in-demand skills for data analysts worldwide,
shows how common each skill is, and compares their median salaries.
The results are visualized in a scatter plot, with skills grouped by technology.
"""

# Importing necessary libraries
import ast  # For safely evaluating string representations of Python objects
import pandas as pd  # For data manipulation and analysis
import seaborn as sns  # For data visualization
from datasets import load_dataset  # For loading datasets from the Hugging Face Hub
import matplotlib.pyplot as plt  # For plotting graphs
from adjustText import adjust_text  # To prevent text overlap in plots

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

# Filter for Data Analyst jobs only
df_da = df[(df.job_title_short == "Data Analyst")].copy()
# Remove rows without salary information
df_da = df_da.dropna(subset=["salary_year_avg"])
# Expand job_skills so each skill gets its own row
df_da_explode = df_da.explode("job_skills")

# Group by skill and calculate how many jobs mention each skill and their median salary
df_da_group = (
    df_da_explode.groupby("job_skills")["salary_year_avg"]
    .agg(["count", "median"])
    .sort_values(by="count", ascending=False)
)
# Rename columns for clarity
df_da_group = df_da_group.rename(
    columns={"count": "skill_count", "median": "median_salary"}
)

# Total number of Data Analyst jobs
da_job_count = len(df_da)

# Calculate what percent of jobs mention each skill
df_da_group["skill_percent"] = df_da_group.skill_count / da_job_count * 100

# Set a minimum percent threshold for high-demand skills
skill_limit = 5

# Keep only skills that appear in more than skill_limit percent of jobs
df_da_high_demand_skill = df_da_group[df_da_group.skill_percent > skill_limit]

# Prepare technology-skill mapping
df_technology = df["job_type_skills"].copy()
df_technology = df_technology.drop_duplicates()  # Remove duplicate rows
df_technology = df_technology.dropna()  # Remove missing values

# Combine all technology-skill dictionaries into one
technology_dict = {}
for row in df_technology:
    row_dict = ast.literal_eval(row)  # Convert string to dictionary
    for key, value in row_dict.items():
        if key in technology_dict:
            technology_dict[key] += value  # Add skills to existing list
        else:
            technology_dict[key] = value  # Create new entry

# Remove duplicate skills for each technology
for key, value in technology_dict.items():
    technology_dict[key] = list(set(value))

# Convert technology-skill dictionary to DataFrame
df_technology = pd.DataFrame(
    list(technology_dict.items()), columns=["technology", "skills"]
)
df_technology = df_technology.explode("skills")  # One row per skill

# Merge skill stats with technology info
df_DA_skills_tech = df_da_group.merge(
    df_technology, left_on="job_skills", right_on="skills"
)

# Keep only high-demand skills in the merged DataFrame
df_DA_skills_tech_high_demand = df_DA_skills_tech[
    df_DA_skills_tech["skill_percent"] > skill_limit
]

# Remove duplicate skills (if a skill is linked to multiple technologies)
df_DA_skills_tech_high_demand_unique = df_DA_skills_tech_high_demand.drop_duplicates(
    subset="skills"
)

# Create scatter plot: skill percent vs. median salary, colored by technology
sns.scatterplot(
    data=df_DA_skills_tech_high_demand_unique,
    x="skill_percent",
    y="median_salary",
    hue="technology",
)

sns.despine()  # Remove top/right plot borders
sns.set_theme(style="ticks")  # Set plot style

# Prepare skill labels for each point
texts = []
for idx, row in df_DA_skills_tech_high_demand_unique.iterrows():
    texts.append(plt.text(row["skill_percent"], row["median_salary"], row["skills"]))

# Adjust text labels to avoid overlap
adjust_text(texts, arrowprops=dict(arrowstyle="->", color="gray"))

# Set axis labels, plot title, and legend
plt.xlabel("Percent of Data Analyst Jobs")
plt.ylabel("Median Yearly Salary")
plt.title("Most Optimal Skills for Data Analysts in the World")
plt.legend(title="Technology")

from matplotlib.ticker import PercentFormatter

# Format y-axis as $K and x-axis as percent
ax = plt.gca()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, pos: f"${int(y/1000)}K"))
ax.xaxis.set_major_formatter(PercentFormatter(decimals=0))

# Adjust layout and show the plot
plt.tight_layout()
plt.show()
