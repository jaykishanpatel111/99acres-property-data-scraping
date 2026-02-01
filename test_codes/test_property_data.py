import requests
from bs4 import BeautifulSoup
import json
import re
import csv
import os
from typing import Dict, Any
from fake_useragent import UserAgent


def get_random_user_agent():
    """
    Generates a random user agent string using the fake_useragent library.
    """
    ua = UserAgent()
    return ua.random
# --------------------------------------------------
# 1️⃣ Scraper / API Call
# --------------------------------------------------
def call_API(url: str) -> str:
    """
    Fully functional 99acres property scraper (requests-based).
    """
    user_agent = get_random_user_agent()
    payload = {}
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1',
    'if-none-match': 'W/"a6005-ZjAUJ6UqcAVkoD/Ia9vK1KAzt6Y"',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    # 'Cookie': '99_ab=29; GOOGLE_SEARCH_ID=4084631769856564402; xAB=SuperControlGroup%3D17%3AN%2CtopMatchHandlingAB%3D66%3AD%2CBFdataremoval%3D29%3AY%2CseamlessLogin%3D56%3AY%2CEMAILOPTIONAL%3D48%3AY%2CMLSEARCHSRP%3D1%3AY%2CDSSimilarProperties%3D87%3AY%2CshowInhousePlayer%3D38%3AD%2CIATABSVF%3D36%3AD%2CVSRAlgoDemandShaping%3D88%3AY%2CBUILDERFLOORSRP%3D99%3AN%2CMLSEARCHMONET%3D78%3AY%2CNEARBYSRP%3D31%3AY%2CppfTemplatePostingV2%3D48%3AY%2CbrokerSupplyRef%3D40%3AY%2CownerEmailOptional%3D3%3AY%2CppfCommSoftPosting%3D51%3AN; session_source=DIRECT; landmark_toast=true; _gcl_au=1.1.349653589.1769856570; _gid=GA1.2.649331308.1769856571; _fbp=fb.1.1769856570831.879743020712544429; _clck=1yly54u%5E2%5Eg36%5E0%5E2222; showCookieBanner=1; _hjSessionUser_3171461=eyJpZCI6IjlmNzI5MTZkLTUwMTMtNTVjNC1iMmQzLTZhMTkxOGYzNGFhYiIsImNyZWF0ZWQiOjE3Njk4NTY1NzEwMTksImV4aXN0aW5nIjp0cnVlfQ==; 99_ab=29; acceptedMobileDsiclaimer=true; hp_bcf_data=; _hjSession_3171461=eyJpZCI6IjBmZWM5ZDM4LWEwZTktNGY3My1iZWYyLWJhZjgyYWI2ZjFiOCIsImMiOjE3Njk4OTMyODc3NjcsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; CPN=/4-bhk-bedroom-independent-house-villa-for-sale-in-heritage-villa-76-kasindra-ahmedabad-south-3798-sq-ft-npspid-S87884256; sessionno=11; session30m=eyJ0b2tlbklkIjoiMWZiZjEyOGYtNTU2Yy00YmNiLTlhNjAtNjQ4MDM2NmEyYmU0IiwiaXNzdWVEYXRlIjoxNzY5ODk1NTM3NDM3fQ; _sess_id=QJp7rZLVDuTmZxk1xcmJuON5cuVMNchpKs7BM6POpQ5eImBNoJipYqYneLZmueoXApnP7MTfnT7Vh11iOYkvaQ%3D%3D; _ga=GA1.1.477790739.1769856571; _ga_9QHC0XEKPS=GS2.1.s1769895558$o6$g1$t1769896413$j40$l0$h0; _uetsid=85d4df90fe9211f0b03a6d756b7dcf35; _uetvid=85d55230fe9211f08d2da945ba1deab4; _clsk=90czva%5E1769896415033%5E7%5E0%5Es.clarity.ms%2Fcollect; 99_ab=74; GOOGLE_SEARCH_ID=2104631769791185608; sessionno=3; xAB=SuperControlGroup%3D17%3AN%2CtopMatchHandlingAB%3D66%3AD%2CBFdataremoval%3D29%3AY%2CseamlessLogin%3D56%3AY%2CEMAILOPTIONAL%3D48%3AY%2CMLSEARCHSRP%3D1%3AY%2CDSSimilarProperties%3D87%3AY%2CshowInhousePlayer%3D38%3AD%2CIATABSVF%3D36%3AD%2CVSRAlgoDemandShaping%3D88%3AY%2CBUILDERFLOORSRP%3D99%3AN%2CMLSEARCHMONET%3D78%3AY%2CNEARBYSRP%3D31%3AY%2CppfTemplatePostingV2%3D48%3AY%2CbrokerSupplyRef%3D40%3AY%2CownerEmailOptional%3D3%3AY%2CppfCommSoftPosting%3D51%3AN'
    }

    try:
        response = requests.get(url, headers=headers, data=payload)
        response.raise_for_status()
        print(f"✅ Fetched page successfully: {response.status_code}")
        return response.text
    except Exception as e:
        print(f"❌ Error fetching page: {e}")
        return ""

# --------------------------------------------------
# 2️⃣ Extract window.__initialData__ (ROBUST FIX)
# --------------------------------------------------
def extract_initial_data(html: str) -> Dict[str, Any]:
    """
    Extracts the JSON blob from window.__initialData__ using string parsing
    instead of regex to handle nested JSON correctly.
    """
    soup = BeautifulSoup(html, "lxml")

    # Iterate over all scripts to find the one containing the data
    for script in soup.find_all("script"):
        if script.string and "window.__initialData__" in script.string:
            content = script.string.strip()
            
            # Locate the start of the JSON object
            start_marker = "window.__initialData__"
            start_index = content.find(start_marker)
            
            # Find the first '{' after the marker
            json_start = content.find("{", start_index)
            if json_start == -1:
                continue
            
            # Extract substring from the first '{' 
            json_str = content[json_start:]
            
            # Robustly find the end of the JSON object
            # We look for the last '}' in the string. 
            # This handles cases where the script ends with ';' or other code.
            json_end = json_str.rfind("}")
            if json_end == -1:
                continue
                
            json_str = json_str[:json_end+1]

            try:
                data = json.loads(json_str)
                print("✅ window.__initialData__ extracted successfully")
                return data
            except json.JSONDecodeError as e:
                print(f"⚠️ Found data block but JSON parse failed: {e}")
                continue

    raise RuntimeError("❌ window.__initialData__ not found in page HTML")

# --------------------------------------------------
# 3️⃣ Dynamically locate property node (UPDATED KEYS)
# --------------------------------------------------
def find_property_node(data: Any) -> Dict[str, Any]:
    """
    Recursively find the dictionary that represents property details.
    Updated markers to match the current 99acres JSON structure (Prop_Id, Price, etc.)
    """
    if isinstance(data, dict):
        # Keys commonly found in the main property detail node
        markers = {"Prop_Id", "Price", "Property_Type", "Building_Name"}
        
        # If at least 2 markers are present, we likely found the node
        if len(markers.intersection(data.keys())) >= 2:
            return data

        for value in data.values():
            found = find_property_node(value)
            if found:
                return found
                
    elif isinstance(data, list):
        for item in data:
            found = find_property_node(item)
            if found:
                return found

    return None

# --------------------------------------------------
# 4️⃣ Parsers (UPDATED KEYS)
# --------------------------------------------------
def parse_property_details(node: dict) -> dict:
    return {
        "listing_id": node.get("Prop_Id"),
        "title": node.get("propertyTitle") or node.get("Start_Text") or node.get("title"),
        "property_type": node.get("Property_Text") or node.get("Property_Type"),
        "project_name": node.get("Building_Name"),
        "bhk": node.get("bedrooms") or node.get("Bedroom_Num"), # Adjust if specific key exists
        "bathrooms": node.get("bathrooms") or node.get("Bathroom_Num"),
        "builtup_area_sqft": node.get("builtUpArea") or node.get("Super_Area") or node.get("displayBuiltupArea"),
        "carpet_area_sqft": node.get("carpetArea") or node.get("Carpet_Area"),
        "furnishing": node.get("Furnish_Label") or node.get("furnishing"),
        "possession": node.get("Availability_Text") or node.get("availabilityStatus"),
        "posted_on": node.get("Posted_On_Label")
    }

def parse_pricing(node: dict) -> dict:
    return {
        "price": node.get("Price") or node.get("price"),
        "price_per_sqft": node.get("Price_Per_Unit_Area_Text") or node.get("pricePerUnitArea"),
        "total_price_text": node.get("Price_Text"), # Sometimes available
    }

def parse_location(node: dict) -> dict:
    return {
        "city_id": node.get("City"),
        "locality_id": node.get("localityid"),
        "address": node.get("address") or node.get("headerDescriptionAddressInfo"),
        "latitude": node.get("latitude"), # Often in a separate 'geo' node inside, but checking here
        "longitude": node.get("longitude"),
    }

def parse_nearby_places(initial_data: dict, property_node: dict) -> list:
    # Sometimes nearby places are inside the property node itself
    nearby_list = property_node.get("nearByPlacesOfInterest") or []
    
    if not nearby_list:
        # Fallback to pageData if not in property node
        page_data = initial_data.get("pageData", {})
        nearby_list = page_data.get("nearByPlacesOfInterest", [])

    results = []
    if isinstance(nearby_list, list):
        for place in nearby_list:
            if isinstance(place, dict):
                results.append({
                    "name": place.get("text") or place.get("name"),
                    "category": place.get("category"),
                    "distance": place.get("distance")
                })
    return results

# --------------------------------------------------
# 5️⃣ Build final payload
# --------------------------------------------------
def build_payload(initial_data: dict) -> dict:
    property_node = find_property_node(initial_data)

    if not property_node:
        # Fallback: Sometimes data is directly in pageData -> payload -> property
        try:
            property_node = initial_data["pageData"]["custominfo"]["payload"]["propertyDetails"]
            print("✅ Property node found via fallback path")
        except KeyError:
            pass

    if not property_node:
        raise RuntimeError("❌ Property data node not found in extracted JSON")

    print("✅ Property node detected")

    return {
        "property": parse_property_details(property_node),
        "pricing": parse_pricing(property_node),
        "location": parse_location(property_node),
        "nearby_places": parse_nearby_places(initial_data, property_node),
    }



# --------------------------------------------------
# 4️⃣ CSV Formatter & Saver
# --------------------------------------------------
def flatten_data_for_csv(payload: dict) -> dict:
    """
    Flattens the nested payload dictionary into a single-level dictionary
    suitable for writing to a CSV row.
    """
    flat = {}
    
    # Flatten Property
    for k, v in payload.get("property", {}).items():
        flat[f"property_{k}"] = v
        
    # Flatten Pricing
    for k, v in payload.get("pricing", {}).items():
        flat[f"price_{k}"] = v
        
    # Flatten Location
    for k, v in payload.get("location", {}).items():
        flat[f"loc_{k}"] = v
        
    # Flatten Images (List -> Pipe separated string)
    images = payload.get("images", [])
    flat["images_all"] = " | ".join(images) if images else ""
    
    # Flatten Nearby Places (List of Dicts -> String)
    nearby = payload.get("nearby_places", [])
    if nearby:
        # Example: "School (0.5 km) | Hospital (1.2 km)"
        flat["nearby_summary"] = " | ".join([f"{p['name']} ({p['distance']})" for p in nearby])
    else:
        flat["nearby_summary"] = ""
        
    return flat

def save_to_csv(data: dict, filename: str = "property_data.csv"):
    """
    Appends the flat data to a CSV file. Creates the file with headers 
    if it doesn't exist.
    """
    file_exists = os.path.isfile(filename)
    fieldnames = list(data.keys())
    
    try:
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
                print(f"📝 Created new file: {filename}")
            
            writer.writerow(data)
            print(f"✅ Data appended to: {filename}")
            
    except IOError as e:
        print(f"❌ Error writing to CSV: {e}")



def main():
    # Use the sample file provided in the context if you want to test offline
    # For live testing, use a real URL
    url = "https://www.99acres.com/3-bhk-bedroom-apartment-flat-for-sale-in-dev-the-galaxy-shela-ahmedabad-west-2010-sq-ft-npspid-S87884256"
    
    # 1. Try to fetch from URL
    html = call_API(url)
    
    if not html:
        print("⚠️ Failed to fetch live URL, checking for local file...")
        try:
            with open("sample_property_page.html", "r", encoding="utf-8") as f:
                html = f.read()
            print("✅ Loaded local HTML file")
        except FileNotFoundError:
            print("❌ No local file found.")
            return

    # 2. Extract Data
    try:
        initial_data = extract_initial_data(html)
        payload = build_payload(initial_data)

        # 2. Flatten for CSV
        flat_data = flatten_data_for_csv(payload)
        
        # 3. Save
        save_to_csv(flat_data, "99acres_data.csv")
        
        # Optional: Print preview
        print("\n👀 Preview of captured data:")
        print(f"Title: {flat_data.get('property_title')}")
        print(f"Price: {flat_data.get('price_total_price_text')}")
        
    except RuntimeError as e:
        print(e)

if __name__ == "__main__":
   main()