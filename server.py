# Instagram Feed Widget
# Author: Patrik Müller
# GitHub: https://github.com/WolverStones
# License: Apache-2.0

import json
import os
import time
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

INSTAGRAM_USERNAME = "nartdanceschool"
CACHE_FILE = "instagram_cache.json"
CACHE_EXPIRY = 3600  # Cache valid for 1 hour
ACCESS_TOKEN = ""  # 🔴 Sem doplň svůj přístupový token


def fetch_instagram_profile():
    """Fetch Instagram profile details including media count."""
    if not ACCESS_TOKEN:
        print("❌ Missing access token for Instagram API.")
        return None

    url = f"https://graph.instagram.com/me?fields=id,username,media_count&access_token={ACCESS_TOKEN}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print(f"❌ Error fetching profile data: {data['error']['message']}")
            return None

        print(f"✅ Profile data fetched: {data}")  # 🛠 Debug log

        return {
            "username": data.get("username", INSTAGRAM_USERNAME),
            "media_count": data.get("media_count", 0),
            "followers": 0,
            "following": 0,
        }
    except requests.RequestException as e:
        print(f"❌ Error fetching profile: {e}")
        return None


def fetch_instagram_feed(limit=3):
    """Fetch latest Instagram posts via Graph API."""
    if not ACCESS_TOKEN:
        print("❌ Missing access token for Instagram API.")
        return []

    url = f"https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,permalink&access_token={ACCESS_TOKEN}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            print(f"❌ Error fetching feed: {data['error']['message']}")
            return []

        return data.get("data", [])
    except requests.RequestException as e:
        print(f"❌ Error making API request: {e}")
        return []


def update_cache():
    """Update cache at server startup and every hour."""
    print("🔄 Updating cache...")

    profile_data = fetch_instagram_profile()

    # Pokud media_count == 0, zkusíme ho znovu získat
    if not profile_data or profile_data["media_count"] == 0:
        print("⚠️ media_count missing or 0, forcing update...")
        profile_data = fetch_instagram_profile()

    # Fallback pokud API selže
    if not profile_data:
        profile_data = {
            "username": INSTAGRAM_USERNAME,
            "media_count": 0,
            "followers": 0,
            "following": 0,
        }

    feed_data = fetch_instagram_feed()

    cache_data = {
        "timestamp": time.time(),
        "profile": profile_data,
        "feed": feed_data or [],
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Cache updated: {profile_data}")


def load_cache():
    """Load cache and update if expired or invalid."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            if time.time() - cache_data.get("timestamp", 0) > CACHE_EXPIRY:
                print("♻️ Cache expired. Updating...")
                update_cache()
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

            return cache_data
        except (json.JSONDecodeError, FileNotFoundError):
            print("⚠️ Corrupt cache file, updating...")
            update_cache()
    else:
        print("⚠️ Cache does not exist. Fetching data...")
        update_cache()

    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/instagram/feed", methods=["GET"])
def get_instagram_data():
    """Return cached profile data and fetch posts dynamically."""
    limit = request.args.get("limit", default=4, type=int)
    cache_data = load_cache()
    feed_data = fetch_instagram_feed(limit)

    return jsonify(
        {
            "profile": {
                "username": cache_data["profile"]["username"],
                "media_count": cache_data["profile"]["media_count"],  # ✅ Opraveno
                "followers": cache_data["profile"]["followers"],
                "following": cache_data["profile"]["following"],
            },
            "feed": feed_data,
        }
    )


if __name__ == "__main__":
    update_cache()  # ✅ Vynucená aktualizace při startu serveru
    app.run(host="0.0.0.0", port=3019)
