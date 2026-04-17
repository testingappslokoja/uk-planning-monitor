import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class BlackpoolScraper(BaseScraper):
    def __init__(self):
        super().__init__("blackpool", {
            "name": "Blackpool Council",
            "base_url": "https://idoxpa.blackpool.gov.uk",
            "search_url": "https://idoxpa.blackpool.gov.uk/online-applications/search.do",
            "weekly_url": "https://idoxpa.blackpool.gov.uk/online-applications/search.do?action=weeklyList&searchType=Application",
            "results_url": "https://idoxpa.blackpool.gov.uk/online-applications/weeklyListResults.do?action=firstPage",
        })

    def get_applications(self, days_back: int = 7) -> List[Dict]:
        applications = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        try:
            soup = self.fetch(self.council_config["weekly_url"])
            if not soup:
                self.logger.error("Failed to fetch Blackpool weekly list page")
                return applications

            form = soup.find("form")
            if not form:
                self.logger.error("No form found on Blackpool weekly list page")
                return applications

            csrf = form.find("input", {"name": "_csrf"})
            if not csrf:
                self.logger.error("No CSRF token found")
                return applications

            week_select = form.find("select", {"name": "week"})
            if not week_select:
                self.logger.error("No week select found")
                return applications

            week_options = week_select.find_all("option")
            if not week_options:
                self.logger.error("No week options found")
                return applications

            first_week = week_options[0]["value"]

            results_soup = self.fetch(
                self.council_config["results_url"],
                data={
                    "_csrf": csrf["value"],
                    "dateType": "DC_Validated",
                    "searchType": "Application",
                    "week": first_week,
                }
            )

            if not results_soup:
                self.logger.error("Failed to fetch Blackpool results")
                return applications

            results = results_soup.find_all(class_="searchresult")
            self.logger.info(f"Found {len(results)} applications on Blackpool page")

            for item in results:
                app = self._parse_result(item)
                if app:
                    try:
                        received_date = datetime.strptime(app.get("received_date", "2000-01-01"), "%Y-%m-%d")
                        if received_date >= cutoff_date:
                            applications.append(app)
                    except (ValueError, TypeError):
                        applications.append(app)

        except Exception as e:
            self.logger.error(f"Error scraping Blackpool: {e}")

        return applications

    def _parse_result(self, item: BeautifulSoup) -> Dict:
        text = item.get_text(strip=True)

        ref_match = re.search(r"Ref\.?\s*No:?\s*([\d/]+)", text, re.I)
        ref = ref_match.group(1) if ref_match else ""

        desc = text.split("Ref. No")[0].strip() if "Ref. No" in text else text[:200]

        link = item.find("a")
        href = link.get("href", "") if link else ""
        detail_url = urljoin(self.council_config["base_url"], href) if href else ""

        received_match = re.search(r"Received:\s*(\d{1,2}\s+\w+\s+\d{4})", text, re.I)
        received_date = ""
        if received_match:
            parsed = self.parse_date(received_match.group(1))
            if parsed:
                received_date = parsed

        address_match = re.search(r"([A-Z][A-Z0-9\s]+(?:ROAD|STREET|AVENUE|CLOSE|WAY|DRIVE|PLACE|LANE|GARDENS|CRESCENT|WALK|ROW|ST|AVE|RD|DR|PL)[,\s]*[A-Z]?\s*\d[A-Z]{0,2}.*)", text, re.I)
        address = address_match.group(1).split("Ref. No")[0].strip() if address_match else ""

        return {
            "reference": ref,
            "address": address,
            "description": desc[:200],
            "received_date": received_date,
            "status": "Pending",
            "council": self.council_config["name"],
            "url": detail_url,
            "scrape_date": datetime.now().isoformat(),
        }