"""
BLOCK 3: SHOW - Streamlit Dashboard
Displays news articles from Supabase in a web dashboard.

IMPORTANT PYTHON/STREAMLIT CONCEPTS FOR C# DEVELOPERS:

1. STREAMLIT'S EXECUTION MODEL:
   - Unlike a C# Windows Forms or Blazor app that runs continuously with event handlers,
     Streamlit works differently: the ENTIRE script runs from top to bottom EVERY time
     the page loads or a user interacts with a widget.
   - Think of it like a C# MVC controller action that re-executes completely
     whenever you click a button or refresh the page.
   - This is why we use @st.cache_data decorators - they cache data between
     re-executions so we don't hit the database every single time.

2. DECORATORS (@st.cache_data):
   - In C#, you'd use attributes like [HttpGet] or [Authorize]
   - In Python, decorators are like attributes that wrap/modify functions
   - @st.cache_data tells Streamlit: "If the function is called with the same
     arguments, return the cached result instead of re-running"
   - This is like MemoryCache in C#, but automatic!

3. SESSION STATE (st.session_state):
   - Like ViewState in ASP.NET WebForms or session variables in ASP.NET Core
   - Persists data across reruns for the current user session
   - Example: storing the refresh button state

4. WIDGETS (st.button, st.selectbox):
   - These are like C# UI controls (Button, DropDownList)
   - But unlike C# where you attach event handlers, in Streamlit you just
     check the widget's value in your script flow
   - Example: if st.button("Click me"): # this runs when button is clicked

5. CACHING VS REFRESH:
   - @st.cache_data caches data across reruns (like a database cache)
   - st.button allows manual refresh when user wants new data
   - The button triggers a full script re-run, which checks for new data
"""

import os
import pandas as pd  # Pandas = like DataTable in C#, for data manipulation
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv  # Loads .env file
from supabase import create_client, Client
import streamlit as st  # Streamlit - web UI framework for Python

# Load environment variables from .env
load_dotenv()


# DECORATOR EXPLANATION:
# @st.cache_data - This is like [Cache] attribute in C# MVC
# It caches the result of this function so it doesn't re-run every time
# the page refreshes. This prevents hitting Supabase on every user interaction.
# 
# The ttl=60 means "cache for 60 seconds" - Time To Live, like CacheItemPolicy
# in C# with AbsoluteExpiration.
#
# In C# terms, this is similar to:
# [OutputCache(Duration = 60)]
# public List<Article> GetArticles() { ... }
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_articles_from_supabase():
    """
    Fetch all articles from Supabase, sorted by published date (newest first).
    
    Returns:
        pandas.DataFrame: A table of articles with columns: id, title, source, 
                         published_at, url, fetched_at
    
    In C# terms, this returns a DataTable or List<Article>.
    """
    try:
        # Get Supabase credentials from environment
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            st.error("Supabase credentials not found in .env file")
            return pd.DataFrame()  # Return empty DataFrame (like empty DataTable)
        
        # Create Supabase client
        # In C#, this would be like: var client = new SupabaseClient(url, key);
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Query all articles, ordered by published_at descending (newest first)
        # .order() is like ORDER BY in SQL: ORDER BY published_at DESC
        # .execute() sends the query to Supabase
        response = supabase.table('news_articles')\
            .select('*')\
            .order('published_at', desc=True)\
            .execute()
        
        # Check if we got data
        if not response.data:
            st.info("No articles found in the database. Run main.py first to collect articles!")
            return pd.DataFrame()
        
        # Convert to pandas DataFrame
        # In C#, this is like: var dataTable = JsonSerializer.Deserialize<DataTable>(json);
        df = pd.DataFrame(response.data)
        
        # --- FIX: Parse dates with timezone awareness ---
        # The dates come from Supabase as ISO8601 strings like: "2026-07-11T22:33:00+00:00"
        # We need to tell pandas the exact format to parse them correctly.
        #
        # In C#, this would be like: DateTime.ParseExact(dateString, "yyyy-MM-ddTHH:mm:sszzz", CultureInfo.InvariantCulture)
        #
        # IMPORTANT: We use utc=True to ensure the datetime is timezone-aware (UTC)
        # This prevents comparison errors later when we compare with UTC times.
        df['published_at'] = pd.to_datetime(df['published_at'], format='ISO8601', utc=True)
        df['fetched_at'] = pd.to_datetime(df['fetched_at'], format='ISO8601', utc=True)
        
        # Format dates for display (we'll keep the UTC timezone)
        df['published_date'] = df['published_at'].dt.strftime('%Y-%m-%d')
        df['published_time'] = df['published_at'].dt.strftime('%H:%M')
        
        return df
        
    except Exception as e:
        # Catching all exceptions, like catch (Exception e) in C#
        st.error(f"Error fetching articles: {e}")
        # Display the error details for debugging
        import traceback
        st.code(traceback.format_exc())
        return pd.DataFrame()


def get_articles_by_day(df, days=7):
    """
    Group articles by day for the last N days.
    
    Parameters:
        df (DataFrame): Articles DataFrame
        days (int): Number of days to look back
    
    Returns:
        DataFrame: Daily article counts
    """
    if df.empty:
        return pd.DataFrame()
    
    # --- FIX: Make cutoff_date timezone-aware (UTC) ---
    # In C#, this would be: DateTime.UtcNow.AddDays(-days)
    # We use timezone.utc to make it timezone-aware like the DataFrame column
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Filter articles from the last N days
    # In pandas, this is like: df[df['published_at'] > cutoffDate] in C#
    recent_articles = df[df['published_at'] >= cutoff_date]
    
    # Group by date and count
    # .groupby() is like GROUP BY in SQL
    # .size() counts rows in each group
    # .reset_index() converts the group index back to a column
    daily_counts = recent_articles.groupby(
        recent_articles['published_at'].dt.date
    ).size().reset_index(name='count')
    
    # Rename the date column
    daily_counts.columns = ['date', 'count']
    
    # Sort by date
    daily_counts = daily_counts.sort_values('date')
    
    return daily_counts


# --- STREAMLIT UI STARTS HERE ---
# This is like the Page_Load() method in C# Web Forms, but it runs
# every time the page loads or user interacts with a widget.

# Set page configuration - this must be the FIRST Streamlit command
# In C#, this is like setting page title in the <head> section
st.set_page_config(
    page_title="News Monitor Dashboard",
    page_icon="📰",
    layout="wide"
)

# --- SIDEBAR (like a left navigation panel) ---
# st.sidebar creates a sidebar similar to a Bootstrap sidebar or
# left menu in a C# web app
with st.sidebar:
    st.title("📰 News Monitor")
    st.markdown("---")
    
    # Display last refresh time (use UTC for consistency)
    # In C#, this would be: lblLastRefresh.Text = DateTime.UtcNow.ToString();
    st.write(f"Last refresh: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # --- REFRESH BUTTON ---
    # In Streamlit, buttons work differently than C#:
    # In C#: button_Click(object sender, EventArgs e) { RefreshData(); }
    # In Streamlit: if st.button("Refresh"): # runs this code immediately
    # 
    # The entire script re-runs when the button is clicked!
    # This is why we use caching to avoid re-fetching unnecessarily.
    refresh = st.button("🔄 Refresh Data", use_container_width=True)
    
    if refresh:
        # Clear the cache to force a fresh fetch
        # st.cache_data.clear() is like clearing MemoryCache in C#
        st.cache_data.clear()
        st.success("Cache cleared! Data will refresh on next load.")
        # The page will re-run automatically
    
    st.markdown("---")
    st.caption("Built with Streamlit | Supabase")

# --- MAIN CONTENT ---

# Title - like an <h1> in HTML
st.title("📊 News Articles Dashboard")

# Fetch data from Supabase
# This is the first time the function runs - it fetches from Supabase
# On subsequent runs (due to caching), it returns cached data
df = get_articles_from_supabase()

# Display statistics (like summary cards)
if not df.empty:
    # Create metrics row - like metric cards in a dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    # st.metric creates a nice metric card
    # In C#, this would be like: <div class="metric"><label>Total</label><value>100</value></div>
    with col1:
        st.metric("📰 Total Articles", len(df))
    
    with col2:
        # Count unique sources
        # df['source'].nunique() is like: articles.Select(a => a.Source).Distinct().Count() in LINQ
        st.metric("📡 Unique Sources", df['source'].nunique())
    
    with col3:
        # Latest article date
        latest = df['published_at'].max()
        st.metric("🕐 Latest Article", latest.strftime('%Y-%m-%d'))
    
    with col4:
        # Oldest article date
        oldest = df['published_at'].min()
        st.metric("📅 Oldest Article", oldest.strftime('%Y-%m-%d'))
    
    # --- TAB 1: Chart View ---
    # st.tabs creates tabbed navigation, like TabControl in C# WinForms
    tab1, tab2 = st.tabs(["📊 Chart View", "📋 Table View"])
    
    with tab1:
        st.subheader("Articles Per Day (Last 7 Days)")
        
        # Prepare data for chart
        daily_counts = get_articles_by_day(df, days=7)
        
        if not daily_counts.empty:
            # Display bar chart
            # st.bar_chart creates a bar chart automatically
            # In C#, this would be like using a Chart control
            st.bar_chart(daily_counts.set_index('date'))
            
            # Show the raw data for transparency
            with st.expander("📊 View Daily Data"):
                st.dataframe(daily_counts)
            
            # Show the top source for the period
            if len(df) > 0:
                # Filter last 7 days
                cutoff = datetime.now(timezone.utc) - timedelta(days=7)
                recent = df[df['published_at'] >= cutoff]
                
                if not recent.empty:
                    # Get top source
                    top_source = recent['source'].value_counts().index[0]
                    top_count = recent['source'].value_counts().iloc[0]
                    
                    st.info(f"🏆 Top source in last 7 days: **{top_source}** ({top_count} articles)")
        else:
            st.warning("No articles found in the last 7 days.")
    
    with tab2:
        st.subheader("Recent Articles")
        
        # --- FILTERS (like dropdown filters in C#) ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Create a dropdown to filter by source
            # st.selectbox is like a ComboBox or DropDownList in C#
            # st.selectbox returns the selected value
            sources = ['All Sources'] + sorted(df['source'].unique().tolist())
            selected_source = st.selectbox('Filter by Source', sources)
        
        with col2:
            # Create a date range filter
            # st.date_input is like DateTimePicker in C# WinForms
            # Convert timezone-aware to naive for date_input (it expects naive dates)
            min_date = df['published_at'].dt.tz_localize(None).min().date()
            max_date = df['published_at'].dt.tz_localize(None).max().date()
            date_range = st.date_input(
                'Date Range',
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        # Apply filters to the DataFrame
        filtered_df = df.copy()
        
        # Filter by source
        if selected_source != 'All Sources':
            filtered_df = filtered_df[filtered_df['source'] == selected_source]
        
        # Filter by date range
        if len(date_range) == 2:  # User selected both dates
            start_date, end_date = date_range
            # Convert to datetime for comparison
            # We need to make them timezone-aware (UTC) for comparison
            start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)
            
            filtered_df = filtered_df[
                (filtered_df['published_at'] >= start_datetime) &
                (filtered_df['published_at'] <= end_datetime)
            ]
        
        # Display the table
        # st.dataframe displays an interactive table (sortable, searchable)
        # In C#, this is like a DataGridView with built-in sorting
        #
        # We select and rename columns for better display
        display_df = filtered_df[['title', 'source', 'published_at', 'url']].copy()
        
        # Format the published_at column
        display_df['published_at'] = display_df['published_at'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename columns (like using column headers in a DataGridView)
        display_df.columns = ['Title', 'Source', 'Published', 'URL']
        
        # Display with clickable URLs
        # st.dataframe with column_config makes URLs clickable
        # In C#, this would be like setting a column to be a HyperLink in a DataGridView
        st.dataframe(
            display_df,
            column_config={
                "URL": st.column_config.LinkColumn("URL"),
                "Title": st.column_config.TextColumn("Title", width="large"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Show count
        st.caption(f"Showing {len(filtered_df)} of {len(df)} articles")

else:
    # Show welcome message with instructions
    st.info("""
    ### 📭 No articles found in the database
    
    **To get started:**
    1. Run `python main.py` to collect articles
    2. Or run `python collect.py` to test the news fetcher
    3. Then refresh this dashboard
    """)
    
    # Quick action button
    if st.button("📰 Check for Articles"):
        # This triggers a reload which will re-run the script
        # and check if articles are now available
        st.rerun()

# --- FOOTER ---
st.markdown("---")
st.caption("News Monitor MVP • Block 3: Dashboard")