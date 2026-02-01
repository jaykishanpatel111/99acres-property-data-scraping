# 🏠 99acres Project & Property Scraper

This project is a Python-based web scraping system designed to extract **real estate project and property data from 99acres.com**.  
It follows a **hybrid scraping approach**, combining **Selenium browser automation** with **direct API requests** to efficiently collect high-quality, structured data while handling complex UI interactions.

The scraper is built with **scalability, fault tolerance, and anti-bot awareness** in mind.

---

## 📌 Key Highlights

- Two-stage scraping architecture (Listing → Data Extraction)
- Hybrid scraping (Selenium + internal APIs)
- Multithreaded execution with controlled concurrency
- Anti-bot mitigation strategies
- Incremental and thread-safe CSV storage
- Designed for re-runs without duplicate data

---

## 🧩 Scraping Architecture Overview

The scraping workflow is divided into **two independent stages**:

### Stage 1: Property Listing Collection  
Collects all unique property / project listing IDs from search result pages.

### Stage 2: Property & Project Data Extraction  
Uses collected listing IDs to scrape detailed data via APIs and page HTML.

---

## 🧱 Stage 1: Property Listing Scraping

**Script:** `scrap_property_listing.py`

### Purpose
Extract all unique listing IDs from 99acres search result pages for a given city.

### Workflow

1. Launch browser using Selenium with human-like configuration.
2. Open `https://www.99acres.com/`.
3. Enter city name (default: **Ahmedabad**) in the search bar.
4. Load the property listing page.
5. Scroll the page gradually to simulate real user behavior.
6. Extract listing IDs from property cards.
7. Navigate through pagination using the **Next Page** button.
8. Deduplicate listing IDs.
9. Persist all IDs to:

```
all_listings.csv
```

---

## 🧱 Stage 2: Property & Project Data Scraping

**Script:** `property_data_merged.py`

### Purpose
Scrape detailed **project-level** and **property-level** data only for listings
that have not been processed earlier.

---

### 🔄 Pre-Processing Logic

1. Load all listing IDs from:
   ```
   all_listings.csv
   ```
2. Load existing output files:
   ```
   99acres_data.csv
   99acers_projects.csv
   ```
3. Identify listing IDs missing from output files.
4. Create a filtered list of **pending listings**.

---

### ⚙️ Scraping Strategy (Hybrid & Multi-Threaded)

Each listing is processed using two parallel methods:

#### 🔹 Project Data Scraping (API-Based)
- Uses internal **99acres project-details API**.
- API endpoints identified via browser Network tab.
- Extracts:
  - Project name & ID
  - Project type & launch status
  - Location, address, latitude & longitude
  - Key highlights and metadata

#### 🔹 Property Data Scraping (HTML-Based)
- Fetches property detail page HTML.
- Parses structured and semi-structured content.
- Extracts:
  - Unit configuration (BHK, area, area type)
  - Pricing details
  - Possession status
  - Floor plan and site plan URLs
  - Seller information

---

### 🧵 Concurrency Model

- Uses `ThreadPoolExecutor`
- Limited to **2 concurrent threads**
- Prevents traffic bursts and IP blocking
- Thread-safe file writing using `threading.Lock`

---

## 💾 Output Files

| File Name | Description |
|---------|------------|
| `all_listings.csv` | All unique scraped listing IDs |
| `99acers_projects.csv` | Project-level data |
| `99acres_data.csv` | Property / unit-level data |
| `/logs/*.log` | Execution logs (daily rotated) |

---

## 🛡️ Anti-Bot & Evasion Techniques

- Gradual full-page scrolling
- Random scroll offsets and jitter
- Random pauses between actions
- Long cooldown after every 10 requests (2–3 minutes)
- Random User-Agent rotation (`fake_useragent`)
- Multiple API tokens & authorization headers
- Designed for Indian mobile proxy rotation

---

## 🧪 SSL & Network Handling

- API requests use `verify=False` to handle SSL and proxy handshake issues.
- SSL warnings are intentionally suppressed.

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- Google Chrome browser

### Install Dependencies

```bash
pip install selenium webdriver-manager fake-useragent requests
```

---

## ▶️ Usage

1. Configure city name in `scrap_property_listing.py`
2. Run listing scraper:
   ```bash
   python scrap_property_listing.py
   ```
3. Run data scraper:
   ```bash
   python property_data_merged.py
   ```

---

## 📊 Data Fields Captured

### Project-Level
- Project ID & Name
- Project Type
- Launch Status
- Address
- Latitude & Longitude
- Key Highlights

### Property-Level
- BHK
- Area (sqft) & area type
- Pricing details
- Possession date
- Floor plan & site plan URLs
- Seller details

---

## ⚠️ Disclaimer

This project is intended for **educational and research purposes only**.  
Scraping websites may violate their Terms of Service.  
Use responsibly and ensure legal compliance.
