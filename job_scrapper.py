import requests
from bs4 import BeautifulSoup
import openpyxl

# Create a workbook
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Jobs"
ws.append(["Job Title", "Company", "Location", "Link"])

def scrape_internshala_jobs():
    print("Scraping Internshala...")
    url = "https://internshala.com/jobs/work-from-home-python-jobs"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = soup.find_all('div', class_='individual_internship')

    for job in jobs:
        title_tag = job.find('div', class_='heading_4_5 profile')
        company_tag = job.find('a', class_='link_display_like_text')
        location_tag = job.find('a', class_='location_link')

        title = title_tag.text.strip() if title_tag else 'N/A'
        company = company_tag.text.strip() if company_tag else 'N/A'
        location = location_tag.text.strip() if location_tag else 'N/A'
        link = "https://internshala.com" + title_tag.find('a')['href'] if title_tag else 'N/A'

        ws.append([title, company, location, link])

    wb.save("internshala_jobs.xlsx")
    print("Scraping completed. Data saved to internshala_jobs.xlsx")

# Run the scraper
if __name__ == "__main__":
    scrape_internshala_jobs()
