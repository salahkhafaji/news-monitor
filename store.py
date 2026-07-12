"""
BLOCK 2: Supabase Storage
Saves news articles to a Supabase (Postgres) table.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client  # Supabase Python client

# Load environment variables
load_dotenv()

def save_articles_to_supabase(articles):
    """
    Save a list of articles to Supabase, skipping duplicates based on URL.
    
    Parameters:
        articles (list): List of article dictionaries from fetch_news()
    
    Returns:
        tuple: (inserted_count, skipped_count)
    """
    
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    # Validate credentials exist
    if not supabase_url or not supabase_key:
        print("ERROR: Supabase credentials not found in .env file")
        print("Please ensure SUPABASE_URL and SUPABASE_KEY are set")
        return 0, len(articles)
    
    try:
        # Create Supabase client
        # This is like initializing a HttpClient with a base URL in C#
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Get existing URLs from the database to check for duplicates
        # supabase.table('news_articles').select('url').execute() 
        # This is like SQL: SELECT url FROM news_articles
        # 
        # In Python, method chaining is common (like LINQ in C#)
        # .execute() sends the query and returns the result
        existing_urls_response = supabase.table('news_articles').select('url').execute()
        
        # Extract URLs from the response
        # The response data is in existing_urls_response.data
        # This is a list of dictionaries: [{'url': 'http://...'}, {'url': 'http://...'}]
        # 
        # List comprehension again: get the 'url' value from each dictionary
        existing_urls = {item['url'] for item in existing_urls_response.data}
        # Using a set {} instead of list [] for O(1) lookups (like HashSet in C#)
        
        # Separate articles into new and duplicate
        new_articles = []
        duplicate_count = 0
        
        for article in articles:
            url = article.get('url')
            
            # Skip articles without a URL
            if not url:
                print(f"Warning: Skipping article without URL: {article.get('title', 'No title')}")
                duplicate_count += 1
                continue
            
            # Check if URL already exists
            if url in existing_urls:
                duplicate_count += 1
                continue
            
            # Add fetched_at timestamp if not present
            # article.get('fetched_at') is like article?.fetched_at in C#
            if 'fetched_at' not in article:
                article['fetched_at'] = datetime.now().isoformat()
            
            new_articles.append(article)
        
        # Insert new articles
        if new_articles:
            print(f"Inserting {len(new_articles)} new articles...")
            
            # Supabase insert - this generates an INSERT SQL statement
            # supabase.table('news_articles').insert(new_articles).execute()
            # This is like: INSERT INTO news_articles (title, source, ...) VALUES (...)
            #
            # Note: In Python, you can pass a list of dictionaries to insert multiple rows
            result = supabase.table('news_articles').insert(new_articles).execute()
            
            # Check if insertion was successful
            # result.data will contain the inserted records with their IDs
            if result.data:
                print(f"Successfully inserted {len(result.data)} articles.")
            else:
                print("Warning: No articles were inserted. Check the response.")
                return 0, duplicate_count + len(articles)
        else:
            print("No new articles to insert.")
        
        return len(new_articles), duplicate_count
        
    except Exception as e:
        print(f"ERROR saving to Supabase: {e}")
        # In Python, you can re-raise an exception if you want it to propagate
        # return 0, len(articles)  # Return counts even on error
        raise  # Re-raise the exception for the caller to handle


def test_supabase_connection():
    """
    Test the Supabase connection - useful for debugging.
    Returns True if connection works, False otherwise.
    """
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            return False
        
        supabase: Client = create_client(supabase_url, supabase_key)
        # Try a simple query to test connection
        # .limit(1) limits to 1 row, like SELECT ... LIMIT 1 in SQL
        response = supabase.table('news_articles').select('*').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection test failed: {e}")
        return False


# Test block
if __name__ == "__main__":
    # Test connection first
    print("Testing Supabase connection...")
    if test_supabase_connection():
        print("✓ Successfully connected to Supabase")
    else:
        print("✗ Failed to connect to Supabase. Check your credentials.")
        exit(1)
    
    # Create some sample articles for testing
    sample_articles = [
        {
            'title': 'Sample Article 1 - AI Advances',
            'source': 'Tech News',
            'published_at': datetime.now().isoformat(),
            'url': 'https://example.com/article1'
        },
        {
            'title': 'Sample Article 2 - Machine Learning',
            'source': 'AI Daily',
            'published_at': datetime.now().isoformat(),
            'url': 'https://example.com/article2'
        }
    ]
    
    print(f"\nSaving {len(sample_articles)} sample articles...")
    inserted, skipped = save_articles_to_supabase(sample_articles)
    
    print(f"Results: {inserted} inserted, {skipped} skipped")