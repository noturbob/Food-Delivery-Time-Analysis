import pandas as pd
from sqlalchemy import create_engine, text
import time

print("Loading data to SQL database...\n")

# Create SQLite connection
engine = create_engine('sqlite:///data/food_delivery.db')

# Load cleaned data
train = pd.read_csv('data/cleaned data/train_clean.csv')
test = pd.read_csv('data/cleaned data/test_clean.csv')

print(f"[Loaded datasets:]")
print(f"   Train: {len(train):,} rows")
print(f"   Test: {len(test):,} rows")

# Convert date/time columns
date_cols = ['Order_Date']
for col in date_cols:
    if col in train.columns:
        train[col] = pd.to_datetime(train[col], errors='coerce')
        test[col] = pd.to_datetime(test[col], errors='coerce')

# Rename Time_taken(min) to Time_taken_min for SQL compatibility
if 'Time_taken(min)' in train.columns:
    train.rename(columns={'Time_taken(min)': 'Time_taken_min'}, inplace=True)

# ============================================
# LOAD TO DATABASE
# ============================================

print(f"\n[Loading to SQLite database...]")

start_time = time.time()

# Load train data
train.to_sql('deliveries', engine, if_exists='replace', index=False, chunksize=1000)

# Add test data (append mode)
test['Time_taken_min'] = None  # Test doesn't have target
test.to_sql('deliveries', engine, if_exists='append', index=False, chunksize=1000)

elapsed = time.time() - start_time

print(f"[Loaded in {elapsed:.2f} seconds]")

# ============================================
# VERIFY
# ============================================

print("\n[Verifying database...]")

with engine.connect() as conn:
    # Count total records
    result = conn.execute(text("SELECT COUNT(*) FROM deliveries"))
    total = result.fetchone()[0]
    print(f"   Total records: {total:,}")
    
    # Count with target variable (train set)
    result = conn.execute(text("SELECT COUNT(*) FROM deliveries WHERE Time_taken_min IS NOT NULL"))
    train_count = result.fetchone()[0]
    print(f"   Train records: {train_count:,}")
    
    # Count without target (test set)
    result = conn.execute(text("SELECT COUNT(*) FROM deliveries WHERE Time_taken_min IS NULL"))
    test_count = result.fetchone()[0]
    print(f"   Test records: {test_count:,}")
    
    # Sample data
    print(f"\n[Sample records:]")
    result = conn.execute(text("SELECT ID, City, Time_taken_min, delivery_distance_km FROM deliveries LIMIT 5"))
    for row in result:
        print(f"   {row}")

print(f"\n[Database created: data/food_delivery.db]")
print(f"[Loading complete!]")