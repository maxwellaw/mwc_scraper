import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import threading

# Load the CSV file
df = pd.read_csv("mwc_exhibitors.csv")

# Maximum number of threads (adjust for your system)
MAX_THREADS = 4
RETRY_LIMIT = 3

# **Global Thread-Local Storage for WebDriver**
thread_local = threading.local()

def get_driver():
    """Ensure each thread has its own WebDriver instance."""
    if not hasattr(thread_local, "driver"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        thread_local.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    return thread_local.driver

def scrape_company(row):
    """Scrape information, location, and interests for a given company."""
    company_name = row["Company Name"]
    profile_link = row["Profile Link"]

    print(f"🔍 Scraping: {company_name}")

    for attempt in range(RETRY_LIMIT):
        try:
            driver = get_driver()  # Use thread-local WebDriver
            driver.get(profile_link)
            time.sleep(random.uniform(2, 4))  # Randomized delay to prevent blocking

            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "maincontent"))
            )

            # Parse HTML
            soup = BeautifulSoup(driver.page_source, "html.parser")

            # **Extract Company Information**
            main_content = soup.find(id="maincontent")
            company_info_section = main_content.find(class_="wysiwyg") if main_content else None
            company_info_text = company_info_section.get_text(" ", strip=True) if company_info_section else "N/A"

            # **Extract Location**
            location_section = soup.select_one(".flex.flex-col.gap-2 a")
            location_text = location_section.get_text(strip=True) if location_section else "N/A"

            # **Extract Interests**
            interests_section = soup.select("#exhibitor-container li.px-4.py-1.text-xs.no-underline.bg-gray-100.border.border-gray-300.rounded-full")
            interests = [interest.get_text(strip=True) for interest in interests_section]
            interests_text = ", ".join(interests) if interests else "N/A"

            print(f"✅ {company_name} → Info: {company_info_text[:50]}... | Location: {location_text} | Interests: {interests_text}")

            return {
                "Company Name": company_name,
                "Profile Link": profile_link,
                "Company Info": company_info_text,
                "Location": location_text,
                "Interests": interests_text
            }

        except Exception as e:
            print(f"⚠️ Retry {attempt + 1}/{RETRY_LIMIT} failed for {company_name}: {e}")

    print(f"❌ {company_name} → Failed after {RETRY_LIMIT} retries.")
    return {
        "Company Name": company_name,
        "Profile Link": profile_link,
        "Company Info": "FAILED",
        "Location": "FAILED",
        "Interests": "FAILED"
    }

# **Threaded Execution**
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(scrape_company, row) for _, row in df.iterrows()]

    for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
        results.append(future.result())

        # **Incremental Saving Every 50 Companies**
        if i % 50 == 0:
            pd.DataFrame(results).to_csv("mwc_exhibitors_enriched_partial.csv", index=False)
            print(f"💾 Progress saved ({i} companies processed).")

# **Final Save**
pd.DataFrame(results).to_csv("mwc_exhibitors.csv", index=False)

print("\n✅ Data saved to mwc_exhibitors.csv")
