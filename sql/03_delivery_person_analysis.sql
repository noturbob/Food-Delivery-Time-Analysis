-- ============================================
-- DELIVERY PERSON PERFORMANCE METRICS
-- ============================================

-- ============================================
-- QUERY 11: TOP 20 FASTEST DELIVERY PERSONS
-- ============================================

SELECT 
    Delivery_person_ID,
    COUNT(*) as total_deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating,
    ROUND(AVG(Delivery_person_Age), 0) as age
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Delivery_person_ID
HAVING COUNT(*) >= 10  -- At least 10 deliveries
ORDER BY avg_time
LIMIT 20;

-- ============================================
-- QUERY 12: DELIVERY PERSON AGE GROUP PERFORMANCE
-- ============================================

SELECT 
    age_group,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance
FROM deliveries
WHERE Time_taken_min IS NOT NULL
  AND age_group IS NOT NULL
GROUP BY age_group
ORDER BY 
    CASE age_group
        WHEN 'Young (18-25)' THEN 1
        WHEN 'Mid (26-35)' THEN 2
        WHEN 'Senior (36-45)' THEN 3
        WHEN 'Veteran (45+)' THEN 4
    END;

-- ============================================
-- QUERY 13: RATING VS DELIVERY TIME CORRELATION
-- ============================================

SELECT 
    rating_category,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(Delivery_person_Ratings), 2) as avg_rating,
    ROUND(MIN(Time_taken_min), 2) as min_time,
    ROUND(MAX(Time_taken_min), 2) as max_time
FROM deliveries
WHERE Time_taken_min IS NOT NULL
  AND rating_category IS NOT NULL
GROUP BY rating_category
ORDER BY 
    CASE rating_category
        WHEN 'Excellent (4.5+)' THEN 1
        WHEN 'Good (4.0-4.5)' THEN 2
        WHEN 'Average (3.5-4.0)' THEN 3
        WHEN 'Low (<3.5)' THEN 4
    END;

-- ============================================
-- QUERY 14: MULTIPLE DELIVERIES IMPACT
-- ============================================

SELECT 
    multiple_deliveries,
    COUNT(*) as total_orders,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY multiple_deliveries
ORDER BY multiple_deliveries;

-- ============================================
-- QUERY 15: ORDER TYPE ANALYSIS
-- ============================================

SELECT 
    Type_of_order,
    COUNT(*) as deliveries,
    ROUND(AVG(Time_taken_min), 2) as avg_time,
    ROUND(AVG(delivery_distance_km), 2) as avg_distance,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM deliveries
WHERE Time_taken_min IS NOT NULL
GROUP BY Type_of_order
ORDER BY deliveries DESC;