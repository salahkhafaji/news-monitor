"""
Main entry point - runs both Blocks 1 and 2 together.
"""

import sys
from collect import fetch_news
from store import save_articles_to_supabase, test_supabase_connection

def main():
    """Main function to orchestrate the entire process."""
    print("=" * 60)
    print("NEWS MONITOR - Block 1 & 2 MVP")
    print("=" * 60)
    
    # Get keyword from user
    keyword = input("\nEnter a keyword to search for: ").strip()
    if not keyword:
        keyword = "technology"
        print(f"Using default keyword: '{keyword}'")
    
    print(f"\n[Step 1] Fetching news for '{keyword}'...")
    articles = fetch_news(keyword, days_back=3, max_articles=20)
    
    if not articles:
        print("No articles found. Exiting.")
        return
    
    print(f"\n[Step 2] Saving {len(articles)} articles to Supabase...")
    
    # Test Supabase connection first
    if not test_supabase_connection():
        print("ERROR: Cannot connect to Supabase. Please check credentials.")
        print("Try running store.py alone to debug.")
        return
    
    inserted, skipped = save_articles_to_supabase(articles)
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  - Articles fetched: {len(articles)}")
    print(f"  - Newly inserted: {inserted}")
    print(f"  - Skipped (duplicates): {skipped}")
    print("=" * 60)

if __name__ == "__main__":
    main()