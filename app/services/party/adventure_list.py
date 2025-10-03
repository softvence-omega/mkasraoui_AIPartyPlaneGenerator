from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = "service_account.json"  # your JSON file path
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# Authenticate with the service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

youtube = build("youtube", "v3", credentials=credentials)

def search_youtube_videos(query: str, max_results: int = 5):

    # Search videos
    search_request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    search_response = search_request.execute()

    # Get video IDs
    video_ids = [item['id']['videoId'] for item in search_response['items']]

    # Fetch video details
    video_request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    video_response = video_request.execute()

    # Format results
    videos = []
    for item in video_response['items']:
        videos.append({
            "title": item['snippet']['title'],
            "description": item['snippet']['description'],
            "channel": item['snippet']['channelTitle'],
            "url": f"https://www.youtube.com/watch?v={item['id']}",
            "views": item['statistics'].get('viewCount', 0)
        })

    return videos

# Example usage
if __name__ == "__main__":
    query = "Party Music Superhero Adventure"
    top_videos = search_youtube_videos(query)
    for v in top_videos:
        print(v)
