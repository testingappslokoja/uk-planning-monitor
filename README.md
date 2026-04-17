# UK Planning Application Monitor

Automated scraper that monitors UK council planning portals and alerts you to relevant applications.

## Features

- Scrapes planning applications from multiple UK councils (Idox Public Access)
- Filters by keywords (extension, loft, conversion, new build, garage)
- Daily automated checks via scheduler
- Alerts saved to JSON file (email can be enabled later)
- JSON-based local storage (no database setup required)
- Modular design - easy to add new councils

## Quick Start

### 1. Install Python

```bash
python --version
```
Requires Python 3.10+

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure (Optional)

By default, alerts are saved to `data/alerts.json`. To enable email notifications later, edit `config.py`:

```python
EMAIL = {
    "enabled": True,  # Set to True to enable email
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,
    "smtp_user": "your-email@gmail.com",
    "smtp_password": "your-app-password",
    "from_email": "your-email@gmail.com",
    "to_email": "destination@example.com",
}
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)

### 4. Run

```bash
# Run once
python main.py

# Run scheduled (daily at 8am)
python main.py --schedule
```

### 5. Running Daily (Windows)

**Option A: Built-in Scheduler**
```bash
python main.py --schedule
```
The scraper will run daily at 8:00 AM. Press `Ctrl+C` to stop.

**Option B: Windows Task Scheduler**
1. Open Task Scheduler (taskschd.msc)
2. Create Basic Task → Name: "UK Planning Monitor"
3. Trigger: Daily → Set time (e.g., 8:00 AM)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\main.py`
7. Start in: `C:\path\to\upwork`

**Option C: Run on Startup (with delay)**
Add to Windows Startup folder to run when you log in.

### 6. Check Results

```bash
type data\alerts.json
```

## Project Structure

```
├── config.py              # Configuration (councils, keywords, email)
├── main.py                # Main runner + scheduler
├── scrapers/
│   ├── base.py            # Base scraper class
│   ├── westminster.py     # Westminster scraper
│   ├── blackpool.py       # Blackpool scraper
│   └── tendring.py        # Tendring scraper
├── filter.py              # Keyword matching
├── notify.py              # Alerts (saves to JSON or sends email)
├── data/
│   ├── cache.json         # Last scraped applications
│   ├── history.json       # Alert history
│   ├── alerts.json        # Latest matched applications
│   └── errors.log         # Error logs
└── requirements.txt       # Python dependencies
```

## Configuration

### Councils

Currently configured:
- Westminster City Council
- Blackpool Council
- Tendring District Council

Enable/disable in `config.py`:
```python
COUNCILS = {
    "westminster": {
        "enabled": True,  # Set to False to disable
        ...
    },
}
```

### Keywords

Default keywords in `config.py`:
```python
KEYWORDS = [
    "extension",
    "loft",
    "conversion",
    "new build",
    "garage",
]
```

### Schedule

Default: Daily at 8:00 AM (London timezone)

Customize in `config.py`:
```python
SCHEDULE = {
    "enabled": True,
    "time": time(9, 0),  # 9:00 AM
    "timezone": "Europe/London",
}
```

## Adding New Councils

1. Create new file in `scrapers/`, e.g., `scrapers/bromley.py`
2. Inherit from `BaseScraper`
3. Implement `get_applications()` method

```python
from scrapers.base import BaseScraper

class BromleyScraper(BaseScraper):
    def __init__(self):
        super().__init__("bromley", {
            "name": "Bromley Council",
            "base_url": "https://idoxpa.bromley.gov.uk",
            "search_url": "https://idoxpa.bromley.gov.uk/online-applications/search.do",
        })

    def get_applications(self, days_back: int = 7) -> List[Dict]:
        # Your scraping logic here
        ...
```

4. Register in `main.py`:
```python
SCRAPERS = {
    "westminster": WestminsterScraper,
    ...
    "bromley": BromleyScraper,
}
```

5. Add to `config.py`:
```python
COUNCILS = {
    ...
    "bromley": {
        "name": "Bromley Council",
        "enabled": True,
        ...
    },
}
```

## Alerts

When new matching applications are found, they are saved to `data/alerts.json`. Each alert entry contains:
- Date/time of the alert
- Count of matched applications
- List of all matched applications with reference, address, description, date, keyword, and link

View alerts with:
```bash
type data\alerts.json
# or on Mac/Linux
cat data/alerts.json
```

## Troubleshooting

### No Data Found

- Check website availability manually
- Website structure may have changed - check the HTML
- Try increasing `REQUEST_DELAY` in `config.py`

### View Logs

Check `data/errors.log` for detailed error messages.

## License

MIT