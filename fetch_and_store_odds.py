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

# Define the API endpoint
url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"

# Parameters for the API request
params = {
    "apiKey": ODDS_API_KEY,
    "regions": "us",
    "markets": "h2h,spreads,totals",
    "oddsFormat": "decimal"
}

# Make the request to TheOddsAPI
response = requests.get(url, params=params)
response.raise_for_status()
odds_json = response.json()

# Prepare data for Supabase
data = []

for game in odds_json:
    for bookmaker in game.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                line = outcome.get("point")

                # Strict filtering: Skip if line is missing, empty, or invalid
                if not line:
                    continue
                try:
                    line = float(line)
                except (ValueError, TypeError):
                    continue

                # Append valid entry
                data.append({
                    "team": outcome.get("name"),
                    "market": market.get("key"),
                    "line": line,
                    "book": bookmaker.get("title"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

# Insert into Supabase
if data:
    supabase.table("props").insert(data).execute()
    print(f"✅ Successfully inserted {len(data)} rows.")
else:
    print("⚠️ No valid props to insert.")
