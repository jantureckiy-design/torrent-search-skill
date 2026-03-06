# Configuration

## Required API Keys

### 1. TMDB API
- Register at: https://www.themoviedb.org/signup
- Get API key from: https://www.themoviedb.org/settings/api
- Environment variable: `TMDB_API_KEY`

### 2. OMDb API (IMDb ratings)
- Register at: http://www.omdbapi.com/apikey.aspx
- Free tier: 1000 requests/day
- Environment variable: `OMDB_API_KEY`

### 3. Telegram Bot Token
- Create bot via @BotFather
- Get token from BotFather
- Environment variable: `TELEGRAM_BOT_TOKEN`

### 4. Ru-tracker Credentials (optional)
For downloading .torrent files, may need:
- Ru-tracker account (free registration)
- Session cookies for authenticated requests

## Environment Setup

```bash
# .env file
TMDB_API_KEY=your_tmdb_key_here
OMDB_API_KEY=your_omdb_key_here
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=-1003861307510  # "Заметки" group
TELEGRAM_TOPIC_ID=114  # "Фильмы" topic
```

## Python Dependencies

```txt
requests>=2.28.0
beautifulsoup4>=4.11.0
python-dotenv>=1.0.0
```

Install with:
```bash
pip install requests beautifulsoup4 python-dotenv
```

## Rate Limiting

- TMDB API: 40 requests/10 seconds
- OMDb API: 1000 requests/day (free)
- Ru-tracker: Add delays between requests (2-3 seconds)
- Telegram: 30 messages/second for bots
