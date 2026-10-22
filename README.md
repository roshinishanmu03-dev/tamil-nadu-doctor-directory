# Tamil Nadu Doctor Directory — Scrapy + Beautiful Soup

Collect **only publicly displayed, permitted** doctor/clinic directory information from an approved listing page and save it in CSV or JSON format. The spider obeys robots rules, uses one request at a time, and never bypasses a CAPTCHA, login, rate limit, or bot-protection system.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Use only an authorized public listing URL:

```bash
scrapy crawl doctors -a start_url='PASTE_PERMITTED_LISTING_URL_HERE' -a max_pages=1 -O tamil_nadu_doctors.csv
```

The output contains public JSON-LD fields when available: name, specialty, locality, region, postal code, rating, review count, source URL, and timestamp. Website markup can change; an empty result is a valid result and should be documented rather than worked around.