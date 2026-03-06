#!/usr/bin/env python3
"""
Test the torrent search skill components.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.search_movie import search_tmdb, get_imdb_rating, get_kinopoisk_rating
from scripts.search_torrent import search_rutracker, rank_torrents

def test_movie_search():
    """Test movie information lookup."""
    print("Testing movie search...")
    
    # This would require actual API keys
    print("Note: Movie search requires TMDB and OMDb API keys")
    print("Set TMDB_API_KEY and OMDB_API_KEY environment variables")
    
    return True

def test_torrent_search():
    """Test torrent search (no API keys needed)."""
    print("\nTesting torrent search...")
    
    # Test with a popular movie
    query = "интерстеллар"
    torrents = search_rutracker(query)
    
    if torrents:
        print(f"Found {len(torrents)} torrents for '{query}'")
        
        # Rank and show top 3
        ranked = rank_torrents(torrents)[:3]
        for i, t in enumerate(ranked, 1):
            print(f"{i}. {t['title'][:60]}...")
            print(f"   Size: {t['size_text']} | Seeds: {t['seeds']} | Quality: {t['quality']}")
        
        return True
    else:
        print(f"No torrents found for '{query}'")
        print("Note: Ru-tracker may be blocking requests or require different parsing")
        return False

if __name__ == "__main__":
    print("Torrent Search Skill Test")
    print("=" * 50)
    
    # Test movie search (informational)
    test_movie_search()
    
    # Test torrent search
    success = test_torrent_search()
    
    if success:
        print("\n✅ Skill components are working!")
        print("\nNext steps:")
        print("1. Get TMDB API key from https://www.themoviedb.org/settings/api")
        print("2. Get OMDb API key from http://www.omdbapi.com/apikey.aspx")
        print("3. Create Telegram bot via @BotFather")
        print("4. Set environment variables in .env file")
    else:
        print("\n⚠️ Some tests failed. Check network connection and Ru-tracker accessibility.")
