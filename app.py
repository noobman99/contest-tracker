from flask import Flask, render_template, request
import sqlite3
import datetime
import os
from utils.database import get_live_db, init_db
from utils.pretty_print import get_color

app = Flask(__name__)


@app.route("/")
def index():
    conn = sqlite3.connect("contests.db")
    cursor = conn.cursor()

    # get the up-to-date contests from the database
    get_live_db(conn)

    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Get query parameters
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    search_query = request.args.get("query", "").lower()

    # Base query
    query = "SELECT name, platform, date, url FROM contests"
    conditions = []
    params = []

    # Add date range filter if provided
    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    # Add search query filter if provided
    if search_query:
        conditions.append("(LOWER(name) LIKE ? OR LOWER(platform) LIKE ?)")
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern])

    # Construct the final query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Order by Date ascending
    query += " ORDER BY date ASC"

    cursor.execute(query, params)
    contests = cursor.fetchall()

    # Convert into data for rendering
    contests_list = []
    for contest in contests:
        name, platform, date_str, url = contest

        contest_date = datetime.datetime.fromisoformat(date_str)
        contest_date = contest_date.astimezone(datetime.timezone.utc)

        hasbegun = contest_date <= current_time

        contests_list.append(
            {
                "name": name,
                "platform": platform,
                "date": date_str,
                "url": url,
                "bgcolor": get_color(platform),
                "hasbegun": hasbegun,
            }
        )

    conn.close()

    return render_template(
        "index.html",
        contests=contests_list,
        date_from=date_from or "",
        date_to=date_to or "",
        query=search_query or "",
    )


if __name__ == "__main__":
    if not os.path.exists("contests.db"):
        init_db()

    # run the flask server
    app.run(debug=True, port="5000")
