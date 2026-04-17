import json
import logging
import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List

from apscheduler.schedulers.blocking import BlockingScheduler

import config
from scrapers.westminster import WestminsterScraper
from scrapers.blackpool import BlackpoolScraper
from scrapers.tendring import TendringScraper
from filter import filter_applications
from notify import send_email_alert


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.ERROR_LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


SCRAPERS = {
    "westminster": WestminsterScraper,
    "blackpool": BlackpoolScraper,
    "tendring": TendringScraper,
}


def load_cache() -> Dict:
    if os.path.exists(config.CACHE_FILE):
        try:
            with open(config.CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
    return {}


def save_cache(cache: Dict) -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    try:
        with open(config.CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")


def load_history() -> List[Dict]:
    if os.path.exists(config.HISTORY_FILE):
        try:
            with open(config.HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load history: {e}")
    return []


def save_history(history: List[Dict]) -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    try:
        with open(config.HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save history: {e}")


def run_scraper() -> List[Dict]:
    logger.info("Starting scraper run...")
    all_new_matches = []
    cache = load_cache()
    history = load_history()

    for council_id, council_config in config.COUNCILS.items():
        if not council_config.get("enabled", True):
            continue

        scraper_class = SCRAPERS.get(council_id)
        if not scraper_class:
            logger.warning(f"No scraper found for {council_id}")
            continue

        try:
            scraper = scraper_class()
            applications = scraper.get_applications(days_back=7)
            logger.info(f"{council_id}: Found {len(applications)} applications")

            cache_key = f"council_{council_id}"
            previous_refs = set(cache.get(cache_key, {}).get("references", []))
            
            new_apps = [app for app in applications if app.get("reference") not in previous_refs]
            
            if new_apps:
                cache[cache_key] = {
                    "references": [app.get("reference") for app in applications],
                    "last_updated": datetime.now().isoformat()
                }

            matched = filter_applications(new_apps)
            logger.info(f"{council_id}: {len(matched)} new matches")
            all_new_matches.extend(matched)

        except Exception as e:
            logger.error(f"Failed to scrape {council_id}: {e}")

    save_cache(cache)

    if all_new_matches:
        history.append({
            "date": datetime.now().isoformat(),
            "count": len(all_new_matches),
            "applications": all_new_matches
        })
        save_history(history[-100:])

    if all_new_matches and config.EMAIL["enabled"]:
        send_email_alert(all_new_matches)

    logger.info(f"Scraper run complete. {len(all_new_matches)} new matches")
    return all_new_matches


def main():
    parser = argparse.ArgumentParser(description="UK Planning Application Monitor")
    parser.add_argument("--schedule", action="store_true", help="Run on schedule")
    parser.add_argument("--hour", type=int, help="Hour to run scheduled job (0-23)")
    args = parser.parse_args()

    if args.schedule:
        scheduler = BlockingScheduler()
        hour = args.hour if args.hour is not None else config.SCHEDULE["time"].hour
        scheduler.add_job(
            run_scraper,
            "cron",
            hour=hour,
            minute=config.SCHEDULE["time"].minute,
            timezone=config.SCHEDULE["timezone"]
        )
        logger.info(f"Scheduler started. Running daily at {hour:02d}:{config.SCHEDULE['time'].minute:02d}")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")
    else:
        run_scraper()


if __name__ == "__main__":
    main()