import pandas as pd
import numpy as np
from datetime import datetime
import re

print("Starting data cleaning and feature engineering...\n")

# ============================================
# LOAD DATA
# ============================================
train = pd.read_csv('data/raw data/train.csv')
test = pd.read_csv('data/raw data/test.csv')

print(f"Loaded train: {len(train):,} rows")
print(f"Loaded test: {len(test):,} rows")

# ============================================
# FUNCTION: Clean dataset
# ============================================
def clean_delivery_data(df, is_train=True):
    df = df.copy()
    
    print(f"\n{'='*60}")
    print(f"CLEANING {'TRAIN' if is_train else 'TEST'} DATASET")
    print(f"{'='*60}")
    
    # 0. CONVERT STRING COLUMNS TO NUMERIC
    print("\n[Step 0: Converting Data Types...]")
    
    # Convert Age to numeric
    if 'Delivery_person_Age' in df.columns:
        df['Delivery_person_Age'] = pd.to_numeric(df['Delivery_person_Age'], errors='coerce')
    
    # Convert Ratings to numeric
    if 'Delivery_person_Ratings' in df.columns:
        df['Delivery_person_Ratings'] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')
    
    # Convert Time_taken to numeric
    if 'Time_taken(min)' in df.columns:
        df['Time_taken(min)'] = pd.to_numeric(df['Time_taken(min)'], errors='coerce')
    
    # 1. HANDLE MISSING VALUES
    print("\n[Step 1: Handling Missing Values...]")
    print(f"Missing values before: {df.isnull().sum().sum()}")
    
    # Fill missing ages with median
    if 'Delivery_person_Age' in df.columns:
        df['Delivery_person_Age'].fillna(df['Delivery_person_Age'].median(), inplace=True)
    
    # Fill missing ratings with mean
    if 'Delivery_person_Ratings' in df.columns:
        df['Delivery_person_Ratings'].fillna(df['Delivery_person_Ratings'].mean(), inplace=True)
    
    # Fill categorical with mode
    cat_cols = ['Weatherconditions', 'Road_traffic_density', 'Type_of_order', 
                'Type_of_vehicle', 'City', 'Festival']
    for col in cat_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col].fillna(df[col].mode()[0], inplace=True)
    
    print(f"Missing values after: {df.isnull().sum().sum()}")
    
    # 2. CLEAN TEXT FIELDS
    print("\n[Step 2: Cleaning Text Fields...]")
    
    # Remove 'conditions ' prefix from weather if present
    if 'Weatherconditions' in df.columns:
        df['Weatherconditions'] = df['Weatherconditions'].str.replace('conditions ', '', regex=False)
        df['Weatherconditions'] = df['Weatherconditions'].str.strip().str.title()
    
    # Clean traffic density
    if 'Road_traffic_density' in df.columns:
        df['Road_traffic_density'] = df['Road_traffic_density'].str.strip().str.title()
    
    # Clean vehicle condition
    if 'Vehicle_condition' in df.columns:
        df['Vehicle_condition'] = df['Vehicle_condition'].astype(str).str.strip()
    
    # Clean city names
    if 'City' in df.columns:
        df['City'] = df['City'].str.strip().str.title()
    
    # 3. FIX DATA TYPES
    print("\n[Step 3: Converting Data Types...]")
    
    # Convert Order_Date
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y', errors='coerce')
    
    # Convert Time columns (they might be in format "11:50" or similar)
    if 'Time_Orderd' in df.columns:
        df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'], format='%H:%M', errors='coerce').dt.time
    
    if 'Time_Order_picked' in df.columns:
        df['Time_Order_picked'] = pd.to_datetime(df['Time_Order_picked'], format='%H:%M', errors='coerce').dt.time
    
    # Convert Festival to boolean
    if 'Festival' in df.columns:
        df['Festival'] = df['Festival'].map({'Yes': 1, 'No': 0})
    
    # Convert multiple_deliveries to int
    if 'multiple_deliveries' in df.columns:
        df['multiple_deliveries'] = pd.to_numeric(df['multiple_deliveries'], errors='coerce').fillna(0).astype(int)
    
    # 4. FEATURE ENGINEERING
    print("\n[Step 4: Creating New Features...]")
    
    # Extract date/time features
    df['order_year'] = df['Order_Date'].dt.year
    df['order_month'] = df['Order_Date'].dt.month
    df['order_day'] = df['Order_Date'].dt.day
    df['order_dayofweek'] = df['Order_Date'].dt.dayofweek
    df['order_week'] = df['Order_Date'].dt.isocalendar().week
    
    # Day names
    df['day_name'] = df['Order_Date'].dt.day_name()
    
    # Weekend flag
    df['is_weekend'] = df['order_dayofweek'].isin([5, 6]).astype(int)
    
    # Extract hour from Time_Orderd
    if 'Time_Orderd' in df.columns:
        df['order_hour'] = pd.to_datetime(df['Time_Orderd'].astype(str), format='%H:%M:%S', errors='coerce').dt.hour
        
        # Time period
        def get_time_period(hour):
            if pd.isna(hour):
                return 'Unknown'
            if 6 <= hour < 12:
                return 'Morning'
            elif 12 <= hour < 17:
                return 'Afternoon'
            elif 17 <= hour < 21:
                return 'Evening'
            else:
                return 'Night'
        
        df['time_period'] = df['order_hour'].apply(get_time_period)
        
        # Peak hours (lunch: 12-2pm, dinner: 7-9pm)
        df['is_peak_hour'] = df['order_hour'].isin([12, 13, 19, 20]).astype(int)
    
    # Calculate distance using Haversine formula
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points on Earth in km"""
        R = 6371  # Earth's radius in km
        
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = R * c
        
        return distance
    
    print("   Calculating delivery distances...")
    df['delivery_distance_km'] = haversine_distance(
        df['Restaurant_latitude'],
        df['Restaurant_longitude'],
        df['Delivery_location_latitude'],
        df['Delivery_location_longitude']
    )
    
    # Distance categories
    df['distance_category'] = pd.cut(
        df['delivery_distance_km'],
        bins=[0, 2, 5, 10, 100],
        labels=['Very Close (<2km)', 'Close (2-5km)', 'Medium (5-10km)', 'Far (>10km)']
    )
    
    # Age groups
    if 'Delivery_person_Age' in df.columns:
        df['age_group'] = pd.cut(
            df['Delivery_person_Age'],
            bins=[0, 25, 35, 45, 100],
            labels=['Young (18-25)', 'Mid (26-35)', 'Senior (36-45)', 'Veteran (45+)']
        )
    
    # Rating categories
    if 'Delivery_person_Ratings' in df.columns:
        df['rating_category'] = pd.cut(
            df['Delivery_person_Ratings'],
            bins=[0, 3.5, 4.0, 4.5, 5.0],
            labels=['Low (<3.5)', 'Average (3.5-4.0)', 'Good (4.0-4.5)', 'Excellent (4.5+)']
        )
    
    # Weather severity
    weather_severity = {
        'Sunny': 1,
        'Cloudy': 1,
        'Fog': 2,
        'Windy': 2,
        'Sandstorms': 3,
        'Stormy': 3
    }
    if 'Weatherconditions' in df.columns:
        df['weather_severity'] = df['Weatherconditions'].map(weather_severity).fillna(1)
    
    # Traffic density mapping
    traffic_mapping = {
        'Low': 1,
        'Medium': 2,
        'High': 3,
        'Jam': 4
    }
    if 'Road_traffic_density' in df.columns:
        df['traffic_level'] = df['Road_traffic_density'].map(traffic_mapping).fillna(2)
    
    # 5. HANDLE OUTLIERS (only for train set with target)
    if is_train and 'Time_taken(min)' in df.columns:
        print("\n[Step 5: Handling Outliers in Target Variable...]")
        
        # Clean Time_taken - remove "(min)" text if present
        if df['Time_taken(min)'].dtype == 'object':
            df['Time_taken(min)'] = df['Time_taken(min)'].str.extract(r'(\d+)').astype(float)
        
        # Only process if we have valid Time_taken values
        if df['Time_taken(min)'].notna().sum() > 0:
            Q1 = df['Time_taken(min)'].quantile(0.25)
            Q3 = df['Time_taken(min)'].quantile(0.75)
            IQR = Q3 - Q1
            
            # Only remove extreme outliers at 99th percentile
            outliers = df[(df['Time_taken(min)'] > df['Time_taken(min)'].quantile(0.99))]
            print(f"   Extreme outliers detected: {len(outliers):,} ({100*len(outliers)/len(df):.2f}%)")
            df = df[df['Time_taken(min)'] <= df['Time_taken(min)'].quantile(0.99)]
            print(f"   After removing extremes: {len(df):,} rows")
        else:
            print("   No valid Time_taken values to process for outliers")
        
        # Delivery speed category
        def categorize_speed(minutes):
            if minutes <= 20:
                return 'Very Fast'
            elif minutes <= 30:
                return 'Fast'
            elif minutes <= 40:
                return 'Normal'
            elif minutes <= 50:
                return 'Slow'
            else:
                return 'Very Slow'
        
        df['delivery_speed'] = df['Time_taken(min)'].apply(categorize_speed)
    
    print(f"\n[CLEANING COMPLETE: {len(df):,} rows × {len(df.columns)} columns]")
    
    return df

# ============================================
# CLEAN BOTH DATASETS
# ============================================

train_clean = clean_delivery_data(train, is_train=True)
test_clean = clean_delivery_data(test, is_train=False)

# ============================================
# SAVE CLEANED DATA
# ============================================

print(f"\n[Saving cleaned datasets...]")
train_clean.to_csv('data/cleaned data/train_clean.csv', index=False)
test_clean.to_csv('data/cleaned data/test_clean.csv', index=False)

print(f"\n[Files saved:]")
print(f"   - data/cleaned data/train_clean.csv ({len(train_clean):,} rows)")
print(f"   - data/cleaned data/test_clean.csv ({len(test_clean):,} rows)")

# ============================================
# CREATE DATA SUMMARY REPORT
# ============================================

report = f"""
{'='*60}
DATA CLEANING & FEATURE ENGINEERING REPORT
{'='*60}

TRAIN DATASET:
--------------
Original rows: {len(train):,}
Cleaned rows: {len(train_clean):,}
Columns: {len(train_clean.columns)}

Target Variable (Time_taken):
  Min: {train_clean['Time_taken(min)'].min():.2f} minutes
  Max: {train_clean['Time_taken(min)'].max():.2f} minutes
  Mean: {train_clean['Time_taken(min)'].mean():.2f} minutes
  Median: {train_clean['Time_taken(min)'].median():.2f} minutes

NEW FEATURES CREATED:
---------------------
Time Features: order_year, order_month, order_day, order_dayofweek, 
               order_week, day_name, order_hour, time_period
Binary Features: is_weekend, is_peak_hour, Festival (converted)
Distance Features: delivery_distance_km, distance_category
Categorical Groupings: age_group, rating_category, delivery_speed
Severity Scores: weather_severity, traffic_level

CATEGORICAL DISTRIBUTIONS:
--------------------------
Cities: {train_clean['City'].nunique()}
Weather conditions: {train_clean['Weatherconditions'].nunique()}
Traffic densities: {train_clean['Road_traffic_density'].nunique()}
Order types: {train_clean['Type_of_order'].nunique()}
Vehicle types: {train_clean['Type_of_vehicle'].nunique()}

MISSING VALUES:
---------------
Train: {train_clean.isnull().sum().sum()} missing values
Test: {test_clean.isnull().sum().sum()} missing values

Date Range: {train_clean['Order_Date'].min()} to {train_clean['Order_Date'].max()}

{'='*60}
"""

with open('docs/reports/cleaning_report.txt', 'w') as f:
    f.write(report)

print("\n[Report saved to: docs/reports/cleaning_report.txt]")
print("\n[DATA CLEANING COMPLETE!]")