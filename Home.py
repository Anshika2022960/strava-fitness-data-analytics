import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Strava Fitness Analytics",
    page_icon="🏃",
    layout="wide"
)


# ============================================================
# DATABASE PATH
# ============================================================

DB_PATH = Path("database/fitness_analytics.db")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    conn = sqlite3.connect(DB_PATH)

    activity = pd.read_sql_query(
        "SELECT * FROM daily_activity",
        conn
    )

    sleep = pd.read_sql_query(
        "SELECT * FROM sleep_data",
        conn
    )

    conn.close()

    # Convert date columns
    activity["ActivityDate"] = pd.to_datetime(
        activity["ActivityDate"]
    )

    sleep["SleepDay"] = pd.to_datetime(
        sleep["SleepDay"]
    )

    return activity, sleep


activity, sleep = load_data()


# ============================================================
# MAIN TITLE
# ============================================================

st.title("🏃 Strava Fitness Data Analytics")

st.markdown(
    """
    **Interactive Fitness Tracking Data Analysis Dashboard**

    This project analyzes Fitbit smart-device data to understand
    users' physical activity, sedentary behaviour, calorie
    expenditure, sleep patterns and overall fitness behaviour.
    """
)

st.divider()


# ============================================================
# ABOUT PROJECT
# ============================================================

with st.expander(
    "📌 About This Project",
    expanded=False
):

    st.write(
        """
        This project analyzes fitness-tracker data using
        **Python, SQL, SQLite and Streamlit**.

        The major stages of the project include:

        - Data collection from the Fitbit fitness dataset
        - Data exploration
        - Data cleaning and preprocessing
        - SQLite database creation
        - 25 SQL analytical queries
        - Daily activity analysis
        - Sleep analysis
        - Calories analysis
        - Hourly activity analysis
        - Interactive data visualization
        - Insights and recommendations
        """
    )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")


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

minimum_date = (
    activity["ActivityDate"]
    .min()
    .date()
)

maximum_date = (
    activity["ActivityDate"]
    .max()
    .date()
)


selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(
        minimum_date,
        maximum_date
    ),
    min_value=minimum_date,
    max_value=maximum_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_activity = activity.copy()


# ------------------------------------------------------------
# USER
# ------------------------------------------------------------

if selected_user != "All Users":

    filtered_activity = filtered_activity[
        filtered_activity["Id"]
        .astype(str)
        == selected_user
    ]


# ------------------------------------------------------------
# DATE RANGE
# ------------------------------------------------------------

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

    filtered_activity = filtered_activity[
        (
            filtered_activity[
                "ActivityDate"
            ] >= start_date
        )
        &
        (
            filtered_activity[
                "ActivityDate"
            ] <= end_date
        )
    ]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_activity.empty:

    st.warning(
        """
        No activity records are available for the
        selected user and date range.
        """
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_users = filtered_activity[
    "Id"
].nunique()


average_steps = filtered_activity[
    "TotalSteps"
].mean()


average_calories = filtered_activity[
    "Calories"
].mean()


average_active_minutes = filtered_activity[
    "TotalActiveMinutes"
].mean()


average_sedentary = filtered_activity[
    "SedentaryMinutes"
].mean()


# ============================================================
# FITNESS OVERVIEW
# ============================================================

st.subheader("📊 Fitness Overview")


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "👥 Users",
    f"{total_users:,}"
)


col2.metric(
    "👟 Avg. Steps",
    f"{average_steps:,.0f}"
)


col3.metric(
    "🔥 Avg. Calories",
    f"{average_calories:,.0f}"
)


col4.metric(
    "🏃 Active Minutes",
    f"{average_active_minutes:.1f}"
)


col5.metric(
    "🪑 Sedentary Minutes",
    f"{average_sedentary:.1f}"
)


st.divider()


# ============================================================
# DATASET INFORMATION
# ============================================================

st.subheader("📁 Dataset Information")


data1, data2, data3, data4 = st.columns(4)


data1.metric(
    "Activity Records",
    f"{len(activity):,}"
)


data2.metric(
    "Sleep Records",
    f"{len(sleep):,}"
)


data3.metric(
    "Unique Activity Users",
    f"{activity['Id'].nunique():,}"
)


analysis_days = (
    activity["ActivityDate"]
    .dt.date
    .nunique()
)


data4.metric(
    "Analysis Days",
    f"{analysis_days}"
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
        filtered_activity
        .groupby(
            "DayOfWeek"
        )["TotalSteps"]
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
# STEPS VS CALORIES
# ------------------------------------------------------------

with right1:

    st.subheader(
        "🔥 Steps vs Calories"
    )

    fig, ax = plt.subplots()

    ax.scatter(
        filtered_activity[
            "TotalSteps"
        ],
        filtered_activity[
            "Calories"
        ],
        alpha=0.6
    )

    ax.set_xlabel(
        "Total Steps"
    )

    ax.set_ylabel(
        "Calories"
    )

    ax.set_title(
        "Steps and Calorie Expenditure"
    )

    st.pyplot(fig)

    plt.close(fig)


st.divider()


# ============================================================
# ROW 2
# ============================================================

left2, right2 = st.columns(2)


# ------------------------------------------------------------
# ACTIVITY INTENSITY
# ------------------------------------------------------------

with left2:

    st.subheader(
        "🏃 Average Activity Intensity"
    )

    intensity_data = pd.DataFrame(
        {

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
        }
    )

    st.bar_chart(
        intensity_data,
        x="Activity Type",
        y="Average Minutes"
    )


# ------------------------------------------------------------
# SEDENTARY TIME
# ------------------------------------------------------------

with right2:

    st.subheader(
        "🪑 Sedentary Time by Weekday"
    )

    sedentary_weekday = (
        filtered_activity
        .groupby(
            "DayOfWeek"
        )["SedentaryMinutes"]
        .mean()
        .reindex(
            weekday_order
        )
        .dropna()
    )

    st.bar_chart(
        sedentary_weekday
    )


st.divider()


# ============================================================
# ROW 3 - DAILY TRENDS
# ============================================================

left3, right3 = st.columns(2)


# ------------------------------------------------------------
# DAILY STEP TREND
# ------------------------------------------------------------

with left3:

    st.subheader(
        "📈 Daily Step Trend"
    )

    daily_steps = (
        filtered_activity
        .groupby(
            "ActivityDate"
        )["TotalSteps"]
        .mean()
        .sort_index()
    )

    st.line_chart(
        daily_steps
    )


# ------------------------------------------------------------
# DAILY CALORIE TREND
# ------------------------------------------------------------

with right3:

    st.subheader(
        "🔥 Daily Calorie Trend"
    )

    daily_calories = (
        filtered_activity
        .groupby(
            "ActivityDate"
        )["Calories"]
        .mean()
        .sort_index()
    )

    st.line_chart(
        daily_calories
    )


st.divider()


# ============================================================
# ACTIVITY LEVEL DISTRIBUTION
# ============================================================

st.subheader(
    "📊 Activity Level Distribution"
)


activity_levels = (
    filtered_activity[
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
    Activity levels are analytical categories created
    from daily step counts during preprocessing.
    They are not clinical fitness classifications.
    """
)


st.divider()


# ============================================================
# QUICK DATA INSIGHTS
# ============================================================

st.subheader(
    "💡 Quick Data Insights"
)


weekday_analysis = (
    filtered_activity
    .groupby(
        "DayOfWeek"
    )["TotalSteps"]
    .mean()
)


if not weekday_analysis.empty:

    most_active_day = (
        weekday_analysis.idxmax()
    )

    most_active_steps = (
        weekday_analysis.max()
    )

    least_active_day = (
        weekday_analysis.idxmin()
    )

    least_active_steps = (
        weekday_analysis.min()
    )


    insight1, insight2, insight3 = st.columns(3)


    insight1.success(
        f"""
        **🏆 Most Active Day**

        {most_active_day}

        Average Steps:
        **{most_active_steps:,.0f}**
        """
    )


    insight2.info(
        f"""
        **📉 Least Active Day**

        {least_active_day}

        Average Steps:
        **{least_active_steps:,.0f}**
        """
    )


    insight3.info(
        f"""
        **🏃 Average Active Time**

        **{average_active_minutes:.1f} minutes/day**
        """
    )


# ============================================================
# CORRELATION SUMMARY
# ============================================================

st.divider()

st.subheader(
    "🔗 Activity Relationship"
)


steps_calorie_corr = (
    filtered_activity[
        [
            "TotalSteps",
            "Calories"
        ]
    ]
    .corr()
    .iloc[0, 1]
)


active_calorie_corr = (
    filtered_activity[
        [
            "TotalActiveMinutes",
            "Calories"
        ]
    ]
    .corr()
    .iloc[0, 1]
)


corr1, corr2 = st.columns(2)


corr1.metric(
    "Steps ↔ Calories",
    f"{steps_calorie_corr:.2f}"
)


corr2.metric(
    "Active Minutes ↔ Calories",
    f"{active_calorie_corr:.2f}"
)


st.caption(
    """
    Correlation shows the strength and direction of
    association between variables. It does not prove
    causation.
    """
)


# ============================================================
# EXPLORE ANALYSIS
# ============================================================

st.divider()

st.subheader(
    "🧭 Explore the Analysis"
)


nav1, nav2, nav3 = st.columns(3)


with nav1:

    st.info(
        """
        ### 👟 Daily Activity

        Explore daily steps, distance,
        active minutes and sedentary behaviour.
        """
    )


    st.info(
        """
        ### 😴 Sleep Analysis

        Analyze sleep duration,
        time in bed and sleep efficiency.
        """
    )


with nav2:

    st.info(
        """
        ### 🔥 Calories Analysis

        Analyze calorie expenditure
        in relation to physical activity.
        """
    )


    st.info(
        """
        ### ⏰ Hourly Activity

        Identify peak and low
        activity periods during the day.
        """
    )


with nav3:

    st.info(
        """
        ### 📊 SQL Analytics

        Explore all 25 SQL
        analytical queries and results.
        """
    )


    st.info(
        """
        ### 💡 Insights & Recommendations

        View the final findings,
        recommendations and conclusion.
        """
    )


# ============================================================
# FILTERED DATASET
# ============================================================

st.divider()


with st.expander(
    "📋 View Filtered Activity Dataset"
):

    display_data = (
        filtered_activity.copy()
    )

    display_data["Id"] = (
        display_data["Id"]
        .astype(str)
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# PROJECT TECHNOLOGIES
# ============================================================

st.divider()

st.subheader(
    "🛠 Technologies Used"
)


tech1, tech2, tech3, tech4 = st.columns(4)


tech1.info(
    """
    **Python**

    Data processing
    and analysis
    """
)


tech2.info(
    """
    **Pandas**

    Data cleaning
    and manipulation
    """
)


tech3.info(
    """
    **SQLite / SQL**

    Database storage
    and analytics
    """
)


tech4.info(
    """
    **Streamlit**

    Interactive
    dashboard
    """
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