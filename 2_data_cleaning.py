import pandas as pd
from pathlib import Path

# Input and output folders
RAW_PATH = Path("data/raw")
CLEAN_PATH = Path("data/cleaned")

# Create cleaned folder if it does not exist
CLEAN_PATH.mkdir(parents=True, exist_ok=True)


# ------------------------------------
# FUNCTION FOR CLEANING DATA
# ------------------------------------

def clean_dataset(filename, date_column):

    print("\nCleaning:", filename)

    # Load dataset
    df = pd.read_csv(RAW_PATH / filename)

    # Original record count
    original_rows = len(df)

    # Remove duplicate records
    df = df.drop_duplicates().copy()

    # Convert date column
    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    # Remove records with invalid dates
    df = df.dropna(subset=[date_column]).copy()

    # Convert dates to ISO format
    df[date_column] = df[date_column].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Save cleaned dataset
    output_file = CLEAN_PATH / filename

    df.to_csv(output_file, index=False)

    print("Original Rows:", original_rows)

    print("Cleaned Rows:", len(df))

    print("Removed Rows:", original_rows - len(df))

    print("Saved:", output_file)

    return df


# ------------------------------------
# 1. DAILY ACTIVITY DATA
# ------------------------------------

activity = clean_dataset(
    "dailyActivity_merged.csv",
    "ActivityDate"
)

# Remove invalid negative values
activity = activity[
    (activity["TotalSteps"] >= 0) &
    (activity["Calories"] >= 0) &
    (activity["TotalDistance"] >= 0) &
    (activity["SedentaryMinutes"] >= 0)
].copy()

# Create new columns
activity["TotalActiveMinutes"] = (
    activity["VeryActiveMinutes"] +
    activity["FairlyActiveMinutes"] +
    activity["LightlyActiveMinutes"]
)

activity["ActivityDate"] = pd.to_datetime(
    activity["ActivityDate"]
)

activity["DayOfWeek"] = (
    activity["ActivityDate"].dt.day_name()
)

activity["Month"] = (
    activity["ActivityDate"].dt.month_name()
)

activity["ActivityLevel"] = pd.cut(
    activity["TotalSteps"],
    bins=[-1, 4999, 7499, 9999, float("inf")],
    labels=[
        "Low Active",
        "Light Active",
        "Moderately Active",
        "Highly Active"
    ]
)

activity["ActivityDate"] = (
    activity["ActivityDate"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
)

activity.to_csv(
    CLEAN_PATH / "dailyActivity_cleaned.csv",
    index=False
)


# ------------------------------------
# 2. SLEEP DATA
# ------------------------------------

sleep = clean_dataset(
    "sleepDay_merged.csv",
    "SleepDay"
)

sleep = sleep[
    (sleep["TotalMinutesAsleep"] >= 0) &
    (sleep["TotalTimeInBed"] >= 0)
].copy()

sleep["SleepHours"] = (
    sleep["TotalMinutesAsleep"] / 60
)

sleep.to_csv(
    CLEAN_PATH / "sleep_cleaned.csv",
    index=False
)


# ------------------------------------
# 3. HOURLY STEPS
# ------------------------------------

hourly_steps = clean_dataset(
    "hourlySteps_merged.csv",
    "ActivityHour"
)

hourly_steps = hourly_steps[
    hourly_steps["StepTotal"] >= 0
].copy()

hourly_steps.to_csv(
    CLEAN_PATH / "hourlySteps_cleaned.csv",
    index=False
)


# ------------------------------------
# 4. HOURLY CALORIES
# ------------------------------------

hourly_calories = clean_dataset(
    "hourlyCalories_merged.csv",
    "ActivityHour"
)

hourly_calories = hourly_calories[
    hourly_calories["Calories"] >= 0
].copy()

hourly_calories.to_csv(
    CLEAN_PATH / "hourlyCalories_cleaned.csv",
    index=False
)


# ------------------------------------
# 5. WEIGHT DATA
# ------------------------------------

weight = clean_dataset(
    "weightLogInfo_merged.csv",
    "Date"
)

weight = weight[
    (weight["WeightKg"] > 0) &
    (weight["BMI"] > 0)
].copy()

weight.to_csv(
    CLEAN_PATH / "weight_cleaned.csv",
    index=False
)


print("\n" + "=" * 60)

print("ALL DATASETS CLEANED SUCCESSFULLY")

print("=" * 60)