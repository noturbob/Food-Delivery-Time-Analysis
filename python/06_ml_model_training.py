import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("ML MODEL TRAINING - DELIVERY TIME PREDICTION")
print("="*70)

# Load cleaned data
train_data = pd.read_csv('data/cleaned data/train_clean.csv')
test_data = pd.read_csv('data/cleaned data/test_clean.csv')

print(f"\nData Loaded:")
print(f"  Training: {train_data.shape}")
print(f"  Test: {test_data.shape}")

# ============================================
# 1. DATA PREPARATION
# ============================================
print("\n" + "="*70)
print("[1. DATA PREPARATION]")
print("="*70)

# Drop rows with missing target variable
train_data = train_data.dropna(subset=['Time_taken(min)']).reset_index(drop=True)
print(f"\nTraining data after removing missing targets: {len(train_data):,} rows")

# Separate features and target
X_train = train_data.drop(['Time_taken(min)', 'ID'], axis=1)
y_train = train_data['Time_taken(min)']

# Handle categorical variables
categorical_cols = X_train.select_dtypes(include=['object']).columns.tolist()
print(f"\nCategorical features to encode: {len(categorical_cols)}")

# Label encode categorical features
label_encoders = {}
X_train_encoded = X_train.copy()

for col in categorical_cols:
    le = LabelEncoder()
    X_train_encoded[col] = le.fit_transform(X_train[col].astype(str))
    label_encoders[col] = le
    print(f"  Encoded {col}: {len(le.classes_)} unique values")

# Drop date and time features that are already encoded or have all NaN values
cols_to_drop = ['Order_Date', 'Time_Orderd', 'Time_Order_picked', 'Festival', 'order_hour']
X_train_encoded = X_train_encoded.drop([col for col in cols_to_drop if col in X_train_encoded.columns], axis=1)

# Handle remaining NaN values by filling with median
X_train_encoded = X_train_encoded.fillna(X_train_encoded.median())

print(f"\nFinal feature count: {X_train_encoded.shape[1]}")
print(f"Features: {list(X_train_encoded.columns)}")

# Split into train and validation
X_tr, X_val, y_tr, y_val = train_test_split(X_train_encoded, y_train, test_size=0.2, random_state=42)
print(f"\nTrain/Validation split:")
print(f"  Training: {X_tr.shape[0]:,} samples")
print(f"  Validation: {X_val.shape[0]:,} samples")

# Scale features
scaler = StandardScaler()
X_tr_scaled = scaler.fit_transform(X_tr)
X_val_scaled = scaler.transform(X_val)

# ============================================
# 2. MODEL TRAINING
# ============================================
print("\n" + "="*70)
print("[2. MODEL TRAINING]")
print("="*70)

models = {
    'Linear Regression': LinearRegression(),
    'Random Forest': RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=50, learning_rate=0.1, max_depth=4, random_state=42)
}

results = {}

for model_name, model in models.items():
    print(f"\nTraining {model_name}...")
    
    # Train
    if model_name == 'Linear Regression':
        model.fit(X_tr_scaled, y_tr)
        y_val_pred = model.predict(X_val_scaled)
    else:
        model.fit(X_tr, y_tr)
        y_val_pred = model.predict(X_val)
    
    # Evaluate
    mse = mean_squared_error(y_val, y_val_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_val, y_val_pred)
    r2 = r2_score(y_val, y_val_pred)
    
    results[model_name] = {
        'model': model,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'mse': mse
    }
    
    print(f"  RMSE: {rmse:.4f} minutes")
    print(f"  MAE: {mae:.4f} minutes")
    print(f"  R² Score: {r2:.4f}")

# ============================================
# 3. MODEL COMPARISON
# ============================================
print("\n" + "="*70)
print("[3. MODEL COMPARISON]")
print("="*70)

results_df = pd.DataFrame({
    'Model': list(results.keys()),
    'RMSE': [results[m]['rmse'] for m in results.keys()],
    'MAE': [results[m]['mae'] for m in results.keys()],
    'R² Score': [results[m]['r2'] for m in results.keys()]
})

print("\n" + results_df.to_string(index=False))

# Select best model
best_model_name = results_df.loc[results_df['R² Score'].idxmax(), 'Model']
best_model = results[best_model_name]['model']

print(f"\n[BEST MODEL: {best_model_name}]")
print(f"  R² Score: {results[best_model_name]['r2']:.4f}")
print(f"  RMSE: {results[best_model_name]['rmse']:.4f} minutes")
print(f"  MAE: {results[best_model_name]['mae']:.4f} minutes")

# ============================================
# 4. FEATURE IMPORTANCE
# ============================================
print("\n" + "="*70)
print("[4. FEATURE IMPORTANCE]")
print("="*70)

if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'Feature': X_train_encoded.columns,
        'Importance': best_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print(f"\nTop 15 Most Important Features:")
    print(feature_importance.head(15).to_string(index=False))

# ============================================
# 5. SAVE MODELS
# ============================================
print("\n" + "="*70)
print("[5. SAVING MODELS]")
print("="*70)

# Save best model
model_path = 'ml_models/saved_models/best_model.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(best_model, f)
print(f"[Saved best model: {model_path}]")

# Save scaler
scaler_path = 'ml_models/saved_models/scaler.pkl'
with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)
print(f"[Saved scaler: {scaler_path}]")

# Save label encoders
encoders_path = 'ml_models/saved_models/label_encoders.pkl'
with open(encoders_path, 'wb') as f:
    pickle.dump(label_encoders, f)
print(f"[Saved label encoders: {encoders_path}]")

# Save feature columns
features_path = 'ml_models/saved_models/feature_columns.pkl'
with open(features_path, 'wb') as f:
    pickle.dump(X_train_encoded.columns.tolist(), f)
print(f"[Saved feature columns: {features_path}]")

# Save results
results_path = 'ml_models/saved_models/model_results.csv'
results_df.to_csv(results_path, index=False)
print(f"[Saved model results: {results_path}]")

print("\n" + "="*70)
print("[MODEL TRAINING COMPLETE!]")
print("="*70)
