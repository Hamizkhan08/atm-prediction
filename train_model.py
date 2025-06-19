# train_model.py (NEW REGRESSION VERSION)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np

# Load data
df = pd.read_csv('atm_data.csv')

# --- Feature Engineering ---
# Create Day_of_Week
df['Day_of_Week'] = pd.to_datetime(df['Date']).dt.day_name()

# Handle potential division by zero if Transactions is 0
df['Avg_Withdrawal_Per_Txn'] = (df['Cash_Dispensed'] / df['Transactions']).replace([np.inf, -np.inf], 0).fillna(0)

# One-hot encode the Day_of_Week
day_dummies = pd.get_dummies(df['Day_of_Week'], prefix='Day_of_Week')
all_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for day in all_days:
    col = f'Day_of_Week_{day}'
    if col not in day_dummies.columns:
        day_dummies[col] = 0
day_dummies = day_dummies[[f'Day_of_Week_{day}' for day in all_days]] # Ensure consistent order

df = pd.concat([df, day_dummies], axis=1)

# --- Define Features and Label for REGRESSION ---
# The model will learn to predict dispensed cash from transaction counts and the day.
# We do NOT include 'Cash_Loaded' here, as it doesn't help predict how much users will take.
feature_cols = ['Transactions'] + day_dummies.columns.tolist()
X = df[feature_cols]
y = df['Cash_Dispensed'] # The label is now a continuous number, not 0 or 1

# --- Train the Regression Model ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Use RandomForestRegressor
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- Save the new model and feature list ---
# It's a good idea to name it differently to avoid confusion, but we'll overwrite for simplicity.
joblib.dump((model, feature_cols), 'model.pkl')

print("REGRESSION model trained to predict 'Cash_Dispensed'.")
print(f"Features used for training: {feature_cols}")
print("Model saved as model.pkl")