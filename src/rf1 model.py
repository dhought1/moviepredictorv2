# -*- coding: utf-8 -*-
"""
Created on Thu May 29 19:59:03 2025

Random Forest Model v1.0 (No themes, Non bucketed years, Genres, No director embeds)

@author: DH
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib



# Import scraped data
df = pd.read_csv("data/watched_cleaned.csv")

# Removes features we don't need (some of which will be incorporated in later versions)
dropped_features = ['Date', 'Name', 'Letterboxd URI', 'Director', 'Genres', 'Themes']
df = df.drop(columns=dropped_features)

# Predicting myRating variable, everything else is features
target = 'myRating'
features = [col for col in df.columns if col != target]

X = df[features]
y = df[target]

# split train/test (research variables)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state = 42)

# train the random forest
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)


model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred, squared = False)


print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# Save to models folder
joblib.dump(model, "models/rf_v1.pkl")
joblib.dump(features, "models/rf_v1_feats.pkl")
print("Model and features saved")


