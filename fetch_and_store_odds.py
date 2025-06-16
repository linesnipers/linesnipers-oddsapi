import requests
from supabase import create_client, Client
import os

# ENV VARIABLES
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
THEODDS_API_KEY = os.environ.get("THEODDS_API_KEY")

# INIT SUPABASE
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# API URL
url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=player_props&oddsFormat=decimal&apiKey={THEODDS_API_KEY}"

def fetch_and_store_odds():
    response = requests.get(url)

    try:
        data = response.json()  # Safely parse JSON
    except ValueError:
        print("❌ Failed to decode JSON. Raw response:", response.text)
        return

    if not isinstance(data, list):
        print("❌ Unexpected data format from API.")
        return

    props_to_insert = []

    for game in data:
        for bookmaker in game.get("bookmakers", []):
            sportsbook = bookmaker.get("title")
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    prop = {
                        "player_name": outcome.get("name"),
                        "prop_type": market.get("key"),
                        "line": outcome.get("point"),
                        "sportsbook": sportsbook
                    }
                    # Only insert if all fields are filled
                    if all(prop.values()):
                        props_to_insert.append(prop)

    if props_to_insert:
        supabase.table("props").insert(props_to_insert).execute()
        print(f"✅ Inserted {len(props_to_insert)} props.")
    else:
        print("⚠️ No valid props to insert.")

if __name__ == "__main__":
    fetch_and_store_odds()