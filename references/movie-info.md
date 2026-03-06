# Movie Information Lookup

## TMDB API

Get movie details from The Movie Database:

```python
import requests

TMDB_API_KEY = "your_tmdb_key"

def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "ru-RU"
    }
    response = requests.get(url, params=params)
    return response.json()["results"][0] if response.json()["results"] else None
```

## IMDb Rating (OMDb API)

```python
def get_imdb_rating(imdb_id):
    url = "http://www.omdbapi.com/"
    params = {
        "apikey": "your_omdb_key",
        "i": imdb_id
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("imdbRating")
```

## Kinopoisk Rating (Web scraping)

```python
from bs4 import BeautifulSoup

def get_kinopoisk_rating(kp_id):
    url = f"https://www.kinopoisk.ru/film/{kp_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    # Parse rating from page
    rating_element = soup.find("span", {"class": "film-rating-value"})
    return rating_element.text if rating_element else None
```

## Combined Movie Info

```python
def get_movie_info(title):
    # 1. Search TMDB
    tmdb_result = search_movie(title)
    if not tmdb_result:
        return None
    
    movie_id = tmdb_result["id"]
    imdb_id = tmdb_result.get("imdb_id")
    
    # 2. Get ratings
    imdb_rating = get_imdb_rating(imdb_id) if imdb_id else None
    kp_rating = get_kinopoisk_rating(movie_id)  # TMDB ID may map to Kinopoisk
    
    return {
        "title": tmdb_result["title"],
        "year": tmdb_result.get("release_date", "")[:4],
        "overview": tmdb_result.get("overview"),
        "imdb_rating": imdb_rating,
        "kinopoisk_rating": kp_rating,
        "poster": f"https://image.tmdb.org/t/p/w500{tmdb_result.get('poster_path', '')}"
    }
```
