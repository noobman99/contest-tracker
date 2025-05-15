import sqlite3
import datetime
import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

URL = "https://atcoder.jp/contests/"


class AtCoderScraper(BaseScraper):

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn)
        self.URL = URL
        self.platform = "AtCoder"

    def scrape(self) -> list:

        response = requests.get(self.URL)
        if response.status_code != 200:
            print("Failed to fetch data from AtCoder")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        contests = []

        for contest in soup.select("#contest-table-upcoming tbody tr"):
            cols = contest.find_all("td")
            if len(cols) < 3:
                continue

            try:
                contest_date = datetime.datetime.fromisoformat(cols[0].text.strip())
                contest_date = contest_date.astimezone(datetime.timezone.utc)
            except ValueError as e:
                print(f"Skipping contest due to date parsing error: {e}")
                continue

            contest_name = cols[1].text.strip()
            contest_url = f"https://atcoder.jp{cols[1].find('a')['href']}"

            contests.append(
                {
                    "name": contest_name,
                    "date": contest_date.isoformat(),
                    "url": contest_url,
                }
            )

        return contests
