import sqlite3
import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .base_scraper import BaseScraper

BASE_URL = "https://www.codechef.com/api/list/contests/all"
FUTURE_URL = f"{BASE_URL}?sort_by=START&sorting_order=asc&offset=0&mode=future_contests"
ALL_URL = f"{BASE_URL}?sort_by=START&sorting_order=asc&offset=0&mode=all"

# CodeChef's API sits behind a WAF that occasionally rejects requests that
# don't look like they came from a browser (default requests/urllib UA,
# missing Accept/Referer headers). Mimic a real browser to cut down on
# intermittent failures.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.codechef.com/contests",
}


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(HEADERS)
    return session


def _parse_contests(raw_contests: list) -> list:
    contests = []

    for contest in raw_contests:
        contest_name = contest["contest_name"]
        contest_url = f"https://www.codechef.com/contests/{contest['contest_code']}"

        try:
            contest_date = datetime.datetime.fromisoformat(
                contest["contest_start_date_iso"]
            )
            contest_date = contest_date.astimezone(datetime.timezone.utc)
        except (ValueError, TypeError, KeyError) as e:
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


class CodeChefScraper(BaseScraper):

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn)
        self.URL = FUTURE_URL
        self.platform = "CodeChef"

    def _fetch(self, url: str) -> dict | None:
        try:
            response = self.session.get(url, timeout=15)
        except requests.RequestException as e:
            print(f"Failed to fetch data from CodeChef ({url}): {e}")
            return None

        if response.status_code != 200:
            print(f"Failed to fetch data from CodeChef: HTTP {response.status_code}")
            return None

        try:
            response_json = response.json()
        except ValueError as e:
            print(f"Failed to parse CodeChef response as JSON: {e}")
            return None

        if response_json.get("status") != "success":
            print("Error in CodeChef API response")
            return None

        return response_json

    def scrape(self) -> list:
        self.session = _build_session()

        response_json = self._fetch(FUTURE_URL)
        if response_json is not None and response_json.get("future_contests"):
            return _parse_contests(response_json["future_contests"])

        # Fall back to the "all" endpoint (the same one codechef.com/contests
        # itself uses) in case mode=future_contests is misbehaving.
        print("Retrying CodeChef scrape with mode=all fallback")
        response_json = self._fetch(ALL_URL)
        if response_json is None:
            return []

        return _parse_contests(response_json.get("future_contests", []))
