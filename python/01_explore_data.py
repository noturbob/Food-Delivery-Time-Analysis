import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 60)
print("FOOD DELIVERY DATASET - INITIAL EXPLORATION")
print("=" * 60)

# Load all files
train = pd.read_csv('data/raw data/train.csv')
test = pd.read_csv('data/raw data/test.csv')
sample = pd.read_csv('data/raw data/Sample_Submission.csv')

# Convert columns to numeric for analysis
train['Time_taken(min)'] = pd.to_numeric(train['Time_taken(min)'], errors='coerce')
train['Delivery_person_Age'] = pd.to_numeric(train['Delivery_person_Age'], errors='coerce')
train['Delivery_person_Ratings'] = pd.to_numeric(train['Delivery_person_Ratings'], errors='coerce')

print(f"\n[DATASET SIZES]:")
print(f"Training set: {len(train):,} rows × {len(train.columns)} columns")
print(f"Test set: {len(test):,} rows × {len(test.columns)} columns")
print(f"Sample submission: {len(sample):,} rows × {len(sample.columns)} columns")

print(f"\n[COLUMNS (Train)]:")
for i, col in enumerate(train.columns, 1):
    dtype = train[col].dtype
    missing = train[col].isnull().sum()
    print(f"{i:2d}. {col:30s} | {str(dtype):10s} | Missing: {missing:5d} ({100*missing/len(train):5.2f}%)")

print(f"\n[TARGET VARIABLE (Time_taken)]:")
print(f"Min: {train['Time_taken(min)'].min():.2f} minutes")
print(f"Max: {train['Time_taken(min)'].max():.2f} minutes")
print(f"Mean: {train['Time_taken(min)'].mean():.2f} minutes")
print(f"Median: {train['Time_taken(min)'].median():.2f} minutes")
print(f"Std Dev: {train['Time_taken(min)'].std():.2f} minutes")

print(f"\n[CATEGORICAL VARIABLES]:")
cat_cols = ['Weatherconditions', 'Road_traffic_density', 'Type_of_order', 
            'Type_of_vehicle', 'Festival', 'City', 'Vehicle_condition']

for col in cat_cols:
    if col in train.columns:
        unique = train[col].nunique()
        print(f"\n{col}: {unique} unique values")
        print(train[col].value_counts().head(5))

print(f"\n[LOCATION DATA]:")
print(f"Restaurant locations: {train['Restaurant_latitude'].notna().sum():,} records")
print(f"Delivery locations: {train['Delivery_location_latitude'].notna().sum():,} records")
print(f"Lat range: {train['Restaurant_latitude'].min():.4f} to {train['Restaurant_latitude'].max():.4f}")
print(f"Lng range: {train['Restaurant_longitude'].min():.4f} to {train['Restaurant_longitude'].max():.4f}")

print(f"\n[DELIVERY PERSON DATA]:")
print(f"Unique delivery persons: {train['Delivery_person_ID'].nunique():,}")
print(f"Age range: {train['Delivery_person_Age'].min():.0f} - {train['Delivery_person_Age'].max():.0f} years")
print(f"Average rating: {train['Delivery_person_Ratings'].mean():.2f}")

print(f"\n[DATE RANGE]:")
train['Order_Date'] = pd.to_datetime(train['Order_Date'], format='%d-%m-%Y', errors='coerce')
print(f"From: {train['Order_Date'].min()}")
print(f"To: {train['Order_Date'].max()}")
print(f"Duration: {(train['Order_Date'].max() - train['Order_Date'].min()).days} days")

# Basic statistics
print(f"\n[NUMERICAL SUMMARY]:")
print(train[['Delivery_person_Age', 'Delivery_person_Ratings', 'Time_taken(min)']].describe())

print("\n[Exploration Complete!]")