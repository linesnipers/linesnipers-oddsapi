import os
import requests
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Odds API config
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
                    line_raw = outcome.get("point")
                    book = bookmaker.get("title")

                    # Validate & sanitize line
                    try:
                        line = float(line_raw)
                    except (TypeError, ValueError):
                        print(f"⚠️ Skipping invalid line: {line_raw}")
                        continue

                    if not team or not market_key or not book:
                        print(f"⛔ Missing required fields. Skipping.")
                        continue

                    data.append({
                        "id": str(uuid.uuid4()),
                        "team": team,
                        "market": market_key,
                        "line": line,
                        "book": book,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

    if data:
        try:
            supabase.table("props").insert(data).execute()
            print(f"✅ Inserted {len(data)} props into Supabase.")
        except Exception as e:
            print(f"❌ Supabase insert failed: {e}")
    else:
        print("⚠️ No valid data to insert.")

if __name__ == "__main__":
    fetch_and_store_odds()
