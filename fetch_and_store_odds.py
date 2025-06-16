import requests
from supabase import create_client, Client
import os

# Environment variables (injected by GitHub Actions)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch odds data
response = requests.get(
    "https://api.the-odds-api.com/v4/sports/upcoming/odds",
    params={
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }
)

# Ensure request succeeded
if response.status_code != 200:
    raise Exception(f"Failed to fetch odds: {response.status_code} - {response.text}")

data = response.json()
rows_to_insert = []

# Parse and filter valid rows
for game in data:
    home_team = game.get("home_team")
    away_team = game.get("away_team")
    commence_time = game.get("commence_time")
    for bookmaker in game.get("bookmakers", []):
        sportsbook = bookmaker.get("title")
        for market in bookmaker.get("markets", []):
            prop_type = market.get("key")
            for outcome in market.get("outcomes", []):
                player_name = outcome.get("name")
                line = outcome.get("point")

                # Skip any entry missing required fields
                if None in [player_name, prop_type, line, sportsbook]:
                    continue

                rows_to_insert.append({
                    "player_name": player_name,
                    "prop_type": prop_type,
                    "line": line,
                    "sportsbook": sportsbook
                })

# Insert to Supabase
if rows_to_insert:
    supabase.table("props").insert(rows_to_insert).execute()
else:
    print("No valid props to insert.")
