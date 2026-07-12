"""
BLOCK 1: News Collection
Fetches recent articles from NewsAPI for a given keyword.
"""

import os
import requests  # Used for making HTTP requests (like HttpClient in C#)
from datetime import datetime, timedelta
from dotenv import load_dotenv  # Loads environment variables from .env file

# Load environment variables from .env file
# In C#, you might use ConfigurationManager or environment variables
load_dotenv()

def fetch_news(keyword, days_back=3, max_articles=50):
    """
    Fetch news articles for a given keyword from NewsAPI.
    
    Parameters:
        keyword (str): The search term (e.g., "AI technology" or "Tesla")
        days_back (int): How many days back to search (default: 3)
        max_articles (int): Maximum number of articles to return (default: 50)
    
    Returns:
        list: List of article dictionaries, each containing:
              - title: article headline
              - source: source name
              - published_at: publication date (ISO format)
              - url: article URL
    
    Note: In Python, type hints (like -> list) are optional but helpful.
    They're similar to C# type annotations but don't enforce types at runtime.
    """
    
    # Get API key from environment variable
    # os.getenv() is like Environment.GetEnvironmentVariable() in C#
    api_key = os.getenv('NEWS_API_KEY')
    
    # Check if API key exists - similar to string.IsNullOrEmpty in C#
    if not api_key:
        print("ERROR: NEWS_API_KEY not found in .env file")
        print("Please create a .env file with your NewsAPI key")
        return []
    
    # Build the API URL with parameters
    # This is like string interpolation in C# ($"...") but using f-strings in Python
    # Python f-strings are prefixed with 'f' and use { } for variables
    base_url = "https://newsapi.org/v2/everything"
    
    # Calculate date range (NewsAPI requires a 'from' parameter)
    # datetime.now() is like DateTime.Now in C#
    # timedelta is like TimeSpan in C# for date arithmetic
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Create query parameters dictionary
    # Python dictionaries are like C# Dictionary<string, string>
    params = {
        'q': keyword,  # Search query
        'from': from_date,
        'sortBy': 'publishedAt',  # Sort by date, newest first
        'apiKey': api_key,
        'pageSize': max_articles,  # Max articles per request (50 is free tier max)
        'language': 'en'  # English only for simplicity
    }
    
    try:
        # Make the HTTP GET request
        # requests.get() is like HttpClient.GetAsync() in C#, but synchronous
        print(f"Fetching news for '{keyword}' from {from_date}...")
        response = requests.get(base_url, params=params, timeout=10)
        
        # Check if request was successful
        # response.raise_for_status() throws an exception for HTTP errors (like 4xx, 5xx)
        # This is similar to EnsureSuccessStatusCode() in C#
        response.raise_for_status()
        
        # Parse JSON response
        # response.json() deserializes the JSON string into Python dictionaries/lists
        # This is like JsonSerializer.Deserialize() in C#
        data = response.json()
        
        # Check for API-specific errors
        # In Python, you check if a key exists in a dictionary using 'in' operator
        if data.get('status') == 'error':
            error_msg = data.get('message', 'Unknown error')
            print(f"NewsAPI error: {error_msg}")
            return []
        
        # Extract articles from response
        articles = data.get('articles', [])
        
        # Check if we got any articles
        if not articles:
            print(f"No articles found for '{keyword}' in the last {days_back} days.")
            return []
        
        # Transform the data - keep only the fields we need
        # This is a list comprehension - a Pythonic way to create a new list from an existing one
        # Think of it like LINQ's .Select() in C#:
        # articles.Select(a => new { Title = a.title, ... })
        # 
        # Syntax: [expression for item in iterable if condition]
        # - expression: what to put in the new list
        # - item: each element from the original list
        # - iterable: the original list
        # - condition (optional): filter items
        #
        # Also note: .get() with a default value is like using the null-conditional operator ?.
        # article.get('title', 'No title') is like article?.title ?? 'No title' in C#
        processed_articles = [
            {
                'title': article.get('title', 'No title'),
                'source': article.get('source', {}).get('name', 'Unknown source'),
                'published_at': article.get('publishedAt', datetime.now().isoformat()),
                'url': article.get('url', '')
            }
            for article in articles
            # Filter out articles without a URL (skip if empty string or None)
            # In Python, empty strings, None, and empty lists are "falsy"
            if article.get('url')
        ]
        
        print(f"Successfully fetched {len(processed_articles)} articles.")
        return processed_articles
        
    except requests.exceptions.Timeout:
        # Catching specific exceptions in Python uses 'except ExceptionType:'
        # This is like catch (TimeoutException) in C#
        print("ERROR: Request timed out. Please check your internet connection.")
        return []
        
    except requests.exceptions.ConnectionError:
        print("ERROR: No internet connection or unable to reach NewsAPI.")
        return []
        
    except requests.exceptions.HTTPError as e:
        # 'as e' captures the exception object, like catch (Exception e) in C#
        if response.status_code == 429:
            print("ERROR: Rate limit exceeded. NewsAPI free tier allows limited requests.")
            print("Please wait a minute before trying again.")
        elif response.status_code == 401:
            print("ERROR: Invalid API key. Please check your NEWS_API_KEY in .env")
        else:
            print(f"HTTP Error: {e}")
        return []
        
    except Exception as e:
        # Catching all other exceptions (like catch (Exception) in C#)
        # In Python, 'Exception' is the base class for all built-in exceptions
        print(f"Unexpected error: {e}")
        return []


# This block runs only when the script is executed directly (not imported)
# In C#, this is like having a Main() method
# __name__ is a special Python variable that's set to "__main__" when the script is run directly
if __name__ == "__main__":
    # Test the function with a sample keyword
    keyword = input("Enter a keyword to search for (e.g., 'AI' or 'Tesla'): ").strip()
    
    if not keyword:
        keyword = "technology"  # Default keyword
    
    articles = fetch_news(keyword)
    
    # Print summary of results
    # f-string formatting: f"text {variable}" is like $"{variable}" in C#
    print(f"\nFound {len(articles)} articles for '{keyword}':")
    print("-" * 50)
    
    # enumerate() gives us both index and value, like for (int i = 0; i < list.Count; i++)
    for i, article in enumerate(articles[:5], 1):  # Show first 5 articles only
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Date: {article['published_at'][:10]}")  # [:10] slices the string to get first 10 chars (YYYY-MM-DD)
        print(f"   URL: {article['url']}")
        print()