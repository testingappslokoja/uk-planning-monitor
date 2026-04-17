import time
import logging
import urllib3
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

import config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseScraper(ABC):
    def __init__(self, council_id: str, council_config: Dict):
        self.council_id = council_id
        self.council_config = council_config
        self.logger = logging.getLogger(f"scraper.{council_id}")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.5",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        })
        self.session.verify = False

    def fetch(self, url: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Optional[BeautifulSoup]:
        for attempt in range(config.MAX_RETRIES):
            try:
                time.sleep(config.REQUEST_DELAY)
                if data:
                    response = self.session.post(
                        url,
                        data=data,
                        timeout=config.REQUEST_TIMEOUT
                    )
                else:
                    response = self.session.get(
                        url,
                        params=params,
                        timeout=config.REQUEST_TIMEOUT
                    )
                response.raise_for_status()
                return BeautifulSoup(response.content, "lxml")
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == config.MAX_RETRIES - 1:
                    self.logger.error(f"Failed to fetch {url} after {config.MAX_RETRIES} attempts")
                    return None
                time.sleep(2 ** attempt)
        return None

    @abstractmethod
    def get_applications(self, days_back: int = 7) -> List[Dict]:
        pass

    def parse_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        date_str = date_str.strip()
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        return " ".join(text.split()).strip()