import requests

def get_lat_lng(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place_name,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "NearbyShopFinder/1.0"
    }

    res = requests.get(url, params=params, headers=headers).json()

    if not res:
        return None, None

    lat = float(res[0]["lat"])
    lng = float(res[0]["lon"])
    return lat, lng
