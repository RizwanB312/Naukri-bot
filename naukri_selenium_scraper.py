from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# === Selenium Setup ===
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Using Selenium Manager (default in selenium 4.11+), no need for webdriver_manager
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# === Google Sheets Setup ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Naukri Job Scraper").sheet1

# Add header only if sheet is empty
if len(sheet.get_all_values()) == 0:
    sheet.append_row(["Keyword", "Job Title", "Company", "Location", "Experience", "Link"])

# Get all existing links to prevent duplicates
existing_links = set(row[5] for row in sheet.get_all_values()[1:] if len(row) > 5)

# === Keywords to Search ===
keywords = [
    "python developer",
    "software developer",
    "software engineer",
    "software fresher",
    "fresher data engineer",
    "fresher testing engineer",
    "QA fresher",
    "developer fresher",
    "backend developer",
    "data analyst fresher",
    "manual testing fresher",
    "automation testing fresher",
    "Web Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "java Developer",
    "Android Developer",
    "Data Analyst",
    "Data Scientist",
    "Machine Learning",
    "AI/ML",
    "Cloud Engineer",
    "DevOps",
    "QA Tester",
    "Cyber Security"
]

def scrape_naukri(keyword):
    print(f"🔍 Searching Naukri for '{keyword}'...")
    search_url = f"https://www.naukri.com/{keyword.replace(' ', '-')}-jobs?k={keyword}"
    driver.get(search_url)

    try:
        job_cards = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
        )
    except:
        print(f"⚠️ No job cards found for '{keyword}'!")
        return

    print(f"🧠 Found {len(job_cards)} job cards for '{keyword}'.")

    rows = []
    for job in job_cards:
        try:
            title_elem = job.find_element(By.CLASS_NAME, "title")
            title = title_elem.text.strip()
            link = title_elem.get_attribute("href")
        except:
            title, link = "N/A", "N/A"

        try:
            company_elem = job.find_element(By.CLASS_NAME, "comp-name")
            company = company_elem.text.strip()
        except:
            company = "N/A"

        try:
            location_elems = job.find_elements(By.CLASS_NAME, "locWdth")
            location = ", ".join([loc.text.strip() for loc in location_elems if loc.text.strip()]) or "N/A"
        except:
            location = "N/A"

        try:
            experience_elem = job.find_element(By.CLASS_NAME, "expwdth")
            experience = experience_elem.text.strip()
        except:
            experience = "N/A"

        # === Only add if not duplicate AND fresher jobs (0 years) ===
        if (
            link not in existing_links
            and link != "N/A"
            and experience != "N/A"
            and re.match(r"^0\s*[-–]?\s*\d*", experience)
        ):
            rows.append([keyword, title, company, location, experience, link])
            existing_links.add(link)

    if rows:
        try:
            sheet.append_rows(rows, value_input_option="USER_ENTERED")
            print(f"✅ {len(rows)} new jobs added to sheet for '{keyword}'.")
        except Exception as e:
            print(f"❌ Error appending rows for '{keyword}': {e}")
    else:
        print(f"ℹ️ No new fresher jobs for '{keyword}'.")

# === Main Loop ===
for kw in keywords:
    scrape_naukri(kw)
    sleep(1)
    print("🟩 Done with keyword:", kw)

print("🛑 Quitting Chrome...")
driver.quit()
print("✅ All jobs scraped and saved to Google Sheets!")
