import sqlite3
import datetime
from scrapers import *


# Initialize database
def init_db():
    conn = sqlite3.connect("contests.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS contests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        platform TEXT NOT NULL,
        date TEXT NOT NULL,
        url TEXT NOT NULL
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS last_update (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        timestamp TEXT NOT NULL
    )
    """
    )

    # Insert initial last_update timestamp if it doesn't exist
    cursor.execute(
        "INSERT OR IGNORE INTO last_update VALUES (1, ?)",
        (datetime.datetime.now().isoformat(),),
    )

    conn.commit()

    scrape_contests(conn)

    conn.close()


# Dummy scraper function
def scrape_contests(conn: sqlite3.Connection):

    print("Scraping contests...")
    cursor = conn.cursor()

    # for all scrapers in scapers package run update_database method
    for scraper_class in scrapers:
        scraper = scraper_class(conn)
        scraper.update_database()

    cursor.execute(
        "UPDATE last_update SET timestamp = ? WHERE id = 1",
        (datetime.datetime.now().isoformat(),),
    )
    conn.commit()
    print("Scraping completed!")


def get_live_db(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM last_update WHERE id = 1")
    last_update_str = cursor.fetchone()[0]
    last_update = datetime.datetime.fromisoformat(last_update_str)
    current_time = datetime.datetime.now()

    # If database was updated more than an hour ago, schedule a scrape
    if (current_time - last_update).total_seconds() > 3600:
        scrape_contests(conn)
