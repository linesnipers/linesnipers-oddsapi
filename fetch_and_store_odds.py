import os
import requests
from datetime import datetime, timezone
from supabase import create_client

# Load environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ODDS_API_KEY = os.environ.get("ODDS_API_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define TheOddsAPI endpoint
url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"

# API request parameters
params = {
    "apiKey": ODDS_API_KEY,
    "regions": "us",
    "markets": "h2h,spreads,totals",
    "oddsFormat": "decimal"
}

# Request data
response = requests.get(url, params=params)
response.raise_for_status()
odds_json = response.json()

# Build data
data = []
for game in odds_json:
    for bookmaker in game.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                line = outcome.get("point")

                # FINAL strict filter: skip null, empty, non-number, or missing
                if line is None:
                    continue
                try:
                    line = float(line)
                except Exception:
                    continue

                data.append({
                    "team": outcome.get("name"),
                    "market": market.get("key"),
                    "line": line,
                    "book": bookmaker.get("title"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

# Insert only if data is clean
if data:
    try:
        supabase.table("props").insert(data).execute()
        print(f"✅ Inserted {len(data)} rows successfully.")
    except Exception as e:
        print(f"❌ Insert failed: {e}")
else:
    print("⚠️ No valid props to insert.")
