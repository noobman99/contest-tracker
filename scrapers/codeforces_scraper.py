import sqlite3
import datetime
import requests
from .base_scraper import BaseScraper

URL = "https://codeforces.com/api/contest.list"


class CodeforcesScraper(BaseScraper):

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn)
        self.URL = URL
        self.platform = "Codeforces"

    def scrape(self) -> list:
        response = requests.get(self.URL)
        if response.status_code != 200:
            print("Failed to fetch data from Codeforces API")
            return []

        response_json = response.json()

        if response_json["status"] != "OK":
            print("Error in Codeforces API response")
            return []

        contests = []

        for contest in response_json["result"]:
            if contest["phase"] == "FINISHED":
                break

            try:
                contest_date = datetime.datetime.fromtimestamp(
                    contest["startTimeSeconds"]
                )
                contest_date = contest_date.astimezone(datetime.timezone.utc)
            except (ValueError, TypeError) as e:
                print(f"Skipping contest due to date parsing error: {e}")
                continue

            contest_name = contest["name"]
            contest_url = f"https://codeforces.com/contests/{contest['id']}"

            contests.append(
                {
                    "name": contest_name,
                    "date": contest_date.isoformat(),
                    "url": contest_url,
                }
            )

        return contests
