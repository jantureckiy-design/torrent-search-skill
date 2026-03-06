# Ru-tracker Search

## Search Page Structure

Ru-tracker search URL: `https://rutracker.org/forum/tracker.php?nm=QUERY`

### Parsing Search Results

```python
import requests
from bs4 import BeautifulSoup
import re

def search_rutracker(query):
    url = "https://rutracker.org/forum/tracker.php"
    params = {"nm": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    response = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    torrents = []
    # Find torrent rows in table
    for row in soup.select("tr.tCenter.hl-tr"):
        torrent = parse_torrent_row(row)
        if torrent:
            torrents.append(torrent)
    
    return torrents

def parse_torrent_row(row):
    try:
        # Extract title and link
        title_elem = row.select_one("td.t-title-col a.tLink")
        if not title_elem:
            return None
            
        title = title_elem.text.strip()
        torrent_id = re.search(r"t=(\d+)", title_elem["href"])
        if not torrent_id:
            return None
            
        # Extract size
        size_elem = row.select_one("td.t-size-col")
        size_text = size_elem.text.strip() if size_elem else ""
        
        # Extract seeds/leeches
        seeds_elem = row.select_one("td.seedmed.bold")
        seeds = int(seeds_elem.text.strip()) if seeds_elem else 0
        
        leeches_elem = row.select_one("td.leechmed.bold")
        leeches = int(leeches_elem.text.strip()) if leeches_elem else 0
        
        # Parse quality from title
        quality = detect_quality(title)
        
        return {
            "id": torrent_id.group(1),
            "title": title,
            "size": parse_size(size_text),
            "size_text": size_text,
            "seeds": seeds,
            "leeches": leeches,
            "quality": quality,
            "url": f"https://rutracker.org/forum/viewtopic.php?t={torrent_id.group(1)}"
        }
    except Exception as e:
        print(f"Error parsing row: {e}")
        return None

def parse_size(size_str):
    # Convert "1.23 GB" to bytes
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    match = re.match(r"([\d.]+)\s*([KMGT]?B)", size_str.upper())
    if match:
        value, unit = match.groups()
        return float(value) * units.get(unit, 1)
    return 0

def detect_quality(title):
    title_lower = title.lower()
    if "4k" in title_lower or "2160p" in title_lower:
        return "4K"
    elif "1080p" in title_lower or "fullhd" in title_lower:
        return "1080p"
    elif "720p" in title_lower or "hd" in title_lower:
        return "720p"
    elif "dvd" in title_lower:
        return "DVD"
    else:
        return "Unknown"
```

## Torrent Ranking

```python
def rank_torrents(torrents):
    # Sort by: seeds (desc), size (desc for quality), quality score
    def sort_key(t):
        quality_score = {
            "4K": 5, "1080p": 4, "720p": 3, 
            "DVD": 2, "Unknown": 1
        }.get(t["quality"], 0)
        
        return (
            -t["seeds"],  # More seeds first
            -t.get("size", 0),  # Larger files (better quality)
            -quality_score  # Higher quality first
        )
    
    return sorted(torrents, key=sort_key)
```

## Download .torrent File

```python
def download_torrent(torrent_id):
    # Ru-tracker requires login for download
    # This is a simplified version
    url = f"https://rutracker.org/forum/dl.php?t={torrent_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://rutracker.org/forum/viewtopic.php?t={torrent_id}"
    }
    
    # Note: May need session with cookies for logged-in users
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.content  # .torrent file bytes
    return None
```
