import pandas as pd
from pathlib import Path

# Dataset location
DATA_PATH = Path("data/raw")

# List of datasets
files = [
    "dailyActivity_merged.csv",
    "sleepDay_merged.csv",
    "hourlySteps_merged.csv",
    "hourlyCalories_merged.csv",
    "weightLogInfo_merged.csv"
]

print("=" * 60)
print("STRAVA FITNESS DATA ANALYTICS")
print("PHASE 1: DATA EXPLORATION")
print("=" * 60)

for file in files:

    print("\n" + "=" * 60)
    print("DATASET:", file)
    print("=" * 60)

    # Load dataset
    df = pd.read_csv(DATA_PATH / file)

    # Display first five records
    print("\nFirst 5 Records:")
    print(df.head())

    # Dataset dimensions
    print("\nDataset Shape:")
    print(df.shape)

    # Column names
    print("\nColumn Names:")
    print(df.columns.tolist())

    # Dataset information
    print("\nDataset Information:")
    df.info()

    # Missing values
    print("\nMissing Values:")
    print(df.isnull().sum())

    # Duplicate records
    print("\nDuplicate Records:")
    print(df.duplicated().sum())

    # Number of unique users
    if "Id" in df.columns:

        print("\nTotal Unique Users:")
        print(df["Id"].nunique())

    # Statistical summary
    print("\nStatistical Summary:")
    print(df.describe(include="all"))

print("\nDATA EXPLORATION COMPLETED SUCCESSFULLY")