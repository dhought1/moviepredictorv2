# -*- coding: utf-8 -*-
"""
Created on Thu May 29 17:15:06 2025

Main

@author: DH
"""

from src.scraper import rate_checker, retry, needs_retry, checker
from src.clean import onehot_genres
from src.predictor_rf1 import predictor
import pandas as pd



''' NOTE: YOU WILL NEED TO RUN 'RATER' SEPERATELY BEFORE PROCEEDING
    LETTERBOXD DOES NOT EXPORT YOUR PERSONAL RATINGS SO THIS IS A 
    PRE-REQUISITE'''

# LOAD WATCHED AND WATCHLIST
watched = pd.read_csv("data/watched_rated.csv")  
watchlist = pd.read_csv("data/watchlist.csv")

# CHECK IF ALL MOVIES IN 'WATCHED' HAVE BEEN RATED (required) BEFORE RUNNING THE REST
rate_checker()

#-----------------------------------------------------------------------------
# CHECKS IF SCRAPED DATA ALREADY EXISTS AND THEN SCRAPES WHATEVER IS LEFT
# the second variable should match the df name, it's just for naming conventions when
# saving csvs later on

checker(watched, 'watched')
checker(watchlist, 'watchlist')


watched = pd.read_csv("data/watched_scraped.csv")
watchlist = pd.read_csv("data/watchlist_scraped.csv")

# RETRYS UNTIL THERE ARE NO MORE TIMEOUT ERRORS 
while needs_retry(watched):
    retry(watched, 'watched')
    
print('No more emptys in Watched')
    
while needs_retry(watchlist):
    retry(watchlist, 'watchlist')

print('No more emptys in Watchlist')

# After the df is scraped, the scraped versions become the working dfs instead
watched = pd.read_csv("data/watched_scraped.csv")  
watchlist = pd.read_csv("data/watchlist_scraped.csv")

#-----------------------------------------------------------------------------
# CLEANING

# One hot encodes the genres
onehot_genres(watched, 'watched')
onehot_genres(watchlist, 'watchlist')

## any future cleaning functions should be called here (themes, for example)
#

# working df is now cleaned data instead
watched = pd.read_csv("data/watched_cleaned.csv")  
watchlist = pd.read_csv("data/watchlist_cleaned.csv")

#------------------------------------------------------------------------------
# PREDICTIONS
# Creates list of predicted userRating for films in your watchlist
predictor()

print('Your Predictions have been generated! Navigate to the results folder')