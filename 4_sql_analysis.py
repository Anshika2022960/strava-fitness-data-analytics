import sqlite3
import pandas as pd

# ============================================================
# STRAVA FITNESS DATA ANALYTICS
# PHASE 5A - 25 SQL ANALYTICAL QUERIES
# ============================================================

DB_PATH = "database/fitness_analytics.db"

conn = sqlite3.connect(DB_PATH)


def run_query(number, title, query):
    """Execute and display an SQL query."""
    print("\n" + "=" * 80)
    print(f"QUERY {number}: {title}")
    print("=" * 80)

    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))

    return result


# ============================================================
# SECTION A: BASIC FITNESS OVERVIEW
# ============================================================

# Q1. How many unique users are in the activity dataset?

q1 = """
SELECT
    COUNT(DISTINCT Id) AS TotalUsers
FROM daily_activity;
"""

run_query(1, "Total Unique Users", q1)


# Q2. How many daily activity records are available?

q2 = """
SELECT
    COUNT(*) AS TotalActivityRecords
FROM daily_activity;
"""

run_query(2, "Total Daily Activity Records", q2)


# Q3. What is the average number of steps per day?

q3 = """
SELECT
    ROUND(AVG(TotalSteps), 2) AS AverageDailySteps
FROM daily_activity;
"""

run_query(3, "Average Daily Steps", q3)


# Q4. What is the average distance travelled per day?

q4 = """
SELECT
    ROUND(AVG(TotalDistance), 2) AS AverageDailyDistance
FROM daily_activity;
"""

run_query(4, "Average Daily Distance", q4)


# Q5. What is the average daily calorie expenditure?

q5 = """
SELECT
    ROUND(AVG(Calories), 2) AS AverageDailyCalories
FROM daily_activity;
"""

run_query(5, "Average Daily Calories", q5)


# ============================================================
# SECTION B: USER ACTIVITY ANALYSIS
# ============================================================

# Q6. Which 10 users have the highest average daily step count?

q6 = """
SELECT
    Id,
    ROUND(AVG(TotalSteps), 2) AS AverageSteps
FROM daily_activity
GROUP BY Id
ORDER BY AverageSteps DESC
LIMIT 10;
"""

run_query(6, "Top 10 Users by Average Steps", q6)


# Q7. Which 10 users have the lowest average daily step count?

q7 = """
SELECT
    Id,
    ROUND(AVG(TotalSteps), 2) AS AverageSteps
FROM daily_activity
GROUP BY Id
ORDER BY AverageSteps ASC
LIMIT 10;
"""

run_query(7, "Bottom 10 Users by Average Steps", q7)


# Q8. What is the average step count for each weekday?

q8 = """
SELECT
    DayOfWeek,
    ROUND(AVG(TotalSteps), 2) AS AverageSteps
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
"""

run_query(8, "Average Steps by Weekday", q8)


# Q9. What is the average total active time per day?

q9 = """
SELECT
    ROUND(AVG(TotalActiveMinutes), 2)
        AS AverageActiveMinutes
FROM daily_activity;
"""

run_query(9, "Average Daily Active Minutes", q9)


# Q10. How much time is spent at different activity intensities?

q10 = """
SELECT
    ROUND(AVG(VeryActiveMinutes), 2)
        AS AvgVeryActiveMinutes,

    ROUND(AVG(FairlyActiveMinutes), 2)
        AS AvgFairlyActiveMinutes,

    ROUND(AVG(LightlyActiveMinutes), 2)
        AS AvgLightlyActiveMinutes
FROM daily_activity;
"""

run_query(10, "Average Minutes by Activity Intensity", q10)


# ============================================================
# SECTION C: SEDENTARY BEHAVIOUR
# ============================================================

# Q11. What is the average sedentary time per day?

q11 = """
SELECT
    ROUND(AVG(SedentaryMinutes), 2)
        AS AverageSedentaryMinutes,

    ROUND(AVG(SedentaryMinutes) / 60.0, 2)
        AS AverageSedentaryHours
FROM daily_activity;
"""

run_query(11, "Average Daily Sedentary Time", q11)


# Q12. Which users have the highest average sedentary time?

q12 = """
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
"""

run_query(12, "Top 10 Users by Sedentary Time", q12)


# Q13. What is the average sedentary time by weekday?

q13 = """
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
"""

run_query(13, "Average Sedentary Minutes by Weekday", q13)


# ============================================================
# SECTION D: CALORIE ANALYSIS
# ============================================================

# Q14. Which users have the highest average calorie expenditure?

q14 = """
SELECT
    Id,
    ROUND(AVG(Calories), 2) AS AverageCalories
FROM daily_activity
GROUP BY Id
ORDER BY AverageCalories DESC
LIMIT 10;
"""

run_query(14, "Top 10 Users by Average Calories", q14)


# Q15. What is the average calorie expenditure for each weekday?

q15 = """
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
"""

run_query(15, "Average Calories by Weekday", q15)


# Q16. How do steps and calories compare for each user?

q16 = """
SELECT
    Id,

    ROUND(AVG(TotalSteps), 2)
        AS AverageSteps,

    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM daily_activity

GROUP BY Id

ORDER BY AverageSteps DESC;
"""

run_query(16, "Average Steps vs Calories by User", q16)


# ============================================================
# SECTION E: SLEEP ANALYSIS
# ============================================================

# Q17. What is the overall average sleep duration?

q17 = """
SELECT
    ROUND(AVG(SleepHours), 2)
        AS AverageSleepHours
FROM sleep_data;
"""

run_query(17, "Average Sleep Duration", q17)


# Q18. Which users sleep the longest on average?

q18 = """
SELECT
    Id,

    ROUND(AVG(SleepHours), 2)
        AS AverageSleepHours

FROM sleep_data

GROUP BY Id

ORDER BY AverageSleepHours DESC

LIMIT 10;
"""

run_query(18, "Top 10 Users by Average Sleep", q18)


# Q19. Which users sleep the least on average?

q19 = """
SELECT
    Id,

    ROUND(AVG(SleepHours), 2)
        AS AverageSleepHours

FROM sleep_data

GROUP BY Id

ORDER BY AverageSleepHours ASC

LIMIT 10;
"""

run_query(19, "Bottom 10 Users by Average Sleep", q19)


# Q20. How efficient is users' sleep?

q20 = """
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
"""

run_query(20, "Sleep Efficiency by User", q20)


# ============================================================
# SECTION F: HOURLY ACTIVITY ANALYSIS
# ============================================================

# Q21. At what hours do users record the most steps?

q21 = """
SELECT
    strftime('%H', ActivityHour) AS Hour,

    ROUND(AVG(StepTotal), 2)
        AS AverageSteps

FROM hourly_steps

GROUP BY Hour

ORDER BY AverageSteps DESC;
"""

run_query(21, "Average Steps by Hour", q21)


# Q22. At what hours is calorie expenditure highest?

q22 = """
SELECT
    strftime('%H', ActivityHour) AS Hour,

    ROUND(AVG(Calories), 2)
        AS AverageCalories

FROM hourly_calories

GROUP BY Hour

ORDER BY AverageCalories DESC;
"""

run_query(22, "Average Calories by Hour", q22)


# ============================================================
# SECTION G: ADVANCED CROSS-DATA ANALYSIS
# ============================================================

# Q23. How do sleep duration and daily steps compare?

q23 = """
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
"""

run_query(23, "Sleep Duration vs Daily Steps", q23)


# Q24. How do sleep duration and sedentary time compare?

q24 = """
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
"""

run_query(24, "Sleep vs Sedentary Time", q24)


# Q25. What is the overall activity profile of each user?

q25 = """
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
"""

run_query(25, "Complete User Activity Profile", q25)


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()

print("\n" + "=" * 80)
print("ALL 25 SQL QUERIES EXECUTED SUCCESSFULLY")
print("=" * 80)