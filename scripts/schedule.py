import json
import http.client
import shutil
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from http.client import HTTPResponse
from pathlib import Path


SCHEDULE_QUERY = """
query($page:Int,$week_start:Int,$week_end:Int){
  Page(page:$page){
    pageInfo{
      hasNextPage
    }
    airingSchedules(airingAt_greater:$week_start,airingAt_lesser:$week_end){
      id
      episode
      airingAt
      media{
        id
        idMal
        type
      }
    }
  }
}
"""


HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/vnd.api+json"
}


KITSU_HEADERS = {
    "Accept": "application/vnd.api+json",
    "Content-Type": "application/vnd.api+json"
}


def execute_request(body, retries=3) -> HTTPResponse | None:
    c = http.client.HTTPSConnection("graphql.anilist.co")

    # Why do we sleep so much?, because the AniList API doesn't like to be spammed.
    time.sleep(2)
    for attempt in range(retries):
        try:
            c.request("POST", "/", body=json.dumps(body), headers=HEADERS)
            response = c.getresponse()
        except:
            time.sleep(2)
            continue

        if response.status == 200 or response.status == 301:
            return response

        if attempt < retries - 1:
            time.sleep(2)

    return None


def get_kitsu_data(kitsu_id, retries=3) -> dict | None:
    c = http.client.HTTPSConnection("kitsu.io")

    for attempt in range(retries):
        try:
            c.request("GET", f"/api/edge/anime/{kitsu_id}", headers=KITSU_HEADERS)
            response = c.getresponse()

            if response.status == 200 or response.status == 301:
                return json.loads(response.read().decode("utf-8"))
        except:
            time.sleep(2)
            continue

    return None


def get_kitsu_id(sql, anilist_id):
    cur = sql.cursor()
    cur.execute("""
        SELECT kitsu_id
        FROM anime_ids
        WHERE anilist_id = ?
    """, (anilist_id,))
    row = cur.fetchone()
    return row[0] if row else None


def main(sql):
    target_file = Path(__file__).resolve().parent.parent / "dist" / "schedule.json"

    # Get start of week and end of week to fetch schedule
    now = datetime.now(timezone.utc)
    weekday = now.weekday()
    start_of_week = now - timedelta(days=weekday)
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

    week_start = int(start_of_week.timestamp())

    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)

    week_end = int(end_of_week.timestamp())

    page = 1

    variables = {
        "page": page,
        "week_start": week_start,
        "week_end": week_end
    }

    result = []

    print("Starting fetch")
    while True:
        variables["page"] = page

        request = {
            "query": SCHEDULE_QUERY,
            "variables": variables
        }

        response = execute_request(request, retries=5)

        if response is None:
            print("Failed to fetch from AniList API")
            return

        json_data = json.loads(response.read().decode("utf-8"))

        for entry in json_data["data"]["Page"]["airingSchedules"]:
            if entry["media"]["type"] is None:
                continue
            if entry["media"]["type"] != "ANIME":
                continue

            kitsu_id = get_kitsu_id(sql, entry["media"]["id"])

            if kitsu_id is None:
                print(f"Couldn't find kitsu id for {entry["media"]["id"]}")
                continue

            kitsu_data = get_kitsu_data(kitsu_id)

            if kitsu_data is None:
                print(f"Couldn't get kitsu data for id {kitsu_id}")
                continue

            result.append({
                "id": kitsu_id,
                "airingAt": entry["airingAt"],
                "next_episode": entry["episode"],
                "data": kitsu_data["data"]
            })

        if not json_data["data"]["Page"]["pageInfo"]["hasNextPage"]:
            break

        page += 1

    print(f"Saving new airing schedule, new length: {len(result)}")
    with open(target_file, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=4)


if __name__ == '__main__':
    sqlite_path = Path(__file__).resolve().parent.parent / "dist" / "anime_ids.sqlite3"
    sqlite_path_copy = Path("anime_ids_temp.sqlite3")

    shutil.copy(sqlite_path, sqlite_path_copy)

    conn = sqlite3.connect(sqlite_path_copy)

    try:
        main(conn)
    except Exception as e:
        print(f"Unexpected failure, {e}")

    conn.close()

    if sqlite_path_copy.exists():
        sqlite_path_copy.unlink()
