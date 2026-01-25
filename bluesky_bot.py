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
        
        # Get post details for quote posting
        post_uri = post.uri
        post_cid = post.cid
        
        print(f"Selected post by @{post.author.handle}")
        
        # Login to bot account and create quote post
        bot_client = Client()
        bot_client.login(BOT_HANDLE, BOT_PASSWORD)
        print(f"Logged into bot account: {BOT_HANDLE}")
        
        # List of possible messages - add or remove as you like!
        messages = [
            "Reminding is revolutionary.",
            "Revisiting.",
            "From the archives.",
            "We forget more than we learn.",
            "I bring things back."
        ]
        
        # Pick a random message
        quote_text = random.choice(messages)
        
        # Create the embed for the quoted post
        from atproto import models
        
        embed = models.AppBskyEmbedRecord.Main(
            record=models.ComAtprotoRepoStrongRef.Main(
                uri=post_uri,
                cid=post_cid
            )
        )
        
        # Send the quote post
        bot_client.send_post(text=quote_text, embed=embed)
        print(f"Successfully quote posted!")
        print(f"Message: {quote_text}")
        print(f"Quoting post by: @{post.author.handle}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    get_random_liked_post()
