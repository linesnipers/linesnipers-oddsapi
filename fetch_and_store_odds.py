import os
import requests
from supabase import create_client, Client

# Load Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load TheOddsAPI credentials
THEODDS_API_KEY = os.getenv("THEODDS_API_KEY")
SPORT = "baseball_mlb"
REGION = "us"
MARKET = "h2h"  # change to match what you're allowed to access on free tier

# TheOddsAPI endpoint (free tier sports odds, no props)
url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"

params = {
    "apiKey": THEODDS_API_KEY,
    "regions": REGION,
    "markets": MARKET,
    "oddsFormat": "decimal"
}

def fetch_and_store_odds():
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print("Failed to fetch from API:", response.text)
        return
    
    games = response.json()
    data_to_insert = []

    for game in games:
        teams = game.get("teams", [])
        bookmakers = game.get("bookmakers", [])

        for bookmaker in bookmakers:
            sportsbook = bookmaker.get("title")
            markets = bookmaker.get("markets", [])

            for market in markets:
                outcomes = market.get("outcomes", [])

                for outcome in outcomes:
                    player_name = outcome.get("name")  # using team name as placeholder
                    line = outcome.get("price")

                    if player_name and line is not None:
                        data_to_insert.append({
                            "player_name": player_name,
                            "prop_type": "Win",  # basic placeholder
                            "line": line,
                            "sportsbook": sportsbook
                        })

    if data_to_insert:
        print(f"Inserting {len(data_to_insert)} rows into Supabase...")
        supabase.table("props").insert(data_to_insert).execute()
    else:
        print("No data to insert.")

if __name__ == "__main__":
   
    fetch_and_store_odds()
    # Triggering GitHub Action manually
