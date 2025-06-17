import os
import requests
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Odds API
API_KEY = os.getenv("ODDS_API_KEY")
SPORT = "americanfootball_nfl"
REGION = "us"
MARKETS = "h2h,spreads,totals"

def fetch_and_store_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGION,
        "markets": MARKETS
    }

    response = requests.get(url, params=params)
    try:
        odds_json = response.json()
    except Exception as e:
        print(f"❌ Failed to parse JSON: {e}")
        return

    data = []

    for game in odds_json:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    team = outcome.get("name")
                    market_key = market.get("key")
                    line = outcome.get("point")
                    book = bookmaker.get("title")

                    # Debug: Print what we got
                    print(f"➡️ team: {team}, market: {market_key}, line: {line}, book: {book}")

                    # FINAL strict null check
                    if not team or not market_key or not book:
                        print("⛔ Missing required text field — skipping.")
                        continue
                    if line is None or not isinstance(line, (int, float)):
                        print("⛔ Line is missing or invalid — skipping.")
                        continue

                    data.append({
                        "id": str(uuid.uuid4()),
                        "team": team,
                        "market": market_key,
                        "line": float(line),
                        "book": book,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

    if data:
        try:
            supabase.table("props").insert(data).execute()
            print(f"✅ Inserted {len(data)} props into Supabase.")
        except Exception as e:
            print(f"❌ Failed inserting into Supabase: {e}")
    else:
        print("⚠️ No valid data to insert.")

if __name__ == "__main__":
    fetch_and_store_odds()
