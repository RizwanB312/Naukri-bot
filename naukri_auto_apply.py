import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from dotenv import load_dotenv
from urllib.parse import urlparse

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
load_dotenv()
NAUKRI_EMAIL = "rizwannowfal001@gmail.com"
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD")
RESUME_PATH = r"C:\Users\rizwa\Downloads\RIZWAN-N-Resume.pdf"
COVER_LETTER = """
Rizwan Nowfal
Kollam, Kerala, India
rizwannowfal001@gmail.com | 7907075183
August 21, 2025

Dear Hiring Manager,

I am writing to express my sincere interest in job opportunities at your esteemed organization that align with my educational background and technical skills. As a dedicated Computer Science and Engineering graduate with hands-on experience in software development, web technologies, and artificial intelligence, I am excited about the possibility of contributing to your team.

During my internship at Cyberfox Solutions, I developed responsive websites, collaborated on API integrations, and worked extensively with version control tools such as Git and GitHub. Academically, I secured the top position in my graduating batch at the College of Engineering and Management Punnapra with a CGPA of 8.78.

My skill set is further enriched by specialized training programs including the AI Mastery Program by Be10x and the 30 Days of Python Bootcamp by AI for Techies. Among my notable projects are AI Guardian, an intelligent mental health chatbot leveraging NLP and machine learning, and AI Mouse, a gesture-based virtual mouse utilizing OpenCV and MediaPipe technologies. These projects demonstrate my problem-solving capabilities, programming expertise, and passion for innovative technology solutions.

I am a quick learner, adaptable, and thrive in collaborative environments. I am confident that my technical knowledge and proactive mindset will add significant value to your organization while offering me a platform for continuous growth.

Thank you for considering my application. I look forward to the opportunity for an interview and to discuss how I can contribute to your team’s success.

Sincerely,
Rizwan Nowfal
"""

# Google Sheets setup
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Naukri Job Scraper").sheet1

def get_jobs_to_apply():
    all_rows = sheet.get_all_values()
    links = []
    for row in all_rows[1:]:
        if len(row) > 5:
            url = row[5].strip()
            # Fixed here: check status column G (index 6) instead of using row.strip()
            if (url.startswith("http://") or url.startswith("https://")) and (len(row) < 7 or not row[6].strip()):
                links.append(url)
    print(f"📝 Found {len(links)} jobs to apply.")
    return links

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

def update_application_status(sheet, job_link, status):
    all_rows = sheet.get_all_values()
    for idx, row in enumerate(all_rows):
        if len(row) > 5 and row[5].strip() == job_link.strip():
            sheet.update_cell(idx + 1, 7, status)
            print(f"🔄 Updated status for {job_link} to '{status}'")
            break

def naukri_login():
    driver.get("https://login.naukri.com/nLogin/Login.php")
    wait.until(EC.presence_of_element_located((By.ID, "usernameField"))).send_keys(NAUKRI_EMAIL)
    driver.find_element(By.ID, "passwordField").send_keys(NAUKRI_PASSWORD)
    driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()
    print("✅ Logged in to Naukri.")

def is_already_applied():
    try:
        elem = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "already-applied"))
        )
        if elem and elem.text.strip().lower() == "applied":
            return True
    except:
        pass
    try:
        elem = driver.find_element(By.XPATH, "//span[contains(@class, 'already-applied') and contains(text(), 'Applied')]")
        if elem.is_displayed():
            return True
    except:
        pass
    return False

def apply_to_job(job_url):
    if not (job_url.startswith("http://") or job_url.startswith("https://")):
        print(f"❌ Skipping invalid URL: {job_url}")
        update_application_status(sheet, job_url, "Invalid URL")
        return

    driver.get(job_url)
    sleep(3)

    if is_already_applied():
        print(f"🟢 Already applied (icon/text found) for: {job_url}")
        update_application_status(sheet, job_url, "Applied")
        return

    print(f"▶️ Attempting to apply to job: {job_url}")
    try:
        original_windows = driver.window_handles

        for attempt in range(3):
            try:
                apply_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Apply')]")))
                apply_btn.click()
                print(f"👍 Clicked Apply button on attempt {attempt+1} for: {job_url}")
                break
            except Exception as e:
                print(f"⚠️ Attempt {attempt+1}/3 failed to click Apply for {job_url}: {e}")
                sleep(2)
        else:
            print(f"❌ Failed to click Apply after 3 attempts: {job_url}")
            update_application_status(sheet, job_url, "Failed")
            return

        sleep(2)

        new_windows = driver.window_handles
        if len(new_windows) > len(original_windows):
            driver.switch_to.window(new_windows[-1])
            current_domain = urlparse(driver.current_url).netloc
            if "naukri.com" not in current_domain:
                print(f"🔗 Redirected externally in new tab: {driver.current_url}. Skipping {job_url}.")
                driver.close()
                driver.switch_to.window(original_windows[0])
                update_application_status(sheet, job_url, "External Application")
                return
        else:
            current_domain = urlparse(driver.current_url).netloc
            if "naukri.com" not in current_domain:
                print(f"🔗 Redirected externally: {driver.current_url}. Skipping {job_url}.")
                update_application_status(sheet, job_url, "External Application")
                return

        sleep(2)

        try:
            inner_text = driver.execute_script("return document.body.innerText").lower()
            if any(
                phrase in inner_text for phrase in [
                    "you have successfully applied to",
                    "application submitted successfully",
                    "thank you for applying",
                    "your application has been received"
                ]
            ):
                print(f"✅ Application confirmed for: {job_url}")
                update_application_status(sheet, job_url, "Applied")
            elif is_already_applied():
                print(f"✅ Detected already-applied after redirect for: {job_url}")
                update_application_status(sheet, job_url, "Applied")
            else:
                raise Exception("No confirmation phrases detected in page text.")
        except Exception as e:
            print(f"⚠️ Application confirmation failed for: {job_url}, Error: {e}")
        #   driver.save_screenshot(f"failed_apply_{job_url.split('/')[-1]}.png")
            update_application_status(sheet, job_url, "Failed")

        all_windows = driver.window_handles
        if len(all_windows) > len(original_windows):
            driver.close()
            driver.switch_to.window(original_windows[0])

    except Exception as e:
        print(f"❌ Error during job application for {job_url}: {e}")
        update_application_status(sheet, job_url, "Skipped/Error")

def main():
    naukri_login()
    while True:
        job_links = get_jobs_to_apply()
        if not job_links:
            print("🛑 No new jobs to apply. Exiting...")
            break
        for link in job_links:
            apply_to_job(link)
            sleep(5)
        print("🔄 Waiting 60 seconds before checking for new jobs...")
        sleep(60)
    driver.quit()
    print("🎉 All jobs processed!")

if __name__ == "__main__":
    main()
