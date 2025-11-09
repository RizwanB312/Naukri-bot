import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Naukri Job Scraper").sheet1

# Clear all contents
sheet.clear()
print("✅ Sheet cleared!")

# Optionally, add header row back
sheet.append_row(["Keyword", "Job Title", "Company", "Location", "Experience", "Link"])
print("✅ Header row added!")
