import json
import sqlite3
import urllib.request
from pathlib import Path
from datetime import datetime


def url2id(url: str) -> int:
    return int(url.split("/")[-1])


def main():
    url = "https://raw.githubusercontent.com/manami-project/anime-offline-database/master/anime-offline-database.json"
    sqlite_path = Path(__file__).resolve().parent.parent / "dist" / "anime_ids.sqlite3"
    versions_file = Path(__file__).resolve().parent.parent / "metadata" / "versions.json"
    temporary_file = Path("anime-offline-database.json")

    with open(versions_file, "r") as f:
        versions = json.load(f)

    stored_version = datetime.strptime(versions["database"], "%Y-%m-%d").date()

    print("About to fetch remote")
    with urllib.request.urlopen(url) as response, open(temporary_file, 'wb') as out_file:
        while True:
            chunk = response.read(8192)
            if not chunk:
                break
            out_file.write(chunk)

    with open(temporary_file, "r", encoding='utf-8') as f:
        data = json.load(f)

    if temporary_file.exists():
        temporary_file.unlink()

    remote_version = datetime.strptime(data["lastUpdate"], "%Y-%m-%d").date()

    if remote_version <= stored_version:
        print("No updates found")
        return

    print("Update found, updating database")

    if sqlite_path.exists():
        sqlite_path.unlink()

    # Create SQLite ids database
    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS anime_ids (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kitsu_id INTEGER NOT NULL,
        mal_id INTEGER,
        anilist_id INTEGER
    );
    """)

    # Indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_kitsu_id ON anime_ids (kitsu_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mal_id ON anime_ids (mal_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_anilist_id ON anime_ids (anilist_id);")

    added = 0
    for anime in data.get("data", []):
        sources = anime["sources"]
        kitsu_id = None
        mal_id = None
        anilist_id = None
        for source in sources:
            if "https://anilist.co" in source:
                anilist_id = url2id(source)
            elif "https://kitsu" in source:
                kitsu_id = url2id(source)
            elif "https://myanimelist.net" in source:
                mal_id = url2id(source)

        if kitsu_id is not None and (mal_id is not None or anilist_id is not None):
            cur.execute("""
                INSERT INTO anime_ids (kitsu_id, mal_id, anilist_id)
                VALUES (?, ?, ?)
            """, (
                kitsu_id,
                mal_id,
                anilist_id
            ))
            added += 1

    conn.commit()
    conn.close()

    versions["database"] = data["lastUpdate"]

    with open(versions_file, "w") as f:
        json.dump(versions, f, indent=4)

    print(f"Finished: {added} entries written to {sqlite_path}, new version is {versions["database"]}")


if __name__ == '__main__':
    main()
