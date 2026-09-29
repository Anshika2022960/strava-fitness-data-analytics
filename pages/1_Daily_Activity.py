import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path




# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Daily Activity Analysis",
    page_icon="👟",
    layout="wide"
)



# ============================================================
# DATABASE PATH - CORRECT FOR STREAMLIT CLOUD
# ============================================================

# This file is inside the pages folder.
# parent.parent takes us back to the main project folder.
BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "fitness_analytics.db"


# Check database exists before connecting
if not DB_PATH.exists():

    st.error(
        """
        Database file was not found.

        Please make sure this file exists in your project:

        database/fitness_analytics.db
        """
    )

    st.stop()


# ============================================================
# LOAD ACTIVITY DATA
# ============================================================

@st.cache_data
def load_activity_data():

    conn = sqlite3.connect(
        str(DB_PATH)
    )

    activity = pd.read_sql_query(
        "SELECT * FROM daily_activity",
        conn
    )

    conn.close()

    activity["ActivityDate"] = pd.to_datetime(
        activity["ActivityDate"]
    )

    return activity


activity = load_activity_data()


# ============================================================
# PAGE TITLE
# ============================================================

st.title("👟 Daily Activity Analysis")

st.write(
    """
    This page analyzes users' daily steps, distance,
    active minutes and sedentary behaviour.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header(
    "🔎 Activity Filters"
)


# ------------------------------------------------------------
# USER FILTER
# ------------------------------------------------------------

users = sorted(
    activity["Id"]
    .astype(str)
    .unique()
)


selected_user = st.sidebar.selectbox(
    "Select User",
    ["All Users"] + users
)


# ------------------------------------------------------------
# DATE FILTER
# ------------------------------------------------------------

min_date = (
    activity["ActivityDate"]
    .min()
    .date()
)

max_date = (
    activity["ActivityDate"]
    .max()
    .date()
)


selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(
        min_date,
        max_date
    ),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered = activity.copy()


# User filter
if selected_user != "All Users":

    filtered = filtered[
        filtered["Id"]
        .astype(str)
        == selected_user
    ]


# Date filter
if (
    isinstance(
        selected_dates,
        (tuple, list)
    )
    and len(selected_dates) == 2
):

    start_date = pd.Timestamp(
        selected_dates[0]
    )

    end_date = pd.Timestamp(
        selected_dates[1]
    )

    filtered = filtered[
        (
            filtered["ActivityDate"]
            >= start_date
        )
        &
        (
            filtered["ActivityDate"]
            <= end_date
        )
    ]


# ============================================================
# EMPTY RESULT CHECK
# ============================================================

if filtered.empty:

    st.warning(
        """
        No activity records are available
        for the selected filters.
        """
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

avg_steps = (
    filtered["TotalSteps"]
    .mean()
)

avg_distance = (
    filtered["TotalDistance"]
    .mean()
)

avg_active = (
    filtered["TotalActiveMinutes"]
    .mean()
)

avg_sedentary = (
    filtered["SedentaryMinutes"]
    .mean()
)

max_steps = (
    filtered["TotalSteps"]
    .max()
)


# ============================================================
# KPI CARDS
# ============================================================

st.subheader(
    "📊 Activity Overview"
)


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "👟 Avg. Steps",
    f"{avg_steps:,.0f}"
)


col2.metric(
    "📍 Avg. Distance",
    f"{avg_distance:.2f}"
)


col3.metric(
    "🏃 Active Minutes",
    f"{avg_active:.1f}"
)


col4.metric(
    "🪑 Sedentary Minutes",
    f"{avg_sedentary:.1f}"
)


col5.metric(
    "🏆 Highest Steps",
    f"{max_steps:,.0f}"
)


st.divider()


# ============================================================
# WEEKDAY ORDER
# ============================================================

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


# ============================================================
# ROW 1
# ============================================================

left1, right1 = st.columns(2)


# ------------------------------------------------------------
# AVERAGE STEPS BY WEEKDAY
# ------------------------------------------------------------

with left1:

    st.subheader(
        "👟 Average Steps by Weekday"
    )

    weekday_steps = (
        filtered
        .groupby("DayOfWeek")[
            "TotalSteps"
        ]
        .mean()
        .reindex(
            weekday_order
        )
        .dropna()
    )

    st.bar_chart(
        weekday_steps
    )


# ------------------------------------------------------------
# DAILY STEP TREND
# ------------------------------------------------------------

with right1:

    st.subheader(
        "📈 Daily Step Trend"
    )

    daily_steps = (
        filtered
        .groupby("ActivityDate")[
            "TotalSteps"
        ]
        .mean()
        .sort_index()
    )

    st.line_chart(
        daily_steps
    )


st.divider()


# ============================================================
# ACTIVITY INTENSITY ANALYSIS
# ============================================================

st.subheader(
    "🏃 Activity Intensity Analysis"
)


intensity = pd.DataFrame(
    {

        "Activity": [
            "Very Active",
            "Fairly Active",
            "Lightly Active",
            "Sedentary"
        ],

        "Average Minutes": [

            filtered[
                "VeryActiveMinutes"
            ].mean(),

            filtered[
                "FairlyActiveMinutes"
            ].mean(),

            filtered[
                "LightlyActiveMinutes"
            ].mean(),

            filtered[
                "SedentaryMinutes"
            ].mean()
        ]
    }
)


st.bar_chart(
    intensity,
    x="Activity",
    y="Average Minutes"
)


st.caption(
    """
    Sedentary minutes are included for comparison.
    Sedentary time represents inactive time and is
    not an activity intensity level.
    """
)


st.divider()


# ============================================================
# ROW 2
# ============================================================

left2, right2 = st.columns(2)


# ------------------------------------------------------------
# STEPS VS DISTANCE
# ------------------------------------------------------------

with left2:

    st.subheader(
        "📍 Steps vs Distance"
    )

    fig, ax = plt.subplots()

    ax.scatter(
        filtered["TotalSteps"],
        filtered["TotalDistance"],
        alpha=0.6
    )

    ax.set_xlabel(
        "Total Steps"
    )

    ax.set_ylabel(
        "Total Distance"
    )

    ax.set_title(
        "Steps and Distance Relationship"
    )

    st.pyplot(
        fig
    )

    plt.close(
        fig
    )


# ------------------------------------------------------------
# ACTIVE VS SEDENTARY TIME
# ------------------------------------------------------------

with right2:

    st.subheader(
        "🪑 Active vs Sedentary Time"
    )

    comparison = pd.DataFrame(
        {

            "Category": [
                "Active Minutes",
                "Sedentary Minutes"
            ],

            "Average Minutes": [
                avg_active,
                avg_sedentary
            ]
        }
    )

    st.bar_chart(
        comparison,
        x="Category",
        y="Average Minutes"
    )


st.divider()


# ============================================================
# TOP USERS
# ============================================================

st.subheader(
    "🏆 Top 10 Users by Average Daily Steps"
)


top_users = (
    filtered
    .groupby("Id")[
        "TotalSteps"
    ]
    .mean()
    .sort_values(
        ascending=False
    )
    .head(10)
    .reset_index()
)


top_users.columns = [
    "User ID",
    "Average Steps"
]


top_users[
    "User ID"
] = (
    top_users[
        "User ID"
    ]
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
# ACTIVITY LEVEL DISTRIBUTION
# ============================================================

st.subheader(
    "📊 Activity Level Distribution"
)


activity_levels = (
    filtered[
        "ActivityLevel"
    ]
    .value_counts()
    .rename_axis(
        "Activity Level"
    )
    .reset_index(
        name="Records"
    )
)


st.bar_chart(
    activity_levels,
    x="Activity Level",
    y="Records"
)


st.caption(
    """
    These activity levels are analytical categories
    created from daily step counts during preprocessing.
    They are not clinical fitness classifications.
    """
)


st.divider()


# ============================================================
# WEEKDAY SUMMARY TABLE
# ============================================================

st.subheader(
    "📅 Weekday Activity Summary"
)


weekday_summary = (
    filtered
    .groupby("DayOfWeek")
    .agg(

        AverageSteps=(
            "TotalSteps",
            "mean"
        ),

        AverageDistance=(
            "TotalDistance",
            "mean"
        ),

        VeryActiveMinutes=(
            "VeryActiveMinutes",
            "mean"
        ),

        FairlyActiveMinutes=(
            "FairlyActiveMinutes",
            "mean"
        ),

        LightlyActiveMinutes=(
            "LightlyActiveMinutes",
            "mean"
        ),

        SedentaryMinutes=(
            "SedentaryMinutes",
            "mean"
        )
    )
    .reindex(
        weekday_order
    )
    .dropna()
    .round(2)
    .reset_index()
)


st.dataframe(
    weekday_summary,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# AUTOMATIC INSIGHTS
# ============================================================

st.divider()

st.subheader(
    "💡 Activity Insights"
)


weekday_average = (
    filtered
    .groupby("DayOfWeek")[
        "TotalSteps"
    ]
    .mean()
)


if not weekday_average.empty:

    highest_day = (
        weekday_average.idxmax()
    )

    highest_value = (
        weekday_average.max()
    )

    lowest_day = (
        weekday_average.idxmin()
    )

    lowest_value = (
        weekday_average.min()
    )


    insight1, insight2, insight3 = st.columns(3)


    insight1.success(
        f"""
        **🏆 Highest Average Activity**

        {highest_day}

        Average Steps:
        **{highest_value:,.0f}**
        """
    )


    insight2.info(
        f"""
        **📉 Lowest Average Activity**

        {lowest_day}

        Average Steps:
        **{lowest_value:,.0f}**
        """
    )


    insight3.info(
        f"""
        **🏃 Average Active Time**

        **{avg_active:.1f} minutes/day**
        """
    )


# ============================================================
# DETAILED DATA
# ============================================================

st.divider()


with st.expander(
    "📋 View Detailed Daily Activity Data"
):

    display_columns = [

        "Id",
        "ActivityDate",
        "TotalSteps",
        "TotalDistance",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes",
        "TotalActiveMinutes",
        "Calories",
        "ActivityLevel"

    ]


    display_data = (
        filtered[
            display_columns
        ]
        .copy()
    )


    display_data[
        "Id"
    ] = (
        display_data[
            "Id"
        ]
        .astype(str)
    )


    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Strava Fitness Data Analytics Case Study | "
    "Fitbit Smart Device Dataset | "
    "Python • SQL • Streamlit"
)