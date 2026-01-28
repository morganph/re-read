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
        
        # Fetch YOUR OWN liked posts (fetch more to get older posts)
        print(f"Fetching your likes...")
        all_likes = []
        cursor = None
        
        # Fetch multiple pages of likes to get older posts
        for i in range(50):  # Fetch 50 pages = up to 5000 likes
            likes_response = main_client.app.bsky.feed.get_actor_likes({
                'actor': MAIN_HANDLE,
                'limit': 100,
                'cursor': cursor
            })
            
            all_likes.extend(likes_response.feed)
            print(f"Fetched {len(likes_response.feed)} likes (total: {len(all_likes)})")
            
            # Check if there are more pages
            if hasattr(likes_response, 'cursor') and likes_response.cursor:
                cursor = likes_response.cursor
            else:
                print("Reached end of likes")
                break
        
        if not all_likes:
            print("No liked posts found!")
            return
        
        print(f"Total likes fetched: {len(all_likes)}")
        
        # Filter out posts from the last 30 days
        from datetime import datetime, timedelta, timezone
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        
        older_likes = []
        for like in all_likes:
            # Get the indexed timestamp from the like
            if hasattr(like, 'indexed_at'):
                post_date = datetime.fromisoformat(like.indexed_at.replace('Z', '+00:00'))
                if post_date < cutoff_date:
                    older_likes.append(like)
        
        print(f"Likes older than 30 days: {len(older_likes)}")
        
        if not older_likes:
            print("No likes found older than 30 days!")
            return
        
        # Pick a random post from the older ones
        random_like = random.choice(older_likes)
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
            "Worth revisiting.",
            "From the archives.",
            "This deserves another look.",
            "Bringing this back.",
            "Still thinking about this one.",
            "A good one to remember."
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
