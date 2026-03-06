# Telegram Integration

## Sending .torrent Files

```python
import requests

def send_torrent_telegram(chat_id, torrent_file, caption, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    
    files = {
        "document": ("movie.torrent", torrent_file, "application/x-bittorrent")
    }
    
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, files=files, data=data)
    return response.json()
```

## Formatting Movie Info Message

```python
def format_movie_message(movie_info, torrent_info):
    title = movie_info.get("title", "Unknown")
    year = movie_info.get("year", "")
    imdb = movie_info.get("imdb_rating", "N/A")
    kp = movie_info.get("kinopoisk_rating", "N/A")
    
    torrent_title = torrent_info.get("title", "")
    size = torrent_info.get("size_text", "Unknown")
    seeds = torrent_info.get("seeds", 0)
    quality = torrent_info.get("quality", "Unknown")
    
    return f"""🎬 <b>{title}</b> ({year})

⭐ <b>IMDb:</b> {imdb}/10
⭐ <b>Кинопоиск:</b> {kp}/10

📥 <b>Торрент:</b> {torrent_title}
💾 <b>Размер:</b> {size}
🌱 <b>Сиды:</b> {seeds}
🎞️ <b>Качество:</b> {quality}

#фильм #торрент"""
```

## Telegram Bot Commands

Set up bot commands:

```python
BOT_COMMANDS = [
    {"command": "фильм", "description": "Поиск фильма с рейтингами"},
    {"command": "торрент", "description": "Поиск торрентов на Ru-tracker"},
    {"command": "скачать", "description": "Скачать выбранный торрент"}
]
```

Update via:
```python
url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
requests.post(url, json={"commands": BOT_COMMANDS})
```
