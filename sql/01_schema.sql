-- ============================================
-- FOOD DELIVERY DATABASE SCHEMA
-- ============================================

DROP TABLE IF EXISTS deliveries;
DROP TABLE IF EXISTS delivery_persons;
DROP TABLE IF EXISTS restaurants;

-- ============================================
-- DELIVERIES TABLE (Main table)
-- ============================================
CREATE TABLE deliveries (
    ID VARCHAR(50) PRIMARY KEY,
    Delivery_person_ID VARCHAR(50),
    Delivery_person_Age INT,
    Delivery_person_Ratings DECIMAL(3,2),
    
    -- Location data
    Restaurant_latitude DECIMAL(10,6),
    Restaurant_longitude DECIMAL(10,6),
    Delivery_location_latitude DECIMAL(10,6),
    Delivery_location_longitude DECIMAL(10,6),
    delivery_distance_km DECIMAL(10,2),
    distance_category VARCHAR(50),
    
    -- Time data
    Order_Date DATE,
    Time_Orderd TIME,
    Time_Order_picked TIME,
    order_year INT,
    order_month INT,
    order_day INT,
    order_dayofweek INT,
    order_week INT,
    day_name VARCHAR(20),
    order_hour INT,
    time_period VARCHAR(20),
    is_weekend BOOLEAN,
    is_peak_hour BOOLEAN,
    
    -- Conditions
    Weatherconditions VARCHAR(50),
    weather_severity INT,
    Road_traffic_density VARCHAR(50),
    traffic_level INT,
    Vehicle_condition VARCHAR(50),
    Type_of_order VARCHAR(50),
    Type_of_vehicle VARCHAR(50),
    multiple_deliveries INT,
    Festival BOOLEAN,
    City VARCHAR(100),
    
    -- Derived features
    age_group VARCHAR(50),
    rating_category VARCHAR(50),
    
    -- Target variable (NULL for test set)
    Time_taken_min DECIMAL(10,2),
    delivery_speed VARCHAR(20)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================
CREATE INDEX idx_delivery_person ON deliveries(Delivery_person_ID);
CREATE INDEX idx_order_date ON deliveries(Order_Date);
CREATE INDEX idx_city ON deliveries(City);
CREATE INDEX idx_weather ON deliveries(Weatherconditions);
CREATE INDEX idx_traffic ON deliveries(Road_traffic_density);
CREATE INDEX idx_time_period ON deliveries(time_period);
CREATE INDEX idx_distance ON deliveries(delivery_distance_km);
CREATE INDEX idx_delivery_time ON deliveries(Time_taken_min);