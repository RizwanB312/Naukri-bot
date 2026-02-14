# Naukri Job Scraper & Auto Apply Bot

## Overview
Automation tool that scrapes job listings and automatically applies to eligible internal postings while skipping external redirect links. Built to reduce manual job search and application effort.

## Features
- Automated login
- Job scraping
- Keyword filtering
- Internal apply automation
- External link skipping
- Duplicate detection
- Configurable filters
- Rate limiting delays

## Tech Stack
- Python
- Selenium
- DOM parsing
- Browser automation

## Execution Flow
1. Start browser session
2. Login
3. Search jobs
4. Scrape listings
5. Filter by rules
6. Apply to internal postings
7. Skip externals
8. Log results

## Configuration
Edit config/search_rules.json

{
  "keywords": ["python", "automation"],
  "experience": "0-3",
  "location": "Bangalore",
  "max_apply": 25
}

## How To Run
pip install -r requirements.txt
python bot/main_bot.py

## Required Setup
- Install browser driver
- Set credentials via environment variables

export NAUKRI_USER=your_email
export NAUKRI_PASS=your_password

## Output
logs/applied_jobs.log contains applied job IDs.

## Safeguards
- Internal apply only
- Duplicate prevention
- Delay between actions

## Limitations
- DOM changes can break selectors
- CAPTCHA may block runs

## Future Improvements
- Headless mode
- Dashboard tracking
- Multi-site support

## Author
Rizwan N
