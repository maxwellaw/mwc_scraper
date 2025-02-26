MWC Exhibitors Scraper & AI Categorization Pipeline
This project automates the extraction, enrichment, and categorization of exhibitor data from the MWC Barcelona website.

🚀 Features
Scrapes exhibitors from the MWC website.
Extracts details like company description, location, and interests.
Uses OpenAI GPT to classify exhibitors into Interest Categories and Business Classes.
Multi-threaded for faster scraping.
Handles API rate limits intelligently.

📂 Project Structure
📦 mwc_scrapper
 ┣ 📜 run_pipeline.py                 # Runs the whole pipeline sequentially
 ┣ 📜 mwc_list_companies.py           # Scrapes list of exhibitors
 ┣ 📜 mwc_fetch_details.py            # Extracts details from each exhibitor page
 ┣ 📜 mwc_ai_categorization.py        # Uses AI to classify exhibitors
 ┣ 📜 requirements.txt                 # Dependencies for the project
 ┣ 📜 LICENSE                          # License file
 ┣ 📜 README.md                        # Documentation

🛠️ Installation
1️⃣ Clone this repository
git clone https://github.com/maxwellaw/mwc_scraper.git
cd mwc_scraper

2️⃣ Install dependencies
Make sure you have Python installed. Then, run:
pip install -r requirements.txt

▶️ Running the Pipeline
To execute all scripts in sequence:
python run_pipeline.py
This will:
Scrape exhibitors.
Extract details (location, description, interests).
Categorize exhibitors using AI.

⚙️ Running Each Script Individually
If you want to run scripts separately:
1️⃣ Scrape Exhibitors List
python mwc_list_companies.py
This will generate mwc_exhibitors.csv.

2️⃣ Fetch Exhibitor Details
python mwc_fetch_details.py
This will enhance mwc_exhibitors.csv with descriptions, locations, and interests.

3️⃣ AI Categorization
python mwc_ai_categorization.py
This will classify exhibitors into Interest Categories and Business Classes, saving the result as mwc_exhibitors_categorized.csv.

📜 License
This project is free to use at your own responsibility. © Jorge Padrón - All rights reserved.

❓ Issues & Support
For support, open an issue on the GitHub repository.
