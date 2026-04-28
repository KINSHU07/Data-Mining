# ============================================================
#  Web Scraping – Monthly District Rainfall Data (1901–2023)
#  Source  : https://data.gov.in
#  Dataset : Monthly Rainfall by District, India
#  Author  : [Your Name]
# ============================================================

import requests                         # sends HTTP requests to the website
from bs4 import BeautifulSoup           # parses the HTML page content
import pandas as pd                     # organises data into a table
import time                             # adds polite delay between requests

# ------------------------------------------------------------
# STEP 1 – Define the target URL
#          data.gov.in hosts government datasets as paginated
#          HTML tables; each page shows ~100 rows.
# ------------------------------------------------------------

BASE_URL  = "https://data.gov.in/resource/district-wise-monthly-rainfall-1901-2023"
HEADERS   = {"User-Agent": "Mozilla/5.0 (Research Project)"}   # identify our bot politely

# ------------------------------------------------------------
# STEP 2 – Send a GET request and load the page
# ------------------------------------------------------------

print("Connecting to data.gov.in ...")
response = requests.get(BASE_URL, headers=HEADERS)

# Check if the server responded successfully (status 200 = OK)
if response.status_code == 200:
    print(f"Connection successful! (Status: {response.status_code})")
else:
    print(f"Failed to connect. (Status: {response.status_code})")

# ------------------------------------------------------------
# STEP 3 – Parse the HTML with BeautifulSoup
# ------------------------------------------------------------

soup = BeautifulSoup(response.text, "html.parser")

# Locate the main data table on the page using its HTML tag
data_table = soup.find("table", {"class": "dataset-table"})
print(f"\nData table found: {data_table is not None}")

# ------------------------------------------------------------
# STEP 4 – Extract column headers from the first <tr> row
# ------------------------------------------------------------

headers_row = data_table.find("tr")                          # first row = header
column_names = [th.text.strip() for th in headers_row.find_all("th")]

# Expected columns after scraping:
# ['year', 'month', 'month_num', 'state', 'district',
#  'agro_zone', 'rainfall_mm', 'normal_mm', 'departure_mm',
#  'departure_pct', 'category', 'rainy_days_est']

print(f"\nColumns detected ({len(column_names)}): {column_names}")

# ------------------------------------------------------------
# STEP 5 – Loop through all rows and collect the data
# ------------------------------------------------------------

all_rows   = []
data_rows  = data_table.find_all("tr")[1:]   # skip the header row (index 0)

print(f"\nScraping {len(data_rows)} rows from the current page ...")

for row in data_rows:
    cells      = row.find_all("td")                          # each <td> is one cell
    row_values = [cell.text.strip() for cell in cells]      # clean extra whitespace
    all_rows.append(row_values)

time.sleep(1)     # wait 1 second – avoids overloading the server (good practice)

# ------------------------------------------------------------
# STEP 6 – Convert to a Pandas DataFrame for easy analysis
# ------------------------------------------------------------

rainfall_df = pd.DataFrame(all_rows, columns=column_names)

# Fix data types so numbers are stored as numbers, not text
rainfall_df["year"]          = pd.to_numeric(rainfall_df["year"])
rainfall_df["rainfall_mm"]   = pd.to_numeric(rainfall_df["rainfall_mm"])
rainfall_df["normal_mm"]     = pd.to_numeric(rainfall_df["normal_mm"])
rainfall_df["departure_pct"] = pd.to_numeric(rainfall_df["departure_pct"])

# ------------------------------------------------------------
# STEP 7 – Quick preview & save
# ------------------------------------------------------------

print("\n--- First 5 rows of scraped data ---")
print(rainfall_df.head())

print(f"\nTotal records scraped : {len(rainfall_df)}")
print(f"Years covered         : {rainfall_df['year'].min()} – {rainfall_df['year'].max()}")
print(f"States covered        : {rainfall_df['state'].nunique()}")

rainfall_df.to_csv("monthly_rainfall_district_1901_2023.csv", index=False)
print("\nData saved to → monthly_rainfall_district_1901_2023.csv")