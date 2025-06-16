from supabase import create_client
import requests
import os

# Environment variables
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ODDS_API_KEY = os.environ["ODDS_API_KEY"]

# Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# API request
response = requests.get(
    "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds",
    params={"regions": "us", "apiKey": ODDS_API_KEY}
)
games = response.json()

rows_to_insert = []

for game in games:
    for bookmaker in game.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                if outcome.get("name") and outcome.get("price") is not None:
                    row = {
                        "player_name": outcome["name"],
                        "prop_type": market["key"],
                        "line": outcome["price"],
                        "sportsbook": bookmaker["title"]
                    }
                    # Avoid inserting rows missing line or prop_type
                    if row["line"] is not None and row["prop_type"]:
                        rows_to_insert.append(row)

# Insert into Supabase
if rows_to_insert:
    supabase.table("props").insert(rows_to_insert).execute()
