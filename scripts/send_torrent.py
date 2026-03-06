#!/usr/bin/env python3
"""
Send torrent file via Telegram.
Usage: python send_torrent.py <torrent_id> <movie_title> [chat_id] [topic_id]
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEFAULT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "-1003861307510")
DEFAULT_TOPIC_ID = os.getenv("TELEGRAM_TOPIC_ID", "114")

def download_torrent_file(torrent_id):
    """Download .torrent file from Ru-tracker."""
    # Note: This is a simplified version
    # Ru-tracker may require login or have anti-bot measures
    url = f"https://rutracker.org/forum/dl.php?t={torrent_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"https://rutracker.org/forum/viewtopic.php?t={torrent_id}",
        "Accept": "application/x-bittorrent, */*"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200 and response.content[:11] == b"d8:announce":
            # Valid .torrent file (starts with torrent header)
            return response.content
        else:
            print(f"Invalid torrent file or download failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Download error: {e}")
        return None

def send_telegram_document(chat_id, document_bytes, filename, caption, topic_id=None):
    """Send document via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    
    # Prepare files
    files = {
        "document": (filename, document_bytes, "application/x-bittorrent")
    }
    
    # Prepare data
    data = {
        "chat_id": chat_id,
        "caption": caption,
        "parse_mode": "HTML"
    }
    
    # Add topic/message thread ID if provided
    if topic_id:
        data["message_thread_id"] = topic_id
    
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Torrent sent successfully!")
            print(f"   Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Telegram error: {result.get('description', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Telegram API error: {e}")
        return False

def format_caption(movie_title, torrent_info):
    """Format caption for Telegram message."""
    title = movie_title
    torrent_title = torrent_info.get("title", "Unknown")[:100]
    size = torrent_info.get("size_text", "Unknown")
    seeds = torrent_info.get("seeds", 0)
    quality = torrent_info.get("quality", "Unknown")
    
    return f"""🎬 <b>{title}</b>

📥 <b>Торрент:</b> {torrent_title}
💾 <b>Размер:</b> {size}
🌱 <b>Сиды:</b> {seeds}
🎞️ <b>Качество:</b> {quality}

#фильм #торрент #rutracker"""

def main():
    if len(sys.argv) < 3:
        print("Usage: python send_torrent.py <torrent_id> <movie_title> [chat_id] [topic_id]")
        print("Example: python send_torrent.py 1234567 \"Inception\" -1003861307510 114")
        sys.exit(1)
    
    torrent_id = sys.argv[1]
    movie_title = sys.argv[2]
    chat_id = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_CHAT_ID
    topic_id = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_TOPIC_ID
    
    print(f"Downloading torrent {torrent_id} for: {movie_title}")
    
    # Download torrent file
    torrent_bytes = download_torrent_file(torrent_id)
    if not torrent_bytes:
        print("Failed to download torrent file")
        sys.exit(1)
    
    print(f"Downloaded {len(torrent_bytes)} bytes")
    
    # Create torrent info for caption
    torrent_info = {
        "title": f"{movie_title}.torrent",
        "size_text": f"{len(torrent_bytes) / 1024:.1f} KB",
        "seeds": "N/A",
        "quality": "Unknown"
    }
    
    # Format filename
    safe_title = "".join(c for c in movie_title if c.isalnum() or c in " .-_")
    filename = f"{safe_title}.torrent"
    
    # Format caption
    caption = format_caption(movie_title, torrent_info)
    
    # Send via Telegram
    print(f"Sending to chat {chat_id}, topic {topic_id}...")
    success = send_telegram_document(chat_id, torrent_bytes, filename, caption, topic_id)
    
    if success:
        print("✅ Done!")
    else:
        print("❌ Failed to send torrent")
        sys.exit(1)

if __name__ == "__main__":
    main()