from random import random, uniform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent

import threading
from threading import Lock


# Create a lock object to prevent CSV corruption
csv_lock = threading.Lock()

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)

import time
import requests
import json
import csv
import os
import logging
from datetime import datetime

#----------------------------------------------- LOGGING SETUP ------------------------------------------------#
# Common formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")

# Clear any existing log handlers
logging.getLogger().handlers = []
logging.getLogger().setLevel(logging.INFO)  # Keep this if you still want other handlers to capture DEBUG

# =========================
# PART 1 — FILE + CONSOLE
# =========================
# Create a logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# File handler (INFO and above only)
# Get current date in DD_MM_YYYY format
current_date = datetime.now().strftime("%d_%m_%Y")

# Create log file name dynamically
log_filename = f"logs/logs_{current_date}.log"

# Setup file handler
file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console handler (DEBUG and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)


# # =========================
# # PART 2 — CONSOLE ONLY
# # =========================

# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)  # Or INFO if you want less output
# console_handler.setFormatter(formatter)

# logging.getLogger().addHandler(console_handler)

def get_random_user_agent():
    """
    Generates a random user agent string using the fake_useragent library.
    """
    ua = UserAgent()
    return ua.random

def open_99acres():
    """
    Initializes a Chrome driver and navigates to 99acres.com.
    """
    # 1. Setup Chrome Options to look less like a bot
    chrome_options = Options()
    # headless mode can be enabled if needed
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # Optional: chrome_options.add_argument("--headless") # Run without a popup window
    
    # 2. Automatically manage the ChromeDriver version
    service = Service(ChromeDriverManager().install())
    
    # 3. Initialize the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        logging.info("Navigating to 99acres...")
        driver.get("https://www.99acres.com/")
        
        # Give the page a few seconds to load its JavaScript components
        random_sleep(1, 5) 
        
        logging.info(f"Successfully loaded: {driver.title}")
        return driver

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        driver.quit()
        return None

def perform_city_search(driver, city_name):
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Click the search wrapper (this activates input)
        search_wrapper = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'DeskSfInput')]"))
        )
        search_wrapper.click()
        random_sleep(1, 5)

        logging.info("Search wrapper clicked.")
        # 2. Find the actual INPUT inside the wrapper
        search_input = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//div[@class='component__DeskSfInput']/input[@type='text']"))
        )

        # 3. Clear & type city name
        search_input.clear()
        search_input.send_keys(city_name)
        logging.info(f"Typed city: {city_name}")

        # 4. Wait for dropdown suggestion & hit ENTER
        random_sleep(1, 3)
        search_input.send_keys(Keys.ENTER)

        logging.info(f"Search for {city_name} executed successfully.")

    except Exception as e:
        logging.error(f"Error during search: {e}")

import random
import logging

def scroll_page(driver, pause_range=(2, 4)):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(*pause_range))

        # Small upward correction (human behavior)
        if random.random() < 0.25:
            driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(random.uniform(1, 2))

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            # Final upward scroll before stopping
            driver.execute_script("window.scrollBy(0, -800);")
            time.sleep(2)
            logging.info("Reached end of page.")
            break

        last_height = new_height

    return True



from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)

def click_next_page(driver, retry_on_reload=True):
    try:
        logging.info("Looking for Next Page button...")

        next_btn = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(normalize-space(),'Next Page')]")
            )
        )

        # Scroll into view (centered)
        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", next_btn
        )
        random_sleep(1, 3)

        # Attempt 1: normal click
        try:
            next_btn.click()
            logging.info("Clicked Next Page (normal click)")
            return True

        except ElementClickInterceptedException:
            logging.warning("Normal click failed, trying JS click...")

        # Attempt 2: JavaScript click
        try:
            driver.execute_script("arguments[0].click();", next_btn)
            logging.info("Clicked Next Page (JS click)")
            return True

        except Exception:
            logging.warning("JS click failed, trying direct navigation...")

        # Attempt 3: navigate via href
        next_url = next_btn.get_attribute("href")
        if next_url:
            driver.get(next_url)
            logging.info(f"Navigated to Next Page via URL: {next_url}")
            return True

        return False

    except (TimeoutException, NoSuchElementException):
        logging.warning("Next Page button not found.")

        # # 🔁 Reload once and retry
        # if retry_on_reload:
        #     logging.info("Reloading page and retrying Next Page...")
        #     driver.refresh()
        #     random_sleep(4, 6)

        #     # Retry once, disable further reloads
        #     return click_next_page(driver, retry_on_reload=False)

        logging.info("Next Page still not found after reload.")
        return False



def find_listings(driver):
    """
    Finds listing IDs inside the main search results container.

    Returns:
        list: List of listing IDs (strings)
    """
    wait = WebDriverWait(driver, 20)
    listing_ids = []

    try:
        # 1. Wait for main results container
        main_container = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='pageComponent undefined']")
            )
        )

        # 2. Find all direct child divs that have an ID
        listing_elements = main_container.find_elements(
            By.XPATH, ".//div[@id and (@data-label or @data-propid)]"
        )

        for el in listing_elements:
            listing_id = el.get_attribute("id")

            if listing_id:
                listing_ids.append(listing_id)

        logging.info(f"Found {len(listing_ids)} listings")
        return listing_ids

    except Exception as e:
        logging.error(f"Error finding listings: {e}")
        return []


def project_details_API(project_id):

    url = f"https://www.99acres.com/api-aggregator/v2/project-details?projectIds=PROJECT_{project_id}_R&page=PROJECT_DETAIL_PAGE&platform=DESKTOP&stage=SCROLL_CLICK&crawlableComponents=SEARCH_RESALE_PROPERTIES,SEARCH_RENTAL_PROPERTIES,SEARCH_BUILDER_PROJECTS,COLLABORATIVE_PROJECTS,SIMILAR_PROJECTS,RATINGS_AND_REVIEWS"

    user_agent = get_random_user_agent()
    payload = {}
    headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-US,en;q=0.9,es;q=0.8',
    'apitoken': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk3MTI5MzUuMjY4LCJleHAiOjE3Njk3MTMwNTUuMjY4LCJocSI6ImExMWNiM2ZmNjkxOTk0MGQxNjI2M2E2NWQwODgzZTE3Iiwid2IiOiIwZWE3MzQ3OTBhMDYzMTc4NjQ4ZTkzMjc2MzliZjBlZSJ9.xngjaYn7IQZViW9CSq_ySkzwjCS9hnrDplsOhMNKMeE',
    'authorizationtoken': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk3MTI2NDIsImV4cCI6MTc2OTcxMzI0MiwiczMiOiJZbHA1V0ZkdWEwMUdMMmc1V1VSek0zQmhNbXBETjFWRFlrWjJRaXRpVjNkQ1JrcDVVM1pKUVVFclZWcFNRVVpyYm5KRksyWmhXakZsYlZJMWRIUmlWM28xTWtOTFkwRnVTVnBxTVUwMU9GUTFaV2d2WVZvclNrNHlhR2xEZVZrM2IwRm1kM2RaVW14cFlrZE1LMUJzUkZaYWVDdFpPVFZPZUVaalZUQjBZM2xLT0dOaWJWQlFaVlF5Um5GNlUzSk1hazR3TmtWd01UVjNkbkpZYVhwWGJEaEhVRGM1VW5aUlpsZHhXVnBhVlVaeFlpOUdhVmRaV1hnemNETXdTakJoVWsxVWFVVldZMUZTZUZKM2VHZEhWWGt6UmtOa1IyRXdPVXR4VjBoV1YzSkxSVE5DZVM5Tk1TdEdWbEJMVVVkSVZqUmlOWFZSWldOUVJuaE1VVm95UkZWcmMwTmFTelZTU1hoMlJWYzFTRlZ4TW1WVVJVbG1NVlJPWjJSU2MwUjJTRGsxVlRNNFdESXplRVZZUzFJNWFVVnNRbXhwVXpodWEybHpMMmwyTlcxRGJFTTRORU52Y0RKRkt6WXZia1pHYWxKdVNXbDFLM0E0WkdwWVFYUkNObnBFY0hSR2JtVm9OSG93UFFvPSIsImRhdGEiOiJJRHlaMTRwQ2YvQ05iWXF5N3NxV2I1S01pdyswd25EcCtQWWs4SW5OSVJzaDZqamlQSHlPRS9OZndNaVJxWWRWRm1PcVhwblFTRlRTZ1h3SlcvaUZ6V2tPM1JzSWk3QWoxanU5VkJvYzE5N0pjMEgvU3FGZVcwbXVCa1hKbUlkUVdYdGV6SmI4alg3TzRiWWFXd3RYQjBubHRseFZDa1g1eUhpdDZ6L2NPVUtYOEYvTzkyR1hIMEFFOGtXQ1dQVnFUdkRaeHdYeGxDNnZ0eHRNUEsrUjZxUjZyeDhvN2dYTG5WampXY3FJTG1kam5XRGU2LzIyZXRudjhPVWR4ZHR5MUtLd09BVm5rL2NLWU04TmpjL0xtMVhoS2ZkWTRicWtQNEYvUmdGZ1pleDV6VEh4c2VHcHhpQUNZSHdQQXpQSS9HNm9EelMvY0lGbngwc2lIODlSMlk4NlEvQWRSeExYREx0SFNtZ3pzaFRhdkcvSEsyVTQxVUw0UEtlTEwxeDUiLCJ2IjoiMiIsInMxIjoiOEZIbjlOREhkcVV4OGIvVG9tQU5HaytLT2h6RjRnQjAiLCJzMiI6IkV2YW1qYmpsWCtWbzFlMyt1b1E2RFZ4YytkTGdQR3Y0In0.wC4MLtuwJDgxRzkTMdDDOQxdOY2tlpuzQbI7tnOOAOo',
    # 'deviceid': '2b30974876de6a17dd6613acfd35eae0',
    'dnt': '1',
    'pagename': 'XID',
    'platform': 'desktop',
    'priority': 'u=1, i',
    'referer': f'https://www.99acres.com/property-r{project_id}',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': user_agent,
    # 'Cookie': '99_ab=40; GOOGLE_SEARCH_ID=2184671769697947514; xAB=SuperControlGroup%3D23%3AN%2CtopMatchHandlingAB%3D51%3AD%2CBFdataremoval%3D7%3AY%2CseamlessLogin%3D79%3AY%2CEMAILOPTIONAL%3D82%3AY%2CMLSEARCHSRP%3D32%3AN%2CDSSimilarProperties%3D93%3AY%2CshowInhousePlayer%3D50%3AD%2CIATABSVF%3D92%3AD%2CVSRAlgoDemandShaping%3D88%3AY%2CBUILDERFLOORSRP%3D53%3AY%2CMLSEARCHMONET%3D37%3AY%2CNEARBYSRP%3D73%3AY%2CppfTemplatePostingV2%3D75%3AY%2CbrokerSupplyRef%3D32%3AY%2CownerEmailOptional%3D19%3AY%2CppfCommSoftPosting%3D74%3AN; session_source=DIRECT; landmark_toast=true; _gcl_au=1.1.1853515014.1769697954; _clck=tsd8w5%5E2%5Eg34%5E0%5E2220; showCookieBanner=1; _gid=GA1.2.1817173398.1769697955; _fbp=fb.1.1769697955419.219187819148461958; _hjSessionUser_3171461=eyJpZCI6ImExY2EwN2FlLWVhODQtNWQ3NC04NjhjLTk1MDdkZjNiODI0YSIsImNyZWF0ZWQiOjE3Njk2OTc5NTQzNjQsImV4aXN0aW5nIjp0cnVlfQ==; hp_bcf_data=; _hjSession_3171461=eyJpZCI6IjMzN2Q3YzU0LTA3MTgtNGIwNC04NGEzLThkMDM0YjFhMWIwNiIsImMiOjE3Njk3MDgzOTY5NjQsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; 99_ab=40; acceptedMobileDsiclaimer=true; session30m=eyJ0b2tlbklkIjoiODExNDdhYzEtOGM4Ni00OGU2LWE0ZDEtYzVlNDY5MDM4NWRkIiwiaXNzdWVEYXRlIjoxNzY5NzEyNTc4ODQ1fQ; sessionno=5; _sess_id=7CsRjTfmEgSmXgNimUiM5qJnzanWRO0ASvXA8j4R%2B0USBNrxGmFT86SZf2rW5pNWVU6XdKa%2BX4bt8Kse%2BxPo4A%3D%3D; _ga_9QHC0XEKPS=GS2.1.s1769710741$o4$g1$t1769712647$j56$l0$h0; _ga=GA1.2.594436881.1769697954; _uetsid=37457b10fd2111f08ee345c1d8e7b106; _uetvid=37459e80fd2111f09a51ef4bbeecf475; _clsk=1jbu9a8%5E1769712930225%5E18%5E0%5Ea.clarity.ms%2Fcollect'
    }

    # Use a session for better performance and retry logic
    session = requests.Session()
    
    try:
        # Added verify=False if you are getting SSL/Proxy errors
        # Added timeout to prevent the script from hanging indefinitely
        response = session.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code != 200:
            for i in range(5):
                logging.warning(f"Retry {i+1} for Project {project_id} (Status: {response.status_code})")
                random_sleep(1, 3)
                response = session.get(url, headers=headers, timeout=15, verify=False)
                if response.status_code == 200:
                    break
        
        return response.text if response.status_code == 200 else None

    except requests.exceptions.SSLError:
        logging.error("SSL Error: Try setting verify=False in the get() request.")
    except Exception as e:
        logging.error(f"Error fetching project details: {e}")
    return None


def extract_99acres_project_data_safe(response_text: str) -> dict:
    try:
        data = json.loads(response_text)
    except Exception:
        return {}

    projects = data.get("projects") or []
    if not projects:
        return {}

    project = projects[0] or {}

    basic = project.get("basicDetails") or {}
    location = basic.get("location") or {}
    components = project.get("components") or {}
    floor_plans = (
        components
        .get("floorPlans", {})
        .get("configurations", {})
        .get("tuples") or []
    )

    # ---------------- Project level ----------------
    result = {
        "project_id": basic.get("projectId"),
        "project_name": basic.get("name"),
        "project_type": "Residential",
        "launch_status": (
            project.get("commonElements", {})
                   .get("benefits", {})
                   .get("heading")
        ),
        "city": location.get("cityName"),
        "locality": location.get("localityName"),
        "state": location.get("stateName"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "address": basic.get("streetAddress"),
        "postal_code": basic.get("postalCode"),
        "price_min": basic.get("price", {}).get("min"),
        "price_max": basic.get("price", {}).get("max"),
        "price_label": basic.get("price", {}).get("label"),
        "site_plan_url": components.get("floorPlans", {}).get("sitePlanURL"),
        "highlights": [
            h.get("text")
            for h in (basic.get("keyHighlights") or [])
            if h.get("text")
        ],
        "government_charges": [
            {
                "title": g.get("title"),
                "points": g.get("points") or []
            }
            for g in (project.get("govtCharges", {}).get("tuples") or [])
        ],
        "has_rera_disclaimer": bool(
            project.get("commonElements", {}).get("reraDefaultInfo")
        ),
        "available_bhk_types": sorted({
            cfg.get("bedroom")
            for cfg in floor_plans
            if cfg.get("bedroom") is not None
        }),
        "units": []
    }

    # ---------------- Unit level ----------------
    for cfg in floor_plans:
        if not isinstance(cfg, dict):
            continue

        bhk = cfg.get("bedroom")
        prop_type = cfg.get("propertyTypeLabel")

        for group in (cfg.get("groups") or []):
            for unit in (group.get("tuples") or []):

                area = unit.get("area") or {}
                price = unit.get("price") or {}
                construction = unit.get("constructionStatusCard") or {}

                images = unit.get("images") or {}
                images_2d = images.get("2D") or []
                images_3d = images.get("3D") or []

                sellers = [
                    {
                        "name": s.get("name"),
                        "company": s.get("companyName"),
                        "type": s.get("label")
                    }
                    for s in (unit.get("sellers", {}).get("tuples") or [])
                ]

                result["units"].append({
                    "bhk": bhk,
                    "property_type": prop_type,
                    "area_sqft": area.get("min"),
                    "area_type": area.get("type", {}).get("label"),
                    "price": price.get("min"),
                    "price_authentic": price.get("authentic"),
                    "possession": construction.get("subLabel"),
                    "possession_raw": construction.get("dateLabel"),
                    "floorplan_2d_url": (
                        images_2d[0].get("variants", {}).get("ORIGINAL")
                        if images_2d else None
                    ),
                    "floorplan_3d_url": (
                        images_3d[0].get("variants", {}).get("LARGE")
                        if images_3d else None
                    ),
                    "sellers": sellers
                })

    return result

def save_99acres_data_to_csv(project_data: dict, csv_path: str):
    if not project_data or "units" not in project_data:
        return

    file_exists = os.path.isfile(csv_path)

    fieldnames = [
        "project_id", "project_name", "project_type", "launch_status",
        "city", "locality", "state", "latitude", "longitude",
        "address", "postal_code",
        "price_min", "price_max", "price_label",
        "site_plan_url", "has_rera_disclaimer",
        "available_bhk_types", "highlights", "government_charges",
        "bhk", "property_type", "area_sqft", "area_type",
        "price", "price_authentic",
        "possession", "possession_raw",
        "floorplan_2d_url", "floorplan_3d_url",
        "sellers"
    ]

    with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for unit in project_data.get("units", []):
            row = {
                "project_id": project_data.get("project_id"),
                "project_name": project_data.get("project_name"),
                "project_type": project_data.get("project_type"),
                "launch_status": project_data.get("launch_status"),
                "city": project_data.get("city"),
                "locality": project_data.get("locality"),
                "state": project_data.get("state"),
                "latitude": project_data.get("latitude"),
                "longitude": project_data.get("longitude"),
                "address": project_data.get("address"),
                "postal_code": project_data.get("postal_code"),
                "price_min": project_data.get("price_min"),
                "price_max": project_data.get("price_max"),
                "price_label": project_data.get("price_label"),
                "site_plan_url": project_data.get("site_plan_url"),
                "has_rera_disclaimer": project_data.get("has_rera_disclaimer"),
                "available_bhk_types": ",".join(
                    map(str, project_data.get("available_bhk_types", []))
                ),
                "highlights": " | ".join(project_data.get("highlights", [])),
                "government_charges": " | ".join(
                    f"{g.get('title')}: {', '.join(g.get('points', []))}"
                    for g in project_data.get("government_charges", [])
                ),
                "bhk": unit.get("bhk"),
                "property_type": unit.get("property_type"),
                "area_sqft": unit.get("area_sqft"),
                "area_type": unit.get("area_type"),
                "price": unit.get("price"),
                "price_authentic": unit.get("price_authentic"),
                "possession": unit.get("possession"),
                "possession_raw": unit.get("possession_raw"),
                "floorplan_2d_url": unit.get("floorplan_2d_url"),
                "floorplan_3d_url": unit.get("floorplan_3d_url"),
                "sellers": " | ".join(
                    f"{s.get('name')} ({s.get('type')})"
                    for s in unit.get("sellers", [])
                )
            }

            writer.writerow(row)

def random_sleep(min_seconds: float, max_seconds: float):
    """
    Suspends execution for a random interval between min and max range.
    """
    sleep_time = uniform(min_seconds, max_seconds)
    print(f"Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)

# def main_2(all_listing_ids):
#     original_data = all_listing_ids
#     numeric_only = [item for item in original_data if item.isdigit()]
#     for project_id in numeric_only:
#         logging.info(f"Fetching details for project ID: {project_id}")
#         response = project_details_API(project_id)
#         project_data = extract_99acres_project_data_safe(response)
#         save_99acres_data_to_csv(project_data, "99acres_projects.csv")
#         random_sleep(1, 2)

def process_single_project(project_id):
    """Function for a single thread to execute"""
    try:
        logging.info(f"Fetching details for project ID: {project_id}")
        
        response = project_details_API(project_id)
        if not response:
            return

        project_data = extract_99acres_project_data_safe(response)
        
        if project_data:
            # Use the lock to ensure thread-safe writing
            with csv_lock:
                save_99acres_data_to_csv(project_data, "99acres_projects.csv")
        
        # Small sleep to avoid overwhelming the API
        random_sleep(2, 4)
        
    except Exception as e:
        logging.error(f"Error in thread for ID {project_id}: {e}")


# Global counter & lock
request_counter = 0
counter_lock = Lock()

def wrapped_process(project_id):
    global request_counter

    process_single_project(project_id)

    with counter_lock:
        request_counter += 1

        # Pause every 10 requests
        if request_counter % 10 == 0:
            sleep_time = random.randint(5, 10)
            logging.info(
                f"Processed {request_counter} projects. "
                f"Sleeping for {sleep_time}s to avoid blocking."
            )
            time.sleep(sleep_time)

def main_2(all_listing_ids):
    numeric_only = [item for item in all_listing_ids if item.isdigit()]

    max_workers = 5
    logging.info(
        f"Starting multithreaded extraction for {len(numeric_only)} projects..."
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(wrapped_process, pid)
            for pid in numeric_only
        ]

        for future in as_completed(futures):
            future.result()  # surface exceptions

    logging.info("Multithreaded processing complete.")


if __name__ == "__main__":
    start_time = time.time()
    logging.info(f"Script started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    city_name = "Ahmedabad"
    browser = open_99acres()
    page_no = 1
    max_pages = 600  # Optional: safety limit so you don't scrape forever

    try:
        if browser:
            perform_city_search(browser, city_name)
            time.sleep(6)

            while page_no <= max_pages:
                logging.info(f"\n--- Processing Page {page_no} ---")

                # 1. Scroll to load content
                scroll_page(browser, pause_range=(2, 4))

                # 2. Extract and clean IDs
                listing_ids = find_listings(browser)
                numeric_only = [item for item in listing_ids if item.isdigit()]
                
                if numeric_only:
                    # main_2(numeric_only)
                    logging.info(f"Page {page_no} listings found: {len(numeric_only)}")
                else:
                    logging.warning(f"No listings found on page {page_no}.")

                # 3. Check for the "Next" button/pagination
                # Note: You'll need a function to click the 'Next' button
                has_next = click_next_page(browser) 
                
                if not has_next:
                    logging.info("No more pages available. Stopping.")
                    break

                page_no += 1
                random_sleep(3, 7)  # Longer sleep between page loads to avoid detection

    finally:
        end_time = time.time()
        logging.info(f"Last page processed: {page_no}")
        logging.info(f"Script ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")
        if browser:
            browser.quit()
