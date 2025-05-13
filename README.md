# k.delivery

k.delivery hosts components intended for use in `k`-like apps. These simplify the process of creating anime tracking
apps, offering always up to date, high quality data sources.


# Components

## `dist/anime_ids.sqlite3`

Offers a lightweight, up-to-date, simplified database with relations between anime tracking services. Implementing
parties can use the database to find the ID for a show in other platforms, ex: Kitsu -> AniList.

This is simplified variation of the [anime-offline-database](https://github.com/manami-project/anime-offline-database) 
project, containing only remote service ids, with no further modifications done to the data.

### Database Schema

anime_ids.sqlite3 contains a single table, `anime_ids`:

| Column       | Type    | Description                                             |
| ------------ | ------- | ------------------------------------------------------- |
| `id`         | INTEGER | Auto-incremented internal ID (primary key)              |
| `kitsu_id`   | INTEGER | **Required.** ID from [Kitsu](https://kitsu.io)         |
| `mal_id`     | INTEGER | Optional ID from [MyAnimeList](https://myanimelist.net) |
| `anilist_id` | INTEGER | Optional ID from [AniList](https://anilist.co)          |

### License

This variation is not affiliated with the upstream project. The **anime-offline-database** project
is licensed under the [Open Database License 1.0](https://github.com/manami-project/anime-offline-database/blob/master/LICENSE),
and **anime_ids.sqlite3** is also licensed under the [Open Database License 1.0](dist/ANIME_IDS_LICENSE.md).

### Distribution

Latest version always available at: `https://raw.githubusercontent.com/astar-workspace/k.delivery/refs/heads/main/dist/anime_ids.sqlite3`

----------------------------

## `dist/schedule.json`

Offers an up-to-date airing anime schedule for the current ongoing week, automatically updated every day at 00:15 UTC.

Contains Kitsu data, obtained from the public Kitsu API and licensed under the
[Kitsu terms and conditions of use](https://kitsu.app/terms). Provided free of charge, with no modifications, for cache
purposes; implementing parties don't have to repeatedly fetch Kitsu for data on these shows.

Some non-creative, non-transformative, factual data is fetched from AniList API to construct this file.

### License

`dist/schedule.json` is in no way affiliated with Kitsu. The file is triple licensed:

- Root `data` field contains Kitsu Services data obtained from the public Kitsu API, and licensed under the 
    [Kitsu terms and conditions](https://kitsu.app/terms). May contain third party data as clarified in the terms
    and conditions.
- Root `id`, `airingAt` and `next_episode` are made available under the [MIT License](LICENSE).

### Distribution

Latest version always available at: `https://raw.githubusercontent.com/astar-workspace/k.delivery/refs/heads/main/dist/schedule.json`

----------------------------

## `metadata/versions.json`

Contains two tracking fields:

- `app`: Tracks internal versions, please ignore.
- `database`: Tracks `anime_ids.sqlite3` version. Can be used to check if a new database version is available.

### License

`metadata/versions.json` is licensed under the [MIT License](LICENSE).

### Distribution

Latest version always available at: `https://raw.githubusercontent.com/astar-workspace/k.delivery/refs/heads/main/metadata/versions.json`

----------------------------

# Disclaimer

Effective 2025/05/13, **k.delivery**, formerly known as **KaizoDelivery**, is now a completely independent project.
It has been fully detached from any former codebases, branding, or affiliations.

This project:

- Contains **no binaries** or proprietary assets from previous implementations.
- Has been rewritten and restructured to serve as a clean, standalone delivery system.
- Is intended for general-purpose use in any `k`-like projects.

Additionally, implementing projects:

- Shall remain fully independent and separate from k.delivery itself.
- Have no official affiliation, governance, or shared development responsibility with the maintainers of k.delivery.
- Must understand the licensing in which each artifact is provided.
