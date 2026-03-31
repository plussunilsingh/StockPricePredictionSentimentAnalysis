#!/usr/bin/env python3
"""
Simple model generator for development.
Creates a toy regression model and saves to models/stock_model.pkl
"""
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import make_regression
import joblib

os.makedirs("models", exist_ok=True)
X, y = make_regression(n_samples=300, n_features=10, noise=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=50, random_state=42)
model.fit(X, y)
joblib.dump(model, "models/stock_model.pkl")
print("Saved model to models/stock_model.pkl")
