import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SQL Analytics",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📊 SQL Fitness Analytics")

st.write(
    """
    Explore 25 SQL queries used to analyze user activity,
    sedentary behaviour, calories, sleep and hourly fitness
    patterns.
    """
)

st.divider()


# ============================================================
# DATABASE CONNECTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "fitness_analytics.db"


if not DB_PATH.exists():

    st.error(
        """
        Database file was not found.

        Please make sure this file exists:

        database/fitness_analytics.db
        """
    )

    st.stop()


def run_sql(query):

    conn = sqlite3.connect(DB_PATH)

    result = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return result


# ============================================================
# SQL QUERY DICTIONARY
# ============================================================

queries = {

    # --------------------------------------------------------
    # BASIC FITNESS OVERVIEW
    # --------------------------------------------------------

    "Q1 - Total Unique Users": {
        "question":
            "How many unique users are present in the activity dataset?",

        "query":
        """
SELECT
    COUNT(DISTINCT Id) AS TotalUsers
FROM daily_activity;
        """,

        "meaning":
            "Shows the number of unique fitness tracker users."
    },


    "Q2 - Total Activity Records": {
        "question":
            "How many daily activity records are available?",

        "query":
        """
SELECT
    COUNT(*) AS TotalActivityRecords
FROM daily_activity;
        """,

        "meaning":
            "Shows the total number of daily activity observations."
    },


    "Q3 - Average Daily Steps": {
        "question":
            "What is the average number of steps recorded per day?",

        "query":
        """
SELECT
    ROUND(AVG(TotalSteps), 2)
        AS AverageDailySteps
FROM daily_activity;
        """,

        "meaning":
            "Shows the overall average daily step count."
    },


    "Q4 - Average Daily Distance": {
        "question":
            "What is the average recorded distance travelled per day?",

        "query":
        """
SELECT
    ROUND(AVG(TotalDistance), 2)
        AS AverageDailyDistance
FROM daily_activity;
        """,

        "meaning":
            "Shows the average daily distance recorded by the tracker."
    },


    "Q5 - Average Daily Calories": {
        "question":
            "What is the average daily calorie expenditure?",

        "query":
        """
SELECT
    ROUND(AVG(Calories), 2)
        AS AverageDailyCalories
FROM daily_activity;
        """,

        "meaning":
            "Shows the average calories recorded per user-day."
    },


    # --------------------------------------------------------
    # ACTIVITY ANALYSIS
    # --------------------------------------------------------

    "Q6 - Top 10 Users by Steps": {
        "question":
            "Which users have the highest average daily step count?",

        "query":
        """
SELECT
    Id,
    ROUND(AVG(TotalSteps), 2)
        AS AverageSteps
FROM daily_activity
GROUP BY Id
ORDER BY AverageSteps DESC
LIMIT 10;
        """,

        "meaning":
            "Identifies users with the highest average recorded step counts."
    },


    "Q7 - Bottom 10 Users by Steps": {
        "question":
            "Which users have the lowest average daily step count?",

        "query":
        """
SELECT
    Id,
    ROUND(AVG(TotalSteps), 2)
        AS AverageSteps
FROM daily_activity
GROUP BY Id
ORDER BY AverageSteps ASC
LIMIT 10;
        """,

        "meaning":
            "Identifies users with the lowest average recorded step counts."
    },


    "Q8 - Steps by Weekday": {
        "question":
            "How does average step count vary across weekdays?",

        "query":
        """
SELECT
    DayOfWeek,
    ROUND(AVG(TotalSteps), 2)
        AS AverageSteps
FROM daily_activity
GROUP BY DayOfWeek
ORDER BY
    CASE DayOfWeek
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;
        """,

        "meaning":
            "Helps identify weekday patterns in physical activity."
    },


    "Q9 - Average Active Minutes": {
        "question":
            "How many active minutes are recorded on an average day?",

        "query":
        """
SELECT
    ROUND(AVG(TotalActiveMinutes), 2)
        AS AverageActiveMinutes
FROM daily_activity;
        """,

        "meaning":
            "Shows average daily active time across light, fair and very active minutes."
    },


    "Q10 - Activity Intensities": {
        "question":
            "How much time is spent at different activity intensities?",

        "query":
        """
SELECT
    ROUND(AVG(VeryActiveMinutes), 2)
        AS AvgVeryActiveMinutes,

    ROUND(AVG(FairlyActiveMinutes), 2)
        AS AvgFairlyActiveMinutes,

    ROUND(AVG(LightlyActiveMinutes), 2)
        AS AvgLightlyActiveMinutes

FROM daily_activity;
        """,

        "meaning":
            "Compares very active, fairly active and lightly active minutes."
    },


    # --------------------------------------------------------
    # SEDENTARY ANALYSIS
    # --------------------------------------------------------

    "Q11 - Average Sedentary Time": {
        "question":
            "What is the average daily sedentary time?",

        "query":
        """
SELECT
    ROUND(AVG(SedentaryMinutes), 2)
        AS AverageSedentaryMinutes,

    ROUND(AVG(SedentaryMinutes) / 60.0, 2)
        AS AverageSedentaryHours

FROM daily_activity;
        """,

        "meaning":
            "Shows the average amount of recorded sedentary time."
    },


    "Q12 - Highest Sedentary Users": {
        "question":
            "Which users have the highest average sedentary time?",

        "query":
        """
SELECT
    Id,

    ROUND(AVG(SedentaryMinutes), 2)
        AS AverageSedentaryMinutes,

    ROUND(AVG(SedentaryMinutes) / 60.0, 2)
        AS AverageSedentaryHours

FROM daily_activity

GROUP BY Id

ORDER BY AverageSedentaryMinutes DESC

LIMIT 10;
        """,

        "meaning":
            "Identifies users with the highest recorded sedentary time."
    },


    "Q13 - Sedentary Time by Weekday": {
        "question":
            "How does sedentary time vary across weekdays?",

        "query":
        """
SELECT
    DayOfWeek,

    ROUND(AVG(SedentaryMinutes), 2)
        AS AverageSedentaryMinutes

FROM daily_activity

GROUP BY DayOfWeek

ORDER BY
    CASE DayOfWeek
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;
        """,

        "meaning":
            "Shows whether sedentary behaviour changes during the week."
    },


    # --------------------------------------------------------
    # CALORIE ANALYSIS
    # --------------------------------------------------------

    "Q14 - Highest Calorie Users": {
        "question":
            "Which users have the highest average calorie expenditure?",

        "query":
        """
SELECT
    Id,
    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM daily_activity

GROUP BY Id

ORDER BY AverageCalories DESC

LIMIT 10;
        """,

        "meaning":
            "Identifies users with the highest average recorded calorie expenditure."
    },


    "Q15 - Calories by Weekday": {
        "question":
            "How does average calorie expenditure vary by weekday?",

        "query":
        """
SELECT
    DayOfWeek,

    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM daily_activity

GROUP BY DayOfWeek

ORDER BY
    CASE DayOfWeek
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;
        """,

        "meaning":
            "Shows weekday differences in average calorie expenditure."
    },


    "Q16 - Steps vs Calories": {
        "question":
            "How do average steps and calories compare for each user?",

        "query":
        """
SELECT
    Id,

    ROUND(AVG(TotalSteps), 2)
        AS AverageSteps,

    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM daily_activity

GROUP BY Id

ORDER BY AverageSteps DESC;
        """,

        "meaning":
            "Allows comparison of recorded movement and calorie expenditure."
    },


    # --------------------------------------------------------
    # SLEEP ANALYSIS
    # --------------------------------------------------------

    "Q17 - Average Sleep": {
        "question":
            "What is the overall average sleep duration?",

        "query":
        """
SELECT
    ROUND(AVG(SleepHours), 2)
        AS AverageSleepHours
FROM sleep_data;
        """,

        "meaning":
            "Shows the average recorded sleep duration."
    },


    "Q18 - Longest Sleep Users": {
        "question":
            "Which users sleep the longest on average?",

        "query":
        """
SELECT
    Id,

    ROUND(AVG(SleepHours), 2)
        AS AverageSleepHours

FROM sleep_data

GROUP BY Id

ORDER BY AverageSleepHours DESC

LIMIT 10;
        """,

        "meaning":
            "Identifies users with the longest average recorded sleep."
    },


    "Q19 - Shortest Sleep Users": {
        "question":
            "Which users sleep the least on average?",

        "query":
        """
SELECT
    Id,

    ROUND(AVG(SleepHours), 2)
        AS AverageSleepHours

FROM sleep_data

GROUP BY Id

ORDER BY AverageSleepHours ASC

LIMIT 10;
        """,

        "meaning":
            "Identifies users with the shortest average recorded sleep."
    },


    "Q20 - Sleep Efficiency": {
        "question":
            "What is the sleep efficiency of each user?",

        "query":
        """
SELECT
    Id,

    ROUND(
        AVG(TotalMinutesAsleep), 2
    ) AS AverageMinutesAsleep,

    ROUND(
        AVG(TotalTimeInBed), 2
    ) AS AverageTimeInBed,

    ROUND(
        100.0 * SUM(TotalMinutesAsleep)
        / NULLIF(SUM(TotalTimeInBed), 0),
        2
    ) AS SleepEfficiencyPercent

FROM sleep_data

GROUP BY Id

ORDER BY SleepEfficiencyPercent DESC;
        """,

        "meaning":
            "Sleep efficiency compares recorded sleeping time with total time spent in bed."
    },


    # --------------------------------------------------------
    # HOURLY ANALYSIS
    # --------------------------------------------------------

    "Q21 - Steps by Hour": {
        "question":
            "At what hours do users record the most steps?",

        "query":
        """
SELECT
    strftime('%H', ActivityHour)
        AS Hour,

    ROUND(AVG(StepTotal), 2)
        AS AverageSteps

FROM hourly_steps

GROUP BY Hour

ORDER BY AverageSteps DESC;
        """,

        "meaning":
            "Identifies the hours with the highest average step activity."
    },


    "Q22 - Calories by Hour": {
        "question":
            "At what hours is average calorie expenditure highest?",

        "query":
        """
SELECT
    strftime('%H', ActivityHour)
        AS Hour,

    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM hourly_calories

GROUP BY Hour

ORDER BY AverageCalories DESC;
        """,

        "meaning":
            "Shows the hours associated with higher average calorie expenditure."
    },


    # --------------------------------------------------------
    # CROSS DATASET ANALYSIS
    # --------------------------------------------------------

    "Q23 - Sleep vs Steps": {
        "question":
            "How do sleep duration and daily steps compare for users with matched activity and sleep dates?",

        "query":
        """
SELECT
    a.Id,

    ROUND(AVG(a.TotalSteps), 2)
        AS AverageSteps,

    ROUND(AVG(s.SleepHours), 2)
        AS AverageSleepHours

FROM daily_activity a

INNER JOIN sleep_data s

    ON a.Id = s.Id

    AND date(a.ActivityDate) =
        date(s.SleepDay)

GROUP BY a.Id

ORDER BY AverageSteps DESC;
        """,

        "meaning":
            "Compares average daily steps and sleep duration using matched user-date records."
    },


    "Q24 - Sleep vs Sedentary Time": {
        "question":
            "How do sleep duration and sedentary time compare?",

        "query":
        """
SELECT
    a.Id,

    ROUND(AVG(a.SedentaryMinutes), 2)
        AS AverageSedentaryMinutes,

    ROUND(AVG(s.SleepHours), 2)
        AS AverageSleepHours

FROM daily_activity a

INNER JOIN sleep_data s

    ON a.Id = s.Id

    AND date(a.ActivityDate) =
        date(s.SleepDay)

GROUP BY a.Id

ORDER BY AverageSedentaryMinutes DESC;
        """,

        "meaning":
            "Compares sedentary behaviour with sleep duration using matched dates."
    },


    "Q25 - Complete User Profile": {
        "question":
            "What is the overall activity profile of each user?",

        "query":
        """
SELECT
    Id,

    COUNT(*) AS RecordedDays,

    ROUND(AVG(TotalSteps), 2)
        AS AverageSteps,

    ROUND(AVG(TotalDistance), 2)
        AS AverageDistance,

    ROUND(AVG(TotalActiveMinutes), 2)
        AS AverageActiveMinutes,

    ROUND(AVG(SedentaryMinutes), 2)
        AS AverageSedentaryMinutes,

    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM daily_activity

GROUP BY Id

ORDER BY AverageSteps DESC;
        """,

        "meaning":
            "Provides a consolidated activity profile for each user."
    }
}


# ============================================================
# CATEGORY
# ============================================================

st.subheader("SQL Query Explorer")

selected_query = st.selectbox(
    "Select an analytical question:",
    list(queries.keys())
)


query_info = queries[selected_query]


# ============================================================
# DISPLAY BUSINESS QUESTION
# ============================================================

st.subheader("Business Question")

st.info(
    query_info["question"]
)


# ============================================================
# DISPLAY SQL
# ============================================================

with st.expander(
    "View SQL Query",
    expanded=False
):

    st.code(
        query_info["query"],
        language="sql"
    )


# ============================================================
# EXECUTE QUERY
# ============================================================

try:

    result = run_sql(
        query_info["query"]
    )

    st.subheader("Query Result")

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # RESULT INFORMATION
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Result Rows",
            len(result)
        )

    with col2:

        st.metric(
            "Result Columns",
            len(result.columns)
        )


    # ========================================================
    # EXPLANATION
    # ========================================================

    st.subheader("What Does This Query Tell Us?")

    st.success(
        query_info["meaning"]
    )


    # ========================================================
    # SIMPLE CHART
    # ========================================================

    numeric_columns = (
        result
        .select_dtypes(include="number")
        .columns
        .tolist()
    )

    if len(result) > 1 and len(numeric_columns) > 0:

        st.subheader("Result Visualization")

        chart_data = result.copy()

        # Remove Id because it is an identifier,
        # not a fitness measurement.
        chart_numeric_columns = [
            col for col in numeric_columns
            if col != "Id"
        ]

        if chart_numeric_columns:

            first_column = result.columns[0]

            try:

                chart_data = chart_data.set_index(
                    first_column
                )

                st.bar_chart(
                    chart_data[
                        chart_numeric_columns
                    ]
                )

            except Exception:

                st.write(
                    "Visualization is not available for this query."
                )


except Exception as error:

    st.error(
        f"Error executing SQL query: {error}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Strava Fitness Data Analytics | SQL Analytics"
)