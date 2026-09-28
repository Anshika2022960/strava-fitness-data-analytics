import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sleep Analysis",
    page_icon="😴",
    layout="wide"
)


# ============================================================
# DATABASE
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

    sleep = pd.read_sql_query(
        "SELECT * FROM sleep_data",
        conn
    )

    activity = pd.read_sql_query(
        "SELECT * FROM daily_activity",
        conn
    )

    conn.close()

    sleep["SleepDay"] = pd.to_datetime(
        sleep["SleepDay"]
    )

    activity["ActivityDate"] = pd.to_datetime(
        activity["ActivityDate"]
    )

    return sleep, activity


sleep, activity = load_data()


# ============================================================
# CREATE ADDITIONAL SLEEP VARIABLES
# ============================================================

sleep["SleepHours"] = (
    sleep["TotalMinutesAsleep"] / 60
)

sleep["TimeInBedHours"] = (
    sleep["TotalTimeInBed"] / 60
)

sleep["SleepEfficiency"] = (
    sleep["TotalMinutesAsleep"]
    /
    sleep["TotalTimeInBed"]
    * 100
)

sleep["DayOfWeek"] = (
    sleep["SleepDay"].dt.day_name()
)


# ============================================================
# TITLE
# ============================================================

st.title("😴 Sleep Analysis")

st.write(
    """
    This page analyzes users' sleep duration, time in bed,
    sleep efficiency and the relationship between sleep and
    physical activity.
    """
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Sleep Filters")


# ------------------------------------------------------------
# USER FILTER
# ------------------------------------------------------------

sleep_users = sorted(
    sleep["Id"].astype(str).unique()
)

selected_user = st.sidebar.selectbox(
    "Select User",
    ["All Users"] + sleep_users
)


# ------------------------------------------------------------
# DATE FILTER
# ------------------------------------------------------------

minimum_date = sleep[
    "SleepDay"
].min().date()

maximum_date = sleep[
    "SleepDay"
].max().date()


selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_sleep = sleep.copy()


if selected_user != "All Users":

    filtered_sleep = filtered_sleep[
        filtered_sleep["Id"].astype(str)
        == selected_user
    ]


if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_date = pd.Timestamp(
        selected_dates[0]
    )

    end_date = pd.Timestamp(
        selected_dates[1]
    )

    filtered_sleep = filtered_sleep[
        (
            filtered_sleep["SleepDay"]
            >= start_date
        )
        &
        (
            filtered_sleep["SleepDay"]
            <= end_date
        )
    ]


if filtered_sleep.empty:

    st.warning(
        "No sleep records are available for the selected filters."
    )

    st.stop()


# ============================================================
# KPI CALCULATIONS
# ============================================================

avg_sleep = filtered_sleep[
    "SleepHours"
].mean()

avg_bed = filtered_sleep[
    "TimeInBedHours"
].mean()

avg_efficiency = filtered_sleep[
    "SleepEfficiency"
].mean()

avg_awake_in_bed = (
    filtered_sleep[
        "TotalTimeInBed"
    ].mean()
    -
    filtered_sleep[
        "TotalMinutesAsleep"
    ].mean()
)

total_sleep_users = filtered_sleep[
    "Id"
].nunique()


# ============================================================
# KPI CARDS
# ============================================================

st.subheader("Sleep Overview")

col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "😴 Avg. Sleep",
    f"{avg_sleep:.2f} hrs"
)


col2.metric(
    "🛏️ Avg. Time in Bed",
    f"{avg_bed:.2f} hrs"
)


col3.metric(
    "💤 Sleep Efficiency",
    f"{avg_efficiency:.1f}%"
)


col4.metric(
    "⏱️ Avg. Awake in Bed",
    f"{avg_awake_in_bed:.0f} min"
)


col5.metric(
    "👥 Sleep Users",
    f"{total_sleep_users}"
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

chart1, chart2 = st.columns(2)


# ------------------------------------------------------------
# CHART 1 - SLEEP BY WEEKDAY
# ------------------------------------------------------------

with chart1:

    st.subheader(
        "Average Sleep by Weekday"
    )

    weekday_sleep = (
        filtered_sleep
        .groupby("DayOfWeek")[
            "SleepHours"
        ]
        .mean()
        .reindex(weekday_order)
        .dropna()
    )

    st.bar_chart(
        weekday_sleep
    )


# ------------------------------------------------------------
# CHART 2 - SLEEP TREND
# ------------------------------------------------------------

with chart2:

    st.subheader(
        "Daily Sleep Trend"
    )

    sleep_trend = (
        filtered_sleep
        .groupby("SleepDay")[
            "SleepHours"
        ]
        .mean()
        .sort_index()
    )

    st.line_chart(
        sleep_trend
    )


st.divider()


# ============================================================
# ROW 2
# ============================================================

chart3, chart4 = st.columns(2)


# ------------------------------------------------------------
# CHART 3 - SLEEP DISTRIBUTION
# ------------------------------------------------------------

with chart3:

    st.subheader(
        "Sleep Duration Distribution"
    )

    fig, ax = plt.subplots()

    ax.hist(
        filtered_sleep["SleepHours"],
        bins=15,
        edgecolor="black"
    )

    ax.set_xlabel(
        "Sleep Duration (Hours)"
    )

    ax.set_ylabel(
        "Number of Records"
    )

    ax.set_title(
        "Distribution of Sleep Duration"
    )

    st.pyplot(fig)

    plt.close(fig)


# ------------------------------------------------------------
# CHART 4 - SLEEP VS TIME IN BED
# ------------------------------------------------------------

with chart4:

    st.subheader(
        "Sleep vs Time in Bed"
    )

    fig, ax = plt.subplots()

    ax.scatter(
        filtered_sleep["TimeInBedHours"],
        filtered_sleep["SleepHours"],
        alpha=0.6
    )

    ax.set_xlabel(
        "Time in Bed (Hours)"
    )

    ax.set_ylabel(
        "Sleep Duration (Hours)"
    )

    ax.set_title(
        "Sleep Duration vs Time in Bed"
    )

    st.pyplot(fig)

    plt.close(fig)


st.divider()


# ============================================================
# USER-WISE SLEEP ANALYSIS
# ============================================================

st.subheader(
    "Top 10 Users by Average Sleep Duration"
)


user_sleep = (
    filtered_sleep
    .groupby("Id")["SleepHours"]
    .mean()
    .sort_values(
        ascending=False
    )
    .head(10)
    .reset_index()
)


user_sleep.columns = [
    "User ID",
    "Average Sleep Hours"
]


user_sleep["User ID"] = (
    user_sleep["User ID"]
    .astype(str)
)


st.bar_chart(
    user_sleep.set_index(
        "User ID"
    )
)


st.dataframe(
    user_sleep,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# SLEEP EFFICIENCY ANALYSIS
# ============================================================

st.subheader(
    "Sleep Efficiency by User"
)


efficiency_by_user = (
    filtered_sleep
    .groupby("Id")
    .agg(
        TotalSleepMinutes=(
            "TotalMinutesAsleep",
            "sum"
        ),

        TotalBedMinutes=(
            "TotalTimeInBed",
            "sum"
        )
    )
    .reset_index()
)


efficiency_by_user[
    "Sleep Efficiency (%)"
] = (

    efficiency_by_user[
        "TotalSleepMinutes"
    ]

    /

    efficiency_by_user[
        "TotalBedMinutes"
    ]

    * 100
)


efficiency_by_user[
    "Sleep Efficiency (%)"
] = (

    efficiency_by_user[
        "Sleep Efficiency (%)"
    ].round(2)
)


efficiency_by_user["Id"] = (
    efficiency_by_user["Id"]
    .astype(str)
)


efficiency_display = (
    efficiency_by_user[
        [
            "Id",
            "Sleep Efficiency (%)"
        ]
    ]
    .rename(
        columns={
            "Id": "User ID"
        }
    )
    .sort_values(
        "Sleep Efficiency (%)",
        ascending=False
    )
)


st.bar_chart(
    efficiency_display
    .set_index("User ID")
)


st.dataframe(
    efficiency_display,
    use_container_width=True,
    hide_index=True
)


st.caption(
    """
    Sleep efficiency here is calculated as recorded minutes
    asleep divided by recorded time in bed × 100.
    """
)


st.divider()


# ============================================================
# MATCH SLEEP WITH DAILY ACTIVITY
# ============================================================

sleep_for_merge = filtered_sleep.copy()

activity_for_merge = activity.copy()


# Create date-only fields
sleep_for_merge["Date"] = (
    sleep_for_merge[
        "SleepDay"
    ].dt.date
)

activity_for_merge["Date"] = (
    activity_for_merge[
        "ActivityDate"
    ].dt.date
)


# Apply selected user to activity data
if selected_user != "All Users":

    activity_for_merge = (
        activity_for_merge[
            activity_for_merge[
                "Id"
            ].astype(str)
            == selected_user
        ]
    )


# Apply selected date range to activity
if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:

    start_day = selected_dates[0]
    end_day = selected_dates[1]

    activity_for_merge = (
        activity_for_merge[
            (
                activity_for_merge["Date"]
                >= start_day
            )
            &
            (
                activity_for_merge["Date"]
                <= end_day
            )
        ]
    )


# Merge on both User ID and Date
merged = pd.merge(
    sleep_for_merge,
    activity_for_merge,
    on=[
        "Id",
        "Date"
    ],
    how="inner"
)


# ============================================================
# SLEEP VS ACTIVITY
# ============================================================

if not merged.empty:

    st.subheader(
        "Sleep and Physical Activity"
    )


    sleep_activity1, sleep_activity2 = (
        st.columns(2)
    )


    # --------------------------------------------------------
    # SLEEP VS STEPS
    # --------------------------------------------------------

    with sleep_activity1:

        st.markdown(
            "**Sleep Duration vs Daily Steps**"
        )

        fig, ax = plt.subplots()

        ax.scatter(
            merged["SleepHours"],
            merged["TotalSteps"],
            alpha=0.6
        )

        ax.set_xlabel(
            "Sleep Duration (Hours)"
        )

        ax.set_ylabel(
            "Daily Steps"
        )

        st.pyplot(fig)

        plt.close(fig)


    # --------------------------------------------------------
    # SLEEP VS SEDENTARY
    # --------------------------------------------------------

    with sleep_activity2:

        st.markdown(
            "**Sleep Duration vs Sedentary Minutes**"
        )

        fig, ax = plt.subplots()

        ax.scatter(
            merged["SleepHours"],
            merged["SedentaryMinutes"],
            alpha=0.6
        )

        ax.set_xlabel(
            "Sleep Duration (Hours)"
        )

        ax.set_ylabel(
            "Sedentary Minutes"
        )

        st.pyplot(fig)

        plt.close(fig)


    st.caption(
        """
        These charts show associations in the recorded
        data. They should not be interpreted as evidence
        that sleep causes changes in activity or sedentary
        behaviour.
        """
    )


else:

    st.info(
        """
        No matching activity and sleep records were found
        for the selected filters.
        """
    )


st.divider()


# ============================================================
# WEEKDAY SLEEP SUMMARY
# ============================================================

st.subheader(
    "Weekday Sleep Summary"
)


weekday_summary = (
    filtered_sleep
    .groupby("DayOfWeek")
    .agg(

        AverageSleepHours=(
            "SleepHours",
            "mean"
        ),

        AverageTimeInBedHours=(
            "TimeInBedHours",
            "mean"
        ),

        AverageSleepEfficiency=(
            "SleepEfficiency",
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
    "Sleep Insights"
)


weekday_analysis = (
    filtered_sleep
    .groupby("DayOfWeek")[
        "SleepHours"
    ]
    .mean()
)


if not weekday_analysis.empty:

    longest_sleep_day = (
        weekday_analysis.idxmax()
    )

    longest_sleep = (
        weekday_analysis.max()
    )

    shortest_sleep_day = (
        weekday_analysis.idxmin()
    )

    shortest_sleep = (
        weekday_analysis.min()
    )


    insight1, insight2, insight3 = (
        st.columns(3)
    )


    insight1.success(
        f"""
        **Longest Average Sleep**

        {longest_sleep_day}

        {longest_sleep:.2f} hours
        """
    )


    insight2.info(
        f"""
        **Shortest Average Sleep**

        {shortest_sleep_day}

        {shortest_sleep:.2f} hours
        """
    )


    insight3.info(
        f"""
        **Overall Sleep Efficiency**

        {avg_efficiency:.1f}%
        """
    )


# ============================================================
# DETAILED DATA
# ============================================================

st.divider()


with st.expander(
    "View Detailed Sleep Data"
):

    display_columns = [

        "Id",
        "SleepDay",
        "TotalSleepRecords",
        "TotalMinutesAsleep",
        "TotalTimeInBed",
        "SleepHours",
        "TimeInBedHours",
        "SleepEfficiency",
        "DayOfWeek"

    ]

    st.dataframe(
        filtered_sleep[
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
    "Strava Fitness Data Analytics | Sleep Analysis"
)