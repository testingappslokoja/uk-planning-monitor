import logging
from datetime import datetime, timedelta
from typing import List, Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class TendringScraper(BaseScraper):
    def __init__(self):
        super().__init__("tendring", {
            "name": "Tendring District Council",
            "base_url": "https://idox.tendringdc.gov.uk",
            "search_url": "https://idox.tendringdc.gov.uk/online-applications/search.do",
        })

    def get_applications(self, days_back: int = 7) -> List[Dict]:
        applications = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        params = {
            "searchType": "application",
            "search": "WeeklyList",
            "weeks": "1",
        }

        soup = self.fetch(self.council_config["search_url"], params)
        if not soup:
            self.logger.error("Failed to fetch Tendring applications")
            return applications

        results = soup.find_all("tr", class_=lambda x: x and "row" in x.lower())
        self.logger.info(f"Found {len(results)} results on Tendring page")

        for row in results:
            try:
                app = self._parse_row(row)
                if app:
                    received_date = datetime.strptime(app.get("received_date", "2000-01-01"), "%Y-%m-%d")
                    if received_date >= cutoff_date:
                        applications.append(app)
            except Exception as e:
                self.logger.warning(f"Failed to parse row: {e}")
                continue

        return applications

    def _parse_row(self, row: BeautifulSoup) -> Dict:
        cells = row.find_all("td")
        if len(cells) < 5:
            return None

        reference = self.clean_text(cells[0].get_text())
        link_elem = cells[0].find("a")
        detail_url = ""
        if link_elem and link_elem.get("href"):
            detail_url = urljoin(self.council_config["base_url"], link_elem["href"])

        address = self.clean_text(cells[1].get_text())
        received_date = self.parse_date(cells[2].get_text())
        status = self.clean_text(cells[3].get_text())

        description = ""
        if len(cells) > 4:
            desc_elem = cells[4].find("span", class_="description")
            if desc_elem:
                description = self.clean_text(desc_elem.get_text())
            else:
                description = self.clean_text(cells[4].get_text())

        return {
            "reference": reference,
            "address": address,
            "description": description,
            "received_date": received_date or "",
            "status": status,
            "council": self.council_config["name"],
            "url": detail_url,
            "scrape_date": datetime.now().isoformat(),
        }