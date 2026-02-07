import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
from google_maps_to_mongodb import scrape_and_store

# load .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# ===============================
# MongoDB (NO PASSWORD IN CODE)
# ===============================
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["grocery_db"]
collection = db["shops"]

# ===============================
# Geocoding: place -> lat/lng
# ===============================
def geocode_place(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "NearbyShopFinder/1.0"}

    res = requests.get(url, params=params, headers=headers).json()
    if not res:
        return None, None

    return float(res[0]["lat"]), float(res[0]["lon"])

# ===============================
# MAIN SEARCH API
# ===============================
@app.route("/search", methods=["POST"])
def search():
    data = request.json or {}

    search_text = data.get("searchQuery", "").strip()
    distance_km = float(data.get("distanceKm", 4))

    if not search_text:
        return jsonify({"error": "Search text required"}), 400

    # STEP 1: scrape Google Maps & store in DB (duplicates skipped)
    scrape_and_store(search_text)

    # STEP 2: detect shop type
    text_lower = search_text.lower()
    shop_type = None
    if any(w in text_lower for w in ["medical", "pharmacy", "chemist"]):
        shop_type = "medical"
    elif any(w in text_lower for w in ["grocery", "kirana", "supermarket"]):
        shop_type = "grocery"

    # STEP 3: extract place
    place = text_lower
    for w in ["medical shop", "grocery store", "medical", "grocery", "pharmacy", "near"]:
        place = place.replace(w, "")
    place = place.strip()

    # STEP 4: geocode place
    lat, lng = geocode_place(place)
    if lat is None:
        return jsonify({"error": "Location not found"}), 400

    # STEP 5: MongoDB geo query
    query = {
        "location": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "$maxDistance": distance_km * 1000
            }
        }
    }

    if shop_type:
        query["shopType"] = shop_type

    shops = list(collection.find(query, {"_id": 0}))

    return jsonify({
        "placeUsed": place,
        "radiusKm": distance_km,
        "count": len(shops),
        "shops": shops
    })

if __name__ == "__main__":
    app.run(debug=True)
