# -*- coding: utf-8 -*-
"""
Created on Fri May 30 12:10:36 2025

Predictor (RF v1)

@author: DH
"""

import joblib
import pandas as pd
import numpy as np


def predictor():
    watchlist = pd.read_csv('data/watchlist_cleaned.csv')

    model = joblib.load("models/rf_v1.pkl")
    features = joblib.load("models/rf_v1_feats.pkl")

    # Movies that aren't yet released have 'Not found' data that needs to be removed
    watchlist.replace("Not found", np.nan, inplace=True)


                        
    X_watchlist = watchlist[features]

    watchlist["predictedRating"] = model.predict(X_watchlist)

    # Organize the output so it's cleaner to look at
    cols = ['Name', 'Year', 'Director', 'Runtime', 'Rating',
        'predictedRating']

    watchlist = watchlist[cols]
    watchlist = watchlist.sort_values(by="predictedRating", ascending=False)
    watchlist["predictedRating"] = watchlist["predictedRating"].round(2)



    watchlist.to_csv("results/watchlist_predicted.csv", index=False)
    print("Predictions saved to results/watchlist_predicted.csv")