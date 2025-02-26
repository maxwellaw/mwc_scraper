from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# List of available interest filters
INTEREST_OPTIONS = {
    "5G/6G": 30, "AGRITECH AND AGRIFOOD": 5, "APP/MOBILE SERVICES": 20, "ARTIFICIAL INTELLIGENCE": 25,
    "AUTOMOTIVE/TRANSPORT": 15, "BIG DATA/ANALYTICS": 18, "CLIMATE/ENVIRONMENT/SUSTAINABILITY": 10,
    "CLOUD SERVICES": 22, "CONSULTANCY": 8, "CYBERSECURITY": 17, "DIGITAL IDENTITY/AUTHENTICATION": 14,
    "DIGITAL MARKETING/ADTECH": 9, "E-COMMERCE": 12, "EDUCATION": 7, "ENTERPRISE SOLUTIONS": 16,
    "eSIM/SIM": 13, "FINTECH/FINANCE/INSURANCE SERVICES": 20, "GAMING": 6, "GOVERNMENT/PUBLIC POLICY": 8,
    "HEALTH/FITNESS/WELLBEING": 11, "IMPACT/SOCIAL INNOVATION": 10, "IOT": 28,
    "MANUFACTURING AND INDUSTRY 4.0": 14, "MEDIA/CONTENT/ENTERTAINMENT": 12,
    "METAVERSE/VIRTUAL REALITY/AUGMENTED REALITY": 9, "MNO/MVNO": 8,
    "MOBILE DEVICE HARDWARE": 26, "MOBILE DEVICE SOFTWARE": 21, "NETWORK INFRASTRUCTURE": 18,
    "NETWORK SECURITY": 16, "OSS/BSS": 7, "PRIVATE NETWORKS": 15, "RETAIL/DISTRIBUTION CHANNELS": 10,
    "ROAMING & INTERCONNECT": 8, "SATELLITE/NON TERRESTRIAL NETWORKS": 12, "SMART CITIES": 13,
    "SOFTWARE SERVICES": 17, "SYSTEMS INTEGRATION": 11, "USER EXPERIENCE": 9,
    "VENTURE CAPITAL/INVESTMENT/M&A": 6, "WEB3, CRYPTO AND NFTS": 7
}

# ✅ Ask the user if they want to filter by interest
print("\nDo you want to apply a filter by interest? (y/n)")
use_filter = input("> ").strip().lower() == "y"

selected_interest = None
if use_filter:
    print("\nSelect an interest filter from the list:")
    for i, interest in enumerate(INTEREST_OPTIONS.keys(), 1):
        print(f"{i}. {interest}")
    
    try:
        choice = int(input("\nEnter the number corresponding to your interest: "))
        if 1 <= choice <= len(INTEREST_OPTIONS):
            selected_interest = list(INTEREST_OPTIONS.keys())[choice - 1].replace(" ", "+").replace("/", "%2F")
            print(f"✅ Selected Interest: {selected_interest.replace('+', ' ')}")
        else:
            print("❌ Invalid choice. No filter will be applied.")
    except ValueError:
        print("❌ Invalid input. No filter will be applied.")

# ✅ Ask user for number of pages (use default if available)
if selected_interest:
    default_pages = INTEREST_OPTIONS.get(selected_interest.replace("+", " "), 10)  # Default 10 if unknown
    try:
        num_pages = int(input(f"\nEnter the number of pages to scrape (default {default_pages}): ") or default_pages)
        print(f"✅ Scraping {num_pages} pages for {selected_interest.replace('+', ' ')}")
    except ValueError:
        print(f"❌ Invalid input. Using default of {default_pages} pages.")
        num_pages = default_pages
else:
    num_pages = int(input("\nEnter the number of pages to scrape (default 30): ") or 30)
    print(f"✅ Scraping {num_pages} pages for all exhibitors.")

# ✅ Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (optional)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# ✅ Automatically install and use the correct ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# ✅ Construct base URL
base_url = "https://www.mwcbarcelona.com/exhibitors"
if selected_interest:
    base_url += f"?interests={selected_interest}"

# ✅ List to store all extracted company data
all_companies = []

# ✅ Iterate through pages based on user input
for page in range(1, num_pages + 1):
    print(f"Scraping page {page}/{num_pages}...")

    url = base_url if page == 1 else f"{base_url}&page={page}"
    driver.get(url)

    try:
        # Wait until exhibitor listing appears
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.exhibitor-listing"))
        )
        time.sleep(2)  # Allow extra time for JavaScript to load
        
        # Extract page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Select all exhibitor elements
        exhibitors = soup.select("ul.exhibitor-listing a")

        for exhibitor in exhibitors:
            company_name = exhibitor.select_one("h3").text.strip() if exhibitor.select_one("h3") else "N/A"
            profile_link = exhibitor.get("href", "No Link")
            
            # Handle missing stand info safely
            stand_div = exhibitor.select_one("div[aria-label]")
            stands = stand_div.text.strip() if stand_div else "N/A"

            # Fix comma issue in company names
            company_name = f'"{company_name}"' if "," in company_name else company_name

            # Debugging Output
            print(f"Extracted: {company_name} | {profile_link} | {stands}")

            all_companies.append({
                "Company Name": company_name,
                "Profile Link": profile_link,
                "Number of Stands": stands
            })

    except Exception as e:
        print(f"⚠️ Skipping page {page} due to error: {e}")

# ✅ Close the browser
driver.quit()

# ✅ Save results to CSV without Logo URL and fixing commas
if all_companies:
    df = pd.DataFrame(all_companies)
    df.to_csv("mwc_exhibitors.csv", index=False, quoting=1)  # Quoting ensures correct formatting
    print("\n✅ Data saved to mwc_exhibitors.csv")
else:
    print("\n⚠️ No data found.")
