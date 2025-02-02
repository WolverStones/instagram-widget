# Instagram Feed Widget
# Author: Patrik Müller
# GitHub: https://github.com/WolverStones
# License: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import time
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, resources={r"/instagram/*": {"origins": "*"}})

INSTAGRAM_USERNAME = "nartdanceschool"
CACHE_FILE = "instagram_cache.json"
CACHE_EXPIRY = 3600  # Cache valid for 1 hour

ACCESS_TOKEN = ""


def fetch_instagram_profile():
    """Scrapes followers, following, and avatar directly from the Instagram profile (without API)."""
    url = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 🛠 Scraping JSON data from meta tags
        scripts = soup.find_all("script", type="application/ld+json")
        profile_data = None

        for script in scripts:
            try:
                json_data = json.loads(script.string)
                if "mainEntityofPage" in json_data:
                    profile_data = json_data["mainEntityofPage"]
                    break
            except (json.JSONDecodeError, TypeError):
                continue

        if not profile_data:
            print("⚠️ Failed to scrape profile data.")
            return None

        # ✅ Retrieving necessary information
        username = profile_data.get("name", INSTAGRAM_USERNAME)
        media_count = profile_data.get("interactionStatistic", [])[0][
            "userInteractionCount"
        ]
        followers = profile_data.get("interactionStatistic", [])[1][
            "userInteractionCount"
        ]
        following = profile_data.get("interactionStatistic", [])[2][
            "userInteractionCount"
        ]
        avatar_url = profile_data.get("image", "")

        return {
            "username": username,
            "media_count": media_count,
            "followers": followers,
            "following": following,
            "profile_picture_url": avatar_url,
        }

    except requests.RequestException as e:
        print(f"❌ Error while scraping profile: {e}")
        return None


def fetch_instagram_feed(limit=3):
    """Fetches the latest Instagram posts via the Graph API with a configurable limit."""
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

        return data.get("data", [])  # Returns as many posts as the API allows
    except requests.RequestException as e:
        print(f"❌ Error making API request: {e}")
        return []


def update_cache():
    """Updates cache every hour."""
    print("🔄 Updating cache...")
    profile_data = fetch_instagram_profile()
    feed_data = fetch_instagram_feed()

    if not profile_data:
        profile_data = {
            "username": INSTAGRAM_USERNAME,
            "media_count": 0,
            "followers": 0,
            "following": 0,
            "profile_picture_url": "",
        }
        print("⚠️ Cannot update profile data - set to default.")

    cache_data = {
        "timestamp": time.time(),
        "profile": profile_data,
        "feed": feed_data if feed_data else [],
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=4)
    print("✅ Cache updated.")


@app.route("/instagram/feed", methods=["GET"])
def get_instagram_data():
    """Returns cached profile data and fetches posts dynamically based on the `limit` URL parameter."""
    limit = request.args.get("limit", default=4, type=int)

    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            if (
                not cache_data
                or "timestamp" not in cache_data
                or "profile" not in cache_data
            ):
                print("⚠️ Cache is empty or invalid. Updating...")
                update_cache()
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

            if time.time() - cache_data["timestamp"] > CACHE_EXPIRY:
                print("♻️ Cache expired. Updating...")
                update_cache()
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

        except (json.JSONDecodeError, FileNotFoundError):
            print("⚠️ Corrupt cache file, updating...")
            update_cache()
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
    else:
        print("⚠️ Cache does not exist. Fetching data...")
        update_cache()
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

    feed_data = fetch_instagram_feed(limit)

    return jsonify({"profile": cache_data["profile"], "feed": feed_data})


if __name__ == "__main__":
    update_cache()
    app.run(host="0.0.0.0", debug=True, port=3019)
