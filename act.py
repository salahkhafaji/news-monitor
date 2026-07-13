"""
BLOCK 5: ACT - Send AI Recommendation via Telegram
Takes the recommendation from Block 4 and sends it as a Telegram message.
"""

import os
import requests
import glob
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def send_telegram_message(message):
    """
    Send a message via Telegram Bot API.
    
    Parameters:
        message (str): The message to send
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get Telegram credentials from environment
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Validate credentials
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
            print("Please add: TELEGRAM_BOT_TOKEN=your_bot_token_here")
            return False
        
        if not chat_id:
            print("❌ TELEGRAM_CHAT_ID not found in .env file")
            print("Please add: TELEGRAM_CHAT_ID=your_chat_id_here")
            return False
        
        # Build the API URL
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Build the request payload (plain text - no HTML)
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        
        print(f"📤 Sending Telegram message to chat ID: {chat_id}")
        print(f"📝 Message preview: {message[:100]}...")
        
        # Send the HTTP POST request
        response = requests.post(url, json=payload, timeout=30)
        
        # Check if the request was successful
        response.raise_for_status()
        
        # Parse the JSON response
        result = response.json()
        
        # Check if Telegram API returned success
        if result.get('ok'):
            print("✅ Telegram message sent successfully!")
            return True
        else:
            print(f"❌ Telegram API returned error: {result.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout: Could not reach Telegram API. Please check your internet connection.")
        return False
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Could not connect to Telegram API. No internet?")
        return False
        
    except requests.exceptions.HTTPError as e:
        if hasattr(response, 'status_code'):
            if response.status_code == 401:
                print("❌ Authentication error: Invalid bot token. Please check TELEGRAM_BOT_TOKEN")
            elif response.status_code == 400:
                print("❌ Bad request: Invalid chat ID or message format. Please check TELEGRAM_CHAT_ID")
            else:
                print(f"❌ HTTP error: {e}")
        else:
            print(f"❌ HTTP error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error sending Telegram message: {e}")
        return False


def get_telegram_bot_info():
    """Test function to get bot information."""
    try:
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN not found")
            return None
        
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return result.get('result')
        
        return None
        
    except Exception as e:
        print(f"Error getting bot info: {e}")
        return None


def get_latest_recommendation():
    """
    Find and read the latest recommendation from the recommendations folder.
    
    Returns:
        str: The recommendation text, or None if not found
    """
    try:
        # Get all recommendation files
        files = glob.glob('recommendations/recommendation_*.txt')
        
        if not files:
            return None
        
        # Get the latest file (sorted by filename which includes timestamp)
        latest_file = sorted(files)[-1]
        
        print(f"📄 Found latest recommendation: {latest_file}")
        
        # Read the recommendation from file
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract the recommendation (skip the header)
            lines = content.split('\n')
            recommendation_text = None
            
            # Find where the recommendation starts (after the separator)
            for i, line in enumerate(lines):
                if '=' in line and len(line.strip()) > 10:
                    # The recommendation starts after the separator
                    recommendation_text = '\n'.join(lines[i+1:])
                    recommendation_text = recommendation_text.strip()
                    break
            
            return recommendation_text
            
    except Exception as e:
        print(f"❌ Error reading recommendation file: {e}")
        return None


def run_decide():
    """Run the decide.py script to generate a recommendation."""
    print("\n⚠️ No recommendation found. Running Block 4 (DECIDE) first...")
    print("Executing: python decide.py")
    
    try:
        # Run decide.py and capture output
        result = subprocess.run(['python', 'decide.py'], capture_output=True, text=True)
        
        # Print the output (shows what decide.py produced)
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"❌ decide.py failed with error: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Could not run decide.py: {e}")
        return False


# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    print("=" * 60)
    print("📨 BLOCK 5: ACT - Send to Telegram")
    print("=" * 60)
    
    # Step 1: Check if we have a saved recommendation
    print("\n🔍 Looking for latest recommendation...")
    
    recommendation_text = get_latest_recommendation()
    
    # If no saved recommendation, run decide.py first
    if not recommendation_text:
        success = run_decide()
        if not success:
            exit(1)
        
        # Try reading the latest recommendation file again
        recommendation_text = get_latest_recommendation()
    
    # Step 2: If we have a recommendation, send it
    if recommendation_text:
        print("\n" + "=" * 60)
        print("📨 Sending recommendation to Telegram...")
        print("=" * 60)
        
        # Format the message with a nice header (PLAIN TEXT - no HTML)
        message = f"""
📊 News Monitor - Daily Recommendation
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

💡 AI Recommendation:
{recommendation_text}

---
Generated by Gemini AI | News Monitor MVP
"""
        
        # Send the message
        success = send_telegram_message(message.strip())
        
        if success:
            print("\n✅ Message sent successfully!")
            print("📱 Check your Telegram for the recommendation")
        else:
            print("\n❌ Failed to send message. Check your Telegram credentials.")
    else:
        print("\n❌ No recommendation to send. Please run decide.py first.")

    print("\n" + "=" * 60)