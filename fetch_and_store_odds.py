import os
import requests
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
import math

# Load .env vars
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        print(f"❌ JSON parse failed: {e}")
        return

    data = []

    for game in odds_json:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    team = outcome.get("name")
                    market_key = market.get("key")
                    book = bookmaker.get("title")
                    line_raw = outcome.get("point")

                    # ✅ Strict validation: skip if invalid line
                    if (
                        line_raw is None or
                        isinstance(line_raw, str) and line_raw.strip().lower() in ["", "null", "none"] or
                        (isinstance(line_raw, float) and math.isnan(line_raw))
                    ):
                        print(f"⚠️ Skipping invalid 'line': {line_raw}")
                        continue

                    try:
                        line = float(line_raw)
                    except Exception as e:
                        print(f"⚠️ Skipping uncastable line '{line_raw}': {e}")
                        continue

                    # Ensure all required fields are present
                    if not all([team, market_key, book]):
                        print(f"⚠️ Missing required fields, skipping row.")
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
            print(f"✅ Inserted {len(data)} rows successfully.")
        except Exception as e:
            print(f"❌ Supabase insert failed: {e}")
    else:
        print("⚠️ No valid props to insert.")

if __name__ == "__main__":
    fetch_and_store_odds()
