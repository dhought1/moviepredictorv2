# -*- coding: utf-8 -*-
"""
Created on Thu May 29 16:17:46 2025

Scraping functions

@author: DH
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import json
import os
import numpy as np
import sys




#------------Individual Functions


# Scrapes 'Directors'
def get_director(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        director_tag = soup.find("a", class_="contributor")
        if director_tag:
            return director_tag.text.strip()
        return "Not found"
    except Exception as e:
        return f"Error: {e}"

# Scrapes 'Runtime'
def get_runtime(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        p_tags = soup.find_all("p")
        for tag in p_tags:
            text = tag.get_text(strip=True)
            if "mins" in text:
                match = re.search(r"(\d+)\s*mins", text)
                if match:
                    return int(match.group(1))
        return "Not found"
    except Exception as e:
        return f"Error: {e}"

# Scrapes Letterboxd Rating
def get_rating(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        json_ld_tag = soup.find("script", type="application/ld+json")
        if json_ld_tag:
            json_text = json_ld_tag.string.strip().strip("/* <![CDATA[ */").strip("/* ]]> */")
            data = json.loads(json_text)
            rating = data.get("aggregateRating", {}).get("ratingValue")
            return float(rating) if rating else "Not found"
        return "Not found"
    except Exception as e:
        return f"Error: {e}"

# Scrapes Genres
def get_genres(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        json_ld_tag = soup.find("script", type="application/ld+json")
        if json_ld_tag:
            raw_text = json_ld_tag.string.strip()
            cleaned = raw_text.strip("/* <![CDATA[ */").strip("/* ]]> */").strip()
            data = json.loads(cleaned)
            genres = data.get("genre")
            if isinstance(genres, list):
                return ", ".join(genres)
            elif isinstance(genres, str):
                return genres
        return "Not found"
    except Exception as e:
        return f"Error: {e}"

# Scrapes Themes
# Note: These aren't used anymore in the current model but they're good to have in case you want them I guess
def get_themes(url):
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        theme_links = soup.select('p a.text-slug[href*="/films/theme/"], p a.text-slug[href*="/films/mini-theme/"]')
        themes = [a.text.strip() for a in theme_links if "Show All" not in a.text]
        return ", ".join(themes) if themes else "Not found"
    except Exception as e:
        return f"Error: {e}"


# Actual Scraper, uses the above functions
def scrape_df(df, output_name):
    start_time = time.time()
    
    directors = []
    runtimes = []
    ratings = []
    genres = []
    themes = []

    for i, url in enumerate(df["Letterboxd URI"]):
        print(f"[{i+1}/{len(df)}] Scraping: {url}")
    
        directors.append(get_director(url))
        runtimes.append(get_runtime(url))
        ratings.append(get_rating(url))
        genres.append(get_genres(url))
        themes.append(get_themes(url))
        time.sleep(random.uniform(8, 15))  # Be polite
    
        elapsed = time.time() - start_time
        avg_per_entry = elapsed / (i + 1)
        remaining = avg_per_entry * (len(df) - (i+1))
        eta_min = int(remaining // 60)
        eta_sec = int(remaining % 60)
    
        print(f" Estimated time remaining: {eta_min} min {eta_sec} sec")
        
    #Add the scraped data to the df   
    df["Director"] = directors
    df["Runtime"] = runtimes
    df["Rating"] = ratings
    df["Genres"] = genres
    df["Themes"] = themes
    #Save it
    df.to_csv(f"data/{output_name}_scraped.csv", index=False)
    print(f" Saved to data/{output_name}_scraped.csv")


#-------------------------------------
# After the first run, a majority of the entries are going to have 429 errors because of timeouts 
# so you need to basically keep retrying until they can all populate with the correct info

def retry(df, output_name):
    start_time = time.time()

    for i, row in df.iterrows():
        url = row["Letterboxd URI"]
        needs_director = pd.isna(row["Director"]) or str(row["Director"]).startswith("Error")
        needs_runtime = pd.isna(row["Runtime"]) or str(row["Runtime"]).startswith("Error")
        needs_genres = pd.isna(row["Genres"]) or str(row["Genres"]).startswith("Error")
        needs_themes = pd.isna(row["Themes"]) or str(row["Themes"]).startswith("Error")
        needs_rating = pd.isna(row["Rating"]) or str(row["Rating"]).startswith("Error")
        
        if any([needs_director, needs_runtime, needs_genres, needs_themes, needs_rating]):
            print(f"\n[Retrying {i+1}] {url}")

            if needs_director:
                df.at[i, "Director"] = get_director(url)
            if needs_runtime:
                df.at[i, "Runtime"] = get_runtime(url)
            if needs_genres:
                df.at[i, "Genres"] = get_genres(url)
            if needs_themes:
                df.at[i, "Themes"] = get_themes(url)
            if needs_rating:
                df.at[i, "Rating"] = get_rating(url)

            # Pause to avoid bot detection
            time.sleep(random.uniform(15, 25))

            # ETA estimate
            elapsed = time.time() - start_time
            completed = i + 1
            remaining_rows = sum(
                pd.isna(df["Director"]) | df["Director"].astype(str).str.startswith("Error") |
                pd.isna(df["Runtime"]) | df["Runtime"].astype(str).str.startswith("Error") |
                pd.isna(df["Genres"]) | df["Genres"].astype(str).str.startswith("Error") |
                pd.isna(df["Themes"]) | df["Themes"].astype(str).str.startswith("Error")
                )
            avg_time_per = elapsed / completed
            remaining_time = avg_time_per * remaining_rows
            eta_min = int(remaining_time // 60)
            eta_sec = int(remaining_time % 60)

            print(f" Estimated time remaining: {eta_min} min {eta_sec} sec")


    df.to_csv(f"data/{output_name}_scraped.csv", index=False)
    print(f" Saved to data/{output_name}_scraped.csv")


# helper function so that the retry can automatically loop later instead of having to manually do it after each time 
def needs_retry(df):
    return any(
        pd.isna(df["Director"]) | df["Director"].astype(str).str.startswith("Error") |
        pd.isna(df["Runtime"]) | df["Runtime"].astype(str).str.startswith("Error") |
        pd.isna(df["Genres"]) | df["Genres"].astype(str).str.startswith("Error") |
        pd.isna(df["Themes"]) | df["Themes"].astype(str).str.startswith("Error") |
        pd.isna(df["Rating"]) | df["Rating"].astype(str).str.startswith("Error")
        
    )



#-------------------FUNCTIONS FOR UPDATING THE WATCHED/WATCHLIST SO IT DOESN'T SCRAPE FOR HOURS
# This one checks if _scraped suffixes already exist. If they do then you don't need to scrape everything
# again from scratch
# probably rename both of these at some point these are kind of ambiguous in retrospect
def checker(df, name):
    scraped_path = f"data/{name}_scraped.csv"
    if os.path.exists(scraped_path):
        print('Scraped File Exists')
        updater(df, name)
    else:
        print('No Previously Scraped Data')
        scrape_df(df, name)
    
    
# these should update the _scraped csvs with raw data from the updated 'watched' then retry will scrape it after
# basically just checks if there are any titles in watched.csv that dont already appear in watched_scraped so it
# can tell what to update
def updater(df, name):
    scraped_path = f"data/{name}_scraped.csv"
    existing = pd.read_csv(scraped_path)
    
    if name == 'watched':
        needs_scraped = pd.read_csv("data/watched_rated.csv")
    elif name == 'watchlist':
        needs_scraped = pd.read_csv("data/watchlist.csv")
    else:
        print('input variable should be watched or watchlist')
    
    new_entries = needs_scraped[~needs_scraped["Name"].isin(existing["Name"])]
    print(f" Found {len(new_entries)} new entries to scrape for '{name}'.")
    
    if not new_entries.empty:
        for col in ["Director", "Runtime", "Rating", "Genres", "Themes"]:
            new_entries[col] = np.nan

        combined = pd.concat([existing, new_entries], ignore_index=True)
        combined.drop_duplicates(subset="Name", inplace=True)
        combined.to_csv(scraped_path, index=False)
        print(f" {name}_scraped.csv updated with new entries.")
    else:
        print(f" No new movies to append for '{name}'.")
        
#-----------------
# MAKING SURE THAT THE USER IS USING RATED DATA AND NOT RAW WATCHED DATA
def rate_checker():
   rated_path = "data/watched_rated.csv"
   if os.path.exists(rated_path):
       print('All movies rated, proceeding to Scraping')
   else:
       print('You need to rate movies first. Please run rater.py before proceeding')
       sys.exit()

    
    