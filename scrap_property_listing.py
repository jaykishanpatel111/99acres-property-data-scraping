import time
import requests
import json
import csv
import os
import logging
from datetime import datetime

from random import random, uniform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)

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

## ------------------------------------------- FUNCTION DEFINITIONS ----------------------------------------------##
# Utility function to sleep for a random duration
def random_sleep(min_seconds: float, max_seconds: float):
    """
    Suspends execution for a random interval between min and max range.
    """
    sleep_time = uniform(min_seconds, max_seconds)
    logging.info(f"Sleeping for {sleep_time:.2f} seconds...")
    time.sleep(sleep_time)

# Function to initialize and open 99acres.com
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

# Function to perform city search
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

# Function to find listing IDs on the page
def scroll_page(driver, pause_range=(2, 4)):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(uniform(*pause_range))

        # Small upward correction (human behavior)
        if uniform(0, 1) < 0.25:
            driver.execute_script("window.scrollBy(0, -500);")
            time.sleep(uniform(1, 2))

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            # Final upward scroll before stopping
            driver.execute_script("window.scrollBy(0, -800);")
            time.sleep(2)
            logging.info("Reached end of page.")
            break

        last_height = new_height

    return True

# Function to find listing IDs on the page
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
        
        # logging.info(f"extracted listing IDs are {listing_ids}.")
        logging.info(f"Found {len(listing_ids)} listings")
        return listing_ids

    except Exception as e:
        logging.error(f"Error finding listings: {e}")
        return []

# Function to clean listing IDs
def clean_list(data_list):
    exclude_patterns = ['muteUnmuteButton_', 'muteUnmuteButton', 'crossSellWidget_' , 'r2mWidget_']
    """
    1. Removes items containing specific keywords.
    2. Removes items that do not contain at least one numeric digit.
    """
    return [
        item for item in data_list 
        if not any(pattern in item for pattern in exclude_patterns) # Filter keywords
        and any(char.isdigit() for char in item)                    # Must have a digit
    ]

# Function to click the "Next Page" button
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

# Function to store listing IDs to CSV
def store_listings_to_csv(listing_ids, csv_path="all_listings.csv"):
    """
    Stores unique listing IDs into a CSV file.
    - Creates file if not exists
    - Appends only new IDs
    - On exception, writes to a new fallback CSV
    """

    if not listing_ids:
        logging.info("No listing IDs to store.")
        return

    try:
        existing_ids = set()

        # Read existing data if file exists
        if os.path.exists(csv_path):
            with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if row:
                        existing_ids.add(row[0])

        # Filter new unique IDs
        new_ids = [lid for lid in listing_ids if lid not in existing_ids]

        if not new_ids:
            logging.info("No new unique listings to append.")
            return

        file_exists = os.path.exists(csv_path)

        # Append safely
        with open(csv_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["listing_id"])

            for lid in new_ids:
                writer.writerow([lid])

        logging.info(f"Stored {len(new_ids)} new listings to {csv_path}")

    except Exception as e:
        logging.error(f"CSV write failed: {e}", exc_info=True)

        # 🔥 Fallback CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fallback_csv = f"all_listings_fallback_{timestamp}.csv"

        try:
            unique_ids = set(listing_ids)

            with open(fallback_csv, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["listing_id"])

                for lid in unique_ids:
                    writer.writerow([lid])

            logging.info(
                f"Fallback CSV created successfully: {fallback_csv} "
                f"with {len(unique_ids)} listings"
            )

        except Exception as fallback_error:
            logging.critical(
                f"Fallback CSV write also failed: {fallback_error}",
                exc_info=True
            )


def main():
    start_time = time.time()
    logging.info(f"Script started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    city_name = "Ahmedabad"
    browser = open_99acres()
    page_no = 5
    max_pages = 600

    all_listings = []  # 🔹 collect all listings here

    try:
        if browser:
            perform_city_search(browser, city_name)
            time.sleep(6)

            while page_no <= max_pages:
                logging.info(f"\n--- Processing Page {page_no} ---")

                # 1. Scroll
                scroll_page(browser, pause_range=(2, 4))

                # 2. Extract IDs
                listing_ids = find_listings(browser)
                project_listing_ids = clean_list(listing_ids)

                if project_listing_ids:
                    all_listings.extend(project_listing_ids)
                    logging.info(f"Page {page_no} listings found: {len(project_listing_ids)}")
                else:
                    logging.warning(f"No listings found on page {page_no}.")

                # 3. Pagination
                has_next = click_next_page(browser)
                if not has_next:
                    logging.info("No more pages available. Stopping.")
                    break

                page_no += 1
                random_sleep(3, 7)

    finally:
        # 🔹 Store unique listings in CSV
        store_listings_to_csv(all_listings, csv_path="all_listings.csv")

        end_time = time.time()
        logging.info(f"Last page processed: {page_no}")
        logging.info(f"Script ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")

        if browser:
            browser.quit()


if __name__ == "__main__":
    main()