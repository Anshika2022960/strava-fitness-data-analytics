import sqlite3
import pandas as pd
from pathlib import Path

# Database folder
DB_PATH = Path("database")

DB_PATH.mkdir(
    parents=True,
    exist_ok=True
)

# Connect to SQLite database
conn = sqlite3.connect(
    DB_PATH / "fitness_analytics.db"
)

# Cleaned data folder
DATA_PATH = Path("data/cleaned")


# Dataset and table mapping
tables = {

    "daily_activity":
        "dailyActivity_cleaned.csv",

    "sleep_data":
        "sleep_cleaned.csv",

    "hourly_steps":
        "hourlySteps_cleaned.csv",

    "hourly_calories":
        "hourlyCalories_cleaned.csv",

    "weight_data":
        "weight_cleaned.csv"

}


# Create SQL tables
for table_name, filename in tables.items():

    df = pd.read_csv(
        DATA_PATH / filename
    )

    df.to_sql(
        table_name,
        conn,
        if_exists="replace",
        index=False
    )

    print(
        f"Table Created: {table_name}"
    )

    print(
        f"Total Records: {len(df)}"
    )


# Create useful indexes
conn.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_daily_activity_user_date
    ON daily_activity(Id, ActivityDate)
    """
)

conn.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_sleep_user_date
    ON sleep_data(Id, SleepDay)
    """
)

conn.commit()

# Display all database tables
query = """

SELECT name
FROM sqlite_master
WHERE type='table'

"""

tables_df = pd.read_sql_query(
    query,
    conn
)

print("\nDATABASE TABLES:")

print(tables_df)

conn.close()

print(
    "\nDATABASE CREATED SUCCESSFULLY"
)