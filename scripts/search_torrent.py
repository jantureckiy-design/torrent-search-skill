#!/usr/bin/env python3
"""
Search for torrents on Ru-tracker.
Usage: python search_torrent.py "Movie Title"
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re
import time

def search_rutracker(query):
    """Search Ru-tracker for torrents."""
    url = "https://rutracker.org/forum/tracker.php"
    params = {"nm": query}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Check if we got blocked or redirected
        if "captcha" in response.text.lower() or "cloudflare" in response.text:
            print("Warning: Possible CAPTCHA or blocking detected")
            return []
        
        return parse_search_results(response.text)
    except Exception as e:
        print(f"Ru-tracker search error: {e}")
        return []

def parse_search_results(html):
    """Parse HTML search results from Ru-tracker."""
    soup = BeautifulSoup(html, "html.parser")
    torrents = []
    
    # Find torrent rows (adjust selector based on actual page structure)
    rows = soup.select("tr.tCenter.hl-tr") or soup.select("tr.hl-tr")
    
    for row in rows:
        torrent = parse_torrent_row(row)
        if torrent:
            torrents.append(torrent)
    
    return torrents

def parse_torrent_row(row):
    """Parse a single torrent row."""
    try:
        # Extract title and link
        title_elem = row.select_one("td.t-title-col a.tLink")
        if not title_elem:
            title_elem = row.select_one("a.tLink")
        
        if not title_elem:
            return None
        
        title = title_elem.text.strip()
        href = title_elem.get("href", "")
        
        # Extract torrent ID
        torrent_id_match = re.search(r"t=(\d+)", href)
        if not torrent_id_match:
            return None
        
        torrent_id = torrent_id_match.group(1)
        
        # Extract size
        size_elem = row.select_one("td.t-size-col")
        size_text = size_elem.text.strip() if size_elem else "0 B"
        
        # Extract seeds/leeches
        seeds_elem = row.select_one("td.seedmed.bold")
        seeds = int(seeds_elem.text.strip()) if seeds_elem and seeds_elem.text.strip().isdigit() else 0
        
        leeches_elem = row.select_one("td.leechmed.bold")
        leeches = int(leeches_elem.text.strip()) if leeches_elem and leeches_elem.text.strip().isdigit() else 0
        
        # Parse quality from title
        quality = detect_quality(title)
        
        # Parse size to bytes
        size_bytes = parse_size_to_bytes(size_text)
        
        return {
            "id": torrent_id,
            "title": title,
            "size_text": size_text,
            "size_bytes": size_bytes,
            "seeds": seeds,
            "leeches": leeches,
            "quality": quality,
            "url": f"https://rutracker.org/forum/viewtopic.php?t={torrent_id}"
        }
    except Exception as e:
        print(f"Error parsing row: {e}")
        return None

def parse_size_to_bytes(size_str):
    """Convert size string like '1.23 GB' to bytes."""
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4
    }
    
    # Match pattern like "1.23 GB" or "1,23 GB" (Russian decimal separator)
    size_str = size_str.replace(",", ".")
    match = re.match(r"([\d.]+)\s*([KMGT]?B)", size_str.upper())
    
    if match:
        value, unit = match.groups()
        try:
            return float(value) * units.get(unit, 1)
        except ValueError:
            return 0
    
    return 0

def detect_quality(title):
    """Detect video quality from title."""
    title_lower = title.lower()
    
    quality_map = [
        ("4k|2160p|uhd", "4K"),
        ("1080p|fullhd|fhd", "1080p"),
        ("720p|hdready", "720p"),
        ("480p|sd", "480p"),
        ("dvd|dvdrip", "DVD"),
        ("web-dl|webdl|web", "Web-DL"),
        ("blu-ray|bluray|bdrip|bdr", "Blu-ray"),
        ("hdr10|hdr", "HDR"),
        ("dv|dolby.vision", "Dolby Vision")
    ]
    
    for pattern, quality in quality_map:
        if re.search(pattern, title_lower):
            return quality
    
    return "Unknown"

def rank_torrents(torrents):
    """Rank torrents by quality and seeds."""
    def sort_key(t):
        # Quality score mapping
        quality_scores = {
            "4K": 100, "1080p": 80, "720p": 60, "480p": 40,
            "Blu-ray": 90, "Web-DL": 85, "HDR": 95, 
            "Dolby Vision": 98, "DVD": 30, "Unknown": 10
        }
        
        quality_score = quality_scores.get(t["quality"], 10)
        seed_score = t["seeds"] * 10  # Weight seeds heavily
        size_score = t["size_bytes"] / (1024**3)  # GB size as minor factor
        
        return -(seed_score + quality_score + size_score)
    
    return sorted(torrents, key=sort_key)

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_torrent.py \"Movie Title\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"Searching Ru-tracker for: {query}")
    
    torrents = search_rutracker(query)
    
    if not torrents:
        print("No torrents found")
        sys.exit(1)
    
    # Rank torrents
    ranked_torrents = rank_torrents(torrents)
    
    print(f"\nFound {len(ranked_torrents)} torrents:")
    print("=" * 80)
    
    for i, torrent in enumerate(ranked_torrents[:10], 1):
        print(f"{i}. {torrent['title'][:80]}...")
        print(f"   📦 Size: {torrent['size_text']} | 🌱 Seeds: {torrent['seeds']} | 🎞️ Quality: {torrent['quality']}")
        print(f"   🔗 ID: {torrent['id']}")
        print()
    
    return ranked_torrents

if __name__ == "__main__":
    main()