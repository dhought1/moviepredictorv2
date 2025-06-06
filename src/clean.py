# -*- coding: utf-8 -*-
"""
Created on Thu May 29 18:21:48 2025

Clean the data in preparation of testing

@author: DH
"""

import pandas as pd


# list of possible genres to make sure that all are accounted for in case there are some outside of my watched/watchlist
# for example if a new movie was added and I'd never seen a 'Mystery' it wouldn't work.
ALL_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
    "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance",
    "Science Fiction", "Thriller", "TV Movie", "War", "Western"
]


#------------------------------------------------------------------------------
# ONE HOT ENCODES THE GENRES
def onehot_genres(df, output_name):
    df_genres = df["Genres"].str.get_dummies(sep=", ")

    # Add missing genre columns if needed
    for genre in ALL_GENRES:
        if genre not in df_genres.columns:
            df_genres[genre] = 0

    # Reorder genre columns
    df_genres = df_genres[ALL_GENRES]

    # Combine everything
    df_final = pd.concat([df, df_genres], axis=1)

    # Save to csv
    df_final.to_csv(f"data/{output_name}_cleaned.csv", index=False)
    print(f" Saved to data/{output_name}_cleaned.csv")
    



    
