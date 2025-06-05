# moviepredictorv2
*For a full write-up on the project please check out notebooks/moviepredictor2.html*

Model that predicts your rating of unseen movies based on Letterboxd data

Before running main.py:
1. Export your Letterboxd user data from https://letterboxd.com/settings/data/
2. Replace 'watched.csv' and 'watchlist.csv' in the /data subfolder with your own 'watched.csv' and 'watchlist.csv' [These are samples]
3. Run rater.py (you will need to re-rate all of your watched films - Letterboxd does not export your ratings)

Once main.py is ran you can see your predicted ratings of films on your watchlist in the 'results' folder.
