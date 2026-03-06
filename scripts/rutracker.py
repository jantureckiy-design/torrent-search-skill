#!/usr/bin/env python3
"""
Ru-tracker authenticated search and download.
Reads credentials from /root/.openclaw/.secrets/rutracker.txt
"""

import requests
from bs4 import BeautifulSoup
import re
import os

SECRETS_PATH = "/root/.openclaw/.secrets/rutracker.txt"

def load_credentials():
    """Load login/password from secrets file."""
    with open(SECRETS_PATH, "r") as f:
        content = f.read()
    login = re.search(r"Login:\s*(.+)", content).group(1).strip()
    password = re.search(r"Password:\s*(.+)", content).group(1).strip()
    return login, password

def create_session():
    """Create authenticated Ru-tracker session."""
    login, password = load_credentials()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    resp = session.post("https://rutracker.org/forum/login.php", data={
        "login_username": login,
        "login_password": password,
        "login": "Вход"
    }, timeout=15)
    
    if "bb_session" not in session.cookies.get_dict():
        raise Exception("Login failed")
    
    return session

def search(query, session=None):
    """Search Ru-tracker for torrents."""
    if session is None:
        session = create_session()
    
    resp = session.get("https://rutracker.org/forum/tracker.php", 
                       params={"nm": query}, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    results = []
    rows = soup.select("table#tor-tbl tr.tCenter.hl-tr")
    
    for row in rows:
        title_el = row.select_one("a.tLink")
        if not title_el:
            continue
        
        title = title_el.text.strip()
        href = title_el.get("href", "")
        tid = re.search(r"t=(\d+)", href)
        if not tid:
            continue
        
        size_el = row.select_one("a.tr-dl")
        size_text = size_el.text.strip() if size_el else "?"
        
        seeds_el = row.select_one("b.seedmed")
        seeds = int(seeds_el.text.strip()) if seeds_el and seeds_el.text.strip().isdigit() else 0
        
        leech_el = row.select_one("td.leechmed b")
        leeches = int(leech_el.text.strip()) if leech_el and leech_el.text.strip().isdigit() else 0
        
        # Parse size to bytes for sorting
        size_bytes = parse_size(size_text)
        
        # Detect quality
        quality = detect_quality(title)
        
        results.append({
            "id": tid.group(1),
            "title": title,
            "size_text": size_text,
            "size_bytes": size_bytes,
            "seeds": seeds,
            "leeches": leeches,
            "quality": quality,
            "url": f"https://rutracker.org/forum/viewtopic.php?t={tid.group(1)}"
        })
    
    return results

def download_torrent(torrent_id, session=None):
    """Download .torrent file by ID. Returns bytes."""
    if session is None:
        session = create_session()
    
    resp = session.get(f"https://rutracker.org/forum/dl.php?t={torrent_id}", timeout=30)
    
    if resp.status_code == 200 and resp.content[0:1] == b'd':
        return resp.content
    
    raise Exception(f"Failed to download torrent {torrent_id}: HTTP {resp.status_code}")

def parse_size(size_str):
    """Convert '1.23 GB ↓' to bytes."""
    size_str = size_str.replace(",", ".").replace("↓", "").strip()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    match = re.match(r"([\d.]+)\s*([KMGT]?B)", size_str.upper())
    if match:
        return float(match.group(1)) * units.get(match.group(2), 1)
    return 0

def detect_quality(title):
    """Detect video quality from title."""
    t = title.lower()
    for pattern, label in [
        (r"4k|2160p|uhd", "4K"),
        (r"1080p|fullhd|fhd", "1080p"),
        (r"720p", "720p"),
        (r"blu-?ray|bdremux|bdr", "Blu-ray"),
        (r"web-?dl|webdl", "Web-DL"),
        (r"hdr10\+|hdr10|hdr", "HDR"),
        (r"dolby.?vision", "DV"),
        (r"dvd", "DVD"),
    ]:
        if re.search(pattern, t):
            return label
    return ""

def filter_movies(results):
    """Filter out music, books, etc. — keep only video content."""
    video_keywords = ["фантастика", "драма", "комедия", "боевик", "триллер", "ужасы",
                      "приключения", "мелодрама", "детектив", "криминал", "мультфильм",
                      "аниме", "HDRip", "BDRip", "WEB-DL", "Blu-ray", "Remux",
                      "1080p", "2160p", "4K", "720p", "DVDRip", "UHD"]
    
    filtered = []
    for r in results:
        title_lower = r["title"].lower()
        # Skip if it's clearly music or books
        if any(kw in title_lower for kw in ["score", "soundtrack", "flac", "mp3", "kbps",
                                             "epub", "mobi", "pdf", "научпоп", "audiobook"]):
            continue
        filtered.append(r)
    
    return filtered

def rank_results(results):
    """Rank by seeds (desc), then quality score."""
    quality_score = {"4K": 10, "DV": 9, "HDR": 8, "Blu-ray": 7, 
                     "1080p": 6, "Web-DL": 5, "720p": 4, "DVD": 3}
    
    return sorted(results, key=lambda r: (
        -r["seeds"],
        -quality_score.get(r["quality"], 0),
        -r["size_bytes"]
    ))

# CLI interface
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python rutracker.py <search query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"🔍 Searching: {query}\n")
    
    sess = create_session()
    results = search(query, sess)
    movies = filter_movies(results)
    ranked = rank_results(movies)
    
    print(f"Found {len(ranked)} video results:\n")
    for i, r in enumerate(ranked[:10], 1):
        q = f" [{r['quality']}]" if r['quality'] else ""
        print(f"{i}. {r['title'][:100]}")
        print(f"   💾 {r['size_text']} | 🌱 {r['seeds']} сидов{q} | ID: {r['id']}")
        print()
