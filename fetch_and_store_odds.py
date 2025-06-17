import os
import uuid
import requests
from datetime import datetime
from supabase import create_client, Client

# Load secrets from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_and_store_odds():
    url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?regions=us&markets=h2h,spreads,totals&apiKey={ODDS_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Failed to fetch odds:", response.status_code, response.text)
        return

    odds_data = response.json()
    valid_data = []

    for game in odds_data:
        teams = game.get("teams")
        bookmakers = game.get("bookmakers", [])

        for book in bookmakers:
            bookmaker = book.get("title")
            for market in book.get("markets", []):
                prop_type = market.get("key")
                for outcome in market.get("outcomes", []):
                    team = outcome.get("name")
                    line = outcome.get("point")

                    # ✅ STRICT CHECK: skip props missing any key data
                    if not team or not prop_type or not bookmaker:
                        continue
                    if line is None or not isinstance(line, (int, float)):
                        continue

                    valid_data.append({
                        "id": str(uuid.uuid4()),
                        "team": team,
                        "prop_type": prop_type,
                        "line": float(line),
                        "bookmaker": bookmaker,
                        "created_at": datetime.utcnow().isoformat()
                    })

    if valid_data:
        print(f"✅ Found {len(valid_data)} valid props. Inserting into Supabase...")
        supabase.table("props").insert(valid_data).execute()
        print("✅ Insert complete.")
    else:
        print("⚠️ No valid props to insert.")

if __name__ == "__main__":
    fetch_and_store_odds()
