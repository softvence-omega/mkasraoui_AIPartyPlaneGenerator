from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import logging

load_dotenv(override=True)
# Load API key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

logger = logging.getLogger(__name__)  # Set up logger

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def search_youtube_videos(query: str, max_results: int = 5):
    """
    Search for YouTube videos based on query.
    
    Args:
        query: Search query string
        max_results: Maximum number of videos to return
    
    Returns:
        List of video details or empty list if error
    """
    try:
        if not YOUTUBE_API_KEY:
            logger.error("YOUTUBE_API_KEY is not set in environment variables")
            return []
        
        logger.info(f"Searching YouTube for: {query}")
        
        # Search videos
        search_request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        )
        search_response = search_request.execute()
        
        if 'items' not in search_response or not search_response['items']:
            logger.warning(f"No videos found for query: {query}")
            return []

        # Get video IDs
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        logger.info(f"Found {len(video_ids)} videos for query: {query}")

        # Fetch video details
        video_request = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        )
        video_response = video_request.execute()

        # Format results
        videos = []
        for item in video_response.get('items', []):
            video_data = {
                "title": item['snippet']['title'],
                "description": item['snippet']['description'],
                "channel": item['snippet']['channelTitle'],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "views": item['statistics'].get('viewCount', 0),
                "thumbnail": item['snippet']['thumbnails']['default']['url']
            }
            videos.append(video_data)

        logger.info(f"Returned {len(videos)} formatted videos")
        return videos
    
    except Exception as e:
        logger.error(f"Error searching YouTube videos: {str(e)}")
        return []

# Example usage
if __name__ == "__main__":
    query = "Party Music Superhero Adventure"
    top_videos = search_youtube_videos(query)
    for v in top_videos:
        print(v)
