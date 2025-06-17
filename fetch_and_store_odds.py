import os
import requests
import uuid
from datetime import datetime
from supabase import create_client, Client

# ENV variables
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
ODDS_API_KEY = os.environ["ODDS_API_KEY"]

# Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch odds
response = requests.get(
    "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds",
    params={
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "apiKey": ODDS_API_KEY,
    }
)

# Check response
if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

games = response.json()

# Filter and structure data
data = []
for game in games:
    teams = game.get("teams", [])
    bookmakers = game.get("bookmakers", [])
    
    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []):
            for outcome in market.get("outcomes", []):
                player_name = outcome.get("name")
                prop_type = market.get("key")
                line = outcome.get("point")
                sportsbook = bookmaker.get("title")
                game_time = game.get("commence_time")

                # 💡 Skip if any required field is missing
                if not all([player_name, prop_type, line]):
                    continue

                data.append({
                    "id": str(uuid.uuid4()),
                    "player_name": player_name,
                    "prop_type": prop_type,
                    "line": line,
                    "sportsbook": sportsbook,
                    "game_time": game_time,
                })

print(f"✅ Filtered {len(data)} valid props")

# Insert to Supabase only if valid
if data:
    print(f"📥 Inserting {len(data)} rows into Supabase...")
    supabase.table("props").insert(data).execute()
    print("✅ Insert successful.")
else:
    print("⚠️ No valid data to insert. Skipped upload.")
