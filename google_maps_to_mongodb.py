from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import time
import re

# ===============================
# LOAD ENV VARIABLES
# ===============================
load_dotenv()

# ===============================
# MongoDB CONNECTION (PASSWORD HIDDEN)
# ===============================
MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)
db = client["grocery_db"]
collection = db["shops"]

collection.create_index(
    [("shopName", 1), ("location.coordinates", 1)],
    unique=True
)
collection.create_index([("location", "2dsphere")])

# ===============================
# CATEGORY → SHOP TYPE MAP
# ===============================
CATEGORY_MAP = {
    "medical": ["pharmacy", "medical", "chemist", "drug"],
    "grocery": ["grocery", "supermarket", "kirana", "provision"],
    "bakery": ["bakery"],
    "restaurant": ["restaurant", "cafe", "food"],
    "electronics": ["electronics", "mobile", "computer"]
}

# ===============================
# CLEAN PHONE
# ===============================
def clean_phone_number(phone):
    if not phone:
        return ""
    phone = re.sub(r"\D", "", phone)
    return phone[-10:] if len(phone) > 10 else phone

# ===============================
# MAIN FUNCTION
# ===============================
def scrape_and_store(search_query):

    query_for_url = search_query.replace(" ", "+")
    URL = f"https://www.google.com/maps/search/{query_for_url}"

    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    wait = WebDriverWait(driver, 25)

    driver.get(URL)
    time.sleep(6)

    scrollable_div = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@aria-label,'Results')]")
        )
    )

    for _ in range(15):
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight",
            scrollable_div
        )
        time.sleep(2)

    shops = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    inserted_count = 0

    print("🚀 Scraping started for:", search_query)

    for shop in shops:
        try:
            link = shop.find_element(By.CSS_SELECTOR, "a.hfpxzc")
            shop_name = link.get_attribute("aria-label")
            href = link.get_attribute("href")

            lat = re.search(r"!3d([-0-9.]+)", href)
            lng = re.search(r"!4d([-0-9.]+)", href)
            if not lat or not lng:
                continue

            driver.execute_script("window.open(arguments[0]);", href)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(4)

            # -------- CATEGORY
            try:
                category = driver.find_element(
                    By.XPATH, "//button[contains(@jsaction,'category')]"
                ).text.strip()
            except:
                category = "Unknown"

            category_lower = category.lower()

            # -------- SHOP TYPE
            shop_type = "other"
            for key, keywords in CATEGORY_MAP.items():
                if any(word in category_lower for word in keywords):
                    shop_type = key
                    break

            # -------- PHONE
            try:
                raw_phone = driver.find_element(
                    By.XPATH, "//button[contains(@aria-label,'Phone')]"
                ).get_attribute("aria-label").replace("Phone: ", "")
                contact = clean_phone_number(raw_phone)
            except:
                contact = ""

            # -------- ADDRESS
            try:
                address = driver.find_element(
                    By.XPATH, "//button[@data-item-id='address']"
                ).get_attribute("aria-label").replace("Address: ", "")
            except:
                address = ""

            # -------- IMAGE
            try:
                image = driver.find_element(
                    By.XPATH, "//img[contains(@src,'googleusercontent.com')]"
                ).get_attribute("src")
            except:
                image = ""

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # ===============================
            # FINAL DATA FORMAT (UNCHANGED)
            # ===============================
            shop_data = {
                "shopName": shop_name,
                "category": category,
                "shopType": shop_type,
                "contactNumber": contact,
                "address": address,
                "image": image,
                "location": {
                    "type": "Point",
                    "coordinates": [
                        float(lng.group(1)),
                        float(lat.group(1))
                    ]
                },
                "searchQuery": search_query
            }

            try:
                collection.insert_one(shop_data)
                inserted_count += 1
                print(f"✅ Inserted: {shop_name} ({shop_type})")
            except:
                print(f"⚠️ Duplicate skipped: {shop_name}")

        except:
            continue

    driver.quit()
    print(f"\n🎉 DONE | New shops inserted: {inserted_count}")
    return inserted_count
