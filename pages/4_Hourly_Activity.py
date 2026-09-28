import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Hourly Activity Analysis",
    page_icon="⏰",
    layout="wide"
)


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


@st.cache_data
def load_data():

    conn = sqlite3.connect(DB_PATH)

    steps = pd.read_sql_query(
        "SELECT * FROM hourly_steps",
        conn
    )

    calories = pd.read_sql_query(
        "SELECT * FROM hourly_calories",
        conn
    )

    conn.close()

    steps["ActivityHour"] = pd.to_datetime(
        steps["ActivityHour"]
    )

    calories["ActivityHour"] = pd.to_datetime(
        calories["ActivityHour"]
    )

    return steps, calories


hourly_steps, hourly_calories = load_data()


# ============================================================
# MERGE HOURLY DATA
# ============================================================

hourly = pd.merge(
    hourly_steps,
    hourly_calories,
    on=["Id", "ActivityHour"],
    how="inner"
)


# ============================================================
# CREATE ADDITIONAL COLUMNS
# ============================================================

hourly["Hour"] = hourly["ActivityHour"].dt.hour

hourly["Date"] = hourly["ActivityHour"].dt.date


def get_day_period(hour):

    if 5 <= hour < 12:
        return "Morning"

    elif 12 <= hour < 17:
        return "Afternoon"

    elif 17 <= hour < 21:
        return "Evening"

    else:
        return "Night"


hourly["DayPeriod"] = hourly["Hour"].apply(
    get_day_period
)


# ============================================================
# TITLE
# ============================================================

st.title("⏰ Hourly Activity Analysis")

st.write(
    """
    This page analyzes hourly step activity and calorie
    expenditure to identify peak and low-activity periods
    throughout the day.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Hourly Activity Filters")


users = sorted(
    hourly["Id"].astype(str).unique()
)

selected_user = st.sidebar.selectbox(
    "Select User",
    ["All Users"] + users
)


min_date = hourly["ActivityHour"].min().date()
max_date = hourly["ActivityHour"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = hourly.copy()


if selected_user != "All Users":

    filtered = filtered[
        filtered["Id"].astype(str)
        == selected_user
    ]


if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_date = selected_dates[0]
    end_date = selected_dates[1]

    filtered = filtered[
        (filtered["Date"] >= start_date)
        &
        (filtered["Date"] <= end_date)
    ]


if filtered.empty:

    st.warning(
        "No hourly records are available for the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

avg_hourly_steps = filtered[
    "StepTotal"
].mean()

avg_hourly_calories = filtered[
    "Calories"
].mean()


hour_step_summary = (
    filtered
    .groupby("Hour")["StepTotal"]
    .mean()
)


hour_calorie_summary = (
    filtered
    .groupby("Hour")["Calories"]
    .mean()
)


peak_step_hour = hour_step_summary.idxmax()
peak_step_value = hour_step_summary.max()

lowest_step_hour = hour_step_summary.idxmin()
lowest_step_value = hour_step_summary.min()

peak_calorie_hour = hour_calorie_summary.idxmax()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Hourly Overview")

col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "👟 Avg. Hourly Steps",
    f"{avg_hourly_steps:,.0f}"
)


col2.metric(
    "🔥 Avg. Hourly Calories",
    f"{avg_hourly_calories:.2f}"
)


col3.metric(
    "🏆 Peak Step Hour",
    f"{peak_step_hour}:00"
)


col4.metric(
    "⬇ Lowest Step Hour",
    f"{lowest_step_hour}:00"
)


col5.metric(
    "🔥 Peak Calorie Hour",
    f"{peak_calorie_hour}:00"
)


st.divider()


# ============================================================
# ROW 1 - HOURLY STEPS AND CALORIES
# ============================================================

left1, right1 = st.columns(2)


with left1:

    st.subheader(
        "Average Steps by Hour"
    )

    hourly_steps_summary = (
        filtered
        .groupby("Hour")["StepTotal"]
        .mean()
        .sort_index()
    )

    st.line_chart(
        hourly_steps_summary
    )


with right1:

    st.subheader(
        "Average Calories by Hour"
    )

    hourly_calorie_summary = (
        filtered
        .groupby("Hour")["Calories"]
        .mean()
        .sort_index()
    )

    st.line_chart(
        hourly_calorie_summary
    )


st.divider()


# ============================================================
# ROW 2 - BAR CHARTS
# ============================================================

left2, right2 = st.columns(2)


with left2:

    st.subheader(
        "Hourly Step Pattern"
    )

    st.bar_chart(
        hourly_steps_summary
    )


with right2:

    st.subheader(
        "Hourly Calorie Pattern"
    )

    st.bar_chart(
        hourly_calorie_summary
    )


st.divider()


# ============================================================
# DAY PERIOD ANALYSIS
# ============================================================

st.subheader(
    "Activity by Time of Day"
)


period_summary = (
    filtered
    .groupby("DayPeriod")
    .agg(

        AverageSteps=(
            "StepTotal",
            "mean"
        ),

        AverageCalories=(
            "Calories",
            "mean"
        ),

        Records=(
            "Id",
            "count"
        )
    )
    .round(2)
    .reset_index()
)


period_order = [
    "Morning",
    "Afternoon",
    "Evening",
    "Night"
]


period_summary["DayPeriod"] = pd.Categorical(
    period_summary["DayPeriod"],
    categories=period_order,
    ordered=True
)


period_summary = period_summary.sort_values(
    "DayPeriod"
)


col3, col4 = st.columns(2)


with col3:

    st.subheader(
        "Average Steps by Day Period"
    )

    st.bar_chart(
        period_summary.set_index(
            "DayPeriod"
        )["AverageSteps"]
    )


with col4:

    st.subheader(
        "Average Calories by Day Period"
    )

    st.bar_chart(
        period_summary.set_index(
            "DayPeriod"
        )["AverageCalories"]
    )


st.dataframe(
    period_summary,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# STEPS VS CALORIES
# ============================================================

st.subheader(
    "Hourly Steps vs Calories"
)


fig, ax = plt.subplots()

ax.scatter(
    filtered["StepTotal"],
    filtered["Calories"],
    alpha=0.5
)

ax.set_xlabel(
    "Hourly Steps"
)

ax.set_ylabel(
    "Hourly Calories"
)

ax.set_title(
    "Relationship Between Hourly Steps and Calories"
)

st.pyplot(fig)

plt.close(fig)


# ============================================================
# CORRELATION
# ============================================================

correlation = (
    filtered[
        ["StepTotal", "Calories"]
    ]
    .corr()
    .iloc[0, 1]
)


st.metric(
    "Steps ↔ Calories Correlation",
    f"{correlation:.2f}"
)


st.caption(
    """
    This correlation describes association only.
    It does not prove that one variable causes the other.
    """
)


st.divider()


# ============================================================
# MOST ACTIVE HOURS TABLE
# ============================================================

st.subheader(
    "Top 5 Most Active Hours"
)


top_hours = (
    filtered
    .groupby("Hour")
    .agg(

        AverageSteps=(
            "StepTotal",
            "mean"
        ),

        AverageCalories=(
            "Calories",
            "mean"
        )
    )
    .sort_values(
        "AverageSteps",
        ascending=False
    )
    .head(5)
    .round(2)
    .reset_index()
)


top_hours["Hour"] = (
    top_hours["Hour"]
    .astype(str)
    + ":00"
)


st.dataframe(
    top_hours,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# LEAST ACTIVE HOURS TABLE
# ============================================================

st.subheader(
    "Top 5 Least Active Hours"
)


low_hours = (
    filtered
    .groupby("Hour")
    .agg(

        AverageSteps=(
            "StepTotal",
            "mean"
        ),

        AverageCalories=(
            "Calories",
            "mean"
        )
    )
    .sort_values(
        "AverageSteps",
        ascending=True
    )
    .head(5)
    .round(2)
    .reset_index()
)


low_hours["Hour"] = (
    low_hours["Hour"]
    .astype(str)
    + ":00"
)


st.dataframe(
    low_hours,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# USER COMPARISON
# ============================================================

st.subheader(
    "Top 10 Users by Average Hourly Steps"
)


top_users = (
    filtered
    .groupby("Id")["StepTotal"]
    .mean()
    .sort_values(
        ascending=False
    )
    .head(10)
    .reset_index()
)


top_users.columns = [
    "User ID",
    "Average Hourly Steps"
]


top_users["User ID"] = (
    top_users["User ID"]
    .astype(str)
)


st.bar_chart(
    top_users.set_index(
        "User ID"
    )
)


st.dataframe(
    top_users,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# AUTOMATIC INSIGHTS
# ============================================================

st.subheader(
    "Hourly Activity Insights"
)


best_period_row = (
    period_summary
    .sort_values(
        "AverageSteps",
        ascending=False
    )
    .iloc[0]
)


best_period = best_period_row[
    "DayPeriod"
]

best_period_steps = best_period_row[
    "AverageSteps"
]


insight1, insight2, insight3 = st.columns(3)


insight1.success(
    f"""
    **Peak Activity Hour**

    {peak_step_hour}:00

    Average Steps:
    {peak_step_value:,.0f}
    """
)


insight2.info(
    f"""
    **Lowest Activity Hour**

    {lowest_step_hour}:00

    Average Steps:
    {lowest_step_value:,.0f}
    """
)


insight3.info(
    f"""
    **Most Active Day Period**

    {best_period}

    Avg Steps:
    {best_period_steps:,.0f}
    """
)


# ============================================================
# DETAILED DATA
# ============================================================

st.divider()


with st.expander(
    "View Detailed Hourly Data"
):

    display_columns = [

        "Id",
        "ActivityHour",
        "Hour",
        "DayPeriod",
        "StepTotal",
        "Calories"

    ]

    st.dataframe(
        filtered[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Strava Fitness Data Analytics | Hourly Activity Analysis"
)