import requests
import os
from supabase import create_client, Client

# Environment variables (set these in Railway or locally)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
THEODDS_API_KEY = os.environ.get("THEODDS_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# API endpoint with free-tier markets
url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=h2h,spreads,totals&oddsFormat=decimal&apiKey={THEODDS_API_KEY}"

def fetch_and_store_odds():
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch odds: {response.status_code} - {response.text}")
        return

    games = response.json()
    data_to_insert = []

    for game in games:
        home_team = game.get("home_team")
        away_team = game.get("away_team")

        for bookmaker in game.get("bookmakers", []):
            sportsbook = bookmaker.get("title")

            for market in bookmaker.get("markets", []):
                market_type = market.get("key")
                for outcome in market.get("outcomes", []):
                    data_to_insert.append({
                        "matchup": f"{away_team} @ {home_team}",
                        "market_type": market_type,
                        "team": outcome.get("name"),
                        "price": outcome.get("price"),
                        "sportsbook": sportsbook
                    })

    # Insert into Supabase (to a table named "odds" for example)
    if data_to_insert:
        supabase.table("odds").insert(data_to_insert).execute()
        print(f"Inserted {len(data_to_insert)} rows into Supabase.")
    else:
        print("No odds data found.")

if __name__ == "__main__":
    fetch_and_store_odds()