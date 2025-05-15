# Contest Schedule Tracker

A mini project to keep track of some competitive programming competitions :)

## Project Structure

```
contest_tracker/
│
├── app.py                      # Main Flask application
├── contests.db                 # SQLite database (created at runtime)
│
├── utils/
|   └── database.py             # Handle the database operations
|   └── pretty_print.py         # Extra functions for formatting
|
├── scrapers/
|   └── base_scraper.py         # Base class for all scrapers
|   └── atcoder_scraper.py      # Scraper overload for AtCoder
|   └── codechef_scraper.py     # Scraper overload for CodeChef
|   └── codeforces_scraper.py   # Scraper overload for Codeforces
|
└── templates/
    └── index.html       # HTML template for the single page application
```

**Notes**: Python version - 3.12.4
