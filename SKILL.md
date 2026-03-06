---
name: torrent-search
description: Search for torrent files on Russian trackers (Ru-tracker) and send them via Telegram. Use when user requests torrent files for movies, TV shows, or other media. Includes movie information lookup (IMDb, Kinopoisk ratings) and torrent quality/size ranking.
---

# Torrent Search Skill

Search for torrents on Russian trackers and deliver .torrent files via Telegram.

## Quick Start

1. **Search for movie** → Get IMDb/Kinopoisk ratings
2. **Search Ru-tracker** → Find torrents, rank by size/quality
3. **Send torrent file** → Deliver .torrent via Telegram

## Workflow

### 1. Movie Information Lookup

Use TMDB API to get movie details, then fetch ratings:

- **IMDb rating**: OMDb API or web scraping
- **Kinopoisk rating**: Web scraping from kinopoisk.ru

See [references/movie-info.md](references/movie-info.md) for API details and examples.

### 2. Ru-tracker Search

Search Ru-tracker for torrents:

- Parse search results page
- Extract: title, size, seeds, quality, format
- Rank by: seed count → size → quality

See [references/ru-tracker.md](references/ru-tracker.md) for parsing details.

### 3. Telegram Integration

Send .torrent files via Telegram Bot API:

- Download .torrent file
- Send as document with caption
- Include movie info and torrent details

See [references/telegram.md](references/telegram.md) for sending files.

## Scripts

- `scripts/search_movie.py` - Movie info and ratings lookup
- `scripts/search_torrent.py` - Ru-tracker search and ranking
- `scripts/send_torrent.py` - Telegram file delivery

## Commands

In Telegram "Фильмы" topic:

- `/фильм Название` - Search movie with ratings
- `/торрент Название` - Search torrents on Ru-tracker
- `/скачать [номер]` - Download specific torrent by number

## Configuration

Required API keys:

- TMDB API key (for movie info)
- OMDb API key (for IMDb ratings)
- Telegram Bot token (for file sending)

See [references/config.md](references/config.md) for setup.
