import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Insights & Recommendations",
    page_icon="💡",
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

    sleep = pd.read_sql_query(
        "SELECT * FROM sleep_data",
        conn
    )

    hourly_steps = pd.read_sql_query(
        "SELECT * FROM hourly_steps",
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

    sleep["SleepDay"] = pd.to_datetime(
        sleep["SleepDay"]
    )

    hourly_steps["ActivityHour"] = pd.to_datetime(
        hourly_steps["ActivityHour"]
    )

    hourly_calories["ActivityHour"] = pd.to_datetime(
        hourly_calories["ActivityHour"]
    )

    return activity, sleep, hourly_steps, hourly_calories


activity, sleep, hourly_steps, hourly_calories = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("💡 Insights & Recommendations")

st.write(
    """
    This page summarizes the major findings from activity,
    sleep, calorie and hourly fitness analysis and converts
    them into actionable recommendations.
    """
)

st.divider()


# ============================================================
# BASIC METRICS
# ============================================================

avg_steps = activity["TotalSteps"].mean()

avg_calories = activity["Calories"].mean()

avg_active_minutes = activity[
    "TotalActiveMinutes"
].mean()

avg_sedentary = activity[
    "SedentaryMinutes"
].mean()

avg_sleep = sleep[
    "SleepHours"
].mean()


# ============================================================
# WEEKDAY ANALYSIS
# ============================================================

weekday_steps = (
    activity
    .groupby("DayOfWeek")["TotalSteps"]
    .mean()
)


most_active_day = weekday_steps.idxmax()
most_active_steps = weekday_steps.max()

least_active_day = weekday_steps.idxmin()
least_active_steps = weekday_steps.min()


# ============================================================
# CALORIE ANALYSIS
# ============================================================

weekday_calories = (
    activity
    .groupby("DayOfWeek")["Calories"]
    .mean()
)

highest_calorie_day = weekday_calories.idxmax()
highest_calorie_value = weekday_calories.max()


# ============================================================
# SLEEP ANALYSIS
# ============================================================

sleep = sleep.copy()

sleep["DayOfWeek"] = (
    sleep["SleepDay"]
    .dt.day_name()
)

weekday_sleep = (
    sleep
    .groupby("DayOfWeek")["SleepHours"]
    .mean()
)

best_sleep_day = weekday_sleep.idxmax()
best_sleep_hours = weekday_sleep.max()

lowest_sleep_day = weekday_sleep.idxmin()
lowest_sleep_hours = weekday_sleep.min()


# ============================================================
# SLEEP EFFICIENCY
# ============================================================

sleep["SleepEfficiency"] = (
    sleep["TotalMinutesAsleep"]
    /
    sleep["TotalTimeInBed"]
    * 100
)

avg_sleep_efficiency = (
    sleep["SleepEfficiency"]
    .mean()
)


# ============================================================
# HOURLY ANALYSIS
# ============================================================

hourly_steps = hourly_steps.copy()

hourly_steps["Hour"] = (
    hourly_steps[
        "ActivityHour"
    ].dt.hour
)

hourly_step_summary = (
    hourly_steps
    .groupby("Hour")[
        "StepTotal"
    ]
    .mean()
)

peak_hour = (
    hourly_step_summary.idxmax()
)

peak_hour_steps = (
    hourly_step_summary.max()
)

lowest_hour = (
    hourly_step_summary.idxmin()
)

lowest_hour_steps = (
    hourly_step_summary.min()
)


# ============================================================
# CORRELATIONS
# ============================================================

steps_calorie_corr = (
    activity[
        ["TotalSteps", "Calories"]
    ]
    .corr()
    .iloc[0, 1]
)

active_calorie_corr = (
    activity[
        ["TotalActiveMinutes", "Calories"]
    ]
    .corr()
    .iloc[0, 1]
)


# ============================================================
# KPI SUMMARY
# ============================================================

st.subheader("Overall Fitness Summary")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "👟 Avg. Steps",
    f"{avg_steps:,.0f}"
)

col2.metric(
    "🔥 Avg. Calories",
    f"{avg_calories:,.0f}"
)

col3.metric(
    "🏃 Active Minutes",
    f"{avg_active_minutes:.1f}"
)

col4.metric(
    "🪑 Sedentary Minutes",
    f"{avg_sedentary:.1f}"
)

col5.metric(
    "😴 Avg. Sleep",
    f"{avg_sleep:.2f} hrs"
)


st.divider()


# ============================================================
# KEY INSIGHTS
# ============================================================

st.subheader("Key Insights")


# ------------------------------------------------------------
# INSIGHT 1
# ------------------------------------------------------------

st.success(
    f"""
    ### 1. Weekday Activity Pattern

    **{most_active_day}** has the highest average
    activity with approximately **{most_active_steps:,.0f}
    steps**.

    **{least_active_day}** has the lowest average
    activity with approximately **{least_active_steps:,.0f}
    steps**.

    This shows that user activity varies across the week.
    """
)


# ------------------------------------------------------------
# INSIGHT 2
# ------------------------------------------------------------

st.info(
    f"""
    ### 2. Sedentary Behaviour

    Users record an average of approximately
    **{avg_sedentary:.1f} sedentary minutes per day**.

    This indicates that a substantial portion of recorded
    time is spent with very low physical activity.
    """
)


# ------------------------------------------------------------
# INSIGHT 3
# ------------------------------------------------------------

st.info(
    f"""
    ### 3. Active Time

    Users record approximately
    **{avg_active_minutes:.1f} active minutes per day**.

    The activity dataset also shows that lightly active
    minutes form a large part of total active time.
    """
)


# ------------------------------------------------------------
# INSIGHT 4
# ------------------------------------------------------------

st.info(
    f"""
    ### 4. Calories and Physical Activity

    Average daily calorie expenditure is approximately
    **{avg_calories:,.0f} calories**.

    The correlation between daily steps and calories is
    **{steps_calorie_corr:.2f}**.

    The correlation between total active minutes and
    calories is **{active_calorie_corr:.2f}**.

    These values indicate association, not causation.
    """
)


# ------------------------------------------------------------
# INSIGHT 5
# ------------------------------------------------------------

st.info(
    f"""
    ### 5. Sleep Pattern

    Average recorded sleep duration is approximately
    **{avg_sleep:.2f} hours**.

    **{best_sleep_day}** has the highest average sleep
    duration at approximately **{best_sleep_hours:.2f}
    hours**.

    **{lowest_sleep_day}** has the lowest average sleep
    duration at approximately **{lowest_sleep_hours:.2f}
    hours**.
    """
)


# ------------------------------------------------------------
# INSIGHT 6
# ------------------------------------------------------------

st.info(
    f"""
    ### 6. Sleep Efficiency

    Average sleep efficiency is approximately
    **{avg_sleep_efficiency:.1f}%**.

    Sleep efficiency represents the proportion of
    time in bed that is recorded as actual sleep.
    """
)


# ------------------------------------------------------------
# INSIGHT 7
# ------------------------------------------------------------

st.info(
    f"""
    ### 7. Peak Activity Hour

    The highest average hourly activity occurs around
    **{peak_hour}:00**, with approximately
    **{peak_hour_steps:,.0f} average steps**.

    The lowest activity occurs around
    **{lowest_hour}:00**.
    """
)


st.divider()


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("Recommendations")


recommendations = [

    (
        "Personalized Step Goals",
        """
        Provide users with personalized daily and weekly
        step goals based on their previous activity patterns.
        """
    ),

    (
        "Movement Reminders",
        """
        Send reminders during prolonged periods of inactivity
        to encourage users to stand, walk or perform light
        physical activity.
        """
    ),

    (
        "Time-Based Notifications",
        f"""
        Activity reminders can be scheduled around lower
        activity periods, while challenges can be promoted
        near commonly active periods such as around
        {peak_hour}:00.
        """
    ),

    (
        "Weekly Activity Challenges",
        f"""
        Since activity varies by weekday, applications can
        introduce targeted challenges particularly around
        lower-activity days such as {least_active_day}.
        """
    ),

    (
        "Sleep Monitoring",
        """
        Provide users with sleep trend summaries, bedtime
        reminders and comparisons between time in bed and
        actual sleep duration.
        """
    ),

    (
        "Integrated Wellness Dashboard",
        """
        Present steps, active minutes, sedentary time,
        calories and sleep together so users can understand
        their overall wellness patterns.
        """
    ),

    (
        "Personalized Engagement",
        """
        Use historical activity patterns to provide more
        relevant goals, reminders and progress messages
        instead of giving every user the same recommendation.
        """
    ),

    (
        "Tracker Wear Detection",
        """
        Extremely high sedentary time or unusual gaps may
        sometimes reflect non-wear rather than true
        inactivity. Improved wear detection can increase
        data reliability.
        """
    )
]


for number, (title, description) in enumerate(
    recommendations,
    start=1
):

    st.markdown(
        f"### {number}. {title}"
    )

    st.write(
        description
    )


st.divider()


# ============================================================
# FINDING → RECOMMENDATION TABLE
# ============================================================

st.subheader(
    "Finding to Recommendation Mapping"
)


mapping = pd.DataFrame({

    "Finding": [

        "Different activity levels across weekdays",

        "High sedentary time",

        "Light activity forms a large share of active time",

        "Activity and calories show measurable association",

        "Sleep duration varies",

        "Peak and low activity hours can be identified"

    ],

    "Recommendation": [

        "Introduce weekday-specific fitness challenges",

        "Provide inactivity and movement reminders",

        "Encourage gradual increases in moderate and vigorous activity",

        "Show activity and calorie trends together",

        "Provide sleep tracking and bedtime reminders",

        "Use time-based reminders and engagement notifications"

    ]

})


st.dataframe(
    mapping,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ============================================================
# BUSINESS IMPACT
# ============================================================

st.subheader(
    "Potential Business Impact"
)


col_a, col_b, col_c = st.columns(3)


col_a.info(
    """
    ### User Engagement

    Personalized reminders and goals may encourage users
    to interact with the fitness application more regularly.
    """
)


col_b.info(
    """
    ### User Retention

    Progress tracking, sleep insights and activity trends
    can provide users with ongoing value from the platform.
    """
)


col_c.info(
    """
    ### Personalization

    Fitness behaviour can be segmented by activity,
    sleep and usage patterns to support more relevant
    wellness features and communication.
    """
)


# ============================================================
# LIMITATIONS
# ============================================================

st.divider()

st.subheader("Dataset Limitations")


st.warning(
    """
    • The dataset contains a relatively small group of users.

    • Participant demographic information such as age,
      gender and occupation is not available.

    • Not every participant has records for every day.

    • Weight information is limited for many users.

    • Some high sedentary values may represent periods when
      the fitness tracker was not being worn.

    • The dataset was collected during a limited period in
      2016, so its patterns should not automatically be
      assumed to represent current fitness-device users.
    """
)


# ============================================================
# CONCLUSION
# ============================================================

st.divider()

st.subheader("Project Conclusion")


st.write(
    """
    The fitness-tracking data provides useful information
    about users' daily activity, sedentary behaviour,
    calorie expenditure, sleep patterns and hourly activity.

    The analysis demonstrates how raw fitness-device data
    can be cleaned, stored in SQL, analyzed using SQL and
    Python, and presented through an interactive Streamlit
    dashboard.

    The findings can support personalized activity goals,
    movement reminders, sleep monitoring and better
    engagement strategies in fitness and wellness
    applications.
    """
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Strava Fitness Data Analytics | Insights & Recommendations"
)