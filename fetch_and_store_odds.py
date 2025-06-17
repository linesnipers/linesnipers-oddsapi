import os
import requests
from datetime import datetime, timezone
from supabase import create_client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
THEODDSAPI_KEY = os.getenv("THEODDSAPI_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_and_store_odds():
    url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?regions=us&markets=h2h,spreads&apiKey={THEODDSAPI_KEY}"
    response = requests.get(url)
    odds_data = response.json()

    # Filter and prepare data
    data = []
    for game in odds_data:
        for bookmaker in game.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    line = outcome.get("point")
                    
                    # Only include props with a valid line
                    if line is None:
                        continue
                    try:
                        float(line)  # make sure it's numeric
                    except ValueError:
                        continue

                    data.append({
                        "team": outcome.get("name"),
                        "market": market.get("key"),
                        "line": float(line),
                        "book": bookmaker.get("title"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

    # Store to Supabase
    if data:
        supabase.table("props").insert(data).execute()
        print(f"✅ Inserted {len(data)} valid props into Supabase.")
    else:
        print("⚠️ No valid props to insert.")

if __name__ == "__main__":
    fetch_and_store_odds()
