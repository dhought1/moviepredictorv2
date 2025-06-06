# -*- coding: utf-8 -*-
"""
Created on Thu May 29 18:40:25 2025

Letterboxd doesnt give you your own ratings when you export the data so you have to do it 
yourself unfortunately. You don't need to do this for watchlist since that's what youre
predicting on.

@author: DH
"""

import pandas as pd
import tkinter as tk
import os
import sys

# Files

INPUT_FILE = "data/watched.csv"
OUTPUT_FILE = "data/watched_rated.csv"





# Load latest watched data
df_new = pd.read_csv(INPUT_FILE)

# Identify the title + year column names
TITLE_COL = "Name"     
YEAR_COL = "Year"

# Load existing ratings if available
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    # Get already-rated keys
    rated_keys = set(zip(df_existing[TITLE_COL], df_existing[YEAR_COL]))
else:
    df_existing = pd.DataFrame()
    rated_keys = set()

# Filter new movies that aren't already rated
df_to_rate = df_new[~df_new.set_index([TITLE_COL, YEAR_COL]).index.isin(rated_keys)].reset_index(drop=True)

# Skip if nothing to rate
if df_to_rate.empty:
    print("All movies are already rated")
    sys.exit()


# GUI setup
index = 0
ratings = []
to_delete = set()

root = tk.Tk()
root.title("Rate Your New Movies")
root.geometry("400x300")

# Progress label (this is where it goes)
progress_label = tk.Label(root, text="", font=("Arial", 12))
progress_label.pack()

# Title label
title_label = tk.Label(root, text="", wraplength=350, font=("Arial", 14), justify="center")
title_label.pack(pady=20)


button_frame = tk.Frame(root)
button_frame.pack(pady=10)

def rate_movie(rating):
    global index
    ratings.append(rating)
    index += 1
    show_next_movie()

def delete_movie():
    global index
    ratings.append(None)
    to_delete.add(index)
    index += 1
    show_next_movie()

def show_next_movie():
    if index >= len(df_to_rate):
        root.destroy()
        finish()
        return
    row = df_to_rate.iloc[index]
    title = row[TITLE_COL]
    year = row[YEAR_COL]
    title_label.config(text=f"Rate this movie:\n\n{title} ({year})")
    progress_label.config(text=f"Movie {index + 1} of {len(df_to_rate)}")


# Rating buttons
for i in range(1, 11):
    val = i * 0.5
    btn = tk.Button(button_frame, text=f"{val} ★", command=lambda r=val: rate_movie(r), width=6)
    btn.grid(row=(i-1)//5, column=(i-1)%5, padx=5, pady=5)

delete_btn = tk.Button(root, text="Delete Movie", command=delete_movie, bg="red", fg="white")
delete_btn.pack(pady=10)

def finish():
    cleaned_df = df_to_rate.drop(index=to_delete).reset_index(drop=True)
    cleaned_df["myRating"] = [r for i, r in enumerate(ratings) if i not in to_delete]
    
    if df_existing.empty:
        combined = cleaned_df
    else:
        combined = pd.concat([df_existing, cleaned_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=[TITLE_COL, YEAR_COL], keep="last")

    combined.to_csv(OUTPUT_FILE, index=False)
    print(f" Updated and saved to {OUTPUT_FILE} with {len(combined)} total rated films.")

# Start GUI
show_next_movie()
root.mainloop()
