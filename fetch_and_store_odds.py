import requests
import os
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
THEODDSAPI_KEY = os.getenv("THEODDSAPI_KEY")

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define your API endpoint
url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds?apiKey={THEODDSAPI_KEY}&regions=us&markets=h2h,spreads,totals&oddsFormat=decimal"

# Fetch and filter data
def fetch_and_store_odds():
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to fetch odds:", response.status_code, response.text)
        return

    odds_data = response.json()
    data = []

    for game in odds_data:
        teams = game.get("teams", [])
        commence_time = game.get("commence_time")
        sites = game.get("bookmakers", [])

        for site in sites:
            bookmaker = site.get("title")
            for market in site.get("markets", []):
                market_type = market.get("key")
                for outcome in market.get("outcomes", []):
                    team = outcome.get("name")
                    line = outcome.get("point")

                    # Skip entries where line is None
                    if line is None:
                        continue

                    data.append({
                        "team": team,
                        "market": market_type,
                        "line": line,
                        "book": bookmaker,
                        "game_time": commence_time or datetime.utcnow().isoformat()
                    })

    # Only insert if valid data exists
    if data:
        supabase.table("props").insert(data).execute()
        print(f"Inserted {len(data)} rows into Supabase.")
    else:
        print("No valid props found to insert.")

# Run it
if __name__ == "__main__":
    fetch_and_store_odds()
