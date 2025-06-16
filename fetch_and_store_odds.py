import os
import requests
from supabase import create_client

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define TheOddsAPI endpoint (free tier supports game odds)
url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
params = {
    "apiKey": ODDS_API_KEY,
    "regions": "us",
    "markets": "h2h,spreads,totals",
    "oddsFormat": "american"
}

# Fetch data from API
response = requests.get(url, params=params)
if response.status_code != 200:
    raise Exception(f"API error {response.status_code}: {response.text}")

games = response.json()

# Parse and insert into Supabase
for game in games:
    home_team = game.get("home_team")
    away_team = game.get("away_team")
    for bookmaker in game.get("bookmakers", []):
        sportsbook = bookmaker["title"]
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                data = {
                    "player_name": outcome.get("name"),  # using team name in free tier
                    "prop_type": market.get("key"),
                    "line": outcome.get("point"),
                    "sportsbook": sportsbook
                }
                # Insert to Supabase
                supabase.table("props").insert(data).execute()

# 🔁 Manual trigger for GitHub Action workflow
