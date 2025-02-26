import pandas as pd
import time
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="") #INSERT YOUR TOKEN

# Define Interest Categories
interest_categories = [
    # 5G & IoT Communications
    "5G Communications for IoT",
    "Multiconnectivity and FRMCS",
    "Vehicle-to-Everything (V2X) Communications",
    "Digital Passenger Experience"]

# Define Business Classes
business_classes = [
    "Service Provider",
    "Sensor Provider",
    "System Integrator",
    "Research Center",
    "Telecom Equipment Vendor",
    "Software Solution Provider",
    "Semiconductor/Chipset Manufacturer",
    "Test & Measurement Solution Provider",
    "IoT Connectivity Provider",
    "Private Network Solution Provider",
    "Cybersecurity Provider",
    "Edge Computing Provider",
    "Satellite Communication Provider",
    "Virtualization & Cloud Provider",
    "AI & Data Analytics Provider"
]

# Function to classify company based on description & interests
def classify_company(info_text, company_interests):
    """Classifies a company into both interest categories and business classes using OpenAI while handling rate limits."""
    
    if pd.isna(info_text) and pd.isna(company_interests):
        return "No Information", "No Classification"
    
    # Combine description and interests into a single text block
    info_text = info_text if isinstance(info_text, str) else ""
    interests_text = company_interests if isinstance(company_interests, str) else ""
    
    combined_text = f"Description: {info_text}\nInterests: {interests_text}"
    
    prompt = f"""
    You are an AI that categorizes companies into two dimensions:
    1️⃣ **Interest Categories**: These are technology-based focus areas where the company operates.
    2️⃣ **Business Classes**: These represent the type of company (e.g., Service Provider, System Integrator).
    
    Given the following company information, classify it into one or more of these **Interest Categories**:
    {', '.join(interest_categories)}
    
    Also, classify it into one or more of these **Business Classes**:
    {', '.join(business_classes)}
    
    - If multiple categories apply, return them as a **comma-separated list**.
    - If none apply, return "Other".
    
    **Company Information**:
    "{combined_text}"

    **Output Format**:
    - Interest Categories: <Comma-separated categories>
    - Business Classes: <Comma-separated classes>
    """

    max_retries = 5
    retry_delay = 5  # Start with a 5-second delay

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3
            )
            
            classification = response.choices[0].message.content.strip()
            
            # Extract Interest Categories & Business Classes
            interest_result = "Interest Categories:" in classification
            class_result = "Business Classes:" in classification

            if interest_result and class_result:
                interest_part = classification.split("Interest Categories:")[1].split("Business Classes:")[0].strip()
                class_part = classification.split("Business Classes:")[1].strip()
            else:
                interest_part = "Other"
                class_part = "Other"

            # Ensure valid categories are selected
            selected_interests = [
                category for category in interest_part.split(", ")
                if category in interest_categories
            ]

            selected_classes = [
                class_name for class_name in class_part.split(", ")
                if class_name in business_classes
            ]

            interest_output = ", ".join(selected_interests) if selected_interests else "Other"
            class_output = ", ".join(selected_classes) if selected_classes else "Other"

            return interest_output, class_output

        except Exception as e:
            error_msg = str(e)
            if "rate_limit_exceeded" in error_msg:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"⚠️ Rate limit hit! Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Error processing: {e}")
                return "Error", "Error"
    
    return "Failed after retries", "Failed after retries"

# Load the CSV file
csv_file = "mwc_exhibitors.csv"
df = pd.read_csv(csv_file)

# Ensure column names are correct
df.columns = [col.strip() for col in df.columns]  # Trim spaces from column names

# Ensure required columns exist
if "Company Info" not in df.columns or "Interests" not in df.columns:
    print("Error: Required columns not found in CSV. Check column names.")
    print("Available columns:", df.columns)
    exit()

# Process each company sequentially
for index, row in df.iterrows():
    print(f"Processing: {row['Company Name']} ({index + 1}/{len(df)})")
    
    interest_category, business_class = classify_company(row["Company Info"], row["Interests"])
    
    df.at[index, "Interest Categories"] = interest_category
    df.at[index, "Business Class"] = business_class
    
    # Add a small delay between requests to avoid hitting the rate limit
    time.sleep(2)  # Adjust this if needed

# Save the updated CSV with categories
output_file = "mwc_exhibitors.csv"
df.to_csv(output_file, index=False)

print(f"✅ Categorization complete! Data saved to {output_file}")
