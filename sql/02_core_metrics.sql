-- ============================================
-- FOOD DELIVERY: CORE BUSINESS METRICS
-- ============================================

-- ============================================
-- QUERY 1: OVERALL BUSINESS SUMMARY
-- ============================================

SELECT 
    COUNT(*) as total_deliveries,
    COUNT(DISTINCT Delivery_person_ID) as total_delivery_persons,
    COUNT(DISTINCT City) as cities_covered,
    ROUND(AVG(Time_taken_min), 2) as avg_delivery_time,
    ROUND(MIN(Time_taken_min), 2) as fastest_delivery,
    ROUND(MAX(Time_taken_min), 2) as slowest_delivery,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_delivery_rating
FROM deliveries
WHERE Time_taken_min IS NOT NULL;

-- ============================================
-- QUERY 2: DELIVERY TIME BY CITY
-- ============================================

SELECT 
    City,
    COUNT(*) as total_deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(MIN(Time_taken_min), 2) as min_time,
    ROUND(MAX(Time_taken_min), 2) as max_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(AVG(Time_taken_min / delivery_distance_km), 2) as time_per_km
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY City
ORDER BY avg_time DESC;

-- ============================================
-- QUERY 3: PEAK HOURS ANALYSIS
-- ============================================

SELECT 
    order_hour,
    time_period,
    COUNT(*) as total_orders,
    ROUND(AVG(Time_taken_min), 2) as avg_delivery_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    is_peak_hour
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY order_hour, time_period, is_peak_hour
ORDER BY order_hour;

-- ============================================
-- QUERY 4: DAY OF WEEK PATTERNS
-- ============================================

SELECT 
    day_name,
    order_dayofweek,
    is_weekend,
    COUNT(*) as total_deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY day_name, order_dayofweek, is_weekend
ORDER BY order_dayofweek;

-- ============================================
-- QUERY 5: WEATHER IMPACT ON DELIVERY TIME
-- ============================================

SELECT 
    Weatherconditions,
    weather_severity,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(MIN(Time_taken_min), 2) as min_time,
    ROUND(MAX(Time_taken_min), 2) as max_time,
    ROUND(SQRT(AVG(Time_taken_min * Time_taken_min) - AVG(Time_taken_min) * AVG(Time_taken_min)), 2) as std_dev
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Weatherconditions, weather_severity
ORDER BY avg_time DESC;

-- ============================================
-- QUERY 6: TRAFFIC DENSITY ANALYSIS
-- ============================================

SELECT 
    Road_traffic_density,
    traffic_level,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Road_traffic_density, traffic_level
ORDER BY traffic_level;

-- ============================================
-- QUERY 7: VEHICLE TYPE PERFORMANCE
-- ============================================

SELECT 
    Type_of_vehicle,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating,
    ROUND(AVG(Time_taken_min / delivery_distance_km), 2) as efficiency_time_per_km
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Type_of_vehicle
ORDER BY avg_time;

-- ============================================
-- QUERY 8: DISTANCE CATEGORY ANALYSIS
-- ============================================

SELECT 
    distance_category,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(MIN(Time_taken_min), 2) as min_time,
    ROUND(MAX(Time_taken_min), 2) as max_time
FROM deliveries
WHERE Time_taken_min IS NOT NULL
  AND distance_category IS NOT NULL
GROUP BY distance_category
ORDER BY 
    CASE distance_category
        WHEN 'Very Close (<2km)' THEN 1
        WHEN 'Close (2-5km)' THEN 2
        WHEN 'Medium (5-10km)' THEN 3
        WHEN 'Far (>10km)' THEN 4
    END;

-- ============================================
-- QUERY 9: DELIVERY SPEED DISTRIBUTION
-- ============================================

SELECT 
    delivery_speed,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance
FROM deliveries
WHERE Time_taken_min IS NOT NULL
  AND delivery_speed IS NOT NULL
GROUP BY delivery_speed
ORDER BY 
    CASE delivery_speed
        WHEN 'Very Fast' THEN 1
        WHEN 'Fast' THEN 2
        WHEN 'Normal' THEN 3
        WHEN 'Slow' THEN 4
        WHEN 'Very Slow' THEN 5
    END;

-- ============================================
-- QUERY 10: FESTIVAL IMPACT
-- ============================================

SELECT 
    CASE WHEN Festival = 1 THEN 'Festival Day' ELSE 'Regular Day' END as day_type,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Festival
ORDER BY Festival DESC;