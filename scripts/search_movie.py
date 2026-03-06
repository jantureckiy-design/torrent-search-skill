#!/usr/bin/env python3
"""
Search for movie information and ratings.
Usage: python search_movie.py "Movie Title"
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

def search_tmdb(query):
    """Search movie on TMDB."""
    if not TMDB_API_KEY:
        print("Error: TMDB_API_KEY not set")
        return None
    
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ru-RU",
        "page": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data["results"]:
            return data["results"][0]  # Return first result
        return None
    except Exception as e:
        print(f"TMDB search error: {e}")
        return None

def get_imdb_rating(imdb_id):
    """Get IMDb rating from OMDb API."""
    if not OMDB_API_KEY or not imdb_id:
        return None
    
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "i": imdb_id
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("imdbRating")
    except Exception as e:
        print(f"OMDb API error: {e}")
        return None

def get_kinopoisk_rating(query):
    """Get Kinopoisk rating via web scraping."""
    # This is a simplified version - Kinopoisk requires proper parsing
    # In production, use API or more robust scraping
    search_url = f"https://www.kinopoisk.ru/index.php?kp_query={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for rating in search results
        rating_elem = soup.find("span", {"class": "rating"})
        if rating_elem:
            return rating_elem.text.strip()
        return None
    except Exception as e:
        print(f"Kinopoisk search error: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_movie.py \"Movie Title\"")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"Searching for: {query}")
    
    # 1. Search TMDB
    tmdb_result = search_tmdb(query)
    if not tmdb_result:
        print("Movie not found on TMDB")
        sys.exit(1)
    
    print(f"\n🎬 {tmdb_result['title']} ({tmdb_result.get('release_date', '')[:4]})")
    print(f"📝 {tmdb_result.get('overview', 'No description')}")
    
    # 2. Get IMDb rating
    imdb_id = tmdb_result.get("imdb_id")
    imdb_rating = get_imdb_rating(imdb_id) if imdb_id else None
    
    # 3. Get Kinopoisk rating
    kp_rating = get_kinopoisk_rating(tmdb_result['title'])
    
    print(f"\n⭐ IMDb: {imdb_rating or 'N/A'}/10")
    print(f"⭐ Кинопоиск: {kp_rating or 'N/A'}/10")
    
    # Return JSON for integration
    result = {
        "title": tmdb_result["title"],
        "year": tmdb_result.get("release_date", "")[:4],
        "overview": tmdb_result.get("overview"),
        "imdb_rating": imdb_rating,
        "kinopoisk_rating": kp_rating,
        "poster": f"https://image.tmdb.org/t/p/w500{tmdb_result.get('poster_path', '')}" if tmdb_result.get('poster_path') else None
    }
    
    return result

if __name__ == "__main__":
    main()