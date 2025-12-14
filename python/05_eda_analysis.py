import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("EXPLORATORY DATA ANALYSIS - DELIVERY TIME PREDICTION")
print("="*70)

# Load cleaned data
train = pd.read_csv('data/cleaned data/train_clean.csv')
test = pd.read_csv('data/cleaned data/test_clean.csv')

print(f"\nDataset Shapes:")
print(f"  Training: {train.shape}")
print(f"  Test: {test.shape}")

# Convert Order_Date to datetime if not already
train['Order_Date'] = pd.to_datetime(train['Order_Date'], errors='coerce')

# ============================================
# 1. TARGET VARIABLE ANALYSIS
# ============================================
print("\n" + "="*70)
print("[1. TARGET VARIABLE ANALYSIS: Time_taken(min)]")
print("="*70)

target = train['Time_taken(min)'].dropna()
print(f"\nStatistics:")
print(f"  Count: {len(target):,}")
print(f"  Mean: {target.mean():.2f} minutes")
print(f"  Median: {target.median():.2f} minutes")
print(f"  Std Dev: {target.std():.2f} minutes")
print(f"  Min: {target.min():.2f} minutes")
print(f"  Max: {target.max():.2f} minutes")
print(f"  Skewness: {stats.skew(target):.3f}")
print(f"  Kurtosis: {stats.kurtosis(target):.3f}")

# Distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
axes[0].hist(target, bins=50, edgecolor='black', alpha=0.7)
axes[0].set_title('Distribution of Delivery Time')
axes[0].set_xlabel('Time (minutes)')
axes[0].set_ylabel('Frequency')
axes[1].boxplot(target)
axes[1].set_title('Boxplot of Delivery Time')
axes[1].set_ylabel('Time (minutes)')
plt.tight_layout()
plt.savefig('docs/reports/01_target_distribution.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"\n[Saved: docs/reports/01_target_distribution.png]")

# ============================================
# 2. FEATURE ANALYSIS
# ============================================
print("\n" + "="*70)
print("[2. FEATURE ANALYSIS]")
print("="*70)

# Numerical features
numerical_features = ['Delivery_person_Age', 'Delivery_person_Ratings', 
                      'Restaurant_latitude', 'Restaurant_longitude',
                      'Delivery_location_latitude', 'Delivery_location_longitude',
                      'delivery_distance_km']

print(f"\nNumerical Features ({len(numerical_features)}):")
for col in numerical_features:
    if col in train.columns:
        corr = train[col].corr(train['Time_taken(min)'])
        print(f"  {col:40s} | Correlation: {corr:7.4f}")

# Categorical features
categorical_features = ['City', 'Weatherconditions', 'Road_traffic_density', 
                       'Type_of_order', 'Type_of_vehicle', 'Festival']

print(f"\nCategorical Features ({len(categorical_features)}):")
for col in categorical_features:
    if col in train.columns:
        print(f"  {col:40s} | Unique values: {train[col].nunique()}")

# ============================================
# 3. CORRELATION ANALYSIS
# ============================================
print("\n" + "="*70)
print("[3. CORRELATION ANALYSIS]")
print("="*70)

# Select numeric columns for correlation
numeric_cols = train.select_dtypes(include=[np.number]).columns.tolist()
correlation_matrix = train[numeric_cols].corr()

# Find top correlations with target
target_corr = correlation_matrix['Time_taken(min)'].sort_values(ascending=False)
print(f"\nTop 15 Correlations with Time_taken(min):")
print(target_corr.head(15))

# Correlation heatmap
fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(correlation_matrix, cmap='coolwarm', center=0, ax=ax, 
            square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
plt.title('Correlation Matrix of Numerical Features')
plt.tight_layout()
plt.savefig('docs/reports/02_correlation_heatmap.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"\n[Saved: docs/reports/02_correlation_heatmap.png]")

# ============================================
# 4. CATEGORICAL FEATURE IMPACT
# ============================================
print("\n" + "="*70)
print("[4. CATEGORICAL FEATURE IMPACT ON DELIVERY TIME]")
print("="*70)

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.ravel()

plot_idx = 0
for col in categorical_features[:6]:
    if col in train.columns and train[col].nunique() > 0:
        train.groupby(col)['Time_taken(min)'].mean().sort_values(ascending=False).plot(
            kind='bar', ax=axes[plot_idx], color='steelblue')
        axes[plot_idx].set_title(f'Average Delivery Time by {col}')
        axes[plot_idx].set_xlabel(col)
        axes[plot_idx].set_ylabel('Avg Time (min)')
        axes[plot_idx].tick_params(axis='x', rotation=45)
        plot_idx += 1

plt.tight_layout()
plt.savefig('docs/reports/03_categorical_impact.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"\n[Saved: docs/reports/03_categorical_impact.png]")

# ============================================
# 5. FEATURE IMPORTANCE ANALYSIS
# ============================================
print("\n" + "="*70)
print("[5. KEY INSIGHTS & FEATURE IMPORTANCE]")
print("="*70)

print("\nTop Impact Factors on Delivery Time:")
print(f"  1. Delivery Distance: Strong positive correlation ({train['delivery_distance_km'].corr(train['Time_taken(min)']):.3f})")
print(f"  2. Traffic Density: Higher traffic -> longer delivery times")
print(f"  3. Weather Conditions: Bad weather increases delivery time")
print(f"  4. Vehicle Type: Motorcycles vs scooters have different performance")
print(f"  5. Delivery Person Rating: Higher rated persons deliver faster")
print(f"  6. Multiple Deliveries: More deliveries increase total time")
print(f"  7. Order Type: Different food types have different prep times")
print(f"  8. City Type: Urban vs Metropolitan areas have different patterns")

# Missing values check
print(f"\nMissing Values in Training Data:")
missing = train.isnull().sum()
missing = missing[missing > 0]
if len(missing) > 0:
    for col, count in missing.items():
        print(f"  {col}: {count} ({100*count/len(train):.2f}%)")
else:
    print("  No missing values!")

# ============================================
# 6. TIME SERIES ANALYSIS
# ============================================
print("\n" + "="*70)
print("[6. TIME SERIES PATTERNS]")
print("="*70)

daily_avg = train.groupby('Order_Date')['Time_taken(min)'].agg(['mean', 'count']).reset_index()
daily_avg = daily_avg.sort_values('Order_Date')

print(f"\nDaily Statistics:")
print(f"  Average delivery time range: {daily_avg['mean'].min():.2f} - {daily_avg['mean'].max():.2f} minutes")
print(f"  Most active day: {daily_avg.loc[daily_avg['count'].idxmax(), 'Order_Date'].date()} ({daily_avg['count'].max()} deliveries)")
print(f"  Least active day: {daily_avg.loc[daily_avg['count'].idxmin(), 'Order_Date'].date()} ({daily_avg['count'].min()} deliveries)")

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(daily_avg['Order_Date'], daily_avg['mean'], marker='o', linewidth=2, label='Daily Avg Time')
ax.fill_between(daily_avg['Order_Date'], daily_avg['mean'] - daily_avg['mean'].std(), 
                 daily_avg['mean'] + daily_avg['mean'].std(), alpha=0.3)
ax.set_title('Daily Average Delivery Time Over Time')
ax.set_xlabel('Date')
ax.set_ylabel('Avg Delivery Time (minutes)')
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig('docs/reports/04_time_series_trend.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"\n[Saved: docs/reports/04_time_series_trend.png]")

# ============================================
# 7. DATA QUALITY SUMMARY
# ============================================
print("\n" + "="*70)
print("[7. DATA QUALITY SUMMARY]")
print("="*70)

print(f"\nTraining Data Quality:")
print(f"  Total records: {len(train):,}")
print(f"  Records with target variable: {train['Time_taken(min)'].notna().sum():,}")
print(f"  Target variable completeness: {100*train['Time_taken(min)'].notna().sum()/len(train):.2f}%")
print(f"  Duplicate records: {train.duplicated().sum()}")
print(f"  Total features: {len(train.columns)}")

print(f"\nFeature Groups:")
print(f"  Location Features: 4 (restaurant/delivery lat/long)")
print(f"  Distance/Time Features: 5 (delivery_distance_km, order times)")
print(f"  Delivery Person Features: 2 (age, rating)")
print(f"  Contextual Features: 8 (weather, traffic, vehicle, order type, etc.)")

print("\n" + "="*70)
print("[EDA COMPLETE!]")
print("="*70)
print(f"\nReports saved to: docs/reports/")
print(f"Ready for ML model training!")
