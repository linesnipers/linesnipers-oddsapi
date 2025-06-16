import os
import requests
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# API parameters
SPORT = "baseball_mlb"
REGION = "us"
MARKET = "h2h,spreads,totals"
ODDS_API_URL = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?regions={REGION}&markets={MARKET}&apiKey={ODDS_API_KEY}"

def fetch_and_store_odds():
    response = requests.get(ODDS_API_URL)
    if response.status_code != 200:
        print("Error fetching odds:", response.status_code, response.text)
        return

    games = response.json()

    for game in games:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    data = {
                        "player_name": outcome.get("name"),
                        "team": game.get("home_team"),
                        "opponent": game.get("away_team"),
                        "prop_type": market.get("key"),
                        "line": outcome.get("point"),
                        "odds": outcome.get("price"),
                        "sportsbook": bookmaker.get("title"),
                    }
                    supabase.table("props").insert(data).execute()

if __name__ == "__main__":
    fetch_and_store_odds()
