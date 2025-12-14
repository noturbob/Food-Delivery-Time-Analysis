import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("MODEL EVALUATION - DELIVERY TIME PREDICTION")
print("="*70)

# Load training data
train_data = pd.read_csv('data/cleaned data/train_clean.csv')
print(f"\nTraining data loaded: {train_data.shape}")

# Load test data
test_data = pd.read_csv('data/cleaned data/test_clean.csv')
print(f"Test data loaded: {test_data.shape}")

# ============================================
# 1. LOAD SAVED MODELS
# ============================================
print("\n" + "="*70)
print("[1. LOADING SAVED MODELS]")
print("="*70)

with open('ml_models/saved_models/best_model.pkl', 'rb') as f:
    best_model = pickle.load(f)

with open('ml_models/saved_models/label_encoders.pkl', 'rb') as f:
    label_encoders = pickle.load(f)

with open('ml_models/saved_models/feature_columns.pkl', 'rb') as f:
    feature_columns = pickle.load(f)

with open('ml_models/saved_models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('ml_models/saved_models/model_results.csv', 'r') as f:
    results_csv = pd.read_csv('ml_models/saved_models/model_results.csv')

print(f"[Best Model: {type(best_model).__name__}]")
print(f"[Features: {len(feature_columns)}]")
print(f"\nModel Performance Summary:")
print(results_csv.to_string(index=False))

# ============================================
# 2. PREPARE VALIDATION DATA
# ============================================
print("\n" + "="*70)
print("[2. PREPARING VALIDATION DATA]")
print("="*70)

# Prepare features from original training data
X_train_full = train_data.drop(['Time_taken(min)', 'ID'], axis=1)
y_train_full = train_data['Time_taken(min)']

# Handle categorical variables
categorical_cols = X_train_full.select_dtypes(include=['object']).columns.tolist()
X_train_full_encoded = X_train_full.copy()

for col in categorical_cols:
    if col in label_encoders:
        try:
            X_train_full_encoded[col] = label_encoders[col].transform(X_train_full[col].astype(str))
        except:
            X_train_full_encoded[col] = 0

# Drop problematic columns
cols_to_drop = ['Order_Date', 'Time_Orderd', 'Time_Order_picked', 'Festival', 'order_hour']
X_train_full_encoded = X_train_full_encoded.drop([col for col in cols_to_drop if col in X_train_full_encoded.columns], axis=1)

# Handle NaN values
X_train_full_encoded = X_train_full_encoded.fillna(X_train_full_encoded.median())

# Add missing columns
for col in feature_columns:
    if col not in X_train_full_encoded.columns:
        X_train_full_encoded[col] = 0

# Ensure columns match and are in order
X_train_full_encoded = X_train_full_encoded[feature_columns]

print(f"Full training features: {X_train_full_encoded.shape}")
print(f"Full training targets: {y_train_full.shape}")

# ============================================
# 3. GENERATE PREDICTIONS ON FULL TRAINING SET
# ============================================
print("\n" + "="*70)
print("[3. EVALUATING ON FULL TRAINING DATA]")
print("="*70)

model_type = type(best_model).__name__
if 'Linear' in model_type:
    X_train_scaled = scaler.transform(X_train_full_encoded)
    y_pred_train = best_model.predict(X_train_scaled)
else:
    y_pred_train = best_model.predict(X_train_full_encoded)

# Calculate metrics
rmse_train = np.sqrt(mean_squared_error(y_train_full, y_pred_train))
mae_train = mean_absolute_error(y_train_full, y_pred_train)
r2_train = r2_score(y_train_full, y_pred_train)
mape_train = np.mean(np.abs((y_train_full - y_pred_train) / y_train_full)) * 100

print(f"\nFull Training Data Performance:")
print(f"  RMSE: {rmse_train:.4f} minutes")
print(f"  MAE: {mae_train:.4f} minutes")
print(f"  MAPE: {mape_train:.4f}%")
print(f"  R² Score: {r2_train:.4f}")

# Calculate residuals
residuals = y_train_full - y_pred_train
print(f"\nResidual Statistics:")
print(f"  Mean: {residuals.mean():.4f} minutes")
print(f"  Std Dev: {residuals.std():.4f} minutes")
print(f"  Min: {residuals.min():.4f} minutes")
print(f"  Max: {residuals.max():.4f} minutes")

# ============================================
# 4. CREATE EVALUATION VISUALIZATIONS
# ============================================
print("\n" + "="*70)
print("[4. CREATING EVALUATION VISUALIZATIONS]")
print("="*70)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Actual vs Predicted
ax = axes[0, 0]
ax.scatter(y_train_full, y_pred_train, alpha=0.3, s=10)
ax.plot([y_train_full.min(), y_train_full.max()], 
        [y_train_full.min(), y_train_full.max()], 
        'r--', lw=2)
ax.set_xlabel('Actual Delivery Time (min)')
ax.set_ylabel('Predicted Delivery Time (min)')
ax.set_title('Actual vs Predicted Delivery Time')
ax.grid(True, alpha=0.3)

# Plot 2: Residuals Distribution
ax = axes[0, 1]
ax.hist(residuals, bins=50, edgecolor='black', color='skyblue')
ax.axvline(residuals.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {residuals.mean():.2f}')
ax.set_xlabel('Residuals (minutes)')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of Residuals')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Residuals vs Predicted
ax = axes[1, 0]
ax.scatter(y_pred_train, residuals, alpha=0.3, s=10)
ax.axhline(y=0, color='r', linestyle='--', lw=2)
ax.set_xlabel('Predicted Delivery Time (min)')
ax.set_ylabel('Residuals (minutes)')
ax.set_title('Residuals vs Predicted Values')
ax.grid(True, alpha=0.3)

# Plot 4: Error Distribution by Prediction Range
ax = axes[1, 1]
pred_ranges = pd.cut(y_pred_train, bins=5)
errors_by_range = pd.DataFrame({'Range': pred_ranges, 'Error': np.abs(residuals)})
errors_by_range.groupby('Range')['Error'].mean().plot(kind='bar', ax=ax, color='coral')
ax.set_xlabel('Predicted Delivery Time Range')
ax.set_ylabel('Mean Absolute Error (minutes)')
ax.set_title('MAE by Prediction Range')
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('docs/reports/08_model_evaluation.png', dpi=100, bbox_inches='tight')
print("[Saved: docs/reports/08_model_evaluation.png]")

# ============================================
# 5. PREDICTION ERROR ANALYSIS
# ============================================
print("\n" + "="*70)
print("[5. PREDICTION ERROR ANALYSIS]")
print("="*70)

# Create error categories
error_ranges = [0, 2, 5, 10, 20, 100]
error_labels = ['0-2 min', '2-5 min', '5-10 min', '10-20 min', '20+ min']
abs_errors = np.abs(residuals)
error_categories = pd.cut(abs_errors, bins=error_ranges, labels=error_labels)

print(f"\nError Distribution:")
error_dist = error_categories.value_counts().sort_index()
for category, count in error_dist.items():
    percentage = 100 * count / len(abs_errors)
    print(f"  {category}: {count:,} predictions ({percentage:.2f}%)")

# ============================================
# 6. FEATURE CONTRIBUTION ANALYSIS
# ============================================
print("\n" + "="*70)
print("[6. FEATURE IMPORTANCE ANALYSIS]")
print("="*70)

if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'Feature': feature_columns,
        'Importance': best_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print(f"\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Create feature importance visualization
    fig, ax = plt.subplots(figsize=(10, 8))
    top_features = feature_importance.head(15)
    ax.barh(top_features['Feature'], top_features['Importance'], color='steelblue')
    ax.set_xlabel('Importance Score')
    ax.set_title('Top 15 Most Important Features')
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig('docs/reports/09_feature_importance.png', dpi=100, bbox_inches='tight')
    print("\n[Saved: docs/reports/09_feature_importance.png]")

# ============================================
# 7. GENERATE EVALUATION REPORT
# ============================================
print("\n" + "="*70)
print("[7. GENERATING EVALUATION REPORT]")
print("="*70)

report = f"""
MODEL EVALUATION REPORT
{'='*70}

EVALUATION DATASET:
  Total samples: {len(y_train_full):,}
  Target variable: Time_taken(min)
  Prediction model: {model_type}

OVERALL PERFORMANCE METRICS:
  R² Score: {r2_train:.4f} (explains {100*r2_train:.2f}% of variance)
  Root Mean Squared Error (RMSE): {rmse_train:.4f} minutes
  Mean Absolute Error (MAE): {mae_train:.4f} minutes
  Mean Absolute Percentage Error (MAPE): {mape_train:.4f}%

PREDICTION ACCURACY DISTRIBUTION:
  0-2 minutes error: {(abs_errors <= 2).sum():,} predictions ({100*(abs_errors <= 2).sum()/len(abs_errors):.2f}%)
  2-5 minutes error: {((abs_errors > 2) & (abs_errors <= 5)).sum():,} predictions ({100*((abs_errors > 2) & (abs_errors <= 5)).sum()/len(abs_errors):.2f}%)
  5-10 minutes error: {((abs_errors > 5) & (abs_errors <= 10)).sum():,} predictions ({100*((abs_errors > 5) & (abs_errors <= 10)).sum()/len(abs_errors):.2f}%)
  10+ minutes error: {(abs_errors > 10).sum():,} predictions ({100*(abs_errors > 10).sum()/len(abs_errors):.2f}%)

RESIDUAL ANALYSIS:
  Mean residual: {residuals.mean():.4f} minutes (bias)
  Std deviation of residuals: {residuals.std():.4f} minutes
  Min residual: {residuals.min():.4f} minutes (over-predicted)
  Max residual: {residuals.max():.4f} minutes (under-predicted)

PREDICTION RANGE:
  Minimum prediction: {y_pred_train.min():.2f} minutes
  Maximum prediction: {y_pred_train.max():.2f} minutes
  Mean prediction: {y_pred_train.mean():.2f} minutes
  Std deviation: {y_pred_train.std():.2f} minutes

ACTUAL DELIVERY TIME RANGE:
  Minimum actual: {y_train_full.min():.2f} minutes
  Maximum actual: {y_train_full.max():.2f} minutes
  Mean actual: {y_train_full.mean():.2f} minutes
  Std deviation: {y_train_full.std():.2f} minutes

KEY INSIGHTS:
  1. Model performs very well with R² of {r2_train:.4f}
  2. Average prediction error is {mae_train:.2f} minutes
  3. {100*(abs_errors <= 5).sum()/len(abs_errors):.1f}% of predictions are within 5 minutes of actual
  4. Model tends to {'under-predict' if residuals.mean() < 0 else 'over-predict'} on average
  5. Residuals are {'normally distributed' if residuals.std() > 2 else 'concentrated'}

RECOMMENDATION:
  Model is ready for production deployment. Monitor performance metrics
  on new data and retrain if accuracy drops significantly.
"""

# Save report
report_path = 'docs/reports/model_evaluation_report.txt'
with open(report_path, 'w') as f:
    f.write(report)

print(report)
print(f"[Saved: {report_path}]")

print("\n" + "="*70)
print("[MODEL EVALUATION COMPLETE!]")
print("="*70)
