"""
BLOCK 4: DECIDE - Generate AI Marketing Recommendations
Reads recent articles from Supabase and uses Google Gemini AI to generate
actionable marketing recommendations.

IMPORTANT PYTHON CONCEPTS FOR C# DEVELOPERS:

1. TYPE HINTS (-> str, -> list, etc.):
   - Similar to C# type annotations but OPTIONAL in Python
   - Example: def get_articles() -> list:  # Returns a list
   - In C#: public List<Article> GetArticles()
   - Python doesn't enforce these at runtime, they're for documentation/IDE help

2. GOOGLE GEMINI API:
   - This is like using any cloud API service in C# (Azure OpenAI, etc.)
   - We send a list of article headlines and get back an AI-generated response
   - The model "gemini-3-flash" is fast and cost-effective for simple tasks

3. ENVIRONMENT VARIABLES:
   - os.getenv('GEMINI_API_KEY') is like Environment.GetEnvironmentVariable() in C#
   - We load them once from .env using load_dotenv()

4. TEXT WRAPPING:
   - In C#, you'd use StringBuilder or string.Concat for long strings
   - In Python, triple quotes (""" """) allow multi-line strings
   - Also, we use join() which is like string.Join() in C#
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai  # Google Gemini AI client

# Load environment variables from .env file
load_dotenv()


def get_articles_from_supabase(limit=10):
    """
    Fetch the most recent articles from Supabase.
    
    Parameters:
        limit (int): Number of articles to fetch (default: 10)
    
    Returns:
        list: List of article dictionaries with title, source, published_at, url
    
    In C#, this would be like:
    public List<Article> GetArticles(int limit = 10) { ... }
    """
    try:
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("ERROR: Supabase credentials not found in .env file")
            return []
        
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Query the most recent articles (ordered by published_at descending)
        # .limit(limit) is like SELECT TOP 10 in SQL
        # In C#, this would be: supabase.Table("news_articles").OrderByDescending(a => a.published_at).Take(limit)
        response = supabase.table('news_articles')\
            .select('title', 'source', 'published_at', 'url')\
            .order('published_at', desc=True)\
            .limit(limit)\
            .execute()
        
        if not response.data:
            print("No articles found in the database.")
            return []
        
        print(f"✅ Fetched {len(response.data)} recent articles from Supabase")
        return response.data
        
    except Exception as e:
        print(f"❌ Error fetching articles from Supabase: {e}")
        return []


def generate_recommendation(articles):
    """
    Send articles to Gemini AI and get a marketing recommendation.
    
    Parameters:
        articles (list): List of article dictionaries from Supabase
    
    Returns:
        str: AI-generated marketing recommendation (2-3 sentences)
    
    How this works in C# terms:
    - This is like calling an API endpoint that uses OpenAI
    - We format the prompt, send it, and parse the response
    - The response is plain text (not JSON)
    
    PYTHON SPECIFIC: 
    - We use f-strings for string interpolation (like $"" in C#)
    - Triple quotes for multi-line strings
    - The API key is read from environment variables
    """
    try:
        # Get Gemini API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            print("Please add: GEMINI_API_KEY=your_key_here")
            return None
        
        # Configure the Gemini API
        # This is like setting up an HttpClient with an API key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        # We use gemini-3-flash for speed and cost-effectiveness
        # In C#, this would be like: var model = new GeminiModel("gemini-3-flash");
        model = genai.GenerativeModel('gemini-3-flash-preview') 
               
        # Build the prompt with article headlines
        # List comprehension: extract titles from articles
        # In C#, this would be: articles.Select(a => a['title']).ToList()
        headlines = [article['title'] for article in articles]
        
        # Create the prompt
        # Triple quotes allow multi-line strings (like @"" in C# verbatim strings)
        prompt = f"""
You are a marketing analyst reviewing recent news articles about a company's industry.

Here are the headlines from the {len(headlines)} most recent news articles:

{chr(10).join(f'- {headline}' for headline in headlines)}

Based on these news headlines, provide ONE short, actionable marketing recommendation.
Keep it very brief - 2-3 sentences maximum.
Focus on what the company should do based on the current news trends.
Make it practical and specific, not generic advice.

Example format: "Given the recent coverage of AI regulations, prioritize creating content about your compliance efforts to build trust with customers."
"""
        
        print("🤔 Generating recommendation using Gemini AI...")
        
        # Send the prompt to Gemini AI
        # This is like calling an async API endpoint
        # The .generate_content() method sends the prompt and returns the response
        response = model.generate_content(prompt)
        
        # Extract the text from the response
        # In Gemini, the response has a .text property
        recommendation = response.text.strip()
        
        print(f"✅ Recommendation generated successfully!")
        print(f"📝 Length: {len(recommendation)} characters")
        
        return recommendation
        
    except Exception as e:
        print(f"❌ Error generating recommendation: {e}")
        return None


def save_recommendation_to_file(recommendation):
    """
    Save the recommendation to a file for history/audit purposes.
    
    Parameters:
        recommendation (str): The AI-generated recommendation
    
    This is like writing to a log file or audit trail in C#.
    We use a timestamped filename for tracking.
    """
    try:
        # Create a filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recommendations/recommendation_{timestamp}.txt'
        
        # Ensure the directory exists
        # os.makedirs() is like Directory.CreateDirectory() in C#
        # exist_ok=True means "don't error if it already exists"
        os.makedirs('recommendations', exist_ok=True)
        
        # Write the recommendation to file
        # In C#, this would be: File.WriteAllText(filename, content);
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(recommendation)
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("Recommendation saved for future reference.\n")
        
        print(f"💾 Recommendation saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"⚠️ Could not save recommendation to file: {e}")
        return None


# --- MAIN EXECUTION BLOCK ---
# This runs when you execute: python decide.py
if __name__ == "__main__":
    print("=" * 60)
    print("📊 BLOCK 4: DECIDE - AI Marketing Recommendations")
    print("=" * 60)
    
    # Step 1: Get recent articles
    print("\n📰 Fetching recent articles...")
    articles = get_articles_from_supabase(limit=10)
    
    if not articles:
        print("No articles available. Run main.py first to collect articles.")
        exit(1)
    
    # Step 2: Generate recommendation using Gemini AI
    print("\n🤖 Generating AI recommendation...")
    recommendation = generate_recommendation(articles)
    
    if not recommendation:
        print("Failed to generate recommendation. Check your Gemini API key.")
        exit(1)
    
    # Step 3: Display the recommendation
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION:")
    print("=" * 60)
    print(recommendation)
    print("=" * 60)
    
    # Step 4: Save to file (optional)
    print("\n💾 Saving recommendation for history...")
    save_recommendation_to_file(recommendation)
    
    print("\n✨ Block 4 complete! Ready for Block 5 (Act)")
    print("To test Block 5, run: python act.py")