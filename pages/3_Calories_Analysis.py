import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Calories Analysis",
    page_icon="🔥",
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

    activity = pd.read_sql_query(
        "SELECT * FROM daily_activity",
        conn
    )

    hourly_calories = pd.read_sql_query(
        "SELECT * FROM hourly_calories",
        conn
    )

    conn.close()

    activity["ActivityDate"] = pd.to_datetime(
        activity["ActivityDate"]
    )

    hourly_calories["ActivityHour"] = pd.to_datetime(
        hourly_calories["ActivityHour"]
    )

    return activity, hourly_calories


activity, hourly_calories = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("🔥 Calories Analysis")

st.write(
    """
    This page analyzes daily and hourly calorie expenditure
    and examines its relationship with steps, active minutes
    and sedentary behaviour.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Calories Filters")


# ------------------------------------------------------------
# USER FILTER
# ------------------------------------------------------------

users = sorted(
    activity["Id"].astype(str).unique()
)

selected_user = st.sidebar.selectbox(
    "Select User",
    ["All Users"] + users
)


# ------------------------------------------------------------
# DATE FILTER
# ------------------------------------------------------------

min_date = activity["ActivityDate"].min().date()
max_date = activity["ActivityDate"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# APPLY FILTERS TO DAILY ACTIVITY
# ============================================================

filtered_activity = activity.copy()


if selected_user != "All Users":

    filtered_activity = filtered_activity[
        filtered_activity["Id"].astype(str)
        == selected_user
    ]


if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_activity = filtered_activity[
        (
            filtered_activity["ActivityDate"]
            >= start_date
        )
        &
        (
            filtered_activity["ActivityDate"]
            <= end_date
        )
    ]


# ============================================================
# APPLY FILTERS TO HOURLY CALORIES
# ============================================================

filtered_hourly = hourly_calories.copy()


if selected_user != "All Users":

    filtered_hourly = filtered_hourly[
        filtered_hourly["Id"].astype(str)
        == selected_user
    ]


if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_hourly = filtered_hourly[
        (
            filtered_hourly["ActivityHour"].dt.normalize()
            >= start_date
        )
        &
        (
            filtered_hourly["ActivityHour"].dt.normalize()
            <= end_date
        )
    ]


if filtered_activity.empty:

    st.warning(
        "No calorie records are available for the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

avg_calories = filtered_activity[
    "Calories"
].mean()

max_calories = filtered_activity[
    "Calories"
].max()

min_calories = filtered_activity[
    "Calories"
].min()

avg_steps = filtered_activity[
    "TotalSteps"
].mean()

avg_active_minutes = filtered_activity[
    "TotalActiveMinutes"
].mean()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Calories Overview")

col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "🔥 Avg. Calories",
    f"{avg_calories:,.0f}"
)


col2.metric(
    "⬆ Highest Calories",
    f"{max_calories:,.0f}"
)


col3.metric(
    "⬇ Lowest Calories",
    f"{min_calories:,.0f}"
)


col4.metric(
    "👟 Avg. Steps",
    f"{avg_steps:,.0f}"
)


col5.metric(
    "🏃 Active Minutes",
    f"{avg_active_minutes:.1f}"
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
# CHART ROW 1
# ============================================================

left1, right1 = st.columns(2)


# ------------------------------------------------------------
# CHART 1 - CALORIES BY WEEKDAY
# ------------------------------------------------------------

with left1:

    st.subheader(
        "Average Calories by Weekday"
    )

    weekday_calories = (
        filtered_activity
        .groupby("DayOfWeek")[
            "Calories"
        ]
        .mean()
        .reindex(weekday_order)
        .dropna()
    )

    st.bar_chart(
        weekday_calories
    )


# ------------------------------------------------------------
# CHART 2 - DAILY CALORIE TREND
# ------------------------------------------------------------

with right1:

    st.subheader(
        "Daily Calorie Trend"
    )

    daily_calories = (
        filtered_activity
        .groupby("ActivityDate")[
            "Calories"
        ]
        .mean()
        .sort_index()
    )

    st.line_chart(
        daily_calories
    )


st.divider()


# ============================================================
# CHART ROW 2
# ============================================================

left2, right2 = st.columns(2)


# ------------------------------------------------------------
# CHART 3 - STEPS VS CALORIES
# ------------------------------------------------------------

with left2:

    st.subheader(
        "Steps vs Calories"
    )

    fig, ax = plt.subplots()

    ax.scatter(
        filtered_activity["TotalSteps"],
        filtered_activity["Calories"],
        alpha=0.6
    )

    ax.set_xlabel(
        "Total Steps"
    )

    ax.set_ylabel(
        "Calories"
    )

    ax.set_title(
        "Relationship Between Steps and Calories"
    )

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# CHART 4 - ACTIVE MINUTES VS CALORIES
# ------------------------------------------------------------

with right2:

    st.subheader(
        "Active Minutes vs Calories"
    )

    fig, ax = plt.subplots()

    ax.scatter(
        filtered_activity[
            "TotalActiveMinutes"
        ],
        filtered_activity[
            "Calories"
        ],
        alpha=0.6
    )

    ax.set_xlabel(
        "Total Active Minutes"
    )

    ax.set_ylabel(
        "Calories"
    )

    ax.set_title(
        "Active Minutes and Calories"
    )

    st.pyplot(fig)

    plt.close(fig)


st.divider()


# ============================================================
# CHART ROW 3
# ============================================================

left3, right3 = st.columns(2)


# ------------------------------------------------------------
# CHART 5 - SEDENTARY MINUTES VS CALORIES
# ------------------------------------------------------------

with left3:

    st.subheader(
        "Sedentary Minutes vs Calories"
    )

    fig, ax = plt.subplots()

    ax.scatter(
        filtered_activity[
            "SedentaryMinutes"
        ],
        filtered_activity[
            "Calories"
        ],
        alpha=0.6
    )

    ax.set_xlabel(
        "Sedentary Minutes"
    )

    ax.set_ylabel(
        "Calories"
    )

    ax.set_title(
        "Sedentary Time and Calories"
    )

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# CHART 6 - ACTIVITY INTENSITY VS CALORIES
# ------------------------------------------------------------

with right3:

    st.subheader(
        "Activity Intensity Summary"
    )

    intensity_summary = pd.DataFrame({

        "Activity Type": [
            "Very Active",
            "Fairly Active",
            "Lightly Active"
        ],

        "Average Minutes": [
            filtered_activity[
                "VeryActiveMinutes"
            ].mean(),

            filtered_activity[
                "FairlyActiveMinutes"
            ].mean(),

            filtered_activity[
                "LightlyActiveMinutes"
            ].mean()
        ]
    })

    st.bar_chart(
        intensity_summary,
        x="Activity Type",
        y="Average Minutes"
    )


st.divider()


# ============================================================
# HOURLY CALORIE ANALYSIS
# ============================================================

st.subheader(
    "Hourly Calorie Pattern"
)


if not filtered_hourly.empty:

    filtered_hourly["Hour"] = (
        filtered_hourly[
            "ActivityHour"
        ].dt.hour
    )


    hourly_summary = (
        filtered_hourly
        .groupby("Hour")[
            "Calories"
        ]
        .mean()
        .sort_index()
    )


    st.line_chart(
        hourly_summary
    )


    peak_hour = hourly_summary.idxmax()
    peak_hour_value = hourly_summary.max()


    st.info(
        f"""
        Highest average hourly calorie expenditure is
        recorded around hour **{peak_hour}:00**
        with an average of **{peak_hour_value:.2f} calories**.
        """
    )


else:

    st.info(
        "No hourly calorie data are available for the selected filters."
    )


st.divider()


# ============================================================
# TOP USERS BY CALORIES
# ============================================================

st.subheader(
    "Top 10 Users by Average Calories"
)


top_calorie_users = (
    filtered_activity
    .groupby("Id")["Calories"]
    .mean()
    .sort_values(
        ascending=False
    )
    .head(10)
    .reset_index()
)


top_calorie_users.columns = [
    "User ID",
    "Average Calories"
]


top_calorie_users[
    "User ID"
] = top_calorie_users[
    "User ID"
].astype(str)


st.bar_chart(
    top_calorie_users.set_index(
        "User ID"
    )
)


st.dataframe(
    top_calorie_users,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# WEEKDAY CALORIE SUMMARY TABLE
# ============================================================

st.subheader(
    "Weekday Calorie Summary"
)


weekday_summary = (
    filtered_activity
    .groupby("DayOfWeek")
    .agg(

        AverageCalories=(
            "Calories",
            "mean"
        ),

        AverageSteps=(
            "TotalSteps",
            "mean"
        ),

        AverageActiveMinutes=(
            "TotalActiveMinutes",
            "mean"
        ),

        AverageSedentaryMinutes=(
            "SedentaryMinutes",
            "mean"
        )
    )
    .reindex(weekday_order)
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
    "Calories Insights"
)


weekday_calorie_avg = (
    filtered_activity
    .groupby("DayOfWeek")[
        "Calories"
    ]
    .mean()
)


if not weekday_calorie_avg.empty:

    highest_day = (
        weekday_calorie_avg.idxmax()
    )

    highest_value = (
        weekday_calorie_avg.max()
    )

    lowest_day = (
        weekday_calorie_avg.idxmin()
    )

    lowest_value = (
        weekday_calorie_avg.min()
    )


    insight1, insight2, insight3 = st.columns(3)


    insight1.success(
        f"""
        **Highest Average Calories**

        {highest_day}

        {highest_value:,.0f}
        """
    )


    insight2.info(
        f"""
        **Lowest Average Calories**

        {lowest_day}

        {lowest_value:,.0f}
        """
    )


    insight3.info(
        f"""
        **Average Daily Calories**

        {avg_calories:,.0f}
        """
    )


# ============================================================
# CORRELATION INFORMATION
# ============================================================

st.divider()

st.subheader(
    "Relationship Summary"
)


steps_corr = filtered_activity[
    ["TotalSteps", "Calories"]
].corr().iloc[0, 1]


active_corr = filtered_activity[
    ["TotalActiveMinutes", "Calories"]
].corr().iloc[0, 1]


sedentary_corr = filtered_activity[
    ["SedentaryMinutes", "Calories"]
].corr().iloc[0, 1]


corr1, corr2, corr3 = st.columns(3)


corr1.metric(
    "Steps ↔ Calories",
    f"{steps_corr:.2f}"
)


corr2.metric(
    "Active Minutes ↔ Calories",
    f"{active_corr:.2f}"
)


corr3.metric(
    "Sedentary ↔ Calories",
    f"{sedentary_corr:.2f}"
)


st.caption(
    """
    Correlation describes the strength and direction of
    association between two variables. It does not prove
    that one variable causes the other.
    """
)


# ============================================================
# DETAILED DATA
# ============================================================

st.divider()


with st.expander(
    "View Detailed Calorie Data"
):

    display_columns = [

        "Id",
        "ActivityDate",
        "DayOfWeek",
        "TotalSteps",
        "TotalActiveMinutes",
        "SedentaryMinutes",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "Calories"

    ]


    st.dataframe(
        filtered_activity[
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
    "Strava Fitness Data Analytics | Calories Analysis"
)