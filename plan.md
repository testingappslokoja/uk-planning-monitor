# Implementation Plan

## Phase 1: Core Infrastructure (Completed)

### 1.1 Project Setup
- [x] Create directory structure (`scrapers/`, `data/`, `docs/`)
- [x] Create `requirements.txt` with dependencies
- [x] Install Python dependencies

### 1.2 Base Scraper Framework
- [x] `scrapers/base.py` - abstract base class with common methods
- [x] Request handling with retry logic and delays
- [x] Session management with proper headers
- [x] Date parsing and text cleaning utilities

## Phase 2: Council Scrapers (In Progress)

### 2.1 Blackpool Scraper ✓
- [x] POST-based weekly list form submission
- [x] CSRF token handling
- [x] Parse `searchresult` class elements
- [x] Extract: reference, description, address, URL
- Tested and working (found 5 apps, 2 matches)

### 2.2 Westminster Scraper
- [ ] Need to identify working endpoint (currently returns 500 errors)
- [ ] Requires similar POST-based form submission

### 2.3 Tendring Scraper
- [ ] SSL certificate issues on this portal
- [ ] May need different approach or skip

### 2.4 Adding New Councils
The framework is modular - to add a new council:
1. Create new scraper in `scrapers/` inheriting from `BaseScraper`
2. Implement `get_applications()` method
3. Add to `config.py`
4. Register in `main.py`

## Phase 3: Filter & Storage (Completed)

### 3.1 Filter Engine
- [x] Keyword matching in description + address
- [x] Case-insensitive matching
- [x] Configurable keywords in `config.py`
- [x] Returns matched keyword for each application

### 3.2 JSON Storage
- [x] `data/cache.json` - last known applications per council
- [x] `data/history.json` - all past matches with timestamps
- [x] Prevents duplicate alerts (compares with cache)

## Phase 4: Notifications (Completed)

### 4.1 Email Notifier
- [x] SMTP configuration in `config.py`
- [x] HTML-formatted email with application details
- [x] Includes direct links to application pages

### 4.2 Error Handling
- [x] Logging to `data/errors.log`
- [x] Graceful error handling per council

## Phase 5: Scheduling (Completed)

### 5.1 Scheduler Integration
- [x] APScheduler for cross-platform scheduling
- [x] Default: daily at 8:00 AM (London timezone)
- [x] Configurable in `config.py`

### 5.2 CLI Options
- [x] `python main.py` - run once
- [x] `python main.py --schedule` - run scheduled
- [x] `python main.py --hour=14` - custom time

## Phase 6: Documentation (Completed)

### 6.1 README.md
- [x] Installation instructions
- [x] Configuration guide
- [x] Usage examples
- [x] Adding new councils guide
- [x] Troubleshooting section

## Phase 7: Future Improvements

### 7.1 Additional Councils
When adding new councils, check:
- Idox Public Access portals use similar structure
- May require POST form submission with CSRF
- Check for weekly list endpoint

### 7.2 Enhancements
- Add more specific address parsing
- Extract more application details from detail pages
- Add status field (pending/decided)
- Consider adding Selenium for JS-heavy pages

## Technical Notes

### Rate Limiting
- 2 second delay between requests (configurable)
- 3 retry attempts with exponential backoff
- User-Agent header to identify scraper

### Data Model
```python
{
    "reference": str,       # e.g., "26/0207"
    "address": str,
    "description": str,
    "received_date": str,   # ISO format (YYYY-MM-DD)
    "status": str,
    "council": str,
    "url": str,
    "scrape_date": str,     # ISO timestamp
    "matched_keyword": str  # Added by filter
}
```

### Alert Logic
1. Fetch current applications from council
2. Compare with cache (by reference)
3. New items → filter by keywords → if match → send alert
4. Update cache

## Current Status

Working: Blackpool scraper
- Found 5 applications in latest run
- 2 matched keywords (extension)
- Email not configured yet (pending user setup)