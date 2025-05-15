from abc import ABC, abstractmethod
import sqlite3
from typing import Any, Dict, List


class BaseScraper(ABC):
    """
    Abstract base class for web scrapers.
    All scrapers should inherit from this class and implement the `scrape` method.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.URL = None
        self.conn = conn
        self.cursor = conn.cursor()
        self.platform = None

    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape data from a website.
        """
        pass

    def update_database(self) -> None:
        """
        Update the database with the scraped data.
        This method should be called by the main application to refresh the contest data.
        It fetches contests from the scrape method and updates the database accordingly.
        """

        # delete old contests
        self.cursor.execute("DELETE FROM contests WHERE platform = ?", (self.platform,))

        contests = self.scrape()
        if not contests:
            print(f"No contests found for {self.platform}.")
            return

        # Insert new contests
        self.cursor.executemany(
            "INSERT INTO contests (name, platform, date, url) VALUES (?, ?, ?, ?)",
            [
                (contest["name"], self.platform, contest["date"], contest["url"])
                for contest in contests
            ],
        )

        self.conn.commit()
