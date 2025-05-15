import sqlite3
import datetime
import requests
from .base_scraper import BaseScraper

URL = "https://www.codechef.com/api/list/contests/all?sort_by=START&sorting_order=asc&offset=0&mode=future_contests"


class CodeChefScraper(BaseScraper):

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn)
        self.URL = URL
        self.platform = "CodeChef"

    def scrape(self) -> list:
        response = requests.get(self.URL)
        if response.status_code != 200:
            print("Failed to fetch data from CodeChef")
            return []

        # save the response text to a file for debugging

        response_json = response.json()

        if response_json["status"] != "success":
            print("Error in CodeChef API response")
            return []

        contests = []

        for contest in response_json["future_contests"]:

            contest_name = contest["contest_name"]
            contest_url = f"https://www.codechef.com/contests/{contest['contest_code']}"

            try:
                contest_date = datetime.datetime.fromisoformat(
                    contest["contest_start_date_iso"]
                )
                contest_date = contest_date.astimezone(datetime.timezone.utc)
            except (ValueError, TypeError) as e:
                print(f"Skipping contest due to date parsing error: {e}")
                continue

            contests.append(
                {
                    "name": contest_name,
                    "date": contest_date.isoformat(),
                    "url": contest_url,
                }
            )

        return contests
