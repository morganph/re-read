import os
import random
import time
from atproto import Client
from datetime import datetime

def get_random_liked_post():
    """Fetch a random post from your liked posts and share it."""
    
    # Get credentials from environment variables
    BOT_HANDLE = os.environ.get('BOT_HANDLE')
    BOT_PASSWORD = os.environ.get('BOT_PASSWORD')
    MAIN_HANDLE = os.environ.get('MAIN_HANDLE')
    MAIN_PASSWORD = os.environ.get('MAIN_PASSWORD')
    
    if not all([BOT_HANDLE, BOT_PASSWORD, MAIN_HANDLE, MAIN_PASSWORD]):
        print("Error: Missing required environment variables")
        print(f"Need: BOT_HANDLE, BOT_PASSWORD, MAIN_HANDLE, MAIN_PASSWORD")
        return
    
    try:
        # Login to main account to fetch likes
        main_client = Client()
        main_client.login(MAIN_HANDLE, MAIN_PASSWORD)
        print(f"Logged into main account: {MAIN_HANDLE}")
        
        # Fetch YOUR OWN liked posts
        print(f"Fetching your likes...")
        likes_response = main_client.app.bsky.feed.get_actor_likes({
            'actor': MAIN_HANDLE,
            'limit': 100  # Fetch up to 100 recent likes
        })
        
        if not likes_response.feed:
            print("No liked posts found!")
            return
        
        # Pick a random post
        random_like = random.choice(likes_response.feed)
        post = random_like.post
        
        # Get post details
        author_handle = post.author.handle
        post_uri = post.uri
        
        # Create the AT Protocol URI for the post
        # URI format: at://did/app.bsky.feed.post/rkey
        uri_parts = post_uri.split('/')
        rkey = uri_parts[-1]
        
        # Construct web URL
        post_url = f"https://bsky.app/profile/{author_handle}/post/{rkey}"
        
        # Get post text (if available)
        post_text = ""
        if hasattr(post.record, 'text'):
            post_text = post.record.text[:100]  # First 100 chars
            if len(post.record.text) > 100:
                post_text += "..."
        
        # Create the bot's post text
        bot_post_text = f'From my bookmarks:\n\n"{post_text}"\n\n— @{author_handle}\n{post_url}'
        
        # Make sure it's under 300 characters
        if len(bot_post_text) > 295:
            # Truncate the quote further if needed
            available_chars = 295 - len(f'From my bookmarks:\n\n"..."\n\n— @{author_handle}\n{post_url}')
            if available_chars > 20:
                post_text = post.record.text[:available_chars] + "..."
                bot_post_text = f'From my bookmarks:\n\n"{post_text}"\n\n— @{author_handle}\n{post_url}'
            else:
                # If still too long, just share the link
                bot_post_text = f'From my bookmarks:\n{post_url}'
        
        # Post it from bot account
        bot_client = Client()
        bot_client.login(BOT_HANDLE, BOT_PASSWORD)
        print(f"Logged into bot account: {BOT_HANDLE}")
        
        bot_client.send_post(text=bot_post_text)
        print(f"Successfully posted!\nContent: {bot_post_text}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    get_random_liked_post()
