-- ============================================
-- ADVANCED ANALYTICS & TIME SERIES
-- ============================================

-- ============================================
-- QUERY 16: MONTHLY DELIVERY TRENDS
-- ============================================

SELECT 
    order_year,
    order_month,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

-- ============================================
-- QUERY 17: DAILY DELIVERY VOLUME & PERFORMANCE
-- ============================================

SELECT 
    Order_Date,
    day_name,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Order_Date, day_name
ORDER BY Order_Date;

-- ============================================
-- QUERY 18: PEAK VS NON-PEAK PERFORMANCE
-- ============================================

SELECT 
    CASE WHEN is_peak_hour = 1 THEN 'Peak Hours' ELSE 'Off-Peak' END as period_type,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(SQRT(AVG(Time_taken_min * Time_taken_min) - AVG(Time_taken_min) * AVG(Time_taken_min)), 2) as time_std_dev
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY is_peak_hour;

-- ============================================
-- QUERY 19: WEATHER + TRAFFIC COMBINED IMPACT
-- ============================================

SELECT 
    Weatherconditions,
    Road_traffic_density,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Weatherconditions, Road_traffic_density
HAVING COUNT(*) >= 50  -- Minimum sample size
ORDER BY avg_time DESC
LIMIT 20;

-- ============================================
-- QUERY 20: VEHICLE CONDITION ANALYSIS
-- ============================================

SELECT 
    Vehicle_condition,
    Type_of_vehicle,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Vehicle_condition, Type_of_vehicle
ORDER BY Vehicle_condition, avg_time;

-- ============================================
-- QUERY 21: DELIVERY EFFICIENCY SCORE
-- (Time per km - lower is better)
-- ============================================

WITH efficiency_metrics AS (
    SELECT 
        Delivery_person_ID,
        COUNT(*) as deliveries,
        ROUND(AVG(Time_taken_min / NULLIF(delivery_distance_km, 0)), 2) as time_per_km,
        ROUND(AVG(Time_taken_min), 2) as avg_time,
        ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating
    FROM deliveries
    WHERE Time_taken_min IS NOT NULL
      AND delivery_distance_km > 0
    GROUP BY Delivery_person_ID
    HAVING COUNT(*) >= 10
)
SELECT 
    Delivery_person_ID,
    deliveries,
    time_per_km,
    avg_time,
    avg_rating,
    CASE 
        WHEN time_per_km <= 3 THEN 'Highly Efficient'
        WHEN time_per_km <= 5 THEN 'Efficient'
        WHEN time_per_km <= 7 THEN 'Average'
        ELSE 'Needs Improvement'
    END as efficiency_category
FROM efficiency_metrics
ORDER BY time_per_km
LIMIT 30;

-- ============================================
-- QUERY 22: MOVING AVERAGE (7-DAY)
-- ============================================

WITH daily_metrics AS (
    SELECT 
        Order_Date,
        COUNT(*) as deliveries,
        AVG(Time_taken_min) as avg_time
    FROM deliveries
    WHERE Time_taken_min IS NOT NULL
    GROUP BY Order_Date
)
SELECT 
    Order_Date,
    deliveries,
    ROUND(avg_time, 2) as avg_time,
    ROUND(AVG(avg_time) OVER (
        ORDER BY Order_Date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) as ma_7day
FROM daily_metrics
ORDER BY Order_Date;

-- ============================================
-- QUERY 23: PERCENTILE ANALYSIS (SQLite Compatible)
-- ============================================

SELECT 
    'Overall' as category,
    ROUND(MIN(Time_taken_min), 2) as min_time,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(MAX(Time_taken_min), 2) as max_time,
    COUNT(*) as total_deliveries
FROM deliveries
WHERE Time_taken_min IS NOT NULL;