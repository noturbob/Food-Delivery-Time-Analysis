import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("GENERATING PREDICTIONS - DELIVERY TIME")
print("="*70)

# Load test data
test_data = pd.read_csv('data/cleaned data/test_clean.csv')
print(f"\nTest data loaded: {test_data.shape}")

# Load saved model and preprocessing objects
print("\n[Loading saved models and preprocessors...]")

with open('ml_models/saved_models/best_model.pkl', 'rb') as f:
    best_model = pickle.load(f)

with open('ml_models/saved_models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('ml_models/saved_models/label_encoders.pkl', 'rb') as f:
    label_encoders = pickle.load(f)

with open('ml_models/saved_models/feature_columns.pkl', 'rb') as f:
    feature_columns = pickle.load(f)

print(f"Model type: {type(best_model).__name__}")
print(f"Feature count: {len(feature_columns)}")
print(f"Features: {feature_columns}")

# ============================================
# 1. PREPARE TEST DATA
# ============================================
print("\n" + "="*70)
print("[1. PREPARING TEST DATA]")
print("="*70)

# Keep ID for later
test_ids = test_data['ID'].copy()

# Prepare features
X_test = test_data.drop(['ID'], axis=1)

# Handle categorical variables
categorical_cols = X_test.select_dtypes(include=['object']).columns.tolist()
X_test_encoded = X_test.copy()

print(f"\nEncoding categorical features:")
for col in categorical_cols:
    if col in label_encoders:
        try:
            X_test_encoded[col] = label_encoders[col].transform(X_test[col].astype(str))
            print(f"  {col}: Encoded successfully")
        except Exception as e:
            print(f"  {col}: Using default for unseen values")
            X_test_encoded[col] = 0

# Drop date and time features
cols_to_drop = ['Order_Date', 'Time_Orderd', 'Time_Order_picked', 'Festival', 'order_hour']
X_test_encoded = X_test_encoded.drop([col for col in cols_to_drop if col in X_test_encoded.columns], axis=1)

# Handle missing columns from training data
for col in feature_columns:
    if col not in X_test_encoded.columns:
        X_test_encoded[col] = 0  # Use default value for missing columns
        print(f"  Adding missing column: {col}")

# Handle NaN values
X_test_encoded = X_test_encoded.fillna(0)

# Ensure columns match training data and in correct order
X_test_encoded = X_test_encoded[feature_columns]

print(f"\nTest data prepared: {X_test_encoded.shape}")

# ============================================
# 2. MAKE PREDICTIONS
# ============================================
print("\n" + "="*70)
print("[2. MAKING PREDICTIONS]")
print("="*70)

# Check if model needs scaling
model_type = type(best_model).__name__
if 'Linear' in model_type:
    X_test_scaled = scaler.transform(X_test_encoded)
    predictions = best_model.predict(X_test_scaled)
else:
    predictions = best_model.predict(X_test_encoded)

print(f"\nPredictions generated: {len(predictions):,}")
print(f"Prediction statistics:")
print(f"  Min: {predictions.min():.2f} minutes")
print(f"  Max: {predictions.max():.2f} minutes")
print(f"  Mean: {predictions.mean():.2f} minutes")
print(f"  Median: {np.median(predictions):.2f} minutes")
print(f"  Std Dev: {predictions.std():.2f} minutes")

# ============================================
# 3. CREATE SUBMISSION FILE
# ============================================
print("\n" + "="*70)
print("[3. CREATING SUBMISSION FILE]")
print("="*70)

submission = pd.DataFrame({
    'ID': test_ids,
    'Time_taken_min': predictions
})

# Round predictions to 2 decimal places
submission['Time_taken_min'] = submission['Time_taken_min'].round(2)

# Save submission
submission_path = 'ml_models/predictions/submission.csv'
submission.to_csv(submission_path, index=False)
print(f"\n[Saved submission: {submission_path}]")
print(f"Submission shape: {submission.shape}")
print(f"\nSample predictions:")
print(submission.head(10).to_string(index=False))

# ============================================
# 4. GENERATE PREDICTION REPORT
# ============================================
print("\n" + "="*70)
print("[4. PREDICTION REPORT]")
print("="*70)

report = f"""
DELIVERY TIME PREDICTION REPORT
{'='*70}

DATASET INFO:
  Total predictions: {len(submission):,}
  Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

PREDICTION STATISTICS:
  Minimum delivery time: {submission['Time_taken_min'].min():.2f} minutes
  Maximum delivery time: {submission['Time_taken_min'].max():.2f} minutes
  Average delivery time: {submission['Time_taken_min'].mean():.2f} minutes
  Median delivery time: {submission['Time_taken_min'].median():.2f} minutes
  Standard deviation: {submission['Time_taken_min'].std():.2f} minutes

DELIVERY TIME CATEGORIES:
  Very Fast (10-15 min): {(submission['Time_taken_min'] <= 15).sum():,} deliveries ({100*(submission['Time_taken_min'] <= 15).sum()/len(submission):.2f}%)
  Fast (15-25 min): {((submission['Time_taken_min'] > 15) & (submission['Time_taken_min'] <= 25)).sum():,} deliveries ({100*((submission['Time_taken_min'] > 15) & (submission['Time_taken_min'] <= 25)).sum()/len(submission):.2f}%)
  Normal (25-35 min): {((submission['Time_taken_min'] > 25) & (submission['Time_taken_min'] <= 35)).sum():,} deliveries ({100*((submission['Time_taken_min'] > 25) & (submission['Time_taken_min'] <= 35)).sum()/len(submission):.2f}%)
  Slow (35+ min): {(submission['Time_taken_min'] > 35).sum():,} deliveries ({100*(submission['Time_taken_min'] > 35).sum()/len(submission):.2f}%)

MODEL INFO:
  Model type: {model_type}
  Total features: {len(feature_columns)}
  
SUBMISSION FILE:
  Location: ml_models/predictions/submission.csv
  Columns: ID, Time_taken_min
  Format: CSV

NEXT STEPS:
  1. Review predictions for anomalies
  2. Create Tableau dashboard for visualization
  3. Present findings to stakeholders
"""

# Save report
report_path = 'docs/reports/prediction_report.txt'
with open(report_path, 'w') as f:
    f.write(report)

print(report)
print(f"[Saved report: {report_path}]")

print("\n" + "="*70)
print("[PREDICTIONS COMPLETE!]")
print("="*70)
